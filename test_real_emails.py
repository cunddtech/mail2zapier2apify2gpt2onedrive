"""
🧪 REAL EMAIL TEST - Letzte 30 Tage mit Zapier-Filtern
=======================================================

Durchsucht echte Emails nach Zapier Filter-Kriterien und testet den kompletten Workflow.
"""

import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict
import httpx
import logging

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.auth.get_graph_token_mail import get_graph_token_mail

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ✅ ZAPIER FILTER-REGELN (1:1 aus Zapier übernommen)
ZAPIER_FILTERS = {
    "subject_keywords": [
        "rechnung", "invoice", "faktura",
        "angebot", "offer", "quote",
        "bestätigung", "confirmation",
        "lieferschein", "delivery note",
        "mahnung", "reminder", "dunning"
    ],
    "has_pdf_attachment": True,
    "min_attachment_size_kb": 10,
    "days_back": 30,
    "max_test_emails": 1  # Nur 1 Email für detaillierten Test
}


async def fetch_recent_emails(token: str, days: int = 30) -> List[Dict]:
    """Ruft Emails der letzten X Tage ab"""
    
    email_address = "mj@cdtechnologies.de"
    start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
    
    url = f"https://graph.microsoft.com/v1.0/users/{email_address}/messages"
    params = {
        "$filter": f"receivedDateTime ge {start_date} and hasAttachments eq true",
        "$select": "id,subject,from,receivedDateTime,hasAttachments,bodyPreview",
        "$orderby": "receivedDateTime desc",
        "$top": 100
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        emails = response.json().get("value", [])
        logger.info(f"📧 {len(emails)} Emails mit Anhängen gefunden")
        return emails


async def get_attachments(token: str, email_id: str) -> List[Dict]:
    """Ruft Anhänge einer Email ab"""
    
    email_address = "mj@cdtechnologies.de"
    url = f"https://graph.microsoft.com/v1.0/users/{email_address}/messages/{email_id}/attachments"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("value", [])


def filter_emails_zapier_style(emails: List[Dict], attachments_map: Dict) -> List[Dict]:
    """Wendet Zapier-Filter an"""
    
    filtered = []
    
    for email in emails:
        subject = email.get("subject", "").lower()
        
        # Filter: Betreff-Keywords
        if not any(kw in subject for kw in ZAPIER_FILTERS["subject_keywords"]):
            continue
        
        # Filter: PDF-Anhang mit Mindestgröße
        email_id = email["id"]
        attachments = attachments_map.get(email_id, [])
        
        has_valid_pdf = False
        for att in attachments:
            name = att.get("name", "").lower()
            size = att.get("size", 0)
            content_type = att.get("contentType", "").lower()
            
            if ("pdf" in name or "pdf" in content_type) and size >= ZAPIER_FILTERS["min_attachment_size_kb"] * 1024:
                has_valid_pdf = True
                break
        
        if not has_valid_pdf:
            continue
        
        filtered.append({**email, "attachments": attachments})
    
    return filtered


async def process_email_via_webhook(email: Dict, webhook_url: str) -> Dict:
    """Sendet Email an Webhook"""
    
    payload = {
        "message_id": email["id"],
        "subject": email.get("subject", ""),
        "from_email": email.get("from", {}).get("emailAddress", {}).get("address", ""),
        "from_name": email.get("from", {}).get("emailAddress", {}).get("name", ""),
        "received_datetime": email.get("receivedDateTime", ""),
        "test_mode": True
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(webhook_url, json=payload)
        
        response_data = None
        if response.status_code == 200:
            try:
                response_data = response.json()
            except:
                response_data = response.text[:500]
        else:
            response_data = response.text[:500]
        
        return {
            "status": response.status_code,
            "response": response_data,
            "subject": email.get("subject", "")[:60]
        }


async def main():
    """Hauptfunktion"""
    
    print("\n" + "="*80)
    print("🧪 REAL EMAIL TEST - Zapier Filter")
    print("="*80)
    
    # 1. Token
    print("\n1️⃣ Graph API Token...")
    token = await get_graph_token_mail()
    if not token:
        print("   ❌ Token konnte nicht geholt werden")
        return []
    print("   ✅ Token OK")
    
    # 2. Emails abrufen
    print(f"\n2️⃣ Emails der letzten {ZAPIER_FILTERS['days_back']} Tage...")
    emails = await fetch_recent_emails(token, ZAPIER_FILTERS['days_back'])
    
    # 3. Anhänge laden
    print("\n3️⃣ Anhänge laden (Top 50)...")
    attachments_map = {}
    for email in emails[:50]:
        try:
            attachments = await get_attachments(token, email["id"])
            attachments_map[email["id"]] = attachments
        except Exception as e:
            logger.warning(f"Anhänge nicht ladbar: {e}")
    
    print(f"   ✅ {len(attachments_map)} Emails mit Anhängen")
    
    # 4. Zapier-Filter
    print("\n4️⃣ Zapier-Filter anwenden...")
    print(f"   Keywords: {', '.join(ZAPIER_FILTERS['subject_keywords'][:5])}...")
    
    filtered = filter_emails_zapier_style(emails, attachments_map)
    test_emails = filtered[:ZAPIER_FILTERS['max_test_emails']]
    
    print(f"\n   ✅ {len(test_emails)} Test-Emails:")
    for i, email in enumerate(test_emails, 1):
        date = email.get("receivedDateTime", "")[:10]
        sender = email.get("from", {}).get("emailAddress", {}).get("name", "")[:20]
        subject = email.get("subject", "")[:50]
        pdf_count = sum(1 for a in email.get("attachments", []) if "pdf" in a.get("name", "").lower())
        
        print(f"      {i}. {date} | {sender} | {subject}... ({pdf_count} PDFs)")
    
    # 5. Webhook verarbeiten
    webhook_url = "https://my-langgraph-agent-production.up.railway.app/webhook/ai-email"
    
    print(f"\n5️⃣ Webhook Processing...")
    print(f"   URL: {webhook_url}")
    
    results = []
    for i, email in enumerate(test_emails, 1):
        print(f"\n   📤 [{i}/{len(test_emails)}] {email.get('subject', '')[:40]}...")
        
        try:
            result = await process_email_via_webhook(email, webhook_url)
            results.append(result)
            
            if result["status"] == 200:
                print(f"      ✅ Success")
                resp = result.get("response", {})
                
                # Detaillierte Response ausgeben
                if isinstance(resp, dict):
                    print(f"         📋 Response Details:")
                    for key, value in list(resp.items())[:8]:  # Top 8 keys
                        if key not in ["email_content", "body", "raw_content"]:  # Skip large fields
                            value_str = str(value)[:80] if value else "N/A"
                            print(f"            {key}: {value_str}")
                else:
                    print(f"         📋 Response: {str(resp)[:200]}")
            else:
                print(f"      ❌ Error {result['status']}")
                print(f"         {result.get('response', '')[:200]}")
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            results.append({"status": 500, "error": str(e), "subject": email.get("subject", "")})
        
        await asyncio.sleep(3)  # Pause zwischen Requests
    
    # 6. Summary
    print("\n" + "="*80)
    print("📊 ZUSAMMENFASSUNG")
    print("="*80)
    
    success = sum(1 for r in results if r.get("status") == 200)
    
    print(f"\n✅ Erfolgreich: {success}/{len(results)}")
    print(f"❌ Fehler: {len(results) - success}/{len(results)}")
    print(f"📈 Success Rate: {success/len(results)*100:.1f}%")
    
    print("\n" + "="*80 + "\n")
    
    return results


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    results = asyncio.run(main())
    
    success_count = sum(1 for r in results if r.get("status") == 200)
    exit(0 if success_count == len(results) else 1)
