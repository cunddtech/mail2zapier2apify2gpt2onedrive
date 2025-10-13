# 🎯 MASTER PROJECT PLAN V2 - C&D Technologies Lead Management Ecosystem

**Stand:** 13. Oktober 2025  
**Version:** 2.0 - Orchestrator-Zentric Architecture  
**Status:** ✅ SipGate 70%, ❌ Email Processing 10%, ⚠️ CRM 50%, 🔜 SQL DB Konzept

---

## 📊 ARCHITEKTUR-VISION

### 🎯 **Zentrale Philosophie:**

```
ORCHESTRATOR = INTELLIGENTES HIRN (Entscheidungen, Routing, Koordination)
WORKERS = SPEZIALISIERTE HÄNDE (Processing, Extraction, Storage)
```

**Orchestrator macht:**
- ✅ Relevanzprüfung (Spam? Wichtig? Dringend?)
- ✅ Routing-Entscheidungen (Einfach selbst? Komplex → Worker?)
- ✅ CRM-Kommunikation (Contact Matching, Event Creation)
- ✅ Task-Ableitung (Was muss gemacht werden?)
- ✅ User-Notifications (Buttons für Interaktion)
- ✅ Final Storage (Datenbank-Einträge, Status-Updates)

**Workers machen:**
- 📧 **Email-Worker (Apify):** Volle Mail laden, OCR, OneDrive Upload, Dokumentklassifizierung
- 🖼️ **Scan-Worker (Apify):** Bild-OCR, Handschrift-Erkennung, Projekt-Fotos
- 💰 **Invoice-Worker (Apify):** Rechnungs-Extraktion (Nummer, Betrag, Fälligkeit)
- 🔍 **Deep-Analysis-Worker (Optional):** Komplexe GPT-Analysen, Sentiment-Detection

---

## 🔄 DATENFLUSS-PRINZIP: MINIMAL → MAXIMUM

### **Stufe 1: MINIMAL INPUT (Zapier)**
```
Zapier sendet NUR:
- Source: "email" | "call" | "whatsapp"
- ID: message_id | call_id
- Timestamp: received_at
- Minimal Context: from, to (nur IDs, keine Inhalte)
```

**Warum?**
- ⚡ Schnell (keine großen Payloads)
- 🔒 Sicher (keine Daten in Zapier-Logs)
- 🎯 Flexibel (Orchestrator entscheidet, was er braucht)

---

### **Stufe 2: QUICK CHECK (Orchestrator)**
```python
@app.post("/webhook/ai-email")
async def process_email(request: Request):
    data = await request.json()
    
    # 1. Minimal Info laden
    message_id = data.get("message_id")
    user_email = data.get("user_email", "mj@cdtechnologies.de")
    
    # 2. Graph API: NUR Headers laden (From, Subject)
    token = await get_graph_token_mail()
    headers = await fetch_email_headers_only(user_email, message_id, token)
    
    # 3. GPT Quick-Check
    relevance = await quick_relevance_check(headers)
    # → {relevant: true, category: "invoice", confidence: 0.95}
    
    # 4. Routing-Decision
    if not relevance["relevant"]:
        return {"status": "spam_filtered"}
    
    if relevance["category"] == "simple_inquiry":
        # Einfach → Orchestrator macht alles selbst
        return await handle_simple_email(headers)
    
    if relevance["category"] == "invoice" and relevance.get("has_attachment"):
        # Komplex → Apify Worker aufrufen
        worker_result = await call_apify_email_worker(message_id, user_email, relevance)
        return await finalize_invoice_processing(worker_result)
```

**Vorteile:**
- 🚀 Schnelle Spam-Filterung (ohne volle Mail zu laden)
- 💰 Cost-Optimierung (GPT Quick-Check günstiger als Full-Processing)
- 🎯 Präzises Routing (nur komplexe Cases gehen zu Apify)

---

### **Stufe 3: DETAIL PROCESSING (Apify Worker)**

