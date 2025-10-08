#!/usr/bin/env python3
"""
🚀 ENHANCED EMAIL ACTOR v3.3 - ABSOLUTE MINIMAL
ZERO APIFY SDK - Nur HTTP API Calls
Umgeht alle Pydantic-Konflikte komplett
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

# Version und Konfiguration
ACTOR_VERSION = "3.3"
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
    Get input data from Apify API without SDK
    """
    try:
        if APIFY_ACTOR_RUN_ID and APIFY_TOKEN:
            # Get input from Apify API
            url = f"https://api.apify.com/v2/actor-runs/{APIFY_ACTOR_RUN_ID}/input"
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {APIFY_TOKEN}'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        else:
            # Fallback: Try to read from stdin or environment
            debug_log("⚠️ Kein APIFY_ACTOR_RUN_ID gefunden, versuche Fallback...")
            
            # Try reading from stdin (Apify sometimes provides input this way)
            import sys
            if not sys.stdin.isatty():
                input_json = sys.stdin.read().strip()
                if input_json:
                    return json.loads(input_json)
            
            # Last resort: create test data
            return {
                "message_id": "test-minimal-001",
                "subject": "Test Email für Minimal Actor",
                "body_content": "Test content for minimal processing",
                "from_email_address_address": "test@example.com",
                "to_recipients_email_address_address": "info@cdtech.de",
                "source": "minimal_test"
            }
            
    except Exception as e:
        debug_log(f"❌ Fehler beim Input-Laden: {str(e)}")
        return {}

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

class MinimalEmailContext:
    """Ultra-minimale Context-Klasse"""
    
    def __init__(self, input_data: Dict[str, Any]):
        # Core fields from input
        self.message_id = input_data.get("message_id", "")
        self.user_email = input_data.get("to_recipients_email_address_address", "")
        self.recipient_email = input_data.get("from_email_address_address", "")
        self.subject = input_data.get("subject", "")
        self.body_content = input_data.get("body_content", "")
        
        # Processing flags
        self.source = input_data.get("source", "mail")
        self.is_spam = False
        self.processing_method = "absolute_minimal"
        
        # Railway integration
        self.railway_enabled = RAILWAY_INTEGRATION
        self.orchestrator_url = RAILWAY_ORCHESTRATOR_URL
        
        # Zapier webhook
        self.zapier_webhook = input_data.get("zapier_webhook") or ALERT_WEBHOOK_URL
        
        # Store all original data
        self.raw_data = input_data.copy()
        
        # Results storage
        self.processing_results = {}
        self.ai_analysis = {}
        self.contact_matching = {}
        
    def validate(self) -> tuple[bool, str]:
        """Validate required fields"""
        if not self.message_id:
            return False, "message_id is required"
        if not self.user_email:
            return False, "user_email is required"
        return True, "valid"

def call_railway_orchestrator_minimal(context: MinimalEmailContext) -> Dict[str, Any]:
    """
    Minimal Railway LangGraph Orchestrator call using only urllib
    """
    if not context.railway_enabled:
        debug_log("🚫 Railway Integration deaktiviert, überspringe Orchestrator-Aufruf")
        return {"status": "skipped", "method": "absolute_minimal"}
    
    try:
        url = f"{context.orchestrator_url}/webhook/ai-email"
        
        payload = {
            "email_data": {
                "message_id": context.message_id,
                "subject": context.subject,
                "body_content": context.body_content,
                "from_email": context.recipient_email,
                "to_email": context.user_email,
                "source": context.source
            },
            "processing_options": {
                "enable_contact_matching": True,
                "enable_task_generation": True,
                "enable_weclapp_integration": True,
                "workflow_type": "enhanced_email_processing"
            },
            "metadata": {
                "actor_version": ACTOR_VERSION,
                "timestamp": 0,  # Simplified timestamp
                "debug_mode": DEBUG_MODE
            }
        }
        
        debug_log(f"🚀 Railway Orchestrator Aufruf: {url}")
        
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
                
                context.processing_method = "railway_langgraph_absolute_minimal"
                context.ai_analysis = result.get("ai_analysis", {})
                context.contact_matching = result.get("contact_matching", {})
                
                return {
                    "status": "success",
                    "method": "railway_langgraph_absolute_minimal",
                    "data": result
                }
            else:
                error_text = response.read().decode('utf-8')
                debug_log(f"⚠️ Railway Orchestrator Fehler: {response.status} - {error_text}")
                return {
                    "status": "error",
                    "method": "fallback_absolute_minimal",
                    "error": f"HTTP {response.status}: {error_text}"
                }
                
    except Exception as e:
        debug_log(f"❌ Railway Orchestrator Exception: {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "method": "fallback_absolute_minimal",
            "error": str(e)
        }

