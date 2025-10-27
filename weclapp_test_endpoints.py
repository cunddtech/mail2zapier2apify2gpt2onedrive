"""
🧪 WEClapp Fallback Database Test Endpoint
Test the fallback database functionality and contact lookup
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ContactCreateRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    contact_type: str = "lead"  # "lead" or "customer"

class ContactSearchRequest(BaseModel):
    email: str

@router.get("/api/weclapp/status")
async def get_weclapp_database_status():
    """
    📊 Get WEClapp database status including fallback information
    """
    try:
        from modules.database.weclapp_fallback import get_weclapp_fallback_db
        import os
        
        fallback_db = get_weclapp_fallback_db()
        stats = fallback_db.get_statistics()
        
        # Check OneDrive database status
        onedrive_db_available = os.path.exists("/tmp/weclapp_sync.db")
        
        return {
            "status": "success",
            "onedrive_db_available": onedrive_db_available,
            "fallback_db_active": True,
            "fallback_db_path": "/tmp/weclapp_fallback.db",
            "statistics": stats,
            "timestamp": "2025-10-26T19:50:00"
        }
        
    except Exception as e:
        logger.error(f"❌ WEClapp status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.post("/api/weclapp/contact/search")
async def search_contact(request: ContactSearchRequest):
    """
    🔍 Search for contact in WEClapp database (OneDrive + Fallback)
    """
    try:
        from modules.database.weclapp_fallback import query_weclapp_contact_with_fallback
        
        contact = await query_weclapp_contact_with_fallback(request.email)
        
        if contact:
            return {
                "status": "found",
                "contact": contact,
                "timestamp": "2025-10-26T19:50:00"
            }
        else:
            return {
                "status": "not_found",
                "email": request.email,
                "message": "Contact not found in any database",
                "timestamp": "2025-10-26T19:50:00"
            }
        
    except Exception as e:
        logger.error(f"❌ Contact search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/api/weclapp/contact/create")
async def create_contact(request: ContactCreateRequest):
    """
    ➕ Add new contact to fallback database
    """
    try:
        from modules.database.weclapp_fallback import get_weclapp_fallback_db
        
        fallback_db = get_weclapp_fallback_db()
        
        contact_id = fallback_db.add_contact(
            name=request.name,
            email=request.email,
            phone=request.phone,
            company=request.company,
            contact_type=request.contact_type
        )
        
        if contact_id:
            return {
                "status": "created",
                "contact_id": contact_id,
                "contact": {
                    "name": request.name,
                    "email": request.email,
                    "phone": request.phone,
                    "company": request.company,
                    "contact_type": request.contact_type
                },
                "database": "fallback",
                "timestamp": "2025-10-26T19:50:00"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create contact")
        
    except Exception as e:
        logger.error(f"❌ Contact creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Creation failed: {str(e)}")

@router.get("/api/weclapp/contacts/list")
async def list_contacts():
    """
    📋 List all contacts in fallback database (for testing)
    """
    try:
        from modules.database.weclapp_fallback import get_weclapp_fallback_db
        import sqlite3
        
        fallback_db = get_weclapp_fallback_db()
        
        # Get all contacts from fallback database
        conn = sqlite3.connect("/tmp/weclapp_fallback.db")
        cursor = conn.cursor()
        
        # Get parties
        cursor.execute("SELECT id, name, email, phone, customerNumber, partyType FROM parties ORDER BY name")
        parties = cursor.fetchall()
        
        # Get leads
        cursor.execute("SELECT id, firstName, lastName, email, phone, company, leadStatus FROM leads ORDER BY firstName, lastName")
        leads = cursor.fetchall()
        
        conn.close()
        
        contacts = []
        
        # Add parties
        for party in parties:
            contacts.append({
                "id": party[0],
                "name": party[1],
                "email": party[2],
                "phone": party[3],
                "customer_number": party[4],
                "type": "party",
                "party_type": party[5]
            })
        
        # Add leads
        for lead in leads:
            contacts.append({
                "id": lead[0],
                "name": f"{lead[1]} {lead[2]}".strip(),
                "email": lead[3],
                "phone": lead[4],
                "company": lead[5],
                "type": "lead",
                "lead_status": lead[6]
            })
        
        return {
            "status": "success",
            "total_contacts": len(contacts),
            "contacts": contacts,
            "database": "fallback",
            "timestamp": "2025-10-26T19:50:00"
        }
        
    except Exception as e:
        logger.error(f"❌ Contact list error: {e}")
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")