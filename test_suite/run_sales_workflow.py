#!/usr/bin/env python3
"""
🎯 SALES WORKFLOW END-TO-END TEST
================================

Vollständiger Sales-Lifecycle von Unbekannt bis Rechnung:
1. Preisanfrage (WEG A - Unbekannter Kontakt)
2. Aufmaß-Termin (WEG B nach Kontakt-Anlegen)
3. Angebot Anfrage (WEG B)
4. Auftragserteilung (WEG B)
5. Montagetermin (WEG B)
6. Rechnung (WEG B mit PDF)
7. After-Sales (WEG B)

Automatisiert alle 7 Emails mit Delays zwischen den Schritten.
"""

import requests
import json
import time
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)

# Configuration
RAILWAY_WEBHOOK = "https://my-langgraph-agent-production.up.railway.app/webhook/ai-email"
TEST_EMAIL = "sales.workflow.test@cdtech-demo.com"  # Must be UNKNOWN in WeClapp!
TEST_NAME = "Max Mustermann"
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
USER_EMAIL = "mj@cdtechnologies.de"

# Delay between emails (seconds)
DELAY_BETWEEN_EMAILS = 45  # Railway needs time to process


def get_graph_token():
    """Get Microsoft Graph API token"""
    tenant_id = os.getenv("GRAPH_TENANT_ID_MAIL")
    client_id = os.getenv("GRAPH_CLIENT_ID_MAIL")
    client_secret = os.getenv("GRAPH_CLIENT_SECRET_MAIL")
    
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"❌ Token request failed: {response.status_code}")
        return None


def send_email_via_graph(subject, body, token):
    """Send email via Microsoft Graph API"""
    url = f"{GRAPH_API_BASE}/users/{USER_EMAIL}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": USER_EMAIL
                    }
                }
            ],
            "from": {
                "emailAddress": {
                    "address": TEST_EMAIL,
                    "name": TEST_NAME
                }
            }
        },
        "saveToSentItems": "false"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code == 202


def check_api_status(endpoint):
    """Check API endpoint for data"""
    url = f"https://my-langgraph-agent-production.up.railway.app/api/{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return None


