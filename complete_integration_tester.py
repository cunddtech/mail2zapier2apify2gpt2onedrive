#!/usr/bin/env python3
"""
📧 ECHTE EMAIL/RECHNUNGS-INTEGRATION TESTER
============================================

Testet das komplette System mit echten E-Mails und Rechnungen:

1. Email Processing → Invoice Detection → Invoice Monitoring
2. Bank Transaction Import → Umsatzabgleich
3. Notification System → Alert Mails

VOLLSTÄNDIGER WORKFLOW-TEST
"""

import sys
import os
import json
import requests
import time
from datetime import datetime, timedelta

# Add project path
sys.path.append('/Users/cdtechgmbh/railway-orchestrator-clean')

from modules.database.invoice_monitoring import InvoiceMonitoringDB
from modules.database.umsatzabgleich import UmsatzabgleichEngine

RAILWAY_URL = "https://my-langgraph-agent-production.up.railway.app"

def simulate_email_with_invoice():
    """Simuliere E-Mail mit Rechnungsanhang"""
    
    print("📧 SIMULIERE EMAIL MIT RECHNUNG")
    print("=" * 50)
    
    # Erstelle Test-Email Payload (wie von Zapier/Microsoft Graph)
    test_email = {
        "subject": "Rechnung RE-2025-TEST-001 - C&D Technologies",
        "body_content": """
        Sehr geehrte Damen und Herren,
        
        anbei erhalten Sie unsere Rechnung RE-2025-TEST-001 über die erbrachten Dacharbeiten.
        
        Rechnungsbetrag: €2.500,00 (netto)
        Fälligkeitsdatum: 30.11.2025
        
        Vielen Dank für Ihren Auftrag!
        
        Mit freundlichen Grüßen
        Max Muster
        """,
        "from_email_address_address": "test-kunde@example.com",
        "message_id": f"test-message-{int(time.time())}",
        "attachments": [
            {
                "filename": "Rechnung_RE-2025-TEST-001.pdf",
                "size": 156789,
                "content_type": "application/pdf"
            }
        ]
    }
    
    print(f"📬 Sende Test-Email an Railway Orchestrator...")
    print(f"📎 Mit Anhang: {test_email['attachments'][0]['filename']}")
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/webhook/ai-email",
            json=test_email,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email verarbeitet!")
            print(f"📊 Workflow: {result.get('workflow_path', 'N/A')}")
            print(f"🤖 AI Intent: {result.get('ai_analysis', {}).get('intent', 'N/A')}")
            
            # Check if invoice was detected
            processing_result = result.get('processing_result', {})
            if 'invoice_detection' in processing_result:
                print(f"💰 Rechnung erkannt!")
                return result
            else:
                print(f"ℹ️ Keine Rechnung erkannt - reguläre E-Mail Verarbeitung")
                return result
        else:
            print(f"❌ Email-Verarbeitung fehlgeschlagen: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Email-Test Fehler: {e}")
        return None


