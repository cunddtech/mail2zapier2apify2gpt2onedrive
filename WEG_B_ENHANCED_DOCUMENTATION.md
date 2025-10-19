# 📋 WEG B Enhanced - Bekannte Kontakte Workflow

## 🎯 Überblick

**WEG B** wird aktiviert, wenn ein Kontakt im CRM (WeClapp) gefunden wird. Das System erstellt automatisch:
- ✅ CRM Communication Log Entry
- 🤖 GPT-4 AI-Analyse der Nachricht
- 📋 Automatische Task-Generierung
- 📧 **NEU:** Intelligente Mitarbeiter-Benachrichtigung mit kontextbasierten Aktionsvorschlägen

---

## 🆕 Was ist neu in WEG B Enhanced?

### **1. Kontextbasierte Aktionsvorschläge**

Das System analysiert die AI-Absicht (Intent) und schlägt automatisch passende Aktionen vor:

#### **📅 Terminanfrage erkannt**
```
Intent: appointment_request, appointment, termin, besichtigung, aufmaß
→ Button: "📅 TERMIN VEREINBAREN"
   "Terminvorschläge an Kunde senden und Aufmaß planen"
```

#### **💰 Preisanfrage erkannt**
```
Intent: quote_request, price_inquiry, preisanfrage, angebot
→ Button: "💰 ANGEBOT ERSTELLEN"
   "Angebot in WeClapp erstellen und an Kunden senden"
```

#### **❓ Rückfrage erkannt**
```
Intent: question, clarification, nachfrage, rückfrage
→ Button: "📞 KUNDE ANRUFEN"
   "Rückruf planen um Fragen zu klären"
```

#### **✅ Bestellung erkannt**
```
Intent: order, bestellung, auftrag
→ Button: "✅ AUFTRAG ANLEGEN"
   "Kundenauftrag in WeClapp erstellen"
```

#### **⚡ Hohe Dringlichkeit erkannt**
```
Urgency: high, urgent, hoch
→ Button: "⚡ DRINGEND BEARBEITEN"
   "Hohe Priorität - Sofortige Bearbeitung erforderlich"
```

---

### **2. Dashboard Links Integration**

Wie bei WEG A erhalten Mitarbeiter jetzt auch bei bekannten Kontakten direkten Zugriff auf:

#### **📄 Invoice Database**
```
Wenn Rechnung erkannt:
→ "Rechnung #RE-2024-001 im System anzeigen"
   Link: https://railway.app/api/invoice/RE-2024-001
```

#### **💼 Sales Pipeline**
```
Wenn Verkaufschance erstellt:
→ "Verkaufschance anzeigen: Preisanfrage Projekt XY"
   Link: https://railway.app/api/opportunity/123
```

#### **☁️ OneDrive Dateien**
```
Für jeden Anhang:
→ "Rechnung.pdf in OneDrive öffnen"
   Link: Direkter OneDrive Sharing Link
```

#### **📊 Dashboard Übersicht**
```
→ "Invoice & Payment Dashboard öffnen"
   Link: http://localhost:3000

→ "Sales Pipeline Dashboard öffnen"
   Link: http://localhost:3000/sales-pipeline
```

---

### **3. Automatisch generierte Tasks anzeigen**

Wenn GPT-4 Tasks erstellt hat, werden diese mit Priorität angezeigt:

```
✅ Automatisch erstellte Aufgaben (3):

🔴 Dringende Rückruf bei Kunde vereinbaren
🟡 Angebot für Projekt XY erstellen
🟢 Dokumentation aktualisieren
```

- 🔴 = High Priority
- 🟡 = Medium Priority
- 🟢 = Normal Priority

Die ersten 2 Tasks werden auch als direkte Action-Buttons angezeigt.

---

### **4. CRM Integration**

```
👤 Kontakt erkannt:
   Max Mustermann (Mustermann GmbH)
   Von: max@mustermann.de
   📋 In WeClapp öffnen
```

Direkter Link zum Kontakt in WeClapp für schnellen Zugriff.

---

### **5. AI-Analyse Display**

```
🤖 KI-Analyse:
   Absicht: quote_request (Preisanfrage)
   Dringlichkeit: high (hoch)
   Stimmung: positive (positiv)
   📎 Anhänge: 2 Datei(en) verarbeitet
```

Vollständige Transparenz über die AI-Auswertung.

---

## 📧 Email-Struktur (WEG B Enhanced)

### **Header**
```
✅ Bekannter Kontakt verarbeitet
[Grüner Gradient - 55EFC4 → 00B894]
```

### **Inhalt**
1. **Kontakt-Info Box** (Grün)
   - Name & Firma
   - Email/Telefon
   - WeClapp Link

2. **Nachricht Box** (Grün)
   - Vollständiger Nachrichtentext
   - First 300 chars Preview

3. **KI-Analyse Box** (Grau-Blau)
   - Intent, Urgency, Sentiment
   - Attachment Count

