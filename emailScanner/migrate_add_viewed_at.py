"""
Migration script to add viewed_at column to Analysis table.
Run this after updating models.py to add the new field to existing databases.
"""
import sys
from pathlib import Path
import logging
from sqlalchemy import text

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models import init_db
from settings import load_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate():
    """Add viewed_at column to analysis table"""
    try:
        # Load settings and initialize database
        config = load_settings()
        engine = init_db(config.database_url)
        
        logger.info("Starting migration: Adding viewed_at column to analysis table")
        
        # Add the column
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("PRAGMA table_info(analysis)"))
            columns = [row[1] for row in result]
            
            if 'viewed_at' in columns:
                logger.info("Column 'viewed_at' already exists. Skipping migration.")
                return
            
            # Add the new column
            conn.execute(text(
                "ALTER TABLE analysis ADD COLUMN viewed_at DATETIME"
            ))
            conn.commit()
            
            logger.info("✓ Successfully added viewed_at column to analysis table")
            logger.info("Migration complete!")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == '__main__':
    migrate()
