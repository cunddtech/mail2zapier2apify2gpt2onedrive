# 🎯 Kompletter Sales Workflow Test
## End-to-End Scenario: Von Unbekannt bis Rechnung

### **📋 Workflow-Schritte:**

1. **Unbekannter Kontakt** (WEG A)
   - Email von neuer Adresse (z.B. `max.test@example.com`)
   - Preisanfrage: "Guten Tag, ich interessiere mich für einen Dachausbau. Können Sie mir ein Angebot erstellen?"

2. **Kontakt Anlegen** (WEG A Aktion)
   - Mitarbeiter erhält Email mit 4 Buttons
   - Klick auf "✅ NEUEN KONTAKT ANLEGEN"
   - Kontakt wird in WeClapp erstellt

3. **Richtpreis Ermittlung**
   - GPT-4 analysiert Anfrage
   - Opportunity wird erstellt (Sales Pipeline)
   - Status: "Lead" (20% Wahrscheinlichkeit)
   - Geschätzter Wert: z.B. 15.000 €

4. **Aufmaß-Termin Vereinbarung**
   - Email: "Wann können Sie für ein Aufmaß vorbeikommen?"
   - WEG B wird aktiviert (Kontakt jetzt bekannt)
   - Smart Action: "📅 TERMIN VEREINBAREN"
   - Opportunity Status → "Qualifiziert" (40%)

5. **Angebot Erstellen**
   - Email: "Vielen Dank für das Aufmaß. Ich warte auf Ihr Angebot."
   - WEG B: Smart Action "💰 ANGEBOT ERSTELLEN"
   - Opportunity Status → "Proposal" (50%)
   - Task: "Angebot erstellen" (High Priority)

6. **Auftrag Bestätigung**
   - Email: "Das Angebot passt. Ich möchte den Auftrag erteilen."
   - WEG B: Smart Action "✅ AUFTRAG ANLEGEN"
   - Opportunity Status → "Won" (100%)
   - Invoice erstellt mit Status "Offen"

7. **Montage-Terminierung**
   - Email: "Wann kann die Montage stattfinden?"
   - WEG B: Smart Action "📅 TERMIN VEREINBAREN"
   - Task: "Montagetermin vereinbaren"

8. **Rechnung Versenden**
   - Email mit PDF-Anhang: "Rechnung_2024_001.pdf"
   - Invoice DB: Rechnung erfasst
   - Dashboard: Invoice sichtbar
   - OneDrive: PDF hochgeladen

9. **After-Sales**
   - Email: "Vielen Dank für die tolle Arbeit!"
   - WEG B: Positive Sentiment erkannt
   - Task: "Follow-up in 3 Monaten"

---

## 🧪 Test-Durchführung

### **Email-Adresse für Test:**
`sales.workflow.test@cdtech-demo.com` (Unbekannt, nicht in WeClapp)

### **Email-Sequenz:**

#### **Email 1: Preisanfrage (WEG A)**
```
Von: sales.workflow.test@cdtech-demo.com
Betreff: Anfrage Dachausbau
Body:
Guten Tag,

ich interessiere mich für einen kompletten Dachausbau für mein Einfamilienhaus in Hamburg.
Das Dach hat eine Fläche von ca. 120 m².

Können Sie mir ein unverbindliches Angebot erstellen?

Mit freundlichen Grüßen
Max Mustermann
```

**Expected Result:**
- ⚠️ WEG A aktiviert (Unbekannter Kontakt)
- Email an Mitarbeiter mit 4 Buttons:
  - ✅ NEUEN KONTAKT ANLEGEN
  - 📦 ALS LIEFERANT ANLEGEN
  - 👤 PRIVATE NACHRICHT
  - 🗑️ SPAM/IRRELEVANT
- Opportunity erstellt: "Anfrage Dachausbau" (Lead, 20%)

---

