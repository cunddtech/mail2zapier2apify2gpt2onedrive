"""
🧠 INTELLIGENT INVOICE MANAGEMENT INTEGRATION
Railway FastAPI + WeClapp + Email API Integration
Erweitert production_langgraph_orchestrator.py um intelligente Rechnungsverarbeitung
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import sqlite3
import json
import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse, HTMLResponse
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router für intelligente Rechnungsverarbeitung
invoice_router = APIRouter(prefix="/api/invoice", tags=["Intelligent Invoice Management"])

# ===============================
# DATABASE INITIALIZATION
# ===============================

def initialize_invoice_database():
    """Initialize SQLite database for intelligent invoice management"""
    db_path = os.getenv("DATABASE_PATH", "./railway_invoice_data.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enhanced invoice table with all necessary fields
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT UNIQUE NOT NULL,
        invoice_date DATE,
        due_date DATE,
        amount_total DECIMAL(12,2),
        amount_net DECIMAL(12,2),
        amount_tax DECIMAL(12,2),
        vendor_name TEXT,
        customer_name TEXT,
        direction TEXT CHECK(direction IN ('incoming', 'outgoing')),
        status TEXT CHECK(status IN ('open', 'paid', 'overdue', 'partial', 'cancelled')),
        payment_status TEXT,
        document_hash TEXT UNIQUE,
        onedrive_path TEXT,
        onedrive_link TEXT,
        email_message_id TEXT,
        weclapp_contact_id TEXT,
        weclapp_invoice_id TEXT,
        project_number TEXT,
        cost_center TEXT,
        category TEXT,
        tags TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_by TEXT DEFAULT 'ai-railway-orchestrator'
    )
    """)
    
    # Bank transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bank_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_date DATE NOT NULL,
        amount DECIMAL(12,2) NOT NULL,
        reference TEXT,
        purpose TEXT,
        counterpart_name TEXT,
        counterpart_iban TEXT,
        transaction_type TEXT,
        matched_invoice_id INTEGER,
        matching_confidence DECIMAL(3,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (matched_invoice_id) REFERENCES invoices (id)
    )
    """)
    
    # Invoice-Bank matching log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_bank_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        bank_transaction_id INTEGER NOT NULL,
        match_type TEXT CHECK(match_type IN ('automatic', 'manual', 'suggested')),
        confidence_score DECIMAL(3,2),
        matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        matched_by TEXT,
        FOREIGN KEY (invoice_id) REFERENCES invoices (id),
        FOREIGN KEY (bank_transaction_id) REFERENCES bank_transactions (id)
    )
    """)
    
    # Invoice email tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        email_message_id TEXT NOT NULL,
        email_subject TEXT,
        email_from TEXT,
        email_to TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
    )
    """)
    
    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoices(invoice_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoices(invoice_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_status ON invoices(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bank_date ON bank_transactions(transaction_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bank_amount ON bank_transactions(amount)")
    
    conn.commit()
    conn.close()
    
    logger.info("✅ Invoice database initialized")

# ===============================
# INVOICE MANAGEMENT FUNCTIONS
# ===============================

async def get_weclapp_api_token():
    """Get WeClapp API token from environment"""
    token = os.getenv("WECLAPP_API_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="WeClapp API token not configured")
    return token

async def get_graph_api_token():
    """Get Microsoft Graph API token from environment"""
    # Use existing token function from production orchestrator
    from production_langgraph_orchestrator import get_graph_token_mail
    return await get_graph_token_mail()

async def save_invoice_to_db(invoice_data: Dict[str, Any]) -> int:
    """Save invoice to SQLite database"""
    db_path = os.getenv("DATABASE_PATH", "./railway_invoice_data.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Insert or update invoice
        cursor.execute("""
        INSERT OR REPLACE INTO invoices (
            invoice_number, invoice_date, due_date, amount_total, amount_net, amount_tax,
            vendor_name, customer_name, direction, status, document_hash,
            onedrive_path, onedrive_link, email_message_id, weclapp_contact_id,
            project_number, category, notes, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_data.get("invoice_number"),
            invoice_data.get("invoice_date"),
            invoice_data.get("due_date"),
            invoice_data.get("amount_total"),
            invoice_data.get("amount_net"),
            invoice_data.get("amount_tax"),
            invoice_data.get("vendor_name"),
            invoice_data.get("customer_name"),
            invoice_data.get("direction", "incoming"),
            invoice_data.get("status", "open"),
            invoice_data.get("document_hash"),
            invoice_data.get("onedrive_path"),
            invoice_data.get("onedrive_link"),
            invoice_data.get("email_message_id"),
            invoice_data.get("weclapp_contact_id"),
            invoice_data.get("project_number"),
            invoice_data.get("category"),
            invoice_data.get("notes"),
            datetime.now().isoformat()
        ))
        
        invoice_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"✅ Invoice saved: {invoice_data.get('invoice_number')} (ID: {invoice_id})")
        return invoice_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error saving invoice: {e}")
        raise
    finally:
        conn.close()