4. **Automatische Tasks Box** (Orange) *[Falls Tasks erstellt]*
   - Liste aller generierten Tasks
   - Mit Prioritäts-Emojis

5. **Dashboard Links Box** (Hellgrün) *[Falls Daten vorhanden]*
   - Invoice API Links
   - Opportunity API Links
   - OneDrive Links
   - Dashboard Links

6. **Empfohlene Aktionen** (Buttons)
   - Kontextbasierte Smart Actions
   - Immer: "📋 IN CRM ÖFFNEN"
   - Optional: Intent-basierte Buttons
   - Immer: Feedback Buttons

### **Footer**
```
🤖 Automatisch generiert vom C&D Lead Management System
Kontakt-ID: {weclapp_contact_id}
```

---

## 🎨 Design-Unterschiede: WEG A vs. WEG B

| Feature | WEG A (Unbekannt) | WEG B (Bekannt) |
|---------|-------------------|-----------------|
| **Header Farbe** | Orange (4ECDC4 → 44A08D) | Grün (55EFC4 → 00B894) |
| **Header Text** | "⚠️ Unbekannter Kontakt" | "✅ Bekannter Kontakt verarbeitet" |
| **Aktionen** | Kontakt Erstellen, Lieferant, Privat, Spam | Intent-basierte Smart Actions |
| **Potential Matches** | Ja (ähnliche Kontakte) | Nein (Kontakt bereits bekannt) |
| **CRM Status** | "Nicht im System" | "In WeClapp gefunden" |
| **Fokus** | Entscheidung: Was tun? | Aktion: Wie weiter? |

---

## 🔧 Technische Implementation

### **Code Location**
- **Notification Data:** `production_langgraph_orchestrator.py` Zeilen 979-1053
- **HTML Generation:** `generate_notification_html()` Zeilen 196-396
- **Smart Actions Logic:** Intent-basierte Button-Generierung Zeilen 985-1027

### **Workflow Path**
```
1. Email/Call empfangen
   ↓
2. CRM Lookup: GEFUNDEN
   ↓
3. Route to WEG B (weg_b_known_contact_node)
   ↓
4. GPT-4 AI Analysis
   ↓
5. Task Generation
   ↓
6. CRM Communication Log
   ↓
7. Invoice/Opportunity Erkennung
   ↓
8. Build notification_data (notification_type: "known_contact_enhanced")
   ↓
9. Generate HTML via generate_notification_html()
   ↓
10. Send via Zapier Webhook
```

### **Intent Detection Trigger**
```python
# Aus AI Analysis:
intent = ai_analysis.get("intent", "")

# Intent Matching (case-insensitive, substring match):
if intent in ["appointment_request", "appointment", "termin", "besichtigung", "aufmaß"]:
    → Schedule Appointment Button

if intent in ["quote_request", "price_inquiry", "preisanfrage", "angebot"]:
    → Create Quote Button

if intent in ["question", "clarification", "nachfrage", "rückfrage"]:
    → Call Customer Button

if intent in ["order", "bestellung", "auftrag"]:
    → Create Order Button
```

### **Urgency Handling**
```python
urgency = ai_analysis.get("urgency", "")

if urgency in ["high", "urgent", "hoch"]:
    → Urgent Response Button (highest priority)
```

---

## 📊 Data Flow

### **Input (processing_result)**
```json
{
  "success": true,
  "workflow_path": "weg_b_known_contact",
  "contact_match": {
    "found": true,
    "contact_id": "12345",
    "contact_name": "Max Mustermann",
    "company": "Mustermann GmbH"
  },
  "ai_analysis": {
    "intent": "quote_request",
    "urgency": "high",
    "sentiment": "positive",
    "suggested_tasks": [...]
  },
  "tasks_generated": [
    {"title": "Angebot erstellen", "priority": "high"},
    {"title": "Termin vereinbaren", "priority": "medium"}
  ],
  "invoice_id": "RE-2024-001",
  "opportunity_id": "123",
  "attachment_results": [
    {
      "filename": "Anfrage.pdf",
      "onedrive_sharing_link": "https://..."
    }
  ]
}
```

### **Output (notification_data)**
```json
{
  "notification_type": "known_contact_enhanced",
  "timestamp": "2025-10-19T14:30:00+02:00",
  "channel": "email",
  "from": "max@mustermann.de",
  "subject": "Re: Preisanfrage",
  "body_preview": "Sehr geehrte Damen und Herren...",
  "contact_match": {...},
  "ai_analysis": {...},
  "tasks_generated": [...],
  "invoice_id": "RE-2024-001",
  "opportunity_id": "123",
  "onedrive_links": [
    {
      "filename": "Anfrage.pdf",
      "sharing_link": "https://..."
    }
  ],
  "action_options": [
    {
      "action": "view_in_crm",
      "label": "📋 IN CRM ÖFFNEN",
      "url": "https://cundd.weclapp.com/webapp/view/party/12345"
    },
    {
      "action": "create_quote",
      "label": "💰 ANGEBOT ERSTELLEN",
      "description": "Angebot in WeClapp erstellen und an Kunden senden",
      "color": "success"
    },
    {
      "action": "urgent_response",
      "label": "⚡ DRINGEND BEARBEITEN",
      "description": "Hohe Priorität - Sofortige Bearbeitung erforderlich",
      "color": "warning"
    },
    ...
  ],
  "html_body": "<html>...</html>"
}
```

