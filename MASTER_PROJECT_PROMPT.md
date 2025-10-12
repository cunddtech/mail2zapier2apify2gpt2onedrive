# 🎯 MASTER PROJECT PROMPT - C&D Technologies Lead Management Ecosystem

## 🌟 **PROJEKT VISION - GESAMTÜBERSICHT**

Du entwickelst ein **intelligentes Lead Management Ecosystem** für C&D Technologies GmbH - ein **Orchestrator-basiertes Microservice System** das ALLE Kundeninteraktions-Kanäle zentral verwaltet, analysiert und automatisiert.

---

## 🏗️ **SYSTEM ARCHITEKTUR** *(Updated: 12. Okt 2025)*

### **🧠 Zentrale Komponente: RAILWAY ORCHESTRATOR (LangGraph + FastAPI)**
- **URL:** https://my-langgraph-agent-production.up.railway.app
- **Status:** ✅ **LIVE IN PRODUCTION**
- **Funktion:** Zentrale KI-Intelligenz & Entscheidungs-Hub für ALLE Lead-Quellen
- **Performance:** 6.6s avg response, WeClapp Contact Matching (100+ Kontakte)
- **AI-Funktionen:** Intent Recognition, Urgency Detection, Sentiment Analysis, Task Generation
- **Aktionen:** CRM-Updates (WeClapp), Workflow-Routing (WEG A/B), Response Generation

### **🤖 APIFY ACTORS (95 Verfügbar) - Spezialisierte Worker:**
**Railway ruft Apify NUR bei Bedarf auf:**

1. **`mail2zapier2apify2gpt2onedrive`** - **6.432 Runs ✅ PRODUCTION**
   - Attachment Processing (PDF, Images)
   - OCR (PDF.co Handwriting + Standard)
   - Document Classification (GPT-4)
   - OneDrive Upload & Folder Management
   - WeClapp Data Integration

2. **`apify-actor-process-scan-modular`** - **468 Runs**
   - Scan-OCR Processing
   - Image Analysis

3. **`weclapp-sql-sync-production`** - **278 Runs**
   - WeClapp ↔ SQL-DB Synchronization

4. **`sipgate-handler`** - **4 Runs (in Entwicklung)**
   - Call Transcription Processing
   - Sentiment Analysis

### **📱 Lead-Quellen (Zapier Triggers → Railway):**
1. **📧 Email Processing** - Gmail/Outlook → Railway (Apify bei Attachments)
2. **📞 SipGate Calls** - Webhook → Railway (Apify bei komplexen Transkripten)
3. **💬 WhatsApp Business** - Webhook → Railway (Apify bei Medien)
4. **📱 Instagram Direct** - Roadmap Q1 2026
5. **🌐 Webmail Contact** - Roadmap Q1 2026
6. **📄 Document Scans** - Railway + Apify scan-ocr
7. **📋 Manual Input** - Direct Railway API Calls

---

## 🔄 **INTELLIGENT WORKFLOW EXAMPLES** *(Production-Tested)*

### **� EMAIL: Einfache Terminanfrage (Railway Only - 6s)**
```
1. ZAPIER TRIGGER: Gmail - New Email von kunde@firma.de
2. ZAPIER → RAILWAY: POST /webhook/ai-email
   { sender: "kunde@firma.de", subject: "Termin Aufmaß", body: "..." }
3. RAILWAY PROCESSING (6.6s):
   - AI Analysis: Intent = "appointment_request", Urgency = "medium"
   - Contact Search: WeClapp → Found (Frank Zimmer, ID 4400)
   - Workflow Routing: WEG B (Known Contact)
   - Task Generation: "Termin vereinbaren - Aufmaß bei Frank Zimmer"
   - CRM Update: WeClapp Communication Log Entry
4. RAILWAY → ZAPIER: POST notification webhook
5. ZAPIER: Email to mj@ + info@: "Neue Aufgabe: Termin Frank Zimmer"

✅ KEIN APIFY ACTOR AUFGERUFEN (Text-only Email)
```

