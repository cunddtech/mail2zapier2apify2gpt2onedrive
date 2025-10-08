#!/usr/bin/env python3
"""
🚀 ENHANCED MULTI-CHANNEL ACTOR v3.5 - UNIFIED COMMUNICATION HUB
Railway LangGraph AI Integration + Email + SipGate + WhatsApp
Vereinheitlichte Multi-Channel Processing Pipeline
"""

import sys
import os
import asyncio
import json
import traceback
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, List
from datetime import datetime

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
ACTOR_VERSION = "3.5"
RAILWAY_ORCHESTRATOR_URL = os.environ.get('ORCHESTRATOR_URL', 'https://my-langgraph-agent-production.up.railway.app')
RAILWAY_INTEGRATION = os.environ.get('RAILWAY_INTEGRATION', 'true').lower() == 'true'
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() == 'true'

# Apify API Configuration
APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
APIFY_ACTOR_RUN_ID = os.environ.get('APIFY_ACTOR_RUN_ID')
APIFY_DEFAULT_DATASET_ID = os.environ.get('APIFY_DEFAULT_DATASET_ID')

# Multi-Channel Webhook URLs
ALERT_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

def debug_log(message: str):
    """Enhanced debug logging mit Multi-Channel Support"""
    timestamp = datetime.now().isoformat()
    print(f"[{ACTOR_VERSION}] {message}")
    if DEBUG_MODE:
        print(f"[DEBUG {timestamp}] {message}")

