#!/usr/bin/env python3
"""
🎯 Direct Webhook Trigger - Bypass Zapier
==========================================

Triggert Railway Webhook direkt mit einer Test-Message-ID
aus dem Microsoft Graph Postfach.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Configuration
RAILWAY_URL = "https://my-langgraph-agent-production.up.railway.app"
WEBHOOK_ENDPOINT = "/webhook/ai-email"
USER_EMAIL = os.getenv("USER_EMAIL", "mj@cdtechnologies.de")  # Allow override via env
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

def get_graph_token():
    """Get Microsoft Graph API token"""
    tenant_id = os.getenv("GRAPH_TENANT_ID_MAIL")
    client_id = os.getenv("GRAPH_CLIENT_ID_MAIL")
    client_secret = os.getenv("GRAPH_CLIENT_SECRET_MAIL")
    
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json().get("access_token")

def search_email_by_subject(token, subject_keyword):
    """Search for email by subject in Inbox"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get recent emails from Inbox
    url = f"{GRAPH_API_BASE}/users/{USER_EMAIL}/mailFolders/Inbox/messages"
    params = {
        "$top": 10,
        "$orderby": "receivedDateTime desc",
        "$select": "id,subject,from,receivedDateTime"
    }
    
    print(f"🔍 Getting recent emails from Inbox...")
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    all_messages = response.json().get("value", [])
    
    # Filter by subject keyword (case insensitive)
    messages = [msg for msg in all_messages 
                if subject_keyword.lower() in msg.get("subject", "").lower()]
    
    if not messages:
        print(f"\n❌ No emails found with subject containing '{subject_keyword}'")
        print(f"\n📋 Recent emails in Inbox:")
        for i, msg in enumerate(all_messages[:5], 1):
            from_email = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
            print(f"   {i}. {msg['subject']}")
            print(f"      From: {from_email}")
        return None
    
    print(f"\n📧 Found {len(messages)} matching email(s):")
    for i, msg in enumerate(messages, 1):
        from_email = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
        received = msg.get("receivedDateTime", "Unknown")
        print(f"   {i}. {msg['subject']}")
        print(f"      From: {from_email}")
        print(f"      Received: {received}")
        print(f"      ID: {msg['id'][:30]}...")
    
    return messages[0]  # Return most recent

def trigger_webhook(message_id, subject_hint=None):
    """Trigger Railway webhook with message_id"""
    url = f"{RAILWAY_URL}{WEBHOOK_ENDPOINT}"
    
    payload = {
        "message_id": message_id,
        "user_email": USER_EMAIL,
        "document_type_hint": "general",
        "priority": "medium"
    }
    
    if subject_hint:
        payload["subject_hint"] = subject_hint
    
    print(f"\n📤 Triggering Railway webhook...")
    print(f"   URL: {url}")
    print(f"   Message ID: {message_id[:30]}...")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"\n✅ Webhook Response: {response.status_code}")
        print(f"   {response.json()}")
        
        if response.status_code == 200:
            print("\n🎉 Webhook triggered successfully!")
            print("⏳ Email is being processed in background...")
            print("   Check Railway logs: railway logs --tail 50")
            print("   Check email inbox in ~30-60 seconds for notification")
            return True
        else:
            print(f"\n❌ Webhook failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error triggering webhook: {e}")
        return False

def main():
    print("=" * 60)
    print("🎯 DIRECT WEBHOOK TRIGGER")
    print("=" * 60)
    
    # Get subject keyword from command line or use default
    subject_keyword = sys.argv[1] if len(sys.argv) > 1 else "Anfrage Dachausbau"
    
    try:
        # Step 1: Get Graph API token
        print("\n🔐 Getting Microsoft Graph API token...")
        token = get_graph_token()
        print("✅ Token acquired")
        
        # Step 2: Search for email
        email = search_email_by_subject(token, subject_keyword)
        
        if not email:
            print("\n💡 Try again with a different subject keyword:")
            print("   python3 trigger_webhook_directly.py 'keyword'")
            return
        
        # Step 3: Confirm
        print(f"\n⚠️  Will trigger webhook for:")
        print(f"   Subject: {email['subject']}")
        print(f"   From: {email.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')}")
        
        confirm = input("\nPress ENTER to continue or CTRL+C to cancel...")
        
        # Step 4: Trigger webhook
        success = trigger_webhook(email["id"], email["subject"])
        
        if success:
            print("\n" + "=" * 60)
            print("✅ SUCCESS - Next Steps:")
            print("=" * 60)
            print("1. Check Railway logs:")
            print("   railway logs --tail 50 | grep 'WEG A\\|WEG B\\|Processing email'")
            print("\n2. Wait 30-60 seconds")
            print("\n3. Check email inbox (mj@cdtechnologies.de) for notification")
            print("\n4. Look for:")
            print("   - ⚠️ WEG A (orange) if contact unknown")
            print("   - ✅ WEG B (green) if contact known")
    
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