### **📄 EMAIL: Rechnung mit PDF (Railway + Apify - 20s)**
```
1. ZAPIER TRIGGER: Gmail - New Email mit PDF-Anhang
2. ZAPIER → RAILWAY: POST /webhook/ai-email (Attachments detected)
3. RAILWAY DECISION: Attachment Processing nötig → Apify Actor
4. RAILWAY → APIFY: Trigger mail2zapier2apify2gpt2onedrive
5. APIFY PROCESSING (12s):
   - Download PDF (Microsoft Graph)
   - OCR Extraction (PDF.co)
   - GPT Classification: "Rechnung"
   - OneDrive Upload: /Lieferanten/2025/Rechnung_XYZ.pdf
6. APIFY → RAILWAY: Return { document_type: "invoice", amount: "1.234,56€" }
7. RAILWAY FINAL PROCESSING (8s):
   - Task: "Rechnung prüfen und buchen - 1.234,56€"
   - CRM Update (WeClapp)
8. RAILWAY → ZAPIER: Notification
9. ZAPIER: Email to mj@ + Buchhaltung

✅ APIFY ACTOR AUFGERUFEN (PDF OCR notwendig)
```

### **📞 SipGate Call: Angebot anfordern (Railway Only - 7s)**
```
1. ZAPIER TRIGGER: SipGate Webhook - Call ended
2. ZAPIER → RAILWAY: POST /webhook/ai-call
   { caller: "+4912345", transcript: "Hallo, ich brauche Angebot..." }
3. RAILWAY PROCESSING (7s):
   - Caller Recognition: +4912345 → Frank Zimmer (WeClapp)
   - AI Transcript Analysis: Intent = "quote_request", Sentiment = "positive"
   - Task Creation: "Angebot erstellen - Terrassendach Frank Zimmer"
   - Call Log: WeClapp Communication Entry
4. RAILWAY → ZAPIER: Notification + SMS Response
5. ZAPIER ACTIONS:
   - Email to mj@: "Frank Zimmer anrufen - Angebot"
   - SMS to +4912345: "Danke! Angebot folgt in 24h"

✅ KEIN APIFY ACTOR (Transkript einfach verarbeitbar)
```

### **💬 WhatsApp Mitarbeiter-Support (Railway Only - 5s)**
```
1. ZAPIER TRIGGER: WhatsApp Business - New Message
2. ZAPIER → RAILWAY: POST /webhook/whatsapp
   { sender: "+491234mj", message: "AB für Projekt Müller?" }
3. RAILWAY PROCESSING (5s):
   - Sender Recognition: Mitarbeiter (Martin)
   - SQL-DB Schnellsuche: "Müller" + "Projekt" + "AB"
   - Ergebnis: AB-12345, Projekt: Terrassendach, 2018
   - Response Generation: "AB-12345 - Terrassendach Müller, Baujahr 2018"
4. RAILWAY → ZAPIER: WhatsApp Reply
5. ZAPIER: WhatsApp Message zurück

✅ KEIN APIFY ACTOR (Text-Nachricht, SQL-DB Lookup)
```

---

## 📡 **CHANNEL-SPEZIFISCHE LOGIK**

### **📞 SipGate Integration:**
- **Events:** newCall, answer, hangup, dtmf, hold
- **AI Features:** Echtzeit-Transkription, Gesprächs-Analyse
- **Smart Actions:** 
  - Richtpreisanfrage → Automatische Berechnung + SMS
  - Terminwunsch → Kalender-Integration + Bestätigung
  - Beschwerde → Priorität HOCH + Sofort-Escalation
- **Follow-up:** Post-Call Summary + CRM Documentation

### **💬 WhatsApp Business:**
- **Message Types:** text, image, document, audio, video, location
- **Smart Recognition:**
  - Mitarbeiter-Anfragen → Interne DB-Suche + Schnell-Response
  - Kunden-Anfragen → Lead-Qualifizierung + Weiterleitung
  - Medien-Upload → Automatische Analyse + Projekt-Zuordnung
- **Business Hours:** Automatische Antworten außerhalb Geschäftszeiten

### **📱 Instagram Direct Messages:**
- **Lead Qualification:** Automatische Erkennung von Interessenten
- **Media Analysis:** Bilder von Bauprojekten → AI-Kostenschätzung
- **Response Templates:** Professionelle Antworten mit CRM-Integration

### **🌐 Webmail/Contact Forms:**
- **Form Integration:** Alle Website-Formulare → Orchestrator
- **Lead Scoring:** Automatische Bewertung basierend auf Anfrage-Qualität
- **Instant Response:** Personalisierte Antworten basierend auf Projekt-Art

