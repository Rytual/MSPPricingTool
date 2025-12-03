"""
Flask web application for MSP Pricing Tool
Serves responsive UI with real-time price queries
"""
from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import logging
from functools import wraps
import subprocess
import tempfile
import sys
from pathlib import Path
from datetime import datetime

from config import config, BASE_DIR, DB_NAME, PORT, HOST, LOGGING_CONFIG

# Determine template and static folder locations
if getattr(sys, 'frozen', False):
    # Running as compiled executable - templates and static are in _MEIPASS
    template_folder = str(Path(sys._MEIPASS) / 'templates')
    static_folder = str(Path(sys._MEIPASS) / 'static')
else:
    # Running as script
    template_folder = str(BASE_DIR / 'templates')
    static_folder = str(BASE_DIR / 'static')

# Initialize Flask app
app = Flask(__name__,
            template_folder=template_folder,
            static_folder=static_folder)

# Configure logging
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

DB_PATH = BASE_DIR / "data" / DB_NAME

# Basic authentication decorator
def check_auth(username, password):
    """Check if username/password combination is valid"""
    if not config.ui_password:
        return True  # No password set, allow access
    return username == config.ui_username and password == config.ui_password

def authenticate():
    """Send 401 response for authentication"""
    return jsonify({"error": "Authentication required"}), 401, \
           {'WWW-Authenticate': 'Basic realm="MSP Pricing Tool"'}

