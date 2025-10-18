"""
📥 Bank Transaction CSV Import
Unterstützt verschiedene CSV-Formate (Sparkasse, Volksbank, etc.)
"""

import csv
from datetime import datetime
from typing import List, Dict
import logging
from modules.database.payment_matching import import_bank_transaction

logger = logging.getLogger(__name__)


def parse_german_date(date_str: str) -> str:
    """
    Parse German date formats to ISO format
    
    Formats:
    - 18.10.2025
    - 18.10.25
    - 2025-10-18
    """
    
    if not date_str:
        return None
    
    try:
        # Try DD.MM.YYYY
        if "." in date_str:
            parts = date_str.split(".")
            if len(parts[2]) == 2:
                # 2-digit year
                parts[2] = "20" + parts[2]
            return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        
        # Already ISO format
        if "-" in date_str:
            return date_str
        
    except:
        pass
    
    return None


def parse_german_amount(amount_str: str) -> float:
    """
    Parse German number format to float
    
    Examples:
    - "1.500,00" → 1500.00
    - "-750,50" → -750.50
    - "2500.00" → 2500.00
    """
    
    if not amount_str:
        return 0.0
    
    # Remove spaces
    amount_str = amount_str.strip()
    
    # German format: . as thousands separator, , as decimal
    if "," in amount_str:
        amount_str = amount_str.replace(".", "").replace(",", ".")
    
    try:
        return float(amount_str)
    except:
        return 0.0


def import_csv_sparkasse(csv_path: str) -> Dict:
    """
    Import Sparkasse CSV format
    
    Expected columns:
    - Auftragskonto, Buchungstag, Valutadatum, Buchungstext,
      Verwendungszweck, Beguenstigter/Zahlungspflichtiger,
      Kontonummer, BLZ, Betrag, Waehrung, Info
    """
    
    stats = {"imported": 0, "skipped": 0, "errors": 0}
    
    with open(csv_path, 'r', encoding='latin-1') as f:
        # Skip header lines (Sparkasse has multiple)
        lines = f.readlines()
        
        # Find header row (starts with "Auftragskonto")
        header_idx = 0
        for i, line in enumerate(lines):
            if "Auftragskonto" in line:
                header_idx = i
                break
        
        # Parse CSV from header
        reader = csv.DictReader(lines[header_idx:], delimiter=';')
        
        for row in reader:
            try:
                # Extract IBAN from Kontonummer/BLZ if available
                receiver_iban = row.get("Kontonummer", "")
                if not receiver_iban.startswith("DE"):
                    receiver_iban = None
                
                transaction_data = {
                    "transaction_id": f"SPK-{row.get('Buchungstag', '')}-{row.get('Betrag', '')}",
                    "transaction_date": parse_german_date(row.get("Buchungstag")),
                    "value_date": parse_german_date(row.get("Valutadatum")),
                    "amount": parse_german_amount(row.get("Betrag")),
                    "currency": row.get("Waehrung", "EUR"),
                    "sender_name": row.get("Beguenstigter/Zahlungspflichtiger") if parse_german_amount(row.get("Betrag", "0")) < 0 else None,
                    "sender_iban": row.get("Auftragskonto") if parse_german_amount(row.get("Betrag", "0")) < 0 else receiver_iban,
                    "receiver_name": row.get("Beguenstigter/Zahlungspflichtiger") if parse_german_amount(row.get("Betrag", "0")) > 0 else None,
                    "receiver_iban": receiver_iban if parse_german_amount(row.get("Betrag", "0")) > 0 else row.get("Auftragskonto"),
                    "purpose": row.get("Verwendungszweck", ""),
                    "reference": row.get("Info", ""),
                    "transaction_type": "credit" if parse_german_amount(row.get("Betrag", "0")) > 0 else "debit"
                }
                
                if transaction_data["transaction_date"]:
                    import_bank_transaction(transaction_data)
                    stats["imported"] += 1
                else:
                    stats["skipped"] += 1
                    
            except Exception as e:
                logger.error(f"Error importing row: {e}")
                stats["errors"] += 1
    
    logger.info(f"CSV Import complete: {stats['imported']} imported, {stats['skipped']} skipped, {stats['errors']} errors")
    
    return stats


def import_csv_generic(csv_path: str, column_mapping: Dict = None) -> Dict:
    """
    Import generic CSV with custom column mapping
    
    Args:
        csv_path: Path to CSV file
        column_mapping: Dict mapping CSV columns to transaction fields
            Example:
            {
                "Date": "transaction_date",
                "Amount": "amount",
                "Description": "purpose",
                "Recipient": "receiver_name"
            }
    """
    
    if column_mapping is None:
        # Default mapping (English)
        column_mapping = {
            "Date": "transaction_date",
            "Value Date": "value_date",
            "Amount": "amount",
            "Currency": "currency",
            "Sender": "sender_name",
            "Sender IBAN": "sender_iban",
            "Receiver": "receiver_name",
            "Receiver IBAN": "receiver_iban",
            "Description": "purpose",
            "Reference": "reference"
        }
    
    stats = {"imported": 0, "skipped": 0, "errors": 0}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            try:
                transaction_data = {}
                
                for csv_col, field_name in column_mapping.items():
                    if csv_col in row:
                        value = row[csv_col]
                        
                        # Parse dates
                        if "date" in field_name:
                            value = parse_german_date(value)
                        
                        # Parse amounts
                        if field_name == "amount":
                            value = parse_german_amount(value)
                        
                        transaction_data[field_name] = value
                
                # Generate transaction ID if not provided
                if "transaction_id" not in transaction_data:
                    transaction_data["transaction_id"] = f"CSV-{i}-{transaction_data.get('transaction_date', '')}"
                
                # Set currency default
                if "currency" not in transaction_data:
                    transaction_data["currency"] = "EUR"
                
                # Determine transaction type
                if "transaction_type" not in transaction_data:
                    amount = transaction_data.get("amount", 0)
                    transaction_data["transaction_type"] = "credit" if amount > 0 else "debit"
                
                if transaction_data.get("transaction_date"):
                    import_bank_transaction(transaction_data)
                    stats["imported"] += 1
                else:
                    stats["skipped"] += 1
                    
            except Exception as e:
                logger.error(f"Error importing row {i}: {e}")
                stats["errors"] += 1
    
    logger.info(f"CSV Import complete: {stats['imported']} imported, {stats['skipped']} skipped, {stats['errors']} errors")
    
    return stats


def import_csv_auto_detect(csv_path: str) -> Dict:
    """
    Auto-detect CSV format and import
    """
    
    # Read first few lines to detect format
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        first_lines = [f.readline() for _ in range(5)]
    
    header = "".join(first_lines)
    
    # Sparkasse format detection
    if "Auftragskonto" in header and "Buchungstag" in header:
        logger.info("📊 Detected: Sparkasse CSV format")
        return import_csv_sparkasse(csv_path)
    
    # Volksbank format
    elif "Buchung" in header and "Valuta" in header:
        logger.info("📊 Detected: Volksbank CSV format")
        # Similar to Sparkasse
        return import_csv_sparkasse(csv_path)
    
    # Generic English format
    elif "Date" in header and "Amount" in header:
        logger.info("📊 Detected: Generic English CSV format")
        return import_csv_generic(csv_path)
    
    else:
        logger.warning("⚠️ Unknown CSV format - attempting generic import")
        return import_csv_generic(csv_path)
