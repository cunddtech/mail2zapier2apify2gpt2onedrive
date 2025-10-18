"""
💰 Payment Matching System
Automatischer Abgleich: Rechnung ↔ Bankumsatz
"""

import sqlite3
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

PAYMENT_DB_PATH = "/tmp/payment_tracking.db"


def init_payment_db():
    """Initialize Payment Tracking Database"""
    
    conn = sqlite3.connect(PAYMENT_DB_PATH)
    cursor = conn.cursor()
    
    # Bank Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bank_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            transaction_date DATE NOT NULL,
            value_date DATE,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'EUR',
            sender_name TEXT,
            sender_iban TEXT,
            receiver_name TEXT,
            receiver_iban TEXT,
            purpose TEXT,
            reference TEXT,
            transaction_type TEXT,  -- credit, debit
            matched_invoice_id INTEGER,
            matched_at DATETIME,
            match_confidence REAL,
            match_method TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (matched_invoice_id) REFERENCES invoices(id)
        )
    """)
    
    # Payment Matches Table - History of all matches
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            invoice_id INTEGER NOT NULL,
            match_confidence REAL NOT NULL,
            match_method TEXT NOT NULL,
            matched_by TEXT,  -- auto, manual
            matched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'confirmed',  -- confirmed, rejected, pending
            notes TEXT,
            FOREIGN KEY (transaction_id) REFERENCES bank_transactions(id),
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        )
    """)
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_date ON bank_transactions(transaction_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_amount ON bank_transactions(amount)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sender_iban ON bank_transactions(sender_iban)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_matched_invoice ON bank_transactions(matched_invoice_id)")
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Payment Tracking DB initialized: {PAYMENT_DB_PATH}")


def import_bank_transaction(transaction_data: Dict) -> int:
    """
    Import single bank transaction
    
    Args:
        transaction_data: Dict with transaction details
        
    Returns:
        transaction_id: Primary key of saved transaction
    """
    
    conn = sqlite3.connect(PAYMENT_DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO bank_transactions (
                transaction_id, transaction_date, value_date,
                amount, currency, sender_name, sender_iban,
                receiver_name, receiver_iban, purpose, reference,
                transaction_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction_data.get("transaction_id"),
            transaction_data.get("transaction_date"),
            transaction_data.get("value_date"),
            transaction_data.get("amount"),
            transaction_data.get("currency", "EUR"),
            transaction_data.get("sender_name"),
            transaction_data.get("sender_iban"),
            transaction_data.get("receiver_name"),
            transaction_data.get("receiver_iban"),
            transaction_data.get("purpose"),
            transaction_data.get("reference"),
            transaction_data.get("transaction_type", "credit" if transaction_data.get("amount", 0) > 0 else "debit")
        ))
        
        transaction_db_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"✅ Transaction imported: {transaction_data.get('transaction_id')} (DB ID: {transaction_db_id})")
        
        return transaction_db_id
        
    except sqlite3.IntegrityError:
        logger.warning(f"⚠️ Transaction {transaction_data.get('transaction_id')} already exists")
        
        # Get existing ID
        cursor.execute("SELECT id FROM bank_transactions WHERE transaction_id = ?", 
                      (transaction_data.get("transaction_id"),))
        result = cursor.fetchone()
        return result[0] if result else None
        
    finally:
        conn.close()