### **📄 Document Scan Intelligence:**
- **OCR Processing:** PDF.co + Handschrift-Erkennung
- **Document Types:** Rechnungen, Aufmaße, Pläne, Garantiescheine
- **Auto-Filing:** Intelligente OneDrive-Ordnerstrukturen
- **Task Generation:** Automatische Aufgaben basierend auf Dokumenttyp

---

## 🤖 **ERWEITERTE KI-FUNKTIONEN**

### **📅 Intelligente Terminplanung:**
```python
# Beispiel-Logik für Terminfindung
def handle_appointment_request(transcript, caller_info):
    if detect_appointment_intent(transcript):
        available_slots = check_calendar_availability()
        if available_slots:
            preferred_time = extract_time_preference(transcript)
            best_match = find_best_slot(available_slots, preferred_time)
            return create_appointment(best_match, caller_info)
        else:
            alternatives = suggest_alternatives(preferred_time)
            return send_reschedule_options(caller_info, alternatives)
```

### **🎯 Kontext-bewusste Aktionen:**
- **Wiederholkunde:** Referenz auf letzte Projekte, personalisierte Ansprache
- **Neukunde:** Vollständige Qualifizierung, Unternehmenspräsentation
- **Service-Fall:** Priorität basierend auf Projekt-Wert und Dringlichkeit
- **Notfall:** Sofortige Eskalation + SMS an Bereitschaftsdienst

### **📊 Predictive Analytics:**
- **Lead Scoring:** KI-basierte Bewertung der Conversion-Wahrscheinlichkeit
- **Seasonal Patterns:** Automatische Kapazitätsplanung basierend auf Jahreszeit
- **Customer Lifetime Value:** Priorisierung basierend auf Kundenwert

---

## 🔧 **TECHNISCHE IMPLEMENTATION** *(Final Architecture)*

### **System Structure:**
```
� LEAD-QUELLEN (Zapier Triggers)
   ├─ 📧 Gmail/Outlook (New Email)
   ├─ 📞 SipGate (Call Events)
   ├─ 💬 WhatsApp Business (New Message)
   └─ 🌐 Website Forms
            ↓
    ┌───────────────┐
    │ ZAPIER ROUTER │ (Trigger → Webhook)
    └───────────────┘
            ↓
    ┌───────────────────────────────┐
    │  🧠 RAILWAY ORCHESTRATOR       │
    │  (FastAPI + LangGraph + GPT-4) │
    │  ✅ ZENTRALE INTELLIGENZ       │
    └───────────────────────────────┘
            ↓
    Entscheidung: Einfach oder Komplex?
            ↓
    ┌───────┴───────┐
    ↓               ↓
┌─────────┐   ┌──────────────┐
│ EINFACH │   │   KOMPLEX    │
│ (70%)   │   │   (30%)      │
└─────────┘   └──────────────┘
    ↓               ↓
Railway direkt  Railway → Apify Actor
    ↓               ↓
- AI Analysis   mail2zapier... (6.432 Runs)
- Contact       scan-ocr (468 Runs)
  Matching      sipgate-handler (4 Runs)
- Task Gen          ↓
- CRM Update    Attachment Processing
    ↓           OCR + OneDrive
    ↓               ↓
    └───────┬───────┘
            ↓
    ┌───────────────┐
    │ WeClapp CRM   │ (Contact, Tasks, Communication Log)
    │ SQL-DB        │ (Performance Cache)
    │ OneDrive      │ (Document Storage)
    └───────────────┘
            ↓
    ┌───────────────┐
    │ ZAPIER OUTPUT │ (Email Notifications)
    └───────────────┘
            ↓
    📧 mj@ + info@ + Mitarbeiter
```

### **Data Flow (Optimized):**
1. **Input:** Zapier Trigger → Railway Webhook
2. **Decision:** Railway: Einfach (direkt) vs Komplex (Apify)
3. **Processing:** 
   - **70% Einfach:** Railway AI Analysis → CRM (6-8s)
   - **30% Komplex:** Railway → Apify Actor → Railway (15-25s)
4. **Output:** WeClapp Update + Task Assignment
5. **Notification:** Zapier Email an Mitarbeiter

**Kostenoptimierung:** 70% ohne Apify = 70% Kosteneinsparung ✅

---

## 🎯 **BUSINESS RULES & LOGIC**

### **Automatisierungs-Regeln:**
- **Richtpreisanfragen:** Unter 5.000€ → Automatische Berechnung + Versand
- **Terminanfragen:** Verfügbar → Auto-Booking, Nicht verfügbar → Alternativen
- **Service-Anfragen:** Garantie → Kostenlos, Außerhalb → Kostenschätzung
- **Notfälle:** 24/7 → Sofortige Weiterleitung an Bereitschaft

