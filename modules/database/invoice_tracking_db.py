"""
📊 Invoice Tracking Database
Verwaltet Rechnungen mit Beträgen, Fälligkeiten, Status
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

DB_PATH = "/tmp/invoice_tracking.db"


def init_invoice_db():
    """Initialize Invoice Tracking Database with comprehensive schema"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Invoices Table - Zentrale Rechnungsverwaltung
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            invoice_date DATE,
            due_date DATE,
            amount_net REAL,
            amount_tax REAL,
            amount_total REAL NOT NULL,
            currency TEXT DEFAULT 'EUR',
            vendor_name TEXT,
            vendor_id TEXT,
            customer_name TEXT,
            customer_id TEXT,
            direction TEXT,  -- 'incoming' or 'outgoing'
            status TEXT DEFAULT 'open',  -- open, paid, overdue, cancelled
            payment_date DATE,
            payment_method TEXT,
            document_hash TEXT,
            onedrive_path TEXT,
            onedrive_link TEXT,
            email_message_id TEXT,
            weclapp_party_id TEXT,
            weclapp_invoice_id TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Invoice Items Table - Rechnungspositionen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            position INTEGER,
            description TEXT,
            quantity REAL,
            unit_price REAL,
            total_price REAL,
            tax_rate REAL,
            article_number TEXT,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        )
    """)
    
    # Payment Reminders Table - Mahnungen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            reminder_level INTEGER,  -- 1, 2, 3
            reminder_date DATE NOT NULL,
            sent_at DATETIME,
            status TEXT DEFAULT 'pending',  -- pending, sent, paid
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        )
    """)
    
    # Indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoices(invoice_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vendor_name ON invoices(vendor_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_due_date ON invoices(due_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON invoices(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_direction ON invoices(direction)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_hash ON invoices(document_hash)")
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Invoice Tracking DB initialized: {DB_PATH}")


def save_invoice(invoice_data: Dict) -> int:
    """
    Save invoice to database
    
    Args:
        invoice_data: Dict with invoice details
        
    Returns:
        invoice_id: Primary key of saved invoice
    """
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO invoices (
                invoice_number, invoice_date, due_date,
                amount_net, amount_tax, amount_total, currency,
                vendor_name, vendor_id, customer_name, customer_id,
                direction, status, document_hash,
                onedrive_path, onedrive_link, email_message_id,
                weclapp_party_id, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_data.get("invoice_number"),
            invoice_data.get("invoice_date"),
            invoice_data.get("due_date"),
            invoice_data.get("amount_net"),
            invoice_data.get("amount_tax"),
            invoice_data.get("amount_total"),
            invoice_data.get("currency", "EUR"),
            invoice_data.get("vendor_name"),
            invoice_data.get("vendor_id"),
            invoice_data.get("customer_name"),
            invoice_data.get("customer_id"),
            invoice_data.get("direction", "incoming"),
            invoice_data.get("status", "open"),
            invoice_data.get("document_hash"),
            invoice_data.get("onedrive_path"),
            invoice_data.get("onedrive_link"),
            invoice_data.get("email_message_id"),
            invoice_data.get("weclapp_party_id"),
            invoice_data.get("notes")
        ))
        
        invoice_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"✅ Invoice saved: {invoice_data.get('invoice_number')} (ID: {invoice_id})")
        
        return invoice_id
        
    except sqlite3.IntegrityError:
        # Invoice number already exists - update instead
        logger.warning(f"⚠️ Invoice {invoice_data.get('invoice_number')} already exists - updating")
        
        cursor.execute("""
            UPDATE invoices SET
                invoice_date = ?, due_date = ?,
                amount_net = ?, amount_tax = ?, amount_total = ?,
                vendor_name = ?, customer_name = ?,
                onedrive_path = ?, onedrive_link = ?,
                updated_at = ?
            WHERE invoice_number = ?
        """, (
            invoice_data.get("invoice_date"),
            invoice_data.get("due_date"),
            invoice_data.get("amount_net"),
            invoice_data.get("amount_tax"),
            invoice_data.get("amount_total"),
            invoice_data.get("vendor_name"),
            invoice_data.get("customer_name"),
            invoice_data.get("onedrive_path"),
            invoice_data.get("onedrive_link"),
            datetime.utcnow().isoformat(),
            invoice_data.get("invoice_number")
        ))
        
        conn.commit()
        
        # Get invoice_id of updated record
        cursor.execute("SELECT id FROM invoices WHERE invoice_number = ?", 
                      (invoice_data.get("invoice_number"),))
        invoice_id = cursor.fetchone()[0]
        
        return invoice_id
        
    finally:
        conn.close()


