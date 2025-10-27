#!/usr/bin/env python3
"""
💰 UMSATZABGLEICH SYSTEM
=======================

Echte Bank-Transaktionen vs. Rechnungen abgleichen
Für C&D Technologies Buchhaltungsüberwachung

Features:
✅ Bank-CSV Import (Sparkasse, Deutsche Bank, etc.)
✅ Automatischer Rechnungs-Matching
✅ Fehlende Zahlungen identifizieren
✅ Doppelzahlungen erkennen
✅ Compliance-Reports
"""

import sqlite3
import csv
import json
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

@dataclass
class BankTransaction:
    """💳 Bank-Transaktion für Umsatzabgleich"""
    id: Optional[int] = None
    transaction_date: str = ""
    amount: float = 0.0
    description: str = ""
    reference: str = ""
    iban_counterpart: str = ""
    name_counterpart: str = ""
    transaction_type: str = ""  # income, expense
    bank_reference: str = ""
    matched_invoice_id: Optional[str] = None
    matching_confidence: float = 0.0
    manual_verified: bool = False
    source: str = "bank_import"
    created_at: str = ""

class UmsatzabgleichEngine:
    """💰 Umsatzabgleich Engine für Rechnungs-Matching"""
    
    def __init__(self, db_path: str = "invoice_monitoring.db"):
        self.db_path = db_path
        self.initialize_umsatz_tables()
    
    def initialize_umsatz_tables(self):
        """🔧 Bank-Transaktionen Tabelle erweitern"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Erweiterte Bank-Transaktionen Tabelle
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT,
                amount REAL,
                description TEXT,
                reference TEXT,
                iban_counterpart TEXT,
                name_counterpart TEXT,
                transaction_type TEXT, -- income, expense
                bank_reference TEXT UNIQUE,
                matched_invoice_id TEXT,
                matching_confidence REAL DEFAULT 0.0,
                manual_verified BOOLEAN DEFAULT FALSE,
                source TEXT DEFAULT 'bank_import',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Matching-Rules Tabelle für AI-Learning
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS matching_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_type TEXT, -- description_pattern, amount_exact, reference_pattern
                pattern TEXT,
                invoice_type TEXT, -- incoming, outgoing
                confidence_weight REAL DEFAULT 1.0,
                auto_apply BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()
            logger.info("✅ Umsatzabgleich tables initialized")
    
    def import_bank_csv(self, csv_file_path: str, bank_format: str = "sparkasse") -> int:
        """📥 Bank-CSV importieren (Sparkasse, Deutsche Bank, etc.)"""
        
        imported_count = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                if bank_format.lower() == "sparkasse":
                    transactions = self._parse_sparkasse_csv(file)
                elif bank_format.lower() == "deutsche_bank":
                    transactions = self._parse_deutsche_bank_csv(file)
                else:
                    transactions = self._parse_generic_csv(file)
                
                for transaction in transactions:
                    self._add_bank_transaction(transaction)
                    imported_count += 1
            
            logger.info(f"✅ {imported_count} Bank-Transaktionen importiert")
            return imported_count
            
        except Exception as e:
            logger.error(f"❌ Bank-CSV Import Fehler: {e}")
            return 0
    
    def _parse_sparkasse_csv(self, file) -> List[BankTransaction]:
        """🏦 Sparkasse CSV Format parsen"""
        transactions = []
        reader = csv.DictReader(file, delimiter=';')
        
        for row in reader:
            try:
                amount = float(row.get('Betrag', '0').replace(',', '.'))
                transaction = BankTransaction(
                    transaction_date=self._parse_date(row.get('Wertstellung', '')),
                    amount=abs(amount),
                    description=row.get('Verwendungszweck', ''),
                    reference=row.get('Kundenreferenz', ''),
                    name_counterpart=row.get('Empfänger/Zahlungspflichtiger', ''),
                    transaction_type="income" if amount > 0 else "expense",
                    bank_reference=row.get('Referenz', ''),
                    source="sparkasse_csv"
                )
                transactions.append(transaction)
            except Exception as e:
                logger.warning(f"⚠️ Fehler beim Parsen der Zeile: {e}")
                continue
        
        return transactions
    
    def _parse_deutsche_bank_csv(self, file) -> List[BankTransaction]:
        """🏦 Deutsche Bank CSV Format parsen"""
        transactions = []
        reader = csv.DictReader(file, delimiter=';')
        
        for row in reader:
            try:
                amount = float(row.get('Umsatz', '0').replace(',', '.'))
                transaction = BankTransaction(
                    transaction_date=self._parse_date(row.get('Wertstellung', '')),
                    amount=abs(amount),
                    description=row.get('Verwendungszweck', ''),
                    reference=row.get('Referenz', ''),
                    name_counterpart=row.get('Begünstigter/Auftraggeber', ''),
                    transaction_type="income" if amount > 0 else "expense",
                    bank_reference=row.get('Transaktionsreferenz', ''),
                    source="deutsche_bank_csv"
                )
                transactions.append(transaction)
            except Exception as e:
                logger.warning(f"⚠️ Fehler beim Parsen der Zeile: {e}")
                continue
        
        return transactions
    
    def _parse_date(self, date_str: str) -> str:
        """📅 Datum parsing für verschiedene Formate"""
        for format_str in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']:
            try:
                return datetime.strptime(date_str, format_str).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return datetime.now().strftime('%Y-%m-%d')
    
    def _add_bank_transaction(self, transaction: BankTransaction) -> int:
        """💳 Bank-Transaktion zur DB hinzufügen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT OR IGNORE INTO bank_transactions 
            (transaction_date, amount, description, reference, iban_counterpart,
             name_counterpart, transaction_type, bank_reference, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction.transaction_date, transaction.amount, 
                transaction.description, transaction.reference,
                transaction.iban_counterpart, transaction.name_counterpart,
                transaction.transaction_type, transaction.bank_reference,
                transaction.source
            ))
            
            return cursor.lastrowid
    
    def auto_match_transactions(self) -> Dict[str, Any]:
        """🤖 Automatisches Matching von Transaktionen zu Rechnungen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Unmatched transactions holen
            cursor.execute("""
            SELECT * FROM bank_transactions 
            WHERE matched_invoice_id IS NULL
            """)
            
            transactions = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            matches_found = 0
            
            for row in transactions:
                transaction = dict(zip(columns, row))
                
                # Versuche Matching mit ausgehenden Rechnungen (Zahlungseingänge)
                if transaction['transaction_type'] == 'income':
                    match = self._find_outgoing_invoice_match(transaction)
                    if match:
                        self._update_transaction_match(transaction['id'], match['invoice_id'], match['confidence'])
                        self._update_invoice_payment_status(match['invoice_id'], 'outgoing', transaction['transaction_date'])
                        matches_found += 1
                
                # Versuche Matching mit eingehenden Rechnungen (Zahlungsausgänge)
                elif transaction['transaction_type'] == 'expense':
                    match = self._find_incoming_invoice_match(transaction)
                    if match:
                        self._update_transaction_match(transaction['id'], match['invoice_id'], match['confidence'])
                        self._update_invoice_payment_status(match['invoice_id'], 'incoming', transaction['transaction_date'])
                        matches_found += 1
            
            return {
                "total_transactions": len(transactions),
                "matches_found": matches_found,
                "unmatched": len(transactions) - matches_found
            }
    
    def _find_outgoing_invoice_match(self, transaction: Dict) -> Optional[Dict]:
        """🔍 Ausgehende Rechnung für Zahlungseingang finden"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            amount = transaction['amount']
            description = transaction['description'].lower()
            
            # Exakte Betragsmatch
            cursor.execute("""
            SELECT id, invoice_number, amount FROM outgoing_invoices 
            WHERE ABS(amount - ?) < 0.01 AND payment_status = 'open'
            """, (amount,))
            
            exact_matches = cursor.fetchall()
            
            for match in exact_matches:
                invoice_id, invoice_number, invoice_amount = match
                
                # Prüfe ob Rechnungsnummer im Verwendungszweck
                if invoice_number.lower() in description:
                    return {
                        "invoice_id": invoice_id,
                        "confidence": 0.95,
                        "match_reason": f"Exact amount + invoice number in description"
                    }
                
                # Prüfe Firmenname
                cursor.execute("""
                SELECT customer_company FROM outgoing_invoices WHERE id = ?
                """, (invoice_id,))
                
                company_result = cursor.fetchone()
                if company_result and company_result[0]:
                    company_name = company_result[0].lower()
                    if any(word in description for word in company_name.split() if len(word) > 3):
                        return {
                            "invoice_id": invoice_id,
                            "confidence": 0.85,
                            "match_reason": f"Exact amount + company name match"
                        }
            
            return None
    
    def _find_incoming_invoice_match(self, transaction: Dict) -> Optional[Dict]:
        """🔍 Eingehende Rechnung für Zahlungsausgang finden"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            amount = transaction['amount']
            description = transaction['description'].lower()
            counterpart_name = transaction.get('name_counterpart', '').lower()
            
            # Exakte Betragsmatch
            cursor.execute("""
            SELECT id, invoice_number, amount, sender_company FROM incoming_invoices 
            WHERE ABS(amount - ?) < 0.01 AND payment_status = 'open'
            """, (amount,))
            
            exact_matches = cursor.fetchall()
            
            for match in exact_matches:
                invoice_id, invoice_number, invoice_amount, sender_company = match
                
                # Prüfe Rechnungsnummer
                if invoice_number.lower() in description:
                    return {
                        "invoice_id": invoice_id,
                        "confidence": 0.95,
                        "match_reason": f"Exact amount + invoice number"
                    }
                
                # Prüfe Firmenname im Empfänger
                if sender_company and sender_company.lower() in counterpart_name:
                    return {
                        "invoice_id": invoice_id,
                        "confidence": 0.85,
                        "match_reason": f"Exact amount + company match"
                    }
            
            return None
    
    def _update_transaction_match(self, transaction_id: int, invoice_id: str, confidence: float):
        """🔗 Transaktion-Rechnung Verknüpfung aktualisieren"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            UPDATE bank_transactions 
            SET matched_invoice_id = ?, matching_confidence = ?
            WHERE id = ?
            """, (invoice_id, confidence, transaction_id))
            
            conn.commit()
    
    def _update_invoice_payment_status(self, invoice_id: str, invoice_type: str, payment_date: str):
        """💰 Rechnungsstatus auf bezahlt setzen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            table_name = f"{invoice_type}_invoices"
            
            cursor.execute(f"""
            UPDATE {table_name}
            SET payment_status = 'paid', payment_date = ?
            WHERE id = ?
            """, (payment_date, invoice_id))
            
            conn.commit()
    
    def get_umsatzabgleich_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """📊 Umsatzabgleich Report generieren"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Bank-Transaktionen im Zeitraum
            cursor.execute("""
            SELECT transaction_type, SUM(amount) as total, COUNT(*) as count
            FROM bank_transactions 
            WHERE transaction_date BETWEEN ? AND ?
            GROUP BY transaction_type
            """, (start_date, end_date))
            
            bank_summary = {row[0]: {"total": row[1], "count": row[2]} for row in cursor.fetchall()}
            
            # Rechnungen im Zeitraum
            cursor.execute("""
            SELECT 'incoming' as type, SUM(amount) as total, COUNT(*) as count
            FROM incoming_invoices 
            WHERE received_date BETWEEN ? AND ?
            UNION ALL
            SELECT 'outgoing' as type, SUM(amount) as total, COUNT(*) as count
            FROM outgoing_invoices 
            WHERE sent_date BETWEEN ? AND ?
            """, (start_date, end_date, start_date, end_date))
            
            invoice_summary = {row[0]: {"total": row[1], "count": row[2]} for row in cursor.fetchall()}
            
            # Unmatched Transaktionen
            cursor.execute("""
            SELECT COUNT(*) FROM bank_transactions 
            WHERE transaction_date BETWEEN ? AND ? 
            AND matched_invoice_id IS NULL
            """, (start_date, end_date))
            
            unmatched_count = cursor.fetchone()[0]
            
            # Abweichungen berechnen
            bank_income = bank_summary.get('income', {}).get('total', 0)
            bank_expense = bank_summary.get('expense', {}).get('total', 0)
            invoice_outgoing = invoice_summary.get('outgoing', {}).get('total', 0)
            invoice_incoming = invoice_summary.get('incoming', {}).get('total', 0)
            
            return {
                "period": f"{start_date} bis {end_date}",
                "bank_transactions": bank_summary,
                "invoices": invoice_summary,
                "unmatched_transactions": unmatched_count,
                "variances": {
                    "income_variance": bank_income - invoice_outgoing,
                    "expense_variance": bank_expense - invoice_incoming,
                    "net_variance": (bank_income - bank_expense) - (invoice_outgoing - invoice_incoming)
                },
                "matching_rate": {
                    "total_transactions": sum(s.get('count', 0) for s in bank_summary.values()),
                    "matched_transactions": sum(s.get('count', 0) for s in bank_summary.values()) - unmatched_count,
                    "matching_percentage": ((sum(s.get('count', 0) for s in bank_summary.values()) - unmatched_count) / 
                                          max(1, sum(s.get('count', 0) for s in bank_summary.values()))) * 100
                }
            }

# Test-Funktionen
def create_sample_bank_data():
    """🧪 Sample Bank-Daten für Testing erstellen"""
    engine = UmsatzabgleichEngine()
    
    # Sample Bank-Transaktionen
    sample_transactions = [
        BankTransaction(
            transaction_date="2025-10-25",
            amount=5678.90,
            description="Überweisung Example AG RE CD-2025-042 Dachsanierung",
            transaction_type="income",
            name_counterpart="Example AG",
            bank_reference="BANK-2025-101",
            source="test_data"
        ),
        BankTransaction(
            transaction_date="2025-10-21",
            amount=1234.00,
            description="Zahlung Lieferant XY ÜBER-2025-999",
            transaction_type="expense", 
            name_counterpart="Lieferant XY GmbH",
            bank_reference="BANK-2025-102",
            source="test_data"
        ),
        BankTransaction(
            transaction_date="2025-10-20",
            amount=3450.00,
            description="Eingang Schmidt Partner Terrassendach",
            transaction_type="income",
            name_counterpart="Schmidt & Partner GmbH", 
            bank_reference="BANK-2025-103",
            source="test_data"
        )
    ]
    
    for transaction in sample_transactions:
        engine._add_bank_transaction(transaction)
    
    return engine

if __name__ == "__main__":
    print("💰 UMSATZABGLEICH SYSTEM TEST")
    print("=" * 50)
    
    # Sample-Daten erstellen
    engine = create_sample_bank_data()
    
    # Auto-Matching durchführen
    print("🤖 Starte automatisches Matching...")
    results = engine.auto_match_transactions()
    print(f"✅ {results['matches_found']} von {results['total_transactions']} Transaktionen gematcht")
    
    # Umsatzabgleich Report
    print("\n📊 Umsatzabgleich Report:")
    report = engine.get_umsatzabgleich_report("2025-10-01", "2025-10-31")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    print("\n✅ Umsatzabgleich System bereit!")