**Email-Worker Flow:**
```
INPUT vom Orchestrator:
{
    "message_id": "AAMkAGE1...",
    "user_email": "mj@cdtechnologies.de",
    "relevance_info": {
        "category": "invoice",
        "priority": "high",
        "expected_attachments": ["pdf"]
    }
}

WORKER PROCESSING:
1. ✅ Volle Email laden (Graph API)
2. ✅ Anhänge identifizieren (PDF, Images)
3. ✅ PDF Download + OCR (PDF.co Standard + Handwriting)
4. ✅ GPT Dokumentklassifizierung
   → Rechnung? Vertrag? Lieferschein? Angebot?
5. ✅ Daten-Extraktion (je nach Dokumenttyp)
   → Rechnungsnummer, Betrag, Fälligkeit, Lieferant
6. ✅ OneDrive Upload mit Ordnerstruktur
   → /Lieferanten/2025/Rechnung_XYZ.pdf
7. ✅ Return strukturierte Daten

OUTPUT zurück an Orchestrator:
{
    "document_type": "invoice",
    "invoice_data": {
        "number": "2025-1234",
        "amount": 1234.56,
        "due_date": "2025-11-15",
        "vendor": "Lieferant GmbH"
    },
    "files": [{
        "onedrive_path": "/Lieferanten/2025/Rechnung_2025-1234.pdf",
        "public_link": "https://..."
    }],
    "ocr_text": "Vollständiger Text...",
    "confidence": 0.98
}
```

**Basis-Code:** `modules/mail/process_email_workflow.py` (bereits vorhanden!)

---

### **Stufe 4: FINAL ACTIONS (Orchestrator)**

```python
async def finalize_invoice_processing(worker_result):
    """
    Orchestrator macht die finalen Business-Actions
    """
    
    # 1. CRM Update
    vendor_contact = await search_weclapp_contact(worker_result["invoice_data"]["vendor"])
    if vendor_contact:
        # Dokument an Lieferant anhängen
        await attach_document_to_party(
            party_id=vendor_contact["id"],
            file_url=worker_result["files"][0]["public_link"]
        )
    
    # 2. Datenbank-Eintrag
    await db.insert_invoice({
        "number": worker_result["invoice_data"]["number"],
        "amount": worker_result["invoice_data"]["amount"],
        "due_date": worker_result["invoice_data"]["due_date"],
        "vendor_id": vendor_contact["id"],
        "status": "open",
        "onedrive_path": worker_result["files"][0]["onedrive_path"]
    })
    
    # 3. Task erstellen
    task = await create_task({
        "title": f"Rechnung prüfen - {worker_result['invoice_data']['number']}",
        "description": f"Betrag: {worker_result['invoice_data']['amount']}€\nFällig: {worker_result['invoice_data']['due_date']}",
        "assigned_to": "mj@cdtechnologies.de",
        "priority": "high" if worker_result["invoice_data"]["amount"] > 1000 else "medium"
    })
    
    # 4. User-Notification mit Buttons
    await send_notification({
        "type": "invoice_received",
        "data": worker_result["invoice_data"],
        "buttons": [
            {"label": "RECHNUNG PRÜFEN", "action": "open_document", "url": worker_result["files"][0]["public_link"]},
            {"label": "ALS BEZAHLT MARKIEREN", "action": "mark_paid", "invoice_id": worker_result["invoice_data"]["number"]},
            {"label": "MAHNUNG ERSTELLEN", "action": "create_reminder"}
        ]
    })
    
    return {"status": "completed", "task_id": task["id"]}
```

---

## 📧 EMAIL PROCESSING - VOLLSTÄNDIGER WORKFLOW

### **Szenario 1: Rechnung mit PDF**

```
1. ZAPIER TRIGGER
   Gmail: New Email detected
   → POST /webhook/ai-email
   {
       "message_id": "AAMkAGE1M2E3...",
       "user_email": "mj@cdtechnologies.de",
       "timestamp": "2025-10-13T14:30:00Z"
   }

2. ORCHESTRATOR: QUICK CHECK (2s)
   ├─ Graph API: Headers laden
   │  From: "rechnung@lieferant.de"
   │  Subject: "Rechnung 2025-1234"
   │  HasAttachments: true
   │
   ├─ GPT Quick-Check (prompt 200 tokens)
   │  "From: rechnung@lieferant.de, Subject: Rechnung 2025-1234, Attachments: 1 PDF"
   │  → {relevant: true, category: "invoice", confidence: 0.99}
   │
   └─ Decision: KOMPLEXE VERARBEITUNG NÖTIG → Apify Worker

3. APIFY EMAIL WORKER (12s)
   ├─ Volle Email laden (Graph API)
   ├─ PDF Download (500 KB)
   ├─ OCR (PDF.co Standard)
   ├─ GPT Dokumentklassifizierung
   │  → "Rechnung, Lieferant: Elektro GmbH, Betrag: 1.234,56€"
   ├─ Daten-Extraktion
   │  Rechnungsnummer: 2025-1234
   │  Betrag: 1234.56
   │  Fälligkeit: 15.11.2025
   │  Lieferant: Elektro GmbH
   ├─ OneDrive Upload
   │  → /Lieferanten/Elektro_GmbH/2025/Rechnung_2025-1234.pdf
   └─ Return to Orchestrator

4. ORCHESTRATOR: FINAL ACTIONS (3s)
   ├─ CRM Search: "Elektro GmbH"
   │  → Found: Party-ID 5500
   ├─ Dokument an Party anhängen
   ├─ SQL DB: Invoice-Eintrag
   │  INSERT INTO invoices (number, amount, due_date, vendor_id, status)
   ├─ Task erstellen
   │  "Rechnung prüfen - 2025-1234 (1.234,56€)"
   └─ Notification
       "📧 Neue Rechnung von Elektro GmbH"
       [RECHNUNG PRÜFEN] [ALS BEZAHLT MARKIEREN]

GESAMT: 17s (Quick-Check 2s + Worker 12s + Final 3s)
```

