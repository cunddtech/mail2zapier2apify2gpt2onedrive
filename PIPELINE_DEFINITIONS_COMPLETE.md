# 📊 PIPELINE-DEFINITIONEN - C&D LEAD MANAGEMENT

**Status:** ✅ Final Definition  
**Datum:** 12. Oktober 2025  
**Kontext:** Vollständige Workflow-Spezifikationen für alle Lead-Kanäle

---

## 📧 **EMAIL-PIPELINES**

### **Pipeline 1: mj@cdtechnologies.de (Geschäftsführer)**

#### **Eingehende Email-Typen:**
- Kundenanfragen (Angebote, Projekte)
- Lieferanten-Rechnungen
- Vertragsdokumente
- Wichtige Korrespondenz

#### **Workflow-Spezifikation:**

```yaml
trigger:
  zapier_app: Gmail
  email_account: mj@cdtechnologies.de
  filter: 
    - Nicht von: noreply@*, notifications@*
    - Nicht Spam/Marketing

action:
  webhook_url: https://my-langgraph-agent-production.up.railway.app/webhook/ai-email
  method: POST
  payload:
    sender: "{{Email Address}}"
    sender_name: "{{From Name}}"
    subject: "{{Subject}}"
    body: "{{Body Plain}}"
    attachments: "{{Attachments}}[]"
    received_at: "{{Received Time}}"
    recipient: "mj@cdtechnologies.de"
    priority: "high"  # Geschäftsführer = hohe Prio

railway_processing:
  ai_analysis:
    - intent_detection: [appointment, quote_request, complaint, invoice, contract, information]
    - urgency_level: [low, medium, high, urgent]
    - sentiment: [positive, neutral, negative]
    - key_topics: extracted automatically
  
  contact_matching:
    - weclapp_search: email + name
    - fallback: apify_dataset_search
  
  workflow_routing:
    - known_contact: WEG_B (personalisierte Antwort)
    - unknown_contact: WEG_A (Lead-Qualifizierung)
  
  attachment_processing:
    if: attachments.length > 0
    then:
      - call_apify_actor: mail2zapier2apify2gpt2onedrive
      - ocr_processing: pdf.co (standard + handwriting)
      - document_classification: [invoice, contract, plan, quote, other]
      - onedrive_upload: /Posteingang/{year}/{sender}/{filename}
  
  task_generation:
    priority_mapping:
      - complaint: "HOCH - Sofortige Bearbeitung"
      - invoice: "MITTEL - Prüfung innerhalb 3 Tagen"
      - quote_request: "HOCH - Angebot binnen 24h"
      - appointment: "MITTEL - Termin koordinieren"
    
    assigned_to:
      - invoice: "Buchhaltung + mj@"
      - quote_request: "mj@"
      - appointment: "mj@ + Außendienst"
      - complaint: "mj@ (CC: Projektleiter)"
  
  crm_update:
    - weclapp_communication_log: true
    - contact_link: true (wenn gefunden)
    - document_attachment: true (wenn OneDrive-Link)

notification:
  zapier_webhook: ZAPIER_NOTIFICATION_WEBHOOK
  email_to: 
    - mj@cdtechnologies.de
    - info@cdtechnologies.de (CC für wichtige Anfragen)
  
  template:
    subject: "🤖 C&D AI: {{channel}} von {{sender_name}} - {{summary}}"
    body: |
      Neue Aufgabe erfordert Ihre Aufmerksamkeit:
      
      Von: {{sender_name}} ({{sender}})
      Betreff: {{subject}}
      Priorität: {{priority}}
      
      AI-Analyse:
      - Intent: {{intent}}
      - Dringlichkeit: {{urgency}}
      - Sentiment: {{sentiment}}
      
      Generierte Aufgabe:
      {{primary_task.title}}
      Zuständig: {{primary_task.assigned_to}}
      Fällig: {{primary_task.due_date}}
      
      WeClApp Link: {{weclapp_link}}
      Dokument: {{onedrive_link}}
```

**Erwartete Performance:**
- **Ohne Attachments:** 6-8s
- **Mit PDF:** 18-22s
- **Mit mehreren PDFs:** 25-35s

---

### **Pipeline 2: info@cdtechnologies.de (Allgemeine Anfragen)**

#### **Eingehende Email-Typen:**
- Neukundenanfragen
- Website-Kontaktformulare
- Marketing-Anfragen
- Support-Tickets

#### **Workflow-Spezifikation:**

