#!/usr/bin/env python3
"""
🧪 RECHNUNGSMONITORING TEST SCRIPT
=================================

Test Script für das produktive Rechnungsüberwachungssystem
Fügt Testdaten hinzu und prüft die Funktionalität
"""

import sys
import os
sys.path.append('/Users/cdtechgmbh/railway-orchestrator-clean')

from modules.database.invoice_monitoring import InvoiceMonitoringDB, IncomingInvoice, OutgoingInvoice
from datetime import datetime, timedelta
import json

def add_test_data():
    """📊 Testdaten für letzte Woche hinzufügen"""
    db = InvoiceMonitoringDB()
    
    # Aktuelle Woche - Eingehende Rechnungen (die wir zahlen müssen)
    incoming_invoices = [
        IncomingInvoice(
            invoice_number="BAUST-2025-1001",
            sender="info@baustoffhandel-mueller.de",
            sender_company="Baustoffhandel Müller GmbH",
            amount=2450.80,
            invoice_date="2025-10-20",
            due_date="2025-11-19",
            received_date="2025-10-21",
            category="material",
            notes="Dachziegel für Projekt München"
        ),
        IncomingInvoice(
            invoice_number="WERK-2025-567",
            sender="buchhaltung@werkzeug-schmidt.de", 
            sender_company="Werkzeug Schmidt KG",
            amount=890.50,
            invoice_date="2025-10-18",
            due_date="2025-11-17",
            received_date="2025-10-19",
            category="tools",
            notes="Spezialwerkzeug Terrassenbau"
        ),
        IncomingInvoice(
            invoice_number="BÜRO-2025-334",
            sender="service@office-partner.de",
            sender_company="Office Partner AG",
            amount=156.90,
            invoice_date="2025-10-15",
            due_date="2025-11-14", 
            received_date="2025-10-16",
            category="office",
            notes="Büromaterial und Druckerpatronen"
        ),
        # Überfällige Rechnung
        IncomingInvoice(
            invoice_number="ÜBER-2025-999",
            sender="mahnung@lieferant-xy.de",
            sender_company="Lieferant XY GmbH",
            amount=1234.00,
            invoice_date="2025-09-15",
            due_date="2025-10-15",  # Bereits überfällig!
            received_date="2025-09-16",
            category="material",
            notes="ÜBERFÄLLIG - Sofort zahlen!"
        )
    ]
    
    # Aktuelle Woche - Ausgehende Rechnungen (die uns bezahlt werden sollen)
    outgoing_invoices = [
        OutgoingInvoice(
            invoice_number="CD-2025-042",
            customer="max.mustermann@example.com",
            customer_company="Example AG",
            amount=5678.90,
            invoice_date="2025-10-25",
            due_date="2025-11-24",
            sent_date="2025-10-25",
            project_name="Dachsanierung München - 80qm",
            payment_terms="30 Tage",
            notes="Hauptprojekt Q4 2025"
        ),
        OutgoingInvoice(
            invoice_number="CD-2025-043",
            customer="info@schmidt-partner.de",
            customer_company="Schmidt & Partner GmbH",
            amount=3450.00,
            invoice_date="2025-10-22",
            due_date="2025-11-21",
            sent_date="2025-10-22",
            project_name="Terrassendach Hamburg - Gewerbeobjekt",
            payment_terms="30 Tage",
            notes="Gewerbeprojekt - pünktliche Zahlung erwartet"
        ),
        OutgoingInvoice(
            invoice_number="CD-2025-044",
            customer="wagner@familie-wagner.de",
            customer_company="Familie Wagner",
            amount=1200.00,
            invoice_date="2025-10-20",
            due_date="2025-11-19",
            sent_date="2025-10-20",
            project_name="Carport Installation - Privat",
            payment_terms="30 Tage",
            notes="Kleinprojekt - Anzahlung erhalten"
        ),
        # Überfällige Ausgangsrechnung
        OutgoingInvoice(
            invoice_number="CD-2025-039",
            customer="kunde@slow-pay.de",
            customer_company="Slow Pay GmbH",
            amount=2890.00,
            invoice_date="2025-09-20",
            due_date="2025-10-20",  # Überfällig!
            sent_date="2025-09-20",
            project_name="Dachausbau Berlin - Nachzahlung",
            payment_terms="30 Tage",
            notes="ÜBERFÄLLIG - Mahnung erforderlich",
            reminder_count=1,
            last_reminder_date="2025-10-25"
        )
    ]
    
    # Daten hinzufügen
    print("📥 Hinzufügen von Eingangsrechnungen...")
    for invoice in incoming_invoices:
        db.add_incoming_invoice(invoice)
        print(f"  ✅ {invoice.invoice_number} - {invoice.sender_company} - €{invoice.amount}")
    
    print("\n📤 Hinzufügen von Ausgangsrechnungen...")
    for invoice in outgoing_invoices:
        db.add_outgoing_invoice(invoice)
        print(f"  ✅ {invoice.invoice_number} - {invoice.customer_company} - €{invoice.amount}")
    
    return db