**Status:** ⚠️ Teilweise implementiert
- ✅ Graph API Integration (gerade eben)
- ❌ Quick-Check fehlt
- ✅ Apify Worker existiert (process_email_workflow.py)
- ❌ Final Actions unvollständig

---

### **Szenario 2: Einfache Terminanfrage (Bekannter Kunde)**

```
1. ZAPIER TRIGGER
   Gmail: New Email
   {
       "message_id": "AAMkAGE1M2E4...",
       "user_email": "mj@cdtechnologies.de"
   }

2. ORCHESTRATOR: QUICK CHECK (1s)
   ├─ Headers laden
   │  From: "mueller@firma.de"
   │  Subject: "Termin für Aufmaß nächste Woche"
   │
   ├─ GPT Quick-Check
   │  → {relevant: true, category: "appointment_request", confidence: 0.95}
   │
   └─ Decision: EINFACH → Selbst verarbeiten (kein Worker nötig)

3. ORCHESTRATOR: PROCESSING (2s)
   ├─ Volle Email laden (nur Body, kein Anhang)
   ├─ Contact Search
   │  → Found: "Müller GmbH" (Party-ID 4400)
   ├─ GPT Intent-Analyse
   │  "Kunde möchte Termin für Aufmaß, nächste Woche, flexibel"
   │  → Task: "Termin vereinbaren - Aufmaß bei Müller GmbH"
   └─ CRM Event erstellen

4. ORCHESTRATOR: FINAL ACTIONS (1s)
   ├─ Task in DB
   ├─ WeClapp CRM Event
   │  Type: LETTER, Status: DONE
   └─ Notification
       "📧 Terminanfrage von Müller GmbH"
       [TERMIN ANBIETEN] [KALENDER ÖFFNEN]

GESAMT: 4s (kein Worker-Call nötig!)
```

**Status:** ✅ Weitgehend implementiert (WEG_B Flow)

---

## 📞 SIPGATE PROCESSING - FINALISIERUNG

### **Aktueller Stand: 70%**

**✅ Was funktioniert:**
- Call Detection (inbound/outbound)
- Transcription Extraction (Summary field)
- Contact Matching (Phone Number → WeClapp)
- CRM Event Creation (INCOMING_CALL/OUTGOING_CALL)
- Unknown Contact Workflow (WEG_A mit Buttons)

**❌ Was fehlt:**

1. **Task-Ableitung aus Transkript:**
```python
async def analyze_call_content(transcription: str) -> Dict:
    """
    GPT analysiert Gesprächsinhalt und leitet Tasks ab
    """
    prompt = f"""
    Analysiere dieses Telefonat und erstelle konkrete Aufgaben:
    
    Transkript: {transcription}
    
    Identifiziere:
    1. Vereinbarte Termine (Datum/Uhrzeit extrahieren)
    2. Offene Aufgaben (Was muss gemacht werden?)
    3. Follow-Ups (Wann zurückrufen?)
    4. Wichtige Infos (Preise, Anforderungen, Beschwerden)
    """
    
    result = await gpt_call(prompt)
    # → {
    #     "tasks": ["Angebot erstellen - Projekt XY"],
    #     "appointments": ["2025-10-20 14:00 - Aufmaß vor Ort"],
    #     "follow_up": "In 3 Tagen Status erfragen"
    # }
```

