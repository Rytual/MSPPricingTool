"""
Main launcher for MSP Pricing Application
Coordinates web server, tray icon, and initial data import
"""
import sys
import logging
import threading
from pathlib import Path
import time

# Configure logging first
from config import LOGGING_CONFIG, BASE_DIR, DB_NAME
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

def check_database_exists():
    """Check if database exists"""
    db_path = BASE_DIR / "data" / DB_NAME
    return db_path.exists()

def initial_setup():
    """Perform initial setup on first run"""
    logger.info("Starting MSP NCE Pricing Tool")

    # Initialize database
    from update_db import init_database
    init_database()

    # Check if we need to import initial CSV
    if not check_database_exists() or get_db_record_count() == 0:
        logger.info("Database is empty, checking for initial CSV")

        # Look for CSV file
        csv_files = list(BASE_DIR.glob("*NCE*.csv"))
        if csv_files:
            logger.info(f"Found initial CSV: {csv_files[0]}")
            from update_db import update_database
            try:
                success = update_database(source='csv', csv_path=csv_files[0])
                if success:
                    logger.info("Initial CSV import successful")
                else:
                    logger.warning("Initial CSV import failed")
            except Exception as e:
                logger.error(f"Error during initial CSV import: {e}", exc_info=True)
        else:
            logger.info("No initial CSV found. Use tray icon to upload CSV or fetch from API")

def get_db_record_count():
    """Get number of records in database"""
    try:
        import sqlite3
        db_path = BASE_DIR / "data" / DB_NAME
        if not db_path.exists():
            return 0

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM prices")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def run_web_server():
    """Run Flask web server in thread"""
    try:
        from app import run_server
        run_server()
    except Exception as e:
        logger.error(f"Web server error: {e}", exc_info=True)

def run_tray():
    """Run system tray icon in thread"""
    try:
        from tray import run_tray_icon
        run_tray_icon()
    except Exception as e:
        logger.error(f"Tray icon error: {e}", exc_info=True)

def main():
    """Main entry point"""
    try:
        # Perform initial setup
        initial_setup()

        # Start web server in separate thread
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()
        logger.info("Web server thread started")

        # Give web server a moment to start
        time.sleep(2)

        # Start tray icon (blocking - runs in main thread)
        logger.info("Starting tray icon")
        run_tray()

        # When tray icon exits, program ends
        logger.info("Application shutting down")

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