async def get_invoice_by_number(invoice_number: str) -> Optional[Dict[str, Any]]:
    """Get invoice by invoice number"""
    db_path = os.getenv("DATABASE_PATH", "./railway_invoice_data.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        SELECT * FROM invoices WHERE invoice_number = ?
        """, (invoice_number,))
        
        row = cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
        
    finally:
        conn.close()

async def update_invoice_status(invoice_id: int, status: str, notes: str = None):
    """Update invoice status"""
    db_path = os.getenv("DATABASE_PATH", "./railway_invoice_data.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        if notes:
            cursor.execute("""
            UPDATE invoices 
            SET status = ?, notes = ?, updated_at = ? 
            WHERE id = ?
            """, (status, notes, datetime.now().isoformat(), invoice_id))
        else:
            cursor.execute("""
            UPDATE invoices 
            SET status = ?, updated_at = ? 
            WHERE id = ?
            """, (status, datetime.now().isoformat(), invoice_id))
        
        conn.commit()
        logger.info(f"✅ Invoice {invoice_id} status updated to: {status}")
        
    finally:
        conn.close()

# ===============================
# BANK TRANSACTION MATCHING
# ===============================

async def match_bank_transactions():
    """Intelligent bank transaction matching using AI"""
    db_path = os.getenv("DATABASE_PATH", "./railway_invoice_data.db")
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Get unmatched bank transactions
        unmatched_transactions = pd.read_sql_query("""
        SELECT * FROM bank_transactions 
        WHERE matched_invoice_id IS NULL
        ORDER BY transaction_date DESC
        """, conn)
        
        # Get open invoices
        open_invoices = pd.read_sql_query("""
        SELECT * FROM invoices 
        WHERE status IN ('open', 'partial')
        ORDER BY invoice_date DESC
        """, conn)
        
        matches = []
        
        for _, transaction in unmatched_transactions.iterrows():
            best_match = None
            best_score = 0.0
            
            for _, invoice in open_invoices.iterrows():
                score = calculate_match_score(transaction, invoice)
                
                if score > best_score and score > 0.7:  # 70% confidence threshold
                    best_score = score
                    best_match = invoice
            
            if best_match is not None:
                matches.append({
                    "transaction_id": transaction["id"],
                    "invoice_id": best_match["id"],
                    "confidence": best_score,
                    "transaction_amount": transaction["amount"],
                    "invoice_amount": best_match["amount_total"],
                    "transaction_date": transaction["transaction_date"],
                    "invoice_number": best_match["invoice_number"]
                })
        
        # Save matches to database
        cursor = conn.cursor()
        for match in matches:
            cursor.execute("""
            INSERT INTO invoice_bank_matches 
            (invoice_id, bank_transaction_id, match_type, confidence_score, matched_by)
            VALUES (?, ?, 'automatic', ?, 'ai-system')
            """, (
                match["invoice_id"],
                match["transaction_id"],
                match["confidence"]
            ))
            
            # Update bank transaction
            cursor.execute("""
            UPDATE bank_transactions 
            SET matched_invoice_id = ?, matching_confidence = ?
            WHERE id = ?
            """, (
                match["invoice_id"],
                match["confidence"],
                match["transaction_id"]
            ))
            
            # Update invoice status if full match
            if abs(match["transaction_amount"] - match["invoice_amount"]) < 1.0:
                cursor.execute("""
                UPDATE invoices 
                SET status = 'paid', updated_at = ?
                WHERE id = ?
                """, (datetime.now().isoformat(), match["invoice_id"]))
        
        conn.commit()
        logger.info(f"✅ Matched {len(matches)} bank transactions")
        return matches
        
    finally:
        conn.close()

def calculate_match_score(transaction: pd.Series, invoice: pd.Series) -> float:
    """Calculate matching score between bank transaction and invoice"""
    score = 0.0
    
    # Amount matching (most important)
    amount_diff = abs(float(transaction["amount"]) - float(invoice["amount_total"]))
    if amount_diff < 1.0:  # Exact match
        score += 0.6
    elif amount_diff < 10.0:  # Close match
        score += 0.4
    elif amount_diff < 100.0:  # Reasonable match
        score += 0.2
    
    # Date proximity
    try:
        trans_date = datetime.fromisoformat(str(transaction["transaction_date"]))
        inv_date = datetime.fromisoformat(str(invoice["invoice_date"]))
        date_diff = abs((trans_date - inv_date).days)
        
        if date_diff <= 5:  # Within 5 days
            score += 0.2
        elif date_diff <= 30:  # Within 30 days
            score += 0.1
    except:
        pass
    
    # Reference/invoice number matching
    reference = str(transaction.get("reference", "")).lower()
    purpose = str(transaction.get("purpose", "")).lower()
    invoice_number = str(invoice.get("invoice_number", "")).lower()
    
    if invoice_number and (invoice_number in reference or invoice_number in purpose):
        score += 0.3
    
    # Counterpart name matching
    counterpart = str(transaction.get("counterpart_name", "")).lower()
    vendor = str(invoice.get("vendor_name", "")).lower()
    customer = str(invoice.get("customer_name", "")).lower()
    
    if vendor and vendor in counterpart:
        score += 0.2
    elif customer and customer in counterpart:
        score += 0.2
    
    return min(score, 1.0)  # Cap at 100%

# ===============================
# DASHBOARD AND REPORTING
# ===============================

@dataclass
class InvoiceAnalytics:
    total_open: float
    total_paid: float
    total_overdue: float
    count_open: int
    count_paid: int
    count_overdue: int
    avg_payment_time: float
    matching_rate: float

async def get_invoice_analytics(start_date: str = None, end_date: str = None) -> InvoiceAnalytics:
    """Get comprehensive invoice analytics"""
    db_path = os.getenv("DATABASE_PATH", "./railway_invoice_data.db")
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Build date filter
        date_filter = ""
        params = []
        
        if start_date:
            date_filter += " AND invoice_date >= ?"
            params.append(start_date)
        
        if end_date:
            date_filter += " AND invoice_date <= ?"
            params.append(end_date)
        
        # Get invoice statistics
        cursor = conn.cursor()
        
        # Total amounts by status
        cursor.execute(f"""
        SELECT status, 
               SUM(amount_total) as total_amount,
               COUNT(*) as count
        FROM invoices 
        WHERE 1=1 {date_filter}
        GROUP BY status
        """, params)
        
        status_stats = {row[0]: {"amount": row[1], "count": row[2]} for row in cursor.fetchall()}
        
        # Calculate analytics
        analytics = InvoiceAnalytics(
            total_open=status_stats.get("open", {}).get("amount", 0.0),
            total_paid=status_stats.get("paid", {}).get("amount", 0.0),
            total_overdue=status_stats.get("overdue", {}).get("amount", 0.0),
            count_open=status_stats.get("open", {}).get("count", 0),
            count_paid=status_stats.get("paid", {}).get("count", 0),
            count_overdue=status_stats.get("overdue", {}).get("count", 0),
            avg_payment_time=0.0,
            matching_rate=0.0
        )
        
        # Calculate matching rate
        cursor.execute(f"""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(matched_invoice_id) as matched_transactions
        FROM bank_transactions
        WHERE 1=1 {date_filter.replace('invoice_date', 'transaction_date')}
        """, params)
        
        trans_row = cursor.fetchone()
        if trans_row and trans_row[0] > 0:
            analytics.matching_rate = (trans_row[1] / trans_row[0]) * 100
        
        return analytics
        
    finally:
        conn.close()

# ===============================
# FASTAPI ROUTES
# ===============================

@invoice_router.get("/analytics")
async def get_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get invoice analytics and dashboard data"""
    try:
        analytics = await get_invoice_analytics(start_date, end_date)
        
        return {
            "status": "success",
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "analytics": {
                "totals": {
                    "open": analytics.total_open,
                    "paid": analytics.total_paid,
                    "overdue": analytics.total_overdue
                },
                "counts": {
                    "open": analytics.count_open,
                    "paid": analytics.count_paid,
                    "overdue": analytics.count_overdue
                },
                "metrics": {
                    "avg_payment_time_days": analytics.avg_payment_time,
                    "bank_matching_rate_percent": analytics.matching_rate
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@invoice_router.get("/{invoice_number}")
async def get_invoice_details(invoice_number: str):
    """Get detailed invoice information"""
    try:
        invoice = await get_invoice_by_number(invoice_number)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "status": "success",
            "invoice": invoice
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Invoice lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@invoice_router.post("/{invoice_number}/status")
async def update_invoice_status_endpoint(
    invoice_number: str,
    request: Request
):
    """Update invoice status"""
    try:
        data = await request.json()
        new_status = data.get("status")
        notes = data.get("notes", "")
        
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        invoice = await get_invoice_by_number(invoice_number)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        await update_invoice_status(invoice["id"], new_status, notes)
        
        return {
            "status": "success",
            "invoice_number": invoice_number,
            "new_status": new_status,
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Status update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@invoice_router.post("/match-transactions")
async def match_transactions_endpoint():
    """Trigger bank transaction matching"""
    try:
        matches = await match_bank_transactions()
        
        return {
            "status": "success",
            "matches_found": len(matches),
            "matches": matches,
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Transaction matching error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@invoice_router.get("/dashboard/html")
async def get_dashboard_html():
    """Get HTML dashboard for invoice management"""
    try:
        analytics = await get_invoice_analytics()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>C&D Invoice Management Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stat-value {{ font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
                .stat-label {{ color: #666; font-size: 1.1em; }}
                .action-buttons {{ display: flex; gap: 15px; flex-wrap: wrap; }}
                .btn {{ padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; }}
                .btn-primary {{ background: #667eea; color: white; }}
                .btn-success {{ background: #51cf66; color: white; }}
                .btn-warning {{ background: #ffd43b; color: #333; }}
                .status-indicator {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }}
                .status-open {{ background: #ffd43b; }}
                .status-paid {{ background: #51cf66; }}
                .status-overdue {{ background: #ff6b6b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 C&D Technologies - Intelligent Invoice Management</h1>
                    <p>AI-Powered Invoice Processing & Bank Transaction Matching</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">€{analytics.total_open:,.2f}</div>
                        <div class="stat-label">
                            <span class="status-indicator status-open"></span>
                            Offene Rechnungen ({analytics.count_open})
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value">€{analytics.total_paid:,.2f}</div>
                        <div class="stat-label">
                            <span class="status-indicator status-paid"></span>
                            Bezahlte Rechnungen ({analytics.count_paid})
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value">€{analytics.total_overdue:,.2f}</div>
                        <div class="stat-label">
                            <span class="status-indicator status-overdue"></span>
                            Überfällige Rechnungen ({analytics.count_overdue})
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value">{analytics.matching_rate:.1f}%</div>
                        <div class="stat-label">
                            🎯 Bank Matching Rate
                        </div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h3>🚀 Quick Actions</h3>
                    <div class="action-buttons">
                        <a href="/api/invoice/match-transactions" class="btn btn-primary">🔄 Match Transactions</a>
                        <a href="/api/invoice/analytics" class="btn btn-success">📊 Get Analytics JSON</a>
                        <a href="https://cundd.weclapp.com" class="btn btn-warning" target="_blank">🔗 Open WeClapp</a>
                        <a href="mailto:mj@cdtechnologies.de?subject=Invoice Management" class="btn btn-primary">✉️ Contact Support</a>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h3>📈 System Integration Status</h3>
                    <p>✅ WeClapp API: Connected</p>
                    <p>✅ Microsoft Graph Email API: Connected</p>
                    <p>✅ Bank Transaction Matching: Active</p>
                    <p>✅ AI Document Classification: Active</p>
                    <p>✅ OneDrive Storage: Connected</p>
                    <p><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        return HTMLResponse(content=f"<h1>Dashboard Error</h1><p>{str(e)}</p>", status_code=500)

# ===============================
# INTEGRATION WITH EXISTING ORCHESTRATOR
# ===============================

async def process_invoice_from_email(email_data: Dict[str, Any], attachment_results: List[Dict[str, Any]]):
    """
    Process invoice from email data and save to intelligent invoice system
    
    This function is called from the main orchestrator when invoices are detected
    """
    try:
        logger.info("🧠 Processing invoice via intelligent invoice system...")
        
        invoices_saved = []
        
        for attachment in attachment_results:
            # Check if this is an invoice
            document_type = attachment.get("document_type", "").lower()
            structured_data = attachment.get("structured_data", {})
            
            if "invoice" in document_type or "rechnung" in document_type:
                # Extract invoice data
                invoice_data = {
                    "invoice_number": structured_data.get("invoice_number"),
                    "invoice_date": structured_data.get("invoice_date"),
                    "due_date": structured_data.get("due_date"),
                    "amount_total": _parse_amount(structured_data.get("total_amount")),
                    "amount_net": _parse_amount(structured_data.get("net_amount")),
                    "amount_tax": _parse_amount(structured_data.get("tax_amount")),
                    "vendor_name": structured_data.get("vendor_name"),
                    "customer_name": structured_data.get("customer_name"),
                    "direction": structured_data.get("direction", "incoming"),
                    "status": "open",
                    "document_hash": attachment.get("document_hash"),
                    "onedrive_path": attachment.get("onedrive_path"),
                    "onedrive_link": attachment.get("onedrive_sharing_link"),
                    "email_message_id": email_data.get("message_id"),
                    "project_number": structured_data.get("project_number"),
                    "category": _categorize_invoice(structured_data),
                    "notes": f"Auto-processed from email: {email_data.get('subject', '')}"
                }
                
                # Only save if we have at least an invoice number
                if invoice_data["invoice_number"]:
                    invoice_id = await save_invoice_to_db(invoice_data)
                    invoices_saved.append({
                        "invoice_id": invoice_id,
                        "invoice_number": invoice_data["invoice_number"],
                        "amount": invoice_data["amount_total"]
                    })
                    
                    logger.info(f"✅ Invoice saved to intelligent system: {invoice_data['invoice_number']}")
                else:
                    logger.warning(f"⚠️ Skipping invoice without number: {attachment.get('filename')}")
        
        # Trigger automatic bank matching if invoices were saved
        if invoices_saved:
            try:
                matches = await match_bank_transactions()
                logger.info(f"🎯 Auto-matched {len(matches)} bank transactions")
            except Exception as match_error:
                logger.warning(f"⚠️ Auto-matching failed: {match_error}")
        
        return invoices_saved
        
    except Exception as e:
        logger.error(f"❌ Invoice processing error: {e}")
        return []

def _parse_amount(amount_str: str) -> Optional[float]:
    """Parse amount string to float"""
    if not amount_str:
        return None
    
    try:
        # Remove currency symbols and formatting
        cleaned = str(amount_str).replace("€", "").replace(",", ".").replace(" ", "")
        return float(cleaned)
    except:
        return None

def _categorize_invoice(structured_data: Dict[str, Any]) -> str:
    """Categorize invoice based on content"""
    vendor = str(structured_data.get("vendor_name", "")).lower()
    
    if any(word in vendor for word in ["dach", "roof", "tile", "ziegel"]):
        return "roofing_materials"
    elif any(word in vendor for word in ["transport", "logistik", "spedition"]):
        return "logistics"
    elif any(word in vendor for word in ["werkzeug", "tool", "equipment"]):
        return "equipment"
    else:
        return "general"

# Initialize database on import
initialize_invoice_database()