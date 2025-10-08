#!/usr/bin/env python3
"""
🚀 ENHANCED EMAIL ACTOR v3.1 - APIFY COMPATIBLE
Enhanced Email Processing Chain mit Railway LangGraph AI Integration
Ohne Pydantic Dependencies für Apify Kompatibilität
"""

import sys
import os
import asyncio
import json
import traceback
from typing import Dict, Any, Optional, List
from apify import Actor
from modules.mail.process_email_workflow import process_email_workflow
from modules.utils.debug_log import debug_log
from modules.auth.get_graph_token_onedrive import get_graph_token_onedrive
from modules.auth.get_graph_token_mail import get_graph_token_mail
from modules.msgraph.download_attachment import download_attachments

# Version und Konfiguration
ACTOR_VERSION = "3.1"
RAILWAY_ORCHESTRATOR_URL = os.environ.get('ORCHESTRATOR_URL', 'https://my-langgraph-agent-production.up.railway.app')
RAILWAY_INTEGRATION = os.environ.get('RAILWAY_INTEGRATION', 'true').lower() == 'true'
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() == 'true'

# Webhook für Notfall-Alarm
ALERT_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

class EmailProcessingContext:
    """Vereinfachte Context-Klasse ohne Pydantic Dependencies"""
    
    def __init__(self, input_data: Dict[str, Any]):
        # Core fields from input
        self.message_id = input_data.get("message_id")
        self.user_email = input_data.get("to_recipients_email_address_address")
        self.recipient_email = input_data.get("from_email_address_address")
        self.subject = input_data.get("subject", "")
        self.body_content = input_data.get("body_content", "")
        
        # Processing flags
        self.source = input_data.get("source", "mail")
        self.is_spam = False
        self.processing_method = "standard"
        
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
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "message_id": self.message_id,
            "user_email": self.user_email,
            "recipient_email": self.recipient_email,
            "subject": self.subject,
            "body_content": self.body_content,
            "source": self.source,
            "is_spam": self.is_spam,
            "processing_method": self.processing_method,
            "railway_enabled": self.railway_enabled,
            "orchestrator_url": self.orchestrator_url,
            "zapier_webhook": self.zapier_webhook,
            "processing_results": self.processing_results,
            "ai_analysis": self.ai_analysis,
            "contact_matching": self.contact_matching,
            "raw_data": self.raw_data
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate required fields"""
        if not self.message_id:
            return False, "message_id is required"
        if not self.user_email:
            return False, "user_email is required"
        return True, "valid"

async def call_railway_orchestrator(context: EmailProcessingContext, endpoint: str = "/webhook/ai-email") -> Dict[str, Any]:
    """
    Railway LangGraph Orchestrator Integration
    Ruft den Railway LangGraph Service für AI-basierte Verarbeitung auf
    """
    if not context.railway_enabled:
        debug_log("🚫 Railway Integration deaktiviert, überspringe Orchestrator-Aufruf")
        return {"status": "skipped", "method": "standard"}
    
    try:
        import aiohttp
        
        url = f"{context.orchestrator_url}{endpoint}"
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
                "timestamp": asyncio.get_event_loop().time(),
                "debug_mode": DEBUG_MODE
            }
        }
        
        debug_log(f"🚀 Railway Orchestrator Aufruf: {url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    debug_log(f"✅ Railway Orchestrator Antwort: {json.dumps(result, indent=2)}")
                    
                    context.processing_method = "railway_langgraph"
                    context.ai_analysis = result.get("ai_analysis", {})
                    context.contact_matching = result.get("contact_matching", {})
                    
                    return {
                        "status": "success",
                        "method": "railway_langgraph",
                        "data": result
                    }
                else:
                    error_text = await response.text()
                    debug_log(f"⚠️ Railway Orchestrator Fehler: {response.status} - {error_text}")
                    return {
                        "status": "error",
                        "method": "fallback_standard",
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
    except Exception as e:
        debug_log(f"❌ Railway Orchestrator Exception: {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "method": "fallback_standard",
            "error": str(e)
        }

async def enhanced_process_email_workflow(context: EmailProcessingContext, access_token_mail: str, access_token_onedrive: str) -> EmailProcessingContext:
    """
    Enhanced Email Processing mit Railway Integration
    Falls Railway nicht verfügbar, Fallback zur Standard-Verarbeitung
    """
    
    # 1. Versuche Railway LangGraph Orchestrator
    debug_log("🤖 Versuche Railway LangGraph Integration...")
    railway_result = await call_railway_orchestrator(context)
    
    if railway_result["status"] == "success":
        debug_log("✅ Railway LangGraph Integration erfolgreich")
        context.processing_results["railway"] = railway_result["data"]
    else:
        debug_log(f"⚠️ Railway Integration fehlgeschlagen: {railway_result.get('error', 'Unknown error')}")
        debug_log("🔄 Fallback zur Standard-Verarbeitung...")
    
    # 2. Standard Email Processing Chain (als Fallback oder Ergänzung)
    debug_log("📧 Starte Standard Email Processing Chain...")
    
    try:
        # Convert context back to dict format for legacy function
        legacy_context = context.to_dict()
        
        processed_context = await process_email_workflow(
            public_link=None,
            input_data=context.raw_data,
            access_token_mail=access_token_mail,
            access_token_onedrive=access_token_onedrive,
            context=legacy_context
        )
        
        # Update context with processed results
        context.processing_results["standard"] = processed_context
        
        debug_log("✅ Standard Email Processing abgeschlossen")
        
    except Exception as e:
        debug_log(f"❌ Fehler in Standard Email Processing: {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        context.processing_results["error"] = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
    
    return context

async def main():
    """
    Enhanced Main Function mit Railway LangGraph Integration
    """
    try:
        debug_log(f"🚀 Enhanced Email Actor v{ACTOR_VERSION} startet...")
        debug_log(f"🔧 Railway Integration: {'Aktiviert' if RAILWAY_INTEGRATION else 'Deaktiviert'}")
        debug_log(f"🔗 Orchestrator URL: {RAILWAY_ORCHESTRATOR_URL}")
        
        async with Actor:
            debug_log("✅ Actor erfolgreich initialisiert")

            # Eingabedaten abrufen
            debug_log("📥 Versuche, Eingabedaten abzurufen...")
            input_data = await Actor.get_input()
            if not input_data:
                debug_log("❌ Keine Eingabedaten empfangen. Abbruch.")
                await Actor.exit(91)
                return

            # Enhanced Context erstellen
            debug_log("🔧 Initialisiere Enhanced Processing Context...")
            context = EmailProcessingContext(input_data)
            
            # Validierung
            is_valid, validation_error = context.validate()
            if not is_valid:
                debug_log(f"❌ Validierung fehlgeschlagen: {validation_error}")
                if validation_error == "user_email is required":
                    debug_log("🚨⚠️ SPAM: Keine user_email identifiziert - möglicherweise Spam")
                    context.is_spam = True
                    # Continue with spam handling instead of exit
                else:
                    await Actor.exit(91)
                    return

            debug_log(f"📋 Processing Context: Message-ID: {context.message_id}, User: {context.user_email}")
            
            # Zugriffstoken für Mail holen
            debug_log("📧 Versuche, Zugriffstoken für Mail zu holen...")
            access_token_mail = await get_graph_token_mail()
            debug_log(f"📧 Zugriffstoken für Mail: {'Erfolgreich' if access_token_mail else 'Fehlgeschlagen'}")
            if not access_token_mail:
                debug_log("❌ Zugriffstoken für Mail konnte nicht geholt werden. Abbruch.")
                await Actor.exit(91)
                return

            # Zugriffstoken für OneDrive holen
            debug_log("📂 Versuche, Zugriffstoken für OneDrive zu holen...")
            access_token_onedrive = await get_graph_token_onedrive()
            debug_log(f"📂 Zugriffstoken für OneDrive: {'Erfolgreich' if access_token_onedrive else 'Fehlgeschlagen'}")
            if not access_token_onedrive:
                debug_log("❌ Zugriffstoken für OneDrive konnte nicht geholt werden. Abbruch.")
                await Actor.exit(91)
                return

            # Enhanced Email Processing starten
            debug_log("🚀 Starte Enhanced Email Processing Chain...")
            try:
                context = await enhanced_process_email_workflow(
                    context=context,
                    access_token_mail=access_token_mail,
                    access_token_onedrive=access_token_onedrive
                )
                
                # Finale Ergebnisse loggen
                debug_log("📊 **Enhanced Processing Ergebnisse:**")
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
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                await Actor.push_data(final_output)
                debug_log("✅ Enhanced Processing abgeschlossen und Daten gepusht")

            except Exception as e:
                debug_log(f"❌ Fehler im Enhanced Processing: {str(e)}")
                debug_log(f"📋 Traceback: {traceback.format_exc()}")
                
                # Error output für Apify
                error_output = {
                    "version": ACTOR_VERSION,
                    "processing_method": "error",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "message_id": context.message_id if context else None,
                    "timestamp": asyncio.get_event_loop().time()
                }
                await Actor.push_data(error_output)
                await Actor.exit(1)

        debug_log(f"🏁 Enhanced Email Actor v{ACTOR_VERSION} abgeschlossen")
        
    except Exception as e:
        debug_log(f"❌ Unerwarteter Fehler in main(): {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    debug_log(f"🔧 Starte Enhanced Email Actor v{ACTOR_VERSION}...")
    asyncio.run(main())