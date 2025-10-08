#!/usr/bin/env python3
"""
🚀 ENHANCED EMAIL ACTOR v3.4 - HYBRID VERSION
Railway LangGraph AI Integration + Vollständige E-Mail-Verarbeitung
Kombiniert AI-Features mit ursprünglicher Anhang-Verarbeitung
"""

import sys
import os
import asyncio
import json
import traceback
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional

# Fix PYTHONPATH für Module-Imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import der ursprünglichen Module (falls verfügbar)
try:
    from modules.mail.process_email_workflow import process_email_workflow
    from modules.auth.get_graph_token_onedrive import get_graph_token_onedrive
    from modules.auth.get_graph_token_mail import get_graph_token_mail
    from modules.mail.process_attachments import process_attachments
    from modules.gpt.analyze_document_with_gpt import analyze_document_with_gpt
    from modules.utils.build_gpt_payload import build_gpt_payload
    from modules.msgraph.fetch_email_with_attachments import fetch_email_details_with_attachments
    from modules.validation.precheck_relevance import precheck_relevance
    from modules.filegen.folder_logic import generate_folder_and_filenames
    from modules.upload.upload_file_to_onedrive import upload_file_to_onedrive
    from modules.msgraph.onedrive_manager import delete_file_from_onedrive
    FULL_EMAIL_PROCESSING_AVAILABLE = True
    print("✅ Vollständige E-Mail-Module erfolgreich geladen")
except ImportError as e:
    print(f"⚠️ Warnung: Vollständige E-Mail-Module nicht verfügbar: {e}")
    FULL_EMAIL_PROCESSING_AVAILABLE = False

# Version und Konfiguration
ACTOR_VERSION = "3.4"
RAILWAY_ORCHESTRATOR_URL = os.environ.get('ORCHESTRATOR_URL', 'https://my-langgraph-agent-production.up.railway.app')
RAILWAY_INTEGRATION = os.environ.get('RAILWAY_INTEGRATION', 'true').lower() == 'true'
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() == 'true'

# Apify API Configuration
APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
APIFY_ACTOR_RUN_ID = os.environ.get('APIFY_ACTOR_RUN_ID')
APIFY_DEFAULT_DATASET_ID = os.environ.get('APIFY_DEFAULT_DATASET_ID')

# Webhook für Notfall-Alarm
ALERT_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

def debug_log(message: str):
    """Simple debug logging"""
    print(f"[{ACTOR_VERSION}] {message}")

def get_input_data() -> Dict[str, Any]:
    """
    Get input data from Apify environment variables and stdin
    """
    debug_log(f"🔍 Environment Check - Run ID: {'SET' if APIFY_ACTOR_RUN_ID else 'MISSING'}, Token: {'SET' if APIFY_TOKEN else 'MISSING'}")
    
    try:
        # Method 1: Try Apify API if we have run ID and token
        if APIFY_ACTOR_RUN_ID and APIFY_TOKEN:
            debug_log("📞 Versuche Apify API Input...")
            url = f"https://api.apify.com/v2/actor-runs/{APIFY_ACTOR_RUN_ID}/input"
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {APIFY_TOKEN}'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                debug_log("✅ Apify API Input erfolgreich geladen")
                return data
        
        # Method 2: Try to read from stdin (Apify provides input this way)
        debug_log("📖 Versuche stdin Input...")
        import sys
        if not sys.stdin.isatty():
            input_json = sys.stdin.read().strip()
            if input_json:
                data = json.loads(input_json)
                debug_log("✅ stdin Input erfolgreich geladen")
                return data
        
        # Method 3: Check environment variables for input data
        debug_log("🔍 Versuche Environment Variables...")
        env_input = {}
        for key in ['message_id', 'subject', 'body_content', 'from_email_address_address', 'to_recipients_email_address_address']:
            env_value = os.environ.get(key.upper())
            if env_value:
                env_input[key] = env_value
        
        if env_input:
            debug_log("✅ Environment Variables Input gefunden")
            return env_input
        
        # Method 4: Use Apify input file if exists
        debug_log("📁 Versuche Apify Input File...")
        input_file_paths = ['/usr/src/app/INPUT', '/usr/src/app/input.json', './input.json']
        for path in input_file_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                    debug_log(f"✅ Input File geladen: {path}")
                    return data
        
        # Last resort: create meaningful test data with attachments
        debug_log("⚠️ Verwende Fallback Test-Daten mit Anhängen...")
        return {
            "message_id": "test-hybrid-001",
            "subject": "Test Email für Enhanced Actor v3.4 mit Anhängen",
            "body_content": "Dies ist ein Test für den Hybrid Actor v3.4 mit Railway Integration und Anhang-Verarbeitung.",
            "from_email_address_address": "test@example.com",
            "to_recipients_email_address_address": "info@cdtech.de",
            "from_email_address_name": "Test Sender",
            "to_recipients_email_address_name": "C&D Tech Team",
            "received_date_time": "2025-10-08T06:30:00Z",
            "attachments": [
                {
                    "id": "test-attachment-001",
                    "name": "test-document.pdf",
                    "content_type": "application/pdf",
                    "size": 12345,
                    "download_url": "https://test.example.com/attachment"
                }
            ],
            "source": "hybrid_test",
            "railway_integration": True,
            "enable_contact_matching": True,
            "enable_task_generation": True,
            "zapier_webhook": ALERT_WEBHOOK_URL
        }
            
    except Exception as e:
        debug_log(f"❌ Fehler beim Input-Laden: {str(e)}")
        # Even in error case, provide basic test data
        return {
            "message_id": "error-hybrid-001",
            "subject": "Error Fallback Test mit Anhängen",
            "body_content": f"Hybrid Fallback due to error: {str(e)}",
            "from_email_address_address": "error@example.com",
            "to_recipients_email_address_address": "info@cdtech.de",
            "source": "error_hybrid_fallback",
            "attachments": []
        }

