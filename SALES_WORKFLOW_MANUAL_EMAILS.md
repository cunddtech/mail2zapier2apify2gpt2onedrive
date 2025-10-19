# 📧 Sales Workflow - Manuelle Email-Vorlagen

## ⚠️ WICHTIG: Email-Adresse muss UNBEKANNT sein!

Verwende eine Email-Adresse, die **NICHT in WeClapp existiert**, z.B.:
- `max.mustermann.test@gmail.com`
- `sales.demo.2025@outlook.com`
- Oder eine andere unbekannte Adresse

---

## 📧 EMAIL 1: Preisanfrage (WEG A - Unbekannter Kontakt)

**An:** info@cdtechnologies.de  
**Von:** [DEINE UNBEKANNTE EMAIL]  
**Betreff:** Anfrage Dachausbau

**Text:**
```
Guten Tag,

ich interessiere mich für einen kompletten Dachausbau für mein Einfamilienhaus in Hamburg.
Das Dach hat eine Fläche von ca. 120 m².

Können Sie mir ein unverbindliches Angebot erstellen?

Mit freundlichen Grüßen
Max Mustermann
```

**⏳ NACH DEM SENDEN:**
1. Warte 30-60 Sekunden
2. Prüfe Email-Posteingang (mj@cdtechnologies.de)
3. Suche nach "⚠️ Unbekannter Kontakt" Email
4. **WICHTIG:** Klicke auf Button "✅ NEUEN KONTAKT ANLEGEN"
5. Warte bis Kontakt in WeClapp angelegt ist
6. **Erst dann** weiter mit Email 2!

**Expected:**
- ⚠️ WEG A Notification (Orange Header)
- 4 Action Buttons
- Opportunity erstellt: "Anfrage Dachausbau" (Lead, 20%)
- Potential Matches angezeigt (falls ähnliche Kontakte)

---

## 📧 EMAIL 2: Aufmaß-Termin Anfrage (WEG B)

**⚠️ ERST SENDEN NACHDEM KONTAKT ANGELEGT IST!**

**An:** info@cdtechnologies.de  
**Von:** [GLEICHE EMAIL WIE OBEN]  
**Betreff:** Re: Anfrage Dachausbau

**Text:**
```
Vielen Dank für Ihre schnelle Rückmeldung!

Wann können Sie für ein Aufmaß vorbeikommen? Ich bin diese Woche täglich ab 16 Uhr verfügbar.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected:**
- ✅ WEG B Notification (Grüner Header)
- Smart Action: 📅 TERMIN VEREINBAREN
- Opportunity Status → "Qualifiziert" (40%)
- Task: "Aufmaß-Termin vereinbaren"
- Dashboard Links sichtbar

---

## 📧 EMAIL 3: Angebot Anfrage (WEG B)

**An:** info@cdtechnologies.de  
**Von:** [GLEICHE EMAIL]  
**Betreff:** Re: Aufmaß-Termin

**Text:**
```
Vielen Dank für das professionelle Aufmaß heute!

Ich warte gespannt auf Ihr detailliertes Angebot.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected:**
- ✅ WEG B Notification
- Smart Action: 💰 ANGEBOT ERSTELLEN
- Opportunity Status → "Proposal" (50%)
- Task: "Angebot erstellen" (High Priority)

---

## 📧 EMAIL 4: Auftragserteilung (WEG B)

**An:** info@cdtechnologies.de  
**Von:** [GLEICHE EMAIL]  
**Betreff:** Auftragserteilung Dachausbau

**Text:**
```
Guten Tag,

Ihr Angebot passt perfekt! Ich möchte den Auftrag hiermit verbindlich erteilen.

Bitte senden Sie mir die Auftragsbestätigung zu.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected:**
- ✅ WEG B Notification
- Smart Action: ✅ AUFTRAG ANLEGEN
- Smart Action: ⚡ DRINGEND BEARBEITEN (wegen Urgency: high)
- Opportunity Status → "Won" (100%)
- Invoice erstellt (falls Betrag erkannt)

---

## 📧 EMAIL 5: Montagetermin (WEG B)

**An:** info@cdtechnologies.de  
**Von:** [GLEICHE EMAIL]  
**Betreff:** Montagetermin

**Text:**
```
Guten Tag,

wann kann die Montage voraussichtlich stattfinden?

Ich bin in 2 Wochen verfügbar.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected:**
- ✅ WEG B Notification
- Smart Action: 📅 TERMIN VEREINBAREN
- Task: "Montagetermin vereinbaren"

---

## 📧 EMAIL 6: Rechnung (WEG B - Optional mit PDF)

**An:** info@cdtechnologies.de  
**Von:** [GLEICHE EMAIL]  
**Betreff:** Rechnung Dachausbau
**Anhang:** (Optional) Rechnung.pdf

