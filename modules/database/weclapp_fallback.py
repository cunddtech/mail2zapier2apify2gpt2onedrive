"""
🔄 WEClapp Database Fallback System
Creates local WEClapp sync database if OneDrive version is not available
Ensures continuous operation with persistent data storage
"""

import os
import sqlite3
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WEClappFallbackDB:
    """
    Fallback WEClapp database system
    - Creates local SQLite database if OneDrive sync is unavailable
    - Maintains contact and opportunity data for uninterrupted operation
    - Automatically migrates data when OneDrive becomes available
    """
    
    def __init__(self, db_path: str = "/tmp/weclapp_fallback.db"):
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Create fallback database with required tables if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create parties table (customers/suppliers)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parties (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    customerNumber TEXT,
                    partyType TEXT DEFAULT 'customer',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create leads table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY,
                    firstName TEXT,
                    lastName TEXT,
                    email TEXT UNIQUE,
                    phone TEXT,
                    company TEXT,
                    leadStatus TEXT DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create opportunities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    party_id INTEGER,
                    lead_id INTEGER,
                    amount REAL,
                    status TEXT DEFAULT 'open',
                    probability INTEGER DEFAULT 50,
                    expected_close_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_id) REFERENCES parties (id),
                    FOREIGN KEY (lead_id) REFERENCES leads (id)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_parties_email ON parties(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_party ON opportunities(party_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_lead ON opportunities(lead_id)")
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ WEClapp fallback database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create fallback database: {e}")
    
    def find_contact_by_email(self, email: str) -> Optional[Dict]:
        """Find contact in fallback database by email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Try parties table first
            cursor.execute("""
                SELECT id, name, email, phone, customerNumber, partyType
                FROM parties 
                WHERE email = ? COLLATE NOCASE
                LIMIT 1
            """, (email,))
            
            row = cursor.fetchone()
            
            if row:
                conn.close()
                logger.info(f"✅ Found contact in fallback DB: {row[1]} (Party ID: {row[0]})")
                
                return {
                    "party_id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "customer_number": row[4],
                    "party_type": row[5],
                    "source": "weclapp_fallback_db"
                }
            
            # Try leads table
            cursor.execute("""
                SELECT id, firstName, lastName, email, phone, company, leadStatus
                FROM leads
                WHERE email = ? COLLATE NOCASE
                LIMIT 1
            """, (email,))
            
            row = cursor.fetchone()
            
            if row:
                conn.close()
                name = f"{row[1]} {row[2]}".strip()
                logger.info(f"✅ Found lead in fallback DB: {name} (Lead ID: {row[0]})")
                
                return {
                    "lead_id": row[0],
                    "name": name,
                    "email": row[3],
                    "phone": row[4],
                    "company": row[5],
                    "lead_status": row[6],
                    "source": "weclapp_fallback_db"
                }
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"❌ Fallback DB query error: {e}")
            return None
    
    def add_contact(self, name: str, email: str, phone: str = None, company: str = None, contact_type: str = "lead") -> Optional[int]:
        """Add new contact to fallback database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if contact_type == "customer":
                # Add as party (customer)
                cursor.execute("""
                    INSERT OR REPLACE INTO parties (name, email, phone, partyType)
                    VALUES (?, ?, ?, ?)
                """, (name, email, phone, "customer"))
            else:
                # Add as lead
                first_name, last_name = (name.split(" ", 1) + [""])[:2]
                cursor.execute("""
                    INSERT OR REPLACE INTO leads (firstName, lastName, email, phone, company, leadStatus)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (first_name, last_name, email, phone, company, "new"))
            
            contact_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Added contact to fallback DB: {name} ({email}) - ID: {contact_id}")
            return contact_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add contact to fallback DB: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM parties")
            parties_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM leads")
            leads_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM opportunities")
            opportunities_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "parties": parties_count,
                "leads": leads_count,
                "opportunities": opportunities_count,
                "total_contacts": parties_count + leads_count,
                "database_path": self.db_path,
                "source": "fallback_database"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get fallback DB statistics: {e}")
            return {"error": str(e)}
    
    def migrate_from_onedrive_db(self, onedrive_db_path: str) -> bool:
        """Migrate data from OneDrive WEClapp database to fallback database"""
        try:
            if not os.path.exists(onedrive_db_path):
                logger.warning(f"OneDrive DB not found: {onedrive_db_path}")
                return False
            
            # Open both databases
            source_conn = sqlite3.connect(onedrive_db_path)
            target_conn = sqlite3.connect(self.db_path)
            
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            # Migrate parties
            source_cursor.execute("SELECT * FROM parties")
            parties = source_cursor.fetchall()
            
            for party in parties:
                target_cursor.execute("""
                    INSERT OR REPLACE INTO parties 
                    (id, name, email, phone, customerNumber, partyType)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, party[:6])  # First 6 columns
            
            # Migrate leads
            source_cursor.execute("SELECT * FROM leads")
            leads = source_cursor.fetchall()
            
            for lead in leads:
                target_cursor.execute("""
                    INSERT OR REPLACE INTO leads 
                    (id, firstName, lastName, email, phone, company, leadStatus)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, lead[:7])  # First 7 columns
            
            target_conn.commit()
            source_conn.close()
            target_conn.close()
            
            logger.info(f"✅ Migrated {len(parties)} parties and {len(leads)} leads from OneDrive DB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration from OneDrive DB failed: {e}")
            return False

# Global fallback database instance
_fallback_db = None

def get_weclapp_fallback_db() -> WEClappFallbackDB:
    """Get global fallback database instance"""
    global _fallback_db
    if _fallback_db is None:
        _fallback_db = WEClappFallbackDB()
    return _fallback_db

async def query_weclapp_contact_with_fallback(email: str) -> Optional[Dict]:
    """
    Query WEClapp contact with fallback strategy:
    1. Try OneDrive sync database
    2. Try fallback database
    3. Return None if not found
    """
    # Try OneDrive database first
    onedrive_db_path = "/tmp/weclapp_sync.db"
    
    if os.path.exists(onedrive_db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(onedrive_db_path)
            cursor = conn.cursor()
            
            # Try parties table first
            cursor.execute("""
                SELECT id, name, email, phone, customerNumber, partyType
                FROM parties 
                WHERE email = ? COLLATE NOCASE
                LIMIT 1
            """, (email,))
            
            row = cursor.fetchone()
            
            if row:
                conn.close()
                return {
                    "party_id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "customer_number": row[4],
                    "party_type": row[5],
                    "source": "weclapp_onedrive_db"
                }
            
            # Try leads table
            cursor.execute("""
                SELECT id, firstName, lastName, email, phone, company, leadStatus
                FROM leads
                WHERE email = ? COLLATE NOCASE
                LIMIT 1
            """, (email,))
            
            row = cursor.fetchone()
            
            if row:
                conn.close()
                name = f"{row[1]} {row[2]}".strip()
                return {
                    "lead_id": row[0],
                    "name": name,
                    "email": row[3],
                    "phone": row[4],
                    "company": row[5],
                    "lead_status": row[6],
                    "source": "weclapp_onedrive_db"
                }
            
            conn.close()
            
        except Exception as e:
            logger.warning(f"OneDrive DB query failed, trying fallback: {e}")
    
    # Try fallback database
    fallback_db = get_weclapp_fallback_db()
    return fallback_db.find_contact_by_email(email)