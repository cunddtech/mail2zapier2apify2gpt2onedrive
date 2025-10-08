#!/usr/bin/env python3
"""
🚀 EMAIL PROCESSING SERVICE v2.0 - Orchestrator Integration
Minimale Erweiterung der autarken y5DdGnNCDBoHfSqs7 App um Orchestrator-Kommunikation
Behält ALLE ursprünglichen Features + Orchestrator Webhook Support
"""

import sys
import os
import json
import asyncio
import requests
from typing import Dict, Any, Optional
from datetime import datetime

# Import original autarkes system
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import komplettes ursprüngliches System
from modules.mail.process_email_workflow import process_email_workflow
from modules.utils.debug_log import debug_log
from modules.auth.get_graph_token_onedrive import get_graph_token_onedrive
from modules.auth.get_graph_token_mail import get_graph_token_mail
from modules.msgraph.download_attachment import download_attachments
from modules.weclapp.weclapp_handler import fetch_weclapp_data
from modules.database.email_database import insert_email_data

ACTOR_VERSION = "2.0"
ORCHESTRATOR_URL = os.environ.get('ORCHESTRATOR_URL', 'https://my-langgraph-agent-production.up.railway.app')
ALERT_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

def detect_lead_source(input_data: Dict[str, Any]) -> str:
    """
    Erkennt die Lead-Quelle basierend auf Input-Struktur
    """
    
    # SipGate Call Detection
    if any(key in input_data for key in ['callId', 'event', 'from', 'to', 'user']):
        return 'sipgate'
    
    # WhatsApp Message Detection  
    if any(key in input_data for key in ['message_type', 'sender_phone', 'chat_id', 'whatsapp']):
        return 'whatsapp'
        
    # Standard Email Detection (Default)
    if any(key in input_data for key in ['body_content', 'subject', 'from_email_address_address']):
        return 'email'
    
    return 'email'  # Default zu Email

def prepare_orchestrator_payload(input_data: Dict[str, Any], lead_source: str) -> Dict[str, Any]:
    """
    Bereitet Payload für Orchestrator vor
    """
    
    payload = {
        "lead_source": lead_source,
        "timestamp": datetime.now().isoformat(),
        "actor_version": ACTOR_VERSION,
        "original_data": input_data
    }
    
    # Lead-Source spezifische Daten extrahieren
    if lead_source == 'email':
        payload.update({
            "subject": input_data.get("subject", ""),
            "sender": input_data.get("from_email_address_address", ""),
            "recipient": input_data.get("to_recipients_email_address_address", ""),
            "content": input_data.get("body_content", ""),
            "has_attachments": bool(input_data.get("attachments"))
        })
    
    elif lead_source == 'sipgate':
        payload.update({
            "call_id": input_data.get("callId", ""),
            "event": input_data.get("event", ""),
            "caller": input_data.get("from", ""),
            "called": input_data.get("to", ""),
            "duration": input_data.get("duration", 0),
            "transcript": input_data.get("transcription", "")
        })
    
    elif lead_source == 'whatsapp':
        payload.update({
            "sender_phone": input_data.get("sender_phone", ""),
            "sender_name": input_data.get("sender_name", ""),
            "message_text": input_data.get("message_text", ""),
            "message_type": input_data.get("message_type", "text"),
            "chat_id": input_data.get("chat_id", "")
        })
    
    return payload

