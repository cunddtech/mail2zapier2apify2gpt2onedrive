#!/usr/bin/env python3
"""
🚀 ENHANCED EMAIL ACTOR v3.2 - ULTRA SAFE APIFY COMPATIBLE
Minimal Dependencies Version - Nur Standard Library + Apify Core
"""

import sys
import os
import asyncio
import json
import traceback
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

# Version und Konfiguration
ACTOR_VERSION = "3.2"
RAILWAY_ORCHESTRATOR_URL = os.environ.get('ORCHESTRATOR_URL', 'https://my-langgraph-agent-production.up.railway.app')
RAILWAY_INTEGRATION = os.environ.get('RAILWAY_INTEGRATION', 'true').lower() == 'true'
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() == 'true'

# Webhook für Notfall-Alarm
ALERT_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

def debug_log(message: str):
    """Simple debug logging"""
    print(f"[{ACTOR_VERSION}] {message}")

class MinimalEmailContext:
    """Ultra-minimale Context-Klasse ohne externe Dependencies"""
    
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
        self.processing_method = "minimal_safe"
        
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
    No external HTTP library dependencies
    """
    if not context.railway_enabled:
        debug_log("🚫 Railway Integration deaktiviert, überspringe Orchestrator-Aufruf")
        return {"status": "skipped", "method": "minimal_safe"}
    
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
                "timestamp": asyncio.get_event_loop().time() if asyncio.get_event_loop() else 0,
                "debug_mode": DEBUG_MODE
            }
        }
        
        debug_log(f"🚀 Railway Orchestrator Aufruf: {url}")
        
        # Use urllib instead of aiohttp for minimal dependencies
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
                
                context.processing_method = "railway_langgraph_minimal"
                context.ai_analysis = result.get("ai_analysis", {})
                context.contact_matching = result.get("contact_matching", {})
                
                return {
                    "status": "success",
                    "method": "railway_langgraph_minimal",
                    "data": result
                }
            else:
                error_text = response.read().decode('utf-8')
                debug_log(f"⚠️ Railway Orchestrator Fehler: {response.status} - {error_text}")
                return {
                    "status": "error",
                    "method": "fallback_minimal",
                    "error": f"HTTP {response.status}: {error_text}"
                }
                
    except Exception as e:
        debug_log(f"❌ Railway Orchestrator Exception: {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "method": "fallback_minimal",
            "error": str(e)
        }

def process_email_minimal(context: MinimalEmailContext) -> MinimalEmailContext:
    """
    Minimal Email Processing ohne externe Dependencies
    Fokus auf Railway Integration und sichere Fallbacks
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
        context.processing_method = "minimal_fallback"
    
    # 2. Minimal Standard Processing
    debug_log("📧 Minimal Standard Processing...")
    context.processing_results["minimal"] = {
        "message_processed": True,
        "timestamp": asyncio.get_event_loop().time() if asyncio.get_event_loop() else 0,
        "method": context.processing_method
    }
    
    return context

async def main():
    """
    Ultra-Safe Main Function - Minimal Dependencies
    """
    try:
        debug_log(f"🚀 Enhanced Email Actor v{ACTOR_VERSION} startet (Ultra-Safe Mode)...")
        debug_log(f"🔧 Railway Integration: {'Aktiviert' if RAILWAY_INTEGRATION else 'Deaktiviert'}")
        debug_log(f"🔗 Orchestrator URL: {RAILWAY_ORCHESTRATOR_URL}")
        
        # Minimal Apify Actor import - nur wenn verfügbar
        try:
            from apify import Actor
            debug_log("✅ Apify SDK erfolgreich importiert")
            
            async with Actor:
                debug_log("✅ Actor erfolgreich initialisiert")

                # Eingabedaten abrufen
                debug_log("📥 Versuche, Eingabedaten abzurufen...")
                input_data = await Actor.get_input()
                if not input_data:
                    debug_log("❌ Keine Eingabedaten empfangen. Abbruch.")
                    await Actor.exit(91)
                    return

                # Minimal Context erstellen
                debug_log("🔧 Initialisiere Minimal Processing Context...")
                context = MinimalEmailContext(input_data)
                
                # Validierung
                is_valid, validation_error = context.validate()
                if not is_valid:
                    debug_log(f"❌ Validierung fehlgeschlagen: {validation_error}")
                    if validation_error == "user_email is required":
                        debug_log("🚨⚠️ SPAM: Keine user_email identifiziert - möglicherweise Spam")
                        context.is_spam = True
                    else:
                        await Actor.exit(91)
                        return

                debug_log(f"📋 Processing Context: Message-ID: {context.message_id}, User: {context.user_email}")
                
                # Minimal Email Processing starten
                debug_log("🚀 Starte Minimal Email Processing...")
                try:
                    context = process_email_minimal(context)
                    
                    # Finale Ergebnisse loggen
                    debug_log("📊 **Minimal Processing Ergebnisse:**")
                    debug_log(f"   Processing Method: {context.processing_method}")
                    debug_log(f"   Railway Integration: {'Aktiv' if context.railway_enabled else 'Inaktiv'}")
                    debug_log(f"   Spam Detection: {'Ja' if context.is_spam else 'Nein'}")
                    
                    if context.ai_analysis:
                        debug_log(f"   AI Analysis: {json.dumps(context.ai_analysis, indent=2)}")
                    
                    if context.contact_matching:
                        debug_log(f"   Contact Matching: {json.dumps(context.contact_matching, indent=2)}")
                    
                    # Output für Apify
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
                        "timestamp": asyncio.get_event_loop().time() if asyncio.get_event_loop() else 0
                    }
                    
                    await Actor.push_data(final_output)
                    debug_log("✅ Minimal Processing abgeschlossen und Daten gepusht")

                except Exception as e:
                    debug_log(f"❌ Fehler im Minimal Processing: {str(e)}")
                    debug_log(f"📋 Traceback: {traceback.format_exc()}")
                    
                    # Error output für Apify
                    error_output = {
                        "version": ACTOR_VERSION,
                        "processing_method": "error",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                        "message_id": context.message_id if context else None,
                        "timestamp": asyncio.get_event_loop().time() if asyncio.get_event_loop() else 0
                    }
                    await Actor.push_data(error_output)
                    await Actor.exit(1)

        except ImportError as e:
            debug_log(f"❌ Apify SDK Import Fehler: {str(e)}")
            debug_log("🔧 Fallback: Standalone Mode ohne Apify SDK")
            # Hier könnte man einen Standalone-Modus implementieren
            
        debug_log(f"🏁 Enhanced Email Actor v{ACTOR_VERSION} abgeschlossen")
        
    except Exception as e:
        debug_log(f"❌ Unerwarteter Fehler in main(): {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    debug_log(f"🔧 Starte Enhanced Email Actor v{ACTOR_VERSION} (Ultra-Safe Mode)...")
    asyncio.run(main())