class MultiChannelContext:
    """
    🚀 UNIFIED MULTI-CHANNEL CONTEXT CLASS
    Einheitliche Verarbeitung für Email, SipGate Calls und WhatsApp Messages
    """
    
    def __init__(self, input_data: Dict[str, Any]):
        # Channel Identification
        self.channel_type = input_data.get("channel_type", "email")
        self.message_id = input_data.get("message_id", f"multichannel-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        self.source = input_data.get("source", "manual")
        
        # Content (unified across channels)
        self.content = input_data.get("body_content", "")
        self.subject = input_data.get("subject", "")
        
        # Contact Information (unified)
        self.sender_name = input_data.get("from_email_address_name", "")
        self.sender_contact = input_data.get("from_email_address_address", "")
        self.recipient_contact = input_data.get("to_recipients_email_address_address", "")
        
        # Channel-specific Data
        self.email_data = self._extract_email_data(input_data) if self.channel_type == "email" else None
        self.sipgate_data = self._extract_sipgate_data(input_data) if self.channel_type == "phone_call" else None
        self.whatsapp_data = self._extract_whatsapp_data(input_data) if self.channel_type == "whatsapp" else None
        
        # Multi-Channel Features
        self.unified_processing = input_data.get("enable_unified_processing", True)
        self.railway_integration = input_data.get("railway_integration", True)
        self.contact_matching = input_data.get("enable_contact_matching", True)
        self.task_generation = input_data.get("enable_task_generation", True)
        
        # Processing Results
        self.processing_results = {
            "channel_type": self.channel_type,
            "railway_results": {},
            "contact_match": {},
            "generated_tasks": [],
            "unified_analysis": {},
            "channel_specific": {}
        }
        
        # Railway Integration
        self.orchestrator_url = RAILWAY_ORCHESTRATOR_URL
        self.zapier_webhook = input_data.get("zapier_webhook") or ALERT_WEBHOOK_URL
        
        # Attachments/Media (universal)
        self.attachments = input_data.get("attachments", [])
        self.media_files = []
        
        # Timing
        self.received_datetime = input_data.get("received_date_time") or datetime.now().isoformat()
        
        # Store raw data
        self.raw_input = input_data.copy()
        
        debug_log(f"🔧 Multi-Channel Context initialisiert: {self.channel_type}")
        debug_log(f"📋 Message ID: {self.message_id}, Sender: {self.sender_contact}")
    
    def _extract_email_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Email-specific data"""
        return {
            "subject": input_data.get("subject", ""),
            "body_content": input_data.get("body_content", ""),
            "from_email": input_data.get("from_email_address_address", ""),
            "from_name": input_data.get("from_email_address_name", ""),
            "to_email": input_data.get("to_recipients_email_address_address", ""),
            "attachments": input_data.get("attachments", [])
        }
    
    def _extract_sipgate_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract SipGate Call-specific data"""
        call_data = input_data.get("sipgate_call_data", {})
        return {
            "call_id": call_data.get("call_id", ""),
            "event": call_data.get("event", "newCall"),
            "direction": call_data.get("direction", "in"),
            "caller_number": call_data.get("from", ""),
            "called_number": call_data.get("to", ""),
            "sipgate_user": call_data.get("user", ""),
            "duration": call_data.get("duration", 0),
            "answered": call_data.get("answered", False),
            "transcription": call_data.get("transcription", ""),
            "recording_url": call_data.get("recording_url", "")
        }
    
    def _extract_whatsapp_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract WhatsApp Message-specific data"""
        wa_data = input_data.get("whatsapp_message_data", {})
        return {
            "message_id": wa_data.get("message_id", ""),
            "chat_id": wa_data.get("chat_id", ""),
            "message_type": wa_data.get("message_type", "text"),
            "sender_phone": wa_data.get("sender_phone", ""),
            "sender_name": wa_data.get("sender_name", ""),
            "message_text": wa_data.get("message_text", ""),
            "media_url": wa_data.get("media_url", ""),
            "media_type": wa_data.get("media_type", ""),
            "timestamp": wa_data.get("timestamp", ""),
            "is_group": wa_data.get("is_group", False),
            "group_name": wa_data.get("group_name", "")
        }
    
    def get_unified_contact_info(self) -> Dict[str, Any]:
        """Einheitliche Contact Information für alle Channels"""
        contact_info = {
            "name": self.sender_name,
            "primary_contact": self.sender_contact,
            "channel": self.channel_type,
            "additional_info": {}
        }
        
        if self.channel_type == "phone_call" and self.sipgate_data:
            contact_info["additional_info"]["phone"] = self.sipgate_data["caller_number"]
            contact_info["additional_info"]["sipgate_user"] = self.sipgate_data["sipgate_user"]
            
        elif self.channel_type == "whatsapp" and self.whatsapp_data:
            contact_info["additional_info"]["whatsapp_phone"] = self.whatsapp_data["sender_phone"]
            contact_info["additional_info"]["chat_id"] = self.whatsapp_data["chat_id"]
            
        elif self.channel_type == "email" and self.email_data:
            contact_info["additional_info"]["email"] = self.email_data["from_email"]
            
        return contact_info
    
    def get_unified_content(self) -> Dict[str, Any]:
        """Einheitlicher Content für AI-Analyse über alle Channels"""
        unified_content = {
            "primary_content": self.content,
            "subject_topic": self.subject,
            "channel": self.channel_type,
            "content_type": "text",
            "media_files": len(self.attachments),
            "formatted_content": ""
        }
        
        # Channel-specific Content Formatting
        if self.channel_type == "email":
            unified_content["formatted_content"] = f"Email Subject: {self.subject}\\n\\nContent:\\n{self.content}"
            
        elif self.channel_type == "phone_call" and self.sipgate_data:
            call_info = f"Call from {self.sipgate_data['caller_number']} to {self.sipgate_data['called_number']}"
            if self.sipgate_data['transcription']:
                unified_content["formatted_content"] = f"Phone Call: {call_info}\\n\\nTranscript:\\n{self.sipgate_data['transcription']}"
            else:
                unified_content["formatted_content"] = f"Phone Call: {call_info}\\n\\nDuration: {self.sipgate_data['duration']}s, Answered: {self.sipgate_data['answered']}"
                
        elif self.channel_type == "whatsapp" and self.whatsapp_data:
            chat_info = f"WhatsApp from {self.whatsapp_data['sender_name']} ({self.whatsapp_data['sender_phone']})"
            if self.whatsapp_data['is_group']:
                chat_info += f" in group '{self.whatsapp_data['group_name']}'"
            unified_content["formatted_content"] = f"{chat_info}\\n\\nMessage:\\n{self.whatsapp_data['message_text']}"
            
        return unified_content
    
    def add_processing_result(self, step: str, result: Dict[str, Any]):
        """Add processing result für Multi-Channel Tracking"""
        self.processing_results[step] = result
        debug_log(f"📊 Processing result added: {step}")
    
    def get_channel_endpoint(self) -> str:
        """Get Railway endpoint basiert auf Channel Type"""
        endpoint_map = {
            "email": "/webhook/ai-email",
            "phone_call": "/webhook/ai-call", 
            "whatsapp": "/webhook/ai-whatsapp",
            "multi_channel": "/webhook/ai-multichannel"
        }
        return endpoint_map.get(self.channel_type, "/webhook/ai-email")
    
    def to_railway_payload(self) -> Dict[str, Any]:
        """Create Railway LangGraph payload für Multi-Channel Processing"""
        base_payload = {
            "channel_data": {
                "channel_type": self.channel_type,
                "message_id": self.message_id,
                "source": self.source,
                "timestamp": self.received_datetime
            },
            "contact_info": self.get_unified_contact_info(),
            "content": self.get_unified_content(),
            "processing_options": {
                "enable_contact_matching": self.contact_matching,
                "enable_task_generation": self.task_generation,
                "enable_unified_processing": self.unified_processing,
                "workflow_type": f"enhanced_{self.channel_type}_processing"
            },
            "metadata": {
                "actor_version": ACTOR_VERSION,
                "processing_timestamp": datetime.now().isoformat(),
                "has_media": len(self.attachments) > 0,
                "media_count": len(self.attachments)
            }
        }
        
        # Add Channel-specific data
        if self.channel_type == "email" and self.email_data:
            base_payload["channel_specific"] = {"email_data": self.email_data}
        elif self.channel_type == "phone_call" and self.sipgate_data:
            base_payload["channel_specific"] = {"sipgate_data": self.sipgate_data}
        elif self.channel_type == "whatsapp" and self.whatsapp_data:
            base_payload["channel_specific"] = {"whatsapp_data": self.whatsapp_data}
            
        return base_payload

# ================================
# RAILWAY MULTI-CHANNEL ORCHESTRATOR INTEGRATION
# ================================

def call_railway_multichannel_orchestrator(context: MultiChannelContext) -> Dict[str, Any]:
    """
    🤖 RAILWAY LANGGRAPH MULTI-CHANNEL ORCHESTRATOR
    Einheitlicher AI-Aufruf für Email, SipGate Calls und WhatsApp Messages
    """
    
    if not context.railway_integration:
        debug_log("🚫 Railway Integration deaktiviert für Multi-Channel Processing")
        return {"status": "skipped", "method": "multichannel_disabled"}
    
    try:
        # Dynamic endpoint basiert auf Channel Type
        endpoint = context.get_channel_endpoint()
        url = f"{context.orchestrator_url}{endpoint}"
        debug_log(f"🚀 Railway Multi-Channel Orchestrator: {url}")
        
        # Channel-specific payload
        payload = context.to_railway_payload()
        debug_log(f"📦 Payload für {context.channel_type}: {json.dumps(payload, indent=2)}")
        
        # HTTP Request zu Railway LangGraph
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': f'Enhanced-MultiChannel-Actor-v{ACTOR_VERSION}',
                'X-Channel-Type': context.channel_type,
                'X-Message-ID': context.message_id
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                debug_log(f"✅ Railway {context.channel_type.title()} Orchestrator Antwort: {json.dumps(result, indent=2)}")
                
                # Store channel-specific results
                context.add_processing_result("railway_multichannel", result)
                
                return {
                    "status": "success",
                    "method": f"railway_multichannel_{context.channel_type}",
                    "data": result,
                    "channel": context.channel_type,
                    "endpoint": endpoint
                }
            else:
                error_text = response.read().decode('utf-8')
                debug_log(f"⚠️ Railway {context.channel_type} Orchestrator Fehler: {response.status} - {error_text}")
                return {
                    "status": "error",
                    "method": f"fallback_{context.channel_type}",
                    "error": f"HTTP {response.status}: {error_text}",
                    "channel": context.channel_type
                }
                
    except Exception as e:
        debug_log(f"❌ Railway Multi-Channel Exception: {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "method": f"fallback_{context.channel_type}",
            "error": str(e),
            "channel": context.channel_type
        }

def call_railway_email_orchestrator(context: MultiChannelContext) -> Dict[str, Any]:
    """Dedicated Email Processing via Railway /webhook/ai-email"""
    if context.channel_type != "email":
        return {"status": "skipped", "reason": "not_email_channel"}
    return call_railway_multichannel_orchestrator(context)

def call_railway_sipgate_orchestrator(context: MultiChannelContext) -> Dict[str, Any]:
    """Dedicated SipGate Call Processing via Railway /webhook/ai-call"""
    if context.channel_type != "phone_call":
        return {"status": "skipped", "reason": "not_phone_channel"}
    return call_railway_multichannel_orchestrator(context)

def call_railway_whatsapp_orchestrator(context: MultiChannelContext) -> Dict[str, Any]:
    """Dedicated WhatsApp Message Processing via Railway /webhook/ai-whatsapp"""
    if context.channel_type != "whatsapp":
        return {"status": "skipped", "reason": "not_whatsapp_channel"}
    return call_railway_multichannel_orchestrator(context)

# ================================
# APIFY INPUT/OUTPUT FUNCTIONS
# ================================

def get_input_data() -> Dict[str, Any]:
    """
    Get Multi-Channel input data from Apify environment
    Supports Email, SipGate und WhatsApp data formats
    """
    debug_log("🔍 Environment Check - Run ID: {}, Token: {}".format(
        "SET" if APIFY_ACTOR_RUN_ID else "NOT_SET",
        "SET" if APIFY_TOKEN else "NOT_SET"
    ))
    
    # Try Apify API first
    if APIFY_TOKEN and APIFY_ACTOR_RUN_ID:
        debug_log("📞 Versuche Apify API Input...")
        try:
            url = f"https://api.apify.com/v2/actor-runs/{APIFY_ACTOR_RUN_ID}/input"
            headers = {'Authorization': f'Bearer {APIFY_TOKEN}'}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    debug_log(f"✅ Apify Input erfolgreich geladen: {list(data.keys())}")
                    return data
        except Exception as e:
            debug_log(f"❌ Fehler beim Input-Laden: {str(e)}")
    
    # Fallback zu stdin für lokale Tests
    debug_log("📋 Fallback zu stdin Input...")
    try:
        input_text = sys.stdin.read().strip()
        if input_text:
            return json.loads(input_text)
    except Exception as e:
        debug_log(f"⚠️ Stdin Input Fehler: {str(e)}")
    
    # Emergency fallback für Multi-Channel Testing
    debug_log("🚨 Emergency Multi-Channel Fallback Input")
    fallback_data = {
        "channel_type": "email",
        "message_id": f"fallback-multichannel-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "body_content": "Multi-Channel Fallback Test - Enhanced Actor v3.5",
        "subject": "Multi-Channel Integration Test",
        "from_email_address_address": "multichannel@example.com",
        "to_recipients_email_address_address": "info@cdtech.de",
        "source": "multichannel_fallback",
        "railway_integration": True,
        "enable_contact_matching": True,
        "enable_task_generation": True,
        "enable_unified_processing": True,
        "workflow_type": "enhanced_multichannel_processing"
    }
    return fallback_data

def push_data_to_apify(data: Dict[str, Any]) -> bool:
    """
    Push Multi-Channel processing results to Apify dataset
    """
    try:
        if not APIFY_TOKEN or not APIFY_DEFAULT_DATASET_ID:
            debug_log("⚠️ Apify credentials nicht verfügbar für Push")
            return False
            
        url = f"https://api.apify.com/v2/datasets/{APIFY_DEFAULT_DATASET_ID}/items"
        headers = {
            'Authorization': f'Bearer {APIFY_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            debug_log(f"✅ Multi-Channel Data erfolgreich gepusht: {response.status}")
            return True
            
    except Exception as e:
        debug_log(f"❌ Push Error: {str(e)}")
        return False

# ================================
# UNIFIED MULTI-CHANNEL PROCESSING PIPELINE
# ================================

async def process_unified_multichannel(context: MultiChannelContext) -> MultiChannelContext:
    """
    🚀 UNIFIED MULTI-CHANNEL PROCESSING PIPELINE
    Einheitliche Verarbeitung für Email, SipGate Calls und WhatsApp Messages
    mit gemeinsamer AI-Analyse und CRM Integration
    """
    
    debug_log(f"🚀 Starte Unified Multi-Channel Processing für: {context.channel_type}")
    
    # STEP 1: Railway LangGraph AI Processing (UNIFIED)
    debug_log("🤖 STEP 1: Railway Multi-Channel AI Integration...")
    railway_result = call_railway_multichannel_orchestrator(context)
    
    if railway_result["status"] == "success":
        debug_log(f"✅ Railway {context.channel_type} Integration erfolgreich")
        context.processing_results["railway_multichannel"] = railway_result["data"]
        
        # Extract unified AI results
        ai_data = railway_result["data"]
        context.processing_results["contact_match"] = ai_data.get("contact_match", {})
        context.processing_results["generated_tasks"] = ai_data.get("tasks_generated", [])
        context.processing_results["unified_analysis"] = ai_data.get("ai_analysis", {})
        
    else:
        debug_log(f"⚠️ Railway {context.channel_type} Integration fehlgeschlagen: {railway_result.get('error', 'Unknown error')}")
        debug_log("🔄 Fallback zur Channel-spezifischen Verarbeitung...")
    
    # STEP 2: Channel-specific Processing
    if context.channel_type == "email":
        context = await process_email_channel(context)
    elif context.channel_type == "phone_call":
        context = await process_sipgate_channel(context)
    elif context.channel_type == "whatsapp":
        context = await process_whatsapp_channel(context)
    
    # STEP 3: Unified Contact Processing (CRM Integration)
    debug_log("👥 STEP 3: Unified Contact Processing...")
    context = await process_unified_contacts(context)
    
    # STEP 4: Unified Task Management
    debug_log("📋 STEP 4: Unified Task Management...")
    context = await process_unified_tasks(context)
    
    # STEP 5: Multi-Channel Analytics
    debug_log("📊 STEP 5: Multi-Channel Analytics...")
    context = await analyze_multichannel_patterns(context)
    
    debug_log(f"✅ Unified Multi-Channel Processing completed: {context.channel_type}")
    return context

async def process_email_channel(context: MultiChannelContext) -> MultiChannelContext:
    """Email-specific Processing mit Integration der ursprünglichen E-Mail-Pipeline"""
    
    debug_log("📧 Processing Email Channel...")
    
    # Use existing email processing if available
    if FULL_EMAIL_PROCESSING_AVAILABLE and context.email_data:
        try:
            debug_log("🔧 Nutze vollständige E-Mail-Verarbeitung...")
            
            # Get Microsoft Graph tokens
            access_token_onedrive = get_graph_token_onedrive()
            access_token_mail = get_graph_token_mail()
            
            if access_token_onedrive and access_token_mail:
                debug_log("✅ Graph Tokens erfolgreich geholt")
                
                # Process attachments if available
                if context.attachments:
                    debug_log(f"📎 Verarbeite {len(context.attachments)} Anhänge...")
                    # Here we would integrate with existing attachment processing
                    context.processing_results["attachments_processed"] = len(context.attachments)
                
                # Integrate with existing email workflow components
                context.processing_results["email_processing"] = {
                    "tokens_obtained": True,
                    "attachments": len(context.attachments),
                    "processing_method": "full_email_pipeline"
                }
                
        except Exception as e:
            debug_log(f"⚠️ Vollständige E-Mail-Verarbeitung fehlgeschlagen: {str(e)}")
            context.processing_results["email_processing"] = {
                "error": str(e),
                "processing_method": "fallback_email"
            }
    
    return context

async def process_sipgate_channel(context: MultiChannelContext) -> MultiChannelContext:
    """SipGate Call-specific Processing"""
    
    debug_log("📞 Processing SipGate Channel...")
    
    if context.sipgate_data:
        call_data = context.sipgate_data
        
        # Process different call events
        call_event = call_data.get("event", "newCall")
        debug_log(f"📞 Processing SipGate Event: {call_event}")
        
        if call_event == "newCall":
            # Handle incoming call
            context.processing_results["sipgate_processing"] = {
                "event": "incoming_call",
                "caller": call_data.get("caller_number", ""),
                "called": call_data.get("called_number", ""),
                "direction": call_data.get("direction", "in"),
                "processing_method": "sipgate_webhook"
            }
            
        elif call_event == "answer":
            # Handle answered call
            context.processing_results["sipgate_processing"] = {
                "event": "call_answered",
                "duration_start": datetime.now().isoformat(),
                "sipgate_user": call_data.get("sipgate_user", ""),
                "processing_method": "sipgate_answer"
            }
            
        elif call_event == "hangup":
            # Handle ended call
            context.processing_results["sipgate_processing"] = {
                "event": "call_ended",
                "duration": call_data.get("duration", 0),
                "answered": call_data.get("answered", False),
                "transcription_available": bool(call_data.get("transcription")),
                "processing_method": "sipgate_hangup"
            }
            
            # Process call transcription if available
            if call_data.get("transcription"):
                debug_log("🎤 Verarbeite Call Transcription...")
                context.processing_results["call_transcript"] = {
                    "content": call_data["transcription"],
                    "duration": call_data.get("duration", 0),
                    "analysis_ready": True
                }
    
    return context

async def process_whatsapp_channel(context: MultiChannelContext) -> MultiChannelContext:
    """WhatsApp Message-specific Processing"""
    
    debug_log("💬 Processing WhatsApp Channel...")
    
    if context.whatsapp_data:
        wa_data = context.whatsapp_data
        
        # Process different message types
        msg_type = wa_data.get("message_type", "text")
        debug_log(f"💬 Processing WhatsApp Message Type: {msg_type}")
        
        if msg_type == "text":
            # Handle text message
            context.processing_results["whatsapp_processing"] = {
                "message_type": "text",
                "sender": wa_data.get("sender_name", ""),
                "phone": wa_data.get("sender_phone", ""),
                "text_content": wa_data.get("message_text", ""),
                "is_group": wa_data.get("is_group", False),
                "processing_method": "whatsapp_text"
            }
            
        elif msg_type in ["image", "document", "audio", "video"]:
            # Handle media message
            context.processing_results["whatsapp_processing"] = {
                "message_type": msg_type,
                "sender": wa_data.get("sender_name", ""),
                "phone": wa_data.get("sender_phone", ""),
                "media_url": wa_data.get("media_url", ""),
                "media_type": wa_data.get("media_type", ""),
                "has_text": bool(wa_data.get("message_text")),
                "processing_method": f"whatsapp_{msg_type}"
            }
            
            # Add media to unified attachments
            if wa_data.get("media_url"):
                media_attachment = {
                    "id": f"wa-media-{wa_data.get('message_id', '')}",
                    "name": f"whatsapp_media.{msg_type}",
                    "content_type": wa_data.get("media_type", f"image/{msg_type}"),
                    "download_url": wa_data.get("media_url", ""),
                    "channel": "whatsapp"
                }
                context.attachments.append(media_attachment)
                debug_log(f"📎 WhatsApp Media hinzugefügt: {msg_type}")
        
        # Group message handling
        if wa_data.get("is_group"):
            context.processing_results["whatsapp_group"] = {
                "group_name": wa_data.get("group_name", ""),
                "chat_id": wa_data.get("chat_id", ""),
                "is_group_admin": False,  # Would need additional data
                "processing_method": "whatsapp_group"
            }
    
    return context

async def process_unified_contacts(context: MultiChannelContext) -> MultiChannelContext:
    """Unified Contact Processing für alle Channels"""
    
    debug_log("👥 Unified Contact Processing...")
    
    unified_contact = context.get_unified_contact_info()
    
    # Integrate mit WeClapp CRM wenn verfügbar
    contact_result = {
        "unified_contact": unified_contact,
        "channel_source": context.channel_type,
        "crm_integration": "available" if context.contact_matching else "disabled",
        "processing_timestamp": datetime.now().isoformat()
    }
    
    # Add Railway contact matching results if available
    if context.processing_results.get("contact_match"):
        contact_result["railway_match"] = context.processing_results["contact_match"]
        debug_log("✅ Railway Contact Matching Daten integriert")
    
    context.processing_results["unified_contacts"] = contact_result
    return context

async def process_unified_tasks(context: MultiChannelContext) -> MultiChannelContext:
    """Unified Task Management für alle Channels"""
    
    debug_log("📋 Unified Task Management...")
    
    # Base task data
    task_data = {
        "channel_source": context.channel_type,
        "message_id": context.message_id,
        "contact_info": context.get_unified_contact_info(),
        "content_summary": context.subject or f"{context.channel_type} interaction",
        "processing_timestamp": datetime.now().isoformat(),
        "auto_generated": context.task_generation
    }
    
    # Add Railway-generated tasks if available
    if context.processing_results.get("generated_tasks"):
        task_data["railway_tasks"] = context.processing_results["generated_tasks"]
        debug_log(f"✅ Railway Generated Tasks: {len(context.processing_results['generated_tasks'])}")
    
    # Channel-specific task generation
    if context.channel_type == "phone_call" and context.sipgate_data:
        if context.sipgate_data.get("event") == "hangup" and not context.sipgate_data.get("answered"):
            task_data["auto_tasks"] = [{
                "title": f"Missed Call Follow-up: {context.sipgate_data.get('caller_number', '')}",
                "description": f"Rückruf für verpassten Anruf von {context.sipgate_data.get('caller_number', '')}",
                "priority": "high",
                "due_date": (datetime.now()).isoformat(),
                "task_type": "callback_required"
            }]
    
    elif context.channel_type == "whatsapp" and context.whatsapp_data:
        if context.whatsapp_data.get("message_type") in ["document", "image"]:
            task_data["auto_tasks"] = [{
                "title": f"WhatsApp Media Review: {context.whatsapp_data.get('sender_name', '')}",
                "description": f"Review WhatsApp {context.whatsapp_data.get('message_type')} from {context.whatsapp_data.get('sender_name', '')}",
                "priority": "medium",
                "due_date": (datetime.now()).isoformat(),
                "task_type": "media_review"
            }]
    
    context.processing_results["unified_tasks"] = task_data
    return context

async def analyze_multichannel_patterns(context: MultiChannelContext) -> MultiChannelContext:
    """Multi-Channel Analytics und Pattern Recognition"""
    
    debug_log("📊 Multi-Channel Analytics...")
    
    analytics_data = {
        "channel_type": context.channel_type,
        "processing_timestamp": datetime.now().isoformat(),
        "unified_processing": context.unified_processing,
        "railway_integration": context.railway_integration,
        "contact_matching": context.contact_matching,
        "task_generation": context.task_generation,
        "media_files": len(context.attachments),
        "processing_steps_completed": len([k for k, v in context.processing_results.items() if v]),
        "ai_analysis_available": bool(context.processing_results.get("unified_analysis")),
        "contact_match_available": bool(context.processing_results.get("contact_match")),
        "tasks_generated": len(context.processing_results.get("generated_tasks", [])),
        "processing_method": f"unified_multichannel_{context.channel_type}"
    }
    
    # Channel-specific analytics
    if context.channel_type == "email":
        analytics_data["email_metrics"] = {
            "has_attachments": len(context.attachments) > 0,
            "attachment_count": len(context.attachments),
            "full_processing_available": FULL_EMAIL_PROCESSING_AVAILABLE
        }
    
    elif context.channel_type == "phone_call" and context.sipgate_data:
        analytics_data["call_metrics"] = {
            "call_duration": context.sipgate_data.get("duration", 0),
            "call_answered": context.sipgate_data.get("answered", False),
            "has_transcription": bool(context.sipgate_data.get("transcription")),
            "call_direction": context.sipgate_data.get("direction", "unknown")
        }
    
    elif context.channel_type == "whatsapp" and context.whatsapp_data:
        analytics_data["whatsapp_metrics"] = {
            "message_type": context.whatsapp_data.get("message_type", "text"),
            "is_group_message": context.whatsapp_data.get("is_group", False),
            "has_media": bool(context.whatsapp_data.get("media_url")),
            "sender_phone": context.whatsapp_data.get("sender_phone", "")
        }
    
    context.processing_results["multichannel_analytics"] = analytics_data
    return context

# ================================
# SIPGATE WEBHOOK HANDLERS
# ================================

class SipGateEventHandler:
    """
    🏢 SIPGATE WEBHOOK EVENT HANDLER
    Spezifische Verarbeitung für verschiedene SipGate Call Events
    """
    
    @staticmethod
    def handle_new_call(context: MultiChannelContext) -> Dict[str, Any]:
        """Handle incoming SipGate newCall event"""
        debug_log("📞 SipGate: New Call Event")
        
        call_data = context.sipgate_data
        return {
            "event_type": "new_call",
            "caller_number": call_data.get("caller_number", ""),
            "called_number": call_data.get("called_number", ""),
            "direction": call_data.get("direction", "in"),
            "call_id": call_data.get("call_id", ""),
            "timestamp": datetime.now().isoformat(),
            "status": "ringing",
            "action_required": "answer_or_route"
        }
    
    @staticmethod
    def handle_call_answer(context: MultiChannelContext) -> Dict[str, Any]:
        """Handle SipGate call answer event"""
        debug_log("📞 SipGate: Call Answered")
        
        call_data = context.sipgate_data
        return {
            "event_type": "call_answered",
            "call_id": call_data.get("call_id", ""),
            "sipgate_user": call_data.get("sipgate_user", ""),
            "answer_timestamp": datetime.now().isoformat(),
            "status": "active",
            "recording_enabled": True,
            "transcription_enabled": True
        }
    
    @staticmethod
    def handle_call_hangup(context: MultiChannelContext) -> Dict[str, Any]:
        """Handle SipGate call hangup event"""
        debug_log("📞 SipGate: Call Ended")
        
        call_data = context.sipgate_data
        duration = call_data.get("duration", 0)
        answered = call_data.get("answered", False)
        
        result = {
            "event_type": "call_ended",
            "call_id": call_data.get("call_id", ""),
            "duration_seconds": duration,
            "answered": answered,
            "end_timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Add follow-up actions based on call outcome
        if not answered:
            result["follow_up"] = {
                "action": "missed_call_followup",
                "priority": "high",
                "suggested_response": "callback_required"
            }
        elif duration > 0 and call_data.get("transcription"):
            result["follow_up"] = {
                "action": "process_transcript", 
                "priority": "medium",
                "transcript_available": True,
                "content": call_data["transcription"]
            }
        
        return result
    
    @staticmethod
    def handle_dtmf_event(context: MultiChannelContext) -> Dict[str, Any]:
        """Handle SipGate DTMF (key press) event"""
        debug_log("📞 SipGate: DTMF Event")
        
        call_data = context.sipgate_data
        return {
            "event_type": "dtmf_received",
            "call_id": call_data.get("call_id", ""),
            "dtmf_input": call_data.get("dtmf", ""),
            "timestamp": datetime.now().isoformat(),
            "action_required": "process_menu_selection"
        }
    
    @staticmethod
    def process_call_context(context: MultiChannelContext) -> MultiChannelContext:
        """Comprehensive SipGate call processing"""
        
        if not context.sipgate_data:
            return context
            
        call_event = context.sipgate_data.get("event", "newCall")
        debug_log(f"📞 Processing SipGate Event: {call_event}")
        
        event_handlers = {
            "newCall": SipGateEventHandler.handle_new_call,
            "answer": SipGateEventHandler.handle_call_answer,
            "hangup": SipGateEventHandler.handle_call_hangup,
            "dtmf": SipGateEventHandler.handle_dtmf_event
        }
        
        if call_event in event_handlers:
            event_result = event_handlers[call_event](context)
            context.processing_results["sipgate_event"] = event_result
            
            # Add to unified content for AI processing
            if call_event == "hangup" and context.sipgate_data.get("transcription"):
                context.content = context.sipgate_data["transcription"]
                context.subject = f"Call Transcript - {context.sipgate_data.get('caller_number', '')}"
        
        return context

# ================================
# WHATSAPP MESSAGE HANDLERS
# ================================

class WhatsAppMessageHandler:
    """
    💬 WHATSAPP MESSAGE HANDLER
    Spezifische Verarbeitung für verschiedene WhatsApp Message Types
    """
    
    @staticmethod
    def handle_text_message(context: MultiChannelContext) -> Dict[str, Any]:
        """Handle WhatsApp text message"""
        debug_log("💬 WhatsApp: Text Message")
        
        wa_data = context.whatsapp_data
        return {
            "message_type": "text",
            "sender": wa_data.get("sender_name", ""),
            "sender_phone": wa_data.get("sender_phone", ""),
            "message_content": wa_data.get("message_text", ""),
            "char_count": len(wa_data.get("message_text", "")),
            "is_group": wa_data.get("is_group", False),
            "group_name": wa_data.get("group_name", "") if wa_data.get("is_group") else None,
            "timestamp": wa_data.get("timestamp", ""),
            "processing_ready": True
        }
    
    @staticmethod
    def handle_media_message(context: MultiChannelContext) -> Dict[str, Any]:
        """Handle WhatsApp media message (image, document, audio, video)"""
        wa_data = context.whatsapp_data
        media_type = wa_data.get("message_type", "image")
        
        debug_log(f"💬 WhatsApp: {media_type.title()} Message")
        
        result = {
            "message_type": media_type,
            "sender": wa_data.get("sender_name", ""),
            "sender_phone": wa_data.get("sender_phone", ""),
            "media_url": wa_data.get("media_url", ""),
            "media_type_mime": wa_data.get("media_type", ""),
            "has_caption": bool(wa_data.get("message_text")),
            "caption": wa_data.get("message_text", ""),
            "is_group": wa_data.get("is_group", False),
            "timestamp": wa_data.get("timestamp", ""),
            "download_required": bool(wa_data.get("media_url"))
        }
        
        # Media-specific processing
        if media_type == "document":
            result["document_processing"] = {
                "requires_ocr": True,
                "ai_analysis": True,
                "storage_required": True
            }
        elif media_type == "image":
            result["image_processing"] = {
                "requires_ocr": True,
                "ai_vision": True,
                "thumbnail_generation": True
            }
        elif media_type == "audio":
            result["audio_processing"] = {
                "requires_transcription": True,
                "speech_to_text": True,
                "duration_analysis": True
            }
        elif media_type == "video":
            result["video_processing"] = {
                "requires_thumbnail": True,
                "duration_analysis": True,
                "frame_extraction": False
            }
        
        return result
    
    @staticmethod
    def handle_location_message(context: MultiChannelContext) -> Dict[str, Any]:
        """Handle WhatsApp location message"""
        debug_log("💬 WhatsApp: Location Message")
        
        wa_data = context.whatsapp_data
        return {
            "message_type": "location",
            "sender": wa_data.get("sender_name", ""),
            "sender_phone": wa_data.get("sender_phone", ""),
            "location_data": "available",  # Would contain lat/lng in real implementation
            "address_lookup": "required",
            "timestamp": wa_data.get("timestamp", ""),
            "action_required": "location_processing"
        }
    
    @staticmethod
    def handle_contact_message(context: MultiChannelContext) -> Dict[str, Any]:
        """Handle WhatsApp contact sharing"""
        debug_log("💬 WhatsApp: Contact Message")
        
        wa_data = context.whatsapp_data
        return {
            "message_type": "contact",
            "sender": wa_data.get("sender_name", ""),
            "sender_phone": wa_data.get("sender_phone", ""),
            "shared_contact": "available",  # Would contain contact data
            "crm_integration": "required",
            "timestamp": wa_data.get("timestamp", ""),
            "action_required": "contact_import"
        }
    
    @staticmethod
    def process_whatsapp_context(context: MultiChannelContext) -> MultiChannelContext:
        """Comprehensive WhatsApp message processing"""
        
        if not context.whatsapp_data:
            return context
            
        msg_type = context.whatsapp_data.get("message_type", "text")
        debug_log(f"💬 Processing WhatsApp Message Type: {msg_type}")
        
        if msg_type == "text":
            result = WhatsAppMessageHandler.handle_text_message(context)
        elif msg_type in ["image", "document", "audio", "video"]:
            result = WhatsAppMessageHandler.handle_media_message(context)
        elif msg_type == "location":
            result = WhatsAppMessageHandler.handle_location_message(context)
        elif msg_type == "contact":
            result = WhatsAppMessageHandler.handle_contact_message(context)
        else:
            result = {"message_type": msg_type, "processing": "unsupported"}
        
        context.processing_results["whatsapp_message"] = result
        
        # Set unified content for AI processing
        if msg_type == "text":
            context.content = context.whatsapp_data.get("message_text", "")
            context.subject = f"WhatsApp von {context.whatsapp_data.get('sender_name', '')}"
        elif context.whatsapp_data.get("message_text"):  # Media with caption
            context.content = f"{msg_type.title()} Message: {context.whatsapp_data.get('message_text', '')}"
            context.subject = f"WhatsApp {msg_type.title()} von {context.whatsapp_data.get('sender_name', '')}"
        
        return context

# ================================
# MULTI-CHANNEL ZAPIER INTEGRATION
# ================================

def build_multichannel_zapier_payload(context: MultiChannelContext) -> Dict[str, Any]:
    """
    🔗 BUILD MULTI-CHANNEL ZAPIER PAYLOAD
    Erweiterte Zapier-Integration mit channel-spezifischen Daten
    """
    
    debug_log("🔗 Building Multi-Channel Zapier Payload...")
    
    # Base unified payload
    base_payload = {
        "actor_version": ACTOR_VERSION,
        "processing_timestamp": datetime.now().isoformat(),
        "channel_type": context.channel_type,
        "message_id": context.message_id,
        "source": context.source,
        
        # Unified contact information
        "contact": context.get_unified_contact_info(),
        
        # Unified content
        "content": context.get_unified_content(),
        
        # Processing results
        "processing_results": context.processing_results,
        
        # Railway AI results
        "ai_analysis": context.processing_results.get("unified_analysis", {}),
        "contact_match": context.processing_results.get("contact_match", {}),
        "generated_tasks": context.processing_results.get("generated_tasks", []),
        
        # Multi-channel features
        "unified_processing": context.unified_processing,
        "railway_integration": context.railway_integration,
        "attachments": context.attachments,
        "media_files_count": len(context.attachments)
    }
    
    # Add channel-specific data
    if context.channel_type == "email":
        base_payload["email_data"] = context.email_data or {}
        base_payload["email_processing"] = context.processing_results.get("email_processing", {})
        
    elif context.channel_type == "phone_call":
        base_payload["sipgate_data"] = context.sipgate_data or {}
        base_payload["call_event"] = context.processing_results.get("sipgate_event", {})
        base_payload["call_metrics"] = context.processing_results.get("multichannel_analytics", {}).get("call_metrics", {})
        
    elif context.channel_type == "whatsapp":
        base_payload["whatsapp_data"] = context.whatsapp_data or {}
        base_payload["whatsapp_message"] = context.processing_results.get("whatsapp_message", {})
        base_payload["whatsapp_metrics"] = context.processing_results.get("multichannel_analytics", {}).get("whatsapp_metrics", {})
    
    # Add analytics data
    base_payload["multichannel_analytics"] = context.processing_results.get("multichannel_analytics", {})
    
    # Legacy compatibility for existing Zapier workflows
    base_payload["legacy_compatibility"] = {
        "email_subject": context.subject,
        "email_body": context.content,
        "from_name": context.sender_name,
        "from_contact": context.sender_contact,
        "to_contact": context.recipient_contact
    }
    
    debug_log(f"🔗 Multi-Channel Zapier Payload created: {len(str(base_payload))} characters")
    return base_payload

def send_to_zapier_webhook(context: MultiChannelContext, payload: Dict[str, Any]) -> bool:
    """Send Multi-Channel data to Zapier webhook"""
    
    if not context.zapier_webhook:
        debug_log("⚠️ Keine Zapier Webhook URL konfiguriert")
        return False
    
    try:
        debug_log(f"🔗 Sende Multi-Channel Daten an Zapier: {context.zapier_webhook}")
        
        json_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            context.zapier_webhook,
            data=json_data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': f'Enhanced-MultiChannel-Actor-v{ACTOR_VERSION}',
                'X-Channel-Type': context.channel_type,
                'X-Message-ID': context.message_id
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            debug_log(f"✅ Zapier Multi-Channel Webhook erfolgreich: {response.status}")
            return True
            
    except Exception as e:
        debug_log(f"❌ Zapier Webhook Fehler: {str(e)}")
        return False

# ================================
# MAIN MULTI-CHANNEL PROCESSING FUNCTION
# ================================

def main():
    """
    🚀 MAIN MULTI-CHANNEL FUNCTION
    Enhanced Email Actor v3.5 - Unified Communication Hub
    Email + SipGate + WhatsApp + Railway LangGraph AI Integration
    """
    try:
        debug_log(f"🚀 Enhanced Multi-Channel Actor v{ACTOR_VERSION} startet...")
        debug_log(f"🔧 Railway Integration: {'Aktiviert' if RAILWAY_INTEGRATION else 'Deaktiviert'}")
        debug_log(f"📧 Vollständige E-Mail-Module: {'Verfügbar' if FULL_EMAIL_PROCESSING_AVAILABLE else 'Nicht verfügbar'}")
        debug_log(f"🔗 Orchestrator URL: {RAILWAY_ORCHESTRATOR_URL}")
        
        # Get Multi-Channel input data
        debug_log("📥 Lade Multi-Channel Input-Daten...")
        input_data = get_input_data()
        
        if not input_data:
            debug_log("❌ Keine Multi-Channel Eingabedaten verfügbar.")
            return
        
        debug_log(f"📋 Input Data Keys: {list(input_data.keys())}")
        
        # Create Multi-Channel context
        debug_log("🔧 Initialisiere Multi-Channel Processing Context...")
        context = MultiChannelContext(input_data)
        
        debug_log(f"📋 Multi-Channel Context: {context.channel_type} - ID: {context.message_id}")
        debug_log(f"👤 Contact: {context.sender_contact}")
        debug_log(f"📎 Attachments/Media: {len(context.attachments)}")
        
        # Channel-specific preprocessing
        if context.channel_type == "phone_call":
            context = SipGateEventHandler.process_call_context(context)
        elif context.channel_type == "whatsapp":
            context = WhatsAppMessageHandler.process_whatsapp_context(context)
        
        debug_log("🚀 Starte Unified Multi-Channel Processing...")
        
        # Run unified multi-channel processing
        context = asyncio.run(process_unified_multichannel(context))
        
        # Build Multi-Channel Zapier payload
        debug_log("🔗 Erstelle Multi-Channel Zapier Payload...")
        zapier_payload = build_multichannel_zapier_payload(context)
        
        # Send to Zapier webhook
        zapier_success = send_to_zapier_webhook(context, zapier_payload)
        
        # Push results to Apify dataset
        final_results = {
            "multichannel_processing": {
                "channel_type": context.channel_type,
                "message_id": context.message_id,
                "processing_timestamp": datetime.now().isoformat(),
                "unified_processing": context.unified_processing,
                "railway_integration": context.railway_integration,
                "processing_results": context.processing_results,
                "zapier_sent": zapier_success,
                "actor_version": ACTOR_VERSION
            },
            "contact_info": context.get_unified_contact_info(),
            "content_summary": context.get_unified_content(),
            "attachments_media": context.attachments,
            "analytics": context.processing_results.get("multichannel_analytics", {})
        }
        
        push_success = push_data_to_apify(final_results)
        
        # Summary
        debug_log("📊 **Multi-Channel Processing Ergebnisse:**")
        debug_log(f"   Channel Type: {context.channel_type}")
        debug_log(f"   Processing Method: unified_multichannel")
        debug_log(f"   Railway Integration: {'Aktiv' if context.railway_integration else 'Deaktiviert'}")
        debug_log(f"   Contact Matching: {'Ja' if context.contact_matching else 'Nein'}")
        debug_log(f"   Task Generation: {'Ja' if context.task_generation else 'Nein'}")
        debug_log(f"   Attachments/Media verarbeitet: {len(context.attachments)}")
        debug_log(f"   Zapier Webhook: {'Erfolgreich' if zapier_success else 'Fehlgeschlagen'}")
        debug_log(f"   Apify Dataset: {'Erfolgreich' if push_success else 'Fehlgeschlagen'}")
        
        # Channel-specific summary
        if context.channel_type == "phone_call" and context.sipgate_data:
            debug_log(f"   Call Duration: {context.sipgate_data.get('duration', 0)}s")
            debug_log(f"   Call Answered: {context.sipgate_data.get('answered', False)}")
        elif context.channel_type == "whatsapp" and context.whatsapp_data:
            debug_log(f"   Message Type: {context.whatsapp_data.get('message_type', 'text')}")
            debug_log(f"   Group Message: {context.whatsapp_data.get('is_group', False)}")
        elif context.channel_type == "email":
            debug_log(f"   Email Processing: {'Vollständig' if FULL_EMAIL_PROCESSING_AVAILABLE else 'Minimal'}")
        
        debug_log("✅ Multi-Channel Processing erfolgreich abgeschlossen")
        
    except Exception as e:
        debug_log(f"❌ Multi-Channel Processing Fehler: {str(e)}")
        debug_log(f"📋 Traceback: {traceback.format_exc()}")
        
        # Emergency fallback notification
        try:
            emergency_payload = {
                "error": "multi_channel_processing_failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
                "actor_version": ACTOR_VERSION,
                "processing_type": "emergency_fallback"
            }
            
            req = urllib.request.Request(
                ALERT_WEBHOOK_URL,
                data=json.dumps(emergency_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=10)
            debug_log("🚨 Emergency notification sent")
            
        except:
            debug_log("❌ Emergency notification failed")

# ================================
# MULTI-CHANNEL TEST FUNCTIONS
# ================================

def create_test_email_data() -> Dict[str, Any]:
    """Create test data for Email channel"""
    return {
        "channel_type": "email",
        "message_id": "test-email-multichannel-001",
        "body_content": "Hallo, ich hätte gerne ein Angebot für eine neue Website mit Multi-Channel Integration.",
        "subject": "Anfrage Website Entwicklung - Multi-Channel Test",
        "from_email_address_name": "Max Mustermann",
        "from_email_address_address": "max.mustermann@example.com",
        "to_recipients_email_address_address": "info@cdtech.de",
        "source": "email_test",
        "railway_integration": True,
        "enable_contact_matching": True,
        "enable_task_generation": True,
        "enable_unified_processing": True,
        "attachments": [
            {
                "id": "email-att-001",
                "name": "anfrage-details.pdf",
                "content_type": "application/pdf",
                "size": 234567,
                "channel": "email"
            }
        ]
    }

def create_test_sipgate_data() -> Dict[str, Any]:
    """Create test data for SipGate phone call"""
    return {
        "channel_type": "phone_call",
        "message_id": "test-sipgate-multichannel-001",
        "body_content": "Call transcript: Kunde möchte Rückruf für Website-Projekt.",
        "subject": "Incoming Call - Website Anfrage",
        "from_email_address_name": "Maria Beispiel",
        "from_email_address_address": "+49 30 12345678",
        "to_recipients_email_address_address": "+49 30 87654321",
        "source": "sipgate",
        "sipgate_call_data": {
            "call_id": "sipgate-test-call-001",
            "event": "hangup",
            "direction": "in",
            "from": "+49 30 12345678",
            "to": "+49 30 87654321",
            "user": "test@cdtech.de",
            "duration": 125,
            "answered": True,
            "transcription": "Guten Tag, ich rufe wegen der Website-Entwicklung an. Können Sie mich zurückrufen?"
        },
        "railway_integration": True,
        "enable_contact_matching": True,
        "enable_task_generation": True,
        "enable_unified_processing": True
    }

def create_test_whatsapp_data() -> Dict[str, Any]:
    """Create test data for WhatsApp message"""
    return {
        "channel_type": "whatsapp",
        "message_id": "test-whatsapp-multichannel-001",
        "body_content": "WhatsApp Nachricht mit Dokument-Anhang für Projekt-Anfrage.",
        "subject": "WhatsApp Message mit Dokument",
        "from_email_address_name": "Anna Schmidt",
        "from_email_address_address": "+49 175 1234567",
        "to_recipients_email_address_address": "+49 175 7654321",
        "source": "whatsapp",
        "whatsapp_message_data": {
            "message_id": "wa-msg-test-001",
            "chat_id": "wa-chat-test-001",
            "message_type": "document",
            "sender_phone": "+49 175 1234567",
            "sender_name": "Anna Schmidt",
            "message_text": "Hier ist das Projektdokument für die Website-Entwicklung",
            "media_url": "https://test.example.com/whatsapp/document.pdf",
            "media_type": "application/pdf",
            "timestamp": datetime.now().isoformat(),
            "is_group": False
        },
        "attachments": [
            {
                "id": "wa-doc-001",
                "name": "projekt-dokument.pdf",
                "content_type": "application/pdf",
                "size": 345678,
                "download_url": "https://test.example.com/whatsapp/document.pdf",
                "channel": "whatsapp"
            }
        ],
        "railway_integration": True,
        "enable_contact_matching": True,
        "enable_task_generation": True,
        "enable_unified_processing": True
    }

def test_multichannel_processing():
    """Test all Multi-Channel processing capabilities"""
    debug_log("🧪 Starting Multi-Channel Processing Tests...")
    
    test_cases = [
        ("Email", create_test_email_data()),
        ("SipGate", create_test_sipgate_data()),
        ("WhatsApp", create_test_whatsapp_data())
    ]
    
    for channel_name, test_data in test_cases:
        debug_log(f"🧪 Testing {channel_name} Channel...")
        try:
            context = MultiChannelContext(test_data)
            
            if context.channel_type == "phone_call":
                context = SipGateEventHandler.process_call_context(context)
            elif context.channel_type == "whatsapp":
                context = WhatsAppMessageHandler.process_whatsapp_context(context)
            
            # Test Railway integration
            railway_result = call_railway_multichannel_orchestrator(context)
            debug_log(f"✅ {channel_name} Railway Test: {railway_result['status']}")
            
            # Test Zapier payload
            zapier_payload = build_multichannel_zapier_payload(context)
            debug_log(f"✅ {channel_name} Zapier Payload: {len(str(zapier_payload))} chars")
            
        except Exception as e:
            debug_log(f"❌ {channel_name} Test Failed: {str(e)}")
    
    debug_log("🧪 Multi-Channel Tests completed")

if __name__ == "__main__":
    debug_log(f"🔧 Starte Enhanced Multi-Channel Actor v{ACTOR_VERSION}...")
    
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_multichannel_processing()
    else:
        main()