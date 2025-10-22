# 🎯 Deployment 17: Status-basierte Smart Actions - Test Guide

## ✅ WAS WURDE IMPLEMENTIERT

**NEU:** WeClapp Opportunity Status Integration  
**Vorteil:** Smart Actions passen sich automatisch an die aktuelle Sales Pipeline Phase an!

### 🔄 WIE ES FUNKTIONIERT

```
1. Email kommt rein → WEG B (bekannter Kontakt)
2. System prüft WeClapp: "Hat dieser Kontakt eine offene Opportunity?"
3a. JA → Holt Opportunity Status (z.B. "Proposal") → Zeigt ANGEBOT Actions
3b. NEIN → Fallback zu Intent-basierten Actions
4. Email mit phasenspezifischen Smart Actions wird versendet
```

---

## 📊 8 SALES PIPELINE PHASEN

### Phase 1: LEAD (10-20%)
**Wann:** Erstkontakt, neuer Interessent  
**Smart Actions:**
- 📞 KONTAKT AUFNEHMEN
- 📧 MAIL SENDEN
- 📋 DATEN VERVOLLSTÄNDIGEN

**Test Email:**
```
An: info@cdtechnologies.de
Von: [bekannter Kontakt mit Opportunity Stage "Lead"]
Betreff: Interesse an Dachausbau
Text: Ich interessiere mich für Ihre Dienstleistungen.
```

---

### Phase 2: QUALIFIED (30-40%)
**Wann:** Kontakt aufgenommen, Bedarf qualifiziert  
**Smart Actions:**
- 💶 RICHTPREIS ERSTELLEN
- 📋 DATEN AUFNEHMEN
- 📅 AUFMASS TERMINIEREN
- 📄 UNTERLAGEN PRÜFEN

**Test Email:**
```
An: info@cdtechnologies.de
Von: [bekannter Kontakt mit Opportunity Stage "Qualified"]
Betreff: Weitere Informationen benötigt
Text: Können Sie mir mehr Details zum Projekt geben?
```

---

### Phase 3: MEASUREMENT (50%)
**Wann:** Aufmaßtermin vereinbart/durchgeführt  
**Smart Actions:**
- 📅 TERMIN BESTÄTIGEN
- 📝 AUFMASS ERFASSEN
- 📸 FOTOS HOCHLADEN
- 💰 ANGEBOT VORBEREITEN

**Test Email:**
```
An: info@cdtechnologies.de
Von: [bekannter Kontakt mit Opportunity Stage "Measurement"]
Betreff: Aufmaßtermin Bestätigung
Text: Wann findet das Aufmaß statt?
```

---

### Phase 4: PROPOSAL (60-70%)
**Wann:** Angebot erstellt, wartet auf Entscheidung  
**Smart Actions:**
- 📊 ANGEBOT ERSTELLEN
- 📧 ANGEBOT VERSENDEN
- 📞 NACHFASSEN

**Test Email:**
```
An: info@cdtechnologies.de
Von: [bekannter Kontakt mit Opportunity Stage "Proposal"]
Betreff: Rückfrage zum Angebot
Text: Ich habe eine Frage zu Ihrem Angebot.
```

---

### Phase 5: ORDER (80-90%) ✅ BEREITS GETESTET
**Wann:** Auftrag erteilt  
**Smart Actions:**
- ✅ AUFTRAG ANLEGEN
- 📦 LIEFERANT BESTELLEN
- 📄 AB VERSENDEN
- 💶 ANZAHLUNGSRECHNUNG
- 🔧 MONTAGE TERMINIEREN

**Test Email:**
```
An: info@cdtechnologies.de
Von: max.mustermann.test2025@gmail.com
Betreff: Auftragserteilung Dachausbau
Text: Ihr Angebot passt perfekt! Ich möchte den Auftrag hiermit verbindlich erteilen.
```
✅ **Bereits in Email 4 der Test Suite validiert!**

---

### Phase 6: PRE-INSTALLATION (90%)
**Wann:** Auftrag bestätigt, Vorbereitung Montage  
**Smart Actions:**
- 📋 LIEFERSCHEIN VORBEREITEN
- 📝 LEISTUNGSNACHWEIS VORBEREITEN
- 📦 MATERIAL PRÜFEN
- 📅 MONTAGE BESTÄTIGEN

**Test Email:**
```
An: info@cdtechnologies.de
Von: [bekannter Kontakt mit Opportunity Stage "Pre-Installation"]
Betreff: Montagevorbereitung
Text: Wann wird das Material geliefert?
```

---

### Phase 7: INSTALLATION (95%)
**Wann:** Montage läuft/abgeschlossen  
**Smart Actions:**
- ✅ MONTAGE ABSCHLIESSEN
- 📋 LIEFERSCHEIN ZURÜCK
- 📝 LEISTUNGSNACHWEIS ZURÜCK
- 📸 ABNAHME DOKUMENTIEREN

**Test Email:**
```
An: info@cdtechnologies.de
Von: [bekannter Kontakt mit Opportunity Stage "Installation"]
Betreff: Montage Abschluss
Text: Die Montage ist fertig, wo schicke ich die Unterlagen hin?
```

---