2. **Automatische Termin-Erstellung:**
```python
if result.get("appointments"):
    for appointment in result["appointments"]:
        await create_calendar_event({
            "title": f"Termin mit {contact_name}",
            "date": appointment["date"],
            "location": appointment.get("location", "Büro"),
            "participants": [contact_email, "mj@cdtechnologies.de"]
        })
```

3. **Follow-Up-Reminder:**
```python
if result.get("follow_up"):
    await create_reminder({
        "title": f"Follow-Up: {contact_name}",
        "due_date": calculate_due_date(result["follow_up"]),
        "type": "call_back"
    })
```

**Ziel: 100% = Call → CRM Event + Tasks + Termine + Follow-Ups (vollautomatisch)**

---

## 🏢 CRM INTEGRATION - FINALISIERUNG

### **Aktueller Stand: 50%**

**✅ Was funktioniert:**
- Contact Search (Email, Phone, Name)
- Party Creation (PERSON + COMPANY)
- CRM Event Creation (INCOMING_CALL, OUTGOING_CALL, LETTER, GENERAL)
- Multi-Contact Fuzzy Matching (Domain, Phone-Prefix, Name)
- contactId Handling (für PERSON parties)

**❌ Was fehlt:**

1. **Opportunity/Chance Tracking:**
```python
async def create_or_update_opportunity(party_id: int, email_content: str):
    """
    Lead → Angebot → Auftrag Pipeline
    """
    
    # GPT extrahiert Projektdetails
    project_info = await extract_project_info(email_content)
    # → {
    #     "project_name": "Sanierung Bürogebäude",
    #     "estimated_value": 45000,
    #     "probability": "high",
    #     "expected_close_date": "2025-12-31"
    # }
    
    # WeClapp Opportunity erstellen
    opportunity = await weclapp_api.create_opportunity({
        "partyId": party_id,
        "name": project_info["project_name"],
        "estimatedValue": project_info["estimated_value"],
        "probability": map_probability(project_info["probability"]),
        "expectedCloseDate": project_info["expected_close_date"],
        "status": "NEW_LEAD"
    })
    
    return opportunity
```

2. **Task Creation in WeClapp:**
```python
# Aktuell: Tasks nur lokal/in Notifications
# Gewünscht: Tasks auch in WeClApp

async def create_weclapp_task(party_id: int, task_data: Dict):
    """
    Task direkt in WeClapp erstellen
    """
    await weclapp_api.post("/task", {
        "partyId": party_id,
        "title": task_data["title"],
        "description": task_data["description"],
        "dueDate": task_data["due_date"],
        "responsibleUserId": "mj@cdtechnologies.de",
        "priority": task_data["priority"]
    })
```

3. **Document Attachment:**
```python
async def attach_document_to_party(party_id: int, file_url: str):
    """
    Rechnung als PDF an Lieferant anhängen
    """
    await weclapp_api.post(f"/party/{party_id}/document", {
        "name": "Rechnung_2025-1234.pdf",
        "url": file_url,
        "type": "INVOICE"
    })
```

4. **Custom Fields Update:**
```python
async def update_party_metadata(party_id: int, data: Dict):
    """
    Tags, Lead-Score, Last-Contact-Date
    """
    await weclapp_api.patch(f"/party/{party_id}", {
        "tags": data.get("tags", []),
        "customAttributes": {
            "lead_score": data.get("lead_score", 0),
            "last_contact_date": now_berlin().isoformat(),
            "preferred_contact_method": data.get("preferred_contact_method", "email")
        }
    })
```

**Ziel: 100% = Vollständige CRM-Synchronisation (nicht nur Events, sondern Tasks, Opportunities, Documents)**

---

## 🗄️ SQL DATENBANK - PRODUCTION-READY

### **Aktueller Stand: Konzept, kaum genutzt**

**Existierend:** `email_data.db` mit Contact-Cache

**Gewünscht:** Zentrale Datenbank für:

1. **Invoice Tracking:**
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL,
    due_date DATE NOT NULL,
    vendor_id INTEGER,
    vendor_name TEXT,
    status TEXT DEFAULT 'open', -- open, paid, overdue
    received_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    paid_date DATETIME,
    onedrive_path TEXT,
    weclapp_party_id INTEGER,
    notes TEXT
);
```

2. **Task Log:**
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    source TEXT, -- email, call, whatsapp
    source_id TEXT, -- message_id, call_id
    assigned_to TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME,
    completed_at DATETIME,
    status TEXT DEFAULT 'open', -- open, in_progress, completed, cancelled
    priority TEXT DEFAULT 'medium' -- low, medium, high, urgent
);
```