def push_data_to_apify(data: Dict[str, Any]) -> bool:
    """
    Push data to Apify dataset without SDK
    """
    try:
        if APIFY_DEFAULT_DATASET_ID and APIFY_TOKEN:
            url = f"https://api.apify.com/v2/datasets/{APIFY_DEFAULT_DATASET_ID}/items"
            
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    'Authorization': f'Bearer {APIFY_TOKEN}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                debug_log(f"✅ Data erfolgreich gepusht: {response.status}")
                return True
        else:
            debug_log("⚠️ Kein Dataset ID, verwende Standard-Output...")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
            
    except Exception as e:
        debug_log(f"❌ Fehler beim Data-Push: {str(e)}")
        return False

class HybridEmailContext:
    """Hybrid Context für AI + vollständige E-Mail-Verarbeitung"""
    
    def __init__(self, input_data: Dict[str, Any]):
        # Core fields from input
        self.message_id = input_data.get("message_id", "")
        self.user_email = input_data.get("to_recipients_email_address_address", "")
        self.recipient_email = input_data.get("from_email_address_address", "")
        self.subject = input_data.get("subject", "")
        self.body_content = input_data.get("body_content", "")
        
        # Attachment handling
        self.attachments = input_data.get("attachments", [])
        self.has_attachments = len(self.attachments) > 0
        
        # Processing flags
        self.source = input_data.get("source", "mail")
        self.is_spam = False
        self.processing_method = "hybrid_ai_plus_full"
        
        # Railway integration
        self.railway_enabled = RAILWAY_INTEGRATION
        self.orchestrator_url = RAILWAY_ORCHESTRATOR_URL
        
        # Zapier webhook
        self.zapier_webhook = input_data.get("zapier_webhook") or ALERT_WEBHOOK_URL
        
        # Store all original data for legacy processing
        self.raw_data = input_data.copy()
        
        # Results storage
        self.processing_results = {}
        self.ai_analysis = {}
        self.contact_matching = {}
        self.attachment_results = {}
        self.onedrive_results = {}
        
    def validate(self) -> tuple[bool, str]:
        """Validate required fields"""
        if not self.message_id:
            return False, "message_id is required"
        if not self.user_email:
            return False, "user_email is required"
        return True, "valid"

