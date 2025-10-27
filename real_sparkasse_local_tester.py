#!/usr/bin/env python3
"""
🏦 ECHTE SPARKASSE CSV LOKALER TESTER
====================================

Verarbeitet echte Sparkasse CSV-Daten lokal
ohne Railway-Abhängigkeit für sofortigen Test
"""

import sys
import os
from pathlib import Path

# Add project path
sys.path.append('/Users/cdtechgmbh/railway-orchestrator-clean')

from modules.database.umsatzabgleich import UmsatzabgleichEngine

def test_real_sparkasse_csv():
    """Teste echte Sparkasse CSV-Datei lokal"""
    
    # Deine neue CSV-Datei
    csv_path = "/Users/cdtechgmbh/Downloads/Umsaetze_DE48548625000002582856_2025.10.26.csv"
    
    print("🏦 ECHTE SPARKASSE CSV TEST")
    print("=" * 50)
    print(f"📁 Datei: {os.path.basename(csv_path)}")
    print(f"📊 Größe: {os.path.getsize(csv_path):,} bytes")
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV-Datei nicht gefunden: {csv_path}")
        return False
    
    try:
        # Initialisiere Umsatzabgleich Engine
        engine = UmsatzabgleichEngine()
        
        print(f"\n📥 IMPORTIERE ECHTE BANK-DATEN...")
        
        # Import the real CSV data using correct method
        transactions_imported = engine.import_bank_csv(csv_path, "sparkasse")
        
        print(f"✅ Import abgeschlossen!")
        print(f"📊 Transaktionen importiert: {transactions_imported}")
        
        if transactions_imported > 0:
            # Get date range for report (use recent period)
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # Last 90 days
            
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            print(f"📅 Analysiere Zeitraum: {start_date_str} bis {end_date_str}")
            
            print(f"\n💰 UMSATZABGLEICH MIT ECHTEN DATEN...")
            
            # Run comprehensive report
            report = engine.get_umsatzabgleich_report(start_date_str, end_date_str)
            
            print(f"\n📊 ECHTE DATEN AUSWERTUNG:")
            print("=" * 50)
            
            # Bank Transactions Summary
            bank_data = report.get('bank_transactions', {})
            bank_income = bank_data.get('income', {}).get('total', 0)
            bank_expense = bank_data.get('expense', {}).get('total', 0)
            bank_net = bank_income - bank_expense
            
            print(f"🏦 BANK UMSÄTZE (echt):")
            print(f"   💚 Eingänge: €{bank_income:,.2f}")
            print(f"   🔴 Ausgänge: €{bank_expense:,.2f}")
            print(f"   💰 Netto: €{bank_net:,.2f}")
            
            # Matching Analysis
            matching = report.get('matching_rate', {})
            print(f"\n🎯 MATCHING ANALYSE:")
            print(f"   Rate: {matching.get('matching_percentage', 0):.1f}%")
            print(f"   Gematcht: {matching.get('matched_count', 0)}")
            print(f"   Ungematcht: {matching.get('unmatched_count', 0)}")
            
            # Variance Analysis
            variances = report.get('variances', {})
            print(f"\n⚖️ ABWEICHUNGSANALYSE:")
            for variance_type, amount in variances.items():
                if abs(amount) > 10:  # Show significant variances
                    status = "🔴 KRITISCH" if abs(amount) > 500 else "⚠️ BEACHTEN"
                    print(f"   {variance_type}: €{amount:,.2f} {status}")
            
            # Critical Points
            critical_points = []
            matching_rate = matching.get('matching_percentage', 100)
            if matching_rate < 80:
                critical_points.append(f"Niedrige Matching Rate: {matching_rate:.1f}%")
            
            net_variance = abs(variances.get('net_variance', 0))
            if net_variance > 500:
                critical_points.append(f"Hohe Abweichung: €{net_variance:,.2f}")
            
            unmatched_count = matching.get('unmatched_count', 0)
            if unmatched_count > 10:
                critical_points.append(f"Viele ungematchte Transaktionen: {unmatched_count}")
            
            if critical_points:
                print(f"\n🚨 KRITISCHE PUNKTE:")
                for point in critical_points:
                    print(f"   • {point}")
            else:
                print(f"\n✅ KEINE KRITISCHEN PUNKTE")
            
            # Unmatched Transactions Detail
            unmatched = report.get('unmatched_transactions', [])
            if unmatched and isinstance(unmatched, list):
                print(f"\n🔍 UNGEMATCHTE TRANSAKTIONEN (erste 5):")
                for tx in unmatched[:5]:
                    if isinstance(tx, dict):
                        amount = tx.get('amount', 0)
                        date = tx.get('date', 'N/A')
                        description = tx.get('description', 'N/A')[:50]
                        print(f"   • €{amount:,.2f} | {date} | {description}...")
            else:
                print(f"\n✅ Alle verfügbaren Transaktionen analysiert")
            
            return {
                'success': True,
                'transactions_imported': transactions_imported,
                'date_range': f"{start_date_str} bis {end_date_str}",
                'bank_net': bank_net,
                'matching_rate': matching_rate,
                'critical_points': critical_points,
                'net_variance': variances.get('net_variance', 0)
            }
        else:
            print(f"⚠️ Keine Transaktionen importiert")
            return {'success': False, 'error': 'No transactions imported'}
        
    except Exception as e:
        print(f"❌ Fehler beim Import: {e}")
        return {'success': False, 'error': str(e)}


def main():
    print("🏦 ECHTE SPARKASSE CSV LOKALER TESTER")
    print("=" * 60)
    print("🎯 Test mit deiner neuen CSV-Datei")
    print()
    
    result = test_real_sparkasse_csv()
    
    if result.get('success'):
        print(f"\n🎉 TEST ERFOLGREICH ABGESCHLOSSEN!")
        print(f"📊 {result['transactions_imported']} Transaktionen verarbeitet")
        print(f"📅 Zeitraum: {result['date_range']}")
        print(f"💰 Bank Netto: €{result['bank_net']:,.2f}")
        print(f"🎯 Matching: {result['matching_rate']:.1f}%")
        
        if result['critical_points']:
            print(f"\n🚨 {len(result['critical_points'])} kritische Punkte erkannt")
            print("📧 In Produktion würden jetzt E-Mail-Alerts gesendet!")
        
        print(f"\n🚀 NÄCHSTE SCHRITTE:")
        print("1. WeClapp Integration für ausgehende Rechnungen")
        print("2. Railway Deployment der neuen Features")
        print("3. Automatische E-Mail-Benachrichtigungen aktivieren")
    else:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {result.get('error')}")


if __name__ == "__main__":
    main()