3. **Communication Log:**
```sql
CREATE TABLE communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL, -- email, call, whatsapp
    direction TEXT, -- inbound, outbound
    from_contact TEXT,
    to_contact TEXT,
    subject TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    weclapp_party_id INTEGER,
    weclapp_event_id INTEGER,
    sentiment TEXT, -- positive, neutral, negative
    urgency TEXT -- low, medium, high, urgent
);
```

4. **Analytics:**
```sql
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    dimension TEXT, -- channel, contact, date
    dimension_value TEXT,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Beispiel-Queries:
-- Lead-Sources: SELECT dimension_value, COUNT(*) FROM analytics WHERE metric_name='lead_source' GROUP BY dimension_value;
-- Response-Times: SELECT AVG(metric_value) FROM analytics WHERE metric_name='response_time_seconds';
```

**Orchestrator nutzt DB für:**
- ✅ Duplikat-Prevention (gleiche Rechnung nicht 2x verarbeiten)
- ✅ Status-Queries (ist Rechnung bereits bezahlt?)
- ✅ Reporting (Liquiditäts-Forecast, überfällige Rechnungen)
- ✅ Task-Management (was ist noch offen?)

---

## 💰 RECHNUNGS-WORKFLOW - V2 FEATURES

### **Basis-Workflow (V1):**
✅ Rechnung empfangen → OCR → CRM + OneDrive + DB + Notification

### **Erweiterte Features (V2):**

1. **Umsatz-Abgleich:**
```python
async def reconcile_invoices_with_payments():
    """
    Automatischer Abgleich Rechnung ↔ Zahlung
    """
    
    # 1. Lade offene Rechnungen aus DB
    open_invoices = await db.query(
        "SELECT * FROM invoices WHERE status='open'"
    )
    
    # 2. Lade Umsätze aus Buchhaltungssystem (API/CSV-Import)
    payments = await fetch_bank_transactions()
    
    # 3. Matching-Algorithmus
    for invoice in open_invoices:
        matching_payment = find_matching_payment(invoice, payments)
        
        if matching_payment:
            # Rechnung als bezahlt markieren
            await db.update_invoice(invoice["id"], {
                "status": "paid",
                "paid_date": matching_payment["date"]
            })
            
            # Notification
            await send_notification({
                "type": "invoice_paid",
                "invoice_number": invoice["number"],
                "amount": invoice["amount"]
            })
```

2. **Nicht zuordenbare Umsätze:**
```python
async def report_unmatched_payments():
    """
    Zahlungen ohne Rechnung identifizieren
    """
    
    payments = await fetch_bank_transactions()
    invoices = await db.query("SELECT * FROM invoices")
    
    unmatched = []
    for payment in payments:
        if not has_matching_invoice(payment, invoices):
            unmatched.append(payment)
    
    if unmatched:
        await send_notification({
            "type": "unmatched_payments",
            "count": len(unmatched),
            "total_amount": sum(p["amount"] for p in unmatched),
            "payments": unmatched
        })
```

3. **Fällige Rechnungen / Mahnwesen:**
```python
async def check_overdue_invoices():
    """
    Täglich: Überfällige Rechnungen identifizieren
    """
    
    today = now_berlin().date()
    
    overdue = await db.query(
        "SELECT * FROM invoices WHERE status='open' AND due_date < ?",
        [today]
    )
    
    for invoice in overdue:
        days_overdue = (today - invoice["due_date"]).days
        
        if days_overdue <= 7:
            # Freundliche Erinnerung
            await send_reminder("friendly", invoice)
        elif days_overdue <= 14:
            # 1. Mahnung
            await send_reminder("first_warning", invoice)
        elif days_overdue <= 30:
            # 2. Mahnung
            await send_reminder("second_warning", invoice)
        else:
            # Eskalation
            await escalate_to_legal(invoice)
```