#### **Email 2: Aufmaß-Termin Anfrage (WEG B)**
```
Von: sales.workflow.test@cdtech-demo.com (NACH Kontakt-Anlegen!)
Betreff: Re: Anfrage Dachausbau
Body:
Vielen Dank für Ihre schnelle Rückmeldung!

Wann können Sie für ein Aufmaß vorbeikommen? Ich bin diese Woche täglich ab 16 Uhr verfügbar.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected Result:**
- ✅ WEG B aktiviert (Kontakt erkannt)
- Email an Mitarbeiter mit Smart Actions:
  - 📋 IN CRM ÖFFNEN
  - 📅 TERMIN VEREINBAREN ← Intent: appointment_request
  - ✅ DATEN OK
- Opportunity Status → "Qualifiziert" (40%)
- Task: "Aufmaß-Termin vereinbaren" (High Priority)

---

#### **Email 3: Angebot Anfrage (WEG B)**
```
Von: sales.workflow.test@cdtech-demo.com
Betreff: Re: Aufmaß-Termin
Body:
Vielen Dank für das professionelle Aufmaß heute!

Ich warte gespannt auf Ihr detailliertes Angebot.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected Result:**
- ✅ WEG B aktiviert
- Smart Actions:
  - 📋 IN CRM ÖFFNEN
  - 💰 ANGEBOT ERSTELLEN ← Intent: quote_request
  - ✅ DATEN OK
- Opportunity Status → "Proposal" (50%)
- Task: "Angebot erstellen" (High Priority)

---

#### **Email 4: Auftragserteilung (WEG B)**
```
Von: sales.workflow.test@cdtech-demo.com
Betreff: Auftragserteilung Dachausbau
Body:
Guten Tag,

Ihr Angebot passt perfekt! Ich möchte den Auftrag hiermit verbindlich erteilen.

Bitte senden Sie mir die Auftragsbestätigung zu.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected Result:**
- ✅ WEG B aktiviert
- Smart Actions:
  - 📋 IN CRM ÖFFNEN
  - ✅ AUFTRAG ANLEGEN ← Intent: order/bestellung
  - ⚡ DRINGEND BEARBEITEN ← Urgency: high
  - ✅ DATEN OK
- Opportunity Status → "Won" (100%)
- Invoice erstellt (Status: Offen, ~15.000 €)
- Task: "Auftrag in WeClapp anlegen" (High Priority)

---

#### **Email 5: Montagetermin (WEG B)**
```
Von: sales.workflow.test@cdtech-demo.com
Betreff: Montagetermin
Body:
Guten Tag,

wann kann die Montage voraussichtlich stattfinden?

Ich bin in 2 Wochen verfügbar.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected Result:**
- ✅ WEG B aktiviert
- Smart Actions:
  - 📋 IN CRM ÖFFNEN
  - 📅 TERMIN VEREINBAREN ← Intent: appointment_request
  - ✅ DATEN OK
- Task: "Montagetermin vereinbaren" (High Priority)

---

#### **Email 6: Rechnung (WEG B mit PDF)**
```
Von: sales.workflow.test@cdtech-demo.com
Betreff: Rechnung Dachausbau
Anhang: Rechnung_Dachausbau_2024.pdf
Body:
Anbei die Rechnung für den abgeschlossenen Dachausbau.

Vielen Dank für die hervorragende Arbeit!

Mit freundlichen Grüßen
Max Mustermann
```

**Expected Result:**
- ✅ WEG B aktiviert
- PDF-Verarbeitung:
  - OCR & GPT-4 Analyse
  - Invoice DB: Rechnung erfasst (RE-2024-XXX)
  - OneDrive: PDF hochgeladen
- Smart Actions:
  - 📋 IN CRM ÖFFNEN
  - 📄 Rechnung #RE-2024-XXX anzeigen ← Dashboard Link
  - ☁️ Rechnung_Dachausbau_2024.pdf in OneDrive ← OneDrive Link
  - 📊 Invoice Dashboard öffnen
  - ✅ DATEN OK
- Sentiment: positive
- Dashboard zeigt Rechnung

---

