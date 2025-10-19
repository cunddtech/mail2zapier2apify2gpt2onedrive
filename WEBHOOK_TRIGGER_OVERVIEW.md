"""
🎯 RAILWAY WEBHOOK TRIGGER ÜBERSICHT & TEST SUITE
================================================

Production URL: https://my-langgraph-agent-production.up.railway.app

===============================================
📋 ALLE WEBHOOK ENDPOINTS & IHRE QUELLEN
===============================================

1. EMAIL WEBHOOKS (Microsoft Graph API Integration)
   ------------------------------------------------
   
   A) INCOMING EMAILS
      Endpoint: POST /webhook/ai-email
                POST /webhook/ai-email/incoming
      
      Zapier Trigger: "New Email Matching Search" (Gmail/Outlook)
      Filter: Keywords (rechnung, invoice, angebot, offer, etc.)
      
      Payload:
      {
          "message_id": "AAMkAGE1...",           # Graph API Message ID (REQUIRED)
          "user_email": "mj@cdtechnologies.de",  # Mailbox (REQUIRED)
          "from": "sender@example.com",          # Optional
          "subject": "Rechnung RE-12345",        # Optional
          "document_type_hint": "invoice",       # Optional: invoice|offer|order_confirmation|delivery_note
          "priority": "high"                     # Optional: low|medium|high|urgent
      }
      
      Verarbeitung:
      - ⚡ Immediate Response (< 1s)
      - 🔄 Background Processing (OCR → GPT-4 → OneDrive → CRM)
      - 💾 Invoice DB Storage (wenn Rechnung)
      - 📁 Automatische Ordnerstruktur
      
      Test-Strategie: ✅ Bereits empfangene Emails nutzen (test_real_emails.py)
   
   
   B) OUTGOING EMAILS
      Endpoint: POST /webhook/ai-email/outgoing
      
      Zapier Trigger: "New Sent Email" (Gmail/Outlook)
      
      Payload:
      {
          "message_id": "AAMkAGE1...",
          "user_email": "mj@cdtechnologies.de",
          "to": "recipient@example.com",
          "subject": "Angebot AN-2025-123"
      }
      
      Verarbeitung:
      - Gleiche Pipeline wie Incoming
      - Direction: "outgoing" für CRM Logging
      
      Test-Strategie: ✅ Gesendete Emails aus "Gesendet" Ordner


2. CALL WEBHOOKS (Dual-Source Support)
   ------------------------------------
   
   Endpoint: POST /webhook/ai-call
   
   Quellen:
   A) SipGate Assist API (Primär)
   B) FrontDesk Webhook (Alternative)
   
   A) SIPGATE ASSIST PAYLOAD:
   {
       "call": {
           "id": "call-12345",
           "direction": "in",              # "in" oder "out"
           "from": "+4930123456",          # Anrufer (bei incoming)
           "to": "+4930654321",            # Angerufener
           "users": [...],                 # Interne User
           "duration": 180000,             # Millisekunden
           "startTime": "2025-10-19T10:00:00Z",
           "endTime": "2025-10-19T10:03:00Z"
       },
       "assist": {
           "summary": {
               "title": "Preisanfrage Dachausbau",
               "content": "Kunde fragt nach Angebot...",
               "action_items": ["Angebot erstellen"],
               "next_steps": ["Follow-up Call"]
           },
           "transcript": {
               "url": "https://sipgate.io/transcript.txt"
           },
           "recording": {
               "url": "https://sipgate.io/recording.mp3"
           }
       }
   }
   
   B) FRONTDESK PAYLOAD:
   {
       "call_id": "fd-12345",
       "call_direction": "inbound",
       "from_number": "+4930123456",
       "to_number": "+4930654321",
       "duration_seconds": 180,
       "recording_url": "https://frontdesk.io/recording.mp3",
       "transcription_url": "https://frontdesk.io/transcript.txt",
       "transcription_text": "Hallo, ich hätte gerne..."
   }
   
   Verarbeitung:
   - 🔍 Telefonnummer → WeClapp Contact Matching
   - 🎯 WEG A: Unbekannt → Notification Email mit 4 Aktions-Buttons
   - 🎯 WEG B: Bekannt → CRM Log + GPT-4 Analysis + Task Creation
   - 🎤 Whisper Transcription (wenn nur Audio vorhanden)
   - 💼 Opportunity Creation (bei Preisanfragen)
   
   Test-Strategie: ⚠️ LIVE TEST erforderlich (SipGate/FrontDesk)


3. FRONTDESK WEBHOOK (Spezialisiert)
   ----------------------------------
   
   Endpoint: POST /webhook/frontdesk
   
   Zapier Trigger: "New Call Recording" (FrontDesk App)
   
   Payload:
   {
       "recording_url": "https://frontdesk.io/recording.mp3",
       "caller_phone": "+4930123456",
       "duration": 180,
       "timestamp": "2025-10-19T10:00:00Z",
       "call_type": "incoming"
   }
   
   Verarbeitung:
   - Download Audio
   - Whisper Transcription
   - Routing zu /webhook/ai-call Pipeline
   
   Test-Strategie: ⚠️ LIVE TEST erforderlich


4. WHATSAPP WEBHOOK
   -----------------
   
   Endpoint: POST /webhook/ai-whatsapp
   
   Zapier Trigger: "New Message" (WhatsApp Business API)
   
   Payload:
   {
       "from": "+4930123456",
       "message": "Hallo, ich hätte gerne ein Angebot für...",
       "timestamp": "2025-10-19T10:00:00Z",
       "media_url": "https://wa.me/media/image.jpg"  # Optional
   }
   
   Verarbeitung:
   - GPT-4 Analysis
   - Contact Matching
   - Response Generation
   - CRM Logging
   
   Test-Strategie: ⚠️ LIVE TEST oder Mock WhatsApp Messages


5. FEEDBACK WEBHOOK (Mitarbeiter-Aktionen)
   ----------------------------------------
   
   Endpoint: POST /webhook/feedback
   
   Quelle: Email Notification Buttons (WEG A)
   
   Payload:
   {
       "action": "create_contact",        # create_contact|mark_private|mark_spam|request_info
       "contact_email": "unknown@example.com",
       "contact_data": {
           "name": "Max Mustermann",
           "company": "Mustermann GmbH",
           "phone": "+4930123456"
       },
       "email_id": "AAMkAGE1..."
   }
   
   Verarbeitung:
   - WeClapp API Calls (Contact Creation)
   - Database Update
   - Confirmation Email
   
   Test-Strategie: ✅ Simulierbar mit curl/test script


6. CONTACT ACTION WEBHOOK (GET/POST)
   ----------------------------------
   
   Endpoint: GET/POST /webhook/contact-action
   
   Quelle: Email Links + Manual Requests
   
   Query Params (GET):
   ?action=create_contact&sender=unknown@example.com&email_id=12345
   
   JSON Body (POST):
   {
       "action": "create_contact",
       "contact_email": "unknown@example.com",
       "email_id": "12345",
       "contact_data": {...}
   }
   
   Test-Strategie: ✅ Einfach testbar mit curl


===============================================
🧪 TEST SUITE STRUKTUR
===============================================

test_suite/
├── test_email_scenarios.py         # Email Tests (historische Emails)
├── test_call_scenarios_live.py     # Call Tests (Live SipGate/FrontDesk)
├── test_whatsapp_scenarios.py      # WhatsApp Tests
├── test_feedback_scenarios.py      # Feedback Webhook Tests
└── test_integration_full.py        # End-to-End Integration Tests


===============================================
📧 EMAIL TEST SZENARIEN
===============================================

SZENARIO 1: EINGANGSRECHNUNG
----------------------------
Quelle: Bereits empfangene Email aus Zapier Filter
Dokument: PDF Rechnung
Expected:
- ✅ OCR Extraktion
- ✅ GPT-4 Invoice Recognition
- ✅ Invoice DB Entry
- ✅ OneDrive Upload (/Eingang/Rechnungen/2025/10/)
- ✅ WeClapp Contact Match
- ✅ Sharing Link Generation

Test Email IDs (Real):
1. "Fwd: Ihre Rechnung..." - RE-12345
2. "Rechnung 56084007" - Standard Invoice
3. "Invoice INV-2025-001" - English Format


SZENARIO 2: ANGEBOT (PREISANFRAGE)
-----------------------------------
Quelle: Bereits empfangene Email
Dokument: PDF oder nur Email Text
Expected:
- ✅ GPT-4 Opportunity Recognition
- ✅ Sales Pipeline DB Entry (Stage: "lead")
- ✅ OneDrive Upload (/Eingang/Angebote/)
- ⚠️ Kein WeClapp Contact → Notification Email (WEG A)
- ✅ 4 Aktions-Buttons

Test Email:
- "Anfrage Dachausbau" (bereits getestet)


SZENARIO 3: AUFTRAGSBESTÄTIGUNG
-------------------------------
Quelle: Bereits empfangene Email
Dokument: PDF Auftragsbestätigung
Expected:
- ✅ GPT-4 Order Recognition
- ✅ OneDrive Upload (/Eingang/Auftragsbestätigungen/)
- ✅ WeClapp Order Match (wenn vorhanden)

Test Email:
- "Auftragsbestätigung AB-2025-123"


SZENARIO 4: LIEFERSCHEIN
------------------------
Quelle: Bereits empfangene Email
Dokument: PDF Lieferschein
Expected:
- ✅ GPT-4 Delivery Note Recognition
- ✅ OneDrive Upload (/Eingang/Lieferscheine/)
- ✅ Order Match (wenn Auftragsnummer vorhanden)


SZENARIO 5: ALLGEMEINE ANFRAGE
------------------------------
Quelle: Email ohne PDF, nur Text
Expected:
- ✅ GPT-4 Classification
- ✅ Email-to-PDF Conversion
- ✅ OneDrive Upload (/Eingang/Allgemein/)
- ✅ Contact Match oder WEG A


SZENARIO 6: EMAIL MIT MEHREREN ANHÄNGEN
---------------------------------------
Quelle: Email mit 3+ PDFs
Expected:
- ✅ Alle PDFs verarbeiten
- ✅ Intelligente Sortierung
- ✅ Separate OneDrive Uploads


===============================================
📞 CALL TEST SZENARIEN (LIVE)
===============================================

SZENARIO 1: INBOUND CALL - BEKANNTER KONTAKT
--------------------------------------------
Quelle: SipGate Assist Webhook
Caller: +4930123456 (in WeClapp vorhanden)
Expected:
- ✅ Contact Match via phone
- ✅ Whisper Transcription
- ✅ GPT-4 Summary & Action Items
- ✅ WeClapp CRM Log (Event)
- ✅ Task Creation (wenn Action Item)
- ✅ WEG B: Direktes CRM Logging

Test Setup:
1. SipGate Test Account
2. Known Contact in WeClapp
3. Webhook configured


SZENARIO 2: INBOUND CALL - UNBEKANNTER KONTAKT
----------------------------------------------
Quelle: SipGate Assist Webhook
Caller: +491234567890 (nicht in WeClapp)
Expected:
- ⚠️ No Contact Match
- ✅ Whisper Transcription
- ✅ GPT-4 Summary
- ✅ WEG A: Notification Email mit 4 Buttons
- ✅ Mitarbeiter wählt Aktion
- ✅ Contact Creation oder Skip

Test Setup:
1. Unknown Phone Number
2. Webhook to Railway
3. Check Notification Email


SZENARIO 3: OUTBOUND CALL LOGGING
----------------------------------
Quelle: SipGate Assist Webhook
Direction: "out"
Expected:
- ✅ Contact Match
- ✅ CRM Logging (Outbound Call)
- ✅ Summary Storage


SZENARIO 4: FRONTDESK INTEGRATION
----------------------------------
Quelle: FrontDesk Webhook
Expected:
- ✅ Source Detection (FrontDesk)
- ✅ Audio Download
- ✅ Whisper Transcription
- ✅ Same Pipeline as SipGate


===============================================
💬 WHATSAPP TEST SZENARIEN
===============================================

SZENARIO 1: PREISANFRAGE VIA WHATSAPP
--------------------------------------
Message: "Hallo, was kostet ein Dachausbau 50qm?"
Expected:
- ✅ GPT-4 Opportunity Recognition
- ✅ Sales Pipeline Entry
- ✅ Auto-Response
- ✅ CRM Logging


SZENARIO 2: STATUSANFRAGE
--------------------------
Message: "Wie ist der Status meiner Rechnung?"
Expected:
- ✅ Contact Match
- ✅ Invoice Lookup
- ✅ Status Response


===============================================
🔘 FEEDBACK WEBHOOK TESTS
===============================================

TEST 1: CREATE CONTACT
-----------------------
Action: "create_contact"
Expected:
- ✅ WeClapp POST /party
- ✅ Contact ID returned
- ✅ Database Update


TEST 2: MARK PRIVATE
--------------------
Action: "mark_private"
Expected:
- ✅ Custom Attribute Set
- ✅ Future Emails Ignored


TEST 3: MARK SPAM
-----------------
Action: "mark_spam"
Expected:
- ✅ Blacklist Entry
- ✅ No further processing


TEST 4: REQUEST INFO
--------------------
Action: "request_info"
Expected:
- ✅ CRM Event Creation
- ✅ Follow-up Task


===============================================
🎯 ZAPIER FILTER REGELN (bereits implementiert)
===============================================

EMAIL FILTER (test_real_emails.py):
----------------------------------
ZAPIER_FILTERS = {
    "subject_keywords": [
        "rechnung", "invoice", "bill", "facture",
        "angebot", "offer", "quote", "quotation",
        "preis", "anfrage", "inquiry",
        "auftragsbestätigung", "order confirmation",
        "lieferschein", "delivery note"
    ],
    "has_pdf_attachment": True,  # oder False für reine Text-Emails
    "min_attachment_size_kb": 10,
    "days_back": 30,  # Historische Emails
    "max_test_emails": 50
}


===============================================
📊 TEST EXECUTION PLAN
===============================================

PHASE 1: EMAIL TESTS (✅ Lokale Ausführung möglich)
-----------------------------------------------
Script: test_real_emails.py (bereits vorhanden)

1. Eingangsrechnungen (10 Emails)
   python test_real_emails.py --scenario invoice --count 10

2. Angebote/Preisanfragen (5 Emails)
   python test_real_emails.py --scenario offer --count 5

3. Auftragsbestätigungen (3 Emails)
   python test_real_emails.py --scenario order --count 3

4. Allgemeine Anfragen (5 Emails)
   python test_real_emails.py --scenario general --count 5

Expected Success Rate: 95%+


PHASE 2: CALL TESTS (⚠️ Live erforderlich)
------------------------------------------
Setup: SipGate Test Account + Railway Webhook

1. Inbound Call - Bekannt (1 Test)
   - Manuell: Call to SipGate Number
   - Expected: CRM Log in WeClapp

2. Inbound Call - Unbekannt (1 Test)
   - Manuell: Call from Unknown Number
   - Expected: Notification Email

3. FrontDesk Integration (1 Test)
   - FrontDesk → Railway Webhook
   - Expected: Transcription + CRM


PHASE 3: WHATSAPP TESTS (⚠️ Live oder Mock)
-------------------------------------------
Setup: WhatsApp Business API + Zapier

1. Preisanfrage (Mock)
   curl -X POST /webhook/ai-whatsapp ...

2. Statusanfrage (Mock)
   curl -X POST /webhook/ai-whatsapp ...


PHASE 4: FEEDBACK TESTS (✅ Lokal testbar)
-----------------------------------------
Script: test_feedback_webhooks.py

1. Create Contact
2. Mark Private
3. Mark Spam
4. Request Info


PHASE 5: INTEGRATION TESTS (End-to-End)
----------------------------------------
1. Email → Invoice DB → Dashboard → Payment Match
2. Call → CRM Log → Task Creation → Follow-up
3. WhatsApp → Opportunity → Sales Pipeline


===============================================
📝 TEST RESULTS TRACKING
===============================================

Test Results werden gespeichert in:
- test_results/email_tests.json
- test_results/call_tests.json
- test_results/integration_tests.json

Format:
{
    "test_id": "email-invoice-001",
    "timestamp": "2025-10-19T10:00:00Z",
    "scenario": "invoice",
    "status": "success",
    "duration_ms": 1234,
    "assertions": {
        "ocr_success": true,
        "invoice_db_saved": true,
        "onedrive_uploaded": true,
        "sharing_link_generated": true
    },
    "errors": []
}


===============================================
🚀 NÄCHSTE SCHRITTE
===============================================

1. ✅ Email Tests ausführen (test_real_emails.py)
2. ⚠️ SipGate Call Test Setup
3. ⚠️ FrontDesk Integration testen
4. ✅ Feedback Webhook Tests schreiben
5. 📊 Dashboard Validation (alle Daten sichtbar)
6. 🔄 End-to-End Integration Tests


===============================================
📞 LIVE TEST KONTAKTE
===============================================

Für Live Tests benötigt:
- SipGate Test Account Credentials
- FrontDesk API Key
- WhatsApp Business API Token
- Test Phone Numbers (bekannt + unbekannt)
"""