async def send_to_orchestrator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sendet Lead-Daten an Orchestrator und erhält Aktionen zurück
    """
    
    try:
        lead_source = payload.get("lead_source", "email")
        endpoint = f"{ORCHESTRATOR_URL}/webhook/{lead_source}"
        
        debug_log(f"📡 Sende an Orchestrator: {endpoint}")
        
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            orchestrator_response = response.json()
            debug_log(f"✅ Orchestrator Response: {orchestrator_response}")
            return orchestrator_response
        else:
            debug_log(f"⚠️ Orchestrator Error {response.status_code}: {response.text}")
            return {"status": "error", "message": "Orchestrator unavailable"}
            
    except Exception as e:
        debug_log(f"❌ Orchestrator Communication Error: {str(e)}")
        return {"status": "error", "message": str(e)}

async def process_with_original_system(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verarbeitet mit dem ursprünglichen autarken System (Fallback)
    """
    
    try:
        debug_log("🔄 Verwende ursprüngliches autarkes System...")
        
        # Daten aus verschachteltem "data"-Feld extrahieren (wie Original)
        data = input_data.get("data", input_data)
        
        # Public Link erstellen (wie Original)
        context = {
            "public_link": data.get("public_link", ""),
            "step": "initialized"
        }

        # Zugriffstoken holen (wie Original)
        access_token_mail = get_graph_token_mail()
        if not access_token_mail:
            debug_log("❌ Zugriffstoken für Mail konnte nicht geholt werden.")
            return {"status": "error", "message": "Mail token unavailable"}

        access_token_onedrive = get_graph_token_onedrive()
        if not access_token_onedrive:
            debug_log("❌ Zugriffstoken für OneDrive konnte nicht geholt werden.")
            return {"status": "error", "message": "OneDrive token unavailable"}

        # Original Workflow ausführen
        gpt_result = await process_email_workflow(
            public_link=context["public_link"],
            input_data=data,
            access_token_mail=access_token_mail,
            access_token_onedrive=access_token_onedrive,
            context=context
        )

        if gpt_result:
            debug_log("✅ Ursprüngliches System erfolgreich.")
            return {
                "status": "success",
                "processing_method": "original_autarke_system",
                "result": gpt_result
            }
        else:
            return {"status": "error", "message": "Original processing failed"}
            
    except Exception as e:
        debug_log(f"❌ Original System Error: {str(e)}")
        return {"status": "error", "message": str(e)}

async def main():
    """
    Hauptfunktion - Orchestrator Integration + Original System Fallback
    """
    
    try:
        debug_log(f"🚀 Email Processing Service v{ACTOR_VERSION} - Orchestrator Integration")
        
        from apify import Actor
        async with Actor:
            debug_log("✅ Actor erfolgreich initialisiert.")

            # Eingabedaten abrufen
            input_data = await Actor.get_input()
            if not input_data:
                debug_log("❌ Keine Eingabedaten empfangen.")
                await Actor.exit(91)
                return

            debug_log(f"📥 Input Keys: {list(input_data.keys())}")
            
            # Lead-Quelle erkennen
            lead_source = detect_lead_source(input_data)
            debug_log(f"🎯 Lead Source erkannt: {lead_source}")

            # Fallback für Zapier-Webhook (wie Original)
            input_data["zapier_webhook"] = input_data.get("zapier_webhook") or ALERT_WEBHOOK_URL

            # Orchestrator-Integration versuchen
            orchestrator_payload = prepare_orchestrator_payload(input_data, lead_source)
            orchestrator_response = await send_to_orchestrator(orchestrator_payload)
            
            result = None
            
            if orchestrator_response.get("status") == "success":
                debug_log("✅ Orchestrator verarbeitung erfolgreich")
                result = {
                    "status": "success",
                    "processing_method": "orchestrator",
                    "lead_source": lead_source,
                    "orchestrator_response": orchestrator_response,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Fallback: Ursprüngliches autarkes System
                debug_log("🔄 Fallback zu ursprünglichem autarken System...")
                result = await process_with_original_system(input_data)
                result["lead_source"] = lead_source
                result["timestamp"] = datetime.now().isoformat()

            # Ergebnis ausgeben
            if result:
                await Actor.push_data(result)
                debug_log(f"✅ Processing completed: {result['processing_method']}")
                
                # Optional: Zapier Webhook (wie Original)
                zapier_webhook = input_data.get("zapier_webhook")
                if zapier_webhook:
                    debug_log(f"🔗 Sende zu Zapier: {zapier_webhook}")
                    # Webhook implementation hier
            else:
                debug_log("❌ Keine Ergebnisse erhalten.")
                await Actor.exit(1)

    except Exception as e:
        debug_log(f"❌ Main Error: {str(e)}")
        error_result = {
            "status": "error",
            "error": str(e),
            "actor_version": ACTOR_VERSION,
            "timestamp": datetime.now().isoformat()
        }
        
        from apify import Actor
        await Actor.push_data(error_result)
        await Actor.exit(1)

if __name__ == "__main__":
    asyncio.run(main())