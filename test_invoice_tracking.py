"""
🧪 Test Invoice Tracking Database
Demonstriert alle Features der Invoice DB
"""

import asyncio
from modules.database.invoice_tracking_db import (
    init_invoice_db,
    save_invoice,
    get_invoice_by_number,
    get_overdue_invoices,
    get_open_invoices,
    mark_invoice_paid,
    get_invoice_statistics
)
from datetime import datetime, timedelta

async def test_invoice_db():
    """Test complete Invoice Tracking functionality"""
    
    print("=" * 70)
    print("🧪 INVOICE TRACKING DATABASE - FUNCTIONAL TEST")
    print("=" * 70)
    print()
    
    # Initialize database
    print("1️⃣  Initializing Invoice DB...")
    init_invoice_db()
    print("   ✅ Database initialized")
    print()
    
    # Test 1: Save incoming invoice
    print("2️⃣  Saving INCOMING invoice...")
    invoice1 = save_invoice({
        "invoice_number": "RE-2025-001",
        "invoice_date": "2025-10-15",
        "due_date": "2025-11-15",
        "amount_total": 1234.56,
        "amount_net": 1037.78,
        "amount_tax": 196.78,
        "vendor_name": "Novoferm Vertriebs GmbH",
        "customer_name": "C&D Technologies GmbH",
        "direction": "incoming",
        "status": "open",
        "document_hash": "abc123def456",
        "onedrive_path": "Scan/Buchhaltung/2025/10/Eingang/Novoferm-Vertriebs-GmbH/RE-2025-001.pdf",
        "onedrive_link": "https://cdtech1-my.sharepoint.com/...",
        "email_message_id": "MSG-123456"
    })
    print(f"   ✅ Invoice saved: ID={invoice1}")
    print()
    
    # Test 2: Save outgoing invoice
    print("3️⃣  Saving OUTGOING invoice...")
    invoice2 = save_invoice({
        "invoice_number": "RE-2025-002",
        "invoice_date": "2025-10-17",
        "due_date": "2025-11-17",
        "amount_total": 5678.90,
        "vendor_name": "C&D Technologies GmbH",
        "customer_name": "Kunde XYZ GmbH",
        "direction": "outgoing",
        "status": "open"
    })
    print(f"   ✅ Invoice saved: ID={invoice2}")
    print()
    
    # Test 3: Save overdue invoice
    print("4️⃣  Saving OVERDUE invoice...")
    past_date = (datetime.now() - timedelta(days=45)).date().isoformat()
    invoice3 = save_invoice({
        "invoice_number": "RE-2025-003",
        "invoice_date": past_date,
        "due_date": past_date,
        "amount_total": 999.99,
        "vendor_name": "Lieferant ABC",
        "direction": "incoming",
        "status": "open"
    })
    print(f"   ✅ Overdue invoice saved: ID={invoice3}")
    print()
    
    # Test 4: Get invoice by number
    print("5️⃣  Retrieving invoice by number...")
    invoice = get_invoice_by_number("RE-2025-001")
    if invoice:
        print(f"   ✅ Found invoice: {invoice['invoice_number']}")
        print(f"      Vendor: {invoice['vendor_name']}")
        print(f"      Amount: {invoice['amount_total']} {invoice['currency']}")
        print(f"      Due: {invoice['due_date']}")
        print(f"      OneDrive: {invoice['onedrive_link'][:60]}..." if invoice['onedrive_link'] else "")
    print()
    
    # Test 5: Get open invoices
    print("6️⃣  Getting all OPEN invoices...")
    open_invoices = get_open_invoices()
    print(f"   ✅ Found {len(open_invoices)} open invoices:")
    for inv in open_invoices:
        print(f"      • {inv['invoice_number']}: {inv['amount_total']} EUR ({inv['direction']}) - Due: {inv['due_date']}")
    print()
    
    # Test 6: Get overdue invoices
    print("7️⃣  Getting OVERDUE invoices...")
    overdue = get_overdue_invoices()
    print(f"   ✅ Found {len(overdue)} overdue invoices:")
    for inv in overdue:
        days_overdue = (datetime.now().date() - datetime.fromisoformat(inv['due_date']).date()).days
        print(f"      • {inv['invoice_number']}: {inv['amount_total']} EUR - {days_overdue} days overdue")
    print()
    
    # Test 7: Get statistics
    print("8️⃣  Invoice Statistics...")
    stats = get_invoice_statistics()
    print(f"   📊 Open invoices (incoming): {stats['total_open_incoming']:.2f} EUR")
    print(f"   📊 Open invoices (outgoing): {stats['total_open_outgoing']:.2f} EUR")
    print(f"   📊 Overdue amount: {stats['total_overdue']:.2f} EUR")
    print(f"   📊 Count open: {stats['count_open']}")
    print(f"   📊 Count overdue: {stats['count_overdue']}")
    print()
    
    # Test 8: Mark invoice as paid
    print("9️⃣  Marking invoice as PAID...")
    mark_invoice_paid("RE-2025-002", payment_method="bank_transfer")
    print(f"   ✅ Invoice RE-2025-002 marked as paid")
    print()
    
    # Test 9: Verify payment
    print("🔟  Verifying payment status...")
    updated_invoice = get_invoice_by_number("RE-2025-002")
    if updated_invoice:
        print(f"   ✅ Status: {updated_invoice['status']}")
        print(f"   ✅ Paid on: {updated_invoice['payment_date']}")
        print(f"   ✅ Method: {updated_invoice['payment_method']}")
    print()
    
    # Final statistics
    print("🏁  FINAL STATISTICS...")
    final_stats = get_invoice_statistics()
    print(f"   📊 Open invoices: {final_stats['count_open']}")
    print(f"   📊 Total open amount (incoming): {final_stats['total_open_incoming']:.2f} EUR")
    print()
    
    print("=" * 70)
    print("✅ INVOICE TRACKING DATABASE TEST COMPLETE!")
    print("=" * 70)
    print()
    print("📋 SUMMARY:")
    print(f"   • Created 3 test invoices")
    print(f"   • 1 paid, {final_stats['count_open']} still open")
    print(f"   • {final_stats['count_overdue']} overdue")
    print(f"   • Total outstanding: {final_stats['total_open_incoming']:.2f} EUR")
    print()


if __name__ == "__main__":
    asyncio.run(test_invoice_db())
