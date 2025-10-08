# 🎯 MASTER PROJECT PROMPT - C&D Technologies Lead Management Ecosystem

## 🌟 **PROJEKT VISION - GESAMTÜBERSICHT**

Du entwickelst ein **intelligentes Lead Management Ecosystem** für C&D Technologies GmbH - ein **Orchestrator-basiertes Microservice System** das ALLE Kundeninteraktions-Kanäle zentral verwaltet, analysiert und automatisiert.

---

## 🏗️ **SYSTEM ARCHITEKTUR**

### **🧠 Zentrale Komponente: ORCHESTRATOR (Railway LangGraph)**
- **URL:** https://my-langgraph-agent-production.up.railway.app
- **Funktion:** Zentrale KI-Intelligenz für ALLE Lead-Quellen
- **Performance:** SQL-Database für schnelle Abfragen, WeClapp CRM für komplexe Daten
- **Aktionen:** Task-Generierung, CRM-Updates, Terminplanung, automatische Antworten

### **📱 Lead-Quellen (Microservices/Apps):**
1. **📧 Email Processing** - Microsoft Graph Integration
2. **📞 SipGate Calls** - Telefon + AI Transcription  
3. **💬 WhatsApp Business** - Nachrichten + Medien
4. **📱 Instagram Direct** - Social Media Anfragen
5. **🌐 Webmail Contact** - Website Formulare
6. **📄 Document Scans** - OCR + AI Analysis
7. **📋 Manual Input** - Mitarbeiter-Eingaben

---

## 🔄 **INTELLIGENT WORKFLOW EXAMPLES**

### **📞 SipGate Call Scenario - Terminfindung:**
```
1. CALL: "Hallo, ich hätte gerne einen Termin für ein Aufmaß"
2. ORCHESTRATOR: 
   - Erkennt: Terminwunsch
   - Prüft: SQL-DB → Kunde bekannt? Letzte Projekte?
   - AI Action: "Gerne! Haben Sie bereits konkrete Zeiträume?"
3. FOLLOW-UP: "Ja, nächste Woche Dienstag oder Mittwoch"
4. ORCHESTRATOR:
   - Prüft: Mitarbeiter-Kalender (API Integration)
   - Verfügbar? → Automatische Terminbestätigung
   - Nicht verfügbar? → Alternative vorschlagen
5. RESULT: CRM Eintrag + Kalender + Bestätigungs-SMS

KI-LOGIK: "Wenn Terminvereinbarung erkannt + Mitarbeiter bestätigt → Verfügbarkeitsprüfung → Eintrag oder Alternativen"
```

### **💬 WhatsApp Mitarbeiter-Support:**
```
1. MESSAGE: "Brauche AB für Projekt Müller, Baujahr 2018"  
2. ORCHESTRATOR:
   - SQL-DB Suche: "Müller" + "2018" + "Projekt"
   - Findet: AB-12345, Projekt: Terrassendach
   - Response: "AB-12345 - Terrassendach Müller, Baujahr 2018"
3. CRM LOG: Anfrage dokumentiert, Wer/Wann/Was
```

### **📄 Scan + Email Workflow:**
```
1. EMAIL: mit PDF-Scan Anhang
2. EMAIL SERVICE → OCR SERVICE: Texterkennung
3. OCR SERVICE → GPT SERVICE: Dokumentklassifikation
4. ORCHESTRATOR: Kontext-Analyse
   - Rechnung? → Buchhaltungs-Workflow
   - Aufmaß? → Projekt-Zuordnung + Task für Kalkulation
   - Garantiefall? → Service-Team + Priorisierung
5. ACTIONS: CRM Update + OneDrive Ablage + Mitarbeiter-Tasks
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

## 🔧 **TECHNISCHE IMPLEMENTATION**

### **Microservice Structure:**
```
📧 Email Service (Apify)     ──┐
📞 SipGate Service (Apify)   ──┤
💬 WhatsApp Service (Apify)  ──┤──► 🧠 ORCHESTRATOR (Railway)
📱 Instagram Service (Apify) ──┤        ↕️
🌐 Webmail Service (Apify)   ──┤    🗄️ SQL-DB (Performance)
📄 OCR Service (Apify)       ──┘        ↕️
                                   🏢 WeClapp CRM (Sync)
```

### **Data Flow:**
1. **Input:** Lead-Quelle → Webhook → Orchestrator
2. **Analysis:** KI-Analyse + SQL-DB Lookup + Kontext-Building  
3. **Decision:** Regelwerk + ML-Models → Action Planning
4. **Execution:** CRM Updates + Task Creation + Responses
5. **Learning:** Feedback Loop → Model Improvement

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

*Entwickelt von C&D Technologies GmbH - Intelligente Digitalisierung für den Mittelstand*