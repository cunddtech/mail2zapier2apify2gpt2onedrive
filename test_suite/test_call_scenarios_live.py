#!/usr/bin/env python3
"""
📞 CALL SCENARIOS TEST SUITE (LIVE)
===================================

Testet SipGate & FrontDesk Call Integration
⚠️ Benötigt Live Test Calls oder Mock Webhooks

SZENARIEN:
1. Inbound Call - Bekannter Kontakt (WEG B)
2. Inbound Call - Unbekannter Kontakt (WEG A)
3. Outbound Call Logging
4. FrontDesk Integration
5. Multi-Language Calls (EN/DE)
6. Long Call (>10 min) mit Action Items
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import time

# Railway Webhook
RAILWAY_WEBHOOK = "https://my-langgraph-agent-production.up.railway.app/webhook/ai-call"

# Test Configuration
KNOWN_CONTACT = {
    "phone": "+4930123456",  # Muss in WeClapp existieren
    "name": "Test Contact",
    "expected_match": True
}

UNKNOWN_CONTACT = {
    "phone": "+491234567890",  # Darf NICHT in WeClapp existieren
    "name": "Unknown Caller",
    "expected_match": False
}


def create_sipgate_assist_payload(
    call_direction: str = "in",
    from_number: str = "+4930123456",
    to_number: str = "+4930654321",
    duration_seconds: int = 180,
    transcript_text: str = "Hallo, ich hätte gerne ein Angebot für einen Dachausbau.",
    summary_title: str = "Preisanfrage Dachausbau"
) -> Dict[str, Any]:
    """
    Erstelle SipGate Assist Webhook Payload
    
    Args:
        call_direction: "in" oder "out"
        from_number: Anrufer Nummer
        to_number: Angerufener Nummer
        duration_seconds: Gesprächsdauer
        transcript_text: Transkript Text
        summary_title: GPT-4 Summary Title
    
    Returns:
        SipGate Assist Format Payload
    """
    now = datetime.now()
    call_id = f"test-call-{int(now.timestamp())}"
    
    payload = {
        "call": {
            "id": call_id,
            "direction": call_direction,
            "from": from_number,
            "to": to_number,
            "users": ["user@cdtechnologies.de"],
            "duration": duration_seconds * 1000,  # Milliseconds
            "startTime": now.isoformat(),
            "endTime": (now.replace(second=now.second + duration_seconds)).isoformat()
        },
        "assist": {
            "summary": {
                "title": summary_title,
                "content": transcript_text,
                "action_items": [
                    "Angebot erstellen",
                    "Follow-up Call in 3 Tagen"
                ],
                "next_steps": [
                    "Kalkulation durchführen",
                    "PDF Angebot versenden"
                ]
            },
            "transcript": {
                "text": transcript_text,
                "url": f"https://sipgate.io/transcript/{call_id}.txt"
            },
            "recording": {
                "url": f"https://sipgate.io/recording/{call_id}.mp3"
            }
        }
    }
    
    return payload


def create_frontdesk_payload(
    from_number: str = "+4930123456",
    to_number: str = "+4930654321",
    duration_seconds: int = 180,
    transcription_text: str = "Hallo, ich hätte gerne ein Angebot."
) -> Dict[str, Any]:
    """
    Erstelle FrontDesk Webhook Payload
    
    Returns:
        FrontDesk Format Payload
    """
    call_id = f"fd-{int(datetime.now().timestamp())}"
    
    payload = {
        "call_id": call_id,
        "call_direction": "inbound",
        "from_number": from_number,
        "to_number": to_number,
        "duration_seconds": duration_seconds,
        "recording_url": f"https://frontdesk.io/recording/{call_id}.mp3",
        "transcription_url": f"https://frontdesk.io/transcript/{call_id}.txt",
        "transcription_text": transcription_text,
        "timestamp": datetime.now().isoformat()
    }
    
    return payload


def send_call_to_webhook(payload: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """
    Sende Call Payload an Railway Webhook
    
    Args:
        payload: Call Webhook Payload
        scenario: Szenario Name
    
    Returns:
        Response Dict
    """
    try:
        print(f"   📡 Sending to webhook...")
        response = requests.post(
            RAILWAY_WEBHOOK,
            json=payload,
            timeout=30  # Longer timeout for call processing
        )
        
        result = {
            "status": "success" if response.status_code == 200 else "error",
            "http_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "scenario": scenario,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"   ✅ Webhook response: {response.status_code}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "scenario": scenario
        }


def test_inbound_known_contact():
    """
    SZENARIO 1: Inbound Call - Bekannter Kontakt
    Expected: WEG B - Direktes CRM Logging
    """
    print("\n" + "="*60)
    print("📞 SZENARIO 1: Inbound Call - Bekannter Kontakt (WEG B)")
    print("="*60 + "\n")
    
    print(f"📋 Test Setup:")
    print(f"   Caller: {KNOWN_CONTACT['phone']} ({KNOWN_CONTACT['name']})")
    print(f"   Expected: Contact Match → CRM Log → Task Creation")
    print()
    
    payload = create_sipgate_assist_payload(
        call_direction="in",
        from_number=KNOWN_CONTACT['phone'],
        duration_seconds=180,
        transcript_text="Hallo, ich hätte gerne ein Angebot für einen Dachausbau. Größe ca. 50qm.",
        summary_title="Preisanfrage Dachausbau"
    )
    
    print(f"📤 Sending SipGate Assist payload...")
    result = send_call_to_webhook(payload, "inbound_known")
    
    print(f"\n📊 Test Result:")
    print(f"   Status: {result['status']}")
    print(f"   HTTP Code: {result.get('http_code', 'N/A')}")
    
    if result['status'] == 'success':
        print(f"   ✅ Webhook accepted call")
        print(f"\n   Expected Actions:")
        print(f"   1. ✅ Contact Match (Phone: {KNOWN_CONTACT['phone']})")
        print(f"   2. ✅ Whisper Transcription")
        print(f"   3. ✅ GPT-4 Summary & Action Items")
        print(f"   4. ✅ WeClapp CRM Log (Event)")
        print(f"   5. ✅ Task Creation (Angebot erstellen)")
        print(f"\n   🔍 Verify in WeClapp CRM:")
        print(f"      - Navigate to Contact: {KNOWN_CONTACT['name']}")
        print(f"      - Check 'Aktivitäten' for new Call Event")
        print(f"      - Check 'Aufgaben' for new Task")
    else:
        print(f"   ❌ Test Failed: {result.get('error', 'Unknown error')}")
    
    return result


def test_inbound_unknown_contact():
    """
    SZENARIO 2: Inbound Call - Unbekannter Kontakt
    Expected: WEG A - Notification Email mit 4 Buttons
    """
    print("\n" + "="*60)
    print("⚠️ SZENARIO 2: Inbound Call - Unbekannter Kontakt (WEG A)")
    print("="*60 + "\n")
    
    print(f"📋 Test Setup:")
    print(f"   Caller: {UNKNOWN_CONTACT['phone']} (Unknown)")
    print(f"   Expected: No Match → Notification Email → 4 Action Buttons")
    print()
    
    payload = create_sipgate_assist_payload(
        call_direction="in",
        from_number=UNKNOWN_CONTACT['phone'],
        duration_seconds=120,
        transcript_text="Guten Tag, ich interessiere mich für Ihre Dienstleistungen.",
        summary_title="Anfrage Dienstleistungen"
    )
    
    print(f"📤 Sending SipGate Assist payload...")
    result = send_call_to_webhook(payload, "inbound_unknown")
    
    print(f"\n📊 Test Result:")
    print(f"   Status: {result['status']}")
    print(f"   HTTP Code: {result.get('http_code', 'N/A')}")
    
    if result['status'] == 'success':
        print(f"   ✅ Webhook accepted call")
        print(f"\n   Expected Actions:")
        print(f"   1. ⚠️ No Contact Match (Phone: {UNKNOWN_CONTACT['phone']})")
        print(f"   2. ✅ Whisper Transcription")
        print(f"   3. ✅ GPT-4 Summary")
        print(f"   4. 📧 Notification Email sent")
        print(f"\n   📧 Check Email Inbox:")
        print(f"      Subject: '🔍 Unbekannter Anrufer: {UNKNOWN_CONTACT['phone']}'")
        print(f"      Body: Call Summary + 4 Action Buttons:")
        print(f"         1. ✅ Kontakt erstellen")
        print(f"         2. 👤 Privat markieren")
        print(f"         3. 🚫 Spam markieren")
        print(f"         4. ℹ️ Rückfrage stellen")
    else:
        print(f"   ❌ Test Failed: {result.get('error', 'Unknown error')}")
    
    return result


def test_outbound_call():
    """
    SZENARIO 3: Outbound Call Logging
    Expected: CRM Log mit "Outbound Call"
    """
    print("\n" + "="*60)
    print("📤 SZENARIO 3: Outbound Call Logging")
    print("="*60 + "\n")
    
    print(f"📋 Test Setup:")
    print(f"   Direction: Outbound")
    print(f"   To: {KNOWN_CONTACT['phone']} ({KNOWN_CONTACT['name']})")
    print(f"   Expected: CRM Log as Outbound")
    print()
    
    payload = create_sipgate_assist_payload(
        call_direction="out",
        from_number="+4930654321",  # Our number
        to_number=KNOWN_CONTACT['phone'],
        duration_seconds=240,
        transcript_text="Hallo Herr Mustermann, ich rufe wegen dem Angebot an.",
        summary_title="Follow-up Call - Angebot Dachausbau"
    )
    
    print(f"📤 Sending SipGate Assist payload...")
    result = send_call_to_webhook(payload, "outbound")
    
    print(f"\n📊 Test Result:")
    print(f"   Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"   ✅ Webhook accepted call")
        print(f"\n   Expected Actions:")
        print(f"   1. ✅ Contact Match")
        print(f"   2. ✅ CRM Log as 'Outbound Call'")
        print(f"   3. ✅ Summary Storage")
        print(f"\n   🔍 Verify in WeClapp:")
        print(f"      - Contact: {KNOWN_CONTACT['name']}")
        print(f"      - Event Type: 'Outbound Call'")
    else:
        print(f"   ❌ Test Failed")
    
    return result


def test_frontdesk_integration():
    """
    SZENARIO 4: FrontDesk Integration
    Expected: Source Detection + Same Pipeline
    """
    print("\n" + "="*60)
    print("📱 SZENARIO 4: FrontDesk Integration")
    print("="*60 + "\n")
    
    print(f"📋 Test Setup:")
    print(f"   Source: FrontDesk Webhook")
    print(f"   Caller: {KNOWN_CONTACT['phone']}")
    print(f"   Expected: FrontDesk Detection → Standard Pipeline")
    print()
    
    payload = create_frontdesk_payload(
        from_number=KNOWN_CONTACT['phone'],
        duration_seconds=150,
        transcription_text="Hallo, ich möchte den Status meiner Bestellung wissen."
    )
    
    print(f"📤 Sending FrontDesk payload...")
    result = send_call_to_webhook(payload, "frontdesk")
    
    print(f"\n📊 Test Result:")
    print(f"   Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"   ✅ Webhook accepted call")
        print(f"\n   Expected Actions:")
        print(f"   1. ✅ FrontDesk Source Detection")
        print(f"   2. ✅ Audio Download")
        print(f"   3. ✅ Transcription Processing")
        print(f"   4. ✅ CRM Log")
    else:
        print(f"   ❌ Test Failed")
    
    return result


def test_long_call_with_action_items():
    """
    SZENARIO 5: Long Call (>10 min) mit Action Items
    Expected: Vollständiges Transcript + Multiple Tasks
    """
    print("\n" + "="*60)
    print("⏱️ SZENARIO 5: Long Call mit Multiple Action Items")
    print("="*60 + "\n")
    
    long_transcript = """
    Guten Tag Herr Müller,
    
    ich rufe an wegen des geplanten Dachausbaus. Wir haben folgende Anforderungen:
    
    1. Ausbau von 50qm Dachgeschoss
    2. Installation von 3 Dachfenstern (Velux)
    3. Dämmung nach EnEV Standard
    4. Elektroinstallation (5 Steckdosen, 3 Deckenlampen)
    5. Fußbodenheizung gewünscht
    
    Zeitrahmen: Start in 3 Monaten, Fertigstellung innerhalb 6 Wochen.
    Budget: ca. 80.000 EUR
    
    Bitte erstellen Sie ein detailliertes Angebot mit:
    - Materialkosten
    - Arbeitskosten
    - Zeitplan
    - Zahlungsbedingungen
    
    Kontakt für Rückfragen: 0171-12345678
    Email: kunde@example.com
    """
    
    payload = create_sipgate_assist_payload(
        call_direction="in",
        from_number=KNOWN_CONTACT['phone'],
        duration_seconds=720,  # 12 minutes
        transcript_text=long_transcript,
        summary_title="Detaillierte Anfrage Dachausbau mit Budget"
    )
    
    # Add more action items
    payload["assist"]["summary"]["action_items"] = [
        "Detailliertes Angebot erstellen",
        "Kalkulation durchführen",
        "Velux Fenster Preise einholen",
        "EnEV Dämmung spezifizieren",
        "Elektroinstallation kalkulieren",
        "Fußbodenheizung Optionen prüfen",
        "Zeitplan erstellen",
        "Follow-up Call in 5 Tagen"
    ]
    
    print(f"📤 Sending long call payload...")
    result = send_call_to_webhook(payload, "long_call")
    
    print(f"\n📊 Test Result:")
    print(f"   Status: {result['status']}")
    print(f"   Duration: 12 minutes")
    print(f"   Action Items: 8")
    
    if result['status'] == 'success':
        print(f"\n   ✅ Expected Actions:")
        print(f"   1. ✅ Full Transcript Storage")
        print(f"   2. ✅ 8 Tasks Created in WeClapp")
        print(f"   3. ✅ Opportunity Created (€80,000)")
        print(f"   4. ✅ Sales Pipeline Entry")
    else:
        print(f"   ❌ Test Failed")
    
    return result


def run_all_call_scenarios():
    """Führe alle Call Szenarien aus"""
    print("\n" + "="*60)
    print("📞 RUNNING ALL CALL SCENARIOS")
    print("="*60)
    
    results = {}
    
    # Scenario 1: Known Contact
    results['inbound_known'] = test_inbound_known_contact()
    time.sleep(5)
    
    # Scenario 2: Unknown Contact
    results['inbound_unknown'] = test_inbound_unknown_contact()
    time.sleep(5)
    
    # Scenario 3: Outbound
    results['outbound'] = test_outbound_call()
    time.sleep(5)
    
    # Scenario 4: FrontDesk
    results['frontdesk'] = test_frontdesk_integration()
    time.sleep(5)
    
    # Scenario 5: Long Call
    results['long_call'] = test_long_call_with_action_items()
    
    # Summary
    print("\n" + "="*60)
    print("📊 OVERALL TEST SUMMARY")
    print("="*60 + "\n")
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_count = len(results)
    
    for scenario, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {scenario}: {result['status']}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print(f"{'='*60}\n")
    
    # Save results
    import os
    os.makedirs("test_results", exist_ok=True)
    filename = f"test_results/call_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_count,
            "successful": success_count,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved: {filename}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Call Scenarios Test Suite (Live)")
    parser.add_argument("--scenario", type=str, 
                       choices=["known", "unknown", "outbound", "frontdesk", "long", "all"],
                       help="Specific scenario to test")
    parser.add_argument("--known-phone", type=str, help="Known contact phone (in WeClapp)")
    parser.add_argument("--unknown-phone", type=str, help="Unknown contact phone")
    
    args = parser.parse_args()
    
    # Update contact info if provided
    if args.known_phone:
        KNOWN_CONTACT['phone'] = args.known_phone
    if args.unknown_phone:
        UNKNOWN_CONTACT['phone'] = args.unknown_phone
    
    # Run tests
    if args.scenario == "all" or not args.scenario:
        run_all_call_scenarios()
    elif args.scenario == "known":
        test_inbound_known_contact()
    elif args.scenario == "unknown":
        test_inbound_unknown_contact()
    elif args.scenario == "outbound":
        test_outbound_call()
    elif args.scenario == "frontdesk":
        test_frontdesk_integration()
    elif args.scenario == "long":
        test_long_call_with_action_items()
