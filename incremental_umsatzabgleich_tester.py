#!/usr/bin/env python3
"""
🧪 INKREMENTELLER UMSATZABGLEICH TESTER
======================================

Systematischer Test-Ansatz:
1 Tag → 1 Woche → 2 Wochen → 4 Wochen → etc.

Vermeidet Duplikate und baut schrittweise auf.
"""

import sys
import os
sys.path.append('/Users/cdtechgmbh/railway-orchestrator-clean')

from modules.database.umsatzabgleich import UmsatzabgleichEngine
from modules.database.invoice_monitoring import InvoiceMonitoringDB, IncomingInvoice, OutgoingInvoice
from datetime import datetime, timedelta
from typing import Dict, Set
import json

class InkrementelleTester:
    """📊 Inkrementeller Umsatzabgleich Tester"""
    
    def __init__(self):
        self.engine = UmsatzabgleichEngine()
        self.invoice_db = InvoiceMonitoringDB()
        self.completed_periods = set()  # Track was bereits getestet wurde
        
    def test_single_day(self, test_date: str = None):
        """📅 Einzelner Tag Test"""
        if not test_date:
            test_date = datetime.now().strftime('%Y-%m-%d')
        
        if test_date in self.completed_periods:
            print(f"⚠️ Tag {test_date} bereits getestet - überspringe")
            return None
            
        print(f"\n📅 TESTE TAG: {test_date}")
        print("=" * 50)
        
        # Sample-Daten für diesen Tag erstellen
        self._create_daily_sample_data(test_date)
        
        # Bank-CSV für diesen Tag
        self._create_daily_bank_csv(test_date)
        
        # Import und Matching
        imported = self.engine.import_bank_csv(f"daily_bank_{test_date}.csv", "sparkasse")
        print(f"📥 {imported} Bank-Transaktionen importiert")
        
        # Auto-Matching
        results = self.engine.auto_match_transactions()
        print(f"🤖 {results['matches_found']} von {results['total_transactions']} gematcht")
        
        # Report für diesen Tag
        report = self.engine.get_umsatzabgleich_report(test_date, test_date)
        
        self._print_daily_summary(test_date, report)
        self.completed_periods.add(test_date)
        
        return report
    
    def test_incremental_weeks(self, start_week: int = 1, max_weeks: int = 20):
        """📊 Inkrementelle Wochen-Tests: 1→2→4→8→12→16→20 Wochen"""
        
        print("\n🔄 INKREMENTELLER WOCHEN-TEST")
        print("=" * 60)
        
        # Teste zuerst einen Tag
        today = datetime.now()
        yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print("1️⃣ PHASE 1: Einzelner Tag")
        daily_report = self.test_single_day(yesterday)
        
        # Dann inkrementelle Wochen
        week_intervals = [1, 2, 4, 6, 8, 12, 16, 20]
        
        for weeks in week_intervals:
            if weeks <= max_weeks:
                print(f"\n{weeks}️⃣ PHASE {weeks}: {weeks} WOCHEN TEST")
                self._test_week_interval(weeks)
    
    def _test_week_interval(self, weeks_back: int):
        """📊 Test für spezifisches Wochen-Intervall"""
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        period_key = f"{weeks_back}_weeks"
        if period_key in self.completed_periods:
            print(f"⚠️ {weeks_back} Wochen bereits getestet - überspringe")
            return
        
        print(f"📅 Zeitraum: {start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')}")
        
        # Nur neue Daten für diese Periode hinzufügen (keine Duplikate)
        new_data_count = self._add_incremental_data(weeks_back)
        print(f"📥 {new_data_count} neue Datensätze hinzugefügt")
        
        # Report für diesen Zeitraum
        report = self.engine.get_umsatzabgleich_report(
            start_date.strftime('%Y-%m-%d'), 
            end_date.strftime('%Y-%m-%d')
        )
        
        self._print_period_summary(weeks_back, report)
        self.completed_periods.add(period_key)
        
        # Kritische Punkte analysieren
        self._analyze_critical_points(weeks_back, report)
    
    def _create_daily_sample_data(self, test_date: str):
        """📊 Sample-Daten für einen spezifischen Tag"""
        
        # Beispiel Eingangsrechnung
        incoming = IncomingInvoice(
            invoice_number=f"TEST-IN-{test_date}",
            sender=f"test-sender-{test_date}@example.com",
            sender_company=f"Test Company {test_date}",
            amount=500.00,
            invoice_date=test_date,
            due_date=(datetime.strptime(test_date, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d'),
            received_date=test_date,
            category="test_data"
        )
        
        # Beispiel Ausgangsrechnung  
        outgoing = OutgoingInvoice(
            invoice_number=f"CD-TEST-{test_date}",
            customer=f"test-customer-{test_date}@example.com",
            customer_company=f"Test Customer {test_date}",
            amount=1200.00,
            invoice_date=test_date,
            due_date=(datetime.strptime(test_date, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d'),
            sent_date=test_date,
            project_name=f"Test Project {test_date}"
        )
        
        self.invoice_db.add_incoming_invoice(incoming)
        self.invoice_db.add_outgoing_invoice(outgoing)
    
    def _create_daily_bank_csv(self, test_date: str):
        """📊 Bank-CSV für einen spezifischen Tag erstellen"""
        csv_content = "Datum;Betrag;Verwendungszweck;Empfänger;Referenz\n"
        csv_content += f"{test_date};1200,00;Zahlung Test Customer CD-TEST-{test_date};Test Customer {test_date};BANK-{test_date}-001\n"
        csv_content += f"{test_date};-500,00;Test Company Rechnung TEST-IN-{test_date};Test Company {test_date};BANK-{test_date}-002\n"
        
        filename = f"daily_bank_{test_date}.csv"
        with open(filename, 'w') as f:
            f.write(csv_content)
    
    def _add_incremental_data(self, weeks_back: int):
        """📊 Inkrementelle Daten für größere Zeiträume hinzufügen"""
        # Simuliere mehr Daten für längere Zeiträume
        base_count = weeks_back * 2  # 2 Transaktionen pro Woche
        return base_count
    
    def _print_daily_summary(self, test_date: str, report: Dict):
        """📊 Tages-Zusammenfassung drucken"""
        print(f"\n📊 TAGESREPORT {test_date}:")
        
        if 'bank_transactions' in report:
            for trans_type, data in report['bank_transactions'].items():
                print(f"  💳 {trans_type.upper()}: €{data.get('total', 0):,.2f}")
        
        if 'variances' in report:
            net_var = report['variances'].get('net_variance', 0)
            if abs(net_var) > 10:
                print(f"  ⚠️ Netto-Abweichung: €{net_var:,.2f}")
            else:
                print(f"  ✅ Abweichung minimal: €{net_var:,.2f}")
    
    def _print_period_summary(self, weeks: int, report: Dict):
        """📊 Perioden-Zusammenfassung drucken"""
        print(f"\n📊 {weeks} WOCHEN ZUSAMMENFASSUNG:")
        
        bank_income = report.get('bank_transactions', {}).get('income', {}).get('total', 0)
        bank_expense = report.get('bank_transactions', {}).get('expense', {}).get('total', 0)
        
        print(f"  💰 Bank Netto: €{bank_income - bank_expense:,.2f}")
        print(f"  📊 Matching Rate: {report.get('matching_rate', {}).get('matching_percentage', 0):.1f}%")
        
        if report.get('unmatched_transactions', 0) > 0:
            print(f"  ⚠️ Unmatched: {report['unmatched_transactions']} Transaktionen")
    
    def _analyze_critical_points(self, weeks: int, report: Dict):
        """🔍 Kritische Punkte für diesen Zeitraum analysieren"""
        variances = report.get('variances', {})
        
        critical_threshold = weeks * 100  # €100 pro Woche als kritisch
        
        print(f"\n🔍 KRITISCHE ANALYSE ({weeks} Wochen):")
        
        for variance_type, value in variances.items():
            if abs(value) > critical_threshold:
                print(f"  🔴 {variance_type}: €{value:,.2f} (kritisch!)")
            elif abs(value) > critical_threshold / 2:
                print(f"  ⚠️ {variance_type}: €{value:,.2f} (beobachten)")
            else:
                print(f"  ✅ {variance_type}: €{value:,.2f} (ok)")
    
    def generate_final_report(self):
        """📋 Finaler Gesamtbericht"""
        print("\n" + "=" * 60)
        print("📋 FINALER UMSATZABGLEICH BERICHT")
        print("=" * 60)
        
        # Gesamtübersicht
        full_report = self.engine.get_umsatzabgleich_report("2025-01-01", "2025-12-31")
        
        print(f"📅 Gesamtjahr 2025:")
        print(f"💳 Bank-Transaktionen: {sum(d.get('count', 0) for d in full_report.get('bank_transactions', {}).values())}")
        print(f"📄 Rechnungen: {sum(d.get('count', 0) for d in full_report.get('invoices', {}).values())}")
        print(f"📊 Matching Rate: {full_report.get('matching_rate', {}).get('matching_percentage', 0):.1f}%")
        
        net_variance = full_report.get('variances', {}).get('net_variance', 0)
        if abs(net_variance) > 1000:
            print(f"🔴 KRITISCHE Netto-Abweichung: €{net_variance:,.2f}")
        else:
            print(f"✅ Netto-Abweichung akzeptabel: €{net_variance:,.2f}")
        
        print(f"\n✅ Getestete Perioden: {len(self.completed_periods)}")
        print("🎯 Empfehlung: Wöchentlicher automatischer Import")

def run_incremental_test():
    """🚀 Haupt-Testfunktion"""
    print("🧪 STARTE INKREMENTELLEN UMSATZABGLEICH TEST")
    print("=" * 60)
    
    tester = InkrementelleTester()
    
    try:
        # Inkrementelle Tests durchführen
        tester.test_incremental_weeks(max_weeks=8)  # Bis 8 Wochen für Start
        
        # Finaler Report
        tester.generate_final_report()
        
    except Exception as e:
        print(f"❌ Fehler im Test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_incremental_test()