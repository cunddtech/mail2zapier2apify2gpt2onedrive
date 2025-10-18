"""
📥 Payment Matching - Beispiel-Nutzung

Dieses Script zeigt, wie man das Payment Matching System nutzt:
1. Bank-Transaktionen importieren
2. Auto-Match ausführen
3. Unmatched Transactions anzeigen
4. Manuelle Matches erstellen
5. Statistiken abrufen
"""

import requests
import base64
from datetime import datetime

# API Base URL (Railway Production)
API_BASE = "https://my-langgraph-agent-production.up.railway.app"


def example_1_import_single_transaction():
    """Beispiel 1: Einzelne Transaktion importieren"""
    
    print("\n" + "="*80)
    print("📝 BEISPIEL 1: Einzelne Transaktion importieren")
    print("="*80)
    
    transaction = {
        "transaction_id": f"EXAMPLE-TX-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "transaction_date": "2025-10-18",
        "value_date": "2025-10-18",
        "amount": -1234.56,  # Negative = Abgang (wir zahlen)
        "currency": "EUR",
        "sender_name": "C&D Tech GmbH",
        "sender_iban": "DE89370400440532013000",
        "receiver_name": "Novoferm Vertriebs GmbH",
        "receiver_iban": "DE89370400440532099999",
        "purpose": "Rechnung RE-2025-001 vom 15.08.2025",
        "reference": "RE-2025-001"
    }
    
    print(f"\n📤 Sende Transaktion:")
    print(f"   Datum: {transaction['transaction_date']}")
    print(f"   Betrag: {transaction['amount']} EUR")
    print(f"   Empfänger: {transaction['receiver_name']}")
    print(f"   Verwendungszweck: {transaction['purpose']}")
    
    response = requests.post(
        f"{API_BASE}/api/payment/import-transaction",
        json=transaction
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Transaktion importiert: ID={result['transaction_id']}")
    else:
        print(f"\n❌ Fehler: {response.status_code} - {response.text}")


def example_2_import_csv():
    """Beispiel 2: CSV-Datei importieren"""
    
    print("\n" + "="*80)
    print("📊 BEISPIEL 2: CSV-Datei importieren")
    print("="*80)
    
    # Beispiel-CSV (Sparkasse Format)
    csv_content = """Auftragskonto;Buchungstag;Valutadatum;Buchungstext;Verwendungszweck;Beguenstigter/Zahlungspflichtiger;Kontonummer;BLZ;Betrag;Waehrung;Info
DE89370400440532013000;18.10.2025;18.10.2025;ÜBERWEISUNG;Rechnung RE-2025-101;ACME GmbH;DE89370400440532099999;;-1500,00;EUR;
DE89370400440532013000;17.10.2025;17.10.2025;GUTSCHRIFT;Payment for Invoice RE-2025-102;Best Customer AG;DE89370400440532088888;;2500,00;EUR;RE-2025-102
"""
    
    # Encode to Base64
    csv_b64 = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
    
    print("\n📤 Sende CSV (2 Transaktionen)...")
    
    response = requests.post(
        f"{API_BASE}/api/payment/import-csv",
        json={
            "csv_content": csv_b64,
            "format": "auto"  # Auto-Erkennung
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        stats = result['stats']
        print(f"\n✅ CSV Import abgeschlossen:")
        print(f"   ✅ Importiert: {stats['imported']}")
        print(f"   ⏭️  Übersprungen: {stats['skipped']}")
        print(f"   ❌ Fehler: {stats['errors']}")
    else:
        print(f"\n❌ Fehler: {response.status_code} - {response.text}")


def example_3_auto_match():
    """Beispiel 3: Auto-Matching ausführen"""
    
    print("\n" + "="*80)
    print("🔍 BEISPIEL 3: Auto-Matching")
    print("="*80)
    
    print("\n📤 Starte Auto-Match (min_confidence=0.7)...")
    
    response = requests.post(
        f"{API_BASE}/api/payment/auto-match",
        json={
            "min_confidence": 0.7  # 70% Minimum
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        stats = result['stats']
        
        print(f"\n📊 Auto-Match Ergebnisse:")
        print(f"   Verarbeitet: {stats['processed']}")
        print(f"   ✅ Matched: {stats['matched']}")
        print(f"   ❌ Unmatched: {stats['unmatched']}")
        print(f"   ⚠️  Low Confidence: {stats['low_confidence']}")
        
        match_rate = (stats['matched'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
        print(f"\n   📈 Match-Rate: {match_rate:.1f}%")
    else:
        print(f"\n❌ Fehler: {response.status_code} - {response.text}")


def example_4_get_unmatched():
    """Beispiel 4: Unmatched Transactions anzeigen"""
    
    print("\n" + "="*80)
    print("📋 BEISPIEL 4: Unmatched Transactions")
    print("="*80)
    
    response = requests.get(f"{API_BASE}/api/payment/unmatched")
    
    if response.status_code == 200:
        result = response.json()
        count = result['count']
        transactions = result['transactions']
        
        print(f"\n📊 Gefunden: {count} unmatched transaction(s)")
        
        if transactions:
            print("\n   Offene Transaktionen:")
            for tx in transactions:
                print(f"\n   ID: {tx['id']}")
                print(f"   └─ Datum: {tx.get('transaction_date')}")
                print(f"   └─ Betrag: {tx.get('amount')} EUR")
                print(f"   └─ Verwendungszweck: {tx.get('purpose', '')[:60]}")
        else:
            print("\n   ✅ Alle Transaktionen sind zugeordnet!")
    else:
        print(f"\n❌ Fehler: {response.status_code} - {response.text}")


def example_5_manual_match():
    """Beispiel 5: Manuelle Zuordnung"""
    
    print("\n" + "="*80)
    print("🔗 BEISPIEL 5: Manuelle Zuordnung")
    print("="*80)
    
    # Zuerst unmatched abrufen
    response = requests.get(f"{API_BASE}/api/payment/unmatched")
    
    if response.status_code == 200:
        result = response.json()
        transactions = result['transactions']
        
        if not transactions:
            print("\n   ℹ️  Keine unmatched Transaktionen vorhanden")
            return
        
        # Erste Transaktion nehmen
        tx = transactions[0]
        
        print(f"\n📝 Transaktion:")
        print(f"   ID: {tx['id']}")
        print(f"   Betrag: {tx.get('amount')} EUR")
        print(f"   Verwendungszweck: {tx.get('purpose', '')}")
        
        # Beispiel: Manuell zu RE-2025-103 zuordnen
        invoice_number = "RE-2025-103"
        
        print(f"\n🔗 Zuordnung zu Rechnung: {invoice_number}")
        
        match_response = requests.post(
            f"{API_BASE}/api/payment/match",
            json={
                "transaction_id": tx['id'],
                "invoice_number": invoice_number
            }
        )
        
        if match_response.status_code == 200:
            print(f"\n✅ Match erfolgreich erstellt!")
            print(f"   Rechnung {invoice_number} wird als PAID markiert")
        else:
            print(f"\n❌ Fehler: {match_response.status_code} - {match_response.text}")
    else:
        print(f"\n❌ Fehler beim Abrufen: {response.status_code}")


def example_6_get_statistics():
    """Beispiel 6: Statistiken abrufen"""
    
    print("\n" + "="*80)
    print("📊 BEISPIEL 6: Payment Statistics")
    print("="*80)
    
    response = requests.get(f"{API_BASE}/api/payment/statistics")
    
    if response.status_code == 200:
        result = response.json()
        stats = result['statistics']
        
        print(f"\n📈 Gesamtstatistik:")
        print(f"   Transaktionen gesamt: {stats['total_transactions']}")
        print(f"   ✅ Matched: {stats['matched_count']}")
        print(f"   ❌ Unmatched: {stats['unmatched_count']}")
        print(f"   📊 Match-Rate: {stats['match_rate']:.1f}%")
        print(f"   💰 Matched Amount: {stats['matched_amount']:.2f} EUR")
    else:
        print(f"\n❌ Fehler: {response.status_code} - {response.text}")


def main():
    """Alle Beispiele ausführen"""
    
    print("\n" + "="*80)
    print("💰 PAYMENT MATCHING SYSTEM - BEISPIEL-NUTZUNG")
    print("="*80)
    print(f"\nAPI Base URL: {API_BASE}")
    
    # Beispiele ausführen
    example_1_import_single_transaction()
    
    # Optional: CSV Import (auskommentiert, da keine echte Datei)
    # example_2_import_csv()
    
    example_3_auto_match()
    example_4_get_unmatched()
    
    # Optional: Manuelles Match (nur wenn unmatched vorhanden)
    # example_5_manual_match()
    
    example_6_get_statistics()
    
    print("\n" + "="*80)
    print("✅ ALLE BEISPIELE ABGESCHLOSSEN")
    print("="*80)
    print("\nWeitere Infos: PAYMENT_MATCHING_API_DOCS.md")
    print("")


if __name__ == "__main__":
    main()
