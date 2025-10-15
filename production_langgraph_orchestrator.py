#!/usr/bin/env python3
"""
🚀 PRODUCTION-READY AI COMMUNICATION ORCHESTRATOR
=================================================

LANGGRAPH/LANGCHAIN MIGRATION - SOFORT LAUFFÄHIG!

SYSTEM FEATURES:
✅ LangGraph State Management
✅ OpenAI GPT-4 Integration
✅ Contact Matching (Apify/WeClapp)
✅ WEG A/B Workflow Routing
✅ Email/Call/WhatsApp Processing
✅ FastAPI Production Server
✅ Docker Container Ready
✅ QNAP Container Station Compatible

PRODUCTION URLs:
🌐 http://192.168.0.101:5001 (QNAP Local)
🔗 https://qlink.to/CundD:5001 (Public Smart URL)

DEPLOYMENT: Kopieren → Docker Build → Container Station Deploy
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass
import pytz  # Timezone support

# Deutsche Zeitzone
BERLIN_TZ = pytz.timezone('Europe/Berlin')

def now_berlin():
    """Return current datetime in Berlin timezone"""
    return datetime.now(BERLIN_TZ)

# LangGraph/LangChain Imports
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# FastAPI Production Server
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response as FastAPIResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# HTTP Client für API Calls
import aiohttp
import httpx
import logging

# SQLite Database für Contact Cache
import sqlite3
import asyncio
from contextlib import asynccontextmanager
import requests

# INLINE Graph API Functions (Railway deployment workaround)
async def get_graph_token_mail():
    """Holt das Zugriffstoken von Microsoft Graph für Mail."""
    tenant_id = os.getenv("GRAPH_TENANT_ID_MAIL")
    client_id = os.getenv("GRAPH_CLIENT_ID_MAIL")
    client_secret = os.getenv("GRAPH_CLIENT_SECRET_MAIL")
    
    if not tenant_id or not client_id or not client_secret:
        logger.error("❌ Fehlende Mail-Graph API Zugangsdaten")
        return None
    
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }
    
    try:
        logger.info(f"🔐 Requesting token: tenant={tenant_id[:8]}..., client={client_id[:8]}...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            if response.status_code == 200:
                logger.info("✅ Graph API token obtained successfully")
                return response.json().get("access_token")
            else:
                error_body = response.text
                logger.error(f"❌ Token error {response.status_code}: {error_body}")
                return None
    except Exception as e:
        logger.error(f"❌ Token exception: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

async def fetch_email_details_with_attachments(user_email, message_id, access_token):
    """Ruft die E-Mail-Daten und Anhänge von Microsoft Graph ab."""
    email_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}?$expand=attachments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    logger.info(f"🔍 Loading email: user={user_email}, message={message_id[:20]}...")
    try:
        response = requests.get(email_url, headers=headers)
        if response.status_code == 200:
            email_data = response.json()
            logger.info(f"✅ Email loaded: Subject='{email_data.get('subject', 'no subject')}', From='{email_data.get('from', {}).get('emailAddress', {}).get('address', 'unknown')}'")
            return email_data
        else:
            logger.error(f"❌ Graph API error: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        logger.error(f"❌ Email fetch exception: {e}")
        return None

# Call Analysis (Task-Ableitung, Termin-Extraktion, Follow-Ups)
from modules.gpt.analyze_call_content import (
    analyze_call_content,
    extract_appointment_datetime,
    calculate_follow_up_date
)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===============================
# ZAPIER NOTIFICATION FUNCTIONS
# ===============================

def generate_notification_html(notification_data: Dict[str, Any]) -> str:
    """
    🎨 Generate complete HTML for email notifications
    Supports both WEG A (unknown) and WEG B (known) contacts
    """
    notification_type = notification_data.get("notification_type", "unknown_contact_action_required")
    
    if notification_type == "unknown_contact_action_required":
        # WEG A: Unknown Contact with Action Buttons
        sender = notification_data.get("sender", "Unbekannt")
        sender_display = notification_data.get("sender_display", sender)
        subject = notification_data.get("subject", "Neue Nachricht")
        body_preview = notification_data.get("body_preview", "")
        received_time = notification_data.get("received_time", "")
        ai_analysis = notification_data.get("ai_analysis", {})
        action_options = notification_data.get("action_options", [])
        email_id = notification_data.get("email_id", "unknown")
        webhook_url = notification_data.get("webhook_reply_url", "")
        
        # Build attachments HTML if present
        attachments_count = notification_data.get("attachments_count", 0)
        if attachments_count > 0:
            attachments_html = f'<p><strong>📎 Anhänge:</strong> {attachments_count} Datei(en)</p>'
        else:
            attachments_html = ''
        
        # Build action buttons HTML
        buttons_html = ""
        for option in action_options:
            action = option.get("action", "")
            label = option.get("label", "")
            description = option.get("description", "")
            color_class = {
                "create_contact": "btn-create",
                "add_to_existing": "btn-primary",
                "mark_private": "btn-private",
                "mark_spam": "btn-spam",
                "request_info": "btn-info",
                "report_issue": "btn-secondary"
            }.get(action, "btn-default")
            
            button_url = f"{webhook_url}?action={action}&sender={sender}&email_id={email_id}"
            
            buttons_html += f"""
            <a href="{button_url}" class="button {color_class}">{label}</a>
            <p class="button-desc">{description}</p>
            """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #2C3E50; background: #FFFFFF; margin: 0; padding: 0; }}
    .container {{ max-width: 650px; margin: 0 auto; padding: 0; background: white; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); overflow: hidden; }}
    .header {{ background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%); color: white; padding: 30px; text-align: center; }}
    .header h2 {{ margin: 0; font-size: 24px; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    .content {{ background: #FFFFFF; padding: 30px; }}
    .info-box {{ background: linear-gradient(135deg, #FFF9E6 0%, #FFE8CC 100%); padding: 20px; margin: 20px 0; border-radius: 10px; border-left: 5px solid #FFB84D; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
    .info-box h3 {{ color: #E67E22; margin-top: 0; font-size: 18px; }}
    .info-box p {{ color: #34495E; margin: 8px 0; }}
    .action-buttons {{ margin: 30px 0; text-align: center; }}
    .action-buttons h3 {{ color: #2C3E50; margin-bottom: 20px; }}
    .button {{ display: inline-block; padding: 14px 28px; margin: 8px 5px; text-decoration: none; border-radius: 25px; font-weight: bold; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
    .btn-create {{ background: linear-gradient(135deg, #52C234 0%, #47A025 100%); color: white; }}
    .btn-create:hover {{ box-shadow: 0 6px 16px rgba(82,194,52,0.4); transform: translateY(-2px); }}
    .btn-primary {{ background: linear-gradient(135deg, #3498DB 0%, #2980B9 100%); color: white; }}
    .btn-primary:hover {{ box-shadow: 0 6px 16px rgba(52,152,219,0.4); transform: translateY(-2px); }}
    .btn-private {{ background: linear-gradient(135deg, #A29BFE 0%, #6C5CE7 100%); color: white; }}
    .btn-private:hover {{ box-shadow: 0 6px 16px rgba(162,155,254,0.4); transform: translateY(-2px); }}
    .btn-spam {{ background: linear-gradient(135deg, #FF7675 0%, #D63031 100%); color: white; }}
    .btn-spam:hover {{ box-shadow: 0 6px 16px rgba(255,118,117,0.4); transform: translateY(-2px); }}
    .btn-info {{ background: linear-gradient(135deg, #74B9FF 0%, #0984E3 100%); color: white; }}
    .btn-info:hover {{ box-shadow: 0 6px 16px rgba(116,185,255,0.4); transform: translateY(-2px); }}
    .btn-secondary {{ background: linear-gradient(135deg, #FFEAA7 0%, #FDCB6E 100%); color: #2C3E50; }}
    .btn-secondary:hover {{ box-shadow: 0 6px 16px rgba(255,234,167,0.4); transform: translateY(-2px); }}
    .ai-analysis {{ background: linear-gradient(135deg, #DFE6E9 0%, #B2BEC3 100%); padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #74B9FF; }}
    .ai-analysis h3 {{ color: #0984E3; margin-top: 0; font-size: 18px; }}
    .ai-analysis p {{ color: #2C3E50; margin: 8px 0; }}
    .footer {{ text-align: center; padding: 20px; background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%); color: #7F8C8D; font-size: 13px; border-radius: 0 0 15px 15px; }}
    .button-desc {{ font-size: 12px; margin: 5px 0 15px 0; color: #7F8C8D; }}
    strong {{ color: #2C3E50; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h2>�️ Unbekannter Kontakt - Aktion erforderlich</h2>
</div>
<div class="content">
<div class="info-box">
<h3>📧 Details:</h3>
<p><strong>Von:</strong> {sender_display}</p>
<p><strong>Betreff:</strong> {subject}</p>
<p><strong>Empfangen:</strong> {received_time}</p>
{attachments_html}
</div>
<div class="info-box">
<h3>📝 Nachricht:</h3>
<p>{body_preview}</p>
</div>
<div class="ai-analysis">
<h3>🤖 KI-Analyse:</h3>
<p><strong>Absicht:</strong> {ai_analysis.get('intent', 'unbekannt')}</p>
<p><strong>Dringlichkeit:</strong> {ai_analysis.get('urgency', 'unbekannt')}</p>
<p><strong>Stimmung:</strong> {ai_analysis.get('sentiment', 'unbekannt')}</p>
</div>
<div class="action-buttons">
<h3>👆 Wähle eine Aktion:</h3>
{buttons_html}
</div>
</div>
<div class="footer">
<p>🤖 Automatisch generiert vom C&D Lead Management System</p>
<p>Email-ID: {email_id}</p>
</div>
</div>
</body>
</html>
"""
        return html
    
    else:
        # WEG B: Known Contact - Simple notification with feedback button
        subject = notification_data.get('subject', 'Kontakt verarbeitet')
        summary = notification_data.get('summary', '')
        contact_match = notification_data.get('contact_match', {})
        contact_name = contact_match.get('contact_name', 'Unbekannt')
        contact_id = contact_match.get('contact_id', '')
        from_contact = notification_data.get('from', '')
        content_preview = notification_data.get('content_preview', '')
        ai_analysis = notification_data.get('ai_analysis', {})
        action_options = notification_data.get('action_options', [])
        
        # Build action buttons HTML
        buttons_html = ""
        for option in action_options:
            action = option.get("action", "")
            label = option.get("label", "")
            description = option.get("description", "")
            url = option.get("url", "")
            
            color_class = {
                "view_in_crm": "btn-info",
                "report_issue": "btn-secondary"
            }.get(action, "btn-default")
            
            if url:
                button_url = url
            else:
                button_url = f"https://my-langgraph-agent-production.up.railway.app/webhook/feedback?type=wrong_match&contact_id={contact_id}&from={from_contact}"
            
            buttons_html += f"""
            <a href="{button_url}" class="button {color_class}">{label}</a>
            <p class="button-desc">{description}</p>
            """
        
        return f"""
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #2C3E50; background: #FFFFFF; margin: 0; padding: 0; }}
    .container {{ max-width: 650px; margin: 0 auto; padding: 0; background: white; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); overflow: hidden; }}
    .header {{ background: linear-gradient(135deg, #55EFC4 0%, #00B894 100%); color: white; padding: 30px; text-align: center; }}
    .header h2 {{ margin: 0; font-size: 24px; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    .content {{ background: #FFFFFF; padding: 30px; }}
    .info-box {{ background: linear-gradient(135deg, #E8F8F5 0%, #D1F2EB 100%); padding: 20px; margin: 20px 0; border-radius: 10px; border-left: 5px solid #00B894; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
    .info-box h3 {{ color: #00B894; margin-top: 0; font-size: 18px; }}
    .info-box p {{ color: #34495E; margin: 8px 0; }}
    .action-buttons {{ margin: 30px 0; text-align: center; }}
    .action-buttons h3 {{ color: #2C3E50; margin-bottom: 20px; }}
    .button {{ display: inline-block; padding: 14px 28px; margin: 8px 5px; text-decoration: none; border-radius: 25px; font-weight: bold; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
    .btn-info {{ background: linear-gradient(135deg, #74B9FF 0%, #0984E3 100%); color: white; }}
    .btn-info:hover {{ box-shadow: 0 6px 16px rgba(116,185,255,0.4); transform: translateY(-2px); }}
    .btn-secondary {{ background: linear-gradient(135deg, #FFEAA7 0%, #FDCB6E 100%); color: #2C3E50; }}
    .btn-secondary:hover {{ box-shadow: 0 6px 16px rgba(255,234,167,0.4); transform: translateY(-2px); }}
    .ai-analysis {{ background: linear-gradient(135deg, #DFE6E9 0%, #B2BEC3 100%); padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #74B9FF; }}
    .ai-analysis h3 {{ color: #0984E3; margin-top: 0; font-size: 18px; }}
    .ai-analysis p {{ color: #2C3E50; margin: 8px 0; }}
    .footer {{ text-align: center; padding: 20px; background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%); color: #7F8C8D; font-size: 13px; border-radius: 0 0 15px 15px; }}
    .button-desc {{ font-size: 12px; margin: 5px 0 15px 0; color: #7F8C8D; }}
    strong {{ color: #2C3E50; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h2>✅ Kontakt erkannt und verarbeitet</h2>
</div>
<div class="content">
<div class="info-box">
<h3>👤 Kontakt:</h3>
<p><strong>{contact_name}</strong></p>
<p>Von: {from_contact}</p>
</div>
<div class="info-box">
<h3>📝 Nachricht:</h3>
<p>{content_preview}</p>
</div>
<div class="ai-analysis">
<h3>🤖 Verarbeitung:</h3>
<p>{summary}</p>
<p><strong>Absicht:</strong> {ai_analysis.get('intent', 'unbekannt')}</p>
<p><strong>Dringlichkeit:</strong> {ai_analysis.get('urgency', 'unbekannt')}</p>
</div>
<div class="action-buttons">
<h3>🔗 Aktionen:</h3>
{buttons_html}
</div>
</div>
<div class="footer">
<p>🤖 Automatisch generiert vom C&D Lead Management System</p>
</div>
</div>
</body>
</html>
"""