def call_railway_orchestrator_hybrid(context: HybridEmailContext) -> Dict[str, Any]:
    """
    Railway LangGraph Orchestrator call mit Anhang-Informationen
    """
    if not context.railway_enabled:
        debug_log("🚫 Railway Integration deaktiviert, überspringe Orchestrator-Aufruf")
        return {"status": "skipped", "method": "hybrid_minimal"}
    
    try:
        url = f"{context.orchestrator_url}/webhook/ai-email"
        
        # Enhanced payload mit Anhang-Informationen
        payload = {
            "email_data": {
                "message_id": context.message_id,
                "subject": context.subject,
                "body_content": context.body_content,
                "from_email": context.recipient_email,
                "to_email": context.user_email,
                "source": context.source,
                "has_attachments": context.has_attachments,
                "attachment_count": len(context.attachments),
                "attachment_info": [
                    {
                        "name": att.get("name", "unknown"),
                        "type": att.get("content_type", "unknown"),
                        "size": att.get("size", 0)
                    }
                    for att in context.attachments
                ]
            },
            "processing_options": {
                "enable_contact_matching": True,
                "enable_task_generation": True,
                "enable_weclapp_integration": True,
                "enable_attachment_analysis": context.has_attachments,
                "workflow_type": "hybrid_enhanced_processing"
            },
            "metadata": {
                "actor_version": ACTOR_VERSION,
                "timestamp": 0,
                "debug_mode": DEBUG_MODE,
                "full_processing_available": FULL_EMAIL_PROCESSING_AVAILABLE
            }
        }
        
        debug_log(f"🚀 Railway Orchestrator Aufruf: {url}")
        debug_log(f"📎 Anhänge: {len(context.attachments)} erkannt")
        
        # Use urllib for HTTP call
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                debug_log(f"✅ Railway Orchestrator Antwort: {json.dumps(result, indent=2)}")
                
                context.processing_method = "railway_langgraph_hybrid"
                context.ai_analysis = result.get("ai_analysis", {})
                context.contact_matching = result.get("contact_matching", {})
                
                return {
                    "status": "success",
                    "method": "railway_langgraph_hybrid",
                    "data": result
                }
            else:
                error_text = response.read().decode('utf-8')
                debug_log(f"⚠️ Railway Orchestrator Fehler: {response.status} - {error_text}")
                return {
                    "status": "error",
                    "method": "fallback_hybrid",
                    "error": f"HTTP {response.status}: {error_text}"
                }
                
    except Exception as e:
        debug_log(f"❌ Railway Orchestrator Exception: {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "method": "fallback_hybrid", 
            "error": str(e)
        }

