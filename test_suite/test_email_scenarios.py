#!/usr/bin/env python3
"""
🧪 EMAIL SCENARIOS TEST SUITE
============================

Testet alle Email-Szenarien mit bereits empfangenen Emails
Nutzt Microsoft Graph API für realistische Tests

SZENARIEN:
1. Eingangsrechnungen (Invoice)
2. Angebote/Preisanfragen (Offer/Quote)
3. Auftragsbestätigungen (Order Confirmation)
4. Lieferscheine (Delivery Note)
5. Allgemeine Anfragen (General Inquiry)
6. Multi-Attachment Emails
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)

# Graph API Configuration
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
USER_EMAIL = "mj@cdtechnologies.de"

# Railway Webhook
RAILWAY_WEBHOOK = "https://my-langgraph-agent-production.up.railway.app/webhook/ai-email"

# Test Configuration per Scenario
SCENARIO_CONFIGS = {
    "invoice": {
        "name": "📄 Eingangsrechnungen",
        "keywords": ["rechnung", "invoice", "bill", "facture"],
        "has_pdf": True,
        "expected_document_type": "invoice",
        "expected_db_save": True,
        "expected_folder": "/Eingang/Rechnungen/",
        "min_test_count": 10
    },
    "offer": {
        "name": "💰 Angebote & Preisanfragen",
        "keywords": ["angebot", "offer", "quote", "preis", "anfrage"],
        "has_pdf": False,  # Can be text only
        "expected_document_type": "offer",
        "expected_opportunity": True,
        "expected_folder": "/Eingang/Angebote/",
        "min_test_count": 5
    },
    "order_confirmation": {
        "name": "✅ Auftragsbestätigungen",
        "keywords": ["auftragsbestätigung", "order confirmation", "bestellung"],
        "has_pdf": True,
        "expected_document_type": "order_confirmation",
        "expected_folder": "/Eingang/Auftragsbestätigungen/",
        "min_test_count": 3
    },
    "delivery_note": {
        "name": "📦 Lieferscheine",
        "keywords": ["lieferschein", "delivery note", "versand"],
        "has_pdf": True,
        "expected_document_type": "delivery_note",
        "expected_folder": "/Eingang/Lieferscheine/",
        "min_test_count": 3
    },
    "general": {
        "name": "📧 Allgemeine Anfragen",
        "keywords": ["anfrage", "inquiry", "frage", "information"],
        "has_pdf": False,
        "expected_document_type": "general",
        "expected_folder": "/Eingang/Allgemein/",
        "min_test_count": 5
    },
    "multi_attachment": {
        "name": "📎 Multi-Attachment Emails",
        "keywords": [],  # Any email with 3+ attachments
        "has_pdf": True,
        "min_attachments": 3,
        "expected_multiple_uploads": True,
        "min_test_count": 2
    }
}


def get_graph_token():
    """Get Microsoft Graph API token for email access"""
    import os
    import requests
    
    tenant_id = os.getenv("GRAPH_TENANT_ID_MAIL")
    client_id = os.getenv("GRAPH_CLIENT_ID_MAIL")
    client_secret = os.getenv("GRAPH_CLIENT_SECRET_MAIL")
    
    if not all([tenant_id, client_id, client_secret]):
        print("❌ Missing Graph API credentials. Set environment variables:")
        print("   GRAPH_TENANT_ID_MAIL, GRAPH_CLIENT_ID_MAIL, GRAPH_CLIENT_SECRET_MAIL")
        return None
    
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Token request failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return None


def fetch_emails_for_scenario(scenario: str, config: Dict, days_back: int = 30) -> List[Dict]:
    """
    Hole Emails für spezifisches Szenario
    
    Args:
        scenario: Szenario Name
        config: Szenario Konfiguration
        days_back: Anzahl Tage zurück
    
    Returns:
        Liste von Email Dicts
    """
    token = get_graph_token()
    
    # Datum Filter
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
    
    # Build filter based on scenario
    if scenario == "multi_attachment":
        filter_str = f"receivedDateTime ge {start_date} and hasAttachments eq true"
    else:
        # Keyword filter
        keyword_filters = " or ".join([f"contains(subject, '{kw}')" for kw in config["keywords"]])
        attachment_filter = " and hasAttachments eq true" if config["has_pdf"] else ""
        filter_str = f"receivedDateTime ge {start_date} and ({keyword_filters}){attachment_filter}"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Fetch emails
    url = f"{GRAPH_API_BASE}/users/{USER_EMAIL}/messages"
    params = {
        "$filter": filter_str,
        "$select": "id,subject,from,receivedDateTime,hasAttachments,importance",
        "$top": 50,
        "$orderby": "receivedDateTime desc"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"❌ Graph API Error: {response.status_code}")
        print(response.text)
        return []
    
    emails = response.json().get("value", [])
    
    # Additional filtering for multi-attachment scenario
    if scenario == "multi_attachment":
        filtered_emails = []
        for email in emails:
            # Get attachment count
            att_url = f"{GRAPH_API_BASE}/users/{USER_EMAIL}/messages/{email['id']}/attachments"
            att_response = requests.get(att_url, headers=headers, params={"$select": "id,name,size"})
            if att_response.status_code == 200:
                attachments = att_response.json().get("value", [])
                if len(attachments) >= config.get("min_attachments", 3):
                    email["attachment_count"] = len(attachments)
                    filtered_emails.append(email)
        return filtered_emails
    
    return emails


def send_email_to_webhook(email_id: str, subject: str, scenario: str, config: Dict) -> Dict[str, Any]:
    """
    Sende Email an Railway Webhook
    
    Args:
        email_id: Graph API Message ID
        subject: Email Subject (für Logging)
        scenario: Szenario Name
        config: Szenario Config
    
    Returns:
        Response Dict mit Status
    """
    payload = {
        "message_id": email_id,
        "user_email": USER_EMAIL,
        "document_type_hint": config.get("expected_document_type"),
        "priority": "medium",
        "test_scenario": scenario
    }
    
    try:
        response = requests.post(
            RAILWAY_WEBHOOK,
            json=payload,
            timeout=5  # Quick timeout for async webhook
        )
        
        result = {
            "status": "success" if response.status_code == 200 else "error",
            "http_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "subject": subject,
            "scenario": scenario
        }
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "subject": subject,
            "scenario": scenario
        }


def run_scenario_tests(scenario: str, max_count: Optional[int] = None, verbose: bool = True):
    """
    Führe Tests für ein Szenario aus
    
    Args:
        scenario: Szenario Name (invoice, offer, etc.)
        max_count: Max Anzahl zu testender Emails (None = alle)
        verbose: Ausführliches Logging
    """
    config = SCENARIO_CONFIGS.get(scenario)
    if not config:
        print(f"❌ Unknown scenario: {scenario}")
        print(f"Available: {list(SCENARIO_CONFIGS.keys())}")
        return
    
    print(f"\n{'='*60}")
    print(f"{config['name']} TEST")
    print(f"{'='*60}\n")
    
    # 1. Fetch Emails
    print(f"1️⃣ Fetching emails for scenario: {scenario}...")
    emails = fetch_emails_for_scenario(scenario, config)
    
    if not emails:
        print(f"⚠️ No emails found for scenario: {scenario}")
        return
    
    print(f"   ✅ Found {len(emails)} emails")
    
    # Limit test count
    test_count = min(len(emails), max_count or config["min_test_count"])
    test_emails = emails[:test_count]
    
    print(f"   🎯 Testing {test_count} emails\n")
    
    # 2. Display Test Emails
    print(f"2️⃣ Test Email Overview:")
    for i, email in enumerate(test_emails, 1):
        sender = email.get("from", {}).get("emailAddress", {}).get("name", "Unknown")
        subject = email.get("subject", "No Subject")
        date = email.get("receivedDateTime", "")[:10]
        
        # Show attachment count for multi-attachment scenario
        att_info = ""
        if scenario == "multi_attachment":
            att_info = f" ({email.get('attachment_count', 0)} attachments)"
        
        print(f"   {i}. {date} | {sender} | {subject[:50]}{att_info}")
    
    print()
    
    # 3. Send to Webhook
    print(f"3️⃣ Sending to Railway Webhook...\n")
    
    results = []
    success_count = 0
    
    for i, email in enumerate(test_emails, 1):
        email_id = email["id"]
        subject = email.get("subject", "No Subject")
        
        print(f"   📤 [{i}/{test_count}] {subject[:60]}...")
        
        result = send_email_to_webhook(email_id, subject, scenario, config)
        results.append(result)
        
        if result["status"] == "success":
            print(f"      ✅ Success")
            success_count += 1
            if verbose and result.get("response"):
                print(f"      📋 Response: {json.dumps(result['response'], indent=10)}")
        else:
            print(f"      ❌ Error: {result.get('error', 'Unknown')}")
        
        print()
    
    # 4. Summary
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY - {config['name']}")
    print(f"{'='*60}")
    print(f"✅ Successful: {success_count}/{test_count}")
    print(f"❌ Failed: {test_count - success_count}/{test_count}")
    print(f"📈 Success Rate: {success_count/test_count*100:.1f}%\n")
    
    # Save results
    save_test_results(scenario, results)
    
    return results


def save_test_results(scenario: str, results: List[Dict]):
    """Speichere Test Results als JSON"""
    os.makedirs("test_results", exist_ok=True)
    
    filename = f"test_results/email_{scenario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "scenario": scenario,
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved: {filename}\n")


def run_all_scenarios(max_per_scenario: int = 5):
    """Führe alle Szenarien aus"""
    print("\n" + "="*60)
    print("🧪 RUNNING ALL EMAIL SCENARIOS")
    print("="*60)
    
    all_results = {}
    
    for scenario in SCENARIO_CONFIGS.keys():
        results = run_scenario_tests(scenario, max_count=max_per_scenario)
        all_results[scenario] = results
        print("\n" + "-"*60 + "\n")
    
    # Overall Summary
    print("\n" + "="*60)
    print("📊 OVERALL TEST SUMMARY")
    print("="*60)
    
    total_tests = 0
    total_success = 0
    
    for scenario, results in all_results.items():
        if results:
            scenario_success = sum(1 for r in results if r["status"] == "success")
            total_tests += len(results)
            total_success += scenario_success
            print(f"{SCENARIO_CONFIGS[scenario]['name']}: {scenario_success}/{len(results)} ✅")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_success}/{total_tests} ({total_success/total_tests*100:.1f}%)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Email Scenarios Test Suite")
    parser.add_argument("--scenario", type=str, help="Specific scenario to test", 
                       choices=list(SCENARIO_CONFIGS.keys()) + ["all"])
    parser.add_argument("--count", type=int, default=5, help="Max emails to test per scenario")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.scenario == "all" or not args.scenario:
        run_all_scenarios(max_per_scenario=args.count)
    else:
        run_scenario_tests(args.scenario, max_count=args.count, verbose=args.verbose)
