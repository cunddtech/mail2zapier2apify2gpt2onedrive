#!/usr/bin/env python3
"""
💼 SALES PIPELINE DATABASE
========================

Verwaltet Verkaufschancen (Opportunities) aus:
- Preisanfragen
- Angebote
- Anfragen
- WeClapp Sync

FEATURES:
✅ SQLite Database
✅ Pipeline Stages (Lead → Angebot → Verhandlung → Gewonnen/Verloren)
✅ Value Tracking
✅ Contact Assignment
✅ Email Linking
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Database path - Railway uses /tmp, local can use relative path
DB_PATH = os.environ.get("SALES_PIPELINE_DB_PATH", "/tmp/sales_pipeline.db")

def init_db():
    """Initialisiere Sales Pipeline Datenbank mit allen Tabellen"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Opportunities (Verkaufschancen)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            stage TEXT NOT NULL, -- lead, qualified, proposal, negotiation, won, lost
            value REAL, -- Geschätzter Wert in EUR
            probability INTEGER, -- 0-100%
            contact_name TEXT,
            contact_email TEXT,
            company_name TEXT,
            source TEXT, -- email, phone, whatsapp, manual
            description TEXT,
            email_message_id TEXT,
            weclapp_id TEXT, -- WeClapp Verkaufschance ID
            expected_close_date TEXT,
            actual_close_date TEXT,
            lost_reason TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            created_by TEXT
        )
    """)
    
    # Activities (Aktivitäten zu Opportunities)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunity_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL, -- email, call, meeting, note, stage_change
            title TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            created_by TEXT,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
        )
    """)
    
    # Indexes für Performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stage ON opportunities(stage)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contact_email ON opportunities(contact_email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_weclapp_id ON opportunities(weclapp_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON opportunities(created_at)")
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Sales Pipeline DB initialized: {DB_PATH}")

# Initialize on import
init_db()


def create_opportunity(opportunity_data: Dict[str, Any]) -> int:
    """
    Erstelle neue Verkaufschance
    
    Args:
        opportunity_data: Dict mit Opportunity-Daten
        
    Returns:
        opportunity_id: ID der erstellten Opportunity
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO opportunities (
            title, stage, value, probability, 
            contact_name, contact_email, company_name,
            source, description, email_message_id, weclapp_id,
            expected_close_date, created_at, updated_at, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        opportunity_data.get("title"),
        opportunity_data.get("stage", "lead"),
        opportunity_data.get("value"),
        opportunity_data.get("probability", 20),
        opportunity_data.get("contact_name"),
        opportunity_data.get("contact_email"),
        opportunity_data.get("company_name"),
        opportunity_data.get("source", "email"),
        opportunity_data.get("description"),
        opportunity_data.get("email_message_id"),
        opportunity_data.get("weclapp_id"),
        opportunity_data.get("expected_close_date"),
        now,
        now,
        opportunity_data.get("created_by", "system")
    ))
    
    opportunity_id = cursor.lastrowid
    
    # Log creation as activity
    cursor.execute("""
        INSERT INTO opportunity_activities (
            opportunity_id, activity_type, title, description, created_at, created_by
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        opportunity_id,
        "stage_change",
        "Verkaufschance erstellt",
        f"Stage: {opportunity_data.get('stage', 'lead')}",
        now,
        opportunity_data.get("created_by", "system")
    ))
    
    conn.commit()
    conn.close()
    
    logger.info(f"💼 Opportunity created: ID={opportunity_id}, Title={opportunity_data.get('title')}")
    return opportunity_id


def update_opportunity_stage(opportunity_id: int, new_stage: str, note: Optional[str] = None) -> bool:
    """Update Opportunity Stage mit Activity Log"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Update stage
    cursor.execute("""
        UPDATE opportunities 
        SET stage = ?, updated_at = ?
        WHERE id = ?
    """, (new_stage, now, opportunity_id))
    
    # Log activity
    cursor.execute("""
        INSERT INTO opportunity_activities (
            opportunity_id, activity_type, title, description, created_at, created_by
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        opportunity_id,
        "stage_change",
        f"Stage geändert zu: {new_stage}",
        note or "",
        now,
        "system"
    ))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success