---

## 🧪 Testing WEG B Enhanced

### **Test Scenario 1: Preisanfrage von bekanntem Kunden**
```bash
# Email mit Betreff "Preisanfrage für Projekt XY"
# Von: bekannter Kunde (im WeClapp vorhanden)
# Mit Anhang: Zeichnung.pdf

Expected Result:
✅ CRM Log erstellt
✅ Task: "Angebot erstellen" (High Priority)
✅ Opportunity erstellt
✅ Email mit Buttons:
   - 📋 IN CRM ÖFFNEN
   - 💰 ANGEBOT ERSTELLEN
   - 💼 Verkaufschance anzeigen: Preisanfrage Projekt XY
   - ☁️ Zeichnung.pdf in OneDrive öffnen
   - ✅ DATEN OK
```

### **Test Scenario 2: Terminanfrage mit hoher Dringlichkeit**
```bash
# Call von bekanntem Kunden
# Transcript: "Ich brauche dringend einen Termin für ein Aufmaß"

Expected Result:
✅ CRM Log erstellt
✅ Task: "Terminvereinbarung" (High Priority)
✅ Email mit Buttons:
   - 📋 IN CRM ÖFFNEN
   - 📅 TERMIN VEREINBAREN
   - ⚡ DRINGEND BEARBEITEN
   - ✅ DATEN OK
```

### **Test Scenario 3: Rückfrage zu laufendem Projekt**
```bash
# Email: "Wie ist der Status von Projekt ABC?"
# Von: bekannter Kunde

Expected Result:
✅ CRM Log erstellt
✅ Task: "Projektstatus mitteilen" (Normal Priority)
✅ Email mit Buttons:
   - 📋 IN CRM ÖFFNEN
   - 📞 KUNDE ANRUFEN
   - ✅ DATEN OK
```

---

## 📈 Monitoring & Analytics

### **Log Messages**
```
✅ Executing WEG B: Known Contact Workflow
✅ WEG B complete: Generated 2 tasks
✅ Sending enhanced notification for known contact: Max Mustermann
```

### **Metrics to Track**
- WEG B activation rate
- Intent distribution (appointment vs. quote vs. question)
- Urgency distribution (high vs. medium vs. low)
- Task generation rate
- Dashboard link click-through rate
- Action button usage (which buttons are clicked most)

---

## 🔮 Future Enhancements

1. **CRM Status Update Vorschläge**
   - "Kontakt-Status auf 'Hot Lead' ändern?"
   - "Verkaufschance auf 'In Verhandlung' verschieben?"

2. **Automatische Email-Templates**
   - Button: "Angebot-Template senden"
   - Button: "Terminvorschläge senden"
   - Button: "Standard-Antwort senden"

3. **Calendar Integration**
   - Terminvorschläge direkt aus Outlook Calendar
   - "Verfügbare Termine: 20.10. 14:00, 21.10. 10:00"

4. **Price Estimation in WEG B**
   - Wie bei Anrufen: Richtpreis-Anzeige
   - "Geschätzter Auftragswert: 5.000-8.000 €"

5. **Follow-up Automation**
   - Automatische Reminder nach X Tagen
   - "Kunde hat noch nicht geantwortet - Nachfassen?"

---

## ✅ Checklist für Go-Live

- [x] WEG B Enhanced Code implementiert
- [x] Dashboard Links integriert
- [x] Smart Actions Intent-basiert
- [x] Urgency Handling implementiert
- [x] Task Display mit Prioritäten
- [x] HTML Template erstellt
- [x] Git committed und gepusht
- [x] Railway Deployment gestartet
- [ ] Railway Deployment abgeschlossen (⏳ ~2 Minuten)
- [ ] Test Email mit bekanntem Kontakt senden
- [ ] Notification Email prüfen
- [ ] Dashboard Links testen
- [ ] Action Buttons testen
- [ ] End-to-End Test mit echtem Kunden

---

## 📞 Support & Feedback

Bei Fragen oder Problemen:
- **Fehler melden:** Via "⚠️ FEHLER MELDEN" Button in der Email
- **Feedback geben:** Via "✅ DATEN OK" Button
- **Logs prüfen:** `railway logs --tail 100 | grep "WEG B"`

---

**Version:** 1.0.0  
**Letzte Änderung:** 19. Oktober 2025  
**Autor:** GitHub Copilot  
**Status:** 🚀 Deployment läuft