4. **Liquiditäts-Forecast:**
```python
async def generate_liquidity_forecast():
    """
    Dashboard: Zu erwartende Ein-/Ausgänge
    """
    
    # Offene Rechnungen (Eingänge)
    expected_income = await db.query(
        "SELECT SUM(amount) as total FROM invoices WHERE status='open' AND due_date <= ?",
        [now_berlin() + timedelta(days=30)]
    )
    
    # Offene Lieferantenrechnungen (Ausgänge)
    expected_expenses = await db.query(
        "SELECT SUM(amount) as total FROM invoices WHERE status='open' AND vendor_id IS NOT NULL"
    )
    
    return {
        "expected_income_30d": expected_income["total"],
        "expected_expenses_30d": expected_expenses["total"],
        "net_forecast": expected_income["total"] - expected_expenses["total"]
    }
```

---

## 🎯 ORCHESTRATOR ROUTING-LOGIK

### **Entscheidungsbaum für EMAIL:**

```python
async def route_email(message_id: str, user_email: str):
    """
    Intelligentes Email-Routing
    """
    
    # STUFE 1: Headers laden
    headers = await fetch_email_headers(message_id, user_email)
    
    # STUFE 2: Quick-Check
    check = await quick_relevance_check(headers)
    
    if not check["relevant"]:
        return {"status": "spam_filtered"}
    
    # STUFE 3: Routing-Decision
    
    # EINFACH: Keine Anhänge, einfache Anfrage
    if check["category"] == "simple_inquiry" and not headers["hasAttachments"]:
        return await handle_simple_email_in_orchestrator(headers)
    
    # KOMPLEX: Rechnung mit PDF
    if check["category"] == "invoice" and headers["hasAttachments"]:
        worker_result = await call_apify_email_worker(message_id, user_email, check)
        return await finalize_invoice_processing(worker_result)
    
    # KOMPLEX: Vertrag/Scan mit mehreren Anhängen
    if check["category"] in ["contract", "scan"] and headers["attachmentCount"] > 1:
        worker_result = await call_apify_scan_worker(message_id, user_email)
        return await finalize_document_processing(worker_result)
    
    # USER-INTERAKTION: Beschwerde
    if check["category"] == "complaint":
        return await create_urgent_task_with_notification(headers)
    
    # DEFAULT: Standard-Processing
    return await handle_standard_email(headers)
```

### **Entscheidungsbaum für CALL:**

```python
async def route_call(call_data: Dict):
    """
    Intelligentes Call-Routing
    """
    
    # STUFE 1: Contact Matching
    contact = await search_contact_by_phone(call_data["external_number"])
    
    # STUFE 2: Transcription Analysis (wenn vorhanden)
    if call_data.get("transcription"):
        analysis = await analyze_call_content(call_data["transcription"])
        
        # Tasks ableiten
        if analysis.get("tasks"):
            for task in analysis["tasks"]:
                await create_task(task)
        
        # Termine erstellen
        if analysis.get("appointments"):
            for appointment in analysis["appointments"]:
                await create_calendar_event(appointment)
    
    # STUFE 3: CRM Event
    await create_crm_event(contact, call_data, analysis)
    
    # STUFE 4: Routing nach Contact-Status
    
    if not contact:
        # WEG_A: Unbekannter Kontakt
        return await send_weg_a_notification(call_data)
    
    if contact["is_vip"]:
        # VIP-Kunde: Sofort Notification
        return await send_vip_notification(contact, call_data)
    
    # WEG_B: Bekannter Kontakt
    return await send_weg_b_notification(contact, call_data)
```

---

## 📋 IMPLEMENTIERUNGS-ROADMAP

### **Phase 1: EMAIL PROCESSING FINALISIEREN (2-3 Tage)**

**Priorität: HOCH**

1. ✅ Graph API Integration (bereits implementiert)
2. ⏳ Quick-Check Endpoint
   - Minimal Headers laden
   - GPT Relevanz-Prüfung
   - Routing-Decision
3. ⏳ Apify Email Worker Integration
   - Orchestrator → Apify API Call
   - process_email_workflow.py als Worker nutzen
   - Response zurück an Orchestrator
4. ⏳ Final Actions implementieren
   - CRM Update (Document Attachment)
   - DB Insert (Invoice Tracking)
   - User Notification mit Buttons

**Test-Szenario:**
- Email mit PDF-Rechnung an mj@cdtechnologies.de
- Erwartung: Spam-Check → Relevant → Apify Worker → OCR → OneDrive → CRM → DB → Notification

---

### **Phase 2: SIPGATE FINALISIEREN (1-2 Tage)**

**Priorität: MITTEL (bereits 70%)**

