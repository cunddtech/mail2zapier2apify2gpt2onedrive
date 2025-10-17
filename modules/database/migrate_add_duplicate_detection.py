"""
Database Migration: Add Duplicate Detection Support

Adds the following columns to attachments table:
- document_hash TEXT (SHA256 hash for duplicate detection)
- onedrive_path TEXT (full OneDrive path after upload)
- duplicate_of INTEGER (FK to original attachment if duplicate)
"""
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "email_data.db"

def migrate_database():
    """
    Run migration to add duplicate detection columns.
    Safe to run multiple times - uses IF NOT EXISTS checks.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    logger.info("🔧 Starting database migration...")
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(attachments)")
        columns = [col[1] for col in cursor.fetchall()]
        logger.info(f"Current columns: {columns}")
        
        # Add document_hash column if missing
        if "document_hash" not in columns:
            logger.info("➕ Adding document_hash column...")
            cursor.execute("ALTER TABLE attachments ADD COLUMN document_hash TEXT")
            logger.info("✅ document_hash column added")
        else:
            logger.info("✓ document_hash column already exists")
        
        # Add onedrive_path column if missing
        if "onedrive_path" not in columns:
            logger.info("➕ Adding onedrive_path column...")
            cursor.execute("ALTER TABLE attachments ADD COLUMN onedrive_path TEXT")
            logger.info("✅ onedrive_path column added")
        else:
            logger.info("✓ onedrive_path column already exists")
        
        # Add duplicate_of column if missing
        if "duplicate_of" not in columns:
            logger.info("➕ Adding duplicate_of column...")
            cursor.execute("ALTER TABLE attachments ADD COLUMN duplicate_of INTEGER")
            logger.info("✅ duplicate_of column added")
        else:
            logger.info("✓ duplicate_of column already exists")
        
        # Create index for fast duplicate lookups
        logger.info("🔍 Creating index on document_hash...")
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_hash ON attachments(document_hash)
        """)
        logger.info("✅ Index created")
        
        conn.commit()
        logger.info("✅ Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