```yaml
trigger:
  zapier_app: Gmail
  email_account: info@cdtechnologies.de
  filter:
    - Nicht von: noreply@*
    - Business Hours: 08:00-18:00 (Auto-Reply außerhalb)

action:
  webhook_url: https://my-langgraph-agent-production.up.railway.app/webhook/ai-email
  payload:
    # ... ähnlich mj@
    recipient: "info@cdtechnologies.de"
    priority: "medium"  # Info = Standard-Prio

railway_processing:
  ai_analysis:
    - lead_scoring: [A-Lead >10k€, B-Lead interessiert, C-Lead niedrige Prio]
    - intent_detection: [quote_request, information_request, support, partnership]
  
  contact_matching:
    - weclapp_search: email + company + phone
    - new_lead_detection: true
  
  workflow_routing:
    - existing_customer: WEG_B (Priorität erhöhen)
    - new_lead: WEG_A (Lead-Qualifizierung)
    - support_request: SUPPORT_WORKFLOW
  
  auto_response:
    if: outside_business_hours OR simple_information_request
    then:
      - generate_response: GPT-4 (professionell, freundlich)
      - send_via_zapier: true
      - template: |
          Vielen Dank für Ihre Anfrage!
          
          Wir haben Ihre Nachricht erhalten und werden uns 
          innerhalb von 24 Stunden bei Ihnen melden.
          
          Für dringende Anfragen:
          Tel: +49 (0) 123 456789
          
          Mit freundlichen Grüßen
          Ihr C&D Technologies Team
  
  task_generation:
    priority_mapping:
      - A-Lead: "HOCH - Kontakt binnen 4h"
      - B-Lead: "MITTEL - Kontakt binnen 24h"
      - C-Lead: "NIEDRIG - Kontakt binnen 3 Tagen"
    
    assigned_to:
      - A-Lead: "mj@"
      - B-Lead: "Vertrieb"
      - Support: "Support-Team"

notification:
  conditions:
    - A-Lead: Sofort (Email + optional SMS)
    - B-Lead: Email innerhalb 1h
    - C-Lead: Tägliche Zusammenfassung
```

**Lead-Scoring Kriterien:**
- **A-Lead (>10.000€):**
  - Konkrete Projektbeschreibung
  - Budget genannt oder impliziert hoch
  - Zeitrahmen definiert
  - Firma bekannt/etabliert

- **B-Lead (Interessiert):**
  - Allgemeine Anfrage mit Details
  - Interesse erkennbar
  - Kein konkretes Projekt yet

- **C-Lead (Niedrig):**
  - Sehr allgemeine Anfrage
  - Keine Details
  - Marketing/Newsletter-Anfragen

---

## 📞 **SIPGATE-PIPELINES**

### **Pipeline 3: SipGate User "mj" (Martin, Geschäftsführer)**

#### **Call-Events:**
- `newCall`: Neuer eingehender Anruf
- `answer`: Anruf wurde angenommen
- `hangup`: Anruf beendet
- `dtmf`: Tasteneingaben (optional für IVR)

#### **Workflow-Spezifikation:**

```yaml
trigger:
  zapier_app: Webhooks by Zapier
  webhook_source: SipGate
  filter:
    - event: [newCall, hangup]
    - user: [mj]  # Nur Calls für Martin

action:
  webhook_url: https://my-langgraph-agent-production.up.railway.app/webhook/ai-call
  payload:
    caller_phone: "{{from}}"
    called_phone: "{{to}}"
    call_id: "{{callId}}"
    event: "{{event}}"
    user: "{{user}}"
    direction: "{{direction}}"  # inbound/outbound
    timestamp: "{{timestamp}}"
    duration: "{{duration}}"  # bei hangup
    transcript: "{{transcript}}"  # falls verfügbar

railway_processing:
  caller_recognition:
    - weclapp_search: phone_number
    - matching_logic: 
        - exact_match: +491234567890
        - normalized_match: 01234567890 → +491234567890
        - partial_match: *67890 (last 5 digits)
  
  event_handling:
    newCall:
      - log_call_start: WeClapp
      - prepare_context: Last interactions, projects
    
    hangup:
      - log_call_end: WeClapp (duration)
      - transcript_analysis: if available
      - task_generation: based on AI analysis
  
  ai_analysis:
    if: transcript available
    then:
      - intent_detection: [quote_request, appointment, complaint, information, callback_request]
      - sentiment: [positive, neutral, negative, frustrated]
      - action_items: extracted automatically
      - urgency: [low, medium, high, urgent]
  
  task_generation:
    conditions:
      - callback_request: "Rückruf an {{caller_name}}"
      - quote_request: "Angebot erstellen für {{caller_name}}"
      - appointment: "Termin vereinbaren mit {{caller_name}}"
      - complaint: "URGENT: Beschwerde {{caller_name}} bearbeiten"
    
    assigned_to: "mj@"
    due_date:
      - urgent: "Heute"
      - high: "Morgen"
      - medium: "Diese Woche"
  
  auto_response:
    sms_notification:
      if: callback_request
      then:
        - send_sms: "Vielen Dank für Ihren Anruf! Wir melden uns innerhalb von 4 Stunden zurück."
        - via_zapier: SMS by Zapier or Twilio

notification:
  immediate:
    - Call Log gespeichert in WeClapp
    - Email an mj@: "Anruf von {{caller_name}} - {{duration}}min"
  
  with_tasks:
    - Email mit generierter Aufgabe
    - Priority Flag wenn urgent
```

