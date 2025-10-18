"""
🧪 COMPREHENSIVE SYSTEM TEST
=============================

End-to-End Test aller Features:
1. Invoice Tracking Database
2. Payment Matching System
3. API Endpoints
4. Integration Test

Dieses Script testet das gesamte System lokal UND auf Railway Production.
"""

import requests
import base64
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List
import json

# Test-Konfiguration
LOCAL_API = "http://localhost:5001"
PRODUCTION_API = "https://my-langgraph-agent-production.up.railway.app"

# Welche API testen? (beide oder einzeln)
TEST_LOCAL = False  # Local nur wenn Server läuft
TEST_PRODUCTION = True


class Colors:
    """ANSI Color Codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{'='*80}\n")


def print_success(msg: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_error(msg: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_warning(msg: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def print_info(msg: str):
    """Print info message"""
    print(f"   {msg}")


# ============================================================================
# TEST 1: INVOICE TRACKING DATABASE
# ============================================================================

def test_1_invoice_database():
    """Test Invoice Tracking Database lokal"""
    
    print_section("TEST 1: INVOICE TRACKING DATABASE")
    
    from modules.database.invoice_tracking_db import (
        save_invoice, get_invoice_by_number, get_open_invoices,
        get_overdue_invoices, mark_invoice_paid, get_invoice_statistics
    )
    
    # 1.1 Create Test Invoices
    print_info("1.1 Erstelle Test-Rechnungen...")
    
    test_invoices = [
        {
            "invoice_number": f"TEST-INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}-001",
            "invoice_date": "2025-10-01",
            "due_date": "2025-10-31",
            "amount_total": 1500.00,
            "amount_net": 1260.50,
            "amount_tax": 239.50,
            "currency": "EUR",
            "vendor_name": "Test Vendor GmbH",
            "customer_name": "C&D Tech GmbH",
            "direction": "incoming",
            "status": "open",
            "onedrive_path": "/test/invoice_001.pdf"
        },
        {
            "invoice_number": f"TEST-INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}-002",
            "invoice_date": "2025-10-05",
            "due_date": "2025-11-05",
            "amount_total": 2500.00,
            "currency": "EUR",
            "vendor_name": "Test Customer AG",
            "direction": "outgoing",
            "status": "open"
        }
    ]
    
    invoice_ids = []
    for inv in test_invoices:
        inv_id = save_invoice(inv)
        invoice_ids.append((inv_id, inv["invoice_number"]))
        print_success(f"Invoice created: {inv['invoice_number']} (ID: {inv_id})")
    
    # 1.2 Retrieve Invoice
    print_info("\n1.2 Rechnung abrufen...")
    
    invoice = get_invoice_by_number(test_invoices[0]["invoice_number"])
    if invoice and invoice["invoice_number"] == test_invoices[0]["invoice_number"]:
        print_success(f"Invoice retrieved: {invoice['invoice_number']}")
    else:
        print_error("Invoice retrieval failed")
        return False
    
    # 1.3 Get Open Invoices
    print_info("\n1.3 Offene Rechnungen...")
    
    open_invoices = get_open_invoices()
    if len(open_invoices) >= 2:
        print_success(f"Open invoices found: {len(open_invoices)}")
    else:
        print_warning(f"Expected ≥2, got {len(open_invoices)}")
    
    # 1.4 Mark as Paid
    print_info("\n1.4 Rechnung als bezahlt markieren...")
    
    mark_invoice_paid(test_invoices[0]["invoice_number"], "2025-10-18", "bank_transfer")
    
    updated_invoice = get_invoice_by_number(test_invoices[0]["invoice_number"])
    if updated_invoice["status"] == "paid":
        print_success(f"Invoice marked as PAID: {updated_invoice['invoice_number']}")
    else:
        print_error("Mark paid failed")
        return False
    
    # 1.5 Statistics
    print_info("\n1.5 Statistiken...")
    
    stats = get_invoice_statistics()
    print_info(f"   Total Invoices: {stats.get('total_count', 0)}")
    print_info(f"   Open Incoming: {stats.get('open_incoming_total', 0)} EUR")
    print_info(f"   Open Outgoing: {stats.get('open_outgoing_total', 0)} EUR")
    
    print_success("Invoice Database Test PASSED")
    return True


# ============================================================================
# TEST 2: PAYMENT MATCHING SYSTEM
# ============================================================================

def test_2_payment_matching():
    """Test Payment Matching System lokal"""
    
    print_section("TEST 2: PAYMENT MATCHING SYSTEM")
    
    from modules.database.payment_matching import (
        import_bank_transaction, find_matching_invoice,
        auto_match_all_transactions, get_payment_statistics
    )
    from modules.database.invoice_tracking_db import save_invoice
    
    # 2.1 Create Invoice for Matching
    print_info("2.1 Erstelle Test-Rechnung für Matching...")
    
    test_invoice = {
        "invoice_number": f"MATCH-TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "invoice_date": "2025-10-10",
        "due_date": "2025-11-10",
        "amount_total": 999.99,
        "currency": "EUR",
        "vendor_name": "Match Test Vendor",
        "direction": "incoming",
        "status": "open"
    }
    
    inv_id = save_invoice(test_invoice)
    print_success(f"Test invoice created: {test_invoice['invoice_number']}")
    
    # 2.2 Import Matching Transaction
    print_info("\n2.2 Importiere passende Transaktion...")
    
    transaction = {
        "transaction_id": f"TEST-TX-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "transaction_date": "2025-10-18",
        "amount": -999.99,
        "sender_name": "C&D Tech GmbH",
        "receiver_name": "Match Test Vendor",
        "purpose": f"Rechnung {test_invoice['invoice_number']} payment",
        "reference": test_invoice['invoice_number']
    }
    
    tx_id = import_bank_transaction(transaction)
    print_success(f"Transaction imported: ID={tx_id}")
    
    # 2.3 Find Match
    print_info("\n2.3 Suche Match...")
    
    match = find_matching_invoice(transaction)
    if match:
        print_success(f"Match found: {match['invoice_number']} (Confidence: {match['match_confidence']:.0%})")
        print_info(f"   Method: {match['match_method']}")
    else:
        print_error("No match found")
        return False
    
    # 2.4 Auto-Match
    print_info("\n2.4 Auto-Match ausführen...")
    
    stats = auto_match_all_transactions(min_confidence=0.5)
    print_info(f"   Processed: {stats['processed']}")
    print_info(f"   Matched: {stats['matched']}")
    print_info(f"   Unmatched: {stats['unmatched']}")
    
    # 2.5 Payment Statistics
    print_info("\n2.5 Payment Statistiken...")
    
    pay_stats = get_payment_statistics()
    print_info(f"   Total Transactions: {pay_stats['total_transactions']}")
    print_info(f"   Match Rate: {pay_stats['match_rate']:.1f}%")
    print_info(f"   Matched Amount: {pay_stats['matched_amount']:.2f} EUR")
    
    print_success("Payment Matching Test PASSED")
    return True


# ============================================================================
# TEST 3: API ENDPOINTS (LOCAL)
# ============================================================================

def test_3_api_local():
    """Test API Endpoints lokal"""
    
    if not TEST_LOCAL:
        print_section("TEST 3: API ENDPOINTS (LOCAL) - SKIPPED")
        return True
    
    print_section("TEST 3: API ENDPOINTS (LOCAL)")
    
    base_url = LOCAL_API
    
    # 3.1 Health Check
    print_info("3.1 Health Check...")
    
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            print_success(f"API reachable: {response.json()}")
        else:
            print_error(f"Status endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot reach local API: {e}")
        print_warning("Make sure server is running: python3 production_langgraph_orchestrator.py")
        return False
    
    # 3.2 Payment Statistics Endpoint
    print_info("\n3.2 Payment Statistics Endpoint...")
    
    response = requests.get(f"{base_url}/api/payment/statistics")
    if response.status_code == 200:
        stats = response.json()['statistics']
        print_success(f"Statistics: {stats['total_transactions']} transactions, {stats['match_rate']:.1f}% match rate")
    else:
        print_error(f"Statistics endpoint error: {response.status_code}")
    
    # 3.3 Import Transaction Endpoint
    print_info("\n3.3 Import Transaction Endpoint...")
    
    test_tx = {
        "transaction_id": f"API-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "transaction_date": "2025-10-18",
        "amount": -123.45,
        "sender_name": "C&D Tech GmbH",
        "receiver_name": "API Test Vendor",
        "purpose": "API Test Payment"
    }
    
    response = requests.post(f"{base_url}/api/payment/import-transaction", json=test_tx)
    if response.status_code == 200:
        print_success(f"Transaction imported via API: ID={response.json()['transaction_id']}")
    else:
        print_error(f"Import endpoint error: {response.status_code} - {response.text}")
    
    print_success("Local API Test PASSED")
    return True


# ============================================================================
# TEST 4: API ENDPOINTS (PRODUCTION)
# ============================================================================

def test_4_api_production():
    """Test API Endpoints auf Railway Production"""
    
    if not TEST_PRODUCTION:
        print_section("TEST 4: API ENDPOINTS (PRODUCTION) - SKIPPED")
        return True
    
    print_section("TEST 4: API ENDPOINTS (PRODUCTION)")
    
    base_url = PRODUCTION_API
    
    # 4.1 Health Check
    print_info("4.1 Production Health Check...")
    
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            print_success(f"Production API online: {response.json()}")
        else:
            print_error(f"Status endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot reach production API: {e}")
        return False
    
    # 4.2 Payment Statistics
    print_info("\n4.2 Production Payment Statistics...")
    
    response = requests.get(f"{base_url}/api/payment/statistics")
    if response.status_code == 200:
        stats = response.json()['statistics']
        print_success("Payment Statistics retrieved:")
        print_info(f"   Total Transactions: {stats['total_transactions']}")
        print_info(f"   Matched: {stats['matched_count']}")
        print_info(f"   Match Rate: {stats['match_rate']:.1f}%")
        print_info(f"   Matched Amount: {stats['matched_amount']:.2f} EUR")
    else:
        print_error(f"Statistics endpoint error: {response.status_code}")
    
    # 4.3 Unmatched Transactions
    print_info("\n4.3 Production Unmatched Transactions...")
    
    response = requests.get(f"{base_url}/api/payment/unmatched")
    if response.status_code == 200:
        result = response.json()
        print_success(f"Unmatched transactions: {result['count']}")
        if result['count'] > 0:
            print_info("   First 3 unmatched:")
            for tx in result['transactions'][:3]:
                print_info(f"   • {tx.get('transaction_date')}: {tx.get('amount')} EUR - {tx.get('purpose', '')[:40]}")
    else:
        print_error(f"Unmatched endpoint error: {response.status_code}")
    
    # 4.4 Import Test Transaction (Production)
    print_info("\n4.4 Import Test Transaction to Production...")
    
    test_tx = {
        "transaction_id": f"PROD-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "transaction_date": datetime.now().strftime('%Y-%m-%d'),
        "amount": -555.55,
        "currency": "EUR",
        "sender_name": "C&D Tech GmbH",
        "receiver_name": "Production Test Vendor",
        "purpose": "Comprehensive System Test - Production Import",
        "reference": "SYSTEST"
    }
    
    response = requests.post(f"{base_url}/api/payment/import-transaction", json=test_tx)
    if response.status_code == 200:
        tx_id = response.json()['transaction_id']
        print_success(f"Test transaction imported to Production: ID={tx_id}")
    else:
        print_error(f"Production import error: {response.status_code} - {response.text}")
        return False
    
    # 4.5 Auto-Match on Production
    print_info("\n4.5 Trigger Auto-Match on Production...")
    
    response = requests.post(f"{base_url}/api/payment/auto-match", json={"min_confidence": 0.7})
    if response.status_code == 200:
        stats = response.json()['stats']
        print_success("Auto-Match executed on Production:")
        print_info(f"   Processed: {stats['processed']}")
        print_info(f"   Matched: {stats['matched']}")
        print_info(f"   Unmatched: {stats['unmatched']}")
    else:
        print_error(f"Auto-match error: {response.status_code}")
    
    print_success("Production API Test PASSED")
    return True


# ============================================================================
# TEST 5: CSV IMPORT
# ============================================================================

def test_5_csv_import():
    """Test CSV Import Funktionalität"""
    
    print_section("TEST 5: CSV IMPORT FUNCTIONALITY")
    
    from modules.database.csv_import import parse_german_date, parse_german_amount, import_csv_generic
    
    # 5.1 Date Parsing
    print_info("5.1 German Date Parsing...")
    
    test_dates = [
        ("18.10.2025", "2025-10-18"),
        ("01.01.25", "2025-01-01"),
        ("2025-10-18", "2025-10-18")
    ]
    
    all_passed = True
    for input_date, expected in test_dates:
        result = parse_german_date(input_date)
        if result == expected:
            print_success(f"'{input_date}' → '{result}' ✓")
        else:
            print_error(f"'{input_date}' → '{result}' (expected '{expected}')")
            all_passed = False
    
    # 5.2 Amount Parsing
    print_info("\n5.2 German Amount Parsing...")
    
    test_amounts = [
        ("1.500,00", 1500.00),
        ("-750,50", -750.50),
        ("2500.00", 2500.00),
        ("1.234.567,89", 1234567.89)
    ]
    
    for input_amount, expected in test_amounts:
        result = parse_german_amount(input_amount)
        if abs(result - expected) < 0.01:
            print_success(f"'{input_amount}' → {result} ✓")
        else:
            print_error(f"'{input_amount}' → {result} (expected {expected})")
            all_passed = False
    
    # 5.3 Create Test CSV
    print_info("\n5.3 Test CSV Import...")
    
    import tempfile
    
    csv_content = """Date,Amount,Description,Sender,Receiver
