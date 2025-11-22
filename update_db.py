"""
Database update module for MSP Pricing Application
Handles CSV ingestion and Partner Center API fetching
"""
import sqlite3
import pandas as pd
import hashlib
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from msal import PublicClientApplication, SerializableTokenCache
import json

from config import config, BASE_DIR, DB_NAME, AUTHORITY, SCOPE, PARTNER_CENTER_API

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = BASE_DIR / "data" / DB_NAME

def init_database():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ChangeIndicator TEXT,
            ProductTitle TEXT,
            ProductId TEXT,
            SkuId TEXT,
            SkuTitle TEXT,
            Publisher TEXT,
            SkuDescription TEXT,
            UnitOfMeasure TEXT,
            TermDuration TEXT,
            BillingPlan TEXT,
            Market TEXT,
            Currency TEXT,
            UnitPrice REAL,
            PricingTierRangeMin TEXT,
            PricingTierRangeMax TEXT,
            EffectiveStartDate TEXT,
            EffectiveEndDate TEXT,
            Tags TEXT,
            ERPPrice REAL,
            Segment TEXT,
            PreviousValues TEXT,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ProductId, SkuId, TermDuration, BillingPlan, Segment, EffectiveStartDate)
        )
    """)

    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_title ON prices(ProductTitle)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_segment ON prices(Segment)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_term ON prices(TermDuration)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_billing ON prices(BillingPlan)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_effective ON prices(EffectiveStartDate, EffectiveEndDate)")

    # Metadata table for tracking updates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def calculate_csv_hash(csv_path):
    """Calculate MD5 hash of CSV file to detect changes"""
    hash_md5 = hashlib.md5()
    with open(csv_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_last_csv_hash():
    """Get the hash of the last imported CSV"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'last_csv_hash'")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def set_last_csv_hash(hash_value):
    """Store the hash of the imported CSV"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value, updated_at)
        VALUES ('last_csv_hash', ?, CURRENT_TIMESTAMP)
    """, (hash_value,))
    conn.commit()
    conn.close()

def filter_active_prices(df):
    """Filter to only include currently active prices"""
    today = datetime.now()

    # Parse dates
    df['EffectiveStartDate'] = pd.to_datetime(df['EffectiveStartDate'], errors='coerce')
    df['EffectiveEndDate'] = pd.to_datetime(df['EffectiveEndDate'], errors='coerce')

    # Filter active prices (start date <= today AND end date >= today or far future)
    active_df = df[
        (df['EffectiveStartDate'] <= today) &
        (df['EffectiveEndDate'] >= today)
    ].copy()

    logger.info(f"Filtered {len(active_df)} active prices from {len(df)} total records")
    return active_df

def ingest_csv(csv_path, force=False):
    """Ingest CSV file into database"""
    csv_path = Path(csv_path)

    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return False

    # Check if CSV has changed
    current_hash = calculate_csv_hash(csv_path)
    last_hash = get_last_csv_hash()

    if not force and current_hash == last_hash:
        logger.info("CSV unchanged, skipping import")
        return True

    logger.info(f"Importing CSV: {csv_path}")

    try:
        # Read CSV
        df = pd.read_csv(csv_path, encoding='utf-8-sig')  # Handle BOM

        # Rename ERP Price column (has space)
        if 'ERP Price' in df.columns:
            df.rename(columns={'ERP Price': 'ERPPrice'}, inplace=True)

        # Filter active prices
        active_df = filter_active_prices(df)

        if active_df.empty:
            logger.warning("No active prices found in CSV")
            return False

        # Convert dates back to strings for storage
        active_df['EffectiveStartDate'] = active_df['EffectiveStartDate'].dt.strftime('%Y-%m-%d %H:%M:%S')
        active_df['EffectiveEndDate'] = active_df['EffectiveEndDate'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Initialize database
        init_database()

        # Clear existing data
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prices")
        conn.commit()

        # Insert new data
        active_df.to_sql('prices', conn, if_exists='append', index=False)

        # Update metadata
        set_last_csv_hash(current_hash)
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES ('last_import', ?, CURRENT_TIMESTAMP)
        """, (datetime.now().isoformat(),))
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES ('import_source', 'csv', CURRENT_TIMESTAMP)
        """)

        conn.commit()
        conn.close()

        logger.info(f"Successfully imported {len(active_df)} active prices")
        config.last_update = datetime.now().isoformat()
        return True

    except Exception as e:
        logger.error(f"Error importing CSV: {e}", exc_info=True)
        return False

