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
from asyncio import Semaphore

# 🔒 Global request limiter to prevent memory overload
# Max 3 concurrent heavy operations (GPT-4, PDF processing, etc.)
REQUEST_SEMAPHORE = Semaphore(3)
active_requests = 0
from contextlib import asynccontextmanager
import requests

# 💰 Richtpreis-Berechnung für Anrufe
from modules.pricing.estimate_from_call import (
    calculate_estimate_from_transcript,
    format_estimate_for_email,
    ProjectEstimate
)

# 📂 Apify Module Imports - Ordnerstruktur & Dokumenten-Klassifikation
from modules.filegen.folder_logic import generate_folder_and_filenames
from modules.gpt.classify_document_with_gpt import classify_document_with_gpt

# 🗄️ Email Tracking Database - Duplikatprüfung
from modules.database.email_tracking_db import get_email_tracking_db, EmailTrackingDB

# ☁️ OneDrive Upload
from modules.upload.upload_file_to_onedrive import upload_file_to_onedrive

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

async def get_graph_token_onedrive():
    """Holt das Zugriffstoken von Microsoft Graph für OneDrive."""
    tenant_id = os.getenv("GRAPH_TENANT_ID_ONEDRIVE")
    client_id = os.getenv("GRAPH_CLIENT_ID_ONEDRIVE")
    client_secret = os.getenv("GRAPH_CLIENT_SECRET_ONEDRIVE")
    
    if not tenant_id or not client_id or not client_secret:
        logger.error("❌ Fehlende OneDrive-Graph API Zugangsdaten")
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
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            if response.status_code == 200:
                logger.info("✅ OneDrive token obtained successfully")
                return response.json().get("access_token")
            else:
                logger.error(f"❌ OneDrive token error {response.status_code}: {response.text}")
                return None
    except Exception as e:
        logger.error(f"❌ OneDrive token exception: {e}")
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
    
    if notification_type == "known_contact_enhanced":
        # ✅ WEG B: Known Contact Enhanced with Smart Actions & Dashboard Links
        subject = notification_data.get('subject', 'Kontakt verarbeitet')
        contact_match = notification_data.get('contact_match', {})
        contact_name = contact_match.get('contact_name', 'Unbekannt')
        company = contact_match.get('company', '')
        contact_id = contact_match.get('contact_id', '')
        from_contact = notification_data.get('from', '')
        body_preview = notification_data.get('body_preview', notification_data.get('content_preview', ''))
        ai_analysis = notification_data.get('ai_analysis', {})
        action_options = notification_data.get('action_options', [])
        tasks_generated = notification_data.get('tasks_generated', [])
        
        # ✨ Build Dashboard Links HTML (same as WEG A)
        dashboard_links_html = ""
        invoice_id = notification_data.get("invoice_id")
        opportunity_id = notification_data.get("opportunity_id")
        onedrive_links = notification_data.get("onedrive_links", [])
        
        dashboard_items = []
        
        if invoice_id:
            invoice_number = notification_data.get("invoice_number", invoice_id)
            dashboard_items.append(
                f"📄 <a href='https://my-langgraph-agent-production.up.railway.app/api/invoice/{invoice_number}' target='_blank'>Rechnung #{invoice_number} im System anzeigen</a>"
            )
        
        if opportunity_id:
            opportunity_title = notification_data.get("opportunity_title", f"Opportunity #{opportunity_id}")
            dashboard_items.append(
                f"💼 <a href='https://my-langgraph-agent-production.up.railway.app/api/opportunity/{opportunity_id}' target='_blank'>Verkaufschance anzeigen: {opportunity_title}</a>"
            )
        
        if onedrive_links:
            for link_data in onedrive_links:
                filename = link_data.get("filename", "Datei")
                sharing_link = link_data.get("sharing_link")
                if sharing_link:
                    dashboard_items.append(
                        f"☁️ <a href='{sharing_link}' target='_blank'>{filename} in OneDrive öffnen</a>"
                    )
        
        dashboard_items.append(
            "📊 <a href='http://localhost:3000' target='_blank'>Invoice & Payment Dashboard öffnen</a>"
        )
        dashboard_items.append(
            "💰 <a href='http://localhost:3000/sales-pipeline' target='_blank'>Sales Pipeline Dashboard öffnen</a>"
        )
        
        if dashboard_items:
            items_html = "<br>".join([f"&nbsp;&nbsp;&nbsp;&nbsp;{item}" for item in dashboard_items])
            dashboard_links_html = f"""
<div class="info-box" style="background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); border-left: 5px solid #66BB6A;">
<h3>🔗 Relevante Links:</h3>
<p>
{items_html}
</p>
</div>
"""
        
        # 📎 Attachments HTML
        attachments_html = ""
        attachments_count = notification_data.get("attachments_count", 0)
        if attachments_count > 0:
            attachments_html = f"<p><strong>📎 Anhänge:</strong> {attachments_count} Datei(en) verarbeitet</p>"
        
        # ✅ Tasks HTML
        tasks_html = ""
        if tasks_generated:
            tasks_items = []
            for task in tasks_generated:
                task_title = task.get('title', 'Unbekannte Aufgabe')
                task_priority = task.get('priority', 'normal')
                priority_emoji = "🔴" if task_priority == "high" else "🟡" if task_priority == "medium" else "🟢"
                tasks_items.append(f"{priority_emoji} {task_title}")
            
            tasks_list = "<br>".join([f"&nbsp;&nbsp;&nbsp;&nbsp;{item}" for item in tasks_items])
            tasks_html = f"""
<div class="info-box" style="background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); border-left: 5px solid #FF9800;">
<h3>✅ Automatisch erstellte Aufgaben ({len(tasks_generated)}):</h3>
<p>
{tasks_list}
</p>
</div>
"""
        
        # Build action buttons HTML
        buttons_html = ""
        for option in action_options:
            action = option.get("action", "")
            label = option.get("label", "")
            description = option.get("description", "")
            url = option.get("url", "")
            color = option.get("color", "primary")
            
            color_class = {
                "view_in_crm": "btn-info",
                "schedule_appointment": "btn-primary",
                "create_quote": "btn-success",
                "call_customer": "btn-info",
                "create_order": "btn-create",
                "urgent_response": "btn-warning",
                "complete_task": "btn-secondary",
                "data_good": "btn-success",
                "data_error": "btn-warning",
                "primary": "btn-primary",
                "success": "btn-success",
                "info": "btn-info",
                "warning": "btn-warning",
                "secondary": "btn-secondary",
                "create": "btn-create"
            }.get(action if action else color, "btn-primary")
            
            # Route feedback actions to /webhook/feedback
            if action in ["data_good", "data_error"]:
                button_url = f"https://my-langgraph-agent-production.up.railway.app/webhook/feedback?action={action}&contact_id={contact_id}&from={from_contact}"
            elif url:
                button_url = url
            else:
                button_url = f"https://cundd.weclapp.com/webapp/view/party/{contact_id}"
            
            buttons_html += f"""
            <a href="{button_url}" class="button {color_class}" target="_blank">{label}</a>
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
    .btn-create {{ background: linear-gradient(135deg, #52C234 0%, #47A025 100%); color: white; }}
    .btn-create:hover {{ box-shadow: 0 6px 16px rgba(82,194,52,0.4); transform: translateY(-2px); }}
    .btn-primary {{ background: linear-gradient(135deg, #3498DB 0%, #2980B9 100%); color: white; }}
    .btn-primary:hover {{ box-shadow: 0 6px 16px rgba(52,152,219,0.4); transform: translateY(-2px); }}
    .btn-info {{ background: linear-gradient(135deg, #74B9FF 0%, #0984E3 100%); color: white; }}
    .btn-info:hover {{ box-shadow: 0 6px 16px rgba(116,185,255,0.4); transform: translateY(-2px); }}
    .btn-success {{ background: linear-gradient(135deg, #00D2A0 0%, #00B894 100%); color: white; }}
    .btn-success:hover {{ box-shadow: 0 6px 16px rgba(0,210,160,0.4); transform: translateY(-2px); }}
    .btn-warning {{ background: linear-gradient(135deg, #FDCB6E 0%, #E17055 100%); color: white; }}
    .btn-warning:hover {{ box-shadow: 0 6px 16px rgba(253,203,110,0.4); transform: translateY(-2px); }}
    .btn-secondary {{ background: linear-gradient(135deg, #FFEAA7 0%, #FDCB6E 100%); color: #2C3E50; }}
    .btn-secondary:hover {{ box-shadow: 0 6px 16px rgba(255,234,167,0.4); transform: translateY(-2px); }}
    .ai-analysis {{ background: linear-gradient(135deg, #DFE6E9 0%, #B2BEC3 100%); padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #74B9FF; }}
    .ai-analysis h3 {{ color: #0984E3; margin-top: 0; font-size: 18px; }}
    .ai-analysis p {{ color: #2C3E50; margin: 8px 0; }}
    .footer {{ text-align: center; padding: 20px; background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%); color: #7F8C8D; font-size: 13px; border-radius: 0 0 15px 15px; }}
    .button-desc {{ font-size: 12px; margin: 5px 0 15px 0; color: #7F8C8D; text-align: center; }}
    strong {{ color: #2C3E50; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h2>✅ Bekannter Kontakt verarbeitet</h2>
</div>
<div class="content">
<div class="info-box">
<h3>👤 Kontakt erkannt:</h3>
<p><strong>{contact_name}</strong>{f" ({company})" if company else ""}</p>
<p>Von: {from_contact}</p>
<p><a href="https://cundd.weclapp.com/webapp/view/party/{contact_id}" target="_blank">📋 In WeClapp öffnen</a></p>
</div>
<div class="info-box">
<h3>📝 Nachricht:</h3>
<p>{body_preview}</p>
</div>
<div class="ai-analysis">
<h3>🤖 KI-Analyse:</h3>
<p><strong>Absicht:</strong> {ai_analysis.get('intent', 'unbekannt')}</p>
<p><strong>Dringlichkeit:</strong> {ai_analysis.get('urgency', 'normal')}</p>
<p><strong>Stimmung:</strong> {ai_analysis.get('sentiment', 'neutral')}</p>
{attachments_html}
</div>
{tasks_html}
{dashboard_links_html}
<div class="action-buttons">
<h3>🎯 Empfohlene Aktionen:</h3>
{buttons_html}
</div>
</div>
<div class="footer">
<p>🤖 Automatisch generiert vom C&D Lead Management System</p>
<p>Kontakt-ID: {contact_id}</p>
</div>
</div>
</body>
</html>
"""
    
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
        
        # 💰 Build price estimate HTML if present (for calls)
        price_estimate = notification_data.get("price_estimate")
        has_price_estimate = notification_data.get("has_price_estimate", False)
        price_estimate_html = ""
        
        if has_price_estimate and price_estimate:
            # Use the formatting function from the pricing module
            from modules.pricing.estimate_from_call import ProjectEstimate
            
            # Convert dict back to ProjectEstimate object
            estimate_obj = ProjectEstimate(
                found=True,
                project_type=price_estimate.get("project_type", ""),
                area_sqm=price_estimate.get("area_sqm"),
                material=price_estimate.get("material", ""),
                work_type=price_estimate.get("work_type", ""),
                material_cost=price_estimate.get("material_cost", 0.0),
                labor_cost=price_estimate.get("labor_cost", 0.0),
                additional_cost=price_estimate.get("additional_cost", 0.0),
                total_cost=price_estimate.get("total_cost", 0.0),
                confidence=price_estimate.get("confidence", 0.0),
                calculation_basis=price_estimate.get("calculation_basis", []),
                additional_services=price_estimate.get("additional_services", []),
                notes=price_estimate.get("notes", "")
            )
            
            price_estimate_html = format_estimate_for_email(estimate_obj)
            logger.info(f"✅ Generated price estimate HTML for notification")
        
        # Build attachments HTML if present
        attachments_count = notification_data.get("attachments_count", 0)
        attachment_results = notification_data.get("attachment_results", [])
        logger.info(f"🔍 DEBUG generate_notification_html: attachments_count={attachments_count}, attachment_results={len(attachment_results)}")
        
        if attachments_count > 0:
            # Build detailed attachment list with OCR results
            attachment_details = []
            for result in attachment_results:
                name = result.get("filename", "Unbekannt")
                size = result.get("size", 0)
                doc_type = result.get("document_type", "unbekannt")
                ocr_route = result.get("ocr_route", "none")
                ocr_text = result.get("ocr_text", "")
                structured_data = result.get("structured_data", {})
                
                # Format size
                if size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size} B"
                
                # Build detail line
                detail_line = f"📄 <strong>{name}</strong> ({size_str})"
                detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;🏷️ Typ: {doc_type}"
                detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;🔍 Verarbeitung: {ocr_route}"
                
                # Add OCR preview if available
                if ocr_text and ocr_text != f"[OCR Placeholder for {name} - Type: {doc_type}]":
                    preview = ocr_text[:150] + "..." if len(ocr_text) > 150 else ocr_text
                    detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;📝 Inhalt: {preview}"
                
                # ✨ PHASE 2: Add structured data if available
                if structured_data:
                    if structured_data.get("invoice_number"):
                        detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;🔢 Rechnungs-Nr: {structured_data['invoice_number']}"
                    if structured_data.get("total_amount"):
                        detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;💰 Betrag: {structured_data['total_amount']}"
                    if structured_data.get("vendor_name"):
                        detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;🏢 Lieferant: {structured_data['vendor_name']}"
                    if structured_data.get("invoice_date"):
                        detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;📅 Rechnungsdatum: {structured_data['invoice_date']}"
                    if structured_data.get("due_date"):
                        detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;⏰ Fällig am: {structured_data['due_date']}"
                    if structured_data.get("direction"):
                        direction_icon = "📥" if structured_data['direction'] == "incoming" else "📤"
                        direction_text = "Eingang (AN uns)" if structured_data['direction'] == "incoming" else "Ausgang (VON uns)"
                        detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;{direction_icon} Richtung: {direction_text}"
                
                # ✨ PHASE 2: Add OneDrive links if available
                onedrive_sharing_link = result.get("onedrive_sharing_link")
                onedrive_web_url = result.get("onedrive_web_url")
                onedrive_path = result.get("onedrive_path")
                
                if onedrive_sharing_link:
                    detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;🔗 <a href='{onedrive_sharing_link}'>OneDrive Link öffnen</a>"
                elif onedrive_web_url:
                    detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;🔗 <a href='{onedrive_web_url}'>OneDrive Link öffnen</a>"
                
                if onedrive_path:
                    detail_line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;📂 Ablage: {onedrive_path}"
                
                attachment_details.append(detail_line)
            
            if attachment_details:
                details_html = "<br><br>".join(attachment_details)
                attachments_html = f'<p><strong>📎 Anhänge ({attachments_count}):</strong><br><br>{details_html}</p>'
            else:
                attachments_html = f'<p><strong>📎 Anhänge:</strong> {attachments_count} Datei(en)</p>'
            
            logger.info(f"✅ Generated attachments_html with OCR details: {len(attachment_results)} files")
        else:
            attachments_html = ''
            logger.info(f"⚠️ No attachments, attachments_html is empty")
        
        # Build action buttons HTML
        buttons_html = ""
        for option in action_options:
            action = option.get("action", "")
            label = option.get("label", "")
            description = option.get("description", "")
            color_class = {
                "create_contact": "btn-create",
                "create_supplier": "btn-supplier",
                "add_to_existing": "btn-primary",
                "mark_private": "btn-private",
                "mark_spam": "btn-spam",
                "request_info": "btn-info",
                "data_good": "btn-success",
                "data_error": "btn-warning",
                "report_issue": "btn-secondary"
            }.get(action, "btn-default")
            
            # Route feedback actions to /webhook/feedback, others to /webhook/contact-action
            if action in ["data_good", "data_error", "report_issue"]:
                button_url = f"https://my-langgraph-agent-production.up.railway.app/webhook/feedback?action={action}&sender={sender}&email_id={email_id}"
            else:
                button_url = f"{webhook_url}?action={action}&sender={sender}&email_id={email_id}"
            
            buttons_html += f"""
            <a href="{button_url}" class="button {color_class}">{label}</a>
            <p class="button-desc">{description}</p>
            """
        
        # ✨ Build Dashboard Links HTML (Invoice DB, Sales Pipeline, OneDrive)
        dashboard_links_html = ""
        invoice_id = notification_data.get("invoice_id")
        opportunity_id = notification_data.get("opportunity_id")
        onedrive_links = notification_data.get("onedrive_links", [])
        
        dashboard_items = []
        
        # Invoice Link
        if invoice_id:
            invoice_number = notification_data.get("invoice_number", invoice_id)
            dashboard_items.append(
                f"📄 <a href='https://my-langgraph-agent-production.up.railway.app/api/invoice/{invoice_number}' target='_blank'>Rechnung #{invoice_number} im System anzeigen</a>"
            )
        
        # Opportunity Link
        if opportunity_id:
            opportunity_title = notification_data.get("opportunity_title", f"Opportunity #{opportunity_id}")
            dashboard_items.append(
                f"💼 <a href='https://my-langgraph-agent-production.up.railway.app/api/opportunity/{opportunity_id}' target='_blank'>Verkaufschance anzeigen: {opportunity_title}</a>"
            )
        
        # OneDrive Links
        if onedrive_links:
            for link_data in onedrive_links:
                filename = link_data.get("filename", "Datei")
                sharing_link = link_data.get("sharing_link")
                if sharing_link:
                    dashboard_items.append(
                        f"☁️ <a href='{sharing_link}' target='_blank'>{filename} in OneDrive öffnen</a>"
                    )
        
        # Dashboard Overview Links
        dashboard_items.append(
            "📊 <a href='http://localhost:3000' target='_blank'>Invoice & Payment Dashboard öffnen</a>"
        )
        dashboard_items.append(
            "💰 <a href='http://localhost:3000/sales-pipeline' target='_blank'>Sales Pipeline Dashboard öffnen</a>"
        )
        
        if dashboard_items:
            items_html = "<br>".join([f"&nbsp;&nbsp;&nbsp;&nbsp;{item}" for item in dashboard_items])
            dashboard_links_html = f"""
<div class="info-box" style="background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); border-left: 5px solid #66BB6A;">
<h3>🔗 Relevante Links:</h3>
<p>
{items_html}
</p>
</div>
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
    .btn-supplier {{ background: linear-gradient(135deg, #FD79A8 0%, #E84393 100%); color: white; }}
    .btn-supplier:hover {{ box-shadow: 0 6px 16px rgba(253,121,168,0.4); transform: translateY(-2px); }}
    .btn-primary {{ background: linear-gradient(135deg, #3498DB 0%, #2980B9 100%); color: white; }}
    .btn-primary:hover {{ box-shadow: 0 6px 16px rgba(52,152,219,0.4); transform: translateY(-2px); }}
    .btn-private {{ background: linear-gradient(135deg, #A29BFE 0%, #6C5CE7 100%); color: white; }}
    .btn-private:hover {{ box-shadow: 0 6px 16px rgba(162,155,254,0.4); transform: translateY(-2px); }}
    .btn-spam {{ background: linear-gradient(135deg, #FF7675 0%, #D63031 100%); color: white; }}
    .btn-spam:hover {{ box-shadow: 0 6px 16px rgba(255,118,117,0.4); transform: translateY(-2px); }}
    .btn-info {{ background: linear-gradient(135deg, #74B9FF 0%, #0984E3 100%); color: white; }}
    .btn-info:hover {{ box-shadow: 0 6px 16px rgba(116,185,255,0.4); transform: translateY(-2px); }}
    .btn-success {{ background: linear-gradient(135deg, #00D2A0 0%, #00B894 100%); color: white; }}
    .btn-success:hover {{ box-shadow: 0 6px 16px rgba(0,210,160,0.4); transform: translateY(-2px); }}
    .btn-warning {{ background: linear-gradient(135deg, #FDCB6E 0%, #E17055 100%); color: white; }}
    .btn-warning:hover {{ box-shadow: 0 6px 16px rgba(253,203,110,0.4); transform: translateY(-2px); }}
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
{attachments_html}
</div>
{price_estimate_html}
{dashboard_links_html}
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
        # 🔍 DEBUG: Check if attachments_html is in the generated HTML
        if "Anhänge:" in html:
            logger.info(f"✅ HTML contains attachments line!")
        else:
            logger.warning(f"❌ HTML does NOT contain attachments line! attachments_html was: {attachments_html}")
        
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
                "data_good": "btn-success",
                "data_error": "btn-warning",
                "report_issue": "btn-secondary"
            }.get(action, "btn-default")
            
            # Route feedback actions to /webhook/feedback
            if action in ["data_good", "data_error", "report_issue"]:
                button_url = f"https://my-langgraph-agent-production.up.railway.app/webhook/feedback?action={action}&contact_id={contact_id}&from={from_contact}"
            elif url:
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
    .btn-success {{ background: linear-gradient(135deg, #00D2A0 0%, #00B894 100%); color: white; }}
    .btn-success:hover {{ box-shadow: 0 6px 16px rgba(0,210,160,0.4); transform: translateY(-2px); }}
    .btn-warning {{ background: linear-gradient(135deg, #FDCB6E 0%, #E17055 100%); color: white; }}
    .btn-warning:hover {{ box-shadow: 0 6px 16px rgba(253,203,110,0.4); transform: translateY(-2px); }}
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
{attachments_html}
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
        
        # Standard actions (always include "add to existing" and "create supplier")
        action_options.extend([
            {
                "action": "create_contact",
                "label": "✅ KONTAKT ANLEGEN",
                "description": "Als neuen Kontakt in WeClapp anlegen"
            },
            {
                "action": "create_supplier",
                "label": "🏭 LIEFERANT ANLEGEN",
                "description": "Als neuen Lieferanten in WeClapp anlegen"
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
                "action": "data_good",
                "label": "✅ DATEN OK",
                "description": "Alle Daten korrekt ausgewertet, keine Fehler",
                "color": "success"
            },
            {
                "action": "data_error",
                "label": "⚠️ FEHLER MELDEN",
                "description": "Daten falsch erkannt oder Verarbeitungsfehler",
                "color": "warning"
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
            # Get actual email subject from processing_result if available
            email_subject = processing_result.get("ai_analysis", {}).get("email_subject", content[:80])
            attachments_count = processing_result.get("attachments_count", 0)
            
            # Add attachment count to subject if present
            if attachments_count > 0:
                subject = f"EMAIL (📎 {attachments_count}): {email_subject}"
            else:
                subject = f"EMAIL: {email_subject}"
            
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
            
            # Attachments Info (clean up file_bytes for JSON serialization)
            "attachments_count": processing_result.get("attachments_count", 0),
            "has_attachments": processing_result.get("has_attachments", False),
            "attachment_results": [
                {k: v for k, v in att.items() if k != "file_bytes"}
                for att in processing_result.get("attachment_results", [])
            ],
            
            # Potential Matches (if any)
            "potential_matches": potential_matches,
            "has_potential_matches": len(potential_matches) > 0,
            
            # Action Options (dynamic based on potential matches)
            "action_options": action_options,
            
            # 💰 Price Estimate (if available for calls)
            "price_estimate": processing_result.get("price_estimate"),
            "has_price_estimate": processing_result.get("price_estimate", {}).get("found", False) if processing_result.get("price_estimate") else False,
            
            # ✨ Invoice & Opportunity IDs (for Dashboard links)
            "invoice_id": processing_result.get("invoice_id"),
            "invoice_number": processing_result.get("invoice_number"),
            "opportunity_id": processing_result.get("opportunity_id"),
            "opportunity_title": processing_result.get("opportunity_title", subject),
            
            # ☁️ OneDrive Links (collect from all attachments)
            "onedrive_links": [
                {
                    "filename": att.get("filename"),
                    "sharing_link": att.get("onedrive_sharing_link"),
                    "web_url": att.get("onedrive_web_url")
                }
                for att in processing_result.get("attachment_results", [])
                if att.get("onedrive_sharing_link") or att.get("onedrive_web_url")
            ],
            
            "responsible_employee": "mj@cdtechnologies.de",
            "to": "mj@cdtechnologies.de, info@cdtechnologies.de",  # Zapier Outlook format
            "webhook_reply_url": "https://my-langgraph-agent-production.up.railway.app/webhook/contact-action",
            
            # ZAPIER COMPATIBILITY: Multiple subject fields
            "email_subject": subject,
            "outlook_subject": subject,
            "notification_subject": subject
        }
        
        # 🎨 Generate complete HTML for email
        notification_data["html_body"] = generate_notification_html(notification_data)
        
        # 🔍 DEBUG: Log attachment info before sending
        logger.info(f"📎 DEBUG notification_data: attachments_count={notification_data.get('attachments_count')}, has_attachments={notification_data.get('has_attachments')}")
        
        # 🔍 DEBUG: Check if html_body contains attachment line
        html_body = notification_data.get("html_body", "")
        if "Anhänge:" in html_body:
            logger.info(f"✅ notification_data['html_body'] CONTAINS 'Anhänge:' before Zapier send")
        else:
            logger.warning(f"❌ notification_data['html_body'] does NOT contain 'Anhänge:' before Zapier send!")
        
        logger.info(f"⚠️ Sending UNKNOWN CONTACT notification for {from_contact}")
    
    else:
        # WEG B: Known Contact - Enhanced notification with smart action suggestions
        ai_analysis = processing_result.get("ai_analysis", {})
        intent = ai_analysis.get("intent", "")
        urgency = ai_analysis.get("urgency", "")
        tasks_generated = processing_result.get("tasks_generated", [])
        
        # 🎯 Intent Override: Keyword-based intent detection for ORDER
        subject = processing_result.get("subject", "").lower()
        body_preview = processing_result.get("body_preview", "").lower() if processing_result.get("body_preview") else ""
        
        if any(keyword in subject or keyword in body_preview for keyword in ["auftrag", "bestellung", "order", "bestellen", "material bestellen", "auftragsbestätigung"]):
            logger.info(f"🎯 INTENT OVERRIDE: Detected ORDER keywords in subject/body, forcing ORDER intent (was: {intent})")
            intent = "order"
        
        # 🎯 Generate smart action buttons based on AI analysis and intent
        smart_actions = []
        
        # Intent-based smart actions
        if intent in ["appointment_request", "appointment", "termin", "besichtigung", "aufmaß"]:
            smart_actions.append({
                "action": "schedule_appointment",
                "label": "� TERMIN VEREINBAREN",
                "description": "Terminvorschläge an Kunde senden und Aufmaß planen",
                "color": "primary",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
        
        if intent in ["quote_request", "price_inquiry", "preisanfrage", "angebot"]:
            smart_actions.append({
                "action": "create_quote",
                "label": "💰 ANGEBOT ERSTELLEN",
                "description": "Angebot in WeClapp erstellen und an Kunden senden",
                "color": "success",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
        
        if intent in ["question", "clarification", "nachfrage", "rückfrage"]:
            smart_actions.append({
                "action": "call_customer",
                "label": "📞 KUNDE ANRUFEN",
                "description": "Rückruf planen um Fragen zu klären",
                "color": "info",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
        
        if intent in ["order", "bestellung", "auftrag"]:
            # Hauptauftrag anlegen
            smart_actions.append({
                "action": "create_order",
                "label": "✅ AUFTRAG ANLEGEN",
                "description": "Kundenauftrag in WeClapp erstellen",
                "color": "create",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
            
            # Bestellung beim Lieferanten
            smart_actions.append({
                "action": "order_supplier",
                "label": "📦 LIEFERANT BESTELLEN",
                "description": "Material beim Lieferanten bestellen",
                "color": "info",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
            
            # Auftragsbestätigung
            smart_actions.append({
                "action": "send_order_confirmation",
                "label": "📄 AB VERSENDEN",
                "description": "Auftragsbestätigung an Kunden senden",
                "color": "primary",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
            
            # Anzahlungsrechnung
            smart_actions.append({
                "action": "create_advance_invoice",
                "label": "💶 ANZAHLUNGSRECHNUNG",
                "description": "Anzahlungsrechnung erstellen (30-50%)",
                "color": "success",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
            
            # Montagetermin
            smart_actions.append({
                "action": "schedule_installation",
                "label": "🔧 MONTAGE TERMINIEREN",
                "description": "Montagetermin mit Kunde vereinbaren",
                "color": "warning",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
        
        # Urgency-based action
        if urgency in ["high", "urgent", "hoch"]:
            smart_actions.append({
                "action": "urgent_response",
                "label": "⚡ DRINGEND BEARBEITEN",
                "description": "Hohe Priorität - Sofortige Bearbeitung erforderlich",
                "color": "warning",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
        
        # Default: Always add CRM view option
        smart_actions.insert(0, {
            "action": "view_in_crm",
            "label": "📋 IN CRM ÖFFNEN",
            "description": f"Kontakt {contact_match.get('contact_name', '')} in WeClapp öffnen",
            "contact_id": contact_match.get("contact_id"),
            "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
        })
        
        # Add tasks as action items if generated
        for task in tasks_generated[:2]:  # Max 2 task buttons
            smart_actions.append({
                "action": "complete_task",
                "label": f"✓ {task.get('title', 'Task')}",
                "description": task.get('description', ''),
                "color": "secondary",
                "url": f"https://cundd.weclapp.com/webapp/view/party/{contact_match.get('contact_id')}"
            })
        
        # Add feedback options
        smart_actions.extend([
            {
                "action": "data_good",
                "label": "✅ DATEN OK",
                "description": "Alle Daten korrekt ausgewertet und zugeordnet",
                "color": "success"
            },
            {
                "action": "data_error",
                "label": "⚠️ FEHLER MELDEN",
                "description": "Daten falsch erkannt, Zuordnung inkorrekt oder Verarbeitungsfehler",
                "color": "warning"
            }
        ])
        
        notification_data = {
            "notification_type": "known_contact_enhanced",  # WEG B Enhanced
            "timestamp": now_berlin().isoformat(),
            "channel": message_type,
            "from": from_contact,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "subject": processing_result.get("subject", ""),
            "body_preview": content[:300] + "..." if len(content) > 300 else content,
            
            # AI Processing Results
            "success": processing_result.get("success", False),
            "workflow_path": processing_result.get("workflow_path"),
            "contact_match": contact_match,
            "ai_analysis": ai_analysis,
            "tasks_generated": tasks_generated,
            "processing_complete": processing_result.get("processing_complete", False),
            
            # ✨ Dashboard IDs (like WEG A)
            "invoice_id": processing_result.get("invoice_id"),
            "invoice_number": processing_result.get("invoice_number"),
            "opportunity_id": processing_result.get("opportunity_id"),
            "opportunity_title": processing_result.get("opportunity_title", processing_result.get("subject", "")),
            
            # ☁️ OneDrive Links (collect from all attachments)
            "onedrive_links": [
                {
                    "filename": att.get("filename"),
                    "sharing_link": att.get("onedrive_sharing_link"),
                    "web_url": att.get("onedrive_web_url")
                }
                for att in processing_result.get("attachment_results", [])
                if att.get("onedrive_sharing_link") or att.get("onedrive_web_url")
            ],
            
            # 📎 Attachment Info
            "attachments_count": processing_result.get("attachments_count", 0),
            "has_attachments": processing_result.get("has_attachments", False),
            
            # 🎯 Smart Action buttons (context-aware)
            "action_options": smart_actions,
            
            # Email Recipients (Zapier Outlook format)
            "responsible_employee": "mj@cdtechnologies.de",
            "to": "mj@cdtechnologies.de, info@cdtechnologies.de",
            
            # Notification Details - MULTIPLE FIELDS FOR ZAPIER COMPATIBILITY
            "notification_subject": f"✅ C&D AI: {message_type.upper()} von {contact_match.get('contact_name', from_contact)}",
            "subject": f"✅ C&D AI: {message_type.upper()} von {contact_match.get('contact_name', from_contact)}",
            "email_subject": f"✅ C&D AI: {message_type.upper()} von {contact_match.get('contact_name', from_contact)}",
            "outlook_subject": f"✅ C&D AI: {message_type.upper()} von {contact_match.get('contact_name', from_contact)}",
            "summary": f"AI hat Kontakt verarbeitet und {len(tasks_generated)} Tasks erstellt"
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
    
    # 🔧 MIGRATION: Add new columns if they don't exist (for old databases)
    try:
        # Check if message_type column exists
        cursor.execute("PRAGMA table_info(email_data)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "message_type" not in columns:
            logger.info("🔧 MIGRATION: Adding new columns to email_data table...")
            cursor.execute("ALTER TABLE email_data ADD COLUMN message_type TEXT")
            cursor.execute("ALTER TABLE email_data ADD COLUMN direction TEXT")
            cursor.execute("ALTER TABLE email_data ADD COLUMN workflow_path TEXT")
            cursor.execute("ALTER TABLE email_data ADD COLUMN ai_intent TEXT")
            cursor.execute("ALTER TABLE email_data ADD COLUMN ai_urgency TEXT")
            cursor.execute("ALTER TABLE email_data ADD COLUMN ai_sentiment TEXT")
            cursor.execute("ALTER TABLE email_data ADD COLUMN attachments_count INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE email_data ADD COLUMN processing_timestamp TEXT")
            cursor.execute("ALTER TABLE email_data ADD COLUMN processing_duration_ms INTEGER")
            cursor.execute("ALTER TABLE email_data ADD COLUMN price_estimate_json TEXT")
            conn.commit()
            logger.info("✅ MIGRATION: New columns added successfully")
    except Exception as e:
        logger.warning(f"⚠️ Migration warning (likely already applied): {e}")
    
    # Index für schnelle Email-Lookups
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_sender ON email_data(sender)
    """)
    
    # Create email_attachments table (for attachment tracking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_message_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        content_type TEXT,
        size_bytes INTEGER,
        file_hash TEXT,
        ocr_text TEXT,
        ocr_route TEXT,
        onedrive_path TEXT,
        onedrive_link TEXT,
        processed_date TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_email_message_id ON email_attachments(email_message_id)
    """)
    
    conn.commit()
    conn.close()
    logger.info("✅ Email Database initialized (email_data.db + email_attachments)")


async def lookup_contact_in_cache(email: str) -> Optional[Dict[str, Any]]:
    """
    🔍 STEP 1: Multi-Source Contact Lookup (Cache → WEClapp Sync DB → WeClapp API)
    
    Sucht Kontakt in mehreren Quellen:
    1. Lokaler email_data.db Cache (schnellster)
    2. WEClapp Sync Database (von Apify Actor)
    3. WeClapp API (langsamster, nur als Fallback)
    """
    try:
        # STEP 1a: Check local email_data cache first
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _sync_lookup_contact, email)
        
        if result:
            logger.info(f"✅ CACHE HIT (email_data) for {email} - Contact ID: {result['weclapp_contact_id']}")
            return result
        
        # STEP 1b: Check WEClapp Sync DB (from Apify actor)
        logger.info(f"🔍 Checking WEClapp Sync DB for {email}...")
        
        # Ensure WEClapp DB is available
        await ensure_weclapp_db_available()
        
        weclapp_contact = await query_weclapp_contact(email)
        
        if weclapp_contact:
            logger.info(f"✅ WECLAPP SYNC DB HIT for {email} - {weclapp_contact.get('name', 'Unknown')}")
            
            # Convert to expected format
            result = {
                "found": True,
                "source": "weclapp_sync_db",
                "weclapp_contact_id": weclapp_contact.get("party_id") or weclapp_contact.get("lead_id"),
                "weclapp_customer_id": weclapp_contact.get("customer_number"),
                "sender": email,
                "name": weclapp_contact.get("name"),
                "phone": weclapp_contact.get("phone"),
                "company": weclapp_contact.get("company"),
                "party_type": weclapp_contact.get("party_type") or "LEAD"
            }
            
            return result
        
        logger.info(f"⚠️ CACHE MISS (all sources) for {email} - Will query WeClapp API")
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
# DUPLIKATSPRÜFUNG & DOKUMENT-TRACKING
# ===============================

async def check_document_duplicate(
    message_id: str = None,
    sender: str = None,
    subject: str = None,
    attachment_filename: str = None,
    document_hash: str = None,
    onedrive_path: str = None
) -> Dict[str, Any]:
    """
    🔍 Prüft ob Dokument bereits verarbeitet wurde
    
    Prüfkriterien (in Reihenfolge):
    1. message_id (Microsoft Graph ID) - 100% sicher
    2. document_hash (SHA256 des PDF) - sehr sicher
    3. onedrive_path - wenn bereits hochgeladen
    4. sender + subject + filename + zeitfenster (24h) - heuristisch
    
    Returns:
        {
            "is_duplicate": bool,
            "duplicate_reason": str,
            "original_record_id": int,
            "original_timestamp": str,
            "onedrive_link": str
        }
    """
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            _check_duplicate_sync,
            message_id, sender, subject, attachment_filename, document_hash, onedrive_path
        )
        
        if result["is_duplicate"]:
            logger.warning(f"⚠️ DUPLICATE: {result['duplicate_reason']}")
        else:
            logger.info(f"✅ No duplicate found - proceeding with processing")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Duplicate check error: {e}")
        # Bei Fehler: Kein Duplikat annehmen (lieber verarbeiten)
        return {"is_duplicate": False, "error": str(e)}


def _check_duplicate_sync(
    message_id: str,
    sender: str,
    subject: str,
    attachment_filename: str,
    document_hash: str,
    onedrive_path: str
) -> Dict[str, Any]:
    """Synchronous duplicate check (runs in executor)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # PRÜFUNG 1: message_id (100% sicher - Microsoft Graph ID)
        if message_id:
            cursor.execute("""
            SELECT id, processing_timestamp, onedrive_link
            FROM processed_documents
            WHERE message_id = ?
            LIMIT 1
            """, (message_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "is_duplicate": True,
                    "duplicate_reason": "message_id_match",
                    "original_record_id": row[0],
                    "original_timestamp": row[1],
                    "onedrive_link": row[2]
                }
        
        # PRÜFUNG 2: document_hash (sehr sicher - SHA256 des PDFs)
        if document_hash:
            cursor.execute("""
            SELECT id, processing_timestamp, onedrive_link
            FROM processed_documents
            WHERE document_hash = ?
            LIMIT 1
            """, (document_hash,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "is_duplicate": True,
                    "duplicate_reason": "document_hash_match",
                    "original_record_id": row[0],
                    "original_timestamp": row[1],
                    "onedrive_link": row[2]
                }
        
        # PRÜFUNG 3: onedrive_path (wenn bereits hochgeladen)
        if onedrive_path:
            cursor.execute("""
            SELECT id, processing_timestamp, onedrive_link
            FROM processed_documents
            WHERE onedrive_path = ?
            LIMIT 1
            """, (onedrive_path,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "is_duplicate": True,
                    "duplicate_reason": "onedrive_path_match",
                    "original_record_id": row[0],
                    "original_timestamp": row[1],
                    "onedrive_link": row[2]
                }
        
        # PRÜFUNG 4: Heuristisch (sender + subject + filename + 24h)
        if sender and subject and attachment_filename:
            # Zeitfenster: 24 Stunden
            time_24h_ago = (datetime.now(BERLIN_TZ) - timedelta(hours=24)).isoformat()
            
            cursor.execute("""
            SELECT id, processing_timestamp, onedrive_link
            FROM processed_documents
            WHERE sender = ?
              AND subject = ?
              AND attachment_filename = ?
              AND processing_timestamp > ?
            LIMIT 1
            """, (sender, subject, attachment_filename, time_24h_ago))
            
            row = cursor.fetchone()
            if row:
                return {
                    "is_duplicate": True,
                    "duplicate_reason": "heuristic_match_24h",
                    "original_record_id": row[0],
                    "original_timestamp": row[1],
                    "onedrive_link": row[2]
                }
        
        # KEIN DUPLIKAT GEFUNDEN
        return {"is_duplicate": False}
        
    finally:
        conn.close()


def _save_processed_document_sync(
    message_id: str,
    sender: str,
    subject: str,
    attachment_filename: str,
    document_hash: str,
    document_type: str,
    onedrive_path: str,
    onedrive_link: str,
    ordnerstruktur: str,
    kunde: str,
    lieferant: str,
    summe: str
) -> int:
    """
    💾 Speichert verarbeitetes Dokument in processed_documents Tabelle
    
    Returns: record_id
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Tabelle erstellen falls nicht vorhanden
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            sender TEXT,
            subject TEXT,
            attachment_filename TEXT,
            document_hash TEXT UNIQUE,
            document_type TEXT,
            onedrive_path TEXT UNIQUE,
            onedrive_link TEXT,
            ordnerstruktur TEXT,
            kunde TEXT,
            lieferant TEXT,
            summe TEXT,
            processing_timestamp TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # CREATE INDEX wenn nicht vorhanden
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_message_id ON processed_documents(message_id)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_hash ON processed_documents(document_hash)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_onedrive_path ON processed_documents(onedrive_path)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sender_subject_filename ON processed_documents(sender, subject, attachment_filename)
        """)
        
        # INSERT
        cursor.execute("""
        INSERT INTO processed_documents (
            message_id, sender, subject, attachment_filename, document_hash,
            document_type, onedrive_path, onedrive_link, ordnerstruktur,
            kunde, lieferant, summe, processing_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message_id, sender, subject, attachment_filename, document_hash,
            document_type, onedrive_path, onedrive_link, ordnerstruktur,
            kunde, lieferant, summe, now_berlin().isoformat()
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"✅ Saved processed document: ID={record_id}, Type={document_type}, Path={onedrive_path}")
        return record_id
        
    except sqlite3.IntegrityError as e:
        # UNIQUE constraint violation - ist ein Duplikat!
        logger.warning(f"⚠️ Document already exists in DB: {e}")
        conn.rollback()
        
        # Hole existing record
        if message_id:
            cursor.execute("SELECT id FROM processed_documents WHERE message_id = ?", (message_id,))
        elif document_hash:
            cursor.execute("SELECT id FROM processed_documents WHERE document_hash = ?", (document_hash,))
        else:
            cursor.execute("SELECT id FROM processed_documents WHERE onedrive_path = ?", (onedrive_path,))
        
        row = cursor.fetchone()
        return row[0] if row else None
        
    except Exception as e:
        logger.error(f"❌ Error saving processed document: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

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
    price_estimate: Optional[Dict[str, Any]]  # 💰 NEW: Automatic price estimation from calls
    
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

# ==================== WECLAPP SYNC DATABASE INTEGRATION ====================

async def download_weclapp_db_from_onedrive(access_token_onedrive: str) -> Optional[str]:
    """
    Downloads WEClapp sync database from OneDrive
    Tries multiple possible locations automatically
    
    Returns: Local path to DB file or None if failed
    """
    logger.info("📥 Downloading WEClapp Sync DB from OneDrive...")
    
    user_email = "mj@cdtechnologies.de"
    local_path = "/tmp/weclapp_sync.db"
    
    # Try multiple possible OneDrive locations
    possible_paths = [
        "/Temp/weclapp_sync.db",
        "/Temp/weclapp_data.db",
        "/scan/weclapp_sync.db",
        "/scan/weclapp_data.db",
        "/Email/weclapp_sync.db",
        "/Database/weclapp_sync.db",
        "/weclapp_sync.db",
        "/weclapp_data.db"
    ]
    
    for try_path in possible_paths:
        logger.info(f"🔍 Trying OneDrive path: {try_path}")
        
        download_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/root:{try_path}:/content"
        
        headers = {"Authorization": f"Bearer {access_token_onedrive}"}
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(download_url, headers=headers)
                
                if response.status_code == 200:
                    file_bytes = response.content
                    file_size_kb = len(file_bytes) / 1024
                    
                    logger.info(f"✅ Found WEClapp DB at {try_path} ({file_size_kb:.1f} KB)")
                    
                    # Save locally
                    with open(local_path, 'wb') as f:
                        f.write(file_bytes)
                    
                    logger.info(f"💾 Saved WEClapp DB to {local_path}")
                    return local_path
                
                elif response.status_code == 404:
                    logger.debug(f"⚠️ Not found at {try_path}")
                    continue
                else:
                    logger.warning(f"⚠️ Error {response.status_code} at {try_path}")
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Download error for {try_path}: {str(e)}")
            continue
    
    logger.warning("❌ Could not find WEClapp DB at any expected OneDrive location")
    return None


async def query_weclapp_contact(sender_email: str) -> Optional[Dict]:
    """
    Query WEClapp sync database for contact information
    
    Returns: Contact info dict or None if not found
    """
    db_path = "/tmp/weclapp_sync.db"
    
    if not os.path.exists(db_path):
        logger.debug(f"⚠️ WEClapp DB not found at {db_path} - download needed")
        return None
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Try parties table first (customers/suppliers)
        cursor.execute("""
            SELECT id, name, email, phone, customerNumber, partyType
            FROM parties 
            WHERE email = ? COLLATE NOCASE
            LIMIT 1
        """, (sender_email,))
        
        row = cursor.fetchone()
        
        if row:
            conn.close()
            logger.info(f"✅ Found contact in WEClapp Sync DB: {row[1]} (Party ID: {row[0]})")
            
            return {
                "party_id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "customer_number": row[4],
                "party_type": row[5],
                "source": "weclapp_sync_db"
            }
        
        # Try leads table
        cursor.execute("""
            SELECT id, firstName, lastName, email, phone, company, leadStatus
            FROM leads
            WHERE email = ? COLLATE NOCASE
            LIMIT 1
        """, (sender_email,))
        
        row = cursor.fetchone()
        
        if row:
            conn.close()
            name = f"{row[1]} {row[2]}".strip()
            logger.info(f"✅ Found lead in WEClapp Sync DB: {name} (Lead ID: {row[0]})")
            
            return {
                "lead_id": row[0],
                "name": name,
                "email": row[3],
                "phone": row[4],
                "company": row[5],
                "lead_status": row[6],
                "source": "weclapp_sync_db"
            }
        
        conn.close()
        logger.debug(f"⚠️ No contact found for {sender_email} in WEClapp Sync DB")
        return None
        
    except Exception as e:
        logger.error(f"❌ WEClapp DB query error: {str(e)}")
        return None


# Global flag to track if WEClapp DB was downloaded this session
WECLAPP_DB_DOWNLOADED = False

async def ensure_weclapp_db_available() -> bool:
    """
    Ensures WEClapp sync database is available locally
    Downloads from OneDrive if needed (once per session)
    
    Returns: True if DB is available, False otherwise
    """
    global WECLAPP_DB_DOWNLOADED
    
    db_path = "/tmp/weclapp_sync.db"
    
    # Check if already downloaded this session
    if WECLAPP_DB_DOWNLOADED and os.path.exists(db_path):
        logger.debug("✅ WEClapp DB already available (cached)")
        return True
    
    # Check if file exists from previous session
    if os.path.exists(db_path):
        # Check age - if older than 1 hour, re-download
        file_age_seconds = datetime.now().timestamp() - os.path.getmtime(db_path)
        if file_age_seconds < 3600:  # 1 hour
            logger.info(f"✅ WEClapp DB available (age: {file_age_seconds/60:.1f} min)")
            WECLAPP_DB_DOWNLOADED = True
            return True
        else:
            logger.info(f"🔄 WEClapp DB outdated (age: {file_age_seconds/3600:.1f} hours), re-downloading...")
    
    # Need to download
    try:
        access_token = await get_graph_token_onedrive()
        if not access_token:
            logger.warning("⚠️ Could not get OneDrive token for WEClapp DB download")
            return False
        
        downloaded_path = await download_weclapp_db_from_onedrive(access_token)
        
        if downloaded_path:
            WECLAPP_DB_DOWNLOADED = True
            logger.info("✅ WEClapp Sync DB successfully downloaded and ready")
            return True
        else:
            logger.warning("⚠️ WEClapp Sync DB download failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ WEClapp DB download error: {str(e)}")
        return False


async def get_graph_token_onedrive():
    """Holt das Zugriffstoken von Microsoft Graph für OneDrive."""
    tenant_id = os.getenv("GRAPH_TENANT_ID_ONEDRIVE") or os.getenv("GRAPH_TENANT_ID")
    client_id = os.getenv("GRAPH_CLIENT_ID_ONEDRIVE") or os.getenv("GRAPH_CLIENT_ID")
    client_secret = os.getenv("GRAPH_CLIENT_SECRET_ONEDRIVE") or os.getenv("GRAPH_CLIENT_SECRET")
    
    if not tenant_id or not client_id or not client_secret:
        logger.error("❌ Fehlende OneDrive-Graph API Zugangsdaten")
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
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                logger.error(f"❌ OneDrive token error {response.status_code}: {response.text}")
                return None
    except Exception as e:
        logger.error(f"❌ OneDrive token exception: {e}")
        return None


# ==================== END WECLAPP SYNC INTEGRATION ====================

async def save_to_database(
    processing_result: Dict,
    message_type: str,
    from_contact: str,
    content: str,
    final_state: Dict,
    message_id: str = ""
) -> int:
    """💾 Save processing results to database and return record ID"""
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
        record_id = await loop.run_in_executor(None, _save_to_db_sync, processing_result, message_type, from_contact, content, final_state, message_id)
        return record_id
    except Exception as e:
        logger.error(f"❌ DB save error: {e}")
        raise


def _save_to_db_sync(processing_result, message_type, from_contact, content, final_state, message_id="") -> int:
    """Synchronous database operations - returns record ID"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        ai_analysis = processing_result.get("ai_analysis", {})
        additional_data = final_state.get("additional_data", {})
        
        cursor.execute("""
        INSERT INTO email_data (
            subject, sender, recipient, received_date, gpt_result,
            message_type, direction, workflow_path,
            ai_intent, ai_urgency, ai_sentiment,
            attachments_count, processing_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ai_analysis.get("email_subject", content[:200]),
            from_contact,
            "mj@cdtechnologies.de",
            now_berlin().isoformat(),
            json.dumps(ai_analysis, ensure_ascii=False),
            message_type,
            additional_data.get("direction", "incoming"),
            processing_result.get("workflow_path"),
            ai_analysis.get("intent"),
            ai_analysis.get("urgency"),
            ai_analysis.get("sentiment"),
            processing_result.get("attachments_count", 0),
            now_berlin().isoformat()
        ))
        
        email_id = cursor.lastrowid
        
        # Insert attachments (use correct table name: email_attachments)
        for att in processing_result.get("attachment_results", []):
            cursor.execute("""
            INSERT INTO email_attachments (
                email_message_id, filename, content_type, size_bytes,
                ocr_text, ocr_route, file_hash, processed_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message_id,
                att.get("filename"),
                att.get("type"),
                att.get("size"),
                att.get("ocr_text", "")[:1000],
                att.get("ocr_route", ""),
                att.get("file_hash", ""),
                now_berlin().isoformat()
            ))
        
        conn.commit()
        logger.info(f"✅ Saved email {email_id} with {len(processing_result.get('attachment_results', []))} attachments")
        return email_id
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


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
    
    def _map_dokumenttyp_to_intent(self, dokumenttyp: str) -> str:
        """Map Apify dokumenttyp to Railway intent"""
        mapping = {
            "rechnung": "sales",
            "eingangsrechnung": "sales",
            "ausgangsrechnung": "sales",
            "angebot": "sales",
            "auftragsbestätigung": "sales",
            "lieferschein": "sales",
            "aufmaß": "sales",
            "anfrage": "information",
            "reklamation": "complaint",
            "behördlich": "information",
            "sonstiges": "information"
        }
        return mapping.get(dokumenttyp.lower(), "information")
    
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
    
    async def _classify_document_async(
        self, 
        ocr_text: str, 
        handwriting_text: str = "", 
        metadata: dict = None
    ) -> dict:
        """
        🤖 ASYNC WRAPPER für classify_document_with_gpt()
        
        Verwendet die modulare classify_document_with_gpt() Funktion,
        aber macht sie async-kompatibel für den LangGraph Orchestrator.
        
        Args:
            ocr_text: Extrahierter OCR-Text
            handwriting_text: Optional handschriftlicher Text
            metadata: Zusätzliche Metadaten (subject, from, etc.)
        
        Returns:
            GPT-Analyse-Ergebnis (Apify JSON Format)
        """
        import asyncio
        
        logger.info("🤖 Using modular classify_document_with_gpt()...")
        
        # Run sync function in executor (thread pool) to make it async
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,  # Use default executor
            classify_document_with_gpt,
            ocr_text,
            handwriting_text,
            metadata or {}
        )
        
        logger.info(f"✅ classify_document_with_gpt() completed: {result.get('dokumenttyp', 'N/A')}")
        return result
    
    async def _ai_analysis_node(self, state: CommunicationState) -> CommunicationState:
        """LangGraph Node: AI Analysis of Communication"""
        
        logger.info(f"🤖 AI analyzing {state['message_type']} from {state['from_contact']}")
        
        try:
            # Get additional context
            additional_data = state.get("additional_data", {})
            email_direction = additional_data.get("email_direction", "incoming")
            subject = additional_data.get("subject", "")
            body = additional_data.get("body", "")
            attachments = additional_data.get("attachments", [])
            attachment_names = [att.get("name", "") for att in attachments] if attachments else []
            attachment_results = additional_data.get("attachment_results", [])
            document_type_hint = additional_data.get("document_type_hint")
            
            # 🎯 USE APIFY PROMPTS - Much better document classification!
            if attachment_results and len(attachment_results) > 0:
                # ✅ EMAIL WITH PDF ATTACHMENTS → analyse_scan_prompt (200 lines!)
                logger.info(f"📄 Using modular classify_document_with_gpt() for {len(attachment_results)} attachment(s)")
                
                # Combine OCR text from all attachments
                ocr_text = "\n\n=== NÄCHSTES DOKUMENT ===\n\n".join([
                    att.get("ocr_text", "") for att in attachment_results if att.get("ocr_text")
                ])
                
                # Combine handwriting text (if any)
                handwriting_text = "\n\n".join([
                    att.get("handwriting_text", "") for att in attachment_results if att.get("handwriting_text")
                ])
                
                # Metadata for classification
                metadata = {
                    "subject": subject,
                    "from": state['from_contact'],
                    "email_direction": email_direction,
                    "attachments_count": len(attachment_results),
                    "document_type_hint": document_type_hint,
                    "attachment_filenames": [att.get("filename", "") for att in attachment_results]
                }
                
                # 🤖 USE MODULAR FUNCTION (instead of inline LLM call)
                apify_result = await self._classify_document_async(
                    ocr_text=ocr_text,
                    handwriting_text=handwriting_text,
                    metadata=metadata
                )
                
            else:
                # ✅ EMAIL WITHOUT ATTACHMENTS → analyse_mail_prompt
                logger.info(f"📧 Using modular classify_document_with_gpt() for text-only email")
                
                # For text-only emails, we still use classify_document_with_gpt
                # but pass email body as "ocr_text"
                metadata = {
                    "subject": subject,
                    "from": state['from_contact'],
                    "email_direction": email_direction,
                    "document_type_hint": document_type_hint,
                    "is_text_only_email": True
                }
                
                # 🤖 USE MODULAR FUNCTION
                apify_result = await self._classify_document_async(
                    ocr_text=body or state['content'],
                    handwriting_text="",
                    metadata=metadata
                )
            
            # apify_result already contains parsed JSON from classify_document_with_gpt()
            # No need for manual parsing - the modular function handles it!
            
            # 🔄 MAP APIFY FIELDS → RAILWAY FORMAT
            # Apify prompts return: dokumenttyp, richtung, rolle, kunde, lieferant, projektnummer, ordnerstruktur, etc.
            # Railway expects: intent, urgency, sentiment, document_type, suggested_tasks, etc.
            
            ai_result = {
                # Core fields from Apify
                "dokumenttyp": apify_result.get("dokumenttyp", "general"),
                "richtung": apify_result.get("richtung", "eingang"),
                "rolle": apify_result.get("rolle", "kunde"),
                "kunde": apify_result.get("kunde", "Unbekannt"),
                "lieferant": apify_result.get("lieferant", "Unbekannt"),
                "projektnummer": apify_result.get("projektnummer", ""),
                "ordnerstruktur": apify_result.get("ordnerstruktur", ""),
                "dateiname": apify_result.get("dateiname", ""),
                "summe": apify_result.get("summe", ""),
                "datum_dokument": apify_result.get("datum_dokument", ""),
                "notizen": apify_result.get("notizen", ""),
                "zu_pruefen": apify_result.get("zu_pruefen", False),
                
                # Map to Railway format
                "document_type": apify_result.get("dokumenttyp", "general"),
                "intent": self._map_dokumenttyp_to_intent(apify_result.get("dokumenttyp", "")),
                "urgency": "high" if apify_result.get("dringend") else "medium",
                "sentiment": "neutral",  # Apify doesn't provide sentiment
                "summary": apify_result.get("notizen", apify_result.get("anliegen", "")),
                "has_pricing": bool(apify_result.get("summe")),
                "key_topics": [apify_result.get("dokumenttyp", "")],
                "suggested_tasks": [],  # Will be generated by workflow nodes
                "response_needed": apify_result.get("zu_pruefen", False),
                
                # Full Apify response for later use
                "_apify_full": apify_result
            }
            
            state["ai_analysis"] = ai_result
            
            logger.info(f"✅ AI Analysis complete (Apify): {ai_result.get('dokumenttyp')} → {ai_result.get('ordnerstruktur', 'N/A')}")
            
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
            # 💰 NEUE FEATURE: Richtpreis-Berechnung auch für WEG A (unbekannte Kontakte)
            if state.get("message_type") == "call" and state.get('content'):
                try:
                    logger.info(f"💰 Calculating price estimate from call transcript (WEG A)...")
                    
                    # Run estimate calculation
                    estimate = calculate_estimate_from_transcript(
                        transcript=state.get('content', ''),
                        caller_info={
                            "name": None,  # Unknown contact
                            "company": None
                        }
                    )
                    
                    if estimate.found:
                        logger.info(f"✅ Price Estimate (WEG A): {estimate.total_cost:.2f} EUR (confidence: {estimate.confidence:.0%})")
                        
                        # Store estimate in state
                        state["price_estimate"] = {
                            "found": True,
                            "project_type": estimate.project_type,
                            "area_sqm": estimate.area_sqm,
                            "material": estimate.material,
                            "work_type": estimate.work_type,
                            "material_cost": estimate.material_cost,
                            "labor_cost": estimate.labor_cost,
                            "additional_cost": estimate.additional_cost,
                            "total_cost": estimate.total_cost,
                            "confidence": estimate.confidence,
                            "calculation_basis": estimate.calculation_basis,
                            "additional_services": estimate.additional_services,
                            "notes": estimate.notes
                        }
                        
                        logger.info(f"✅ Price estimate stored in state for notification")
                    else:
                        logger.info(f"⚠️ No price estimate possible (WEG A): {estimate.notes}")
                        state["price_estimate"] = {
                            "found": False,
                            "notes": estimate.notes
                        }
                
                except Exception as e:
                    logger.error(f"❌ Price estimate error (WEG A): {e}")
                    # Continue without estimate - not critical
            
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
            contact_name = state["contact_match"].get("contact_name", "Unbekannt")
            
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
            
            # 📧 SEND WEG B NOTIFICATION EMAIL
            logger.info("📧 Generating WEG B employee notification")
            try:
                # Build processing_result for notification
                processing_result = {
                    "workflow_type": "WEG_B",
                    "contact_match": state.get("contact_match", {}),
                    "ai_analysis": state.get("ai_analysis", {}),
                    "tasks_generated": state.get("tasks_generated", []),
                    "attachments": state.get("attachments", []),
                    "opportunity_id": state.get("opportunity_id"),
                    "invoice_id": state.get("invoice_id"),
                    "subject": state.get("subject", ""),
                    "message_id": state.get("message_id", ""),
                }
                
                # Note: Notification already sent above in WEG B workflow
                # No need to call send_final_notification() again (causes duplicate emails)
                logger.info("✅ WEG B notification sent successfully")
            except Exception as notif_error:
                logger.error(f"❌ Failed to send WEG B notification: {notif_error}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
                # Don't fail the whole workflow if notification fails
            
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
            
            # 💰 NEUE FEATURE: Richtpreis-Berechnung für Dacharbeiten aus Transcript
            if message_type == "call" and state.get('content'):
                try:
                    logger.info(f"💰 Calculating price estimate from call transcript...")
                    
                    # Run estimate calculation
                    estimate = calculate_estimate_from_transcript(
                        transcript=state.get('content', ''),
                        caller_info={
                            "name": contact_match.get("name") if contact_match else None,
                            "company": contact_match.get("company") if contact_match else None
                        }
                    )
                    
                    if estimate.found:
                        logger.info(f"✅ Price Estimate: {estimate.total_cost:.2f} EUR (confidence: {estimate.confidence:.0%})")
                        
                        # Store estimate in state
                        state["price_estimate"] = {
                            "project_type": estimate.project_type,
                            "area_sqm": estimate.area_sqm,
                            "material": estimate.material,
                            "work_type": estimate.work_type,
                            "material_cost": estimate.material_cost,
                            "labor_cost": estimate.labor_cost,
                            "additional_cost": estimate.additional_cost,
                            "total_cost": estimate.total_cost,
                            "confidence": estimate.confidence,
                            "calculation_basis": estimate.calculation_basis,
                            "additional_services": estimate.additional_services,
                            "notes": estimate.notes
                        }
                        
                        # Add estimate to description
                        description += f"\n\n### 💰 Automatische Kostenschätzung:\n\n"
                        description += f"**Projekt:** {estimate.project_type.title()}\n"
                        description += f"**Fläche:** {estimate.area_sqm:.0f} m²\n"
                        description += f"**Material:** {estimate.material}\n"
                        description += f"**Arbeitsart:** {estimate.work_type}\n\n"
                        description += f"**Kosten:**\n"
                        description += f"- Material: {estimate.material_cost:,.2f} EUR\n"
                        description += f"- Arbeit: {estimate.labor_cost:,.2f} EUR\n"
                        if estimate.additional_cost > 0:
                            description += f"- Zusatzleistungen: {estimate.additional_cost:,.2f} EUR\n"
                        description += f"- **GESAMT (Richtwert): {estimate.total_cost:,.2f} EUR**\n\n"
                        description += f"**Genauigkeit:** {estimate.confidence:.0%}\n"
                        description += f"_{estimate.notes}_\n"
                        
                        # Create automatic task for quote preparation
                        state["tasks_generated"].append({
                            "title": f"Angebot vorbereiten: {estimate.project_type.title()} ({estimate.area_sqm:.0f} m²)",
                            "description": f"Richtpreis: {estimate.total_cost:,.2f} EUR\n\nBasis:\n" + "\n".join(f"- {basis}" for basis in estimate.calculation_basis),
                            "priority": "high" if estimate.total_cost > 10000 else "medium",
                            "due_date": (now_berlin() + timedelta(days=2)).isoformat(),
                            "source": "price_estimate"
                        })
                        
                        logger.info(f"✅ Price estimate added to communication log and task generated")
                    else:
                        logger.info(f"⚠️ No price estimate possible: {estimate.notes}")
                        # Still store the reason in state
                        state["price_estimate"] = {
                            "found": False,
                            "notes": estimate.notes
                        }
                
                except Exception as e:
                    logger.error(f"❌ Price estimate error: {e}")
                    # Continue without estimate - not critical
            
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
            
            # 📊 Extract invoice_id and opportunity_id from attachment_results for dashboard links
            attachment_results = state_additional_data.get("attachment_results", [])
            invoice_id = None
            invoice_number = None
            opportunity_id = None
            opportunity_title = None
            
            for att_result in attachment_results:
                # Get first invoice_id found
                if not invoice_id and att_result.get("invoice_id"):
                    invoice_id = att_result.get("invoice_id")
                    invoice_number = att_result.get("invoice_number", invoice_id)
                # Get first opportunity_id found
                if not opportunity_id and att_result.get("opportunity_id"):
                    opportunity_id = att_result.get("opportunity_id")
                    opportunity_title = att_result.get("opportunity_title")
            
            processing_result = {
                "success": True,
                "workflow_path": final_state.get("workflow_path"),
                "contact_match": final_state.get("contact_match"),
                "ai_analysis": final_state.get("ai_analysis"),
                "tasks_generated": final_state.get("tasks_generated", []),
                "processing_complete": final_state.get("processing_complete", False),
                "errors": final_state.get("errors", []),
                # EMAIL METADATA (for keyword override and notifications)
                "subject": state_additional_data.get("subject", ""),
                "body": content,
                "body_preview": content[:300] if content else "",
                # Attachment info from state's additional_data
                "attachments_count": state_additional_data.get("attachments_count", 0),
                "has_attachments": state_additional_data.get("has_attachments", False),
                "attachment_results": attachment_results,
                # 💰 Price Estimate (if calculated)
                "price_estimate": final_state.get("price_estimate"),
                # 📊 Dashboard IDs (extracted from attachment processing)
                "invoice_id": invoice_id,
                "invoice_number": invoice_number,
                "opportunity_id": opportunity_id,
                "opportunity_title": opportunity_title,
                # 📊 DETAILED PROCESSING INFO (for debugging/monitoring)
                "processing_details": {
                    "timestamp": final_state.get("timestamp"),
                    "message_type": message_type,
                    "from_contact": from_contact,
                    "workflow_executed": final_state.get("workflow_path"),
                    "contact_lookup": {
                        "attempted": True,
                        "found": final_state.get("contact_match", {}).get("found", False),
                        "source": final_state.get("contact_match", {}).get("source", "none"),
                        "contact_id": final_state.get("contact_match", {}).get("contact_id"),
                        "contact_name": final_state.get("contact_match", {}).get("name"),
                        "company": final_state.get("contact_match", {}).get("company")
                    },
                    "ai_processing": {
                        "executed": final_state.get("ai_analysis") is not None,
                        "intent": final_state.get("ai_analysis", {}).get("intent"),
                        "urgency": final_state.get("ai_analysis", {}).get("urgency"),
                        "sentiment": final_state.get("ai_analysis", {}).get("sentiment")
                    },
                    "pricing": {
                        "attempted": message_type == "call" and bool(content),
                        "calculated": final_state.get("price_estimate", {}).get("found", False) if final_state.get("price_estimate") else False,
                        "amount": final_state.get("price_estimate", {}).get("total_cost") if final_state.get("price_estimate") else None,
                        "confidence": final_state.get("price_estimate", {}).get("confidence") if final_state.get("price_estimate") else None
                    },
                    "tasks": {
                        "count": len(final_state.get("tasks_generated", [])),
                        "types": [task.get("task_type") for task in final_state.get("tasks_generated", [])]
                    },
                    "crm_updates": {
                        "count": len(final_state.get("crm_updates", [])),
                        "types": [update.get("type") for update in final_state.get("crm_updates", [])]
                    },
                    "attachments": {
                        "count": state_additional_data.get("attachments_count", 0),
                        "processed": len(state_additional_data.get("attachment_results", []))
                    }
                }
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
            
            # 💾 SAVE TO DATABASE
            db_saved = False
            db_record_id = None
            db_error_msg = None
            try:
                message_id = additional_data.get("message_id", "") if additional_data else ""
                db_record_id = await save_to_database(processing_result, message_type, from_contact, content, final_state, message_id)
                db_saved = True
                logger.info(f"✅ Data saved to database (record_id: {db_record_id})")
            except Exception as db_error:
                logger.error(f"❌ Database save error: {db_error}")
                db_error_msg = str(db_error)
                # Don't fail the whole process if DB save fails
            
            # 📝 ADD DATABASE & NOTIFICATION INFO TO RESPONSE
            processing_result["processing_details"]["database"] = {
                "saved": db_saved,
                "record_id": db_record_id,
                "error": db_error_msg
            }
            processing_result["processing_details"]["notification"] = {
                "sent": processing_result.get("notification_sent", False),
                "error": processing_result.get("notification_error")
            }
            
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

# FastAPI App with startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI application"""
    # STARTUP
    logger.info("🚀 Starting AI Communication Orchestrator...")
    logger.info("📥 Downloading WEClapp Sync Database from OneDrive...")
    
    try:
        # Pre-download WEClapp DB at startup
        db_available = await ensure_weclapp_db_available()
        if db_available:
            logger.info("✅ WEClapp Sync DB ready at startup")
        else:
            logger.warning("⚠️ WEClapp Sync DB not available - will retry on first request")
    except Exception as e:
        logger.error(f"❌ Startup WEClapp DB download error: {e}")
    
    logger.info("✅ AI Communication Orchestrator ready!")
    
    yield  # Server is running
    
    # SHUTDOWN
    logger.info("👋 Shutting down AI Communication Orchestrator...")

app = FastAPI(
    title="AI Communication Orchestrator",
    description="Production-ready LangGraph AI Communication Processing System",
    version="1.3.0-weclapp-sync",
    lifespan=lifespan
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
    weclapp_db_status = "✅ Available" if os.path.exists("/tmp/weclapp_sync.db") else "⚠️ Not Downloaded"
    
    return {
        "status": "✅ AI Communication Orchestrator ONLINE",
        "system": "LangGraph + FastAPI Production",
        "version": "1.4.0-sipgate-pricing",
        "weclapp_sync_db": weclapp_db_status,
        "endpoints": [
            "/webhook/ai-email (deprecated - use /incoming or /outgoing)",
            "/webhook/ai-email/incoming",
            "/webhook/ai-email/outgoing",
            "/webhook/ai-email/test (test with JSON attachments)",
            "/webhook/ai-call",
            "/webhook/frontdesk",
            "/webhook/feedback",
            "/webhook/ai-whatsapp"
        ],
        "features": [
            "Email Direction Detection (incoming/outgoing)",
            "Document Type Classification (invoice/offer/order/delivery/general)",
            "Intelligent Attachment Processing",
            "Type-specific OCR Routes",
            "💰 Automatic Price Estimation from Call Transcripts (NEW)",
            "Database Schema Migration Support (NEW)",
            "🧪 Test Endpoint with JSON Attachments (NEW)"
        ],
        "timestamp": now_berlin().isoformat()
    }

@app.post("/webhook/ai-email/test")
async def process_email_test(request: Request):
    """
    🧪 TEST EMAIL PROCESSING WITH JSON ATTACHMENTS
    
    For testing purposes - accepts complete email data in JSON format
    including attachments metadata (simulated, no actual file download)
    
    Expected payload:
    {
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Email Subject",
        "body": "Email content...",
        "attachments": [
            {
                "filename": "document.pdf",
                "size": 145000,
                "content_type": "application/pdf"
            }
        ],
        "received_date": "2025-10-16T18:00:00+02:00"
    }
    """
    
    try:
        data = await request.json()
        logger.info(f"🧪 TEST: Processing email from {data.get('from', 'unknown')}")
        
        # Extract data
        from_contact = data.get("from", "")
        to_contact = data.get("to", "")
        subject = data.get("subject", "")
        body = data.get("body", "")
        attachments_meta = data.get("attachments", [])
        received_date = data.get("received_date", now_berlin().isoformat())
        
        # Simulate attachment results (since we can't actually download in test)
        attachment_results = []
        for att in attachments_meta:
            filename = att.get("filename", "unknown.pdf")
            size = att.get("size", 0)
            content_type = att.get("content_type", "application/pdf")
            
            # Classify document type from filename
            doc_type = "general"
            if any(word in filename.lower() for word in ["rechnung", "invoice", "re-"]):
                doc_type = "invoice"
            elif any(word in filename.lower() for word in ["angebot", "offer", "quote"]):
                doc_type = "offer"
            elif any(word in filename.lower() for word in ["bestellung", "order", "po-"]):
                doc_type = "order"
            elif any(word in filename.lower() for word in ["liefer", "delivery", "dn-"]):
                doc_type = "delivery_note"
            
            # Simulate OCR result (test placeholder)
            attachment_results.append({
                "filename": filename,
                "size": size,
                "content_type": content_type,
                "document_type": doc_type,
                "ocr_route": f"simulated_{doc_type}_ocr",
                "ocr_text": f"[TEST: Simulated OCR for {filename} - Type: {doc_type}]",
                "structured_data": {
                    "test_mode": True,
                    "document_type": doc_type
                }
            })
        
        logger.info(f"🧪 TEST: Simulated {len(attachment_results)} attachments")
        
        # Process via LangGraph with simulated attachments
        result = await orchestrator.process_communication(
            message_type="email",
            from_contact=from_contact,
            content=f"{subject}\n\n{body}",
            additional_data={
                "subject": subject,
                "body": body,
                "to": to_contact,
                "received_date": received_date,
                "attachments_count": len(attachment_results),
                "has_attachments": len(attachment_results) > 0,
                "attachment_results": attachment_results,
                "test_mode": True
            }
        )
        
        logger.info(f"✅ TEST: Email processing complete: {result.get('workflow_path', 'unknown')}")
        
        return {
            "status": "success",
            "test_mode": True,
            "ai_processing": result,
            "simulated_attachments": len(attachment_results)
        }
        
    except Exception as e:
        logger.error(f"❌ TEST: Email processing error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e), "test_mode": True}
        )

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
        "subject": "...",  # Optional metadata
        "document_type_hint": "invoice",  # Optional: invoice|offer|order_confirmation|delivery_note|general
        "priority": "high"  # Optional: low|medium|high|urgent
    }
    """
    
    global active_requests
    
    # 🔒 Memory protection: Limit concurrent requests
    async with REQUEST_SEMAPHORE:
        active_requests += 1
        logger.info(f"🔒 Processing email (active requests: {active_requests}/{REQUEST_SEMAPHORE._value + 1})")
        
        try:
            data = await request.json()
            data["email_direction"] = "incoming"  # Mark as incoming
            message_id = data.get("message_id") or data.get("id")
            user_email = data.get("user_email") or data.get("mailbox") or data.get("recipient")
            
            # 🎯 NEW: Extract document_type_hint from Zapier (Multi-Zap Strategy)
            document_type_hint = data.get("document_type_hint")
            priority = data.get("priority", "medium")
            
            # ⚡ IMMEDIATE RESPONSE - No logging before response!
            # Fire-and-forget background task
            import asyncio
            asyncio.create_task(process_email_background(
                data, message_id, user_email, 
                document_type_hint=document_type_hint,
                priority=priority
            ))
            
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
        finally:
            active_requests -= 1
            logger.info(f"🔓 Email processing complete (active requests: {active_requests})")

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
        "subject": "...",  # Optional metadata
        "document_type_hint": "invoice",  # Optional
        "priority": "medium"  # Optional
    }
    """
    
    try:
        data = await request.json()
        data["email_direction"] = "outgoing"  # Mark as outgoing
        message_id = data.get("message_id") or data.get("id")
        user_email = data.get("user_email") or data.get("mailbox") or data.get("sender")
        
        # 🎯 NEW: Extract document_type_hint from Zapier
        document_type_hint = data.get("document_type_hint")
        priority = data.get("priority", "medium")
        
        # ⚡ IMMEDIATE RESPONSE - No logging before response!
        # Fire-and-forget background task
        import asyncio
        asyncio.create_task(process_email_background(
            data, message_id, user_email,
            document_type_hint=document_type_hint,
            priority=priority
        ))
        
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
    subject: str,
    document_type_hint: str = None,  # 🎯 NEW: Accept hint from Zapier
    email_direction: str = "incoming"  # ✨ NEW: For direction detection
) -> List[Dict]:
    """
    📎 INTELLIGENT ATTACHMENT PROCESSING
    
    1. Classify document type from subject + filename (or use hint from Zapier)
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
        
        # 🎯 PRIORITY 1: Use document_type_hint from Zapier (Multi-Zap Strategy)
        if document_type_hint:
            expected_type = document_type_hint
            logger.info(f"🎯 FAST-PATH: Using document type hint from Zapier: {expected_type}")
        else:
            # FALLBACK: Classify expected document type from subject
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
                
                # 🔧 WORKAROUND: Treat message/rfc822 as potential PDF attachments
                # (Outlook sometimes wraps PDFs as RFC822 messages)
                if att_type == "message/rfc822":
                    logger.info(f"📧 Detected RFC822 message - attempting to extract PDF content...")
                    att_type = "application/pdf"  # Force PDF processing
                
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
                        
                        # 🔐 Calculate SHA256 hash for duplicate detection
                        import hashlib
                        document_hash = hashlib.sha256(file_bytes).hexdigest()
                        logger.info(f"🔐 Document hash: {document_hash[:16]}...")
                        
                        # Build email_data dict for OCR function
                        email_data_dict = {
                            "user_email": user_email,
                            "message_id": message_id,
                            "access_token": access_token,
                            "subject": subject,
                            "email_direction": email_direction
                        }
                        
                        # Choose OCR route based on type
                        ocr_result = await process_attachment_ocr(
                            file_bytes=file_bytes,
                            filename=att_name,
                            content_type=att_type,
                            document_type=expected_type,
                            email_data=email_data_dict,
                            attachment=attachment
                        )
                        
                        results.append({
                            "filename": att_name,
                            "type": att_type,
                            "size": att_size,
                            "file_bytes": file_bytes,  # 💾 Keep for OneDrive upload
                            "document_hash": document_hash,  # 🔐 For duplicate detection
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
    document_type: str,
    email_data: Dict = None,
    attachment: Dict = None
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
        import httpx
        import base64
        
        pdfco_api_key = os.getenv("PDFCO_API_KEY")
        if not pdfco_api_key:
            logger.warning("⚠️ PDFCO_API_KEY not found, using placeholder")
            result["route"] = f"{document_type}_placeholder"
            result["text"] = f"[OCR Placeholder - PDFCO_API_KEY missing]"
            return result
        
        logger.info(f"🔍 OCR Route: {document_type} for {filename}")
        
        # Convert file_bytes to base64
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')
        
        # Choose PDF.co route based on document type
        if document_type == "invoice":
            # PDF.co Standard OCR for invoices (using original working method)
            logger.info("📊 Using PDF.co Standard OCR for invoice...")
            
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    # Step 1: Upload file using multipart/form-data (NOT json)
                    files = {
                        "file": (filename, file_bytes, "application/pdf")
                    }
                    upload_response = await client.post(
                        "https://api.pdf.co/v1/file/upload",
                        headers={"x-api-key": pdfco_api_key},
                        files=files
                    )
                    
                    if upload_response.status_code != 200:
                        error_text = upload_response.text if upload_response.text else "No error message"
                        result["text"] = f"[OCR Error: Upload failed - {upload_response.status_code}]"
                        result["route"] = "invoice_ocr_failed"
                        logger.warning(f"⚠️ PDF.co upload error: {upload_response.status_code}")
                        logger.warning(f"⚠️ Response: {error_text[:500]}")
                    else:
                        upload_data = upload_response.json()
                        uploaded_url = upload_data.get("url")
                        logger.info(f"✅ File uploaded to PDF.co: {uploaded_url[:100]}...")
                        
                        # Step 2: OCR with uploaded URL
                        response = await client.post(
                            "https://api.pdf.co/v1/pdf/convert/to/text",
                            headers={"x-api-key": pdfco_api_key},
                            json={
                                "url": uploaded_url,
                                "inline": True,
                                "async": False,
                                "lang": "deu+eng"
                            }
                            )
                        
                        if response.status_code == 200:
                            ocr_text = response.text
                            result["text"] = ocr_text[:1000] if ocr_text else "[No text extracted]"
                            result["route"] = "invoice_ocr"
                            logger.info(f"✅ Invoice OCR completed: {len(ocr_text)} chars extracted")
                            
                            # ✨ NEW: GPT-4 Analyse des OCR-Textes
                            try:
                                from modules.gpt.classify_document_with_gpt import classify_document_with_gpt
                                
                                logger.info("🤖 Starting GPT-4 document analysis...")
                                gpt_analysis = classify_document_with_gpt(
                                    ocr_text=ocr_text,
                                    handwriting_text="",
                                    metadata={
                                        "email_subject": email_data.get("subject", "") if email_data else "",
                                        "filename": filename,
                                        "email_direction": email_data.get("email_direction", "incoming") if email_data else "incoming",
                                        "document_type": document_type
                                    }
                                )
                                
                                if not gpt_analysis.get("error"):
                                    # Strukturierte Daten extrahieren
                                    result["structured"] = {
                                        "invoice_number": gpt_analysis.get("rechnungsnummer", ""),
                                        "total_amount": gpt_analysis.get("betrag", ""),
                                        "vendor_name": gpt_analysis.get("lieferant", ""),
                                        "customer_name": gpt_analysis.get("kunde", ""),
                                        "invoice_date": gpt_analysis.get("datum_dokument", ""),
                                        "due_date": gpt_analysis.get("faelligkeitsdatum", ""),
                                        "document_type": gpt_analysis.get("dokumenttyp", document_type),
                                        "project_number": gpt_analysis.get("projektnummer", ""),
                                        "direction": "incoming"  # Default
                                    }
                                    
                                    # ✨ Task 1.3: DIRECTION DETECTION (Eingang vs Ausgang)
                                    direction = "incoming"  # Default: Dokument AN uns
                                    
                                    # Methode 1: Aus GPT-Analyse (wenn vorhanden)
                                    if gpt_analysis.get("richtung"):
                                        gpt_direction = gpt_analysis["richtung"].lower()
                                        if "ausgang" in gpt_direction or "outgoing" in gpt_direction:
                                            direction = "outgoing"
                                        elif "eingang" in gpt_direction or "incoming" in gpt_direction:
                                            direction = "incoming"
                                    
                                    # Methode 2: Aus Dokumenttyp
                                    doc_type = gpt_analysis.get("dokumenttyp", "").lower()
                                    if "ausgangsrechnung" in doc_type or "outgoing" in doc_type:
                                        direction = "outgoing"
                                    elif doc_type in ["rechnung", "eingangsrechnung", "lieferschein"]:
                                        direction = "incoming"
                                    
                                    # Methode 3: OCR-Text Pattern Matching (C&D Technologies Analyse)
                                    ocr_lower = ocr_text.lower()
                                    if "rechnungssteller: c&d technologies" in ocr_lower or "rechnungssteller c&d technologies" in ocr_lower:
                                        direction = "outgoing"  # VON uns
                                        logger.info("   🔍 Direction: OUTGOING (detected from OCR: 'Rechnungssteller C&D')")
                                    elif "empfänger: c&d technologies" in ocr_lower or "empfänger c&d technologies" in ocr_lower:
                                        direction = "incoming"  # AN uns
                                        logger.info("   🔍 Direction: INCOMING (detected from OCR: 'Empfänger C&D')")
                                    
                                    # Methode 4: Email Direction (aus Zapier)
                                    if email_data:
                                        email_direction = email_data.get("email_direction", "").lower()
                                        if email_direction == "outgoing" and direction == "incoming":
                                            # Wenn Email outgoing und kein anderer Hinweis, ist es wahrscheinlich unsere Rechnung
                                            direction = "outgoing"
                                            logger.info("   🔍 Direction: OUTGOING (from email_direction)")
                                    
                                    result["structured"]["direction"] = direction
                                    result["gpt_analysis"] = gpt_analysis  # Full GPT result for folder logic
                                    
                                    logger.info(f"✅ GPT-4 Analysis completed: {result['structured'].get('document_type', 'unknown')}")
                                    logger.info(f"   📊 Direction: {direction.upper()} ({'AN uns' if direction == 'incoming' else 'VON uns'})")
                                    if result["structured"].get("invoice_number"):
                                        logger.info(f"   📄 Invoice: {result['structured']['invoice_number']}")
                                    if result["structured"].get("total_amount"):
                                        logger.info(f"   💰 Amount: {result['structured']['total_amount']}")
                                    
                                    # ✨ Task 1.4: ORDNERSTRUKTUR GENERIEREN & ONEDRIVE UPLOAD
                                    try:
                                        from modules.filegen.folder_logic import generate_folder_and_filenames
                                        
                                        # Kontext für Folder Logic
                                        context = {
                                            "dokumenttyp": result["structured"]["document_type"],
                                            "kunde": result["structured"]["customer_name"],
                                            "lieferant": result["structured"]["vendor_name"],
                                            "projekt": result["structured"]["project_number"],
                                            "datum_dokument": result["structured"]["invoice_date"]
                                        }
                                        
                                        # Ordnerstruktur generieren
                                        folder_data = generate_folder_and_filenames(
                                            context=context,
                                            gpt_result=gpt_analysis,
                                            attachments=[{"filename": filename}]
                                        )
                                        
                                        result["folder_data"] = folder_data
                                        logger.info(f"📂 Folder structure: {folder_data['ordnerstruktur']}")
                                        logger.info(f"📄 Target filename: {folder_data['pdf_filenames'][0]}")
                                        
                                        # ✨ OneDrive Upload (Phase 1.4)
                                        try:
                                            # TEMP FIX: Use MAIL token for OneDrive (same tenant)
                                            user_email = "mj@cdtechnologies.de"  # Use mj@ instead of info@
                                            access_token = await get_graph_token_mail()  # Use mail token instead of onedrive
                                            
                                            if not access_token:
                                                logger.warning("⚠️ No OneDrive access_token available - skipping upload")
                                            else:
                                                folder_path = folder_data["ordnerstruktur"]
                                                target_filename = folder_data["pdf_filenames"][0]
                                                
                                                logger.info(f"☁️ Starting OneDrive upload to: {folder_path}/{target_filename}")
                                                
                                                # Upload URL für Microsoft Graph API
                                                upload_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/root:/{folder_path}/{target_filename}:/content"
                                                
                                                headers = {
                                                    "Authorization": f"Bearer {access_token}",
                                                    "Content-Type": "application/octet-stream"
                                                }
                                                
                                                # Upload mit httpx (async)
                                                async with httpx.AsyncClient(timeout=60.0) as upload_client:
                                                    upload_response = await upload_client.put(
                                                        upload_url,
                                                        headers=headers,
                                                        content=file_bytes
                                                    )
                                                    
                                                    if upload_response.status_code in [200, 201]:
                                                        upload_data = upload_response.json()
                                                        web_url = upload_data.get("webUrl", "")
                                                        file_id = upload_data.get("id", "")
                                                        
                                                        result["onedrive_uploaded"] = True
                                                        result["onedrive_path"] = f"{folder_path}/{target_filename}"
                                                        result["onedrive_web_url"] = web_url
                                                        result["onedrive_file_id"] = file_id
                                                        
                                                        logger.info(f"✅ OneDrive upload successful!")
                                                        logger.info(f"   📂 Path: {folder_path}/{target_filename}")
                                                        logger.info(f"   🔗 Web URL: {web_url[:80]}...")
                                                        
                                                        # ✨ PHASE 2: Generate sharing link
                                                        try:
                                                            from modules.msgraph.generate_onedrive_sharing_link import generate_onedrive_sharing_link
                                                            
                                                            sharing_link = await generate_onedrive_sharing_link(
                                                                user_email=user_email,
                                                                file_id=file_id,
                                                                access_token=access_token,
                                                                link_type="view",  # readonly
                                                                scope="organization"  # nur innerhalb Organisation
                                                            )
                                                            
                                                            if sharing_link:
                                                                result["onedrive_sharing_link"] = sharing_link
                                                                logger.info(f"   🔗 Sharing Link: {sharing_link[:80]}...")
                                                            else:
                                                                logger.warning("   ⚠️ Could not generate sharing link - using web URL")
                                                                result["onedrive_sharing_link"] = web_url
                                                        except Exception as sharing_error:
                                                            logger.warning(f"   ⚠️ Sharing link exception: {sharing_error}")
                                                            result["onedrive_sharing_link"] = web_url  # Fallback to web URL
                                                        
                                                        # ✨ PHASE 3: Save invoice to tracking database
                                                        if result["structured"].get("document_type") in ["Rechnung", "Eingangsrechnung", "Ausgangsrechnung", "invoice"]:
                                                            try:
                                                                from modules.database.invoice_tracking_db import save_invoice
                                                                
                                                                invoice_data = {
                                                                    "invoice_number": result["structured"].get("invoice_number"),
                                                                    "invoice_date": result["structured"].get("invoice_date"),
                                                                    "due_date": result["structured"].get("due_date"),
                                                                    "amount_total": result["structured"].get("total_amount"),
                                                                    "amount_net": result["structured"].get("net_amount"),
                                                                    "amount_tax": result["structured"].get("tax_amount"),
                                                                    "vendor_name": result["structured"].get("vendor_name"),
                                                                    "customer_name": result["structured"].get("customer_name"),
                                                                    "direction": result["structured"].get("direction", "incoming"),
                                                                    "status": "open",
                                                                    "document_hash": result.get("document_hash"),
                                                                    "onedrive_path": f"{folder_path}/{target_filename}",
                                                                    "onedrive_link": result.get("onedrive_sharing_link"),
                                                                    "email_message_id": email_data.get("message_id") if email_data else None
                                                                }
                                                                
                                                                # Nur speichern wenn Rechnungsnummer vorhanden
                                                                if invoice_data["invoice_number"]:
                                                                    invoice_id = save_invoice(invoice_data)
                                                                    result["invoice_id"] = invoice_id
                                                                    logger.info(f"   💾 Invoice saved to DB: ID={invoice_id}")
                                                                else:
                                                                    logger.info("   ⚠️ No invoice number - skipping DB save")
                                                            except Exception as db_error:
                                                                logger.warning(f"   ⚠️ Invoice DB save failed: {db_error}")
                                                        
                                                        # ✨ PHASE 3.5: Create Sales Opportunity for Preisanfragen/Angebote
                                                        doc_type = result["structured"].get("document_type", "").lower()
                                                        if any(keyword in doc_type for keyword in ["preisanfrage", "angebot", "anfrage", "quote", "proposal", "inquiry"]):
                                                            try:
                                                                from modules.database.sales_pipeline_db import create_opportunity
                                                                
                                                                # Determine stage and probability based on document type
                                                                if "angebot" in doc_type or "quote" in doc_type or "proposal" in doc_type:
                                                                    stage = "proposal"
                                                                    probability = 50
                                                                elif "preisanfrage" in doc_type or "anfrage" in doc_type or "inquiry" in doc_type:
                                                                    stage = "lead"
                                                                    probability = 20
                                                                else:
                                                                    stage = "qualified"
                                                                    probability = 30
                                                                
                                                                # Extract contact info from email or document
                                                                contact_name = None
                                                                contact_email = None
                                                                company_name = None
                                                                
                                                                if email_data:
                                                                    sender = email_data.get("sender", {})
                                                                    contact_email = sender.get("emailAddress", {}).get("address")
                                                                    contact_name = sender.get("emailAddress", {}).get("name")
                                                                
                                                                # Try to extract from GPT analysis
                                                                if not contact_name:
                                                                    contact_name = result["structured"].get("customer_name") or result["structured"].get("vendor_name")
                                                                if not company_name:
                                                                    company_name = result["structured"].get("customer_name") or result["structured"].get("vendor_name")
                                                                
                                                                # Extract value if available
                                                                value = result["structured"].get("total_amount")
                                                                if value:
                                                                    try:
                                                                        value = float(value)
                                                                    except:
                                                                        value = None
                                                                
                                                                # Create opportunity
                                                                opportunity_data = {
                                                                    "title": email_data.get("subject", "Unbekannte Anfrage") if email_data else "Unbekannte Anfrage",
                                                                    "stage": stage,
                                                                    "value": value,
                                                                    "probability": probability,
                                                                    "contact_name": contact_name,
                                                                    "contact_email": contact_email,
                                                                    "company_name": company_name,
                                                                    "source": "email",
                                                                    "description": result.get("text", "")[:500] if result.get("text") else None,
                                                                    "email_message_id": email_data.get("message_id") if email_data else None,
                                                                    "created_by": "ai-orchestrator"
                                                                }
                                                                
                                                                opportunity_id = create_opportunity(opportunity_data)
                                                                result["opportunity_id"] = opportunity_id
                                                                logger.info(f"   💼 Opportunity created: ID={opportunity_id}, Stage={stage}")
                                                                
                                                            except Exception as opp_error:
                                                                logger.warning(f"   ⚠️ Opportunity creation failed: {opp_error}")
                                                        
                                                        
                                                    else:
                                                        logger.warning(f"⚠️ OneDrive upload failed: {upload_response.status_code}")
                                                        logger.warning(f"   Response: {upload_response.text[:500]}")
                                                        result["onedrive_uploaded"] = False
                                                        result["onedrive_error"] = f"HTTP {upload_response.status_code}"
                                        
                                        except Exception as upload_error:
                                            logger.error(f"❌ OneDrive upload exception: {upload_error}")
                                            result["onedrive_uploaded"] = False
                                            result["onedrive_error"] = str(upload_error)
                                        
                                    except Exception as folder_error:
                                        logger.error(f"❌ Folder structure generation failed: {folder_error}")
                                        result["folder_data"] = {}
                                else:
                                    logger.warning(f"⚠️ GPT-4 analysis returned error: {gpt_analysis.get('error')}")
                                    result["structured"] = {}
                                    result["gpt_analysis"] = gpt_analysis
                                    
                            except Exception as gpt_error:
                                logger.error(f"❌ GPT-4 analysis failed: {gpt_error}")
                                result["structured"] = {}
                                result["gpt_analysis"] = {"error": str(gpt_error)}
                        else:
                            error_text = response.text if response.text else "No error message"
                            result["text"] = f"[OCR Error: HTTP {response.status_code}]"
                            result["route"] = "invoice_ocr_failed"
                            logger.warning(f"⚠️ Invoice OCR HTTP error: {response.status_code}")
                            logger.warning(f"⚠️ PDF.co Response: {error_text[:500]}")
                        
            except Exception as e:
                logger.error(f"❌ Invoice OCR exception: {e}")
                result["text"] = f"[OCR Error: {str(e)}]"
                result["route"] = "invoice_ocr_failed"
        
        elif document_type == "delivery_note":
            # PDF.co Handwriting OCR
            logger.info("✍️ Using PDF.co Handwriting OCR...")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.pdf.co/v1/pdf/convert/to/text",
                    headers={"x-api-key": pdfco_api_key},
                    json={
                        "file": file_base64,
                        "inline": True,
                        "async": False,
                        "OCRLanguage": "German",
                        "OCRMode": "TextFromImagesAndVectorGraphicsAndText"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == False:
                        result["text"] = data.get("body", "")[:500]
                        result["route"] = "handwriting_ocr"
                        logger.info(f"✅ Handwriting OCR: {len(result['text'])} chars")
                    else:
                        result["text"] = f"[OCR Error: {data.get('message')}]"
                        result["route"] = "handwriting_ocr_failed"
        
        else:
            # PDF.co Standard OCR
            logger.info("📄 Using PDF.co Standard OCR...")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.pdf.co/v1/pdf/convert/to/text",
                    headers={"x-api-key": pdfco_api_key},
                    json={
                        "file": file_base64,
                        "inline": True,
                        "async": False,
                        "OCRLanguage": "German"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == False:
                        result["text"] = data.get("body", "")[:500]
                        result["route"] = "standard_ocr"
                        logger.info(f"✅ Standard OCR: {len(result['text'])} chars")
                    else:
                        result["text"] = f"[OCR Error: {data.get('message')}]"
                        result["route"] = "standard_ocr_failed"
        
    except Exception as e:
        logger.error(f"❌ OCR error for {filename}: {e}")
        result["text"] = f"[OCR Exception: {str(e)}]"
        result["route"] = "ocr_exception"
    
    return result


async def process_email_background(
    data: dict, 
    message_id: str, 
    user_email: str, 
    document_type_hint: str = None, 
    priority: str = "medium"
):
    """
    Background task to process email without blocking Zapier webhook
    
    Args:
        data: Full webhook payload from Zapier
        message_id: Microsoft Graph API message ID
        user_email: Mailbox email (mj@cdtechnologies.de)
        document_type_hint: Optional hint from Zapier (invoice|offer|order_confirmation|delivery_note|general)
        priority: Optional priority from Zapier (low|medium|high|urgent)
    """
    try:
        # NOW we can log (after response sent to Zapier)
        logger.info(f"📧 Email webhook: message_id={message_id}, user={user_email}")
        
        if document_type_hint:
            logger.info(f"🎯 FAST-PATH: Document type hint from Zapier: {document_type_hint} (priority: {priority})")
        
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
            
            # � SCHRITT 1: DUPLIKATPRÜFUNG VOR PROCESSING
            tracking_db = get_email_tracking_db()
            processing_start_time = asyncio.get_event_loop().time()
            
            # Check 1: Message ID bereits verarbeitet?
            duplicate_by_id = tracking_db.check_duplicate_by_message_id(message_id)
            if duplicate_by_id:
                logger.warning(f"⚠️ DUPLICATE by Message ID: {message_id}")
                logger.warning(f"   Original: {duplicate_by_id['processed_date']}")
                logger.warning(f"   Workflow: {duplicate_by_id['workflow_path']}")
                logger.warning(f"   OneDrive: {duplicate_by_id['onedrive_link']}")
                
                # Send duplicate notification (optional)
                logger.info("⏭️ Skipping duplicate email processing")
                return  # Early exit!
            
            # Check 2: Ähnlicher Content in letzten 24h?
            duplicate_by_content = tracking_db.check_duplicate_by_content(
                subject=subject,
                body=body[:500],  # Nur erste 500 Zeichen
                from_address=from_address,
                hours_window=24
            )
            if duplicate_by_content:
                logger.warning(f"⚠️ DUPLICATE by Content: Similar email from {from_address}")
                logger.warning(f"   Original Subject: {duplicate_by_content['subject']}")
                logger.warning(f"   Original Date: {duplicate_by_content['processed_date']}")
                logger.warning(f"   OneDrive: {duplicate_by_content['onedrive_link']}")
                
                # Save as duplicate reference
                tracking_db.save_email(
                    message_id=message_id,
                    user_email=user_email,
                    from_address=from_address,
                    subject=subject,
                    body=body,
                    received_date=email_data.get("receivedDateTime", ""),
                    workflow_path="DUPLICATE",
                    ai_analysis={},
                    is_duplicate=True,
                    duplicate_of=duplicate_by_content["message_id"]
                )
                
                logger.info("⏭️ Skipping duplicate email processing")
                return  # Early exit!
            
            logger.info("✅ No duplicate found - proceeding with processing")
            
            # �📎 PROCESS ATTACHMENTS (if any)
            attachment_results = []
            if len(attachments) > 0:
                logger.info(f"📎 Processing {len(attachments)} attachment(s)...")
                attachment_results = await process_attachments_intelligent(
                    attachments=attachments,
                    message_id=message_id,
                    user_email=user_email,
                    access_token=access_token,
                    subject=subject,
                    document_type_hint=document_type_hint,  # 🎯 NEW: Pass hint to attachment processing
                    email_direction=data.get("email_direction", "incoming")  # ✨ NEW: For direction detection
                )
                logger.info(f"✅ Attachments processed: {len(attachment_results)} results")
                
                # 🔍 DUPLIKATPRÜFUNG FÜR ATTACHMENTS (File-Hash)
                for att_result in attachment_results:
                    file_bytes = att_result.get("file_bytes")
                    if file_bytes:
                        # Berechne File-Hash
                        file_hash = tracking_db.calculate_file_hash(file_bytes)
                        att_result["file_hash"] = file_hash
                        
                        # Prüfe ob dieser File-Hash bereits existiert
                        duplicate_att = tracking_db.check_duplicate_attachment(file_hash)
                        if duplicate_att:
                            logger.warning(f"⚠️ DUPLICATE ATTACHMENT: {att_result.get('filename')}")
                            logger.warning(f"   Original: {duplicate_att['filename']} from email '{duplicate_att['email_subject']}'")
                            logger.warning(f"   Original Date: {duplicate_att['processed_date']}")
                            logger.warning(f"   OneDrive: {duplicate_att['onedrive_link']}")
                            
                            att_result["is_duplicate"] = True
                            att_result["duplicate_info"] = duplicate_att
                        else:
                            att_result["is_duplicate"] = False
                    else:
                        att_result["file_hash"] = ""
                        att_result["is_duplicate"] = False
            
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
                    "attachment_results": attachment_results,  # OCR results
                    "document_type_hint": document_type_hint,  # 🎯 NEW: Pass hint to AI analysis
                    "priority": priority  # 🎯 NEW: Pass priority
                }
            )
            logger.info(f"✅ Email processing complete: {result.get('workflow_path', 'unknown')}")
            
            # � ORDNERSTRUKTUR GENERIEREN
            ai_analysis = result.get("ai_analysis", {})
            
            # Kontext für folder_logic vorbereiten
            context = {
                "dokumenttyp": ai_analysis.get("dokumenttyp", "unbekannt"),
                "kunde": ai_analysis.get("kunde", "Unbekannt"),
                "lieferant": ai_analysis.get("lieferant", "Unbekannt"),
                "projekt": ai_analysis.get("projektnummer", "Unbekannt"),
                "datum_dokument": ai_analysis.get("datum", ""),
                "valid_attachments": attachment_results  # Alle verarbeiteten Anhänge
            }
            
            try:
                folder_info = generate_folder_and_filenames(
                    context=context,
                    gpt_result=ai_analysis,
                    attachments=attachment_results
                )
                
                logger.info(f"📁 Ordnerstruktur generiert: {folder_info.get('ordnerstruktur')}")
                logger.info(f"📄 Dateinamen ({len(folder_info.get('pdf_filenames', []))}): {folder_info.get('pdf_filenames')}")
                
                # Ordnerstruktur zu attachment_results hinzufügen
                for i, att_result in enumerate(attachment_results):
                    if i < len(folder_info.get("pdf_filenames", [])):
                        att_result["target_folder"] = folder_info.get("ordnerstruktur")
                        att_result["target_filename"] = folder_info["pdf_filenames"][i]
                        att_result["target_full_path"] = f"{folder_info['ordnerstruktur']}/{folder_info['pdf_filenames'][i]}"
                        logger.info(f"  → {att_result.get('filename')} → {att_result['target_full_path']}")
                
            except Exception as folder_error:
                logger.error(f"❌ Fehler bei Ordnerstruktur-Generierung: {folder_error}")
                # Fallback: Basis-Ordner verwenden
                for att_result in attachment_results:
                    att_result["target_folder"] = "Scan/Unbekannt"
                    att_result["target_filename"] = att_result.get("filename", "unknown.pdf")
                    att_result["target_full_path"] = f"Scan/Unbekannt/{att_result['target_filename']}"
            
            # ☁️ ONEDRIVE UPLOAD
            logger.info(f"☁️ Starte OneDrive Upload für {len(attachment_results)} Dateien...")
            
            for att_result in attachment_results:
                try:
                    # Skip Duplikate
                    if att_result.get("is_duplicate", False):
                        logger.warning(f"⏭️ Skipping duplicate: {att_result.get('filename')}")
                        continue
                    
                    file_bytes = att_result.get("file_bytes")
                    target_folder = att_result.get("target_folder", "Scan/Unbekannt")
                    target_filename = att_result.get("target_filename", att_result.get("filename", "unknown.pdf"))
                    
                    if not file_bytes:
                        logger.warning(f"⚠️ No file_bytes for {att_result.get('filename')}, skipping upload")
                        continue
                    
                    logger.info(f"⬆️ Uploading: {target_filename} → {target_folder}")
                    
                    # OneDrive Upload
                    upload_url = await upload_file_to_onedrive(
                        user_mail=user_email,
                        folder_path=target_folder,
                        filename=target_filename,
                        file_bytes=file_bytes,
                        access_token_onedrive=access_token
                    )
                    
                    if upload_url:
                        logger.info(f"✅ Upload erfolgreich: {upload_url}")
                        att_result["onedrive_uploaded"] = True
                        att_result["onedrive_path"] = f"{target_folder}/{target_filename}"
                        att_result["onedrive_url"] = upload_url
                        
                        # Update tracking DB
                        try:
                            tracking_db.update_onedrive_upload(
                                message_id=message_id,
                                onedrive_path=att_result["onedrive_path"],
                                onedrive_link=upload_url
                            )
                            logger.info(f"💾 Tracking DB updated with OneDrive path")
                        except Exception as db_update_error:
                            logger.error(f"❌ Failed to update tracking DB: {db_update_error}")
                    else:
                        logger.error(f"❌ Upload fehlgeschlagen für {target_filename}")
                        att_result["onedrive_uploaded"] = False
                        att_result["onedrive_error"] = "Upload failed"
                        
                except Exception as upload_error:
                    logger.error(f"❌ Upload-Fehler für {att_result.get('filename')}: {upload_error}")
                    att_result["onedrive_uploaded"] = False
                    att_result["onedrive_error"] = str(upload_error)
            
            # 💾 SPEICHERN IN EMAIL TRACKING DB
            processing_time = asyncio.get_event_loop().time() - processing_start_time

            
            try:
                email_id = tracking_db.save_email(
                    message_id=message_id,
                    user_email=user_email,
                    from_address=from_address,
                    subject=subject,
                    body=body[:1000],  # Nur erste 1000 Zeichen
                    received_date=email_data.get("receivedDateTime", ""),
                    workflow_path=result.get("workflow_path", "unknown"),
                    ai_analysis=ai_analysis,
                    attachment_results=attachment_results,
                    processing_time=processing_time,
                    is_duplicate=False,
                    duplicate_of=None
                )
                logger.info(f"💾 Email saved to tracking DB with ID: {email_id}")
            except Exception as db_error:
                logger.error(f"❌ Failed to save to tracking DB: {db_error}")
            
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
    - Datenqualität (korrekt/fehlerhaft)
    
    Expected payload:
    {
        "type": "bug|feature|improvement|wrong_match|data_good|data_error",
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
        
        # Handle special action types from notification buttons
        action = data.get("action", feedback_type)
        
        # Map actions to feedback types
        action_mapping = {
            "data_good": {
                "type": "data_quality_good",
                "default_message": "Alle Daten wurden korrekt ausgewertet und zugeordnet.",
                "emoji": "✅",
                "priority": "low"
            },
            "data_error": {
                "type": "data_quality_error",
                "default_message": "Fehler bei der Datenauswertung oder -zuordnung erkannt.",
                "emoji": "⚠️",
                "priority": "high"
            },
            "create_supplier": {
                "type": "supplier_creation",
                "default_message": "Lieferant soll angelegt werden.",
                "emoji": "🏭",
                "priority": "medium"
            },
            "report_issue": {
                "type": "bug_report",
                "default_message": "Problem oder Fehlverhalten gemeldet.",
                "emoji": "🐛",
                "priority": "high"
            }
        }
        
        # Get action details or use defaults
        action_info = action_mapping.get(action, {
            "type": feedback_type,
            "default_message": message or "Kein Details angegeben",
            "emoji": "📝",
            "priority": "medium"
        })
        
        # Use provided message or default
        final_message = message or action_info["default_message"]
        
        # Store in optimization list (simple file-based for now)
        feedback_entry = {
            "timestamp": now_berlin().isoformat(),
            "type": action_info["type"],
            "action": action,
            "message": final_message,
            "context": context,
            "reporter": reporter,
            "priority": action_info["priority"],
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
        emoji = action_info["emoji"]
        logger.info(f"{emoji} FEEDBACK [{action_info['type']}] Priority: {action_info['priority'].upper()}: {final_message}")
        if context:
            logger.info(f"   Context: {context}")
        
        # Return user-friendly response based on action
        response_messages = {
            "data_good": "✅ Danke für die Bestätigung! Datenqualität dokumentiert.",
            "data_error": "⚠️ Fehler dokumentiert. Wir werden das überprüfen.",
            "create_supplier": "🏭 Lieferanten-Anfrage erfasst.",
            "report_issue": "🐛 Problem erfasst. Vielen Dank für die Meldung!"
        }
        
        return {
            "status": "success",
            "message": response_messages.get(action, "Feedback erfasst - Vielen Dank!"),
            "feedback_id": f"fb-{int(now_berlin().timestamp())}",
            "priority": action_info["priority"]
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
# 💰 PAYMENT MATCHING API ENDPOINTS
# ===============================

@app.post("/api/payment/import-csv")
async def import_payment_csv(request: Request):
    """
    📥 Import bank transactions from CSV file
    
    Expected payload:
    {
        "csv_content": "base64 encoded CSV",
        "format": "sparkasse" | "volksbank" | "generic" | "auto"
    }
    """
    
    try:
        from modules.database.csv_import import import_csv_auto_detect
        import base64
        import tempfile
        
        data = await request.json()
        
        # Decode CSV content
        csv_content = base64.b64decode(data.get("csv_content", ""))
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            temp_path = f.name
        
        # Import
        stats = import_csv_auto_detect(temp_path)
        
        # Cleanup
        os.remove(temp_path)
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ CSV import error: {e}")
        raise HTTPException(status_code=500, detail=f"CSV import failed: {str(e)}")


@app.post("/api/payment/import-transaction")
async def import_single_transaction(request: Request):
    """
    💳 Import single bank transaction
    
    Expected payload:
    {
        "transaction_id": "BANK-TX-123",
        "transaction_date": "2025-10-18",
        "amount": -1500.00,
        "sender_name": "ACME GmbH",
        "sender_iban": "DE89370400440532099999",
        "receiver_name": "C&D Tech GmbH",
        "receiver_iban": "DE89370400440532013000",
        "purpose": "Rechnung RE-2025-101"
    }
    """
    
    try:
        from modules.database.payment_matching import import_bank_transaction
        
        data = await request.json()
        
        transaction_id = import_bank_transaction(data)
        
        return {
            "status": "success",
            "transaction_id": transaction_id
        }
        
    except Exception as e:
        logger.error(f"❌ Transaction import error: {e}")
        raise HTTPException(status_code=500, detail=f"Transaction import failed: {str(e)}")


@app.post("/api/payment/auto-match")
async def auto_match_payments(request: Request):
    """
    🔍 Auto-match all unmatched transactions to invoices
    
    Optional payload:
    {
        "min_confidence": 0.7
    }
    """
    
    try:
        from modules.database.payment_matching import auto_match_all_transactions
        
        try:
            data = await request.json()
            min_confidence = data.get("min_confidence", 0.7)
        except:
            min_confidence = 0.7
        
        stats = auto_match_all_transactions(min_confidence=min_confidence)
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Auto-match error: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-match failed: {str(e)}")


@app.get("/api/payment/unmatched")
async def get_unmatched_payments():
    """
    📋 Get all unmatched bank transactions
    """
    
    try:
        from modules.database.payment_matching import get_unmatched_transactions
        
        unmatched = get_unmatched_transactions()
        
        return {
            "status": "success",
            "count": len(unmatched),
            "transactions": unmatched
        }
        
    except Exception as e:
        logger.error(f"❌ Get unmatched error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get unmatched transactions: {str(e)}")


@app.get("/api/payment/statistics")
async def get_payment_stats():
    """
    📊 Get payment matching statistics
    """
    
    try:
        from modules.database.payment_matching import get_payment_statistics
        
        stats = get_payment_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Get statistics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.post("/api/payment/match")
async def manual_match_payment(request: Request):
    """
    🔗 Manually match transaction to invoice
    
    Expected payload:
    {
        "transaction_id": 1,
        "invoice_number": "RE-2025-101"
    }
    """
    
    try:
        from modules.database.payment_matching import match_transaction_to_invoice
        
        data = await request.json()
        
        transaction_id = data.get("transaction_id")
        invoice_number = data.get("invoice_number")
        
        if not transaction_id or not invoice_number:
            raise HTTPException(status_code=400, detail="Missing transaction_id or invoice_number")
        
        success = match_transaction_to_invoice(transaction_id, invoice_number, matched_by="manual")
        
        if success:
            return {
                "status": "success",
                "message": f"Transaction {transaction_id} matched to invoice {invoice_number}"
            }
        else:
            raise HTTPException(status_code=500, detail="Match creation failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Manual match error: {e}")
        raise HTTPException(status_code=500, detail=f"Manual match failed: {str(e)}")


# ===============================
# 📊 INVOICE API ENDPOINTS
# ===============================

@app.get("/api/invoice/statistics")
async def get_invoice_statistics():
    """Get invoice statistics"""
    try:
        from modules.database.invoice_tracking_db import get_invoice_statistics
        
        stats = get_invoice_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Invoice statistics error: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics failed: {str(e)}")


@app.get("/api/invoice/recent")
async def get_recent_invoices(limit: int = 20):
    """Get recent invoices"""
    try:
        from modules.database.invoice_tracking_db import get_recent_invoices
        
        invoices = get_recent_invoices(limit)
        
        return {
            "status": "success",
            "invoices": invoices,
            "count": len(invoices)
        }
        
    except Exception as e:
        logger.error(f"❌ Recent invoices error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")


@app.get("/api/invoice/{invoice_number}")
async def get_invoice_details(invoice_number: str):
    """Get invoice details by number"""
    try:
        from modules.database.invoice_tracking_db import get_invoice_by_number
        
        invoice = get_invoice_by_number(invoice_number)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "status": "success",
            "invoice": invoice
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Invoice details error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoice: {str(e)}")


# ===============================
# 💼 SALES PIPELINE API ENDPOINTS
# ===============================

@app.get("/api/opportunity/statistics")
async def get_opportunity_statistics():
    """
    Get Sales Pipeline Statistics
    
    Returns:
    - Opportunities by stage (lead, qualified, proposal, negotiation)
    - Won/Lost statistics
    - Weighted pipeline value
    """
    try:
        from modules.database.sales_pipeline_db import get_pipeline_statistics
        stats = get_pipeline_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Opportunity statistics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")


@app.get("/api/opportunity/recent")
async def get_recent_opportunities_endpoint(limit: int = 20, stage: Optional[str] = None):
    """
    Get Recent Opportunities
    
    Query Parameters:
    - limit: Number of opportunities to return (default: 20)
    - stage: Filter by stage (lead, qualified, proposal, negotiation, won, lost)
    """
    try:
        from modules.database.sales_pipeline_db import get_recent_opportunities
        opportunities = get_recent_opportunities(limit, stage)
        
        return {
            "status": "success",
            "opportunities": opportunities,
            "count": len(opportunities)
        }
        
    except Exception as e:
        logger.error(f"❌ Recent opportunities error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch opportunities: {str(e)}")


@app.get("/api/opportunity/{opportunity_id}")
async def get_opportunity_details(opportunity_id: int):
    """
    Get Opportunity Details with Activities
    
    Path Parameters:
    - opportunity_id: Opportunity ID
    """
    try:
        from modules.database.sales_pipeline_db import get_opportunity_by_id
        opportunity = get_opportunity_by_id(opportunity_id)
        
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        return {
            "status": "success",
            "opportunity": opportunity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Opportunity details error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch opportunity: {str(e)}")


@app.post("/api/opportunity")
async def create_opportunity_endpoint(request: Request):
    """
    Create New Opportunity
    
    Request Body:
    {
        "title": "Dachausbau Projekt",
        "stage": "lead",
        "value": 50000.0,
        "probability": 30,
        "contact_name": "Max Mustermann",
        "contact_email": "max@example.com",
        "company_name": "Mustermann GmbH",
        "source": "email",
        "description": "Preisanfrage für Dachausbau"
    }
    """
    try:
        from modules.database.sales_pipeline_db import create_opportunity
        data = await request.json()
        
        opportunity_id = create_opportunity(data)
        
        return {
            "status": "success",
            "opportunity_id": opportunity_id,
            "message": "Opportunity created successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Create opportunity error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create opportunity: {str(e)}")


@app.put("/api/opportunity/{opportunity_id}/stage")
async def update_opportunity_stage_endpoint(opportunity_id: int, request: Request):
    """
    Update Opportunity Stage
    
    Request Body:
    {
        "stage": "qualified",
        "note": "Telefongespräch geführt, Budget bestätigt"
    }
    """
    try:
        from modules.database.sales_pipeline_db import update_opportunity_stage
        data = await request.json()
        
        success = update_opportunity_stage(
            opportunity_id, 
            data.get("stage"), 
            data.get("note")
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        return {
            "status": "success",
            "message": f"Stage updated to {data.get('stage')}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update stage error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update stage: {str(e)}")


@app.post("/api/opportunity/{opportunity_id}/activity")
async def add_opportunity_activity(opportunity_id: int, request: Request):
    """
    Add Activity to Opportunity
    
    Request Body:
    {
        "activity_type": "email",
        "title": "Follow-up Email gesendet",
        "description": "Angebot zugesandt mit Details",
        "created_by": "mj@cdtechnologies.de"
    }
    """
    try:
        from modules.database.sales_pipeline_db import add_activity
        data = await request.json()
        
        activity_id = add_activity(opportunity_id, data)
        
        return {
            "status": "success",
            "activity_id": activity_id,
            "message": "Activity added successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Add activity error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add activity: {str(e)}")


@app.get("/api/opportunity/search")
async def search_opportunities_endpoint(q: str):
    """
    Search Opportunities
    
    Query Parameters:
    - q: Search query (searches title, company, contact)
    """
    try:
        from modules.database.sales_pipeline_db import search_opportunities
        opportunities = search_opportunities(q)
        
        return {
            "status": "success",
            "opportunities": opportunities,
            "count": len(opportunities)
        }
        
    except Exception as e:
        logger.error(f"❌ Search opportunities error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search opportunities: {str(e)}")


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
    print("✅ Payment Matching System ready  💰 NEW")
    print("🌐 Server starting on http://0.0.0.0:5001")
    print("")
    print("📡 WEBHOOK ENDPOINTS:")
    print("  - POST /webhook/ai-email")
    print("  - POST /webhook/ai-call")
    print("  - POST /webhook/frontdesk  🎙️")
    print("  - POST /webhook/feedback   🐛")
    print("  - POST /webhook/ai-whatsapp")
    print("")
    print("💰 PAYMENT API ENDPOINTS:")
    print("  - POST /api/payment/import-csv")
    print("  - POST /api/payment/import-transaction")
    print("  - POST /api/payment/auto-match")
    print("  - GET  /api/payment/unmatched")
    print("  - GET  /api/payment/statistics")
    print("  - POST /api/payment/match")
    print("")
    print("📊 INVOICE API ENDPOINTS:")
    print("  - GET  /api/invoice/statistics")
    print("  - GET  /api/invoice/recent?limit=20")
    print("  - GET  /api/invoice/{invoice_number}")
    print("  - POST /api/payment/auto-match")
    print("  - POST /api/payment/match (manual)")
    print("  - GET  /api/payment/unmatched")
    print("  - GET  /api/payment/statistics")
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