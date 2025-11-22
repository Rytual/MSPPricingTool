"""
Automatic update script for MSP Pricing Tool
Can be run as a scheduled task to update pricing data
"""
import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOGGING_CONFIG
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

def main():
    """Run automatic update"""
    logger.info("Starting automatic update")

    try:
        from update_db import update_database

        # Try API first, fall back to existing CSV if available
        logger.info("Attempting to fetch from Partner Center API")
        success = update_database(source='api')

        if success:
            logger.info("Automatic update from API completed successfully")
            sys.exit(0)
        else:
            logger.warning("API update failed, database unchanged")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Automatic update failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