### **Qualifizierungs-Matrix:**
```
A-Lead: Konkrete Projekte >10k€, bekannte Kunden
B-Lead: Interesse vorhanden, Budget unklar  
C-Lead: Allgemeine Anfragen, niedrige Priorität
Hot: Sofortige Bearbeitung erforderlich
```

### **Response-Templates:**
- **Professionell:** Geschäftskunden, größere Projekte
- **Persönlich:** Privatkunden, Bestandskunden
- **Technisch:** Fachspezifische Anfragen
- **Verkäuferisch:** Neue Leads, Upselling-Potenzial

---

## 📱 **ERWEITERUNGS-ROADMAP**

### **Phase 1: Basis-Channels** (Aktuell)
- ✅ Email Processing (Autark)
- 🔄 SipGate Integration
- 🔄 WhatsApp Business

### **Phase 2: Social & Web** (Q1 2026)
- 📱 Instagram Direct Messages
- 🌐 Website Contact Forms
- 📧 Newsletter Management

### **Phase 3: Advanced AI** (Q2 2026)
- 🎥 Video-Call Integration (Teams/Zoom)
- 🗣️ Voice Assistant (Alexa/Google)
- 📊 Predictive Lead Scoring

### **Phase 4: Enterprise** (Q3 2026)
- 🏢 Multi-Tenant Support
- 🌍 Multi-Language Support
- 📈 Advanced Analytics Dashboard

---

## 💡 **WICHTIGE DESIGN-PRINZIPIEN**

1. **SQL-First Performance:** Schnelle Abfragen für Echtzeit-Responses
2. **Microservice Skalierung:** Jeder Channel eigenständig skalierbar
3. **AI-Human Handoff:** Intelligente Eskalation bei komplexen Fällen
4. **Context Awareness:** Jede Interaktion nutzt vollständigen Kunden-Kontext
5. **Ausfallsicherheit:** Fallback-Systeme für kritische Prozesse
6. **Privacy by Design:** DSGVO-konforme Datenverarbeitung
7. **Continuous Learning:** System lernt aus jeder Interaktion

---

## 🎯 **VERWENDUNG DIESES PROMPTS**

**Nutze diesen Master-Prompt wenn:**
- Du dich in technischen Details verlierst
- Die große Vision aus dem Blick gerät  
- Neue Features/Channels geplant werden
- Architektur-Entscheidungen getroffen werden
- Stakeholder-Präsentationen vorbereitet werden

**Denke immer daran:** Es ist ein **intelligentes Ecosystem**, nicht nur einzelne Apps!

---

## 📄 **WICHTIGE DOKUMENTATION**

- **`ARCHITECTURE_DECISION_FINAL.md`** - Detaillierte Architektur-Entscheidung (Zapier → Railway → Apify)
- **`PRODUCTION_DEPLOYMENT_FINAL_REPORT.md`** - Production Status & Test Results
- **`ZAPIER_INTEGRATION_GUIDE.md`** - Zapier Setup Schritt-für-Schritt
- **`RAILWAY_PRODUCTION_TEST_REPORT.md`** - Webhook Tests & Performance
- **`production_langgraph_orchestrator.py`** - Railway Orchestrator Source Code

---

## 🎯 **STATUS QUO (12. Okt 2025)**

### **✅ LIVE IN PRODUCTION:**
- Railway Orchestrator: https://my-langgraph-agent-production.up.railway.app
- WeClapp Contact Matching: 100+ Kontakte
- WEG A (Unknown) + WEG B (Known) Workflows: ✅ Getestet
- Performance: 6.6s avg response
- Security: 95/100 Punkte (Secrets entfernt, generische Errors)

### **⏳ IN KONFIGURATION:**
- Zapier Zaps: Gmail/Outlook → Railway Webhooks
- Email-Benachrichtigungen: mj@, info@

### **🔄 NÄCHSTE INTEGRATION:**
1. **Email (mj@, info@)** - Diese Woche
2. **SipGate (mj, kt, lh)** - Nächste Woche
3. **WhatsApp Business** - Folgende Woche

---

*Entwickelt von C&D Technologies GmbH - Intelligente Digitalisierung für den Mittelstand*  
*Letzte Aktualisierung: 12. Oktober 2025*