def extract_invoice_number_from_text(text: str) -> Optional[str]:
    """
    Extract invoice number from payment purpose/reference text
    
    Patterns:
    - RE-2025-001
    - Rechnung 123456
    - Invoice #12345
    - RG 2025/001
    """
    
    if not text:
        return None
    
    # Pattern 1: RE-YYYY-NNN
    match = re.search(r'RE-\d{4}-\d+', text, re.IGNORECASE)
    if match:
        return match.group(0)
    
    # Pattern 2: Rechnung NNNNNN
    match = re.search(r'(?:Rechnung|Invoice|RG)\s*[#:]?\s*(\d+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 3: Generic number pattern (6+ digits)
    match = re.search(r'\b\d{6,}\b', text)
    if match:
        return match.group(0)
    
    return None


def calculate_match_confidence(
    invoice: Dict,
    transaction: Dict,
    match_factors: Dict
) -> Tuple[float, str]:
    """
    Calculate confidence score for invoice-transaction match
    
    Returns:
        (confidence_score, match_method)
    """
    
    confidence = 0.0
    methods = []
    
    # Factor 1: Exact Amount Match (40 points)
    if abs(float(invoice.get("amount_total", 0)) - abs(float(transaction.get("amount", 0)))) < 0.01:
        confidence += 0.40
        methods.append("amount_exact")
    elif abs(float(invoice.get("amount_total", 0)) - abs(float(transaction.get("amount", 0)))) < 1.0:
        # Close but not exact (within 1 EUR)
        confidence += 0.20
        methods.append("amount_close")
    
    # Factor 2: Invoice Number in Purpose/Reference (30 points)
    purpose_text = f"{transaction.get('purpose', '')} {transaction.get('reference', '')}"
    extracted_invoice_num = extract_invoice_number_from_text(purpose_text)
    
    if extracted_invoice_num and invoice.get("invoice_number"):
        if extracted_invoice_num == invoice.get("invoice_number"):
            confidence += 0.30
            methods.append("invoice_number_exact")
        elif extracted_invoice_num in invoice.get("invoice_number") or invoice.get("invoice_number") in extracted_invoice_num:
            confidence += 0.15
            methods.append("invoice_number_partial")
    
    # Factor 3: Vendor/Customer Name Match (20 points)
    vendor_name = invoice.get("vendor_name", "").lower()
    sender_name = transaction.get("sender_name", "").lower()
    
    if vendor_name and sender_name:
        # Exact match
        if vendor_name == sender_name:
            confidence += 0.20
            methods.append("name_exact")
        # Partial match (any word)
        elif any(word in sender_name for word in vendor_name.split() if len(word) > 3):
            confidence += 0.10
            methods.append("name_partial")
    
    # Factor 4: Date Proximity (10 points)
    # Transaction should be within 60 days of due date
    if invoice.get("due_date") and transaction.get("transaction_date"):
        try:
            due_date = datetime.fromisoformat(invoice["due_date"]).date()
            trans_date = datetime.fromisoformat(transaction["transaction_date"]).date()
            
            days_diff = abs((trans_date - due_date).days)
            
            if days_diff <= 7:
                confidence += 0.10
                methods.append("date_close")
            elif days_diff <= 30:
                confidence += 0.05
                methods.append("date_medium")
        except:
            pass
    
    match_method = "+".join(methods) if methods else "no_match"
    
    return (confidence, match_method)


def find_matching_invoice(transaction: Dict, invoice_db_path: str = "/tmp/invoice_tracking.db") -> Optional[Dict]:
    """
    Find matching invoice for a bank transaction
    
    Args:
        transaction: Bank transaction dict
        invoice_db_path: Path to invoice database
        
    Returns:
        Best matching invoice with confidence score, or None
    """
    
    import os
    if not os.path.exists(invoice_db_path):
        logger.warning(f"⚠️ Invoice DB not found: {invoice_db_path}")
        return None
    
    conn = sqlite3.connect(invoice_db_path)
    cursor = conn.cursor()
    
    # Get all open invoices with matching direction
    # For incoming money (credit) → match outgoing invoices (our invoices to customers)
    # For outgoing money (debit) → match incoming invoices (vendor invoices we pay)
    
    transaction_amount = float(transaction.get("amount", 0))
    
    if transaction_amount > 0:
        # Credit (money in) → our outgoing invoices
        direction = "outgoing"
    else:
        # Debit (money out) → incoming invoices we need to pay
        direction = "incoming"
    
    cursor.execute("""
        SELECT * FROM invoices 
        WHERE status = 'open' 
        AND direction = ?
        AND ABS(amount_total - ?) < 10000  -- Pre-filter by amount (within 10k EUR)
        ORDER BY created_at DESC
    """, (direction, abs(transaction_amount)))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        logger.info(f"   No open {direction} invoices found for matching")
        return None
    
    # Convert to dicts
    columns = [desc[0] for desc in cursor.description]
    invoices = [dict(zip(columns, row)) for row in rows]
    
    # Calculate confidence for each invoice
    best_match = None
    best_confidence = 0.0
    
    for invoice in invoices:
        confidence, match_method = calculate_match_confidence(
            invoice, transaction, {}
        )
        
        if confidence > best_confidence:
            best_confidence = confidence
            best_match = invoice
            best_match["match_confidence"] = confidence
            best_match["match_method"] = match_method
    
    # Only return if confidence > 50%
    if best_match and best_confidence >= 0.5:
        logger.info(f"   ✅ Match found: Invoice {best_match['invoice_number']} (confidence: {best_confidence:.0%})")
        return best_match
    elif best_match:
        logger.info(f"   ⚠️ Low confidence match: {best_confidence:.0%} - requires manual review")
        return None
    else:
        logger.info(f"   ❌ No matching invoice found")
        return None


def match_transaction_to_invoice(transaction_db_id: int, invoice_number: str, matched_by: str = "auto") -> bool:
    """
    Create match between transaction and invoice
    
    Args:
        transaction_db_id: ID in bank_transactions table
        invoice_number: Invoice number to match
        matched_by: 'auto' or 'manual'
        
    Returns:
        Success status
    """
    
    # Get invoice ID from invoice DB
    import os
    invoice_db_path = "/tmp/invoice_tracking.db"
    
    if not os.path.exists(invoice_db_path):
        logger.error("❌ Invoice DB not found")
        return False
    
    inv_conn = sqlite3.connect(invoice_db_path)
    inv_cursor = inv_conn.cursor()
    
    inv_cursor.execute("SELECT id FROM invoices WHERE invoice_number = ?", (invoice_number,))
    result = inv_cursor.fetchone()
    
    if not result:
        logger.error(f"❌ Invoice {invoice_number} not found")
        inv_conn.close()
        return False
    
    invoice_id = result[0]
    inv_conn.close()
    
    # Create match record
    pay_conn = sqlite3.connect(PAYMENT_DB_PATH)
    pay_cursor = pay_conn.cursor()
    
    try:
        pay_cursor.execute("""
            INSERT INTO payment_matches (
                transaction_id, invoice_id, match_confidence,
                match_method, matched_by, status
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (transaction_db_id, invoice_id, 1.0, "manual", matched_by, "confirmed"))
        
        # Update transaction
        pay_cursor.execute("""
            UPDATE bank_transactions SET
                matched_invoice_id = ?,
                matched_at = ?,
                match_confidence = 1.0,
                match_method = ?
            WHERE id = ?
        """, (invoice_id, datetime.utcnow().isoformat(), "manual", transaction_db_id))
        
        pay_conn.commit()
        
        logger.info(f"✅ Match created: Transaction {transaction_db_id} → Invoice {invoice_number}")
        
        # Mark invoice as paid
        inv_conn = sqlite3.connect(invoice_db_path)
        inv_cursor = inv_conn.cursor()
        
        # Get transaction date
        pay_cursor.execute("SELECT transaction_date FROM bank_transactions WHERE id = ?", (transaction_db_id,))
        trans_date = pay_cursor.fetchone()[0]
        
        inv_cursor.execute("""
            UPDATE invoices SET
                status = 'paid',
                payment_date = ?,
                payment_method = 'bank_transfer',
                updated_at = ?
            WHERE invoice_number = ?
        """, (trans_date, datetime.utcnow().isoformat(), invoice_number))
        
        inv_conn.commit()
        inv_conn.close()
        
        logger.info(f"   💰 Invoice {invoice_number} marked as PAID")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Match creation failed: {e}")
        return False
        
    finally:
        pay_conn.close()


def auto_match_all_transactions(min_confidence: float = 0.7) -> Dict:
    """
    Auto-match all unmatched transactions to invoices
    
    Args:
        min_confidence: Minimum confidence threshold (0.0-1.0)
        
    Returns:
        Statistics dict
    """
    
    pay_conn = sqlite3.connect(PAYMENT_DB_PATH)
    pay_cursor = pay_conn.cursor()
    
    # Get all unmatched transactions
    pay_cursor.execute("""
        SELECT * FROM bank_transactions 
        WHERE matched_invoice_id IS NULL
        ORDER BY transaction_date DESC
    """)
    
    rows = pay_cursor.fetchall()
    pay_conn.close()
    
    if not rows:
        logger.info("   No unmatched transactions found")
        return {"processed": 0, "matched": 0, "unmatched": 0}
    
    columns = [desc[0] for desc in pay_cursor.description]
    transactions = [dict(zip(columns, row)) for row in rows]
    
    stats = {
        "processed": len(transactions),
        "matched": 0,
        "unmatched": 0,
        "low_confidence": 0
    }
    
    logger.info(f"🔍 Auto-matching {len(transactions)} transactions...")
    
    for transaction in transactions:
        logger.info(f"\n   Transaction: {transaction['transaction_date']} | {transaction['amount']} EUR | {transaction.get('purpose', '')[:50]}")
        
        matching_invoice = find_matching_invoice(transaction)
        
        if matching_invoice:
            confidence = matching_invoice.get("match_confidence", 0.0)
            
            if confidence >= min_confidence:
                # Auto-match
                success = match_transaction_to_invoice(
                    transaction["id"],
                    matching_invoice["invoice_number"],
                    matched_by="auto"
                )
                
                if success:
                    stats["matched"] += 1
                else:
                    stats["unmatched"] += 1
            else:
                logger.info(f"   ⚠️ Confidence {confidence:.0%} below threshold {min_confidence:.0%} - skipping")
                stats["low_confidence"] += 1
        else:
            stats["unmatched"] += 1
    
    return stats


def get_unmatched_transactions() -> List[Dict]:
    """Get all unmatched bank transactions"""
    
    conn = sqlite3.connect(PAYMENT_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM bank_transactions 
        WHERE matched_invoice_id IS NULL
        ORDER BY transaction_date DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def get_payment_statistics() -> Dict:
    """Get payment matching statistics"""
    
    pay_conn = sqlite3.connect(PAYMENT_DB_PATH)
    pay_cursor = pay_conn.cursor()
    
    # Total transactions
    pay_cursor.execute("SELECT COUNT(*) FROM bank_transactions")
    total_transactions = pay_cursor.fetchone()[0]
    
    # Matched
    pay_cursor.execute("SELECT COUNT(*) FROM bank_transactions WHERE matched_invoice_id IS NOT NULL")
    matched_count = pay_cursor.fetchone()[0]
    
    # Total matched amount
    pay_cursor.execute("SELECT SUM(ABS(amount)) FROM bank_transactions WHERE matched_invoice_id IS NOT NULL")
    matched_amount = pay_cursor.fetchone()[0] or 0.0
    
    pay_conn.close()
    
    return {
        "total_transactions": total_transactions,
        "matched_count": matched_count,
        "unmatched_count": total_transactions - matched_count,
        "match_rate": (matched_count / total_transactions * 100) if total_transactions > 0 else 0.0,
        "matched_amount": matched_amount
    }


# Auto-initialize on import
import os
if not os.path.exists(PAYMENT_DB_PATH):
    init_payment_db()
