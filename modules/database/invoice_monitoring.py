#!/usr/bin/env python3
"""
📊 RECHNUNGSPROZESS MONITORING SYSTEM
===================================

PRODUKTIVES SYSTEM für C&D Technologies:
✅ Eingehende Rechnungen Tracking
✅ Ausgehende Rechnungen Status  
✅ Umsatzabgleich & Compliance
✅ Fälligkeitsüberwachung
✅ Kritische Punkte Dashboard

Database: invoice_monitoring.db
Integration: WeClapp CRM + Email Processing
"""

import sqlite3
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Database Configuration
INVOICE_DB_PATH = "invoice_monitoring.db"

@dataclass
class IncomingInvoice:
    """📥 Eingehende Rechnung"""
    id: Optional[int] = None
    invoice_number: str = ""
    sender: str = ""
    sender_company: str = ""
    amount: float = 0.0
    currency: str = "EUR"
    invoice_date: str = ""
    due_date: str = ""
    received_date: str = ""
    payment_status: str = "open"  # open, paid, overdue
    payment_date: Optional[str] = None
    email_message_id: Optional[str] = None
    pdf_path: Optional[str] = None
    weclapp_vendor_id: Optional[str] = None
    category: str = ""  # material, service, office, etc.
    notes: str = ""
    created_at: str = ""
    
@dataclass 
class OutgoingInvoice:
    """📤 Ausgehende Rechnung"""
    id: Optional[int] = None
    invoice_number: str = ""
    customer: str = ""
    customer_company: str = ""
    amount: float = 0.0
    currency: str = "EUR"
    invoice_date: str = ""
    due_date: str = ""
    sent_date: str = ""
    payment_status: str = "open"  # open, paid, partial, overdue
    payment_date: Optional[str] = None
    weclapp_customer_id: Optional[str] = None
    weclapp_opportunity_id: Optional[str] = None
    project_name: str = ""
    payment_terms: str = "30 Tage"
    reminder_count: int = 0
    last_reminder_date: Optional[str] = None
    notes: str = ""
    created_at: str = ""

