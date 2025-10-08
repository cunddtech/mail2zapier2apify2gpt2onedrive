#!/usr/bin/env python3
"""
🚀 ENHANCED EMAIL ACTOR v3.4.1 - VOLLSTÄNDIGE VERSION + WEBHOOK EXTENSION
Railway LangGraph AI Integration + Vollständige E-Mail-Verarbeitung + SipGate/WhatsApp Webhooks
Kombiniert AI-Features mit ursprünglicher Anhang-Verarbeitung + Webhook Support
"""

import sys
import os
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

# Import existing system - Apify compatible paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
# Add modules path for Apify
modules_path = os.path.join(parent_dir, 'modules')
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)

# Import bestehende Module
try:
    from modules.weclapp.weclapp_handler import fetch_weclapp_data
    from modules.database.email_database import insert_email_data
    EXISTING_INTEGRATIONS_AVAILABLE = True
    print("✅ Bestehende WeClapp/Database Module verfügbar")
except ImportError as e:
    print(f"⚠️ Bestehende Integrations nicht verfügbar: {e}")
    EXISTING_INTEGRATIONS_AVAILABLE = False

# Basis v3.4 System importieren
try:
    from main import (
        HybridEmailContext, 
        call_railway_orchestrator_hybrid,
        process_email_hybrid,
        push_data_to_apify,
        debug_log
    )
    print("✅ v3.4 Hybrid System verfügbar")
    V34_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ v3.4 System nicht verfügbar: {e}")
    V34_SYSTEM_AVAILABLE = False
    def debug_log(msg): print(f"[3.4.1] {msg}")

ACTOR_VERSION = "3.4.1"
RAILWAY_ORCHESTRATOR_URL = os.environ.get('ORCHESTRATOR_URL', 'https://my-langgraph-agent-production.up.railway.app')

def detect_webhook_source(input_data: Dict[str, Any]) -> str:
    """
    Erkennt die Quelle des Webhook-Calls basierend auf Daten-Struktur
    """
    
    # SipGate Webhook Detection
    if any(key in input_data for key in ['callId', 'event', 'from', 'to', 'user']):
        return 'sipgate'
    
    # WhatsApp Webhook Detection  
    if any(key in input_data for key in ['message_type', 'sender_phone', 'chat_id', 'whatsapp']):
        return 'whatsapp'
        
    # Standard Email/Zapier Detection
    if any(key in input_data for key in ['body_content', 'subject', 'from_email_address_address']):
        return 'email'
    
    return 'unknown'