1. ✅ Call Detection (done)
2. ✅ Transcription Extraction (done)
3. ✅ Contact Matching (done)
4. ✅ CRM Event (done)
5. ⏳ Task-Ableitung aus Transkript
   - GPT Analyse implementieren
   - Task-Erstellung automatisieren
6. ⏳ Termin-Extraktion
   - "Nächste Woche Montag 14 Uhr" → Calendar Event
7. ⏳ Follow-Up-Reminder
   - "In 3 Tagen zurückrufen" → Reminder

**Test-Szenario:**
- Anruf von bekanntem Kunden mit Transkript "Ich brauche ein Angebot für Sanierung, können wir nächste Woche Montag 10 Uhr telefonieren?"
- Erwartung: CRM Event + Task "Angebot erstellen" + Termin "20.10.2025 10:00 Call"

---

### **Phase 3: CRM INTEGRATION ERWEITERN (2-3 Tage)**

**Priorität: MITTEL**

1. ✅ Contact Search/Create (done)
2. ✅ CRM Event (done)
3. ⏳ Opportunity Tracking
   - Lead → Angebot → Auftrag Pipeline
4. ⏳ Task in WeClapp
   - Nicht nur lokal, auch in CRM
5. ⏳ Document Attachment
   - PDF an Party anhängen
6. ⏳ Custom Fields
   - Tags, Lead-Score, Metadata

---

### **Phase 4: SQL DATENBANK PRODUCTION-READY (3-4 Tage)**

**Priorität: MITTEL-NIEDRIG**

1. ⏳ Schema erweitern
   - Invoices, Tasks, Communications, Analytics
2. ⏳ DB-Helper-Funktionen
   - insert_invoice(), update_task(), etc.
3. ⏳ Orchestrator Integration
   - Alle Actions schreiben in DB
4. ⏳ Duplikat-Prevention
   - "Rechnung bereits verarbeitet?"
5. ⏳ Reporting-Endpoints
   - GET /api/invoices/overdue
   - GET /api/tasks/open

---

### **Phase 5: RECHNUNGS-WORKFLOW V2 (4-5 Tage)**

**Priorität: NIEDRIG (Future)**

1. ⏳ Umsatz-Import
   - Buchhaltungssystem-API oder CSV
2. ⏳ Matching-Algorithmus
   - Rechnung ↔ Zahlung
3. ⏳ Unmatched-Payments-Report
4. ⏳ Mahnwesen
   - Automatische Erinnerungen/Mahnungen
5. ⏳ Liquiditäts-Forecast
   - Dashboard mit 30-Tage-Prognose

---

## 🎯 SUCCESS METRICS

### **Email Processing:**
- ✅ 95%+ Spam-Filterung korrekt
- ✅ <20s Processing-Zeit (mit Apify Worker)
- ✅ 90%+ OCR-Genauigkeit bei Rechnungen
- ✅ 100% Rechnungen in OneDrive UND DB UND CRM

### **SipGate:**
- ✅ 100% Calls erfasst (CRM Event)
- ✅ 80%+ Tasks automatisch abgeleitet
- ✅ 70%+ Termine automatisch erkannt

### **CRM Integration:**
- ✅ 95%+ Contact-Matching korrekt
- ✅ 100% Communications geloggt
- ✅ 80%+ Opportunities automatisch erstellt

### **SQL Datenbank:**
- ✅ Duplikat-Prevention 100%
- ✅ Reporting verfügbar (Dashboards)
- ✅ 90%+ Invoice-Payment-Matching

---

## 🚀 GETTING STARTED

### **Nächster Schritt (JETZT):**

1. **Zapier konfigurieren:**
   - Outlook/Gmail Trigger: Sende nur `message_id` + `user_email`
   - Testen mit einer Test-Email

2. **Orchestrator Quick-Check implementieren:**
   - Endpoint: `/webhook/ai-email` erweitern
   - Headers laden (kein Body)
   - GPT Quick-Relevance-Check
   - Routing-Decision loggen

3. **Erste Test-Email durchlaufen:**
   - Spam → gefiltert
   - Terminanfrage → einfach (Orchestrator)
   - Rechnung → komplex (Apify Worker)

**Dann Schritt für Schritt die Roadmap abarbeiten!**

---

## 📞 KONTAKT & FEEDBACK

**Questions?**
- Was ist unklar?
- Welche Prioritäten anpassen?
- Welche Features fehlen noch?

**Let's build this! 🚀**