**Erwartete Performance:**
- **Mit Transkript:** 7-10s
- **Ohne Transkript:** 3-5s (nur Call Log)

---

### **Pipeline 4: SipGate User "kt" (Katrin, Vertrieb)**

```yaml
trigger:
  zapier_app: Webhooks by Zapier
  filter:
    - user: [kt]

# Ähnlich mj@, aber:
task_assignment:
  - default: "kt@cdtechnologies.de"
  - escalation: "mj@" (wenn Anrufer nach GF fragt)

auto_response:
  business_hours_only: true
  after_hours:
    - sms: "Vielen Dank! Wir melden uns am nächsten Werktag."
```

---

### **Pipeline 5: SipGate User "lh" (Lukas, Projektleiter)**

```yaml
trigger:
  filter:
    - user: [lh]

task_assignment:
  - project_related: "lh@cdtechnologies.de"
  - technical_complaint: "lh@ + Technical Team"

call_priority:
  - existing_projects: HIGH
  - warranty_calls: URGENT
```

---

## 💬 **WHATSAPP-PIPELINES**

### **Pipeline 6: WhatsApp Business - Kundenanfragen**

#### **Message-Typen:**
- `text`: Einfache Textnachricht
- `image`: Foto (z.B. von Bauprojekt)
- `document`: PDF, Word, etc.
- `audio`: Sprachnachricht
- `location`: Standort-Sharing

#### **Workflow-Spezifikation:**

```yaml
trigger:
  zapier_app: WhatsApp Business (via Zapier/Make/n8n)
  filter:
    - not_from: broadcast_list
    - message_type: [text, image, document, audio, location]

action:
  webhook_url: https://my-langgraph-agent-production.up.railway.app/webhook/whatsapp
  payload:
    sender_phone: "{{from}}"
    sender_name: "{{profile_name}}"
    message_type: "{{type}}"
    message_content: "{{text}}"  # for text
    media_url: "{{media_url}}"  # for image/document
    location: "{{location}}"  # for location
    timestamp: "{{timestamp}}"

railway_processing:
  sender_recognition:
    - weclapp_search: phone_number
    - context_detection: Mitarbeiter vs Kunde
  
  message_type_routing:
    text:
      - ai_analysis: intent, urgency
      - instant_response: if simple query
      - task_generation: if complex
    
    image:
      - call_apify: apify-actor-process-scan-modular
      - image_ocr: extract text from photo
      - project_detection: "Bauprojekt-Foto?"
      - cost_estimation: AI-based rough estimate
    
    document:
      - call_apify: mail2zapier2apify2gpt2onedrive
      - document_processing: OCR + Classification
      - onedrive_upload: true
    
    audio:
      - call_apify: sipgate-handler (reuse transcription)
      - whisper_transcription: OpenAI Whisper
      - text_analysis: same as text message
    
    location:
      - geocoding: address lookup
      - project_association: "Baustelle an dieser Adresse?"
      - appointment_scheduling: "Aufmaß an diesem Standort?"
  
  context_specific_logic:
    mitarbeiter:
      - quick_db_lookup: SQL-Database
      - response_speed: <5s
      - examples:
          - "AB für Müller?" → "AB-12345 - Terrassendach"
          - "Wann Termin Schmidt?" → "Morgen 14:00 Uhr"
    
    kunde:
      - lead_qualification: standard process
      - response_template: professional, friendly
      - examples:
          - "Wie viel kostet Terrassendach?" → "Gerne! Größe?"
          - "Termin möglich?" → "Ja, wann passt es?"
  
  auto_response:
    enabled: true
    conditions:
      - simple_question: instant_answer
      - complex_query: acknowledgment + task
      - after_hours: "Wir melden uns morgen früh!"
    
    templates:
      acknowledgment: |
        Vielen Dank für Ihre Nachricht! 
        Wir kümmern uns darum und melden uns in Kürze.
      
      instant_answer: |
        {{gpt_generated_response}}
      
      after_hours: |
        Vielen Dank! Wir sind außerhalb der Geschäftszeiten.
        Wir melden uns am nächsten Werktag.

notification:
  conditions:
    - mitarbeiter_query: Keine Email (direkt beantwortet)
    - kunde_lead: Email an mj@ + info@
    - urgent: SMS an zuständigen Mitarbeiter
```