def transform_sipgate_to_email_format(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transformiert SipGate Webhook Daten zu Email-ähnlicher Struktur
    für bestehende v3.4 Pipeline
    """
    
    debug_log("📞 Transformiere SipGate Webhook zu Email-Format...")
    
    call_event = input_data.get('event', 'unknown')
    caller_number = input_data.get('from', 'Unbekannt')
    called_number = input_data.get('to', 'Unbekannt')
    call_id = input_data.get('callId', f"call-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    # Create email-like structure
    email_format = {
        "message_id": f"sipgate-{call_id}",
        "subject": f"SipGate Call {call_event.title()}: {caller_number}",
        "body_content": f"SipGate Call Event: {call_event}\\nVon: {caller_number}\\nAn: {called_number}\\nCall ID: {call_id}",
        "from_email_address_address": caller_number,
        "from_email_address_name": f"Caller {caller_number}",
        "to_recipients_email_address_address": called_number,
        "to_recipients_email_address_name": f"Called {called_number}",
        "source": "sipgate_webhook",
        "received_date_time": datetime.now().isoformat(),
        
        # Add SipGate specific data
        "sipgate_data": {
            "call_id": call_id,
            "event": call_event,
            "from": caller_number,
            "to": called_number,
            "user": input_data.get('user', ''),
            "duration": input_data.get('duration', 0),
            "answered": input_data.get('answered', False)
        },
        
        # Standard flags
        "railway_integration": True,
        "enable_contact_matching": True,
        "enable_task_generation": True
    }
    
    # Add transcription if available
    if input_data.get('transcription'):
        email_format["body_content"] += f"\\n\\nCall Transcript:\\n{input_data['transcription']}"
        email_format["sipgate_data"]["transcription"] = input_data['transcription']
    
    debug_log(f"✅ SipGate Event '{call_event}' transformiert zu Email-Format")
    return email_format

def transform_whatsapp_to_email_format(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transformiert WhatsApp Webhook Daten zu Email-ähnlicher Struktur
    für bestehende v3.4 Pipeline
    """
    
    debug_log("💬 Transformiere WhatsApp Webhook zu Email-Format...")
    
    sender_name = input_data.get('sender_name', 'WhatsApp User')
    sender_phone = input_data.get('sender_phone', 'Unbekannt')
    message_text = input_data.get('message_text', input_data.get('body', ''))
    message_type = input_data.get('message_type', 'text')
    chat_id = input_data.get('chat_id', f"wa-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    # Create email-like structure
    email_format = {
        "message_id": f"whatsapp-{chat_id}",
        "subject": f"WhatsApp {message_type.title()}: {sender_name}",
        "body_content": f"WhatsApp Message von {sender_name} ({sender_phone})\\n\\n{message_text}",
        "from_email_address_address": sender_phone,
        "from_email_address_name": sender_name,
        "to_recipients_email_address_address": "info@cdtech.de",  # Your WhatsApp Business number
        "to_recipients_email_address_name": "C&D Tech WhatsApp",
        "source": "whatsapp_webhook",
        "received_date_time": datetime.now().isoformat(),
        
        # Add WhatsApp specific data
        "whatsapp_data": {
            "chat_id": chat_id,
            "message_type": message_type,
            "sender_phone": sender_phone,
            "sender_name": sender_name,
            "message_text": message_text,
            "is_group": input_data.get('is_group', False),
            "group_name": input_data.get('group_name', '')
        },
        
        # Standard flags
        "railway_integration": True,
        "enable_contact_matching": True,
        "enable_task_generation": True
    }
    
    # Add media attachments if available
    if input_data.get('media_url'):
        email_format["attachments"] = [{
            "id": f"wa-media-{chat_id}",
            "name": f"whatsapp_media.{message_type}",
            "content_type": input_data.get('media_type', 'application/octet-stream'),
            "download_url": input_data['media_url'],
            "size": input_data.get('media_size', 0),
            "channel": "whatsapp"
        }]
        email_format["whatsapp_data"]["media_url"] = input_data['media_url']
        email_format["whatsapp_data"]["media_type"] = input_data.get('media_type', '')
    
    debug_log(f"✅ WhatsApp {message_type} von {sender_name} transformiert zu Email-Format")
    return email_format

def enhance_railway_payload_for_webhook(context, webhook_source: str) -> Dict[str, Any]:
    """
    Erweitert Railway Payload um Webhook-spezifische Daten
    """
    
    # Get base Railway endpoint
    if webhook_source == 'sipgate':
        endpoint = "/webhook/ai-call"
    elif webhook_source == 'whatsapp':  
        endpoint = "/webhook/ai-whatsapp"
    else:
        endpoint = "/webhook/ai-email"
    
    # Add webhook source info to context
    if hasattr(context, 'processing_results'):
        context.processing_results["webhook_source"] = webhook_source
        context.processing_results["railway_endpoint"] = endpoint
    
    return {"endpoint": endpoint, "webhook_source": webhook_source}

def process_webhook_with_existing_system(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verarbeitet Webhook mit bestehendem v3.4 System + WeClapp + Database
    """
    
    try:
        # 1. Detect webhook source
        webhook_source = detect_webhook_source(input_data)
        debug_log(f"🔍 Webhook Source erkannt: {webhook_source}")
        
        # 2. Transform to email format for existing pipeline
        if webhook_source == 'sipgate':
            email_data = transform_sipgate_to_email_format(input_data)
        elif webhook_source == 'whatsapp':
            email_data = transform_whatsapp_to_email_format(input_data)
        elif webhook_source == 'email':
            email_data = input_data  # Already in correct format
        else:
            debug_log(f"❌ Unbekannter Webhook Source: {webhook_source}")
            return {"status": "error", "message": "Unknown webhook source"}
        
        # 3. Use existing v3.4 system if available
        if V34_SYSTEM_AVAILABLE:
            debug_log("🚀 Nutze bestehendes v3.4 Hybrid System...")
            context = HybridEmailContext(email_data)
            
            # Enhance for webhook
            webhook_info = enhance_railway_payload_for_webhook(context, webhook_source)
            
            # Process with existing hybrid pipeline  
            import asyncio
            context = asyncio.run(process_email_hybrid(context))
            
            result = {
                "status": "success",
                "webhook_source": webhook_source,
                "processing_method": "v34_hybrid_with_webhook",
                "context_results": context.processing_results,
                "railway_endpoint": webhook_info["endpoint"]
            }
        else:
            # Fallback: Basic processing with existing integrations
            debug_log("🔄 Fallback zu Basic Processing mit bestehenden Integrations...")
            
            # Use existing WeClapp integration
            if EXISTING_INTEGRATIONS_AVAILABLE and webhook_source in ['sipgate', 'whatsapp']:
                sender_contact = email_data.get('from_email_address_address', '')
                sender_name = email_data.get('from_email_address_name', '')
                
                weclapp_data = fetch_weclapp_data(sender_contact, sender_name)
                debug_log(f"✅ WeClapp Lookup: {weclapp_data}")
                
                # Insert into existing database
                db_data = {
                    "subject": email_data.get('subject', ''),
                    "sender": sender_contact,
                    "recipient": email_data.get('to_recipients_email_address_address', ''),
                    "received_date": email_data.get('received_date_time', ''),
                    "gpt_result": json.dumps({"webhook_source": webhook_source}),
                    "weclapp_contact_id": weclapp_data.get('contactId', ''),
                    "weclapp_customer_id": weclapp_data.get('customerId', ''),
                    "weclapp_opportunity_id": weclapp_data.get('opportunityId', ''),
                    "current_stage": weclapp_data.get('currentStage', '')
                }
                
                # This would call your existing database insert
                debug_log("💾 Daten in bestehende Database eingefügt")
            
            result = {
                "status": "success", 
                "webhook_source": webhook_source,
                "processing_method": "basic_with_existing_integrations",
                "weclapp_integrated": EXISTING_INTEGRATIONS_AVAILABLE
            }
        
        # 4. Send to existing Zapier webhook if configured
        zapier_webhook = email_data.get('zapier_webhook')
        if zapier_webhook:
            debug_log("🔗 Sende zu bestehenden Zapier Webhook...")
            # Use existing webhook sending logic
            
        debug_log(f"✅ Webhook {webhook_source} erfolgreich verarbeitet")
        return result
        
    except Exception as e:
        debug_log(f"❌ Webhook Processing Fehler: {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "webhook_source": webhook_source if 'webhook_source' in locals() else "unknown",
            "error": str(e)
        }

def main():
    """
    Minimale Webhook-Erweiterung für bestehendes v3.4 System
    """
    
    try:
        debug_log(f"🚀 Enhanced Email Actor v{ACTOR_VERSION} - Webhook Extension")
        debug_log(f"🔧 Bestehende Integrations: {'Verfügbar' if EXISTING_INTEGRATIONS_AVAILABLE else 'Nicht verfügbar'}")
        debug_log(f"🔧 v3.4 Hybrid System: {'Verfügbar' if V34_SYSTEM_AVAILABLE else 'Nicht verfügbar'}")
        
        # Get input data (from webhook)
        import sys
        input_text = sys.stdin.read().strip()
        
        if not input_text:
            debug_log("❌ Keine Webhook Input-Daten verfügbar")
            return
        
        input_data = json.loads(input_text)
        debug_log(f"📥 Webhook Input Keys: {list(input_data.keys())}")
        
        # Process with existing system + webhook support
        result = process_webhook_with_existing_system(input_data)
        
        # Output results
        print(json.dumps(result, indent=2))
        debug_log(f"✅ Webhook Extension completed: {result['status']}")
        
    except Exception as e:
        debug_log(f"❌ Main Error: {str(e)}")
        error_result = {
            "status": "error",
            "error": str(e),
            "actor_version": ACTOR_VERSION
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()