def get_invoice_by_number(invoice_number: str) -> Optional[Dict]:
    """Get invoice by invoice number"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    
    return None


def get_overdue_invoices() -> List[Dict]:
    """Get all overdue invoices"""
    
    today = datetime.now().date().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM invoices 
        WHERE status = 'open' 
        AND due_date < ?
        ORDER BY due_date ASC
    """, (today,))
    
    rows = cursor.fetchall()
    conn.close()
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def get_open_invoices(direction: str = None) -> List[Dict]:
    """Get all open invoices (optionally filtered by direction)"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if direction:
        cursor.execute("""
            SELECT * FROM invoices 
            WHERE status = 'open' AND direction = ?
            ORDER BY due_date ASC
        """, (direction,))
    else:
        cursor.execute("""
            SELECT * FROM invoices 
            WHERE status = 'open'
            ORDER BY due_date ASC
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def mark_invoice_paid(invoice_number: str, payment_date: str = None, payment_method: str = None):
    """Mark invoice as paid"""
    
    if not payment_date:
        payment_date = datetime.now().date().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE invoices SET 
            status = 'paid',
            payment_date = ?,
            payment_method = ?,
            updated_at = ?
        WHERE invoice_number = ?
    """, (payment_date, payment_method, datetime.utcnow().isoformat(), invoice_number))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Invoice {invoice_number} marked as paid")


def get_invoice_statistics() -> Dict:
    """Get invoice statistics"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total open amount
    cursor.execute("""
        SELECT SUM(amount_total) FROM invoices 
        WHERE status = 'open' AND direction = 'incoming'
    """)
    total_open_incoming = cursor.fetchone()[0] or 0.0
    
    cursor.execute("""
        SELECT SUM(amount_total) FROM invoices 
        WHERE status = 'open' AND direction = 'outgoing'
    """)
    total_open_outgoing = cursor.fetchone()[0] or 0.0
    
    # Overdue amount
    today = datetime.now().date().isoformat()
    cursor.execute("""
        SELECT SUM(amount_total) FROM invoices 
        WHERE status = 'open' AND due_date < ? AND direction = 'incoming'
    """, (today,))
    total_overdue = cursor.fetchone()[0] or 0.0
    
    # Count invoices
    cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'open'")
    count_open = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'open' AND due_date < ?", (today,))
    count_overdue = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_open_incoming": total_open_incoming,
        "total_open_outgoing": total_open_outgoing,
        "total_overdue": total_overdue,
        "count_open": count_open,
        "count_overdue": count_overdue
    }


def get_recent_invoices(limit: int = 20) -> List[Dict]:
    """Get recent invoices"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            invoice_number, invoice_date, due_date, amount_total, currency,
            vendor_name, customer_name, status, direction, onedrive_link,
            payment_date, created_at
        FROM invoices
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    invoices = []
    for row in cursor.fetchall():
        invoices.append({
            "invoice_number": row[0],
            "invoice_date": row[1],
            "due_date": row[2],
            "amount_total": row[3],
            "currency": row[4],
            "vendor_name": row[5],
            "customer_name": row[6],
            "status": row[7],
            "direction": row[8],
            "onedrive_link": row[9],
            "payment_date": row[10],
            "created_at": row[11]
        })
    
    conn.close()
    return invoices


def get_invoice_by_number(invoice_number: str) -> Dict:
    """Get invoice by invoice number"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, invoice_number, invoice_date, due_date, amount_net, amount_tax, amount_total,
            currency, vendor_name, vendor_id, customer_name, customer_id, status, direction,
            onedrive_link, payment_date, payment_method, created_at, updated_at
        FROM invoices
        WHERE invoice_number = ?
    """, (invoice_number,))
    
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    invoice = {
        "id": row[0],
        "invoice_number": row[1],
        "invoice_date": row[2],
        "due_date": row[3],
        "amount_net": row[4],
        "amount_tax": row[5],
        "amount_total": row[6],
        "currency": row[7],
        "vendor_name": row[8],
        "vendor_id": row[9],
        "customer_name": row[10],
        "customer_id": row[11],
        "status": row[12],
        "direction": row[13],
        "onedrive_link": row[14],
        "payment_date": row[15],
        "payment_method": row[16],
        "created_at": row[17],
        "updated_at": row[18]
    }
    
    # Get items
    cursor.execute("""
        SELECT position, description, quantity, unit_price, total_price
        FROM invoice_items
        WHERE invoice_id = ?
        ORDER BY position
    """, (invoice["id"],))
    
    items = []
    for item_row in cursor.fetchall():
        items.append({
            "position": item_row[0],
            "description": item_row[1],
            "quantity": item_row[2],
            "unit_price": item_row[3],
            "total_price": item_row[4]
        })
    
    invoice["items"] = items
    
    conn.close()
    return invoice


# Auto-initialize on import
if not os.path.exists(DB_PATH):
    init_invoice_db()
