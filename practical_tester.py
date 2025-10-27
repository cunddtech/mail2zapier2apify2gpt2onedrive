#!/usr/bin/env python3
"""
🚀 PRAKTISCHER UMSATZABGLEICH TESTER
===================================

Einfaches Interface für deinen Test-Ansatz:
1 Tag → 1 Woche → 2/4/6/8/12/16/20 Wochen

USAGE:
python3 practical_tester.py --day        # Einzelner Tag
python3 practical_tester.py --week 1     # 1 Woche  
python3 practical_tester.py --week 4     # 4 Wochen
python3 practical_tester.py --all        # Komplett 1→20 Wochen
"""

import sys
import argparse
sys.path.append('/Users/cdtechgmbh/railway-orchestrator-clean')

from incremental_umsatzabgleich_tester import InkrementelleTester
from datetime import datetime, timedelta

def main():
    parser = argparse.ArgumentParser(description='🚀 Praktischer Umsatzabgleich Tester')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--day', action='store_true', help='📅 Teste einen einzelnen Tag')
    group.add_argument('--week', type=int, help='📊 Teste spezifische Anzahl Wochen (1-20)')
    group.add_argument('--all', action='store_true', help='🔄 Teste alle Intervalle: 1→2→4→6→8→12→16→20 Wochen')
    
    parser.add_argument('--date', type=str, help='📅 Spezifisches Datum (YYYY-MM-DD), sonst heute')
    parser.add_argument('--reset', action='store_true', help='🔄 Reset alle vorherigen Tests')
    
    args = parser.parse_args()
    
    print("🚀 PRAKTISCHER UMSATZABGLEICH TESTER GESTARTET")
    print("=" * 60)
    
    tester = InkrementelleTester()
    
    if args.reset:
        print("🔄 Resette vorherige Tests...")
        tester.completed_periods.clear()
    
    try:
        if args.day:
            # Einzelner Tag Test
            test_date = args.date or (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"📅 TESTE EINZELNEN TAG: {test_date}")
            
            report = tester.test_single_day(test_date)
            
            if report:
                print_quick_summary(report, f"Tag {test_date}")
            
        elif args.week:
            # Spezifische Wochen
            weeks = args.week
            if weeks < 1 or weeks > 20:
                print("❌ Wochen müssen zwischen 1 und 20 sein")
                return
            
            print(f"📊 TESTE {weeks} WOCHEN")
            tester._test_week_interval(weeks)
            
        elif args.all:
            # Alle Intervalle
            print("🔄 TESTE ALLE INTERVALLE: 1→2→4→6→8→12→16→20 Wochen")
            tester.test_incremental_weeks(max_weeks=20)
            tester.generate_final_report()
        
        print("\n✅ TEST ABGESCHLOSSEN!")
        print("🎯 NÄCHSTE SCHRITTE:")
        print("  1. Echte Bank-CSV importieren: --csv /path/to/bank.csv")
        print("  2. Dashboard integration testen")
        print("  3. Produktiven Einsatz starten")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

def print_quick_summary(report, period_name):
    """📊 Schnelle Zusammenfassung"""
    print(f"\n📊 QUICK SUMMARY - {period_name}:")
    print("-" * 40)
    
    # Bank-Zahlen
    bank_transactions = report.get('bank_transactions', {})
    income = bank_transactions.get('income', {}).get('total', 0)
    expense = bank_transactions.get('expense', {}).get('total', 0)
    
    print(f"💳 Bank Netto: €{income - expense:,.2f}")
    print(f"📊 Matching: {report.get('matching_rate', {}).get('matching_percentage', 0):.1f}%")
    
    # Kritische Punkte
    variances = report.get('variances', {})
    net_variance = variances.get('net_variance', 0)
    
    if abs(net_variance) > 500:
        print(f"🔴 KRITISCH: Abweichung €{net_variance:,.2f}")
    elif abs(net_variance) > 100:
        print(f"⚠️ BEOBACHTEN: Abweichung €{net_variance:,.2f}")
    else:
        print(f"✅ OK: Abweichung €{net_variance:,.2f}")

if __name__ == "__main__":
    main()