**Text:**
```
Anbei die Rechnung für den abgeschlossenen Dachausbau.

Vielen Dank für die hervorragende Arbeit!

Mit freundlichen Grüßen
Max Mustermann
```

**Expected:**
- ✅ WEG B Notification
- Falls PDF angehängt:
  - 📄 Rechnung im System anzeigen (Dashboard Link)
  - ☁️ PDF in OneDrive öffnen Link
  - Invoice DB: Rechnung erfasst
- Sentiment: positive

---

## 📧 EMAIL 7: After-Sales Feedback (WEG B)

**An:** info@cdtechnologies.de  
**Von:** [GLEICHE EMAIL]  
**Betreff:** Feedback Dachausbau

**Text:**
```
Guten Tag,

ich möchte mich nochmal für die exzellente Arbeit bedanken!
Das Dach sieht fantastisch aus und alles wurde super sauber hinterlassen.

Ich werde Sie gerne weiterempfehlen.

Mit freundlichen Grüßen
Max Mustermann
```

**Expected:**
- ✅ WEG B Notification
- Sentiment: very positive
- Task: "Follow-up in 3 Monaten" (Low Priority)
- Opportunity bleibt "Won"

---

## 📊 VALIDIERUNG NACH ALLEN EMAILS

### **1. Email-Posteingang prüfen:**
```
Erwarte:
- 1x WEG A Email (Orange, Email 1)
- 6x WEG B Emails (Grün, Emails 2-7)
- Alle mit Dashboard Links
- Smart Actions in WEG B Emails
```

### **2. Sales Pipeline Dashboard:**
```bash
# Dashboard öffnen
open http://localhost:3000/sales-pipeline

Erwarte:
✅ 1 Won Opportunity
   - Titel: "Anfrage Dachausbau"
   - Wert: ~15.000 € (geschätzt)
   - Wahrscheinlichkeit: 100%
   - Kontakt: Max Mustermann
   - Status: Gewonnen
```

### **3. Invoice Dashboard (falls PDF gesendet):**
```bash
# Dashboard öffnen
open http://localhost:3000

Erwarte:
📄 1 Open Invoice (falls PDF in Email 6)
   - Nummer: RE-2024-XXX
   - Kunde: Max Mustermann
   - Status: Offen
```

### **4. API Endpoints prüfen:**
```bash
# Sales Pipeline Statistics
curl -s https://my-langgraph-agent-production.up.railway.app/api/opportunity/statistics | python3 -m json.tool

# Invoice Statistics
curl -s https://my-langgraph-agent-production.up.railway.app/api/invoice/statistics | python3 -m json.tool
```

### **5. Railway Logs prüfen:**
```bash
railway logs --tail 100 | grep -E "WEG A|WEG B|Opportunity|Intent"

Erwarte:
- "🆕 Executing WEG A: Unknown Contact Workflow" (Email 1)
- "✅ Executing WEG B: Known Contact Workflow" (Emails 2-7)
- Intent-Erkennung: appointment, quote_request, order
- Opportunity-Erstellung und Status-Updates
```

---

## ⏱️ TIMING

**Zwischen den Emails:**
- Nach Email 1: **WARTEN bis Kontakt angelegt** (manueller Schritt!)
- Zwischen Emails 2-7: **30-60 Sekunden** (für async Processing)

**Gesamtdauer:** ~10-15 Minuten

---

## ✅ SUCCESS CRITERIA

- [ ] Email 1: WEG A aktiviert, 4 Buttons erhalten
- [ ] Kontakt erfolgreich angelegt in WeClapp
- [ ] Emails 2-7: Alle WEG B, Smart Actions korrekt
- [ ] Opportunity erstellt und Status-Progression:
  - Email 1: Lead (20%)
  - Email 2: Qualifiziert (40%)
  - Email 3: Proposal (50%)
  - Email 4: Won (100%)
- [ ] Dashboard Links in allen Emails sichtbar
- [ ] Tasks automatisch erstellt
- [ ] Sales Pipeline Dashboard zeigt Won Opportunity
- [ ] Keine Memory Crashes auf Railway

---

## 🚨 TROUBLESHOOTING

**Problem:** WEG A wird nicht erkannt
- Lösung: Email-Adresse wirklich unbekannt? Prüfe WeClapp!

**Problem:** WEG B wird nicht erkannt nach Kontakt-Anlegen
- Lösung: Warte 1-2 Minuten, WeClapp Sync braucht Zeit

**Problem:** Dashboard leer
- Lösung: Async Processing läuft noch, warte 2-3 Minuten

**Problem:** Railway Logs zeigen Errors
- Lösung: `railway logs --tail 50` prüfen, Memory Crash möglich

---

**Status:** 📋 Bereit zum Kopieren & Senden  
**Dauer:** ~15 Minuten  
**Schwierigkeit:** Einfach (Copy & Paste)