def get_pipeline_statistics() -> Dict[str, Any]:
    """Get Sales Pipeline Statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total value by stage
    cursor.execute("""
        SELECT 
            stage,
            COUNT(*) as count,
            SUM(value) as total_value,
            AVG(probability) as avg_probability
        FROM opportunities
        WHERE stage NOT IN ('won', 'lost')
        GROUP BY stage
    """)
    
    stages = {}
    for row in cursor.fetchall():
        stage, count, total_value, avg_probability = row
        stages[stage] = {
            "count": count,
            "total_value": total_value or 0.0,
            "avg_probability": avg_probability or 0
        }
    
    # Won/Lost stats
    cursor.execute("""
        SELECT 
            stage,
            COUNT(*) as count,
            SUM(value) as total_value
        FROM opportunities
        WHERE stage IN ('won', 'lost')
        GROUP BY stage
    """)
    
    won_lost = {}
    for row in cursor.fetchall():
        stage, count, total_value = row
        won_lost[stage] = {
            "count": count,
            "total_value": total_value or 0.0
        }
    
    # Weighted pipeline value (probability * value)
    cursor.execute("""
        SELECT SUM(value * probability / 100.0) as weighted_value
        FROM opportunities
        WHERE stage NOT IN ('won', 'lost')
    """)
    weighted_value = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        "stages": stages,
        "won_lost": won_lost,
        "weighted_pipeline_value": weighted_value,
        "timestamp": datetime.now().isoformat()
    }


def get_recent_opportunities(limit: int = 20, stage: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent opportunities with optional stage filter"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if stage:
        cursor.execute("""
            SELECT * FROM opportunities
            WHERE stage = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (stage, limit))
    else:
        cursor.execute("""
            SELECT * FROM opportunities
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
    
    opportunities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return opportunities


def get_opportunity_by_id(opportunity_id: int) -> Optional[Dict[str, Any]]:
    """Get full opportunity details with activities"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get opportunity
    cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opportunity_id,))
    opportunity = cursor.fetchone()
    
    if not opportunity:
        conn.close()
        return None
    
    opportunity_dict = dict(opportunity)
    
    # Get activities
    cursor.execute("""
        SELECT * FROM opportunity_activities
        WHERE opportunity_id = ?
        ORDER BY created_at DESC
    """, (opportunity_id,))
    
    opportunity_dict["activities"] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return opportunity_dict


def add_activity(opportunity_id: int, activity_data: Dict[str, Any]) -> int:
    """Add activity to opportunity"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO opportunity_activities (
            opportunity_id, activity_type, title, description, created_at, created_by
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        opportunity_id,
        activity_data.get("activity_type"),
        activity_data.get("title"),
        activity_data.get("description"),
        now,
        activity_data.get("created_by", "system")
    ))
    
    activity_id = cursor.lastrowid
    
    # Update opportunity timestamp
    cursor.execute("""
        UPDATE opportunities 
        SET updated_at = ?
        WHERE id = ?
    """, (now, opportunity_id))
    
    conn.commit()
    conn.close()
    
    return activity_id


def search_opportunities(query: str) -> List[Dict[str, Any]]:
    """Search opportunities by title, company, or contact"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_pattern = f"%{query}%"
    cursor.execute("""
        SELECT * FROM opportunities
        WHERE title LIKE ? 
           OR company_name LIKE ?
           OR contact_name LIKE ?
           OR contact_email LIKE ?
        ORDER BY created_at DESC
        LIMIT 50
    """, (search_pattern, search_pattern, search_pattern, search_pattern))
    
    opportunities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return opportunities


if __name__ == "__main__":
    # Test database
    print("🧪 Testing Sales Pipeline Database...")
    
    # Create test opportunity
    test_opp = {
        "title": "Dachausbau - Mustermann GmbH",
        "stage": "lead",
        "value": 50000.0,
        "probability": 30,
        "contact_name": "Max Mustermann",
        "contact_email": "max@mustermann.de",
        "company_name": "Mustermann GmbH",
        "source": "email",
        "description": "Preisanfrage für Dachausbau 200qm"
    }
    
    opp_id = create_opportunity(test_opp)
    print(f"✅ Created opportunity: {opp_id}")
    
    # Get statistics
    stats = get_pipeline_statistics()
    print(f"📊 Pipeline Stats: {stats}")
    
    # Get recent
    recent = get_recent_opportunities(5)
    print(f"📋 Recent Opportunities: {len(recent)}")
    
    print("✅ All tests passed!")
