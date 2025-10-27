#!/usr/bin/env python3
"""
🚀 RAILWAY API ENDPOINT - INTELLIGENTES RECHNUNGSMANAGEMENT
==========================================================

API Endpoint für die Integration in production_langgraph_orchestrator.py
Stellt das intelligente Rechnungsmanagement als REST API zur Verfügung
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import sys
import os
from datetime import datetime

# Add project path
sys.path.append('/Users/cdtechgmbh/railway-orchestrator-clean')

from intelligent_invoice_system import IntelligentInvoiceManager

# Router für Railway Integration
intelligent_invoice_router = APIRouter(prefix="/api/intelligent-invoice", tags=["Intelligent Invoice Management"])

@intelligent_invoice_router.get("/analyze")
async def run_intelligent_invoice_analysis() -> Dict[str, Any]:
    """
    🎯 VOLLSTÄNDIGE RECHNUNGSANALYSE
    
    Führt komplette Analyse aus:
    1. E-Mail Scanning nach Rechnungen
    2. Bank-Abgleich für Zahlungsstatus
    3. Unzugeordnete Transaktionen finden
    4. WeClapp Ausgangsrechnungen prüfen
    5. Steuerberater-Report generieren
    """
    
    try:
        manager = IntelligentInvoiceManager()
        result = manager.run_complete_analysis()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "analysis_result": result,
            "summary": {
                "incoming_invoices_total": result['incoming_invoices']['total'],
                "incoming_invoices_paid": result['incoming_invoices']['paid'],
                "incoming_invoices_unpaid": result['incoming_invoices']['unpaid'],
                "unmatched_transactions": result['unmatched_transactions']['total'],
                "missing_receipts": result['unmatched_transactions']['missing_receipts'],
                "tax_report_file": result['tax_report']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invoice analysis failed: {str(e)}")

@intelligent_invoice_router.get("/scan-emails")
async def scan_emails_for_invoices(days_back: int = 30) -> Dict[str, Any]:
    """
    📧 E-MAIL SCANNING
    
    Scannt E-Mails nach Rechnungsanhängen
    """
    
    try:
        manager = IntelligentInvoiceManager()
        invoices = manager.scan_incoming_emails_for_invoices(days_back)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "invoices_found": len(invoices),
            "invoices": [
                {
                    "invoice_number": inv.invoice_number,
                    "sender": inv.sender,
                    "amount": inv.amount,
                    "invoice_date": inv.invoice_date,
                    "due_date": inv.due_date
                }
                for inv in invoices
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email scanning failed: {str(e)}")

@intelligent_invoice_router.get("/unmatched-transactions")
async def get_unmatched_transactions() -> Dict[str, Any]:
    """
    🔍 UNZUGEORDNETE TRANSAKTIONEN
    
    Findet Bank-Transaktionen ohne zugeordnete Belege
    """
    
    try:
        manager = IntelligentInvoiceManager()
        unmatched = manager.analyze_unmatched_transactions()
        
        missing_receipts = [tx for tx in unmatched if tx.missing_receipt]
        business_relevant = [tx for tx in unmatched if tx.tax_relevance == "business"]
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "total_unmatched": len(unmatched),
            "missing_receipts": len(missing_receipts),
            "business_relevant": len(business_relevant),
            "transactions": [
                {
                    "transaction_id": tx.transaction_id,
                    "date": tx.date,
                    "amount": tx.amount,
                    "description": tx.description,
                    "missing_receipt": tx.missing_receipt,
                    "tax_relevance": tx.tax_relevance
                }
                for tx in unmatched
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unmatched transactions analysis failed: {str(e)}")

@intelligent_invoice_router.get("/outgoing-invoices")
async def analyze_outgoing_invoices() -> Dict[str, Any]:
    """
    📤 AUSGEHENDE RECHNUNGEN
    
    Analysiert WeClapp Ausgangsrechnungen vs. Bank-Eingänge
    """
    
    try:
        manager = IntelligentInvoiceManager()
        result = manager.analyze_outgoing_invoices()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "analysis": result,
            "summary": {
                "total_paid": len(result.get('paid', [])),
                "total_unpaid": len(result.get('unpaid', [])),
                "total_overdue": len(result.get('overdue', [])),
                "total_outstanding": result.get('total_outstanding', 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outgoing invoices analysis failed: {str(e)}")

@intelligent_invoice_router.get("/tax-report")
async def generate_tax_report() -> Dict[str, Any]:
    """
    📁 STEUERBERATER REPORT
    
    Generiert vollständigen Report für Steuerberater
    """
    
    try:
        manager = IntelligentInvoiceManager()
        
        # Hole alle Daten
        invoices = manager.scan_incoming_emails_for_invoices(90)
        matched_invoices = manager.match_invoices_with_bank_transactions(invoices)
        unmatched = manager.analyze_unmatched_transactions()
        
        # Generiere Report
        report_file = manager.generate_tax_filing_report(matched_invoices, unmatched)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "report_file": report_file,
            "summary": {
                "total_invoices": len(matched_invoices),
                "paid_invoices": len([inv for inv in matched_invoices if inv.payment_status == "paid"]),
                "missing_receipts": len([tx for tx in unmatched if tx.missing_receipt]),
                "business_unmatched": len([tx for tx in unmatched if tx.tax_relevance == "business"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tax report generation failed: {str(e)}")

@intelligent_invoice_router.get("/dashboard")
async def get_dashboard_data() -> Dict[str, Any]:
    """
    📊 DASHBOARD DATEN
    
    Liefert alle Daten für ein Management Dashboard
    """
    
    try:
        manager = IntelligentInvoiceManager()
        
        # Sammle alle Daten
        invoices = manager.scan_incoming_emails_for_invoices(30)
        matched_invoices = manager.match_invoices_with_bank_transactions(invoices)
        unmatched = manager.analyze_unmatched_transactions()
        outgoing = manager.analyze_outgoing_invoices()
        
        # Berechne Kennzahlen
        total_incoming_amount = sum(inv.amount for inv in matched_invoices)
        paid_amount = sum(inv.amount for inv in matched_invoices if inv.payment_status == "paid")
        unpaid_amount = sum(inv.amount for inv in matched_invoices if inv.payment_status in ["unpaid", "overdue"])
        
        missing_receipts = [tx for tx in unmatched if tx.missing_receipt]
        missing_amount = sum(abs(tx.amount) for tx in missing_receipts)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "dashboard": {
                "incoming_invoices": {
                    "total_count": len(matched_invoices),
                    "total_amount": total_incoming_amount,
                    "paid_count": len([inv for inv in matched_invoices if inv.payment_status == "paid"]),
                    "paid_amount": paid_amount,
                    "unpaid_count": len([inv for inv in matched_invoices if inv.payment_status in ["unpaid", "overdue"]]),
                    "unpaid_amount": unpaid_amount
                },
                "outgoing_invoices": {
                    "total_count": len(outgoing.get('paid', [])) + len(outgoing.get('unpaid', [])) + len(outgoing.get('overdue', [])),
                    "paid_count": len(outgoing.get('paid', [])),
                    "unpaid_count": len(outgoing.get('unpaid', [])),
                    "overdue_count": len(outgoing.get('overdue', [])),
                    "total_outstanding": outgoing.get('total_outstanding', 0)
                },
                "unmatched_transactions": {
                    "total_count": len(unmatched),
                    "missing_receipts_count": len(missing_receipts),
                    "missing_receipts_amount": missing_amount,
                    "business_relevant_count": len([tx for tx in unmatched if tx.tax_relevance == "business"])
                },
                "alerts": {
                    "overdue_invoices": len(outgoing.get('overdue', [])),
                    "missing_receipts": len(missing_receipts),
                    "urgent_action_required": len(missing_receipts) > 0 or len(outgoing.get('overdue', [])) > 0
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data generation failed: {str(e)}")

# Integration Code für production_langgraph_orchestrator.py
"""
INTEGRATION ANLEITUNG:

1. In production_langgraph_orchestrator.py hinzufügen:

```python
from railway_intelligent_invoice_api import intelligent_invoice_router

# Router registrieren
app.include_router(intelligent_invoice_router)
```

2. Neue API Endpoints verfügbar:
   - GET /api/intelligent-invoice/analyze - Vollständige Analyse
   - GET /api/intelligent-invoice/scan-emails - E-Mail Scanning
   - GET /api/intelligent-invoice/unmatched-transactions - Unzugeordnete Transaktionen
   - GET /api/intelligent-invoice/outgoing-invoices - Ausgangsrechnungen
   - GET /api/intelligent-invoice/tax-report - Steuerberater Report
   - GET /api/intelligent-invoice/dashboard - Dashboard Daten

3. Dashboard Integration:
   Nutze /api/intelligent-invoice/dashboard für Management Dashboard mit:
   - Eingangsrechnungen Übersicht
   - Ausgangsrechnungen Status
   - Fehlende Belege Alerts
   - Kritische Handlungsfelder
"""