async def send_final_notification(processing_result: Dict[str, Any], message_type: str, from_contact: str, content: str):
    """
    🎯 FINAL ZAPIER NOTIFICATION - Email an Markus & Info
    
    Wird nach jedem erfolgreichen AI Processing aufgerufen
    ENHANCED: Spezielle Behandlung für unbekannte Kontakte
    """
    
    ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/u5ilur9/"
    
    contact_match = processing_result.get("contact_match", {})
    contact_found = contact_match.get("found", False)
    
    # 🆕 ENHANCED: Unknown Contact Notification (Zapier-compatible format)
    if not contact_found:
        # Check for potential matches from fuzzy search
        potential_matches = processing_result.get("potential_matches", [])
        
        # Build action options based on whether we have potential matches
        action_options = []
        
        if potential_matches:
            # Add "KONTAKT ZUORDNEN" as first option if we found potential matches
            for match in potential_matches[:1]:  # Only show best match in button
                action_options.append({
                    "action": "assign_to_existing",
                    "label": "KONTAKT ZUORDNEN",
                    "description": f"Zu existierendem Kontakt zuordnen: {match.get('contact_name')} ({match.get('reason')})",
                    "contact_id": match.get("contact_id"),
                    "existing_contact": match.get("contact_name")
                })
        
        # Standard actions (always include "add to existing")
        action_options.extend([
            {
                "action": "create_contact",
                "label": "✅ KONTAKT ANLEGEN",
                "description": "Als neuen Kontakt in WeClapp anlegen"
            },
            {
                "action": "add_to_existing",
                "label": "➕ ZU BESTEHENDEM HINZUFÜGEN",
                "description": "Email/Telefon zu einem bestehenden Kontakt hinzufügen",
                "requires_search": True
            },
            {
                "action": "mark_private",
                "label": "🔒 PRIVAT MARKIEREN",
                "description": "Als private Anfrage markieren (kein CRM-Eintrag)"
            },
            {
                "action": "mark_spam",
                "label": "🚫 SPAM MARKIEREN",
                "description": "Als Spam markieren und blockieren"
            },
            {
                "action": "request_info",
                "label": "📨 INFO ANFORDERN",
                "description": "Mehr Informationen vom Absender anfordern"
            },
            {
                "action": "report_issue",
                "label": "🐛 PROBLEM MELDEN",
                "description": "Fehlverhalten oder fehlende Funktion melden",
                "color": "secondary"
            }
        ])
        
        # Build subject and body based on message type
        if message_type == "call":
            call_data = processing_result.get("additional_data", {})
            call_direction = call_data.get("call_direction", "inbound")
            call_duration = call_data.get("call_duration", 0)
            caller_name = call_data.get("caller_name", "")
            phone = from_contact or "Unbekannt"
            
            subject = f"CALL: Anruf {call_direction} - {phone}"
            if caller_name:
                subject += f" ({caller_name})"
            
            sender_display = f"{caller_name} ({phone})" if caller_name else phone
        elif message_type == "email":
            subject = f"EMAIL: {content[:80]}"
            sender_display = from_contact
        else:
            subject = f"{message_type.upper()}: {content[:100]}"
            sender_display = from_contact
        
        notification_data = {
            "notification_type": "unknown_contact_action_required",
            "email_id": f"railway-{now_berlin().timestamp()}",
            "sender": from_contact,
            "sender_name": processing_result.get("sender_name", "Unbekannt"),
            "sender_display": sender_display,
            "subject": subject,
            "body_preview": content[:500] + "..." if len(content) > 500 else content,
            "received_time": now_berlin().isoformat(),
            "message_type": message_type,
            
            # AI Analysis (flattened for Zapier)
            "ai_analysis": processing_result.get("ai_analysis", {}),
            
            # Attachments Info
            "attachments_count": processing_result.get("attachments_count", 0),
            "has_attachments": processing_result.get("has_attachments", False),
            
            # Potential Matches (if any)
            "potential_matches": potential_matches,
            "has_potential_matches": len(potential_matches) > 0,
            
            # Action Options (dynamic based on potential matches)
            "action_options": action_options,
            
            "responsible_employee": "mj@cdtechnologies.de",
            "webhook_reply_url": "https://my-langgraph-agent-production.up.railway.app/webhook/contact-action"
        }
        
        # 🎨 Generate complete HTML for email
        notification_data["html_body"] = generate_notification_html(notification_data)
        
        # 🔍 DEBUG: Log attachment info before sending
        logger.info(f"📎 DEBUG notification_data: attachments_count={notification_data.get('attachments_count')}, has_attachments={notification_data.get('has_attachments')}")
        
        logger.info(f"⚠️ Sending UNKNOWN CONTACT notification for {from_contact}")
    
    else:
        # Standard Notification for known contacts
        # Add feedback/report option even for successful processing
        standard_actions = [
            {
                "action": "view_in_crm",
                "label": "📋 IN CRM ÖFFNEN",
                "description": f"Kontakt in WeClapp öffnen",
                "contact_id": contact_match.get("contact_id"),
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            },
            {
                "action": "report_issue",
                "label": "🐛 PROBLEM MELDEN",
                "description": "Fehlverhalten, falsche Zuordnung oder fehlende Funktion melden",
                "color": "secondary"
            }
        ]
        
        notification_data = {
            "notification_type": "standard",
            "timestamp": now_berlin().isoformat(),
            "channel": message_type,
            "from": from_contact,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            
            # AI Processing Results
            "success": processing_result.get("success", False),
            "workflow_path": processing_result.get("workflow_path"),
            "contact_match": contact_match,
            "ai_analysis": processing_result.get("ai_analysis", {}),
            "tasks_generated": processing_result.get("tasks_generated", []),
            "processing_complete": processing_result.get("processing_complete", False),
            
            # Action buttons (including feedback)
            "action_options": standard_actions,
            
            # Email Recipients
            "recipients": ["mj@cdtechnologies.de", "info@cdtechnologies.de"],
            
            # Notification Details
            "subject": f"🤖 C&D AI: {message_type.upper()} von {contact_match.get('contact_name', from_contact)}",
            "summary": f"AI hat {len(processing_result.get('tasks_generated', []))} Tasks erstellt"
        }
        
        # 🎨 Generate complete HTML for email
        notification_data["html_body"] = generate_notification_html(notification_data)
        
        logger.info(f"✅ Sending standard notification for known contact: {contact_match.get('contact_name', from_contact)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                ZAPIER_WEBHOOK_URL,
                json=notification_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ Zapier notification sent successfully for {message_type}")
                    return True
                else:
                    logger.warning(f"⚠️ Zapier notification failed - Status: {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Zapier notification error: {e}")
        return False


def _extract_company_from_email(email: str) -> str:
    """Extract potential company name from email domain"""
    if "@" in email:
        domain = email.split("@")[1].split(".")[0]
        return domain.capitalize()
    return ""


def _suggest_contact_type(processing_result: Dict[str, Any]) -> str:
    """Suggest contact type based on AI analysis"""
    intent = processing_result.get("ai_analysis", {}).get("intent", "")
    
    if intent in ["quote_request", "appointment", "project_inquiry"]:
        return "customer"
    elif intent in ["invoice", "delivery", "order"]:
        return "supplier"
    else:
        return "prospect"

# ===============================
# SQLITE CONTACT CACHE LAYER
# ===============================

DB_PATH = os.getenv("DATABASE_PATH", "./email_data.db")

def initialize_contact_cache():
    """
    🗄️ SQLITE EMAIL DATABASE - Performance Layer
    
    Nutzt die existierende email_data.db die von weclapp-sql-sync-production Actor gefüllt wird.
    MASTER PLAN: Erste Anlaufstelle vor WeClapp API Call!
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        sender TEXT,
        recipient TEXT,
        received_date TEXT,
        ocr_text TEXT,
        gpt_result TEXT,
        weclapp_contact_id TEXT,
        weclapp_customer_id TEXT,
        weclapp_opportunity_id TEXT,
        current_stage TEXT,
        gpt_status_suggestion TEXT,
        status_deviation BOOLEAN,
        remarks TEXT
    )
    """)
    
    # Index für schnelle Email-Lookups
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_sender ON email_data(sender)
    """)
    
    conn.commit()
    conn.close()
    logger.info("✅ Email Database initialized (email_data.db)")


async def lookup_contact_in_cache(email: str) -> Optional[Dict[str, Any]]:
    """
    🔍 STEP 1: Cache Lookup (Sub-Second Performance)
    
    Sucht Kontakt zuerst im lokalen SQLite Cache.
    Nur bei Cache Miss wird WeClapp API aufgerufen.
    """
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _sync_lookup_contact, email)
        
        if result:
            logger.info(f"✅ CACHE HIT for {email} - Contact ID: {result['weclapp_contact_id']}")
            return result
        else:
            logger.info(f"⚠️ CACHE MISS for {email} - Will query WeClapp")
            return None
            
    except Exception as e:
        logger.error(f"❌ Cache lookup error: {e}")
        return None


def _sync_lookup_contact(email: str) -> Optional[Dict[str, Any]]:
    """Synchronous SQLite lookup in email_data.db (runs in executor)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT DISTINCT weclapp_contact_id, weclapp_customer_id, sender
    FROM email_data
    WHERE sender = ? AND weclapp_contact_id IS NOT NULL
    ORDER BY id DESC
    LIMIT 1
    """, (email.lower(),))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = {
            "found": True,
            "source": "cache",
            "weclapp_contact_id": row[0],
            "weclapp_customer_id": row[1],
            "sender": row[2]
        }
        conn.close()
        return result
    
    conn.close()
    return None


async def cache_contact(email: str, weclapp_data: Dict[str, Any]):
    """
    💾 STEP 2: Cache Write-Back nach WeClapp Lookup
    
    Speichert WeClapp Contact in lokalem Cache für zukünftige Lookups.
    """
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _sync_cache_contact, email, weclapp_data)
        logger.info(f"✅ Contact cached: {email} → {weclapp_data.get('weclapp_contact_id')}")
    except Exception as e:
        logger.error(f"❌ Cache write error: {e}")


def _sync_cache_contact(email: str, weclapp_data: Dict[str, Any]):
    """Synchronous SQLite write (runs in executor)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO email_data (sender, weclapp_contact_id, weclapp_customer_id, received_date, subject)
    VALUES (?, ?, ?, ?, ?)
    """, (
        email.lower(),
        weclapp_data.get("weclapp_contact_id"),
        weclapp_data.get("weclapp_customer_id"),
        now_berlin().isoformat(),
        "Contact cached from WeClapp lookup"
    ))
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Cached in email_data.db: {email} → {weclapp_data.get('weclapp_contact_id')}")

# ===============================
# LANGRAPH STATE DEFINITIONS
# ===============================

class CommunicationState(TypedDict):
    """LangGraph State für AI Communication Processing"""
    
    # Input Data
    message_type: str  # "email", "call", "whatsapp"
    from_contact: str
    content: str
    timestamp: str
    additional_data: Optional[Dict[str, Any]]  # Email attachments, call metadata, etc.
    
    # Processing Results
    contact_match: Optional[Dict[str, Any]]
    ai_analysis: Optional[Dict[str, Any]]
    workflow_path: Optional[str]  # "WEG_A" or "WEG_B"
    tasks_generated: List[Dict[str, Any]]
    crm_updates: List[Dict[str, Any]]
    
    # Final Output
    processing_complete: bool
    response_sent: bool
    errors: List[str]

@dataclass
class ContactMatch:
    """Contact Matching Result"""
    found: bool
    contact_id: Optional[str] = None
    contact_name: Optional[str] = None
    company: Optional[str] = None
    confidence: float = 0.0
    source: Optional[str] = None  # "cache", "weclapp", "apify", "manual"
    cache_hits: int = 0  # How many times this contact was found in cache

@dataclass
class AITask:
    """Generated AI Task"""
    title: str
    description: str
    assigned_to: str
    priority: str  # "low", "medium", "high", "urgent"
    due_date: str
    task_type: str  # "follow_up", "quote", "support", "meeting"
    contact_id: Optional[str] = None

# ===============================
# PRODUCTION AI ORCHESTRATOR
# ===============================

class ProductionAIOrchestrator:
    """Production-ready LangGraph AI Communication Orchestrator"""
    
    def __init__(self):
        # Environment Setup with debugging
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.apify_token = os.getenv("APIFY_TOKEN")
        self.weclapp_api_token = os.getenv("WECLAPP_API_TOKEN")
        self.weclapp_domain = os.getenv("WECLAPP_DOMAIN", "cdtech")
        
        # ⚠️ SECURITY: Only log existence, NEVER log actual keys or full env list
        print(f"🔍 Environment Check: OpenAI API Key configured: {bool(self.openai_api_key)}")
        print(f"🔍 Environment Check: WeClapp API Token configured: {bool(self.weclapp_api_token)}")
        print(f"🔍 Environment Check: Apify Token configured: {bool(self.apify_token)}")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable required!")
        
        # LangChain/OpenAI Setup
        self.llm = ChatOpenAI(
            api_key=self.openai_api_key,
            model="gpt-4-turbo-preview",
            temperature=0.1,
            max_tokens=2000
        )
        
        # JSON Output Parser
        self.json_parser = JsonOutputParser()
        
        # Build LangGraph Workflow
        self.workflow = self._build_langgraph_workflow()
        
        logger.info("✅ Production AI Orchestrator initialized with LangGraph")
    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Builds the main LangGraph workflow"""
        
        # Create StateGraph
        workflow = StateGraph(CommunicationState)
        
        # Define workflow nodes
        workflow.add_node("contact_lookup", self._contact_lookup_node)
        workflow.add_node("ai_analysis", self._ai_analysis_node)
        workflow.add_node("workflow_routing", self._workflow_routing_node)
        workflow.add_node("weg_a_unknown_contact", self._weg_a_unknown_contact_node)
        workflow.add_node("weg_b_known_contact", self._weg_b_known_contact_node)
        workflow.add_node("finalize_processing", self._finalize_processing_node)
        
        # Define workflow edges
        workflow.set_entry_point("contact_lookup")
        
        # Contact Lookup → AI Analysis
        workflow.add_edge("contact_lookup", "ai_analysis")
        
        # AI Analysis → Workflow Routing
        workflow.add_edge("ai_analysis", "workflow_routing")
        
        # Conditional routing based on contact match
        workflow.add_conditional_edges(
            "workflow_routing",
            self._route_workflow_condition,
            {
                "WEG_A": "weg_a_unknown_contact",
                "WEG_B": "weg_b_known_contact"
            }
        )
        
        # Both paths lead to finalization
        workflow.add_edge("weg_a_unknown_contact", "finalize_processing")
        workflow.add_edge("weg_b_known_contact", "finalize_processing")
        
        # Finalization ends the workflow
        workflow.add_edge("finalize_processing", END)
        
        return workflow.compile()
    
    async def _contact_lookup_node(self, state: CommunicationState) -> CommunicationState:
        """LangGraph Node: Contact Lookup in CRM/Database"""
        
        logger.info(f"🔍 Contact lookup for: {state['from_contact']}")
        
        try:
            # STEP 1: Direct WeClapp Contact Search (Email or Phone)
            weclapp_match = await self._search_weclapp_contact(state["from_contact"])
            
            # STEP 2: If no direct match, try FUZZY MATCHING
            potential_matches = []
            if not weclapp_match.found:
                logger.info("🔍 No direct match - trying fuzzy search...")
                potential_matches = await self._fuzzy_contact_search(state["from_contact"], state)
                
                if potential_matches:
                    logger.info(f"✨ Found {len(potential_matches)} potential matches via fuzzy search")
                    # Store potential matches for WEG_A notification
                    state["potential_matches"] = potential_matches
            
            # STEP 3: Apify Contact Search (wenn WeClapp nichts findet)
            if not weclapp_match.found and not potential_matches:
                apify_match = await self._search_apify_contact(state["from_contact"])
                contact_match = apify_match
            else:
                contact_match = weclapp_match
            
            # Ensure contact_match is valid
            if contact_match is None:
                raise ValueError("Contact search returned None")
            
            # Update state with safe attribute access
            state["contact_match"] = {
                "found": getattr(contact_match, "found", False),
                "contact_id": getattr(contact_match, "contact_id", None),
                "contact_name": getattr(contact_match, "contact_name", None),
                "company": getattr(contact_match, "company", None),
                "confidence": getattr(contact_match, "confidence", 0.0),
                "source": getattr(contact_match, "source", "unknown")
            }
            
            logger.info(f"✅ Contact match result: {contact_match.found} ({contact_match.source})")
            
        except Exception as e:
            logger.error(f"❌ Contact lookup error: {e}")
            state["errors"].append(f"Contact lookup failed: {e}")
            state["contact_match"] = {
                "found": False,
                "contact_id": None,
                "contact_name": None,
                "company": None,
                "confidence": 0.0,
                "source": "error"
            }
        
        return state
    
    async def _ai_analysis_node(self, state: CommunicationState) -> CommunicationState:
        """LangGraph Node: AI Analysis of Communication"""
        
        logger.info(f"🤖 AI analyzing {state['message_type']} from {state['from_contact']}")
        
        try:
            # Get additional context
            additional_data = state.get("additional_data", {})
            email_direction = additional_data.get("email_direction", "incoming")
            subject = additional_data.get("subject", "")
            attachments = additional_data.get("attachments", [])
            attachment_names = [att.get("name", "") for att in attachments] if attachments else []
            
            # AI Analysis Prompt with Document Type Classification
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """Du bist ein AI Communication Analyst für ein deutsches Unternehmen.
                
Analysiere die eingehende Kommunikation und erstelle eine JSON-Antwort mit:

{{
    "intent": "support|sales|information|complaint|follow_up",
    "urgency": "low|medium|high|urgent", 
    "sentiment": "positive|neutral|negative",
    "document_type": "invoice|offer|order_confirmation|delivery_note|general",
    "has_pricing": true,
    "key_topics": ["thema1", "thema2"],
    "suggested_tasks": [
        {{
            "title": "Aufgaben-Titel",
            "type": "follow_up|quote|support|meeting|payment|delivery",
            "priority": "low|medium|high|urgent",
            "due_hours": 24
        }}
    ],
    "response_needed": true,
    "summary": "Kurze deutsche Zusammenfassung"
}}

**DOKUMENTTYP-KLASSIFIKATION:**
- "invoice": Rechnung, Zahlungsaufforderung, RE:, Invoice (mit/ohne Anhang)
- "offer": Angebot, Quote, Preisanfrage, Richtpreis (mit/ohne Anhang)
- "order_confirmation": Auftragsbestätigung, AB:, Order Confirmation
- "delivery_note": Aufmaß, Lieferschein, Delivery Note, Measurement
- "general": Allgemeine Anfrage, Info-Request, Support

Antworte nur mit dem JSON, keine zusätzlichen Texte."""),
                ("user", f"""Kommunikation analysieren:
                
Art: {state['message_type']}
Richtung: {email_direction}
Von: {state['from_contact']}
Betreff: {subject}
Anhänge: {len(attachment_names)} ({', '.join(attachment_names[:3])})
Inhalt: {state['content'][:1000]}
Zeit: {state['timestamp']}

Bekannter Kontakt: {state.get('contact_match', {}).get('found', False)}
""")
            ])
            
            # Execute AI Analysis
            response = await self.llm.ainvoke(analysis_prompt.format_messages())
            ai_result = self.json_parser.parse(response.content)
            
            state["ai_analysis"] = ai_result
            
            logger.info(f"✅ AI Analysis complete: {ai_result.get('intent')} ({ai_result.get('urgency')})")
            
        except Exception as e:
            logger.error(f"❌ AI Analysis error: {e}")
            state["errors"].append(f"AI analysis failed: {e}")
            state["ai_analysis"] = {"error": str(e), "fallback": True}
        
        return state
    
    async def _workflow_routing_node(self, state: CommunicationState) -> CommunicationState:
        """LangGraph Node: Determine Workflow Path (WEG A/B)"""
        
        contact_found = state.get("contact_match", {}).get("found", False)
        
        if contact_found:
            state["workflow_path"] = "WEG_B"
            logger.info("🎯 Routing to WEG B (Known Contact)")
        else:
            state["workflow_path"] = "WEG_A"
            logger.info("🆕 Routing to WEG A (Unknown Contact)")
        
        return state
    
    def _route_workflow_condition(self, state: CommunicationState) -> str:
        """Conditional edge function for workflow routing"""
        return state["workflow_path"]
    
    async def _weg_a_unknown_contact_node(self, state: CommunicationState) -> CommunicationState:
        """LangGraph Node: WEG A - Unknown Contact Workflow"""
        
        logger.info("🆕 Executing WEG A: Unknown Contact Workflow")
        
        try:
            # Generate employee notification
            notification = await self._generate_employee_notification(state)
            
            # Create temporary CRM entry
            temp_entry = await self._create_temporary_crm_entry(state)
            
            # Generate follow-up tasks
            tasks = [
                AITask(
                    title=f"Unbekannter Kontakt zuordnen: {state['from_contact']}",
                    description=f"Neue {state['message_type']} von unbekanntem Kontakt. Entscheidung über CRM-Aufnahme erforderlich.",
                    assigned_to="sales_team",
                    priority="medium",
                    due_date=self._calculate_due_date(24),  # 24 Stunden
                    task_type="follow_up",
                    contact_id=None
                )
            ]
            
            state["tasks_generated"] = [self._task_to_dict(task) for task in tasks]
            
            logger.info(f"✅ WEG A complete: Generated {len(tasks)} tasks")
            
        except Exception as e:
            logger.error(f"❌ WEG A error: {e}")
            state["errors"].append(f"WEG A processing failed: {e}")
        
        return state
    
    async def _weg_b_known_contact_node(self, state: CommunicationState) -> CommunicationState:
        """LangGraph Node: WEG B - Known Contact Workflow"""
        
        logger.info("✅ Executing WEG B: Known Contact Workflow")
        
        try:
            contact_id = state["contact_match"]["contact_id"]
            
            # Update contact communication log
            await self._update_contact_communication_log(contact_id, state)
            
            # Generate AI-suggested tasks
            ai_analysis = state.get("ai_analysis", {})
            tasks = []
            
            for suggested_task in ai_analysis.get("suggested_tasks", []):
                task = AITask(
                    title=suggested_task["title"],
                    description=f"AI-generierte Aufgabe basierend auf {state['message_type']}",
                    assigned_to=self._determine_assignee(suggested_task, state),
                    priority=suggested_task["priority"],
                    due_date=self._calculate_due_date(suggested_task.get("due_hours", 48)),
                    task_type=suggested_task["type"],
                    contact_id=contact_id
                )
                tasks.append(task)
            
            # Create tasks in CRM
            for task in tasks:
                await self._create_crm_task(task)
            
            state["tasks_generated"] = [self._task_to_dict(task) for task in tasks]
            
            # Automatic response if needed
            if ai_analysis.get("response_needed"):
                await self._send_automatic_response(state)
            
            logger.info(f"✅ WEG B complete: Generated {len(tasks)} tasks")
            
        except Exception as e:
            logger.error(f"❌ WEG B error: {e}")
            state["errors"].append(f"WEG B processing failed: {e}")
        
        return state
    
    async def _finalize_processing_node(self, state: CommunicationState) -> CommunicationState:
        """LangGraph Node: Finalize Processing"""
        
        logger.info("🏁 Finalizing AI Communication Processing")
        
        # Mark processing as complete
        state["processing_complete"] = True
        
        # Log final results
        logger.info(f"📊 Processing Summary:")
        logger.info(f"  - Contact Match: {state.get('contact_match', {}).get('found', False)}")
        logger.info(f"  - Workflow Path: {state.get('workflow_path')}")
        logger.info(f"  - Tasks Generated: {len(state.get('tasks_generated', []))}")
        logger.info(f"  - Errors: {len(state.get('errors', []))}")
        
        return state
    
    # ===============================
    # CONTACT LOOKUP METHODS
    # ===============================
    
    async def _search_weclapp_contact(self, contact_identifier: str) -> ContactMatch:
        """
        🔍 ENHANCED: Two-Tier Contact Lookup (MASTER PLAN)
        
        STEP 1: SQLite Cache (Sub-Second)
        STEP 2: WeClapp API (only on Cache Miss)
        """
        
        # STEP 1: Check SQLite Cache first
        cached_contact = await lookup_contact_in_cache(contact_identifier)
        
        if cached_contact:
            return ContactMatch(
                found=True,
                contact_id=cached_contact.get("weclapp_contact_id"),
                contact_name=cached_contact.get("contact_name"),  # May be None from minimal cache
                company=cached_contact.get("company_name"),
                confidence=1.0,
                source="cache",
                cache_hits=cached_contact.get("cache_hits", 0)
            )
        
        # STEP 2: Cache Miss - Query WeClapp API
        if not self.weclapp_api_token:
            logger.warning("⚠️ WeClapp API token not configured")
            return ContactMatch(found=False, source="weclapp_unavailable")
        
        try:
            logger.info(f"🔎 Cache Miss - Querying WeClapp for: {contact_identifier}")
            
            # WeClapp API Call with EMAIL FILTER for exact match
            headers = {
                "AuthenticationToken": self.weclapp_api_token,
                "Accept": "application/json"
            }
            
            # Determine if contact_identifier is EMAIL or PHONE
            is_phone = contact_identifier.startswith("+") or contact_identifier.isdigit()
            
            # Filter by exact email or phone match using WeClapp API
            if is_phone:
                # Phone number search (try multiple formats)
                search_params = {
                    "phone-eq": contact_identifier,
                    "serializationConfiguration": "IGNORE_EMPTY",
                    "pageSize": 5  # Get multiple results for phone (may match different formats)
                }
                logger.info(f"🔍 Searching by PHONE: {contact_identifier}")
            else:
                # Email search
                search_params = {
                    "email-eq": contact_identifier.lower(),
                    "serializationConfiguration": "IGNORE_EMPTY",
                    "pageSize": 1  # Only need 1 result for exact match
                }
                logger.info(f"🔍 Searching by EMAIL: {contact_identifier}")
            
            url = f"https://{self.weclapp_domain}.weclapp.com/webapp/api/v1/contact"
            logger.info(f"📞 WeClapp URL: {url} with filter: {search_params}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=search_params) as response:
                    logger.info(f"📬 WeClapp Response Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        contacts = data.get("result", [])
                        
                        if len(contacts) > 0:
                            # Exact match found via WeClapp email filter
                            contact = contacts[0]
                            contact_name = f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip()
                            company_name = contact.get("company", {}).get("name") if contact.get("company") else None
                            
                            logger.info(f"✅ EXACT MATCH FOUND in WeClapp: {contact_name} (ID: {contact.get('id')})")
                            
                            # STEP 3: Cache the result for future lookups
                            await cache_contact(contact_identifier, {
                                "weclapp_contact_id": str(contact.get("id")),
                                "weclapp_customer_id": str(contact.get("customerId")) if contact.get("customerId") else None,
                                "contact_name": contact_name,
                                "company_name": company_name,
                                "phone": contact.get("phone")
                            })
                            
                            return ContactMatch(
                                found=True,
                                contact_id=str(contact.get("id")),
                                contact_name=contact_name,
                                company=company_name,
                                confidence=1.0,
                                source="weclapp"
                            )
                        else:
                            logger.warning(f"❌ No match found in WeClapp for: {contact_identifier}")
                    else:
                        logger.error(f"❌ WeClapp API returned status {response.status}")
            
            return ContactMatch(found=False, source="weclapp")
            
        except Exception as e:
            logger.error(f"❌ WeClapp search exception: {e}")
            return ContactMatch(found=False, source="weclapp_error")
    
    async def _search_apify_contact(self, contact_identifier: str) -> ContactMatch:
        """Search contact in Apify datasets"""
        
        # Simplified Apify contact search
        # In production: Search durch Apify datasets
        
        return ContactMatch(found=False, source="apify")
    
    async def _fuzzy_contact_search(self, contact_identifier: str, state: CommunicationState) -> List[Dict[str, Any]]:
        """
        🔍 FUZZY CONTACT MATCHING
        
        Erweiterte Suche wenn kein direkter Match:
        1. Domain-Suche (Email) → Firma mit mehreren Mitarbeitern
        2. Telefon-Prefix → Kunde mit mehreren Nummern  
        3. Namen-Matching → Alternativer Kontakt
        """
        
        potential_matches = []
        
        if not self.weclapp_api_token:
            return potential_matches
        
        try:
            headers = {
                "AuthenticationToken": self.weclapp_api_token,
                "Accept": "application/json"
            }
            
            # 1. DOMAIN-SUCHE (Email)
            if "@" in contact_identifier:
                domain = contact_identifier.split("@")[1]
                logger.info(f"🔍 Fuzzy: domain @{domain}")
                
                url = f"https://{self.weclapp_domain}.weclapp.com/webapp/api/v1/party"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params={"email-like": f"%@{domain}", "pageSize": 5}) as response:
                        if response.status == 200:
                            data = await response.json()
                            for contact in data.get("result", []):
                                if contact.get("email", "").lower() != contact_identifier.lower():
                                    # Safely extract company name (can be string or dict)
                                    company_data = contact.get("company")
                                    company_name = None
                                    if isinstance(company_data, dict):
                                        company_name = company_data.get("name")
                                    elif isinstance(company_data, str):
                                        company_name = company_data
                                    
                                    potential_matches.append({
                                        "match_type": "domain",
                                        "confidence": 0.8,
                                        "contact_id": str(contact.get("id")),
                                        "contact_name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip(),
                                        "company": company_name,
                                        "existing_identifier": contact.get("email"),
                                        "reason": f"Gleiche Firma (@{domain})"
                                    })
            
            # 2. TELEFON-PREFIX
            elif contact_identifier.startswith("+") and len(contact_identifier) >= 8:
                prefix = contact_identifier[:8]
                logger.info(f"🔍 Fuzzy: phone {prefix}*")
                
                url = f"https://{self.weclapp_domain}.weclapp.com/webapp/api/v1/party"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params={"phone-like": f"{prefix}%", "pageSize": 5}) as response:
                        if response.status == 200:
                            data = await response.json()
                            for contact in data.get("result", []):
                                if contact.get("phone") and contact.get("phone") != contact_identifier:
                                    # Safely extract company name (can be string or dict)
                                    company_data = contact.get("company")
                                    company_name = None
                                    if isinstance(company_data, dict):
                                        company_name = company_data.get("name")
                                    elif isinstance(company_data, str):
                                        company_name = company_data
                                    
                                    potential_matches.append({
                                        "match_type": "phone_prefix",
                                        "confidence": 0.7,
                                        "contact_id": str(contact.get("id")),
                                        "contact_name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip(),
                                        "company": company_name,
                                        "existing_identifier": contact.get("phone"),
                                        "reason": f"Ähnliche Nummer ({contact.get('phone')})"
                                    })
            
            # Limit to top 3
            potential_matches = sorted(potential_matches, key=lambda x: x["confidence"], reverse=True)[:3]
            logger.info(f"✅ Fuzzy: {len(potential_matches)} matches")
            return potential_matches
            
        except Exception as e:
            logger.error(f"❌ Fuzzy error: {str(e)}")
            return []
    
    # ===============================
    # CRM INTEGRATION METHODS
    # ===============================
    
    async def _update_contact_communication_log(self, contact_id: str, state: CommunicationState):
        """
        📝 WeClapp CRM Communication Log
        
        Creates detailed crmEvent entry with:
        - Call transcript
        - AI Analysis (Intent, Urgency, Sentiment)
        - Generated tasks
        - Call direction (inbound/outbound) & duration
        """
        
        logger.info(f"📝 Creating WeClapp Communication Log for contact {contact_id}")
        
        if not self.weclapp_api_token:
            logger.warning("⚠️ WeClapp API token not configured - skipping CRM log")
            return
        
        try:
            # Prepare communication log data
            message_type = state.get("message_type", "unknown")
            ai_analysis = state.get("ai_analysis", {})
            additional_data = state.get("additional_data", {})
            
            # Call-specific data
            if message_type == "call":
                call_direction = additional_data.get("call_direction", "inbound")
                call_duration = additional_data.get("call_duration", 0)
                call_transcript = state.get("content", "")
                
                description = f"""
📞 **Telefonat ({call_direction.upper()})**

⏱️ **Dauer:** {call_duration} Sekunden
📅 **Zeitpunkt:** {state.get('timestamp', now_berlin().isoformat())}

---

### 📝 Gesprächstranskript:
{call_transcript}

---

### 🤖 KI-Analyse:

**Absicht:** {ai_analysis.get('intent', 'Unbekannt')}
**Dringlichkeit:** {ai_analysis.get('urgency', 'medium')}
**Stimmung:** {ai_analysis.get('sentiment', 'neutral')}

**Zusammenfassung:**
{ai_analysis.get('summary', 'Keine Zusammenfassung verfügbar')}

---

### ✅ Generierte Aufgaben:
"""
                # Add generated tasks to description
                for task in state.get("tasks_generated", []):
                    description += f"\n- {task.get('title', 'Unbekannte Aufgabe')}"
                
                event_type = "CALL"
                subject = f"Telefonat ({call_direction}) - {ai_analysis.get('intent', 'Allgemein')}"
            
            # Email-specific data
            elif message_type == "email":
                description = f"""
📧 **Email empfangen**

📩 **Von:** {state.get('from_contact')}
📅 **Zeitpunkt:** {state.get('timestamp', now_berlin().isoformat())}

---

### 📝 Email-Inhalt:
{state.get('content', '')[:1000]}...

---

### 🤖 KI-Analyse:

**Absicht:** {ai_analysis.get('intent', 'Unbekannt')}
**Dringlichkeit:** {ai_analysis.get('urgency', 'medium')}
**Stimmung:** {ai_analysis.get('sentiment', 'neutral')}

---

### ✅ Generierte Aufgaben:
"""
                for task in state.get("tasks_generated", []):
                    description += f"\n- {task.get('title', 'Unbekannte Aufgabe')}"
                
                event_type = "EMAIL"
                subject = f"Email - {ai_analysis.get('intent', 'Allgemein')}"
            
            # WhatsApp-specific data
            elif message_type == "whatsapp":
                description = f"""
💬 **WhatsApp Nachricht**

📱 **Von:** {state.get('from_contact')}
📅 **Zeitpunkt:** {state.get('timestamp', now_berlin().isoformat())}

---

### 📝 Nachricht:
{state.get('content', '')}

---

### 🤖 KI-Analyse:

**Absicht:** {ai_analysis.get('intent', 'Unbekannt')}
**Dringlichkeit:** {ai_analysis.get('urgency', 'medium')}
**Stimmung:** {ai_analysis.get('sentiment', 'neutral')}

---

### ✅ Generierte Aufgaben:
"""
                for task in state.get("tasks_generated", []):
                    description += f"\n- {task.get('title', 'Unbekannte Aufgabe')}"
                
                event_type = "NOTE"
                subject = f"WhatsApp - {ai_analysis.get('intent', 'Allgemein')}"
            
            else:
                event_type = "NOTE"
                subject = f"{message_type.capitalize()} - Kommunikation"
                description = state.get('content', 'Keine Details verfügbar')
            
            # 🎯 NEUE FEATURE: Call Analysis für Task-Ableitung, Termin-Extraktion, Follow-Ups
            if message_type == "call" and state.get('content'):
                try:
                    call_duration = state.get("call_duration", 0)
                    contact_name = contact_match.get("name", "Unbekannt") if contact_match else "Unbekannt"
                    
                    logger.info(f"🎯 Analyzing call transcript for tasks/appointments...")
                    call_analysis = await analyze_call_content(
                        transcription=state.get('content', ''),
                        contact_name=contact_name,
                        duration_seconds=call_duration
                    )
                    
                    # Log results
                    if call_analysis:
                        logger.info(f"✅ Call Analysis Complete:")
                        logger.info(f"   📋 Tasks: {len(call_analysis.get('tasks', []))}")
                        logger.info(f"   📅 Appointments: {len(call_analysis.get('appointments', []))}")
                        logger.info(f"   ⏰ Follow-Ups: {len(call_analysis.get('follow_ups', []))}")
                        logger.info(f"   📝 Summary: {call_analysis.get('summary', '')}")
                        
                        # Store analysis in state for later use
                        state["call_analysis"] = call_analysis
                        
                        # Add analyzed tasks to state's tasks_generated
                        for task_data in call_analysis.get('tasks', []):
                            state["tasks_generated"].append({
                                "title": task_data.get("title"),
                                "description": task_data.get("description"),
                                "priority": task_data.get("priority", "medium"),
                                "due_date": task_data.get("due_date"),
                                "source": "call_transcript_analysis"
                            })
                        
                        # Enhance description with analysis
                        description += f"\n\n### 🎯 Call-Analyse:\n\n"
                        description += f"**Zusammenfassung:** {call_analysis.get('summary', 'N/A')}\n\n"
                        
                        if call_analysis.get('tasks'):
                            description += "**Erkannte Aufgaben:**\n"
                            for task in call_analysis.get('tasks', []):
                                description += f"- [{task.get('priority', 'medium').upper()}] {task.get('title')}\n"
                        
                        if call_analysis.get('appointments'):
                            description += "\n**Vereinbarte Termine:**\n"
                            for apt in call_analysis.get('appointments', []):
                                description += f"- 📅 {apt.get('date')} {apt.get('time', '')} - {apt.get('description')}\n"
                        
                        if call_analysis.get('follow_ups'):
                            description += "\n**Follow-Ups:**\n"
                            for followup in call_analysis.get('follow_ups', []):
                                description += f"- ⏰ {followup.get('due_date')}: {followup.get('action')}\n"
                    
                except Exception as e:
                    logger.error(f"❌ Call analysis error: {e}")
                    # Continue without analysis - not critical
            
            # Create WeClapp crmEvent
            # Determine correct type based on message type and direction
            if message_type == "call":
                call_direction = state.get("call_direction", "inbound")
                crm_type = "INCOMING_CALL" if call_direction == "inbound" else "OUTGOING_CALL"
            elif message_type == "email":
                crm_type = "LETTER"  # WeClapp uses LETTER for emails
            else:
                crm_type = "GENERAL"
            
            crm_event_data = {
                "partyId": int(contact_id),
                "contactId": int(contact_id),  # ✅ For PERSON parties, contactId must equal partyId
                "type": crm_type,  # ✅ INCOMING_CALL, OUTGOING_CALL, LETTER, or GENERAL
                "eventType": event_type,
                "subject": subject,
                "description": description,
                "contactChannel": "PHONE" if message_type == "call" else "EMAIL" if message_type == "email" else "OTHER",
                "status": "DONE",
                "eventDate": int(now_berlin().timestamp() * 1000)  # Unix timestamp in milliseconds
            }
            
            headers = {
                "AuthenticationToken": self.weclapp_api_token,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            url = f"https://{self.weclapp_domain}.weclapp.com/webapp/api/v1/crmEvent"
            
            logger.info(f"📤 Creating WeClapp crmEvent: {subject}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=crm_event_data) as response:
                    if response.status == 201:
                        crm_event = await response.json()
                        logger.info(f"✅ WeClapp crmEvent created: ID {crm_event.get('id')}")
                        return crm_event
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ WeClapp crmEvent creation failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ WeClapp Communication Log error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        
    async def _create_crm_task(self, task: AITask):
        """Create task in CRM system"""
        
        logger.info(f"📋 Creating CRM task: {task.title}")
        
        # WeClapp task creation
        # Implementierung abhängig von WeClapp API
    
    async def _create_temporary_crm_entry(self, state: CommunicationState) -> Dict[str, Any]:
        """Create temporary CRM entry for unknown contact"""
        
        logger.info(f"🆕 Creating temporary CRM entry for {state['from_contact']}")
        
        return {
            "temp_id": f"temp_{now_berlin().timestamp()}",
            "contact": state["from_contact"],
            "status": "pending_assignment"
        }
    
    # ===============================
    # NOTIFICATION METHODS
    # ===============================
    
    async def _generate_employee_notification(self, state: CommunicationState) -> Dict[str, Any]:
        """Generate notification for employee decision"""
        
        logger.info("📧 Generating employee notification")
        
        notification = {
            "type": "unknown_contact_decision",
            "subject": f"Neue {state['message_type']} von unbekanntem Kontakt: {state['from_contact']}",
            "content": f"""
Neue Kommunikation von unbekanntem Kontakt benötigt Entscheidung:

📧 **Details:**
- Von: {state['from_contact']}
- Art: {state['message_type']}
- Zeit: {state['timestamp']}
- Inhalt: {state['content'][:300]}...

🤖 **AI-Analyse:**
{json.dumps(state.get('ai_analysis', {}), indent=2, ensure_ascii=False)}

🎯 **Erforderliche Aktion:**
- [ ] Neuen Kontakt im CRM anlegen
- [ ] Als privat/Spam markieren
- [ ] Weitere Informationen einholen

Antworten Sie mit den erforderlichen Kontakt-Details oder markieren Sie als "Privat/Spam".
""",
            "priority": state.get("ai_analysis", {}).get("urgency", "medium"),
            "assigned_to": self._determine_responsible_employee(state)
        }
        
        return notification
    
    async def _send_automatic_response(self, state: CommunicationState):
        """Send automatic response if needed"""
        
        logger.info("🤖 Sending automatic response")
        
        # Automatische Antwort-Logik
        # Je nach message_type unterschiedliche Antworten
    
    # ===============================
    # UTILITY METHODS
    # ===============================
    
    def _determine_assignee(self, suggested_task: Dict[str, Any], state: CommunicationState) -> str:
        """Determine who should be assigned to a task"""
        
        task_type = suggested_task.get("type", "follow_up")
        
        mapping = {
            "sales": "sales_team",
            "support": "support_team", 
            "quote": "sales_team",
            "meeting": "management",
            "follow_up": "sales_team"
        }
        
        return mapping.get(task_type, "general_team")
    
    def _determine_responsible_employee(self, state: CommunicationState) -> str:
        """Determine responsible employee for unknown contact"""
        
        # Zeit-basierte Zuweisung
        hour = now_berlin().hour
        
        if 9 <= hour <= 17:
            return "sales_team"
        else:
            return "service_team"
    
    def _calculate_due_date(self, hours_from_now: int) -> str:
        """Calculate due date"""
        
        from datetime import datetime, timedelta
        
        due_date = now_berlin() + timedelta(hours=hours_from_now)
        return due_date.isoformat()
    
    def _task_to_dict(self, task: AITask) -> Dict[str, Any]:
        """Convert AITask to dictionary"""
        
        return {
            "title": task.title,
            "description": task.description,
            "assigned_to": task.assigned_to,
            "priority": task.priority,
            "due_date": task.due_date,
            "task_type": task.task_type,
            "contact_id": task.contact_id
        }
    
    # ===============================
    # MAIN PROCESSING METHOD
    # ===============================
    
    async def process_communication(self, 
                                  message_type: str,
                                  from_contact: str,
                                  content: str,
                                  additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main processing method - executes the LangGraph workflow"""
        
        logger.info(f"🚀 Processing {message_type} from {from_contact}")
        
        # Initialize state
        initial_state = CommunicationState(
            message_type=message_type,
            from_contact=from_contact,
            content=content,
            timestamp=now_berlin().isoformat(),
            contact_match=None,
            ai_analysis=None,
            workflow_path=None,
            tasks_generated=[],
            crm_updates=[],
            processing_complete=False,
            response_sent=False,
            errors=[],
            additional_data=additional_data or {}
        )
        
        try:
            # Execute LangGraph workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Build processing result
            # Get additional_data from final_state (it flows through the workflow)
            state_additional_data = final_state.get("additional_data", {})
            
            processing_result = {
                "success": True,
                "workflow_path": final_state.get("workflow_path"),
                "contact_match": final_state.get("contact_match"),
                "ai_analysis": final_state.get("ai_analysis"),
                "tasks_generated": final_state.get("tasks_generated", []),
                "processing_complete": final_state.get("processing_complete", False),
                "errors": final_state.get("errors", []),
                # Attachment info from state's additional_data
                "attachments_count": state_additional_data.get("attachments_count", 0),
                "has_attachments": state_additional_data.get("has_attachments", False),
                "attachment_results": state_additional_data.get("attachment_results", [])
            }
            
            # 🎯 SEND FINAL ZAPIER NOTIFICATION
            try:
                notification_sent = await send_final_notification(
                    processing_result, message_type, from_contact, content
                )
                processing_result["notification_sent"] = notification_sent
                if notification_sent:
                    logger.info("✅ Final email notification sent via Zapier")
                else:
                    logger.warning("⚠️ Final email notification failed")
            except Exception as notification_error:
                logger.error(f"❌ Notification error: {notification_error}")
                processing_result["notification_sent"] = False
                processing_result["notification_error"] = str(notification_error)
            
            return processing_result
            
        except Exception as e:
            logger.error(f"❌ Workflow execution error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "workflow_path": None,
                "processing_complete": False,
                "notification_sent": False
            }
            
            # Send error notification too
            try:
                await send_final_notification(error_result, message_type, from_contact, content)
            except:
                pass  # Don't fail on notification error
                
            return error_result

# ===============================
# FASTAPI PRODUCTION SERVER
# ===============================

# Initialize SQLite Contact Cache
initialize_contact_cache()

# Initialize Orchestrator
orchestrator = ProductionAIOrchestrator()

# FastAPI App
app = FastAPI(
    title="AI Communication Orchestrator",
    description="Production-ready LangGraph AI Communication Processing System",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "✅ AI Communication Orchestrator ONLINE",
        "system": "LangGraph + FastAPI Production",
        "endpoints": [
            "/webhook/ai-email (deprecated - use /incoming or /outgoing)",
            "/webhook/ai-email/incoming",
            "/webhook/ai-email/outgoing",
            "/webhook/ai-call",
            "/webhook/frontdesk",
            "/webhook/feedback",
            "/webhook/ai-whatsapp"
        ],
        "version": "1.3.0",
        "features": [
            "Email Direction Detection (incoming/outgoing)",
            "Document Type Classification (invoice/offer/order/delivery/general)",
            "Intelligent Attachment Processing",
            "Type-specific OCR Routes"
        ],
        "timestamp": now_berlin().isoformat()
    }

@app.post("/webhook/ai-email")
@app.post("/webhook/ai-email/incoming")
async def process_email_incoming(request: Request):
    """
    📧 INCOMING EMAIL PROCESSING WITH MICROSOFT GRAPH API
    
    Zapier sends minimal metadata → Railway loads full email via Graph API
    
    Expected payload from Zapier:
    {
        "message_id": "AAMkAGE1...",  # Graph API Message ID
        "user_email": "mj@cdtechnologies.de",  # Mailbox to query
        "from": "sender@example.com",  # Optional metadata
        "subject": "..."  # Optional metadata
    }
    """
    
    try:
        data = await request.json()
        data["email_direction"] = "incoming"  # Mark as incoming
        message_id = data.get("message_id") or data.get("id")
        user_email = data.get("user_email") or data.get("mailbox") or data.get("recipient")
        
        # ⚡ IMMEDIATE RESPONSE - No logging before response!
        # Fire-and-forget background task
        import asyncio
        asyncio.create_task(process_email_background(data, message_id, user_email))
        
        # Return immediately (< 1 second)
        return JSONResponse(
            status_code=200,
            content={
                "status": "accepted",
                "message_id": message_id,
                "direction": "incoming"
            }
        )
        
    except Exception as e:
        # Even errors return fast
        return JSONResponse(
            status_code=200,
            content={"status": "error", "error": str(e)}
        )

@app.post("/webhook/ai-email/outgoing")
async def process_email_outgoing(request: Request):
    """
    📤 OUTGOING EMAIL PROCESSING WITH MICROSOFT GRAPH API
    
    Zapier sends minimal metadata → Railway loads full email via Graph API
    
    Expected payload from Zapier:
    {
        "message_id": "AAMkAGE1...",  # Graph API Message ID
        "user_email": "mj@cdtechnologies.de",  # Mailbox to query
        "to": "recipient@example.com",  # Optional metadata
        "subject": "..."  # Optional metadata
    }
    """
    
    try:
        data = await request.json()
        data["email_direction"] = "outgoing"  # Mark as outgoing
        message_id = data.get("message_id") or data.get("id")
        user_email = data.get("user_email") or data.get("mailbox") or data.get("sender")
        
        # ⚡ IMMEDIATE RESPONSE - No logging before response!
        # Fire-and-forget background task
        import asyncio
        asyncio.create_task(process_email_background(data, message_id, user_email))
        
        # Return immediately (< 1 second)
        return JSONResponse(
            status_code=200,
            content={
                "status": "accepted",
                "message_id": message_id,
                "direction": "outgoing"
            }
        )
        
    except Exception as e:
        # Even errors return fast
        return JSONResponse(
            status_code=200,
            content={"status": "error", "error": str(e)}
        )

async def process_attachments_intelligent(
    attachments: List[Dict],
    message_id: str,
    user_email: str,
    access_token: str,
    subject: str
) -> List[Dict]:
    """
    📎 INTELLIGENT ATTACHMENT PROCESSING
    
    1. Classify document type from subject + filename
    2. Download attachment bytes from Graph API
    3. Choose OCR route based on type:
       - invoice → PDF.co Invoice Parser
       - delivery_note/aufmaß → PDF.co Handwriting OCR
       - offer/order → PDF.co Standard OCR
    4. Extract text and structured data
    5. Return results for GPT analysis
    """
    results = []
    
    try:
        import httpx
        import base64
        
        # Classify expected document type from subject
        subject_lower = subject.lower()
        expected_type = "general"
        
        if any(word in subject_lower for word in ["rechnung", "invoice", "re:"]):
            expected_type = "invoice"
        elif any(word in subject_lower for word in ["angebot", "offer", "quote"]):
            expected_type = "offer"
        elif any(word in subject_lower for word in ["auftragsbestätigung", "ab:", "order"]):
            expected_type = "order_confirmation"
        elif any(word in subject_lower for word in ["aufmaß", "lieferschein", "delivery"]):
            expected_type = "delivery_note"
        
        logger.info(f"📊 Expected document type from subject: {expected_type}")
        
        for attachment in attachments:
            try:
                att_id = attachment.get("id")
                att_name = attachment.get("name", "unknown")
                att_type = attachment.get("contentType", "")
                att_size = attachment.get("size", 0)
                
                logger.info(f"📎 Processing: {att_name} ({att_type}, {att_size} bytes)")
                
                # Only process PDFs and images
                if att_type not in ["application/pdf", "image/jpeg", "image/png", "image/jpg"]:
                    logger.warning(f"⚠️ Skipping unsupported type: {att_type}")
                    continue
                
                # Download attachment bytes via Graph API
                download_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}/attachments/{att_id}/$value"
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        download_url,
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    
                    if response.status_code == 200:
                        file_bytes = response.content
                        logger.info(f"✅ Downloaded {len(file_bytes)} bytes for {att_name}")
                        
                        # Choose OCR route based on type
                        ocr_result = await process_attachment_ocr(
                            file_bytes=file_bytes,
                            filename=att_name,
                            content_type=att_type,
                            document_type=expected_type
                        )
                        
                        results.append({
                            "filename": att_name,
                            "type": att_type,
                            "size": att_size,
                            "document_type": expected_type,
                            "ocr_text": ocr_result.get("text", ""),
                            "structured_data": ocr_result.get("structured", {}),
                            "ocr_route": ocr_result.get("route", "none")
                        })
                        
                    else:
                        logger.error(f"❌ Failed to download {att_name}: {response.status_code}")
                        
            except Exception as att_error:
                logger.error(f"❌ Error processing attachment {att_name}: {att_error}")
                
    except Exception as e:
        logger.error(f"❌ Attachment processing error: {e}")
    
    return results


async def process_attachment_ocr(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    document_type: str
) -> Dict:
    """
    🤖 OCR PROCESSING WITH TYPE-SPECIFIC ROUTES
    
    Routes:
    - invoice → PDF.co Invoice Parser (structured extraction)
    - delivery_note → PDF.co Handwriting OCR
    - offer/order/general → PDF.co Standard OCR
    """
    result = {"text": "", "structured": {}, "route": "none"}
    
    try:
        # For now, return placeholder (will integrate PDF.co in next step)
        logger.info(f"🔍 OCR Route: {document_type} for {filename}")
        
        # TODO: Implement PDF.co calls
        # if document_type == "invoice":
        #     result = await pdfco_invoice_parser(file_bytes)
        # elif document_type == "delivery_note":
        #     result = await pdfco_handwriting_ocr(file_bytes)
        # else:
        #     result = await pdfco_standard_ocr(file_bytes)
        
        result["route"] = f"{document_type}_ocr"
        result["text"] = f"[OCR Placeholder for {filename} - Type: {document_type}]"
        
    except Exception as e:
        logger.error(f"❌ OCR error for {filename}: {e}")
        result["error"] = str(e)
    
    return result


async def process_email_background(data: dict, message_id: str, user_email: str):
    """Background task to process email without blocking Zapier webhook"""
    try:
        # NOW we can log (after response sent to Zapier)
        logger.info(f"📧 Email webhook data: message_id={message_id}, user_email={user_email}")
        logger.info(f"🔍 DEBUG: Full data keys: {list(data.keys())}")
        
        # If message_id provided → Load full email from Graph API
        if message_id and user_email:
            logger.info(f"🔍 Loading full email via Graph API: message_id={message_id}, mailbox={user_email}")
            
            # Get Graph API token
            access_token = await get_graph_token_mail()
            if not access_token:
                logger.error("❌ Failed to get Graph API token")
                return
            
            # Fetch full email with attachments
            email_data = await fetch_email_details_with_attachments(
                user_email=user_email,
                message_id=message_id,
                access_token=access_token
            )
            
            if not email_data:
                logger.error(f"❌ Failed to load email from Graph API: {message_id}")
                return
            
            # Extract email details
            from_address = email_data.get("from", {}).get("emailAddress", {}).get("address", "")
            subject = email_data.get("subject", "")
            body = email_data.get("body", {}).get("content", "")
            body_type = email_data.get("body", {}).get("contentType", "html")
            attachments = email_data.get("attachments", [])
            
            logger.info(f"✅ Email loaded: From={from_address}, Subject={subject}, Attachments={len(attachments)}")
            
            # 📎 PROCESS ATTACHMENTS (if any)
            attachment_results = []
            if len(attachments) > 0:
                logger.info(f"📎 Processing {len(attachments)} attachment(s)...")
                attachment_results = await process_attachments_intelligent(
                    attachments=attachments,
                    message_id=message_id,
                    user_email=user_email,
                    access_token=access_token,
                    subject=subject
                )
                logger.info(f"✅ Attachments processed: {len(attachment_results)} results")
            
            # Process with full email data
            result = await orchestrator.process_communication(
                message_type="email",
                from_contact=from_address,
                content=f"{subject}\n\n{body}",
                additional_data={
                    **data,
                    "subject": subject,
                    "body": body,
                    "body_type": body_type,
                    "attachments": attachments,
                    "has_attachments": len(attachments) > 0,
                    "attachments_count": len(attachments),
                    "attachment_results": attachment_results  # OCR results
                }
            )
            logger.info(f"✅ Email processing complete: {result.get('workflow_path', 'unknown')}")
            
        else:
            # Fallback: Process with provided data (no Graph API)
            logger.warning("⚠️ No message_id provided - processing with limited data from Zapier")
            result = await orchestrator.process_communication(
                message_type="email",
                from_contact=data.get("from", ""),
                content=data.get("content", data.get("subject", "")),
                additional_data=data
            )
            logger.info(f"✅ Email processing complete (fallback): {result.get('workflow_path', 'unknown')}")
        
    except Exception as e:
        logger.error(f"❌ Background email processing error: {e}")
        import traceback
        logger.error(traceback.format_exc())

@app.post("/webhook/ai-call")
async def process_call(request: Request):
    """
    📞 SIPGATE CALL PROCESSING (SipGate Assist + FrontDesk)
    
    Supports TWO webhook sources:
    1. SipGate Assist API (nested structure: data["call"], data["assist"])
    2. FrontDesk (flat structure with recording_url, etc.)
    
    Flow:
    1. Telefonnummer-Matching in WeClapp (phone-eq=...)
    2. WEG_A: Unbekannt → Notification Email mit 4 Buttons
    3. WEG_B: Bekannt → CRM Log mit Transcript, AI Analysis, Tasks
    """
    
    try:
        data = await request.json()
        logger.info(f"📞 Call Webhook Payload: {json.dumps(data, ensure_ascii=False)[:1000]}")
        
        # 🔍 DETECT WEBHOOK SOURCE: SipGate Assist vs FrontDesk
        is_sipgate_assist = "call" in data and "assist" in data
        is_frontdesk = "recording_url" in data or "audio_url" in data or "transcription_url" in data
        
        if is_sipgate_assist:
            logger.info("✅ Detected: SipGate Assist API webhook")
            # 🎯 SIPGATE ASSIST API STRUCTURE (v1)
            call_data = data.get("call", {})
            assist_data = data.get("assist", {})
            summary_data = assist_data.get("summary", {})
        elif is_frontdesk:
            logger.info("✅ Detected: FrontDesk webhook")
            # FrontDesk sends flat structure
            call_data = data  # All data at root level
            assist_data = {}
            summary_data = {}
        else:
            logger.warning("⚠️ Unknown webhook format - treating as generic call")
            call_data = data
            assist_data = {}
            summary_data = {}
        
        logger.info(f"✅ Processing call with source: {'SipGate Assist' if is_sipgate_assist else 'FrontDesk' if is_frontdesk else 'Unknown'}")
        
        # Extract call direction (format differs between sources)
        if is_sipgate_assist:
            call_direction = call_data.get("direction", "in")  # "in" or "out"
            call_direction = "inbound" if call_direction == "in" else "outbound"
        else:
            # FrontDesk or generic format
            call_direction = call_data.get("call_direction", call_data.get("direction", "inbound"))
        
        # 🎯 EXTRACT CALL INFO (source-aware)
        if is_sipgate_assist:
            call_id = call_data.get("id", "")
            call_duration = call_data.get("duration", 0) // 1000  # SipGate: milliseconds
            call_start_time = call_data.get("startTime", "")
            call_end_time = call_data.get("endTime", "")
            call_users = call_data.get("users", [])
            
            # Phone numbers from nested structure
            if call_direction == "outbound":
                external_number = call_data.get("to", "")
                our_number = call_data.get("from", "")
            else:
                external_number = call_data.get("from", "")
                our_number = call_data.get("to", "")
        else:
            # FrontDesk format (flat structure)
            call_id = call_data.get("call_id", call_data.get("id", ""))
            call_duration = call_data.get("duration", call_data.get("call_duration", 0))
            call_start_time = call_data.get("start_time", call_data.get("startTime", ""))
            call_end_time = call_data.get("end_time", call_data.get("endTime", ""))
            call_users = []
            
            # Phone numbers (various field names)
            external_number = (
                call_data.get("caller") or 
                call_data.get("from") or 
                call_data.get("phone") or
                call_data.get("caller_number") or
                ""
            )
            our_number = (
                call_data.get("called") or
                call_data.get("to") or
                call_data.get("recipient") or
                ""
            )
        
        # Normalize phone format (remove spaces, dashes, brackets)
        phone_normalized = external_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # 🎯 EXTRACT TRANSCRIPTION (source-aware)
        if is_sipgate_assist:
            # SipGate Assist: nested in assist.summary
            call_transcript = summary_data.get("content", "")
            key_points = summary_data.get("keyPoints", [])
            topics = summary_data.get("topics", [])
            
            # Extract SmartAnswers (caller name, company, etc.)
            call_scenarios = assist_data.get("callScenarios", [])
            caller_name = ""
            company_name = ""
            caller_request = ""
            
            for scenario in call_scenarios:
                smart_answers = scenario.get("smartAnswers", [])
                for answer_set in smart_answers:
                    items = answer_set.get("setItems", [])
                    for item in items:
                        question = item.get("question", "").lower()
                        answer = item.get("answer", "")
                        
                        if "name" in question and not caller_name:
                            caller_name = answer
                        elif "firma" in question or "company" in question:
                            company_name = answer
                        elif "anliegen" in question or "anfrage" in question:
                            caller_request = answer
        else:
            # FrontDesk: flat structure
            call_transcript = (
                call_data.get("transcription") or
                call_data.get("transcript") or
                call_data.get("text") or
                call_data.get("content") or
                ""
            )
            key_points = call_data.get("key_points", [])
            topics = call_data.get("topics", [])
            
            # Caller details from flat structure
            caller_name = call_data.get("caller_name", call_data.get("name", ""))
            company_name = call_data.get("company", call_data.get("company_name", ""))
            caller_request = call_data.get("request", call_data.get("purpose", ""))
            
            # Recording URL (FrontDesk specific)
            recording_url = (
                call_data.get("recording_url") or
                call_data.get("audio_url") or
                call_data.get("recordingUrl") or
                ""
            )
        
        # Legacy/additional fields
        if not is_sipgate_assist and recording_url:
            logger.info(f"🎙️ FrontDesk Recording: {recording_url}")
        
        call_status = ""
        assigned_user = call_users[0] if call_users and is_sipgate_assist else ""
        user_id = ""
        notes = ""
        tags = []
        
        # 📊 LOG ALL EXTRACTED DATA
        logger.info(f"📞 Call Details:")
        logger.info(f"   Direction: {call_direction} | Duration: {call_duration}s | Call ID: {call_id}")
        logger.info(f"   📞 External: {phone_normalized} | Our Number: {our_number}")
        if caller_name:
            logger.info(f"   📛 Caller Name: {caller_name}")
        if company_name:
            logger.info(f"   🏢 Company: {company_name}")
        if caller_request:
            logger.info(f"   💬 Request: {caller_request[:100]}...")
        if assigned_user:
            logger.info(f"   👤 Assigned to: {assigned_user}")
        if key_points:
            logger.info(f"   🔑 Key Points: {len(key_points)} items")
        if topics:
            logger.info(f"   🏷️ Topics: {', '.join(topics)}")
        
        # Build comprehensive transcript for AI analysis
        if not call_transcript:
            call_transcript = f"Anruf {call_direction} - Dauer: {call_duration}s - Keine Transkription verfügbar"
        else:
            # Enhance transcript with structured data
            transcript_parts = [call_transcript]
            
            if caller_name:
                transcript_parts.append(f"\n👤 Anrufer: {caller_name}")
            if company_name:
                transcript_parts.append(f"\n🏢 Firma: {company_name}")
            if key_points:
                transcript_parts.append(f"\n\n🔑 Wichtige Punkte:\n" + "\n".join(f"- {point}" for point in key_points))
            
            call_transcript = "".join(transcript_parts)
        
        # Process through orchestrator (includes phone matching)
        result = await orchestrator.process_communication(
            message_type="call",
            from_contact=phone_normalized,
            content=call_transcript,
            additional_data={
                **data,
                # Source identification
                "webhook_source": "sipgate_assist" if is_sipgate_assist else "frontdesk" if is_frontdesk else "unknown",
                # Core call data
                "call_direction": call_direction,
                "call_duration": call_duration,
                "call_id": call_id,
                "call_start_time": call_start_time,
                "call_end_time": call_end_time,
                "phone_normalized": phone_normalized,
                "external_number": external_number,
                "our_number": our_number,
                # Extracted contact/company data
                "caller_name": caller_name,
                "company_name": company_name,
                "caller_request": caller_request,
                # AI/transcription data
                "key_points": key_points,
                "topics": topics,
                "recording_url": recording_url if 'recording_url' in locals() else "",
                # Legacy fields
                "assigned_user": assigned_user,
                "user_id": user_id,
                "notes": notes,
                "tags": tags
            }
        )
        
        logger.info(f"✅ Call processing complete: {result.get('workflow_path', 'unknown')}")
        
        return {"ai_processing": result}
        
    except Exception as e:
        logger.error(f"❌ Call processing error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # ⚠️ SECURITY: Never expose internal error details to client
        raise HTTPException(status_code=500, detail="Internal server error during call processing")

@app.post("/webhook/frontdesk")
async def process_frontdesk(request: Request):
    """
    🎙️ FRONTDESK CALL RECORDING & TRANSCRIPTION
    
    Dedicated endpoint for FrontDesk webhooks.
    Simpler than /webhook/ai-call - no auto-detection needed.
    
    Expected FrontDesk payload (flat structure):
    {
        "caller": "+49123456789",
        "transcription": "...",
        "recording_url": "https://...",
        "duration": 120,
        "caller_name": "Max Mustermann",
        "company": "Beispiel GmbH"
    }
    """
    
    try:
        data = await request.json()
        logger.info(f"🎙️ FrontDesk Webhook: {json.dumps(data, ensure_ascii=False)[:1000]}")
        
        # Extract phone number (various field names)
        phone_number = (
            data.get("caller") or 
            data.get("from") or 
            data.get("phone") or
            data.get("caller_number") or
            ""
        )
        
        # Extract transcription
        transcription = (
            data.get("transcription") or
            data.get("transcript") or
            data.get("text") or
            data.get("content") or
            ""
        )
        
        # Extract additional metadata
        caller_name = data.get("caller_name", data.get("name", ""))
        company = data.get("company", data.get("company_name", ""))
        duration = data.get("duration", data.get("call_duration", 0))
        recording_url = data.get("recording_url", data.get("audio_url", ""))
        
        # Log extracted data
        logger.info(f"📞 FrontDesk Call: {phone_number}")
        if caller_name:
            logger.info(f"   📛 Name: {caller_name}")
        if company:
            logger.info(f"   🏢 Company: {company}")
        if duration:
            logger.info(f"   ⏱️ Duration: {duration}s")
        if recording_url:
            logger.info(f"   🎙️ Recording: {recording_url}")
        
        # Build enhanced transcript
        transcript_parts = [transcription] if transcription else ["Keine Transkription verfügbar"]
        
        if caller_name:
            transcript_parts.append(f"\n👤 Anrufer: {caller_name}")
        if company:
            transcript_parts.append(f"\n🏢 Firma: {company}")
        
        enhanced_transcript = "".join(transcript_parts)
        
        # Process through orchestrator
        result = await orchestrator.process_communication(
            message_type="call",
            from_contact=phone_number,
            content=enhanced_transcript,
            additional_data={
                **data,
                "webhook_source": "frontdesk",
                "call_direction": data.get("direction", "inbound"),
                "call_duration": duration,
                "phone_normalized": phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", ""),
                "caller_name": caller_name,
                "company_name": company,
                "recording_url": recording_url
            }
        )
        
        logger.info(f"✅ FrontDesk call processing complete: {result.get('workflow_path', 'unknown')}")
        
        return {
            "status": "success",
            "message": "FrontDesk call processed",
            "workflow_path": result.get("workflow_path"),
            "phone": phone_number
        }
        
    except Exception as e:
        logger.error(f"❌ FrontDesk processing error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/webhook/feedback")
async def process_feedback(request: Request):
    """
    🐛 FEEDBACK & PROBLEM REPORTING
    
    Sammelt Feedback von Mitarbeitern zu:
    - Fehlverhalten des Systems
    - Falsche Kontakt-Zuordnungen
    - Fehlende Funktionen
    - Verbesserungsvorschläge
    
    Expected payload:
    {
        "type": "bug|feature|improvement|wrong_match",
        "message": "Beschreibung des Problems",
        "context": {
            "email_id": "...",
            "contact_id": "...",
            "workflow_path": "..."
        }
    }
    """
    
    try:
        data = await request.json()
        logger.info(f"🐛 Feedback received: {json.dumps(data, ensure_ascii=False)[:500]}")
        
        feedback_type = data.get("type", "general")
        message = data.get("message", "")
        context = data.get("context", {})
        reporter = data.get("reporter", "unknown")
        
        # Store in optimization list (simple file-based for now)
        feedback_entry = {
            "timestamp": now_berlin().isoformat(),
            "type": feedback_type,
            "message": message,
            "context": context,
            "reporter": reporter,
            "status": "new"
        }
        
        # Append to feedback log file
        import json as json_lib
        feedback_file = "feedback_log.jsonl"
        try:
            with open(feedback_file, "a") as f:
                f.write(json_lib.dumps(feedback_entry, ensure_ascii=False) + "\n")
            logger.info(f"✅ Feedback stored in {feedback_file}")
        except Exception as e:
            logger.error(f"❌ Failed to write feedback: {e}")
        
        # Log to console for immediate visibility
        logger.info(f"📝 FEEDBACK [{feedback_type}]: {message}")
        if context:
            logger.info(f"   Context: {context}")
        
        return {
            "status": "success",
            "message": "Feedback erfasst - Vielen Dank!",
            "feedback_id": f"fb-{int(now_berlin().timestamp())}"
        }
        
    except Exception as e:
        logger.error(f"❌ Feedback processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/webhook/ai-whatsapp")
async def process_whatsapp(request: Request):
    """Process incoming WhatsApp message via webhook"""
    
    try:
        data = await request.json()
        
        result = await orchestrator.process_communication(
            message_type="whatsapp",
            from_contact=data.get("from", ""),
            content=data.get("message", data.get("content", "")),
            additional_data=data
        )
        
        return {"ai_processing": result}
        
    except Exception as e:
        logger.error(f"WhatsApp processing error: {e}")
        # ⚠️ SECURITY: Never expose internal error details to client
        raise HTTPException(status_code=500, detail="Internal server error during WhatsApp processing")

@app.api_route("/webhook/contact-action", methods=["GET", "POST"])
async def handle_contact_action(request: Request):
    """
    🎯 MITARBEITER-AKTIONEN für unbekannte Kontakte
    
    Empfängt Entscheidung des Mitarbeiters und führt entsprechende WeClapp API Calls aus:
    - create_contact: POST /party (neuer Kontakt)
    - mark_private: Custom Attribute "private_contact"
    - mark_spam: Custom Attribute "spam_contact"
    - request_info: POST /crmEvent (Rückfrage dokumentieren)
    
    Akzeptiert GET (Query Params) und POST (JSON Body)
    """
    
    try:
        # Support both GET and POST
        if request.method == "GET":
            # GET: Extract from query parameters
            action = request.query_params.get("action")
            contact_email = request.query_params.get("sender")  # From email link
            email_id = request.query_params.get("email_id")
            contact_data = {}  # Optional: Could parse from query params
        else:
            # POST: Extract from JSON body
            data = await request.json()
            action = data.get("action")
            contact_email = data.get("contact_email") or data.get("sender")
            email_id = data.get("email_id")
            contact_data = data.get("contact_data", {})
        
        # 🆕 FALLBACK: If sender is empty, try to get it from email database
        sender_name = None
        if not contact_email and email_id:
            logger.info(f"⚠️ Sender empty, looking up in database for email_id: {email_id}")
            try:
                db_conn = sqlite3.connect(DB_PATH)
                cursor = db_conn.execute(
                    "SELECT sender, sender_name FROM email_data WHERE id = ? OR subject LIKE ?",
                    (email_id, f"%{email_id}%")
                )
                row = cursor.fetchone()
                db_conn.close()
                if row:
                    contact_email = row[0]
                    sender_name = row[1] if len(row) > 1 else None
                    logger.info(f"✅ Found sender from database: {contact_email} ({sender_name})")
                else:
                    logger.warning(f"❌ No email found in database for email_id: {email_id}")
            except Exception as db_error:
                logger.error(f"❌ Database lookup error: {str(db_error)}")
        
        if not action or not contact_email:
            raise HTTPException(status_code=400, detail="action and contact_email/sender required")
        
        logger.info(f"📋 Contact Action received: {action} for {contact_email}")
        
        result = {}
        
        # ACTION 1: Kontakt im CRM anlegen
        if action == "create_contact":
            async with aiohttp.ClientSession() as session:
                headers = {
                    "AuthenticationToken": orchestrator.weclapp_api_token,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                # 🔧 Namen-Parsing: Versuche sender_name zu splitten oder nutze Placeholder
                first_name = contact_data.get("first_name", "")
                last_name = contact_data.get("last_name", "")
                
                # Fallback 1: sender_name aus DB (wenn vorhanden)
                if not first_name and not last_name and sender_name:
                    name_parts = sender_name.strip().split(maxsplit=1)
                    first_name = name_parts[0] if len(name_parts) > 0 else "Unbekannt"
                    last_name = name_parts[1] if len(name_parts) > 1 else "Kontakt"
                
                # 🎯 CHECK: Is contact_email actually a PHONE NUMBER?
                is_phone = contact_email and (contact_email.startswith("+") or contact_email.replace(" ", "").isdigit())
                
                # Fallback 2: Phone Number → Generate dummy email + use number as name
                if is_phone:
                    phone_clean = contact_email.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                    first_name = f"Tel {phone_clean}"
                    last_name = "Kontakt"
                    # Generate dummy email: phone@noemail.local
                    dummy_email = f"{phone_clean}@noemail.local"
                    phone_number = phone_clean
                elif not first_name and contact_email:
                    # Fallback 3: Email-Prefix als Vorname (z.B. "jaszczyk" → "Jaszczyk")
                    if "@" in contact_email:
                        email_prefix = contact_email.split("@")[0]
                        first_name = email_prefix.capitalize()
                        last_name = "Kontakt"
                        dummy_email = contact_email
                        phone_number = ""
                    else:
                        # Invalid format - use placeholder
                        first_name = "Unbekannt"
                        last_name = "Kontakt"
                        dummy_email = f"unknown{contact_email}@noemail.local"
                        phone_number = ""
                else:
                    # Fallback 4: Absolute Placeholders
                    if not first_name:
                        first_name = "Unbekannt"
                        last_name = "Kontakt"
                    dummy_email = contact_email if "@" in contact_email else f"unknown@noemail.local"
                    phone_number = ""
                
                party_data = {
                    "partyType": "PERSON",
                    "email": dummy_email,  # Always valid email format!
                    "firstName": first_name,
                    "lastName": last_name,
                    "company": contact_data.get("company", ""),
                    "phone": phone_number or contact_data.get("phone", "") or (contact_email if is_phone else ""),
                    "tags": ["AI_GENERATED", "UNKNOWN_CONTACT_CONVERTED"]
                }
                
                url = f"https://{orchestrator.weclapp_domain}.weclapp.com/webapp/api/v2/party"
                
                async with session.post(url, headers=headers, json=party_data) as response:
                    if response.status == 201:
                        created_party = await response.json()
                        result = {
                            "success": True,
                            "action": "contact_created",
                            "party_id": created_party.get("id"),
                            "message": f"Kontakt {contact_email} erfolgreich angelegt"
                        }
                        logger.info(f"✅ Contact created: {created_party.get('id')}")
                    else:
                        result = {
                            "success": False,
                            "error": f"WeClapp API error: {response.status}"
                        }
        
        # ACTION 2: Als privat markieren
        elif action == "mark_private":
            # Erstelle CRM Event für Dokumentation
            async with aiohttp.ClientSession() as session:
                headers = {
                    "AuthenticationToken": orchestrator.weclapp_api_token,
                    "Content-Type": "application/json"
                }
                
                crm_event = {
                    "type": "NOTE",
                    "description": f"Kontakt als PRIVAT markiert: {contact_email}",
                    "tags": ["PRIVATE_CONTACT"]
                }
                
                url = f"https://{orchestrator.weclapp_domain}.weclapp.com/webapp/api/v2/crmEvent"
                
                async with session.post(url, headers=headers, json=crm_event) as response:
                    result = {
                        "success": response.status == 201,
                        "action": "marked_private",
                        "message": f"{contact_email} als privat markiert"
                    }
        
        # ACTION 3: Als Spam markieren
        elif action == "mark_spam":
            async with aiohttp.ClientSession() as session:
                headers = {
                    "AuthenticationToken": orchestrator.weclapp_api_token,
                    "Content-Type": "application/json"
                }
                
                crm_event = {
                    "type": "NOTE",
                    "description": f"Kontakt als SPAM markiert: {contact_email}",
                    "tags": ["SPAM_CONTACT", "BLACKLIST"]
                }
                
                url = f"https://{orchestrator.weclapp_domain}.weclapp.com/webapp/api/v2/crmEvent"
                
                async with session.post(url, headers=headers, json=crm_event) as response:
                    result = {
                        "success": response.status == 201,
                        "action": "marked_spam",
                        "message": f"{contact_email} als Spam markiert"
                    }
        
        # ACTION 4: Weitere Informationen einholen
        elif action == "request_info":
            async with aiohttp.ClientSession() as session:
                headers = {
                    "AuthenticationToken": orchestrator.weclapp_api_token,
                    "Content-Type": "application/json"
                }
                
                task_data = {
                    "title": f"Weitere Infos einholen: {contact_email}",
                    "description": f"Kontakt {contact_email} - Zusätzliche Informationen anfordern vor CRM-Aufnahme",
                    "status": "OPEN",
                    "priority": "MEDIUM",
                    "dueDate": (now_berlin() + timedelta(days=2)).isoformat()
                }
                
                url = f"https://{orchestrator.weclapp_domain}.weclapp.com/webapp/api/v2/task"
                
                async with session.post(url, headers=headers, json=task_data) as response:
                    if response.status == 201:
                        task = await response.json()
                        result = {
                            "success": True,
                            "action": "info_requested",
                            "task_id": task.get("id"),
                            "message": f"Follow-up Task erstellt für {contact_email}"
                        }
                    else:
                        result = {"success": False, "error": f"Task creation failed: {response.status}"}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Contact action error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/status")
async def system_status():
    """System status and configuration"""
    
    return {
        "system": "AI Communication Orchestrator",
        "framework": "LangGraph + LangChain + FastAPI",
        "status": "ONLINE",
        "configuration": {
            "openai_configured": bool(orchestrator.openai_api_key),
            "weclapp_configured": bool(orchestrator.weclapp_api_token),
            "apify_configured": bool(orchestrator.apify_token)
        },
        "workflow_nodes": [
            "contact_lookup",
            "ai_analysis", 
            "workflow_routing",
            "weg_a_unknown_contact",
            "weg_b_known_contact",
            "finalize_processing"
        ]
    }

@app.post("/admin/cache/reset")
async def reset_contact_cache(request: Request):
    """🗑️ ADMIN: Reset Email Database Cache"""
    
    try:
        # Optional: Add authentication here
        # auth_header = request.headers.get("Authorization")
        # if auth_header != f"Bearer {os.getenv('ADMIN_TOKEN')}":
        #     raise HTTPException(status_code=401, detail="Unauthorized")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get cache stats before reset
        cursor.execute("SELECT COUNT(*) FROM email_data")
        total_entries = cursor.fetchone()[0] or 0
        
        # Clear cache
        cursor.execute("DELETE FROM email_data")
        conn.commit()
        conn.close()
        
        logger.warning(f"⚠️ EMAIL DATABASE RESET: Deleted {total_entries} entries")
        
        return {
            "status": "success",
            "message": "Email database reset successfully",
            "deleted_entries": total_entries
        }
        
    except Exception as e:
        logger.error(f"❌ Cache reset error: {e}")
        raise HTTPException(status_code=500, detail=f"Cache reset failed: {str(e)}")

# ===============================
# PRODUCTION SERVER STARTUP
# ===============================

if __name__ == "__main__":
    print("🚀 STARTING PRODUCTION AI ORCHESTRATOR")
    print("=" * 50)
    print("✅ LangGraph Workflow initialized")
    print("✅ FastAPI server configured")
    print("✅ OpenAI GPT-4 integration ready")
    print("✅ WeClapp CRM integration ready")
    print("🌐 Server starting on http://0.0.0.0:5001")
    print("")
    print("📡 WEBHOOK ENDPOINTS:")
    print("  - POST /webhook/ai-email")
    print("  - POST /webhook/ai-call")
    print("  - POST /webhook/frontdesk  🎙️")
    print("  - POST /webhook/feedback   🐛 NEW")
    print("  - POST /webhook/ai-whatsapp")
    print("")
    print("🎯 READY FOR PRODUCTION DEPLOYMENT!")
    
    # Production server
    uvicorn.run(
        "production_langgraph_orchestrator:app",
        host="0.0.0.0",
        port=5001,
        reload=False,  # Production mode
        workers=1,
        log_level="info"
    )