"""
Fahrtenbuch Dashboard API - Trip Management & Matching Interface

FastAPI Endpoints für:
- Trip-Liste anzeigen (INTERNAL/MATCHED/OPEN)
- Match bearbeiten/korrigieren
- Unmatched Trips zuordnen (Kunden-Suche)
- Neue Kunden anlegen bei unbekannten Adressen
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/fahrtenbuch", tags=["Fahrtenbuch"])

# Database Path
DB_PATH = "/tmp/email_tracking.db"

# ============================================================================
# MODELS
# ============================================================================

class TripResponse(BaseModel):
    id: int
    trip_date: str
    start_time: str
    destination_address: str
    distance_km: float
    status: str
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    match_confidence: Optional[float] = None
    internal_location: Optional[str] = None
    driver_name: Optional[str] = None
    vehicle_plate: Optional[str] = None
    notes: Optional[str] = None

class TripAssignment(BaseModel):
    trip_id: int
    customer_id: str
    customer_name: str
    match_confidence: Optional[int] = 100  # Manual = 100%
    notes: Optional[str] = None

class NewCustomerData(BaseModel):
    trip_id: int
    company: str
    street: str
    zipcode: str
    city: str
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

# ============================================================================
# DATABASE HELPERS
# ============================================================================

def get_db_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """Convert sqlite3.Row to dict"""
    return dict(zip(row.keys(), row))

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/trips", response_model=Dict[str, List[TripResponse]])
async def get_trips(
    status: Optional[str] = None,
    days: int = 30
):
    """
    Get trips grouped by status
    
    Query params:
    - status: Filter by INTERNAL/MATCHED/OPEN (optional)
    - days: Last N days (default 30)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build query
    query = """
        SELECT 
            id, trip_date, start_time, destination_address, distance_km,
            status, customer_id, customer_name, match_confidence,
            internal_location, driver_name, vehicle_plate, notes
        FROM trip_logs
        WHERE trip_date >= date('now', '-' || ? || ' days')
    """
    params = [days]
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY trip_date DESC, start_time DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Group by status
    grouped = {
        "INTERNAL": [],
        "MATCHED": [],
        "OPEN": []
    }
    
    for row in rows:
        trip_dict = dict_from_row(row)
        trip_status = trip_dict['status']
        if trip_status in grouped:
            grouped[trip_status].append(TripResponse(**trip_dict))
    
    return grouped

