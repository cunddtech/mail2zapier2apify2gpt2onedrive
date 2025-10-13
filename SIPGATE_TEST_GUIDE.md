# 📞 SIPGATE INTEGRATION - TEST GUIDE

## 🎯 **TEST-SZENARIEN**

### **Test 1: Einfacher Anruf (Bekannter Kontakt)**
**Ziel:** Railway erkennt Kontakt, erstellt Task, loggt in WeClapp

**Test-Ablauf:**
1. Rufe **eine der SipGate-Nummern an** (mj, kt, lh)
2. Sprich kurze Nachricht:
   ```
   "Hallo, hier ist Frank Zimmer. Ich brauche ein Angebot für ein Terrassendach."
   ```
3. Lege auf

**Erwartetes Ergebnis:**
- ✅ SipGate Webhook → Zapier → Railway
- ✅ Railway erkennt: Frank Zimmer (WeClapp ID 4400)
- ✅ WEG_B Workflow (Known Contact)
- ✅ Task: "Angebot erstellen - Terrassendach Frank Zimmer"
- ✅ WeClapp Communication Log Entry
- ✅ Notification Email an mj@

---

### **Test 2: Anruf von unbekannter Nummer**
**Ziel:** WEG_A Workflow für unbekannten Anrufer

**Test-Ablauf:**
1. Rufe von **unbekannter Handynummer** an
2. Sprich Nachricht:
   ```
   "Guten Tag, ich interessiere mich für eine Markise. Bitte rufen Sie zurück."
   ```
3. Lege auf

**Erwartetes Ergebnis:**
- ✅ Railway erkennt: Unbekannte Nummer
- ✅ WEG_A Workflow (Unknown Contact)
- ✅ Notification Email mit 4 Buttons (KONTAKT ANLEGEN, etc.)
- ✅ Button "KONTAKT ANLEGEN" funktioniert

---

### **Test 3: Termin-Anfrage**
**Ziel:** AI erkennt Terminwunsch, erstellt entsprechende Task

**Test-Ablauf:**
1. Rufe an und sage:
   ```
   "Hallo, ich würde gerne einen Termin für ein Aufmaß vereinbaren. 
   Wäre nächste Woche Mittwoch möglich?"
   ```

**Erwartetes Ergebnis:**
- ✅ AI Analysis: Intent = "appointment_request"
- ✅ Task: "Termin vereinbaren - Aufmaß am Mittwoch"
- ✅ Urgency: "medium" oder "high"

---

### **Test 4: Notfall/Dringend**
**Ziel:** AI erkennt Dringlichkeit, priorisiert Task

**Test-Ablauf:**
1. Rufe an und sage:
   ```
   "NOTFALL! Bei uns ist das Terrassendach undicht, es regnet rein! 
   Bitte sofort zurückrufen!"
   ```

**Erwartetes Ergebnis:**
- ✅ AI Analysis: Urgency = "high" oder "critical"
- ✅ Sentiment: "negative" (Stress erkennbar)
- ✅ Task mit HOCH-Priorität
- ✅ Sofort-Notification (nicht nur Email)

---

## 🔍 **MONITORING WÄHREND DES TESTS:**

### **Terminal 1: Railway Logs Live**
```bash
railway logs --follow 2>&1 | grep -E "(SipGate|Call|Transcript|WEG_)"
```

### **Terminal 2: Alle Railway Requests**
```bash
railway logs --follow 2>&1 | grep "POST /webhook"
```

### **Terminal 3: AI Analysis**
```bash
railway logs --follow 2>&1 | grep -E "(AI Analysis|Intent|Urgency|Sentiment)"
```

---

## 📊 **ERFOLGS-KRITERIEN:**

| Test | Status | Railway Response | WeClapp Update | Notification |
|------|--------|------------------|----------------|--------------|
| Bekannter Kontakt | ⏳ | < 8s | ✅ Call Log | ✅ Email |
| Unbekannte Nummer | ⏳ | < 8s | ✅ Temp Entry | ✅ WEG_A Email |
| Termin-Anfrage | ⏳ | < 8s | ✅ Task Created | ✅ Email |
| Notfall | ⏳ | < 8s | ✅ High Prio | ✅ Urgent Email |

---

## 🚨 **TROUBLESHOOTING:**

### **Problem: Keine Railway Logs nach Anruf**
**Ursache:** SipGate Webhook nicht konfiguriert oder Zapier Zap aus
**Fix:** 
1. Prüfe SipGate Webhook Settings
2. Prüfe Zapier Zap "SipGate → Railway" ist AN

### **Problem: Transkript leer oder fehlerhaft**
**Ursache:** SipGate Transkription funktioniert nicht
**Fix:**
1. Prüfe SipGate Transkription-Feature aktiv
2. Falls nicht: Manuelle Transkription oder Whisper API

### **Problem: Kontakt nicht erkannt**
**Ursache:** Telefonnummer nicht in WeClapp
**Fix:**
1. Prüfe WeClapp Kontakt: Telefonnummer korrekt gespeichert?
2. Format: +49... oder 0049... ?

---

## 📝 **TEST-PROTOKOLL:**

Nach jedem Test notiere:
```
Test: [Name]
Zeit: [HH:MM]
Railway Response: [Sekunden]
Workflow: [WEG_A / WEG_B]
Task Created: [Ja/Nein]
WeClapp Updated: [Ja/Nein]
Notification Sent: [Ja/Nein]
Fehler: [Falls vorhanden]
```

---

## 🎯 **NÄCHSTE SCHRITTE NACH ERFOLG:**

1. ✅ SipGate funktioniert → **WhatsApp Business** vorbereiten
2. ✅ Alle Channels getestet → **Production Monitoring** einrichten
3. ✅ Task Management → **Dashboard** für Übersicht bauen

---

*Test Guide erstellt: 13. Oktober 2025, 23:30 Uhr*
*Status: Ready for Testing 📞*
