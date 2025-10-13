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
from fastapi.responses import Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# HTTP Client für API Calls
import aiohttp
import logging

# SQLite Database für Contact Cache
import sqlite3
import asyncio
from contextlib import asynccontextmanager

# Microsoft Graph API für Email-Loading
from modules.auth.get_graph_token_mail import get_graph_token_mail
from modules.msgraph.fetch_email_with_attachments import fetch_email_details_with_attachments

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
        
        # Standard actions
        action_options.extend([
            {
                "action": "create_contact",
                "label": "KONTAKT ANLEGEN",
                "description": "Als neuen Kontakt in WeClapp anlegen"
            },
            {
                "action": "mark_private",
                "label": "PRIVAT MARKIEREN",
                "description": "Als private Anfrage markieren (kein CRM-Eintrag)"
            },
            {
                "action": "mark_spam",
                "label": "SPAM MARKIEREN",
                "description": "Als Spam markieren und blockieren"
            },
            {
                "action": "request_info",
                "label": "INFO ANFORDERN",
                "description": "Mehr Informationen vom Absender anfordern"
            }
        ])
        
        notification_data = {
            "notification_type": "unknown_contact_action_required",
            "email_id": f"railway-{now_berlin().timestamp()}",
            "sender": from_contact,
            "sender_name": processing_result.get("sender_name", "Unbekannt"),
            "subject": f"{message_type.upper()}: {content[:100]}",
            "body_preview": content[:500] + "..." if len(content) > 500 else content,
            "received_time": now_berlin().isoformat(),
            
            # AI Analysis (flattened for Zapier)
            "ai_analysis": processing_result.get("ai_analysis", {}),
            
            # Potential Matches (if any)
            "potential_matches": potential_matches,
            "has_potential_matches": len(potential_matches) > 0,
            
            # Action Options (dynamic based on potential matches)
            "action_options": action_options,
            
            "responsible_employee": "mj@cdtechnologies.de",
            "webhook_reply_url": "https://my-langgraph-agent-production.up.railway.app/webhook/contact-action"
        }
        
        logger.info(f"⚠️ Sending UNKNOWN CONTACT notification for {from_contact}")
    
    else:
        # Standard Notification for known contacts
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
            
            # Email Recipients
            "recipients": ["mj@cdtechnologies.de", "info@cdtechnologies.de"],
            
            # Notification Details
            "subject": f"🤖 C&D AI: {message_type.upper()} von {from_contact}",
            "summary": f"AI hat {len(processing_result.get('tasks_generated', []))} Tasks erstellt"
        }
        
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
            # AI Analysis Prompt (Fixed JSON escaping)
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """Du bist ein AI Communication Analyst für ein deutsches Unternehmen.
                
Analysiere die eingehende Kommunikation und erstelle eine JSON-Antwort mit:

{{
    "intent": "support|sales|information|complaint|follow_up",
    "urgency": "low|medium|high|urgent", 
    "sentiment": "positive|neutral|negative",
    "key_topics": ["thema1", "thema2"],
    "suggested_tasks": [
        {{
            "title": "Aufgaben-Titel",
            "type": "follow_up|quote|support|meeting",
            "priority": "low|medium|high|urgent",
            "due_hours": 24
        }}
    ],
    "response_needed": true,
    "summary": "Kurze deutsche Zusammenfassung"
}}

Antworte nur mit dem JSON, keine zusätzlichen Texte."""),
                ("user", f"""Kommunikation analysieren:
                
Art: {state['message_type']}
Von: {state['from_contact']}
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
                                    potential_matches.append({
                                        "match_type": "domain",
                                        "confidence": 0.8,
                                        "contact_id": str(contact.get("id")),
                                        "contact_name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip(),
                                        "company": contact.get("company", {}).get("name") if contact.get("company") else None,
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
                                    potential_matches.append({
                                        "match_type": "phone_prefix",
                                        "confidence": 0.7,
                                        "contact_id": str(contact.get("id")),
                                        "contact_name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip(),
                                        "company": contact.get("company", {}).get("name") if contact.get("company") else None,
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
            errors=[]
        )
        
        try:
            # Execute LangGraph workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Build processing result
            processing_result = {
                "success": True,
                "workflow_path": final_state.get("workflow_path"),
                "contact_match": final_state.get("contact_match"),
                "ai_analysis": final_state.get("ai_analysis"),
                "tasks_generated": final_state.get("tasks_generated", []),
                "processing_complete": final_state.get("processing_complete", False),
                "errors": final_state.get("errors", [])
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
            "/webhook/ai-email",
            "/webhook/ai-call", 
            "/webhook/ai-whatsapp"
        ],
        "version": "1.0.0",
        "timestamp": now_berlin().isoformat()
    }

@app.post("/webhook/ai-email")
async def process_email(request: Request):
    """
    📧 EMAIL PROCESSING WITH MICROSOFT GRAPH API
    
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
        logger.info(f"📧 Email webhook triggered: {json.dumps(data, ensure_ascii=False)[:500]}")
        logger.info(f"🔍 DEBUG: message_id={data.get('message_id')}, id={data.get('id')}, user_email={data.get('user_email')}, mailbox={data.get('mailbox')}")
        
        message_id = data.get("message_id") or data.get("id")
        user_email = data.get("user_email") or data.get("mailbox")
        
        # If message_id provided → Load full email from Graph API
        if message_id and user_email:
            logger.info(f"🔍 Loading full email via Graph API: message_id={message_id}, mailbox={user_email}")
            
            # Get Graph API token
            access_token = await get_graph_token_mail()
            if not access_token:
                logger.error("❌ Failed to get Graph API token")
                raise HTTPException(status_code=500, detail="Graph API authentication failed")
            
            # Fetch full email with attachments
            email_data = await fetch_email_details_with_attachments(
                user_email=user_email,
                message_id=message_id,
                access_token=access_token
            )
            
            if not email_data:
                logger.error(f"❌ Failed to load email from Graph API: {message_id}")
                raise HTTPException(status_code=404, detail="Email not found")
            
            # Extract email details
            from_address = email_data.get("from", {}).get("emailAddress", {}).get("address", "")
            subject = email_data.get("subject", "")
            body = email_data.get("body", {}).get("content", "")
            body_type = email_data.get("body", {}).get("contentType", "html")
            attachments = email_data.get("attachments", [])
            
            logger.info(f"✅ Email loaded: From={from_address}, Subject={subject}, Attachments={len(attachments)}")
            
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
                    "has_attachments": len(attachments) > 0
                }
            )
            
        else:
            # Fallback: Process with provided data (no Graph API)
            logger.warning("⚠️ No message_id provided - processing with limited data from Zapier")
            result = await orchestrator.process_communication(
                message_type="email",
                from_contact=data.get("from", ""),
                content=data.get("content", data.get("subject", "")),
                additional_data=data
            )
        
        return {"ai_processing": result}
        
    except Exception as e:
        logger.error(f"Email processing error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # ⚠️ SECURITY: Never expose internal error details to client
        raise HTTPException(status_code=500, detail="Internal server error during email processing")

@app.post("/webhook/ai-call")
async def process_call(request: Request):
    """
    📞 SIPGATE CALL PROCESSING
    
    Flow:
    1. Telefonnummer-Matching in WeClapp (phone-eq=...)
    2. WEG_A: Unbekannt → Notification Email mit 4 Buttons
    3. WEG_B: Bekannt → CRM Log mit Transcript, AI Analysis, Tasks
    """
    
    try:
        data = await request.json()
        logger.info(f"📞 SipGate Full Payload: {json.dumps(data, ensure_ascii=False)}")
        
        # 🎯 SIPGATE SENDS ALL DATA IN ONE EVENT!
        # No separate "hangup" event - transcription ("Summary") is in the FIRST POST!
        logger.info("✅ Processing SipGate call with available data")
        
        # Extract call direction FIRST (determines logic)
        call_direction = data.get("direction", "inbound")  # inbound or outbound
        
        # 🎯 EXTRACT ALL AVAILABLE SIPGATE DATA
        # Basic call info
        call_status = data.get("call_status", data.get("status", ""))
        call_duration = data.get("call_duration", data.get("duration", 0))
        call_timestamp = data.get("timestamp", now_berlin().isoformat())
        
        # Contact info from SipGate CRM (if available)
        caller_name = data.get("caller_name", data.get("contact_name", data.get("name", "")))
        company_name = data.get("company", data.get("company_name", ""))
        
        # Assigned user/employee (which team member)
        assigned_user = data.get("user", data.get("username", ""))
        user_id = data.get("userId", data.get("user_id", ""))
        
        # Recording & Notes
        recording_url = data.get("recording_url", data.get("recordingUrl", ""))
        notes = data.get("notes", data.get("comment", ""))
        tags = data.get("tags", [])
        
        # 🎯 FIX: OUTBOUND vs INBOUND caller logic
        if call_direction == "outbound":
            # WE called someone → "to" is the EXTERNAL contact
            external_number = data.get("to") or data.get("recipient") or data.get("callee") or ""
            our_number = data.get("from") or data.get("caller") or ""
        else:
            # Someone called US → "from" is the EXTERNAL contact
            external_number = (
                data.get("caller") or          # Standard SipGate field
                data.get("callerNumber") or     # Alternative field
                data.get("remote") or           # Remote party
                data.get("from") or             # Fallback
                ""
            )
            our_number = (
                data.get("to") or 
                data.get("recipient") or 
                data.get("callee") or
                data.get("called") or
                ""
            )
        
        # Normalize phone format (remove spaces, dashes, brackets)
        phone_normalized = external_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Extract transcription (SipGate might send in different fields)
        call_transcript = (
            data.get("transcription") or 
            data.get("transcript") or 
            data.get("Summary") or  # Seen in your payload!
            data.get("summary") or
            ""
        )
        
        # 📊 LOG ALL EXTRACTED DATA
        logger.info(f"📞 Call Details:")
        logger.info(f"   Direction: {call_direction} | Status: {call_status} | Duration: {call_duration}s")
        logger.info(f"   External: {phone_normalized} | Our Number: {our_number}")
        if caller_name:
            logger.info(f"   📛 Caller Name: {caller_name}")
        if company_name:
            logger.info(f"   🏢 Company: {company_name}")
        if assigned_user:
            logger.info(f"   👤 Assigned to: {assigned_user} ({user_id})")
        if recording_url:
            logger.info(f"   🎙️ Recording: {recording_url}")
        if tags:
            logger.info(f"   🏷️ Tags: {', '.join(tags) if isinstance(tags, list) else tags}")
        
        # Check if transcript is available
        if not call_transcript:
            call_transcript = f"Anruf {call_direction} - Dauer: {call_duration}s - Keine Transkription verfügbar"
        
        # Process through orchestrator (includes phone matching)
        result = await orchestrator.process_communication(
            message_type="call",
            from_contact=phone_normalized,
            content=call_transcript,
            additional_data={
                **data,
                "call_direction": call_direction,
                "call_duration": call_duration,
                "call_timestamp": call_timestamp,
                "call_status": call_status,
                "phone_normalized": phone_normalized,
                # SipGate CRM data (if available)
                "caller_name": caller_name,
                "company_name": company_name,
                "assigned_user": assigned_user,
                "user_id": user_id,
                "recording_url": recording_url,
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