def process_email_minimal(context: MinimalEmailContext) -> MinimalEmailContext:
    """
    Absolute minimal Email Processing
    """
    
    # 1. Versuche Railway LangGraph Orchestrator
    debug_log("🤖 Versuche Railway LangGraph Integration...")
    railway_result = call_railway_orchestrator_minimal(context)
    
    if railway_result["status"] == "success":
        debug_log("✅ Railway LangGraph Integration erfolgreich")
        context.processing_results["railway"] = railway_result["data"]
    else:
        debug_log(f"⚠️ Railway Integration fehlgeschlagen: {railway_result.get('error', 'Unknown error')}")
        debug_log("🔄 Fallback zur Minimal-Verarbeitung...")
        context.processing_method = "absolute_minimal_fallback"
    
    # 2. Absolute Minimal Processing
    debug_log("📧 Absolute Minimal Processing...")
    context.processing_results["minimal"] = {
        "message_processed": True,
        "timestamp": 0,
        "method": context.processing_method,
        "apify_environment": {
            "has_run_id": bool(APIFY_ACTOR_RUN_ID),
            "has_token": bool(APIFY_TOKEN),
            "has_dataset": bool(APIFY_DEFAULT_DATASET_ID)
        }
    }
    
    return context

def main():
    """
    Absolute Minimal Main Function - NO DEPENDENCIES
    """
    try:
        debug_log(f"🚀 Enhanced Email Actor v{ACTOR_VERSION} startet (Absolute Minimal Mode)...")
        debug_log(f"🔧 Railway Integration: {'Aktiviert' if RAILWAY_INTEGRATION else 'Deaktiviert'}")
        debug_log(f"🔗 Orchestrator URL: {RAILWAY_ORCHESTRATOR_URL}")
        
        # Get input data without Apify SDK
        debug_log("📥 Lade Input-Daten ohne SDK...")
        input_data = get_input_data()
        
        if not input_data:
            debug_log("❌ Keine Eingabedaten verfügbar. Verwende Fallback.")
            return
        
        debug_log(f"📋 Input Data Keys: {list(input_data.keys())}")
        
        # Create minimal context
        debug_log("🔧 Initialisiere Absolute Minimal Context...")
        context = MinimalEmailContext(input_data)
        
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
        
        # Process email
        debug_log("🚀 Starte Absolute Minimal Processing...")
        context = process_email_minimal(context)
        
        # Final results
        debug_log("📊 **Absolute Minimal Processing Ergebnisse:**")
        debug_log(f"   Processing Method: {context.processing_method}")
        debug_log(f"   Railway Integration: {'Aktiv' if context.railway_enabled else 'Inaktiv'}")
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
            "message_id": context.message_id,
            "user_email": context.user_email,
            "subject": context.subject,
            "is_spam": context.is_spam,
            "ai_analysis": context.ai_analysis,
            "contact_matching": context.contact_matching,
            "processing_results": context.processing_results,
            "timestamp": 0,
            "success": True
        }
        
        # Push data without SDK
        success = push_data_to_apify(final_output)
        if success:
            debug_log("✅ Absolute Minimal Processing erfolgreich abgeschlossen")
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
    debug_log(f"🔧 Starte Enhanced Email Actor v{ACTOR_VERSION} (Absolute Minimal Mode)...")
    main()