@router.get("/trips/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: int):
    """Get single trip details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, trip_date, start_time, destination_address, distance_km,
            status, customer_id, customer_name, match_confidence,
            internal_location, driver_name, vehicle_plate, notes
        FROM trip_logs
        WHERE id = ?
    """, (trip_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return TripResponse(**dict_from_row(row))

@router.post("/trips/{trip_id}/assign")
async def assign_trip_to_customer(trip_id: int, assignment: TripAssignment = Body(...)):
    """
    Assign trip to customer (manual or correction)
    
    Body:
    {
        "trip_id": 123,
        "customer_id": "3528",
        "customer_name": "Mustermann GmbH",
        "match_confidence": 100,
        "notes": "Manuell zugeordnet"
    }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify trip exists
    cursor.execute("SELECT id FROM trip_logs WHERE id = ?", (trip_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Update trip
    cursor.execute("""
        UPDATE trip_logs
        SET 
            customer_id = ?,
            customer_name = ?,
            match_confidence = ?,
            status = 'MATCHED',
            notes = ?
        WHERE id = ?
    """, (
        assignment.customer_id,
        assignment.customer_name,
        assignment.match_confidence,
        assignment.notes,
        trip_id
    ))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Trip {trip_id} assigned to customer {assignment.customer_name}")
    
    return {
        "success": True,
        "message": f"Trip assigned to {assignment.customer_name}",
        "trip_id": trip_id
    }

@router.post("/trips/{trip_id}/unassign")
async def unassign_trip(trip_id: int):
    """Remove customer assignment from trip"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE trip_logs
        SET 
            customer_id = NULL,
            customer_name = NULL,
            match_confidence = NULL,
            status = 'OPEN'
        WHERE id = ?
    """, (trip_id,))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "Trip assignment removed",
        "trip_id": trip_id
    }

@router.get("/customers/search")
async def search_customers(q: str):
    """
    Search WeClapp customers for assignment
    
    Query param:
    - q: Search term (company name, city, address)
    """
    import os
    import requests
    
    api_token = os.getenv("WECLAPP_API_TOKEN")
    base_url = os.getenv("WECLAPP_BASE_URL")
    
    if not api_token or not base_url:
        raise HTTPException(status_code=500, detail="WeClapp API not configured")
    
    # Search WeClapp
    url = f"{base_url}customer"
    headers = {"AuthenticationToken": api_token}
    params = {"term": q, "pageSize": 20}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        customers = []
        for c in data.get("result", []):
            # Get primary address
            addresses = c.get('addresses', [])
            address_str = ""
            if addresses:
                addr = addresses[0]
                street = addr.get('street1', '')
                city = addr.get('city', '')
                zipcode = addr.get('zipcode', '')
                address_str = f"{street}, {zipcode} {city}".strip(', ')
            
            customers.append({
                "id": c.get('id'),
                "company": c.get('company', f"Kunde #{c.get('customerNumber', c.get('id'))}"),
                "customerNumber": c.get('customerNumber'),
                "address": address_str
            })
        
        return {"customers": customers}
    
    except Exception as e:
        logger.error(f"WeClapp search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/customers/create")
async def create_customer_and_assign(data: NewCustomerData = Body(...)):
    """
    Create new customer in WeClapp and assign trip
    
    Body:
    {
        "trip_id": 123,
        "company": "Neue Firma GmbH",
        "street": "Musterstraße 1",
        "zipcode": "12345",
        "city": "Musterstadt",
        "contact_first_name": "Max",
        "contact_last_name": "Mustermann",
        "email": "max@musterfirma.de",
        "phone": "+49123456789",
        "notes": "Aus Fahrtenbuch angelegt"
    }
    """
    import os
    import requests
    
    api_token = os.getenv("WECLAPP_API_TOKEN")
    base_url = os.getenv("WECLAPP_BASE_URL")
    
    if not api_token or not base_url:
        raise HTTPException(status_code=500, detail="WeClapp API not configured")
    
    # Create customer in WeClapp
    url = f"{base_url}customer"
    headers = {
        "AuthenticationToken": api_token,
        "Content-Type": "application/json"
    }
    
    customer_payload = {
        "company": data.company,
        "partyType": "ORGANIZATION",
        "addresses": [{
            "street1": data.street,
            "zipcode": data.zipcode,
            "city": data.city,
            "countryCode": "DE",
            "primeAddress": True
        }]
    }
    
    # Add contact if provided
    if data.contact_first_name or data.contact_last_name:
        customer_payload["contacts"] = [{
            "firstName": data.contact_first_name or "",
            "lastName": data.contact_last_name or "",
            "emailAddress": data.email or "",
            "phone": data.phone or ""
        }]
    
    try:
        response = requests.post(url, headers=headers, json=customer_payload, timeout=10)
        response.raise_for_status()
        new_customer = response.json()
        
        customer_id = new_customer.get('id')
        
        # Assign trip to new customer
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE trip_logs
            SET 
                customer_id = ?,
                customer_name = ?,
                match_confidence = 100,
                status = 'MATCHED',
                notes = ?
            WHERE id = ?
        """, (
            str(customer_id),
            data.company,
            f"Neuer Kunde angelegt. {data.notes or ''}",
            data.trip_id
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ New customer created: {data.company} (ID: {customer_id})")
        
        return {
            "success": True,
            "message": "Customer created and trip assigned",
            "customer_id": customer_id,
            "customer_name": data.company,
            "trip_id": data.trip_id
        }
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"WeClapp API error: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {e.response.text}")
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(days: int = 30):
    """Get fahrtenbuch statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as count,
            ROUND(SUM(distance_km), 1) as total_km,
            ROUND(AVG(distance_km), 1) as avg_km
        FROM trip_logs
        WHERE trip_date >= date('now', '-' || ? || ' days')
        GROUP BY status
    """, (days,))
    
    rows = cursor.fetchall()
    conn.close()
    
    stats = {
        "INTERNAL": {"count": 0, "total_km": 0, "avg_km": 0},
        "MATCHED": {"count": 0, "total_km": 0, "avg_km": 0},
        "OPEN": {"count": 0, "total_km": 0, "avg_km": 0}
    }
    
    for row in rows:
        row_dict = dict_from_row(row)
        status = row_dict['status']
        if status in stats:
            stats[status] = {
                "count": row_dict['count'],
                "total_km": row_dict['total_km'],
                "avg_km": row_dict['avg_km']
            }
    
    return {
        "days": days,
        "stats": stats,
        "total": {
            "count": sum(s['count'] for s in stats.values()),
            "total_km": sum(s['total_km'] for s in stats.values())
        }
    }
