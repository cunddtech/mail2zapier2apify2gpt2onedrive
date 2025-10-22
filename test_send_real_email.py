#!/usr/bin/env python3
"""
Send a real test email via Microsoft Graph API to test WeClapp Opportunity Status integration
"""

import requests
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.auth.get_graph_token_mail import get_graph_token_mail_sync

def send_test_email():
    """Send test email via Microsoft Graph API"""
    
    print("🔐 Getting Graph API token...")
    access_token = get_graph_token_mail_sync()
    
    if not access_token:
        print("❌ Failed to get access token")
        return False
    
    print("✅ Token obtained")
    
    # Email content
    email_data = {
        "message": {
            "subject": "TEST: Auftragserteilung - Dachausbau Hamburg",
            "body": {
                "contentType": "Text",
                "content": """Guten Tag,

hiermit erteile ich Ihnen den Auftrag für den Dachausbau wie besprochen.

Bitte bestellen Sie das Material beim Lieferanten und schicken Sie mir die Auftragsbestätigung.

Wann können wir die Montage terminieren?

Mit freundlichen Grüßen
Max Mustermann
max.mustermann.test2025@gmail.com

---
TEST EMAIL für WeClapp Opportunity Status Integration
Deployment 18 - Loop Prevention Active"""
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "info@cdtechnologies.de"
                    }
                }
            ]
        },
        "saveToSentItems": True
    }
    
    print("📧 Sending email to info@cdtechnologies.de...")
    print(f"   From: mj@cdtechnologies.de (on behalf of Max Mustermann)")
    print(f"   Subject: TEST: Auftragserteilung - Dachausbau Hamburg")
    
    # Send email from mj@cdtechnologies.de mailbox
    url = "https://graph.microsoft.com/v1.0/users/mj@cdtechnologies.de/sendMail"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=email_data, headers=headers)
    
    if response.status_code == 202:
        print("✅ Email sent successfully!")
        print("\n⏳ Wait 30-60 seconds, then check:")
        print("   1. Railway logs: railway logs --tail 100")
        print("   2. Email inbox: mj@cdtechnologies.de")
        print("\n🔍 Look for:")
        print("   - INTENT OVERRIDE (keyword: auftrag)")
        print("   - Opportunity Status query")
        print("   - Stage-based smart actions")
        return True
    else:
        print(f"❌ Failed to send email: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    send_test_email()
