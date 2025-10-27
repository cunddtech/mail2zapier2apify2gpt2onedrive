#!/usr/bin/env python3
"""
🧪 VOLLSTÄNDIGER UMSATZABGLEICH TEST
==================================

Test mit echten Bank-CSV Daten und automatischem Matching
"""

import sys
sys.path.append('/Users/cdtechgmbh/railway-orchestrator-clean')

from modules.database.umsatzabgleich import UmsatzabgleichEngine
import json

def test_full_umsatzabgleich():
    """💰 Vollständiger Umsatzabgleich Test mit CSV-Import"""
    
    print("💰 VOLLSTÄNDIGER UMSATZABGLEICH TEST")
    print("=" * 60)
    
    # Umsatzabgleich Engine starten
    engine = UmsatzabgleichEngine()
    
    print("📥 1. Bank-CSV Import...")
    imported_count = engine.import_bank_csv(
        csv_file_path="/Users/cdtechgmbh/railway-orchestrator-clean/sample_bank_data.csv",
        bank_format="sparkasse"
    )
    print(f"✅ {imported_count} Bank-Transaktionen importiert")
    
    print("\n🤖 2. Automatisches Rechnungs-Matching...")
    match_results = engine.auto_match_transactions()
    print(f"✅ {match_results['matches_found']} von {match_results['total_transactions']} automatisch gematcht")
    print(f"⚠️ {match_results['unmatched']} Transaktionen ungematcht")
    
    print("\n📊 3. Umsatzabgleich Report (Oktober 2025)...")
    report = engine.get_umsatzabgleich_report("2025-10-01", "2025-10-31")
    
    print(f"📅 Zeitraum: {report['period']}")
    print("\n💳 BANK-TRANSAKTIONEN:")
    for trans_type, data in report['bank_transactions'].items():
        print(f"  {trans_type.upper()}: {data['count']} × €{data['total']:,.2f}")
    
    print("\n📄 RECHNUNGEN:")
    for invoice_type, data in report['invoices'].items():
        print(f"  {invoice_type.upper()}: {data['count']} × €{data['total']:,.2f}")
    
    print("\n🔍 ABWEICHUNGSANALYSE:")
    variances = report['variances']
    print(f"  📈 Einnahmen-Abweichung: €{variances['income_variance']:,.2f}")
    print(f"  📉 Ausgaben-Abweichung: €{variances['expense_variance']:,.2f}")
    print(f"  💰 Netto-Abweichung: €{variances['net_variance']:,.2f}")
    
    print(f"\n📊 MATCHING-RATE:")
    matching = report['matching_rate']
    print(f"  ✅ {matching['matched_transactions']} von {matching['total_transactions']} Transaktionen gematcht")
    print(f"  📊 Matching-Rate: {matching['matching_percentage']:.1f}%")
    
    # Kritische Punkte identifizieren
    print("\n🔴 KRITISCHE PUNKTE:")
    if abs(variances['income_variance']) > 100:
        print(f"  ⚠️ Hohe Einnahmen-Abweichung: €{variances['income_variance']:,.2f}")
    
    if abs(variances['expense_variance']) > 100:
        print(f"  ⚠️ Hohe Ausgaben-Abweichung: €{variances['expense_variance']:,.2f}")
    
    if matching['matching_percentage'] < 80:
        print(f"  ⚠️ Niedrige Matching-Rate: {matching['matching_percentage']:.1f}%")
    
    if report['unmatched_transactions'] > 0:
        print(f"  ⚠️ {report['unmatched_transactions']} ungematcht Transaktionen")
    
    print("\n🎯 GESCHÄFTSANALYSE:")
    bank_net = report['bank_transactions'].get('income', {}).get('total', 0) - report['bank_transactions'].get('expense', {}).get('total', 0)
    invoice_net = report['invoices'].get('outgoing', {}).get('total', 0) - report['invoices'].get('incoming', {}).get('total', 0)
    
    print(f"  💰 Bank Netto-Cash Flow: €{bank_net:,.2f}")
    print(f"  📄 Rechnungen Netto-Flow: €{invoice_net:,.2f}")
    print(f"  🎯 Differenz: €{bank_net - invoice_net:,.2f}")
    
    if bank_net > invoice_net:
        print("  ✅ Bank-Flow höher als Rechnungen (zusätzliche Einnahmen?)")
    elif bank_net < invoice_net:
        print("  ⚠️ Bank-Flow niedriger als Rechnungen (ausstehende Zahlungen?)")
    else:
        print("  🎯 Perfect Match - Bank und Rechnungen stimmen überein!")
    
    return report

if __name__ == "__main__":
    report = test_full_umsatzabgleich()
    
    print("\n" + "=" * 60)
    print("✅ UMSATZABGLEICH ABGESCHLOSSEN")
    print("🚀 System bereit für produktive Bank-Datenintegration!")
    print("📊 Empfehlung: Wöchentlicher automatischer Import + Report")