def print_step(number, title):
    """Print formatted step header"""
    print("\n" + "="*60)
    print(f"📧 STEP {number}: {title}")
    print("="*60)


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  🎯 SALES WORKFLOW END-TO-END TEST                         ║
║                                                             ║
║  Email: sales.workflow.test@cdtech-demo.com                ║
║  Steps: 7 Emails (Preisanfrage → Rechnung)                ║
║  Duration: ~6 minutes (45s delays)                         ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Get Graph API token
    print("🔐 Getting Microsoft Graph API token...")
    token = get_graph_token()
    if not token:
        print("❌ Failed to get Graph token. Exiting.")
        return
    print("✅ Token acquired\n")
    
    # Wait for user confirmation
    input("⚠️  WARNING: This will send 7 real emails!\n   Email must be UNKNOWN in WeClapp.\n   Press ENTER to continue or CTRL+C to cancel...")
    
    # ====================================================================
    # EMAIL 1: Preisanfrage (WEG A - Unbekannter Kontakt)
    # ====================================================================
    print_step(1, "Preisanfrage (WEG A)")
    
    subject_1 = "Anfrage Dachausbau"
    body_1 = """Guten Tag,

ich interessiere mich für einen kompletten Dachausbau für mein Einfamilienhaus in Hamburg.
Das Dach hat eine Fläche von ca. 120 m².

Können Sie mir ein unverbindliches Angebot erstellen?

Mit freundlichen Grüßen
Max Mustermann
"""
    
    print(f"📤 Sending: {subject_1}")
    if send_email_via_graph(subject_1, body_1, token):
        print("✅ Email sent successfully")
        print("⏳ Expected: WEG A notification")
        print("   - Email to employee with 4 buttons")
        print("   - Opportunity created (Lead, 20%)")
    else:
        print("❌ Failed to send email")
        return
    
    print(f"\n⏳ Waiting {DELAY_BETWEEN_EMAILS} seconds for processing...")
    time.sleep(DELAY_BETWEEN_EMAILS)
    
    # ====================================================================
    # MANUAL STEP: User must click "NEUEN KONTAKT ANLEGEN" button
    # ====================================================================
    print("\n" + "⚠️ "*30)
    print("⚠️  MANUAL ACTION REQUIRED!")
    print("⚠️  Check your email inbox for WEG A notification")
    print("⚠️  Click: '✅ NEUEN KONTAKT ANLEGEN' button")
    print("⚠️  Wait for contact to be created in WeClapp")
    print("⚠️ "*30)
    input("\nPress ENTER once contact is created in WeClapp...")
    
    # ====================================================================
    # EMAIL 2: Aufmaß-Termin (WEG B)
    # ====================================================================
    print_step(2, "Aufmaß-Termin Anfrage (WEG B)")
    
    subject_2 = "Re: Anfrage Dachausbau"
    body_2 = """Vielen Dank für Ihre schnelle Rückmeldung!

Wann können Sie für ein Aufmaß vorbeikommen? Ich bin diese Woche täglich ab 16 Uhr verfügbar.

Mit freundlichen Grüßen
Max Mustermann
"""
    
    print(f"📤 Sending: {subject_2}")
    if send_email_via_graph(subject_2, body_2, token):
        print("✅ Email sent successfully")
        print("⏳ Expected: WEG B notification")
        print("   - Smart Action: 📅 TERMIN VEREINBAREN")
        print("   - Opportunity Status → Qualifiziert (40%)")
    else:
        print("❌ Failed to send email")
        return
    
    print(f"\n⏳ Waiting {DELAY_BETWEEN_EMAILS} seconds for processing...")
    time.sleep(DELAY_BETWEEN_EMAILS)
    
    # ====================================================================
    # EMAIL 3: Angebot Anfrage (WEG B)
    # ====================================================================
    print_step(3, "Angebot Anfrage (WEG B)")
    
    subject_3 = "Re: Aufmaß-Termin"
    body_3 = """Vielen Dank für das professionelle Aufmaß heute!

Ich warte gespannt auf Ihr detailliertes Angebot.

Mit freundlichen Grüßen
Max Mustermann
"""
    
    print(f"📤 Sending: {subject_3}")
    if send_email_via_graph(subject_3, body_3, token):
        print("✅ Email sent successfully")
        print("⏳ Expected: WEG B notification")
        print("   - Smart Action: 💰 ANGEBOT ERSTELLEN")
        print("   - Opportunity Status → Proposal (50%)")
    else:
        print("❌ Failed to send email")
        return
    
    print(f"\n⏳ Waiting {DELAY_BETWEEN_EMAILS} seconds for processing...")
    time.sleep(DELAY_BETWEEN_EMAILS)
    
    # ====================================================================
    # EMAIL 4: Auftragserteilung (WEG B)
    # ====================================================================
    print_step(4, "Auftragserteilung (WEG B)")
    
    subject_4 = "Auftragserteilung Dachausbau"
    body_4 = """Guten Tag,

Ihr Angebot passt perfekt! Ich möchte den Auftrag hiermit verbindlich erteilen.

Bitte senden Sie mir die Auftragsbestätigung zu.

Mit freundlichen Grüßen
Max Mustermann
"""
    
    print(f"📤 Sending: {subject_4}")
    if send_email_via_graph(subject_4, body_4, token):
        print("✅ Email sent successfully")
        print("⏳ Expected: WEG B notification")
        print("   - Smart Action: ✅ AUFTRAG ANLEGEN")
        print("   - Smart Action: ⚡ DRINGEND BEARBEITEN")
        print("   - Opportunity Status → Won (100%)")
    else:
        print("❌ Failed to send email")
        return
    
    print(f"\n⏳ Waiting {DELAY_BETWEEN_EMAILS} seconds for processing...")
    time.sleep(DELAY_BETWEEN_EMAILS)
    
    # ====================================================================
    # EMAIL 5: Montagetermin (WEG B)
    # ====================================================================
    print_step(5, "Montagetermin Anfrage (WEG B)")
    
    subject_5 = "Montagetermin"
    body_5 = """Guten Tag,

wann kann die Montage voraussichtlich stattfinden?

Ich bin in 2 Wochen verfügbar.

Mit freundlichen Grüßen
Max Mustermann
"""
    
    print(f"📤 Sending: {subject_5}")
    if send_email_via_graph(subject_5, body_5, token):
        print("✅ Email sent successfully")
        print("⏳ Expected: WEG B notification")
        print("   - Smart Action: 📅 TERMIN VEREINBAREN")
    else:
        print("❌ Failed to send email")
        return
    
    print(f"\n⏳ Waiting {DELAY_BETWEEN_EMAILS} seconds for processing...")
    time.sleep(DELAY_BETWEEN_EMAILS)
    
    # ====================================================================
    # EMAIL 6: Rechnung (WEG B) - NOTE: No PDF in this automated test
    # ====================================================================
    print_step(6, "Rechnung Hinweis (WEG B)")
    
    subject_6 = "Rechnung Dachausbau"
    body_6 = """Anbei finden Sie die Rechnung für den abgeschlossenen Dachausbau.

(PDF-Anhang müsste manuell hinzugefügt werden für vollständigen Test)

Vielen Dank für die hervorragende Arbeit!

Mit freundlichen Grüßen
Max Mustermann
"""
    
    print(f"📤 Sending: {subject_6}")
    if send_email_via_graph(subject_6, body_6, token):
        print("✅ Email sent successfully")
        print("⏳ Expected: WEG B notification")
        print("   - NOTE: No PDF, so no Invoice DB entry")
        print("   - Positive sentiment detected")
    else:
        print("❌ Failed to send email")
        return
    
    print(f"\n⏳ Waiting {DELAY_BETWEEN_EMAILS} seconds for processing...")
    time.sleep(DELAY_BETWEEN_EMAILS)
    
    # ====================================================================
    # EMAIL 7: After-Sales (WEG B)
    # ====================================================================
    print_step(7, "After-Sales Feedback (WEG B)")
    
    subject_7 = "Feedback Dachausbau"
    body_7 = """Guten Tag,

ich möchte mich nochmal für die exzellente Arbeit bedanken!
Das Dach sieht fantastisch aus und alles wurde super sauber hinterlassen.

Ich werde Sie gerne weiterempfehlen.

Mit freundlichen Grüßen
Max Mustermann
"""
    
    print(f"📤 Sending: {subject_7}")
    if send_email_via_graph(subject_7, body_7, token):
        print("✅ Email sent successfully")
        print("⏳ Expected: WEG B notification")
        print("   - Sentiment: very positive")
        print("   - Task: Follow-up in 3 Monaten")
    else:
        print("❌ Failed to send email")
        return
    
    # ====================================================================
    # VALIDATION
    # ====================================================================
    print("\n" + "="*60)
    print("🎯 WORKFLOW COMPLETE - Validation Phase")
    print("="*60)
    
    print("\n⏳ Waiting 60 seconds for final processing...")
    time.sleep(60)
    
    print("\n📊 Checking API Endpoints...")
    
    # Check Opportunity API
    opp_stats = check_api_status("opportunity/statistics")
    if opp_stats and opp_stats.get("status") == "success":
        stats = opp_stats.get("statistics", {})
        print("\n💼 Sales Pipeline:")
        print(f"   Stages: {stats.get('stages', {})}")
        print(f"   Won/Lost: {stats.get('won_lost', {})}")
        print(f"   Pipeline Value: {stats.get('weighted_pipeline_value', 0)} €")
    else:
        print("\n⚠️  Sales Pipeline: No data yet (async processing)")
    
    # Check Invoice API
    inv_stats = check_api_status("invoice/statistics")
    if inv_stats and inv_stats.get("status") == "success":
        stats = inv_stats.get("statistics", {})
        print("\n📄 Invoice Database:")
        print(f"   Open Incoming: {stats.get('total_open_incoming', 0)} €")
        print(f"   Count Open: {stats.get('count_open', 0)}")
    else:
        print("\n⚠️  Invoice DB: No data (expected - no PDF sent)")
    
    print("\n" + "="*60)
    print("✅ SALES WORKFLOW TEST COMPLETED")
    print("="*60)
    print("""
Next Steps:
1. Check email inbox for all 7 notifications
2. Open Dashboard: http://localhost:3000/sales-pipeline
3. Verify Opportunity in Sales Pipeline
4. Check Railway logs: railway logs --tail 100 | grep "WEG"

Expected Results:
- 1x WEG A email (Step 1)
- 6x WEG B emails (Steps 2-7)
- 1 Opportunity: "Anfrage Dachausbau" (Won, 100%)
- Multiple Tasks created
- Dashboard links in all emails
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test abgebrochen!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
