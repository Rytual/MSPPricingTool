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
from pathlib import Path
from datetime import datetime

from config import config, BASE_DIR, DB_NAME, PORT, HOST, LOGGING_CONFIG

# Initialize Flask app
app = Flask(__name__,
            template_folder=str(BASE_DIR / 'templates'),
            static_folder=str(BASE_DIR / 'static'))

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
            results.append({
                'id': row['id'],
                'ProductTitle': row['ProductTitle'],
                'ProductId': row['ProductId'],
                'SkuId': row['SkuId'],
                'SkuTitle': row['SkuTitle'],
                'SkuDescription': row['SkuDescription'],
                'TermDuration': row['TermDuration'],
                'TermDurationHuman': term_duration_to_human(row['TermDuration']),
                'BillingPlan': row['BillingPlan'],
                'UnitPrice': row['UnitPrice'],
                'ERPPrice': row['ERPPrice'],
                'Currency': row['Currency'],
                'Segment': row['Segment'],
                'EffectiveStartDate': row['EffectiveStartDate'],
                'Market': row['Market'],
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

        price_detail = dict(row)
        price_detail['TermDurationHuman'] = term_duration_to_human(row['TermDuration'])

        conn.close()

        return jsonify(price_detail)

    except Exception as e:
        logger.error(f"Error fetching price detail: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/draft', methods=['POST'])
@requires_auth
def generate_draft():
    """Generate quote draft and open in Notepad"""
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

        # Calculate final price with margin
        base_price = float(row['UnitPrice'])
        margin_multiplier = 1 + (margin / 100)
        final_price = base_price * margin_multiplier
        total_est = final_price * quantity

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
SKU ID:         {row['SkuId']}
Publisher:      {row['Publisher']}

PRICING DETAILS
---------------
Term:           {term_duration_to_human(row['TermDuration'])}
Billing:        {row['BillingPlan']}
Segment:        {row['Segment']}
Currency:       {row['Currency']}

Base Price:     ${base_price:.2f} /user/month
Margin:         {margin}%
Final Price:    ${final_price:.2f} /user/month

Quantity:       {quantity} [Edit as needed]
Total Est:      ${total_est:.2f} /month

EFFECTIVE DATES
---------------
From:           {row['EffectiveStartDate']}
To:             {row['EffectiveEndDate']}

DESCRIPTION
-----------
{row['SkuDescription'] or 'N/A'}

NOTES
-----
- Pricing is based on Microsoft NCE License-Based pricing
- Final pricing subject to Microsoft's terms and conditions
- Quantity and margin can be adjusted as needed
- Contact eMazzanti Technologies for final quote approval

========================================
       eMazzanti Technologies
========================================
"""

        conn.close()

        # Write to temporary file and open in Notepad
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(draft_text)
            temp_path = f.name

        # Open in Notepad (Windows)
        try:
            subprocess.Popen(['notepad.exe', temp_path])
        except Exception as e:
            logger.warning(f"Could not open Notepad: {e}")
            # Return the draft text if Notepad fails
            return jsonify({'draft': draft_text})

        return jsonify({'success': True, 'file': temp_path})

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