#### **Email 7: After-Sales (WEG B)**
```
Von: sales.workflow.test@cdtech-demo.com
Betreff: Feedback Dachausbau
Body:
Guten Tag,

ich möchte mich nochmal für die exzellente Arbeit bedanken!
Das Dach sieht fantastisch aus und alles wurde super sauber hinterlassen.

Ich werde Sie gerne weiterempfehlen.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected Result:**
- ✅ WEG B aktiviert
- AI Analysis:
  - Intent: feedback
  - Sentiment: very positive
  - Urgency: low
- Task: "Follow-up in 3 Monaten" (Low Priority)
- Opportunity: Status bleibt "Won"
- CRM Log: Positive Feedback erfasst

---

## 📊 Dashboard Validierung

Nach dem kompletten Workflow sollte das Dashboard zeigen:

### **Sales Pipeline Dashboard** (`localhost:3000/sales-pipeline`)
```
✅ 1 Won Opportunity
   Titel: Anfrage Dachausbau
   Wert: ~15.000 €
   Wahrscheinlichkeit: 100%
   Kontakt: Max Mustermann
   Status: Gewonnen
   
📊 Pipeline Statistics:
   Total Won: 1
   Total Value: 15.000 €
   Average Deal Size: 15.000 €
```

### **Invoice Dashboard** (`localhost:3000`)
```
📄 1 Open Invoice
   Nummer: RE-2024-XXX
   Kunde: Max Mustermann
   Betrag: ~15.000 €
   Status: Offen
   
📊 Invoice Statistics:
   Total Open Incoming: 15.000 €
   Count Open: 1
```

---

## 🔍 Validierungs-Checkliste

### **WEG A (Email 1):**
- [ ] Unbekannter Kontakt erkannt
- [ ] Mitarbeiter-Email mit 4 Buttons erhalten
- [ ] Potential Matches angezeigt (falls ähnliche Kontakte)
- [ ] Opportunity erstellt (Lead, 20%)

### **Kontakt Anlegen:**
- [ ] Button "NEUEN KONTAKT ANLEGEN" geklickt
- [ ] WeClapp: Kontakt erstellt
- [ ] Email-Bestätigung erhalten

### **WEG B (Email 2-7):**
- [ ] Alle Emails erkannt als bekannter Kontakt
- [ ] Smart Actions korrekt (Intent-basiert)
- [ ] Dashboard Links in allen Emails
- [ ] Tasks automatisch erstellt

### **Opportunity Tracking:**
- [ ] Status-Änderungen: Lead → Qualifiziert → Proposal → Won
- [ ] Wahrscheinlichkeit: 20% → 40% → 50% → 100%
- [ ] Activities geloggt

### **Invoice Processing:**
- [ ] PDF verarbeitet
- [ ] Invoice DB: Rechnung erfasst
- [ ] OneDrive: PDF hochgeladen
- [ ] Dashboard: Rechnung sichtbar

### **Dashboard:**
- [ ] Sales Pipeline: 1 Won Opportunity sichtbar
- [ ] Invoice Dashboard: 1 offene Rechnung sichtbar
- [ ] Links funktionieren
- [ ] Daten korrekt

---

## 🚀 Ausführung

```bash
# 1. Email Test-Suite läuft bereits (30 Emails)
# Warten bis complete...

# 2. Dashboard prüfen (sollte leer sein vor Workflow)
open http://localhost:3000
open http://localhost:3000/sales-pipeline

# 3. Sales Workflow durchspielen:
# Email 1-7 manuell senden oder über Test-Script

# 4. Nach jeder Email: Logs prüfen
railway logs --tail 20 | grep -E "WEG A|WEG B|Opportunity|Invoice"

# 5. Dashboard aktualisieren und validieren
open http://localhost:3000/sales-pipeline

# 6. API Endpoints prüfen
curl https://my-langgraph-agent-production.up.railway.app/api/opportunity/statistics
curl https://my-langgraph-agent-production.up.railway.app/api/invoice/statistics
```

---

## 📝 Notizen

- Email-Adresse muss WIRKLICH unbekannt sein (nicht in WeClapp)
- Zwischen Emails 30-60 Sekunden warten (async Processing)
- Dashboard Live-Refresh alle 5 Sekunden
- Railway Logs in Echtzeit beobachten
- Button-Klicks öffnen WeClapp/Dashboard

---

**Status:** 🚀 Bereit für Durchführung  
**Geschätzte Dauer:** 15-20 Minuten  
**Voraussetzung:** Email Test-Suite abgeschlossen