### Phase 8: WON (100%)
**Wann:** Projekt abgeschlossen  
**Smart Actions:**
- 💶 RECHNUNG ERSTELLEN
- 📧 RECHNUNG VERSENDEN
- 💳 ZAHLUNG ERFASSEN
- 😊 FEEDBACK EINHOLEN
- ⭐ BEWERTUNG ANFORDERN

**Test Email:**
```
An: info@cdtechnologies.de
Von: [bekannter Kontakt mit Opportunity Stage "Won"]
Betreff: Projekt abgeschlossen
Text: Vielen Dank für die tolle Arbeit!
```

---

## 🧪 VOLLSTÄNDIGE TEST SUITE

### Test 1: Opportunity-basierte Actions (PRIORITY 1)

**Setup:**
1. Erstelle Kontakt in WeClapp mit offener Opportunity
2. Setze Opportunity Stage (z.B. "Proposal")
3. Sende Email von diesem Kontakt

**Expected Result:**
- System findet Opportunity
- Log: `📊 Opportunity Status: ID=..., Stage=Proposal, Probability=60%`
- Log: `✅ Using X stage-based smart actions for: Proposal`
- Email enthält ANGEBOT Actions (📊 ANGEBOT ERSTELLEN, 📧 ANGEBOT VERSENDEN, 📞 NACHFASSEN)

---

### Test 2: Intent-basierte Actions Fallback (PRIORITY 2)

**Setup:**
1. Verwende Kontakt OHNE offene Opportunity
2. Sende Email mit klarem Intent (z.B. "Auftrag")

**Expected Result:**
- System findet keine Opportunity
- Log: `ℹ️ No open opportunity found for contact X`
- Log: `ℹ️ Using fallback ORDER actions (no opportunity found)`
- Email enthält Intent-basierte ORDER Actions (Fallback)

---

### Test 3: Stage-Progression Test

**Email-Sequenz für einen Kontakt:**

1. **EMAIL 1**: Lead Stage → Zeigt KONTAKT Actions
2. **EMAIL 2**: Manually update zu "Qualified" → Zeigt RICHTPREIS/AUFMASS Actions
3. **EMAIL 3**: Manually update zu "Proposal" → Zeigt ANGEBOT Actions
4. **EMAIL 4**: Manually update zu "Order" → Zeigt ORDER Actions (6 Buttons)
5. **EMAIL 5**: Manually update zu "Won" → Zeigt RECHNUNG/FEEDBACK Actions

**Erwartung:** Jede Email zeigt andere Smart Actions basierend auf Opportunity Stage!

---

## 📋 RAILWAY LOGS PRÜFEN

```bash
# Check Opportunity Status Abfrage
railway logs --tail 200 | grep "Opportunity Status"

# Expected Output:
# 📊 Opportunity Status: ID=12345, Stage=Proposal, Probability=60%

# Check Stage-based Actions
railway logs --tail 200 | grep "stage-based smart actions"

# Expected Output:
# ✅ Using 4 stage-based smart actions for: Proposal

# Check Fallback zu Intent
railway logs --tail 200 | grep "fallback ORDER actions"

# Expected Output (wenn keine Opportunity):
# ℹ️ Using fallback ORDER actions (no opportunity found)
```

---

## ⚙️ WECLAPP UMGEBUNGSVARIABLEN

**Erforderlich in Railway:**
```bash
WECLAPP_API_KEY=<your-api-key>
WECLAPP_TENANT=cundd
```

**Prüfen:**
```bash
railway variables | grep WECLAPP
```

---

## 🎯 SUCCESS CRITERIA

✅ **Test PASSED wenn:**
1. Opportunity Status wird aus WeClapp geholt (Log: "Opportunity Status")
2. Stage-basierte Actions werden generiert (Log: "stage-based smart actions")
3. Email enthält phasenspezifische Buttons (nicht generic)
4. Fallback funktioniert wenn keine Opportunity (Log: "fallback")
5. Keine doppelten "IN CRM ÖFFNEN" Buttons
6. Opportunity-Link statt Contact-Link wenn Opportunity vorhanden

---

## 🔧 TROUBLESHOOTING

**Problem 1: "No open opportunity found"**
- Lösung: Opportunity Status in WeClapp muss "OPEN" sein (nicht "WON" oder "LOST")

**Problem 2: "Generic actions statt stage-specific"**
- Lösung: Check WECLAPP_API_KEY in Railway Environment Variables

**Problem 3: "Doppelte Actions in Email"**
- Gelöst: Code prüft jetzt auf Duplikate mit `any(a.get("action") == "view_in_crm")`

**Problem 4: "WeClapp API Error"**
- Check: `railway logs --tail 100 | grep "WeClapp API"`
- Mögliche Ursache: API Key abgelaufen oder falsche Permissions

---

## 📊 DEPLOYMENT STATUS

**Deployment 17:**
- Status: ✅ DEPLOYED
- Commit: 06202a5
- Railway: Version 1.4.0-status-based-actions
- New Module: `modules/crm/opportunity_status_handler.py`
- Documentation: `SALES_PIPELINE_PHASES.md`

**Features:**
- 8 Sales Pipeline Phasen
- 35+ phasenspezifische Smart Actions
- WeClapp Opportunity Status Integration
- Automatische Phase-Erkennung
- Intent-based Fallback

---

**Erstellt:** 2025-10-21  
**Status:** 🧪 Bereit für Testing  
**Next:** Vollständige Test Suite mit allen 8 Phasen durchführen