def requires_auth(f):
    """Decorator for routes requiring authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip authentication if no password is configured
        if not config.ui_password:
            return f(*args, **kwargs)

        # Require authentication if password is set
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def term_duration_to_human(term):
    """Convert ISO 8601 duration to human readable"""
    mapping = {
        'P1Y': '1 Year (Annual)',
        'P1M': '1 Month (Monthly)',
        'P3Y': '3 Years',
        'P2Y': '2 Years',
        '': 'Not specified'
    }
    return mapping.get(term, term)

@app.route('/')
@requires_auth
def index():
    """Main query interface"""
    return render_template('query.html')

@app.route('/api/filters', methods=['GET'])
@requires_auth
def get_filters():
    """Get unique values for filter dropdowns"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get unique products
        cursor.execute("""
            SELECT DISTINCT ProductTitle
            FROM prices
            WHERE ProductTitle IS NOT NULL
            ORDER BY ProductTitle
        """)
        products = [row[0] for row in cursor.fetchall()]

        # Get unique segments
        cursor.execute("""
            SELECT DISTINCT Segment
            FROM prices
            WHERE Segment IS NOT NULL
            ORDER BY Segment
        """)
        segments = [row[0] for row in cursor.fetchall()]

        # Get unique term durations
        cursor.execute("""
            SELECT DISTINCT TermDuration
            FROM prices
            WHERE TermDuration IS NOT NULL
            ORDER BY TermDuration
        """)
        terms = [row[0] for row in cursor.fetchall()]

        # Get unique billing plans
        cursor.execute("""
            SELECT DISTINCT BillingPlan
            FROM prices
            WHERE BillingPlan IS NOT NULL
            ORDER BY BillingPlan
        """)
        billing = [row[0] for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'products': products,
            'segments': segments,
            'terms': terms,
            'billing': billing
        })

    except Exception as e:
        logger.error(f"Error fetching filters: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
@requires_auth
def query_prices():
    """Query prices based on filters"""
    try:
        data = request.get_json()
        product = data.get('product')
        segment = data.get('segment')
        term = data.get('term')
        billing = data.get('billing')
        search = data.get('search', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query
        query = "SELECT * FROM prices WHERE 1=1"
        params = []

        if product:
            query += " AND ProductTitle = ?"
            params.append(product)

        if segment:
            query += " AND Segment = ?"
            params.append(segment)

        if term:
            query += " AND TermDuration = ?"
            params.append(term)

        if billing:
            query += " AND BillingPlan = ?"
            params.append(billing)

        if search:
            query += " AND (ProductTitle LIKE ? OR SkuTitle LIKE ? OR SkuDescription LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        query += " ORDER BY ProductTitle, SkuTitle"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert to list of dicts
        results = []
        for row in rows:
            unit_price = float(row['UnitPrice']) if row['UnitPrice'] else 0
            erp_price = float(row['ERPPrice']) if row['ERPPrice'] else 0

            # Calculate markup percentage: ((ERP - MS) / MS) * 100
            markup_percent = 0
            if unit_price > 0:
                markup_percent = ((erp_price - unit_price) / unit_price) * 100

            results.append({
                'id': row['id'],
                'ProductTitle': row['ProductTitle'],
                'SkuTitle': row['SkuTitle'],
                'TermDuration': row['TermDuration'],
                'TermDurationHuman': term_duration_to_human(row['TermDuration']),
                'BillingPlan': row['BillingPlan'],
                'UnitPrice': unit_price,
                'ERPPrice': erp_price,
                'MarkupPercent': round(markup_percent, 1),
                'ProfitPerLicense': round(erp_price - unit_price, 2),
                'Currency': row['Currency'],
                'Segment': row['Segment'],
                'SkuDescription': row['SkuDescription'],
                'Publisher': row['Publisher']
            })

        conn.close()

        return jsonify({
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Error querying prices: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/price/<int:price_id>', methods=['GET'])
@requires_auth
def get_price_detail(price_id):
    """Get detailed information for a specific price"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM prices WHERE id = ?", (price_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({'error': 'Price not found'}), 404

        unit_price = float(row['UnitPrice']) if row['UnitPrice'] else 0
        erp_price = float(row['ERPPrice']) if row['ERPPrice'] else 0

        # Calculate markup percentage
        markup_percent = 0
        if unit_price > 0:
            markup_percent = ((erp_price - unit_price) / unit_price) * 100

        price_detail = dict(row)
        price_detail['TermDurationHuman'] = term_duration_to_human(row['TermDuration'])
        price_detail['UnitPrice'] = unit_price
        price_detail['ERPPrice'] = erp_price
        price_detail['MarkupPercent'] = round(markup_percent, 1)
        price_detail['ProfitPerLicense'] = round(erp_price - unit_price, 2)

        conn.close()

        return jsonify(price_detail)

    except Exception as e:
        logger.error(f"Error fetching price detail: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/draft', methods=['POST'])
@requires_auth
def generate_draft():
    """Generate quote draft and return as HTML for browser display"""
    try:
        data = request.get_json()
        price_id = data.get('price_id')
        margin = data.get('margin', 20)
        quantity = data.get('quantity', 1)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM prices WHERE id = ?", (price_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({'error': 'Price not found'}), 404

        # Calculate prices
        ms_price = float(row['UnitPrice'])  # What Microsoft charges us (Partner Price)
        erp_price = float(row['ERPPrice']) if row['ERPPrice'] else 0  # Microsoft Retail Price

        # Calculate standard markup
        standard_markup = 0
        if ms_price > 0:
            standard_markup = ((erp_price - ms_price) / ms_price) * 100

        # Apply margin adjustment from slider
        final_price = ms_price * (1 + margin / 100)
        profit_per_license = final_price - ms_price
        total_cost = ms_price * quantity
        total_price = final_price * quantity
        total_profit = total_price - total_cost

        # Generate draft text
        draft_text = f"""
========================================
        QUOTE DRAFT SUMMARY
========================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PRODUCT INFORMATION
-------------------
Product:        {row['ProductTitle']}
SKU:            {row['SkuTitle']}
Segment:        {row['Segment']}

PRICING BREAKDOWN (per user/month)
-----------------------------------
Partner Price:      ${ms_price:.2f}
Your Markup:        {margin:.1f}%
Quote Price:        ${final_price:.2f}
Profit/License:     ${profit_per_license:.2f}

MS Retail Price:    ${erp_price:.2f} (Standard Markup: {standard_markup:.1f}%)

CONTRACT DETAILS
----------------
Term:           {term_duration_to_human(row['TermDuration'])}
Billing:        {row['BillingPlan']}
Currency:       {row['Currency']}

QUANTITY & TOTALS
-----------------
Quantity:       {quantity} licenses
Monthly Cost:   ${total_cost:.2f}
Monthly Quote:  ${total_price:.2f}
Monthly Profit: ${total_profit:.2f}

Annual Total:   ${total_price * 12:.2f} (if monthly billing)

DESCRIPTION
-----------
{row['SkuDescription'] or 'N/A'}

NOTES
-----
- Pricing is based on Microsoft NCE License-Based pricing
- Adjust quantity and margin as needed for final quote
- Contact eMazzanti Technologies for final quote approval

========================================
       eMazzanti Technologies
========================================
"""

        conn.close()

        # Generate HTML page for browser display
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quote Draft - {row['ProductTitle']}</title>
    <style>
        body {{
            font-family: 'Consolas', 'Courier New', monospace;
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            margin: 0;
            line-height: 1.4;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: #2d2d2d;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
            font-size: 14px;
        }}
        .actions {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #444;
            text-align: center;
        }}
        button {{
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        button:hover {{
            background-color: #106ebe;
        }}
        @media print {{
            body {{
                background-color: white;
                color: black;
            }}
            .container {{
                background-color: white;
                box-shadow: none;
            }}
            .actions {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <pre>{draft_text}</pre>
        <div class="actions">
            <button onclick="window.print()">Print Quote</button>
            <button onclick="copyToClipboard()">Copy to Clipboard</button>
            <button onclick="window.close()">Close</button>
        </div>
    </div>
    <script>
        function copyToClipboard() {{
            const text = document.querySelector('pre').textContent;
            navigator.clipboard.writeText(text).then(() => {{
                alert('Quote copied to clipboard!');
            }}).catch(err => {{
                console.error('Failed to copy:', err);
                // Fallback for older browsers
                const textarea = document.createElement('textarea');
                textarea.value = text;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                alert('Quote copied to clipboard!');
            }});
        }}
    </script>
</body>
</html>"""

        return jsonify({'success': True, 'html': html_content})

    except Exception as e:
        logger.error(f"Error generating draft: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
@requires_auth
def export_csv():
    """Export current query results to CSV"""
    try:
        data = request.get_json()
        results = data.get('results', [])

        if not results:
            return jsonify({'error': 'No results to export'}), 400

        # Create CSV in memory
        import csv
        import io

        output = io.StringIO()
        if results:
            writer = csv.DictWriter(output, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        output.seek(0)

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
            f.write(output.getvalue())
            temp_path = f.name

        return send_file(temp_path,
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name=f'pricing_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

    except Exception as e:
        logger.error(f"Error exporting CSV: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
@requires_auth
def get_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM prices")
        total_count = cursor.fetchone()['count']

        cursor.execute("SELECT value FROM metadata WHERE key = 'last_import'")
        last_import = cursor.fetchone()
        last_import_date = last_import['value'] if last_import else 'Never'

        conn.close()

        return jsonify({
            'total_prices': total_count,
            'last_import': last_import_date
        })

    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

def run_server():
    """Run the Flask server"""
    logger.info(f"Starting MSP Pricing Tool web server on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)

if __name__ == '__main__':
    run_server()
