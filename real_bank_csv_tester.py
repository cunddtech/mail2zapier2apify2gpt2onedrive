#!/usr/bin/env python3
"""
📥 ECHTE BANK-CSV TEST IMPORTER
===============================

Upload echte Sparkasse/Deutsche Bank CSV Dateien
für produktiven Umsatzabgleich-Test

USAGE:
    python3 real_bank_csv_tester.py /path/to/bank.csv
    python3 real_bank_csv_tester.py --interactive
"""

import sys
import os
import base64
import json
import requests
from pathlib import Path

# Add project path
sys.path.append('/Users/cdtechgmbh/railway-orchestrator-clean')

def upload_csv_to_railway(csv_path, bank_type="auto"):
    """Upload CSV to Railway Umsatzabgleich API"""
    
    RAILWAY_URL = "https://my-langgraph-agent-production.up.railway.app"
    
    if not os.path.exists(csv_path):
        print(f"❌ Datei nicht gefunden: {csv_path}")
        return False
    
    # Read and encode CSV
    with open(csv_path, 'rb') as f:
        csv_content = f.read()
        csv_base64 = base64.b64encode(csv_content).decode('utf-8')
    
    filename = os.path.basename(csv_path)
    
    # Prepare request
    payload = {
        "csv_content": csv_base64,
        "bank_type": bank_type,
        "filename": filename
    }
    
    print(f"📤 Uploading {filename} to Railway...")
    print(f"🔗 Target: {RAILWAY_URL}/api/umsatzabgleich/bank-csv")
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/umsatzabgleich/bank-csv",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload erfolgreich!")
            print(f"📊 Ergebnis: {result.get('message', 'N/A')}")
            
            # Show import details
            import_result = result.get('import_result', {})
            if import_result:
                print(f"   📥 Transaktionen importiert: {import_result.get('transactions_imported', 0)}")
                date_range = import_result.get('date_range', {})
                if date_range:
                    print(f"   📅 Zeitraum: {date_range.get('start')} bis {date_range.get('end')}")
            
            return True
            
        else:
            print(f"❌ Upload fehlgeschlagen: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Railway Server antwortet nicht")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Verbindungsfehler - Railway Server nicht erreichbar")
        return False
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False


def get_umsatzabgleich_report():
    """Get report after upload"""
    
    RAILWAY_URL = "https://my-langgraph-agent-production.up.railway.app"
    
    try:
        # Get last 30 days
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{RAILWAY_URL}/api/umsatzabgleich/report",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "include_details": True
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            report = result.get('report', {})
            
            print(f"\n📊 UMSATZABGLEICH REPORT:")
            print(f"=" * 50)
            
            # Matching Rate
            matching = report.get('matching_rate', {})
            print(f"🎯 Matching Rate: {matching.get('matching_percentage', 0):.1f}%")
            print(f"   Matched: {matching.get('matched_count', 0)}")
            print(f"   Total: {matching.get('total_count', 0)}")
            
            # Bank vs Invoice Totals
            bank_total = report.get('bank_transactions', {}).get('total', 0)
            invoice_total = report.get('invoice_data', {}).get('total', 0)
            print(f"\n💰 FINANZEN:")
            print(f"   Bank Netto: €{bank_total:,.2f}")
            print(f"   Rechnungen: €{invoice_total:,.2f}")
            
            # Variances
            variances = report.get('variances', {})
            net_variance = variances.get('net_variance', 0)
            print(f"   Abweichung: €{net_variance:,.2f}")
            
            # Critical Points
            critical_points = report.get('critical_points', [])
            if critical_points:
                print(f"\n🚨 KRITISCHE PUNKTE:")
                for point in critical_points:
                    print(f"   • {point}")
            else:
                print(f"\n✅ Keine kritischen Punkte")
            
            return True
            
        else:
            print(f"❌ Report-Abruf fehlgeschlagen: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Report-Fehler: {e}")
        return False


def interactive_mode():
    """Interactive CSV upload mode"""
    
    print("🎯 INTERAKTIVER CSV UPLOAD MODUS")
    print("=" * 50)
    
    # Find CSV files in common locations
    search_paths = [
        "~/Downloads",
        "~/Desktop", 
        "/tmp",
        "."
    ]
    
    csv_files = []
    for search_path in search_paths:
        expanded_path = Path(search_path).expanduser()
        if expanded_path.exists():
            for csv_file in expanded_path.glob("*.csv"):
                csv_files.append(str(csv_file))
    
    if csv_files:
        print("📂 Gefundene CSV-Dateien:")
        for i, csv_file in enumerate(csv_files, 1):
            size = os.path.getsize(csv_file)
            print(f"   {i}. {csv_file} ({size:,} bytes)")
        
        print(f"   0. Eigenen Pfad eingeben")
        
        try:
            choice = int(input("\n🔢 Datei auswählen (Nummer): "))
            
            if choice == 0:
                csv_path = input("📂 CSV-Pfad eingeben: ").strip()
            elif 1 <= choice <= len(csv_files):
                csv_path = csv_files[choice - 1]
            else:
                print("❌ Ungültige Auswahl")
                return False
                
        except ValueError:
            print("❌ Ungültige Eingabe")
            return False
    else:
        print("📂 Keine CSV-Dateien in Standard-Ordnern gefunden")
        csv_path = input("📂 CSV-Pfad eingeben: ").strip()
    
    # Bank type selection
    print(f"\n🏦 Bank-Typ auswählen:")
    print("   1. Auto-Erkennung (empfohlen)")
    print("   2. Sparkasse")
    print("   3. Deutsche Bank")
    print("   4. Volksbank")
    
    try:
        bank_choice = int(input("🔢 Bank-Typ (1-4): "))
        bank_types = {1: "auto", 2: "sparkasse", 3: "deutsche_bank", 4: "volksbank"}
        bank_type = bank_types.get(bank_choice, "auto")
    except ValueError:
        bank_type = "auto"
    
    print(f"\n🚀 Upload starten...")
    success = upload_csv_to_railway(csv_path, bank_type)
    
    if success:
        print(f"\n📊 Report abrufen...")
        get_umsatzabgleich_report()
        
        # Ask for notification test
        test_notification = input("\n📧 Test-Benachrichtigung senden? (y/n): ").lower()
        if test_notification == 'y':
            send_test_notification()


def send_test_notification():
    """Send test notification"""
    
    RAILWAY_URL = "https://my-langgraph-agent-production.up.railway.app"
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/umsatzabgleich/notification-test",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Test-Benachrichtigung gesendet!")
            else:
                print(f"❌ Test-Benachrichtigung fehlgeschlagen: {result.get('message')}")
        else:
            print(f"❌ Notification-Test fehlgeschlagen: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Notification-Fehler: {e}")


def main():
    print("📥 ECHTE BANK-CSV TESTER")
    print("=" * 50)
    print("🎯 Upload für produktiven Umsatzabgleich")
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_mode()
        else:
            csv_path = sys.argv[1]
            bank_type = sys.argv[2] if len(sys.argv) > 2 else "auto"
            
            success = upload_csv_to_railway(csv_path, bank_type)
            if success:
                get_umsatzabgleich_report()
    else:
        print("USAGE:")
        print("   python3 real_bank_csv_tester.py /path/to/bank.csv")
        print("   python3 real_bank_csv_tester.py --interactive")
        print()
        
        choice = input("🎯 Interaktiven Modus starten? (y/n): ").lower()
        if choice == 'y':
            interactive_mode()


if __name__ == "__main__":
    main()