**Spezial-Features:**
- **Mitarbeiter-Schnellsuche:** SQL-DB für sofortige Antworten
- **Kunden-Lead-Qualifizierung:** Standard AI-Workflow
- **Medien-Analyse:** Automatische Projekt-Zuordnung bei Fotos
- **Standort-Sharing:** Auto-Termin-Koordination

---

## 🔄 **CROSS-PIPELINE-LOGIK**

### **Kontakt-Konsolidierung:**
```
Email (mj@) + SipGate Call + WhatsApp Message
    ↓
Alle verknüpft mit gleichem WeClapp Contact (ID 4400)
    ↓
Communication Timeline in WeClapp:
  - 10:00: Email erhalten (Angebot angefordert)
  - 11:30: Call (Nachfrage zum Angebot)
  - 14:00: WhatsApp (Termin vereinbart)
```

### **Task-Priorisierung über Kanäle:**
```
Priority Matrix:
  1. URGENT: Beschwerde (Phone/WhatsApp) > Email
  2. HIGH: A-Lead Email > B-Lead Call
  3. MEDIUM: Standard-Anfragen alle Kanäle
  4. LOW: Marketing, Newsletter, Allgemein
```

### **Duplicate Detection:**
```
Wenn innerhalb 1h:
  - Email + Call vom gleichen Kontakt
  → Merge zu einer Task
  → Update Priority (Call → höher)
```

---

## 📊 **PERFORMANCE-ZIELE PRO PIPELINE**

| Pipeline | Response Time | Apify Usage | Success Rate |
|----------|---------------|-------------|--------------|
| mj@ Email (Text) | < 8s | 0% | 99% |
| mj@ Email (PDF) | < 25s | 100% | 95% |
| info@ Email | < 10s | 30% | 98% |
| SipGate Call | < 5s | 10% | 99% |
| WhatsApp Text | < 6s | 0% | 99% |
| WhatsApp Media | < 20s | 90% | 95% |

---

## 🎯 **TASK-MANAGEMENT-SYSTEM**

### **Task-Speicherung:**
1. **WeClapp CRM:**
   - Primary Task Storage
   - Contact Association
   - Project Linking
   - Status Tracking

2. **SQL-Database:**
   - Performance Cache
   - Quick Lookups
   - Analytics Data

3. **Zapier Notifications:**
   - Email-Benachrichtigungen
   - SMS (urgent)
   - Slack (optional)

### **Task-Dashboard:**

**Option A: WeClapp CRM (empfohlen)**
```
WeClapp → Aufgaben-Modul
  ├─ Meine Aufgaben (pro Mitarbeiter)
  ├─ Team-Übersicht
  ├─ Heute fällig
  ├─ Überfällig
  └─ Abgeschlossen
```

**Option B: Separates Dashboard (future)**
```
Custom Dashboard (React/Vue)
  ├─ Echtzeit-Updates (Websockets)
  ├─ Kanban-Board (To-Do, In Progress, Done)
  ├─ Kalender-Ansicht
  ├─ Analytics & Reporting
  └─ Mobile App
```

### **Mitarbeiter-Views:**

**mj@ (Geschäftsführer):**
- Alle High-Priority Tasks
- A-Leads sofort
- Escalations
- Tages-Übersicht 08:00 Uhr

**kt@ (Vertrieb):**
- B-Leads
- Angebotsanfragen
- Follow-ups
- Kalender-Integration

**lh@ (Projektleiter):**
- Projekt-bezogene Anfragen
- Technische Beschwerden
- Aufmaß-Termine
- Baustellen-Koordination

---

## 📧 **BENACHRICHTIGUNGS-MATRIX**

| Task Priority | Email | SMS | Slack | Time |
|---------------|-------|-----|-------|------|
| URGENT | mj@ + Team | mj@ | #alerts | Sofort |
| HIGH | Zuständiger | - | #tasks | <5 min |
| MEDIUM | Zuständiger | - | - | <1h |
| LOW | Tägliche Zusammenfassung | - | - | 08:00 |

---

**Status:** ✅ Finalisiert  
**Nächste Schritte:** End-to-End Testing pro Pipeline  
**Verantwortlich:** DevOps + AI Team
