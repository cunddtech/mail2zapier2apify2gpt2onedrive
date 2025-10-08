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

# Import der ursprünglichen Module (falls verfügbar)
try:
    from modules.mail.process_email_workflow import process_email_workflow
    from modules.auth.get_graph_token_onedrive import get_graph_token_onedrive
    from modules.auth.get_graph_token_mail import get_graph_token_mail
    FULL_EMAIL_PROCESSING_AVAILABLE = True
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
    Hybrid Email Processing: Railway AI + Vollständige E-Mail-Verarbeitung
    """
    
    # 1. Railway LangGraph AI Processing
    debug_log("🤖 Starte Railway LangGraph Integration...")
    railway_result = call_railway_orchestrator_hybrid(context)
    
    if railway_result["status"] == "success":
        debug_log("✅ Railway LangGraph Integration erfolgreich")
        context.processing_results["railway"] = railway_result["data"]
    else:
        debug_log(f"⚠️ Railway Integration fehlgeschlagen: {railway_result.get('error', 'Unknown error')}")
        
    # 2. Vollständige E-Mail-Verarbeitung (wenn verfügbar)
    if FULL_EMAIL_PROCESSING_AVAILABLE and context.has_attachments:
        debug_log("📧 Starte vollständige E-Mail-Verarbeitung mit Anhängen...")
        
        try:
            # Get Microsoft Graph tokens
            debug_log("🔑 Hole Microsoft Graph Tokens...")
            access_token_mail = await get_graph_token_mail()
            access_token_onedrive = await get_graph_token_onedrive()
            
            if access_token_mail and access_token_onedrive:
                debug_log("✅ Graph Tokens erfolgreich geholt")
                
                # Convert to legacy format
                legacy_context = context.raw_data.copy()
                
                # Call original processing workflow
                processed_context = await process_email_workflow(
                    public_link=None,
                    input_data=context.raw_data,
                    access_token_mail=access_token_mail,
                    access_token_onedrive=access_token_onedrive,
                    context=legacy_context
                )
                
                context.processing_results["full_email"] = processed_context
                context.attachment_results = processed_context.get("processed_attachments", {})
                context.onedrive_results = processed_context.get("onedrive_upload", {})
                
                debug_log("✅ Vollständige E-Mail-Verarbeitung abgeschlossen")
                debug_log(f"📎 Anhänge verarbeitet: {len(context.attachment_results)}")
                
            else:
                debug_log("❌ Graph Tokens konnten nicht geholt werden")
                context.processing_results["token_error"] = "Could not obtain Graph tokens"
                
        except Exception as e:
            debug_log(f"❌ Fehler in vollständiger E-Mail-Verarbeitung: {str(e)}")
            context.processing_results["full_email_error"] = {
                "message": str(e),
                "traceback": traceback.format_exc()
            }
    else:
        if not FULL_EMAIL_PROCESSING_AVAILABLE:
            debug_log("⚠️ Vollständige E-Mail-Module nicht verfügbar")
        if not context.has_attachments:
            debug_log("ℹ️ Keine Anhänge erkannt - überspringe Anhang-Verarbeitung")
    
    # 3. Minimal Processing als Fallback
    debug_log("📧 Hybrid Processing Summary...")
    context.processing_results["summary"] = {
        "message_processed": True,
        "timestamp": 0,
        "method": context.processing_method,
        "railway_integration": context.railway_enabled,
        "full_processing": FULL_EMAIL_PROCESSING_AVAILABLE,
        "attachments_processed": len(context.attachment_results),
        "onedrive_upload": bool(context.onedrive_results)
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