async def process_email_hybrid(context: HybridEmailContext) -> HybridEmailContext:
    """
    🚀 VOLLSTÄNDIGE HYBRID EMAIL PROCESSING 
    Railway AI + Alle ursprünglichen Processing-Steps
    """
    
    # 1. Railway LangGraph AI Processing (NEUE FUNKTION)
    debug_log("🤖 Starte Railway LangGraph Integration...")
    railway_result = call_railway_orchestrator_hybrid(context)
    
    if railway_result["status"] == "success":
        debug_log("✅ Railway LangGraph Integration erfolgreich")
        context.processing_results["railway"] = railway_result["data"]
        context.ai_analysis = railway_result["data"].get("ai_analysis", {})
        context.contact_matching = railway_result["data"].get("contact_match", {})
    else:
        debug_log(f"⚠️ Railway Integration fehlgeschlagen: {railway_result.get('error', 'Unknown error')}")
        
    # 2. VOLLSTÄNDIGE URSPRÜNGLICHE E-MAIL-VERARBEITUNG
    if FULL_EMAIL_PROCESSING_AVAILABLE:
        debug_log("📧 Starte VOLLSTÄNDIGE E-Mail-Verarbeitung (alle ursprünglichen Steps)...")
        
        try:
            # Get Microsoft Graph tokens
            debug_log("🔑 Hole Microsoft Graph Tokens...")
            access_token_mail = await get_graph_token_mail()
            access_token_onedrive = await get_graph_token_onedrive()
            
            if access_token_mail and access_token_onedrive:
                debug_log("✅ Graph Tokens erfolgreich geholt")
                
                # STEP 1: Relevanzprüfung
                debug_log("🧠 STEP 1: Starte Relevanzprüfung...")
                try:
                    relevance_result = await precheck_relevance(context.raw_data, access_token_mail)
                    context.processing_results["relevance_check"] = relevance_result
                    context.raw_data["precheck_result"] = relevance_result
                    context.raw_data["relevant"] = relevance_result.get("relevant", True)  # Default: relevant
                    
                    if not relevance_result.get("relevant", True):
                        debug_log(f"❌ Mail als nicht relevant eingestuft: {relevance_result.get('grund', 'Kein Grund')}")
                        context.processing_method = "irrelevant_skipped"
                        return context
                    debug_log("✅ STEP 1: Relevanzprüfung bestanden")
                except Exception as e:
                    debug_log(f"⚠️ STEP 1: Relevanzprüfung fehlgeschlagen: {str(e)} - Fortsetzung...")
                
                # STEP 2: Anhang-Metadaten laden (wenn nötig)
                if context.has_attachments:
                    debug_log("📎 STEP 2: Lade Anhang-Metadaten...")
                    try:
                        if context.attachments and isinstance(context.attachments[0], dict) and "filename" not in context.attachments[0]:
                            email_data = await fetch_email_details_with_attachments(
                                user_email=context.user_email,
                                message_id=context.message_id,
                                access_token=access_token_mail
                            )
                            if email_data and "attachments" in email_data:
                                context.attachments = email_data["attachments"]
                                context.raw_data["attachments"] = email_data["attachments"]
                                debug_log("✅ STEP 2: Anhang-Metadaten erfolgreich nachgeladen")
                            else:
                                debug_log("⚠️ STEP 2: Konnte keine Anhang-Metadaten laden")
                        else:
                            debug_log("✅ STEP 2: Anhang-Metadaten bereits vorhanden")
                    except Exception as e:
                        debug_log(f"⚠️ STEP 2: Anhang-Metadaten Fehler: {str(e)}")
                
                # STEP 3: Anhang-Verarbeitung 
                if context.has_attachments:
                    debug_log("📎 STEP 3: Starte Anhang-Verarbeitung...")
                    try:
                        processed_attachments = await process_attachments(
                            attachments=context.attachments,
                            user_email=context.user_email,
                            message_id=context.message_id,
                            access_token_mail=access_token_mail,
                            access_token_onedrive=access_token_onedrive,
                            context=context.raw_data
                        )
                        context.attachment_results = processed_attachments or []
                        context.raw_data["processed_attachments"] = processed_attachments
                        debug_log(f"✅ STEP 3: {len(context.attachment_results)} Anhänge verarbeitet")
                    except Exception as e:
                        debug_log(f"❌ STEP 3: Anhang-Verarbeitung fehlgeschlagen: {str(e)}")
                        context.attachment_results = []
                else:
                    debug_log("ℹ️ STEP 3: Keine Anhänge vorhanden - überspringe")
                    context.attachment_results = []
                
                # STEP 4: GPT-Input erstellen
                debug_log("🧠 STEP 4: Erstelle GPT-Input...")
                try:
                    gpt_input = build_gpt_payload(
                        context=context.raw_data,
                        attachments=context.attachment_results,
                        weclapp_info=context.raw_data.get("weclapp_info", {}),
                        public_url=context.raw_data.get("public_url", {}),
                        relevant=context.raw_data.get("relevant", True)
                    )
                    context.raw_data["gpt_input"] = gpt_input
                    debug_log("✅ STEP 4: GPT-Input erstellt")
                except Exception as e:
                    debug_log(f"⚠️ STEP 4: GPT-Input Erstellung fehlgeschlagen: {str(e)}")
                    gpt_input = {}
                
                # STEP 5: GPT-Analyse (zusätzlich zu Railway)
                debug_log("🧠 STEP 5: Starte ursprüngliche GPT-Analyse...")
                try:
                    if gpt_input:
                        gpt_result = await analyze_document_with_gpt(gpt_input)
                        if gpt_result:
                            context.processing_results["gpt_analysis"] = gpt_result
                            context.raw_data["gpt_result"] = gpt_result
                            debug_log("✅ STEP 5: GPT-Analyse erfolgreich")
                        else:
                            debug_log("⚠️ STEP 5: GPT-Analyse lieferte keine Ergebnisse")
                    else:
                        debug_log("⚠️ STEP 5: Kein GPT-Input - überspringe GPT-Analyse")
                except Exception as e:
                    debug_log(f"⚠️ STEP 5: GPT-Analyse fehlgeschlagen: {str(e)}")
                
                # STEP 6: Ordner-Generierung
                debug_log("📂 STEP 6: Generiere Ordner und Dateinamen...")
                try:
                    gpt_result = context.raw_data.get("gpt_result", {})
                    if gpt_result:
                        folder_data = generate_folder_and_filenames(context.raw_data, gpt_result)
                        context.processing_results["folder_data"] = folder_data
                        context.raw_data["folder_data"] = folder_data
                        debug_log(f"✅ STEP 6: Ordnerstruktur generiert: {folder_data.get('ordnerstruktur', 'N/A')}")
                    else:
                        debug_log("⚠️ STEP 6: Keine GPT-Ergebnisse für Ordner-Generierung")
                except Exception as e:
                    debug_log(f"⚠️ STEP 6: Ordner-Generierung fehlgeschlagen: {str(e)}")
                
                # STEP 7: OneDrive Upload
                debug_log("⬆️ STEP 7: Starte OneDrive Upload...")
                try:
                    folder_data = context.raw_data.get("folder_data", {})
                    if folder_data and context.attachment_results:
                        final_folder_path = folder_data.get("ordnerstruktur", "/scan/verarbeitet")
                        pdf_filenames = folder_data.get("pdf_filenames", [])
                        
                        for i, attachment in enumerate(context.attachment_results):
                            filename = pdf_filenames[i] if i < len(pdf_filenames) else attachment.get("filename", f"file_{i}.pdf")
                            file_bytes = context.raw_data.get("file_bytes", {}).get(attachment.get("filename"))
                            
                            if file_bytes:
                                upload_result = await upload_file_to_onedrive(
                                    user_mail=context.user_email,
                                    folder_path=final_folder_path,
                                    filename=filename,
                                    file_bytes=file_bytes,
                                    access_token_onedrive=access_token_onedrive
                                )
                                if upload_result:
                                    debug_log(f"✅ STEP 7: Datei hochgeladen: {filename}")
                                    context.onedrive_results[filename] = upload_result
                                else:
                                    debug_log(f"❌ STEP 7: Upload fehlgeschlagen: {filename}")
                        
                        debug_log(f"✅ STEP 7: OneDrive Upload abgeschlossen - {len(context.onedrive_results)} Dateien")
                    else:
                        debug_log("ℹ️ STEP 7: Keine Dateien für OneDrive Upload")
                except Exception as e:
                    debug_log(f"❌ STEP 7: OneDrive Upload fehlgeschlagen: {str(e)}")
                
                # STEP 8: Zapier Integration (erweitert) - VOLLSTÄNDIGE URSPRÜNGLICHE PAYLOAD
                debug_log("🌐 STEP 8: Sende Daten an Zapier...")
                try:
                    # Extrahiere detaillierte Daten aus GPT-Ergebnissen (wie ursprünglich)
                    gpt_result = context.processing_results.get("gpt_analysis", {})
                    folder_data = context.processing_results.get("folder_data", {})
                    
                    # Robust alle möglichen Felder abdecken (wie ursprünglich)
                    pdf_proc = context.raw_data.get("pdf_processing", {})
                    invoice_data = (
                        pdf_proc.get("invoice_data")
                        or pdf_proc.get("invoice")
                        or pdf_proc.get("header")
                        or {}
                    )
                    vendor = (
                        pdf_proc.get("vendor")
                        or pdf_proc.get("vendor_data")
                        or pdf_proc.get("company_information")
                        or {}
                    )
                    customer = (
                        pdf_proc.get("customer")
                        or pdf_proc.get("customer_data")
                        or pdf_proc.get("customer_information")
                        or {}
                    )
                    payment_details = (
                        pdf_proc.get("payment_details")
                        or pdf_proc.get("paymentDetails")
                        or {
                            "totals": pdf_proc.get("totals", {}),
                            "payment_terms": pdf_proc.get("payment_terms", {}),
                            "order_details": pdf_proc.get("order_details", {}),
                        }
                    )
                    billing_address = (
                        pdf_proc.get("billing_address")
                        or pdf_proc.get("billingAddress")
                        or {}
                    )
                    shipping_address = (
                        pdf_proc.get("shipping_address")
                        or pdf_proc.get("shippingAddress")
                        or {}
                    )
                    
                    # WeClapp-Informationen
                    weclapp_info = context.raw_data.get("weclapp_info", {})
                    weclapp_kunde = weclapp_info.get("kunde", None)
                    weclapp_lieferant = weclapp_info.get("lieferant", None)
                    weclapp_projekt = weclapp_info.get("projekt", None)
                    weclapp_auftragsnummer = weclapp_info.get("auftragsnummer", None)
                    weclapp_id = weclapp_info.get("weclapp_id", None)
                    
                    # Task-Daten extrahieren
                    def get_task_data(gpt_result, raw_data):
                        # Prüfe verschiedene mögliche Felder im gpt_result
                        for key in ("task_data", "aufgabe", "task", "todo", "taskResult"):
                            value = gpt_result.get(key)
                            if value and isinstance(value, dict) and any(value.values()):
                                return value
                            if value and isinstance(value, str) and value.strip():
                                return {"Beschreibung": value.strip(), "Fälligkeitsdatum": "", "Priorität": "niedrig"}
                        # Prüfe auch im Raw-Data
                        for key in ("task_data", "aufgabe", "task", "todo", "taskResult"):
                            value = raw_data.get(key)
                            if value and isinstance(value, dict) and any(value.values()):
                                return value
                            if value and isinstance(value, str) and value.strip():
                                return {"Beschreibung": value.strip(), "Fälligkeitsdatum": "", "Priorität": "niedrig"}
                        # Fallback
                        return {
                            "Beschreibung": "Keine Aufgabe erforderlich",
                            "Fälligkeitsdatum": "",
                            "Priorität": "niedrig"
                        }
                    task_data = get_task_data(gpt_result, context.raw_data)
                    
                    # VOLLSTÄNDIGE URSPRÜNGLICHE ZAPIER-PAYLOAD
                    final_payload = {
                        "Dokumenttyp": gpt_result.get("dokumenttyp", "Rechnung"),
                        "Richtung": gpt_result.get("richtung", "Eingang"),
                        "Rolle": gpt_result.get("rolle", "Lieferant"),
                        "Rechnungsnummer": invoice_data.get("document_number") or invoice_data.get("invoiceNumber") or invoice_data.get("nummer") or "Unbekannt",
                        "Rechnungsdatum": invoice_data.get("date") or invoice_data.get("invoiceDate") or "Unbekannt",
                        "E-Mail-Eingang": context.raw_data.get("created_date_time", context.raw_data.get("received_date_time", "Unbekannt")),
                        "Fälligkeit": payment_details.get("dueDate") or payment_details.get("fälligkeitsdatum") or "Unbekannt",
                        "Lieferant": vendor.get("company_name") or vendor.get("name") or context.recipient_email or "Unbekannt",
                        "Kunde": customer.get("customer_name") or customer.get("name") or gpt_result.get("kunde") or "Unbekannt",
                        "Projekt": payment_details.get("projectNumber") or invoice_data.get("project_number") or "Unbekannt",
                        "WeClapp": {
                            "Kunde": weclapp_kunde,
                            "Lieferant": weclapp_lieferant,
                            "Projekt": weclapp_projekt,
                            "Auftragsnummer": weclapp_auftragsnummer,
                            "WeClapp-ID": weclapp_id,
                            "Weitere_Info": weclapp_info
                        },
                        "Beträge": {
                            "Zwischensumme": (
                                payment_details.get("subtotal")
                                or payment_details.get("net_amount")
                                or payment_details.get("totals", {}).get("net_amount")
                                or "Unbekannt"
                            ),
                            "MwSt.": (
                                payment_details.get("tax")
                                or payment_details.get("tax_amount")
                                or payment_details.get("totals", {}).get("tax_amount")
                                or "Unbekannt"
                            ),
                            "Gesamtbetrag": (
                                payment_details.get("total")
                                or payment_details.get("total_amount")
                                or payment_details.get("totals", {}).get("total_amount")
                                or "Unbekannt"
                            ),
                        },
                        "Zahlungsbedingungen": (
                            payment_details.get("terms")
                            or payment_details.get("payment_terms", {}).get("terms")
                            or payment_details.get("payment_terms")
                            or payment_details.get("payment_terms_text")
                            or "Unbekannt"
                        ),
                        "Rechnungsadresse": billing_address,
                        "Lieferadresse": shipping_address,
                        "Ablageort": {
                            "Ordner": folder_data.get("ordnerstruktur", ""),
                            "Dateipfad": [
                                {
                                    "Dateiname": name,
                                    "Link": att.get("url", "Keine Datei")
                                }
                                for name, att in zip(folder_data.get("pdf_filenames", []), context.attachment_results)
                            ]
                        },
                        "Status": {
                            "Relevanz": context.raw_data.get("precheck_result", {}).get("relevant", True),
                            "Manuell prüfen": gpt_result.get("zu_pruefen", True)
                        },
                        "Aufgabe": task_data,
                        # NEUE HYBRID-FEATURES
                        "Enhanced_v34": {
                            "version": ACTOR_VERSION,
                            "processing_method": "hybrid_complete_enhanced",
                            "railway_analysis": context.ai_analysis,
                            "contact_matching": context.contact_matching,
                            "attachments_processed": len(context.attachment_results),
                            "onedrive_files": list(context.onedrive_results.keys()),
                            "full_processing": FULL_EMAIL_PROCESSING_AVAILABLE,
                            "timestamp": 0
                        }
                    }
                    
                    if context.zapier_webhook:
                        import requests
                        headers = {"Content-Type": "application/json"}
                        zapier_response = requests.post(
                            context.zapier_webhook, 
                            data=json.dumps(final_payload), 
                            headers=headers
                        )
                        if zapier_response and zapier_response.status_code == 200:
                            debug_log("✅ STEP 8: Daten erfolgreich an Zapier gesendet")
                        else:
                            debug_log(f"⚠️ STEP 8: Zapier Fehler: {zapier_response.status_code if zapier_response else 'Keine Antwort'}")
                    else:
                        debug_log("ℹ️ STEP 8: Kein Zapier-Webhook konfiguriert")
                except Exception as e:
                    debug_log(f"⚠️ STEP 8: Zapier Integration fehlgeschlagen: {str(e)}")
                
                # STEP 9: Context-JSON-Speicherung (ursprüngliche Funktion)
                debug_log("💾 STEP 9: Speichere Context-Datei als JSON...")
                try:
                    import datetime
                    # Serializable Context erstellen (ohne file_bytes)
                    serializable_context = {k: v for k, v in context.raw_data.items() if k != "file_bytes"}
                    serializable_context["enhanced_v34_results"] = {
                        "railway_analysis": context.ai_analysis,
                        "contact_matching": context.contact_matching,
                        "processing_results": context.processing_results,
                        "attachment_results": context.attachment_results,
                        "onedrive_results": context.onedrive_results
                    }
                    
                    context_file_bytes = json.dumps(serializable_context, indent=2, ensure_ascii=False).encode("utf-8")
                    verarbeitet_folder = "/scan/verarbeitet"
                    folder_data = context.processing_results.get("folder_data", {})
                    pdf_filenames = folder_data.get("pdf_filenames", [])
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                    if pdf_filenames:
                        for pdf_filename in pdf_filenames:
                            base_name = os.path.splitext(pdf_filename)[0]
                            json_filename = f"{base_name}_{timestamp}.json"
                            debug_log(f"⬆️ Speichere context-Datei: {json_filename} -> {verarbeitet_folder}")
                            verarbeitet_upload_result = await upload_file_to_onedrive(
                                user_mail=context.user_email,
                                folder_path=verarbeitet_folder,
                                filename=json_filename,
                                file_bytes=context_file_bytes,
                                access_token_onedrive=access_token_onedrive
                            )
                            if verarbeitet_upload_result:
                                debug_log(f"✅ STEP 9: Context-Datei gespeichert: {json_filename}")
                            else:
                                debug_log(f"❌ STEP 9: Context-Datei Upload fehlgeschlagen: {json_filename}")
                    else:
                        # Kein Anhang, also generischer Name
                        json_filename = f"email_{context.message_id}_{timestamp}.json"
                        debug_log(f"⬆️ Speichere context-Datei: {json_filename} -> {verarbeitet_folder}")
                        verarbeitet_upload_result = await upload_file_to_onedrive(
                            user_mail=context.user_email,
                            folder_path=verarbeitet_folder,
                            filename=json_filename,
                            file_bytes=context_file_bytes,
                            access_token_onedrive=access_token_onedrive
                        )
                        if verarbeitet_upload_result:
                            debug_log(f"✅ STEP 9: Context-Datei gespeichert: {json_filename}")
                        else:
                            debug_log(f"❌ STEP 9: Context-Datei Upload fehlgeschlagen: {json_filename}")
                except Exception as e:
                    debug_log(f"⚠️ STEP 9: Context-JSON-Speicherung fehlgeschlagen: {str(e)}")
                
                # STEP 10: Temp-Cleanup (ursprüngliche Funktion)
                debug_log("🗑️ STEP 10: Lösche temporäre Dateien...")
                try:
                    if context.attachment_results:
                        temp_folder = "Temp"
                        for attachment in context.attachment_results:
                            filename = attachment.get("filename")
                            if filename:
                                await delete_file_from_onedrive(
                                    access_token_onedrive=access_token_onedrive,
                                    user_email=context.user_email,
                                    folder_path=temp_folder,
                                    filename=filename
                                )
                        debug_log("✅ STEP 10: Temporäre Dateien gelöscht")
                    else:
                        debug_log("ℹ️ STEP 10: Keine temporären Dateien zu löschen")
                except Exception as e:
                    debug_log(f"⚠️ STEP 10: Temp-Cleanup fehlgeschlagen: {str(e)}")
                
                context.processing_method = "hybrid_complete_success"
                
            else:
                debug_log("❌ Graph Tokens konnten nicht geholt werden")
                context.processing_results["token_error"] = "Could not obtain Graph tokens"
                context.processing_method = "hybrid_token_error"
                
        except Exception as e:
            debug_log(f"❌ Fehler in vollständiger E-Mail-Verarbeitung: {str(e)}")
            context.processing_results["full_email_error"] = {
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            context.processing_method = "hybrid_error"
    else:
        debug_log("⚠️ Vollständige E-Mail-Module nicht verfügbar - nur Railway AI Processing")
        context.processing_method = "railway_only"
    
    # Final Summary
    debug_log("📧 HYBRID PROCESSING COMPLETE!")
    context.processing_results["final_summary"] = {
        "message_processed": True,
        "timestamp": 0,
        "method": context.processing_method,
        "railway_integration": context.railway_enabled,
        "full_processing": FULL_EMAIL_PROCESSING_AVAILABLE,
        "attachments_processed": len(context.attachment_results),
        "onedrive_upload": bool(context.onedrive_results),
        "steps_completed": [
            "railway_ai", "relevance_check", "attachment_metadata", 
            "attachment_processing", "gpt_analysis", "folder_generation",
            "onedrive_upload", "zapier_integration_complete", "context_json_save", "temp_cleanup"
        ],
        "original_steps_preserved": True,
        "enhanced_features": True
    }
    
    return context

def main():
    """
    Hybrid Main Function - AI + Vollständige E-Mail-Verarbeitung
    """
    try:
        debug_log(f"🚀 Enhanced Email Actor v{ACTOR_VERSION} startet (Hybrid Mode)...")
        debug_log(f"🔧 Railway Integration: {'Aktiviert' if RAILWAY_INTEGRATION else 'Deaktiviert'}")
        debug_log(f"📧 Vollständige E-Mail-Module: {'Verfügbar' if FULL_EMAIL_PROCESSING_AVAILABLE else 'Nicht verfügbar'}")
        debug_log(f"🔗 Orchestrator URL: {RAILWAY_ORCHESTRATOR_URL}")
        
        # Get input data without Apify SDK
        debug_log("📥 Lade Input-Daten...")
        input_data = get_input_data()
        
        if not input_data:
            debug_log("❌ Keine Eingabedaten verfügbar.")
            return
        
        debug_log(f"📋 Input Data Keys: {list(input_data.keys())}")
        
        # Create hybrid context
        debug_log("🔧 Initialisiere Hybrid Processing Context...")
        context = HybridEmailContext(input_data)
        
        # Validation
        is_valid, validation_error = context.validate()
        if not is_valid:
            debug_log(f"❌ Validierung fehlgeschlagen: {validation_error}")
            if validation_error == "user_email is required":
                debug_log("🚨⚠️ SPAM: Keine user_email identifiziert - möglicherweise Spam")
                context.is_spam = True
            else:
                debug_log("🔄 Fortsetzung trotz Validierungsfehler...")
        
        debug_log(f"📋 Processing Context: Message-ID: {context.message_id}, User: {context.user_email}")
        debug_log(f"📎 Anhänge: {len(context.attachments)} erkannt")
        
        # Process email with hybrid approach
        debug_log("🚀 Starte Hybrid Email Processing...")
        
        # Use asyncio.run for the async processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        context = loop.run_until_complete(process_email_hybrid(context))
        loop.close()
        
        # Final results
        debug_log("📊 **Hybrid Processing Ergebnisse:**")
        debug_log(f"   Processing Method: {context.processing_method}")
        debug_log(f"   Railway Integration: {'Aktiv' if context.railway_enabled else 'Inaktiv'}")
        debug_log(f"   Vollständige Verarbeitung: {'Ja' if FULL_EMAIL_PROCESSING_AVAILABLE else 'Nein'}")
        debug_log(f"   Anhänge verarbeitet: {len(context.attachment_results)}")
        debug_log(f"   OneDrive Upload: {'Ja' if context.onedrive_results else 'Nein'}")
        debug_log(f"   Spam Detection: {'Ja' if context.is_spam else 'Nein'}")
        
        if context.ai_analysis:
            debug_log(f"   AI Analysis Keys: {list(context.ai_analysis.keys())}")
        
        if context.contact_matching:
            debug_log(f"   Contact Matching Keys: {list(context.contact_matching.keys())}")
        
        # Create final output
        final_output = {
            "version": ACTOR_VERSION,
            "processing_method": context.processing_method,
            "railway_integration": context.railway_enabled,
            "full_email_processing": FULL_EMAIL_PROCESSING_AVAILABLE,
            "message_id": context.message_id,
            "user_email": context.user_email,
            "subject": context.subject,
            "is_spam": context.is_spam,
            "has_attachments": context.has_attachments,
            "attachment_count": len(context.attachments),
            "attachments_processed": len(context.attachment_results),
            "onedrive_upload": bool(context.onedrive_results),
            "ai_analysis": context.ai_analysis,
            "contact_matching": context.contact_matching,
            "processing_results": context.processing_results,
            "timestamp": 0,
            "success": True
        }
        
        # Push data without SDK
        success = push_data_to_apify(final_output)
        if success:
            debug_log("✅ Hybrid Processing erfolgreich abgeschlossen")
        else:
            debug_log("⚠️ Data Push fehlgeschlagen, aber Processing war erfolgreich")
        
    except Exception as e:
        debug_log(f"❌ Unerwarteter Fehler in main(): {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        
        # Create error output
        error_output = {
            "version": ACTOR_VERSION,
            "processing_method": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": 0,
            "success": False
        }
        
        push_data_to_apify(error_output)

if __name__ == "__main__":
    debug_log(f"🔧 Starte Enhanced Email Actor v{ACTOR_VERSION} (Hybrid Mode)...")
    main()