class InvoiceMonitoringDB:
    """📊 Rechnungsüberwachung Database Manager"""
    
    def __init__(self, db_path: str = INVOICE_DB_PATH):
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        """🔧 Database Schema erstellen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Eingehende Rechnungen
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS incoming_invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE,
                sender TEXT,
                sender_company TEXT,
                amount REAL,
                currency TEXT DEFAULT 'EUR',
                invoice_date TEXT,
                due_date TEXT,
                received_date TEXT,
                payment_status TEXT DEFAULT 'open',
                payment_date TEXT,
                email_message_id TEXT,
                pdf_path TEXT,
                weclapp_vendor_id TEXT,
                category TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Ausgehende Rechnungen 
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS outgoing_invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE,
                customer TEXT,
                customer_company TEXT,
                amount REAL,
                currency TEXT DEFAULT 'EUR',
                invoice_date TEXT,
                due_date TEXT,
                sent_date TEXT,
                payment_status TEXT DEFAULT 'open',
                payment_date TEXT,
                weclapp_customer_id TEXT,
                weclapp_opportunity_id TEXT,
                project_name TEXT,
                payment_terms TEXT DEFAULT '30 Tage',
                reminder_count INTEGER DEFAULT 0,
                last_reminder_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Umsatz-Tracking (für Abgleich)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS revenue_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT,
                amount REAL,
                description TEXT,
                invoice_reference TEXT,
                bank_reference TEXT,
                matched_invoice_id TEXT,
                transaction_type TEXT, -- income, expense
                source TEXT, -- bank_import, manual, weclapp_sync
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()
            logger.info("✅ Invoice monitoring database initialized")
    
    def add_incoming_invoice(self, invoice: IncomingInvoice) -> int:
        """📥 Eingehende Rechnung hinzufügen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT OR REPLACE INTO incoming_invoices 
            (invoice_number, sender, sender_company, amount, currency, 
             invoice_date, due_date, received_date, payment_status, 
             email_message_id, pdf_path, weclapp_vendor_id, category, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice.invoice_number, invoice.sender, invoice.sender_company,
                invoice.amount, invoice.currency, invoice.invoice_date,
                invoice.due_date, invoice.received_date, invoice.payment_status,
                invoice.email_message_id, invoice.pdf_path, invoice.weclapp_vendor_id,
                invoice.category, invoice.notes
            ))
            
            invoice_id = cursor.lastrowid
            conn.commit()
            logger.info(f"📥 Incoming invoice added: {invoice.invoice_number}")
            return invoice_id
    
    def add_outgoing_invoice(self, invoice: OutgoingInvoice) -> int:
        """📤 Ausgehende Rechnung hinzufügen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT OR REPLACE INTO outgoing_invoices 
            (invoice_number, customer, customer_company, amount, currency,
             invoice_date, due_date, sent_date, payment_status,
             weclapp_customer_id, weclapp_opportunity_id, project_name,
             payment_terms, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice.invoice_number, invoice.customer, invoice.customer_company,
                invoice.amount, invoice.currency, invoice.invoice_date,
                invoice.due_date, invoice.sent_date, invoice.payment_status,
                invoice.weclapp_customer_id, invoice.weclapp_opportunity_id,
                invoice.project_name, invoice.payment_terms, invoice.notes
            ))
            
            invoice_id = cursor.lastrowid
            conn.commit()
            logger.info(f"📤 Outgoing invoice added: {invoice.invoice_number}")
            return invoice_id
    
    def get_overdue_incoming_invoices(self, days_overdue: int = 0) -> List[Dict]:
        """⚠️ Überfällige eingehende Rechnungen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("""
            SELECT * FROM incoming_invoices 
            WHERE payment_status = 'open' 
            AND due_date < date('now', '-{} days')
            ORDER BY due_date ASC
            """.format(days_overdue))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_overdue_outgoing_invoices(self, days_overdue: int = 0) -> List[Dict]:
        """⚠️ Überfällige ausgehende Rechnungen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM outgoing_invoices 
            WHERE payment_status = 'open'
            AND due_date < date('now', '-{} days')
            ORDER BY due_date ASC
            """.format(days_overdue))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_week_summary(self, weeks_back: int = 1) -> Dict[str, Any]:
        """📊 Wochenzusammenfassung für Umsatzabgleich"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            week_start = (datetime.now() - timedelta(weeks=weeks_back)).strftime('%Y-%m-%d')
            week_end = (datetime.now() - timedelta(weeks=weeks_back-1)).strftime('%Y-%m-%d')
            
            # Eingehende Rechnungen der Woche
            cursor.execute("""
            SELECT COUNT(*) as count, SUM(amount) as total
            FROM incoming_invoices 
            WHERE received_date BETWEEN ? AND ?
            """, (week_start, week_end))
            
            incoming = cursor.fetchone()
            
            # Ausgehende Rechnungen der Woche
            cursor.execute("""
            SELECT COUNT(*) as count, SUM(amount) as total
            FROM outgoing_invoices 
            WHERE sent_date BETWEEN ? AND ?
            """, (week_start, week_end))
            
            outgoing = cursor.fetchone()
            
            return {
                "period": f"{week_start} bis {week_end}",
                "incoming": {"count": incoming[0] or 0, "total": incoming[1] or 0},
                "outgoing": {"count": outgoing[0] or 0, "total": outgoing[1] or 0}
            }
    
    def get_critical_points(self) -> Dict[str, Any]:
        """🔴 Kritische Punkte Zusammenfassung"""
        overdue_incoming = self.get_overdue_incoming_invoices(0)
        overdue_outgoing = self.get_overdue_outgoing_invoices(0)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Offene Beträge
            cursor.execute("""
            SELECT SUM(amount) FROM incoming_invoices WHERE payment_status = 'open'
            """)
            open_incoming_total = cursor.fetchone()[0] or 0
            
            cursor.execute("""
            SELECT SUM(amount) FROM outgoing_invoices WHERE payment_status = 'open'
            """)
            open_outgoing_total = cursor.fetchone()[0] or 0
            
            return {
                "overdue_incoming_count": len(overdue_incoming),
                "overdue_outgoing_count": len(overdue_outgoing),
                "open_incoming_total": open_incoming_total,
                "open_outgoing_total": open_outgoing_total,
                "cash_flow_balance": open_outgoing_total - open_incoming_total,
                "overdue_incoming": overdue_incoming[:5],  # Top 5
                "overdue_outgoing": overdue_outgoing[:5]   # Top 5
            }

# Global instance
invoice_db = InvoiceMonitoringDB()

def process_incoming_invoice_email(email_data: Dict) -> Optional[int]:
    """📥 Email-basierte Rechnungsverarbeitung"""
    try:
        # Extract invoice data from email
        invoice = IncomingInvoice(
            invoice_number=extract_invoice_number(email_data.get('subject', '')),
            sender=email_data.get('from_email_address_address', ''),
            sender_company=extract_company_name(email_data.get('from_email_address_name', '')),
            received_date=datetime.now().strftime('%Y-%m-%d'),
            email_message_id=email_data.get('message_id'),
            category="pending_classification"
        )
        
        return invoice_db.add_incoming_invoice(invoice)
        
    except Exception as e:
        logger.error(f"❌ Error processing incoming invoice: {e}")
        return None

def extract_invoice_number(subject: str) -> str:
    """🔍 Rechnungsnummer aus Email-Betreff extrahieren"""
    import re
    patterns = [
        r'Rechnung[:\s]*([A-Z0-9\-/]+)',
        r'Invoice[:\s]*([A-Z0-9\-/]+)',
        r'RE[:\s]*([A-Z0-9\-/]+)',
        r'([0-9]{4,})',  # Fallback für reine Zahlen
    ]
    
    for pattern in patterns:
        match = re.search(pattern, subject, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return f"UNKNOWN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def extract_company_name(sender_name: str) -> str:
    """🏢 Firmenname aus Absendername extrahieren"""
    # Simple company name extraction
    if 'GmbH' in sender_name or 'AG' in sender_name or 'KG' in sender_name:
        return sender_name
    return ""

if __name__ == "__main__":
    # Test the system
    db = InvoiceMonitoringDB()
    
    # Add sample data
    sample_incoming = IncomingInvoice(
        invoice_number="RE-2025-001",
        sender="max@musterfirma.de",
        sender_company="Musterfirma GmbH",
        amount=1234.56,
        invoice_date="2025-10-20",
        due_date="2025-11-19",
        received_date="2025-10-21",
        category="material"
    )
    
    sample_outgoing = OutgoingInvoice(
        invoice_number="CD-2025-042",
        customer="kunde@example.com",
        customer_company="Example AG",
        amount=5678.90,
        invoice_date="2025-10-25",
        due_date="2025-11-24",
        sent_date="2025-10-25",
        project_name="Dachsanierung München"
    )
    
    print("📥 Adding sample invoices...")
    db.add_incoming_invoice(sample_incoming)
    db.add_outgoing_invoice(sample_outgoing)
    
    print("📊 Critical points:")
    critical = db.get_critical_points()
    print(json.dumps(critical, indent=2, ensure_ascii=False))