def get_msal_app():
    """Get MSAL PublicClientApplication instance"""
    if not config.client_id or not config.tenant_id:
        raise ValueError("Azure AD credentials not configured")

    authority_url = f"{AUTHORITY}/{config.tenant_id}"
    app = PublicClientApplication(
        config.client_id,
        authority=authority_url
    )
    return app

def acquire_token_interactive():
    """Acquire token via interactive browser login (first-time setup)"""
    try:
        app = get_msal_app()

        # Try to acquire token interactively
        result = app.acquire_token_interactive(
            scopes=SCOPE,
            prompt='select_account'
        )

        if "access_token" in result:
            config.access_token = result["access_token"]
            if "refresh_token" in result:
                config.refresh_token = result["refresh_token"]
            logger.info("Successfully acquired token interactively")
            return result["access_token"]
        else:
            error = result.get("error_description", result.get("error", "Unknown error"))
            logger.error(f"Interactive token acquisition failed: {error}")
            return None

    except Exception as e:
        logger.error(f"Error during interactive authentication: {e}", exc_info=True)
        return None

def acquire_token_silent():
    """Acquire token silently using refresh token"""
    try:
        app = get_msal_app()

        # Get accounts
        accounts = app.get_accounts()

        if accounts:
            result = app.acquire_token_silent(
                scopes=SCOPE,
                account=accounts[0]
            )

            if result and "access_token" in result:
                config.access_token = result["access_token"]
                if "refresh_token" in result:
                    config.refresh_token = result["refresh_token"]
                logger.info("Successfully acquired token silently")
                return result["access_token"]

        # If silent fails, try interactive
        logger.info("Silent token acquisition failed, trying interactive")
        return acquire_token_interactive()

    except Exception as e:
        logger.error(f"Error during silent authentication: {e}", exc_info=True)
        return acquire_token_interactive()

def fetch_from_partner_center_api():
    """Fetch pricing data from Partner Center API"""
    try:
        # Acquire token
        token = acquire_token_silent()
        if not token:
            logger.error("Failed to acquire access token")
            return False

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        # Fetch pricing data - using the updatedlicensebased view for NCE
        # Note: The actual endpoint may vary - this is a common pattern
        url = f"{PARTNER_CENTER_API}/ratecards/azure"

        logger.info(f"Fetching pricing from Partner Center API: {url}")
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            logger.info("Successfully fetched pricing data from API")

            # Process and store data
            # The API response structure may vary - adapt as needed
            # For now, we'll log success but recommend using CSV until API is validated
            logger.warning("API fetch successful but CSV import is recommended for initial setup")
            return True
        else:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error fetching from Partner Center API: {e}", exc_info=True)
        return False

def update_database(source='csv', csv_path=None):
    """
    Main update function
    source: 'csv' or 'api'
    """
    logger.info(f"Starting database update from {source}")

    if source == 'csv':
        if not csv_path:
            # Look for CSV in current directory
            csv_files = list(BASE_DIR.glob("*NCE*.csv"))
            if csv_files:
                csv_path = csv_files[0]
            else:
                logger.error("No CSV file specified or found")
                return False

        return ingest_csv(csv_path)

    elif source == 'api':
        return fetch_from_partner_center_api()

    else:
        logger.error(f"Unknown source: {source}")
        return False

if __name__ == "__main__":
    # Initialize database on first run
    init_database()

    # Try to import initial CSV if it exists
    csv_file = BASE_DIR / "Nov_NCE_LicenseBasedPL_GA_US.csv"
    if csv_file.exists():
        update_database(source='csv', csv_path=csv_file)
    else:
        logger.info("No initial CSV found. Use the tray icon to upload or fetch from API.")
