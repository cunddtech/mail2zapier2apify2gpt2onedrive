"""
🧪 Test Suite: Payment Matching System
"""

from modules.database.payment_matching import (
    init_payment_db, import_bank_transaction,
    find_matching_invoice, match_transaction_to_invoice,
    auto_match_all_transactions, get_unmatched_transactions,
    get_payment_statistics, extract_invoice_number_from_text
)
from modules.database.invoice_tracking_db import save_invoice
from datetime import datetime, timedelta


def test_payment_matching():
    """Test payment matching workflow"""
    
    print("\n" + "="*80)
    print("🧪 PAYMENT MATCHING TEST SUITE")
    print("="*80)
    
    # 1. Initialize databases
    print("\n1️⃣ Initialize Payment DB...")
    init_payment_db()
    print("   ✅ Payment DB ready")
    
    # 2. Create test invoices
    print("\n2️⃣ Create Test Invoices...")
    
    invoices = [
        {
            "invoice_number": "RE-2025-101",
            "invoice_date": "2025-10-01",
            "due_date": "2025-10-31",
            "amount_total": 1500.00,
            "amount_net": 1260.50,
            "amount_tax": 239.50,
            "currency": "EUR",
            "vendor_name": "ACME GmbH",
            "customer_name": "C&D Tech GmbH",
            "direction": "incoming",
            "status": "open",
            "onedrive_path": "/test/invoice101.pdf"
        },
        {
            "invoice_number": "RE-2025-102",
            "invoice_date": "2025-10-05",
            "due_date": "2025-11-05",
            "amount_total": 2500.00,
            "amount_net": 2100.84,
            "amount_tax": 399.16,
            "currency": "EUR",
            "vendor_name": "Best Customer AG",
            "customer_name": "C&D Tech GmbH",
            "direction": "outgoing",
            "status": "open",
            "onedrive_path": "/test/invoice102.pdf"
        },
        {
            "invoice_number": "RE-2025-103",
            "invoice_date": "2025-09-15",
            "due_date": "2025-10-15",
            "amount_total": 750.00,
            "amount_net": 630.25,
            "amount_tax": 119.75,
            "currency": "EUR",
            "vendor_name": "Supplier XYZ",
            "customer_name": "C&D Tech GmbH",
            "direction": "incoming",
            "status": "open",
            "onedrive_path": "/test/invoice103.pdf"
        }
    ]
    
    for inv in invoices:
        inv_id = save_invoice(inv)
        print(f"   ✅ Invoice created: {inv['invoice_number']} ({inv['amount_total']} EUR, {inv['direction']})")
    
    # 3. Import test bank transactions
    print("\n3️⃣ Import Bank Transactions...")
    
    transactions = [
        {
            "transaction_id": "BANK-TX-001",
            "transaction_date": "2025-10-18",
            "value_date": "2025-10-18",
            "amount": -1500.00,  # Outgoing payment
            "currency": "EUR",
            "sender_name": "C&D Tech GmbH",
            "sender_iban": "DE89370400440532013000",
            "receiver_name": "ACME GmbH",
            "receiver_iban": "DE89370400440532099999",
            "purpose": "Rechnung RE-2025-101 vom 01.10.2025",
            "reference": "RE-2025-101",
            "transaction_type": "debit"
        },
        {
            "transaction_id": "BANK-TX-002",
            "transaction_date": "2025-10-17",
            "value_date": "2025-10-17",
            "amount": 2500.00,  # Incoming payment
            "currency": "EUR",
            "sender_name": "Best Customer AG",
            "sender_iban": "DE89370400440532088888",
            "receiver_name": "C&D Tech GmbH",
            "receiver_iban": "DE89370400440532013000",
            "purpose": "Payment for Invoice RE-2025-102",
            "reference": "RE-2025-102",
            "transaction_type": "credit"
        },
        {
            "transaction_id": "BANK-TX-003",
            "transaction_date": "2025-10-16",
            "value_date": "2025-10-16",
            "amount": -749.99,  # Outgoing, slightly different amount
            "currency": "EUR",
            "sender_name": "C&D Tech GmbH",
            "sender_iban": "DE89370400440532013000",
            "receiver_name": "Supplier XYZ GmbH",
            "receiver_iban": "DE89370400440532077777",
            "purpose": "Supplier invoice payment",
            "reference": "103",  # Only partial invoice number
            "transaction_type": "debit"
        },
        {
            "transaction_id": "BANK-TX-004",
            "transaction_date": "2025-10-15",
            "value_date": "2025-10-15",
            "amount": -3500.00,  # No matching invoice
            "currency": "EUR",
            "sender_name": "C&D Tech GmbH",
            "sender_iban": "DE89370400440532013000",
            "receiver_name": "Random Vendor Ltd",
            "receiver_iban": "DE89370400440532066666",
            "purpose": "Office supplies",
            "reference": "MISC",
            "transaction_type": "debit"
        }
    ]
    
    for tx in transactions:
        tx_id = import_bank_transaction(tx)
        print(f"   ✅ Transaction imported: {tx['transaction_id']} ({tx['amount']} EUR)")
    
    # 4. Test invoice number extraction
    print("\n4️⃣ Test Invoice Number Extraction...")
    
    test_texts = [
        "Rechnung RE-2025-101 vom 01.10.2025",
        "Payment for Invoice RE-2025-102",
        "RG 123456",
        "Invoice #789012",
        "Misc payment"
    ]
    
    for text in test_texts:
        extracted = extract_invoice_number_from_text(text)
        print(f"   '{text[:40]}' → {extracted}")
    
    # 5. Test manual matching
    print("\n5️⃣ Test Find Matching Invoice...")
    
    for tx in transactions[:3]:  # First 3 should match
        print(f"\n   Transaction: {tx['transaction_id']} | {tx['amount']} EUR")
        match = find_matching_invoice(tx)
        
        if match:
            print(f"   ✅ Match found: Invoice {match['invoice_number']}")
            print(f"      Confidence: {match['match_confidence']:.0%}")
            print(f"      Method: {match['match_method']}")
        else:
            print(f"   ❌ No match found")
    
    # 6. Test auto-matching
    print("\n6️⃣ Auto-Match All Transactions...")
    
    stats = auto_match_all_transactions(min_confidence=0.6)
    
    print(f"\n   📊 Auto-Matching Results:")
    print(f"      Processed: {stats['processed']}")
    print(f"      ✅ Matched: {stats['matched']}")
    print(f"      ❌ Unmatched: {stats['unmatched']}")
    print(f"      ⚠️  Low Confidence: {stats['low_confidence']}")
    
    # 7. Get unmatched transactions
    print("\n7️⃣ Get Unmatched Transactions...")
    
    unmatched = get_unmatched_transactions()
    
    if unmatched:
        print(f"   Found {len(unmatched)} unmatched transaction(s):")
        for tx in unmatched:
            print(f"      • {tx['transaction_id']}: {tx['amount']} EUR - {tx.get('purpose', '')[:40]}")
    else:
        print(f"   ✅ All transactions matched!")
    
    # 8. Get payment statistics
    print("\n8️⃣ Payment Statistics...")
    
    pay_stats = get_payment_statistics()
    
    print(f"\n   📊 Overall Statistics:")
    print(f"      Total Transactions: {pay_stats['total_transactions']}")
    print(f"      ✅ Matched: {pay_stats['matched_count']}")
    print(f"      ❌ Unmatched: {pay_stats['unmatched_count']}")
    print(f"      Match Rate: {pay_stats['match_rate']:.1f}%")
    print(f"      💰 Matched Amount: {pay_stats['matched_amount']:.2f} EUR")
    
    # 9. Verify invoices marked as paid
    print("\n9️⃣ Verify Invoices Marked as PAID...")
    
    from modules.database.invoice_tracking_db import get_invoice_by_number
    
    for inv_num in ["RE-2025-101", "RE-2025-102", "RE-2025-103"]:
        invoice = get_invoice_by_number(inv_num)
        if invoice:
            status_emoji = "✅" if invoice["status"] == "paid" else "❌"
            print(f"   {status_emoji} {inv_num}: Status = {invoice['status']}")
            if invoice.get("payment_date"):
                print(f"      Payment Date: {invoice['payment_date']}")
        else:
            print(f"   ❌ Invoice {inv_num} not found")
    
    print("\n" + "="*80)
    print("✅ PAYMENT MATCHING TEST SUITE COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_payment_matching()