def check_invoice_monitoring():
    """Prüfe Invoice Monitoring Database"""
    
    print(f"\n📊 PRÜFE INVOICE MONITORING")
    print("=" * 50)
    
    try:
        invoice_db = InvoiceMonitoringDB()
        
        # Get overdue invoices instead of recent (matching actual API)
        overdue_incoming = invoice_db.get_overdue_incoming_invoices()
        overdue_outgoing = invoice_db.get_overdue_outgoing_invoices()
        
        print(f"📥 Überfällige Eingangsrechnungen: {len(overdue_incoming)}")
        print(f"📤 Überfällige Ausgangsrechnungen: {len(overdue_outgoing)}")
        
        # Show some examples
        for invoice in overdue_incoming[:3]:
            print(f"   • {invoice['invoice_number']} - €{invoice['amount']:,.2f} ({invoice['payment_status']})")
        
        # Get critical points
        critical_points = invoice_db.get_critical_points()
        if critical_points:
            print(f"\n🚨 KRITISCHE PUNKTE:")
            for point in critical_points:
                print(f"   • {point}")
        
        # Get weekly summary
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        weekly_summary = invoice_db.get_week_summary(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        print(f"\n📅 WÖCHENTLICHE ZUSAMMENFASSUNG:")
        print(f"   Eingangsrechnungen: {weekly_summary['incoming']['count']} (€{weekly_summary['incoming']['total']:,.2f})")
        print(f"   Ausgangsrechnungen: {weekly_summary['outgoing']['count']} (€{weekly_summary['outgoing']['total']:,.2f})")
        print(f"   Netto Cash Flow: €{weekly_summary['net_cash_flow']:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Invoice Monitoring Fehler: {e}")
        return False


def run_umsatzabgleich_test():
    """Führe Umsatzabgleich mit aktuellen Daten durch"""
    
    print(f"\n💰 UMSATZABGLEICH TEST")
    print("=" * 50)
    
    try:
        engine = UmsatzabgleichEngine()
        
        # Test mit letzten 30 Tagen
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        report = engine.get_umsatzabgleich_report(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        print(f"📊 UMSATZABGLEICH ERGEBNISSE:")
        
        # Matching Rate
        matching = report.get('matching_rate', {})
        print(f"   🎯 Matching Rate: {matching.get('matching_percentage', 0):.1f}%")
        print(f"   ✅ Gematcht: {matching.get('matched_count', 0)}")
        print(f"   📊 Gesamt: {matching.get('total_count', 0)}")
        
        # Financials
        bank_data = report.get('bank_transactions', {})
        invoice_data = report.get('invoice_data', {})
        
        bank_total = bank_data.get('total', 0)
        invoice_total = invoice_data.get('total', 0)
        
        print(f"\n💰 FINANZÜBERSICHT:")
        print(f"   Bank Netto: €{bank_total:,.2f}")
        print(f"   Rechnungen: €{invoice_total:,.2f}")
        print(f"   Differenz: €{bank_total - invoice_total:,.2f}")
        
        # Variances
        variances = report.get('variances', {})
        for var_type, amount in variances.items():
            if abs(amount) > 50:  # Only show significant variances
                print(f"   {var_type}: €{amount:,.2f}")
        
        # Critical Check
        critical_issues = []
        matching_rate = matching.get('matching_percentage', 100)
        if matching_rate < 80:
            critical_issues.append(f"Niedrige Matching Rate: {matching_rate:.1f}%")
        
        net_variance = abs(variances.get('net_variance', 0))
        if net_variance > 500:
            critical_issues.append(f"Hohe Abweichung: €{net_variance:,.2f}")
        
        if critical_issues:
            print(f"\n🚨 KRITISCHE PUNKTE:")
            for issue in critical_issues:
                print(f"   • {issue}")
            return critical_issues
        else:
            print(f"\n✅ Keine kritischen Abweichungen")
            return []
        
    except Exception as e:
        print(f"❌ Umsatzabgleich Fehler: {e}")
        return None


def test_notification_system(critical_issues=None):
    """Teste das Notification System"""
    
    print(f"\n📧 NOTIFICATION SYSTEM TEST")
    print("=" * 50)
    
    try:
        # Test standard notification
        response = requests.post(
            f"{RAILWAY_URL}/api/umsatzabgleich/notification-test",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print(f"✅ Test-Benachrichtigung erfolgreich gesendet!")
            else:
                print(f"❌ Test-Benachrichtigung fehlgeschlagen: {result.get('message')}")
        
        # If we have critical issues, test critical notification
        if critical_issues:
            print(f"\n🚨 Sende kritische Benachrichtigung...")
            
            # This would be called automatically by the system
            # For testing, we simulate the critical notification
            test_critical_data = {
                "period": "Test-Integration",
                "matching_rate": {"matching_percentage": 75.0},
                "variances": {"net_variance": 1500.00},
                "bank_transactions": {"total": 25000.00},
                "invoice_data": {"total": 23500.00},
                "critical_points": critical_issues
            }
            
            print(f"   📊 Kritische Daten simuliert")
            print(f"   📧 In Produktion würde jetzt automatische E-Mail gesendet")
        
        return True
        
    except Exception as e:
        print(f"❌ Notification Test Fehler: {e}")
        return False


def run_complete_integration_test():
    """Führe kompletten Integration Test durch"""
    
    print("🚀 VOLLSTÄNDIGER INTEGRATION TEST")
    print("=" * 70)
    print("📧 Email → 💰 Invoice → 🏦 Bank → 📊 Abgleich → 📬 Notification")
    print("=" * 70)
    
    # Step 1: Email Processing
    print(f"\n🔄 SCHRITT 1: Email Processing")
    email_result = simulate_email_with_invoice()
    
    if not email_result:
        print(f"❌ Email Processing fehlgeschlagen - Test abgebrochen")
        return False
    
    time.sleep(2)  # Give system time to process
    
    # Step 2: Invoice Monitoring Check
    print(f"\n🔄 SCHRITT 2: Invoice Monitoring")
    invoice_success = check_invoice_monitoring()
    
    if not invoice_success:
        print(f"⚠️ Invoice Monitoring Probleme erkannt")
    
    # Step 3: Umsatzabgleich
    print(f"\n🔄 SCHRITT 3: Umsatzabgleich")
    critical_issues = run_umsatzabgleich_test()
    
    # Step 4: Notification System
    print(f"\n🔄 SCHRITT 4: Notification System")
    notification_success = test_notification_system(critical_issues)
    
    # Final Summary
    print(f"\n📊 INTEGRATION TEST ZUSAMMENFASSUNG")
    print("=" * 50)
    print(f"✅ Email Processing: {'OK' if email_result else 'FEHLER'}")
    print(f"✅ Invoice Monitoring: {'OK' if invoice_success else 'FEHLER'}")
    print(f"✅ Umsatzabgleich: {'OK' if critical_issues is not None else 'FEHLER'}")
    print(f"✅ Notifications: {'OK' if notification_success else 'FEHLER'}")
    
    if critical_issues:
        print(f"\n🚨 Kritische Punkte erkannt: {len(critical_issues)}")
        for issue in critical_issues:
            print(f"   • {issue}")
    
    return True


def main():
    print("📧💰 ECHTE EMAIL/RECHNUNGS-INTEGRATION TESTER")
    print("=" * 70)
    print("🎯 Vollständiger Workflow-Test mit Railway Integration")
    print()
    
    choice = input("🔄 Vollständigen Integration Test starten? (y/n): ").lower()
    
    if choice == 'y':
        run_complete_integration_test()
    else:
        print("📋 Verfügbare Einzeltests:")
        print("   1. Email Processing Test")
        print("   2. Invoice Monitoring Check")
        print("   3. Umsatzabgleich Test")
        print("   4. Notification Test")
        
        try:
            test_choice = int(input("🔢 Test auswählen (1-4): "))
            
            if test_choice == 1:
                simulate_email_with_invoice()
            elif test_choice == 2:
                check_invoice_monitoring()
            elif test_choice == 3:
                run_umsatzabgleich_test()
            elif test_choice == 4:
                test_notification_system()
            else:
                print("❌ Ungültige Auswahl")
                
        except ValueError:
            print("❌ Ungültige Eingabe")


if __name__ == "__main__":
    main()