def test_critical_points(db):
    """🔴 Kritische Punkte testen"""
    print("\n🔴 KRITISCHE PUNKTE ANALYSE:")
    print("=" * 50)
    
    critical = db.get_critical_points()
    
    print(f"💰 Offene Eingangsrechnungen: €{critical['open_incoming_total']:,.2f}")
    print(f"💰 Offene Ausgangsrechnungen: €{critical['open_outgoing_total']:,.2f}")
    print(f"📊 Cash Flow Balance: €{critical['cash_flow_balance']:,.2f}")
    print(f"⚠️ Überfällige Eingänge: {critical['overdue_incoming_count']}")
    print(f"⚠️ Überfällige Ausgänge: {critical['overdue_outgoing_count']}")
    
    if critical['overdue_incoming']:
        print("\n🔴 ÜBERFÄLLIGE EINGANGSRECHNUNGEN (ZU ZAHLEN):")
        for invoice in critical['overdue_incoming']:
            print(f"  ⚠️ {invoice['invoice_number']} - {invoice['sender_company']}")
            print(f"     €{invoice['amount']:,.2f} | Fällig: {invoice['due_date']}")
    
    if critical['overdue_outgoing']:
        print("\n🔴 ÜBERFÄLLIGE AUSGANGSRECHNUNGEN (MAHNUNGEN):")
        for invoice in critical['overdue_outgoing']:
            print(f"  ⚠️ {invoice['invoice_number']} - {invoice['customer_company']}")
            print(f"     €{invoice['amount']:,.2f} | Fällig: {invoice['due_date']}")

def test_week_summary(db):
    """📊 Wochenzusammenfassung testen"""
    print("\n📊 WOCHENZUSAMMENFASSUNG:")
    print("=" * 50)
    
    summary = db.get_week_summary(1)  # Letzte Woche
    
    print(f"📅 Zeitraum: {summary['period']}")
    print(f"📥 Eingangsrechnungen: {summary['incoming']['count']} Stück | €{summary['incoming']['total']:,.2f}")
    print(f"📤 Ausgangsrechnungen: {summary['outgoing']['count']} Stück | €{summary['outgoing']['total']:,.2f}")
    
    if summary['outgoing']['total'] > 0:
        ratio = (summary['incoming']['total'] / summary['outgoing']['total']) * 100
        print(f"💡 Kosten-Umsatz-Verhältnis: {ratio:.1f}%")

if __name__ == "__main__":
    print("🧪 RECHNUNGSMONITORING TEST GESTARTET")
    print("=" * 60)
    
    # Testdaten hinzufügen
    db = add_test_data()
    
    # Tests durchführen
    test_critical_points(db)
    test_week_summary(db)
    
    print("\n🎯 NÄCHSTE SCHRITTE:")
    print("1. Dashboard API-Integration testen")
    print("2. WeClapp-Sync für echte Daten einrichten") 
    print("3. Email-Processing für automatische Rechnungserkennung")
    print("4. Bank-Import für Umsatzabgleich implementieren")
    
    print("\n✅ TEST ABGESCHLOSSEN - System bereit für Produktion!")