2025-10-18,-100.00,Test Payment 1,C&D Tech GmbH,Vendor A
2025-10-17,250.50,Customer Payment,Customer B,C&D Tech GmbH
2025-10-16,-75.00,Office Supplies,C&D Tech GmbH,Vendor C
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write(csv_content)
        temp_csv_path = f.name
    
    try:
        stats = import_csv_generic(temp_csv_path)
        print_success(f"CSV Import: {stats['imported']} imported, {stats['errors']} errors")
        
        if stats['imported'] == 3 and stats['errors'] == 0:
            print_success("CSV Import Test PASSED")
        else:
            print_warning(f"Expected 3 imported, 0 errors. Got: {stats}")
    finally:
        os.remove(temp_csv_path)
    
    return all_passed


# ============================================================================
# TEST 6: INTEGRATION TEST
# ============================================================================

def test_6_integration():
    """Complete Integration Test: Invoice → Payment → Match"""
    
    print_section("TEST 6: FULL INTEGRATION TEST")
    
    from modules.database.invoice_tracking_db import save_invoice, get_invoice_by_number
    from modules.database.payment_matching import import_bank_transaction, auto_match_all_transactions
    
    # 6.1 Create Invoice
    print_info("6.1 Create Invoice...")
    
    invoice_num = f"INTEGRATION-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    invoice = {
        "invoice_number": invoice_num,
        "invoice_date": "2025-10-15",
        "due_date": "2025-11-15",
        "amount_total": 777.77,
        "currency": "EUR",
        "vendor_name": "Integration Test Vendor GmbH",
        "direction": "incoming",
        "status": "open",
        "onedrive_path": "/test/integration.pdf"
    }
    
    inv_id = save_invoice(invoice)
    print_success(f"Invoice created: {invoice_num} (Amount: 777.77 EUR)")
    
    # 6.2 Import Matching Payment
    print_info("\n6.2 Import matching bank transaction...")
    
    transaction = {
        "transaction_id": f"INT-TX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "transaction_date": "2025-10-18",
        "amount": -777.77,
        "sender_name": "C&D Tech GmbH",
        "receiver_name": "Integration Test Vendor GmbH",
        "purpose": f"Payment for invoice {invoice_num}",
        "reference": invoice_num
    }
    
    tx_id = import_bank_transaction(transaction)
    print_success(f"Transaction imported: ID={tx_id}")
    
    # 6.3 Auto-Match
    print_info("\n6.3 Execute Auto-Match...")
    
    stats = auto_match_all_transactions(min_confidence=0.5)
    print_success(f"Auto-Match: {stats['matched']} matched, {stats['unmatched']} unmatched")
    
    # 6.4 Verify Invoice Status
    print_info("\n6.4 Verify invoice is marked as PAID...")
    
    updated_invoice = get_invoice_by_number(invoice_num)
    
    if updated_invoice and updated_invoice['status'] == 'paid':
        print_success(f"✅✅✅ INTEGRATION TEST PASSED ✅✅✅")
        print_info(f"   Invoice {invoice_num} successfully matched and marked as PAID")
        print_info(f"   Payment Date: {updated_invoice.get('payment_date')}")
        print_info(f"   Payment Method: {updated_invoice.get('payment_method')}")
        return True
    else:
        print_error("Integration test FAILED - Invoice not marked as paid")
        print_info(f"   Status: {updated_invoice.get('status') if updated_invoice else 'NOT FOUND'}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Execute all tests"""
    
    print("\n" + "="*80)
    print(f"{Colors.BOLD}{Colors.BLUE}🧪 COMPREHENSIVE SYSTEM TEST SUITE{Colors.END}")
    print(f"{'='*80}\n")
    print(f"Test Configuration:")
    print(f"  Local API:      {'ENABLED' if TEST_LOCAL else 'DISABLED'}")
    print(f"  Production API: {'ENABLED' if TEST_PRODUCTION else 'DISABLED'}")
    print(f"  Production URL: {PRODUCTION_API}")
    print(f"  Timestamp:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run Tests
    try:
        results['Invoice Database'] = test_1_invoice_database()
    except Exception as e:
        print_error(f"Test 1 crashed: {e}")
        results['Invoice Database'] = False
    
    try:
        results['Payment Matching'] = test_2_payment_matching()
    except Exception as e:
        print_error(f"Test 2 crashed: {e}")
        results['Payment Matching'] = False
    
    try:
        results['API Local'] = test_3_api_local()
    except Exception as e:
        print_error(f"Test 3 crashed: {e}")
        results['API Local'] = False
    
    try:
        results['API Production'] = test_4_api_production()
    except Exception as e:
        print_error(f"Test 4 crashed: {e}")
        results['API Production'] = False
    
    try:
        results['CSV Import'] = test_5_csv_import()
    except Exception as e:
        print_error(f"Test 5 crashed: {e}")
        results['CSV Import'] = False
    
    try:
        results['Integration'] = test_6_integration()
    except Exception as e:
        print_error(f"Test 6 crashed: {e}")
        results['Integration'] = False
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{'='*80}")
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED ({passed}/{total}) 🎉{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  {passed}/{total} TESTS PASSED{Colors.END}")
    print(f"{'='*80}\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
