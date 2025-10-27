#!/usr/bin/env python3
"""
🚀 SCHNELLSTART: UMSATZABGLEICH TESTEN
=====================================

1) COMMAND LINE TESTS:
   cd /Users/cdtechgmbh/railway-orchestrator-clean
   python3 practical_tester.py --day        # 📅 1 Tag
   python3 practical_tester.py --week 2     # 📊 2 Wochen  
   python3 practical_tester.py --all        # 🔄 Alles

2) WEB DASHBOARD:
   python3 web_dashboard_tester.py          # 🌐 Browser auf localhost:8080

3) ECHTE BANK-CSV TESTEN:
   - Sparkasse/Deutsche Bank CSV in /tmp/ kopieren
   - python3 practical_tester.py --csv /tmp/bank_data.csv --week 4

=====================================
🎯 SOFORT LOSLEGEN - ALLE OPTIONEN!
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 UMSATZABGLEICH - SCHNELLSTART")
    print("=" * 50)
    
    # Aktuelles Verzeichnis prüfen
    current_dir = os.getcwd()
    target_dir = "/Users/cdtechgmbh/railway-orchestrator-clean"
    
    if current_dir != target_dir:
        print(f"📁 Wechsle von {current_dir} nach {target_dir}")
        os.chdir(target_dir)
    
    print("📋 VERFÜGBARE TEST-OPTIONEN:")
    print()
    print("1️⃣  COMMAND LINE TESTS:")
    print("   python3 practical_tester.py --day        # 📅 1 Tag")
    print("   python3 practical_tester.py --week 2     # 📊 2 Wochen")
    print("   python3 practical_tester.py --week 8     # 📊 8 Wochen")
    print("   python3 practical_tester.py --all        # 🔄 Alle Tests")
    print()
    print("2️⃣  WEB DASHBOARD:")
    print("   python3 web_dashboard_tester.py          # 🌐 Browser Interface")
    print("   → Dann http://localhost:8080 öffnen")
    print()
    print("3️⃣  ECHTE BANK-CSV:")
    print("   python3 practical_tester.py --csv /path/to/bank.csv --week 4")
    print()
    
    choice = input("🎯 Was möchten Sie testen? (1=CLI, 2=Web, 3=CSV, q=quit): ").strip()
    
    if choice == "1":
        print("\n📅 Starte 1-Tag Test...")
        subprocess.run([sys.executable, "practical_tester.py", "--day"])
        
    elif choice == "2":
        print("\n🌐 Starte Web Dashboard...")
        print("🔗 Öffnen Sie http://localhost:8080 in Ihrem Browser")
        subprocess.run([sys.executable, "web_dashboard_tester.py"])
        
    elif choice == "3":
        csv_path = input("📂 Pfad zur Bank-CSV Datei: ").strip()
        if os.path.exists(csv_path):
            weeks = input("📊 Anzahl Wochen (default: 4): ").strip() or "4"
            subprocess.run([sys.executable, "practical_tester.py", "--csv", csv_path, "--week", weeks])
        else:
            print(f"❌ Datei nicht gefunden: {csv_path}")
            
    elif choice.lower() == "q":
        print("👋 Bis bald!")
        
    else:
        print("❌ Ungültige Eingabe")

if __name__ == "__main__":
    main()