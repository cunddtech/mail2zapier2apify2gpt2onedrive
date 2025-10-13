# 📋 ZAPIER SCREEN SHARING SESSION - CHECKLIST

**Datum:** 12. Oktober 2025  
**Ziel:** Existierende Zaps duplizieren und für Railway anpassen  
**Dauer:** ~15-30 Minuten

---

## ✅ **VOR DEM SCREEN SHARING:**

### **1. Browser vorbereiten:**
- [ ] Zapier Dashboard öffnen: https://zapier.com/app/zaps
- [ ] Railway Dashboard öffnen: https://railway.app/project/03611984-78a4-458b-bd84-895906a2b149
- [ ] Gmail/Outlook Login bereit (für Test-Emails)

### **2. Accounts checken:**
- [ ] Zapier Login: ✅
- [ ] Gmail mj@ verbunden: ?
- [ ] Gmail info@ verbunden: ?
- [ ] Webhooks by Zapier verfügbar: ?

### **3. Existierende Zaps identifizieren:**
Welche Zaps haben wir bereits, die wir als Vorlage nutzen können?
- [ ] Email → Apify Zap (alt)
- [ ] Email → Webhook Zap (falls vorhanden)
- [ ] Notification Zap (falls vorhanden)

---

## 🎯 **WÄHREND DES SCREEN SHARINGS:**

### **Phase 1: Existierende Zaps analysieren (5 min)**

**Ich schaue mir an:**
1. Liste aller aktiven Zaps
2. Welcher Zap kommt Railway am nächsten?
3. Welche Trigger/Actions sind bereits konfiguriert?
4. Welche Accounts sind verbunden?

**Copy-Paste bereit halten:**
```
Railway Webhook URL (Email):
https://my-langgraph-agent-production.up.railway.app/webhook/ai-email

Railway Webhook URL (Call):
https://my-langgraph-agent-production.up.railway.app/webhook/ai-call

Railway Webhook URL (WhatsApp):
https://my-langgraph-agent-production.up.railway.app/webhook/whatsapp
```

---

### **Phase 2: Zap 1 - mj@ Email → Railway (10 min)**

**Schritt-für-Schritt:**

1. **Existierenden Zap duplizieren:**
   - [ ] Besten Email-Zap auswählen
   - [ ] "Duplicate" klicken
   - [ ] Umbenennen: "AI Email Processor - mj@cdtechnologies.de"

2. **Trigger anpassen:**
   - [ ] Gmail Account: mj@cdtechnologies.de
   - [ ] Event: New Email
   - [ ] Filter (optional): Exclude noreply@, notifications@

3. **Action ändern (Webhook):**
   - [ ] App: Webhooks by Zapier
   - [ ] Action: POST
   - [ ] URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-email`
   - [ ] Payload Type: JSON
   - [ ] Data (Copy-Paste):
     ```json
     {
       "sender": "{{1. Email Address}}",
       "sender_name": "{{1. From Name}}",
       "subject": "{{1. Subject}}",
       "body": "{{1. Body Plain}}",
       "attachments": "{{1. Attachment}}",
       "received_at": "{{1. Received}}",
       "recipient": "mj@cdtechnologies.de",
       "priority": "high"
     }
     ```

4. **Test ausführen:**
   - [ ] Test-Email an mj@ senden
   - [ ] Zapier Test durchführen
   - [ ] Railway Logs prüfen
   - [ ] WeClapp Task überprüfen

5. **Zap aktivieren:**
   - [ ] "Turn On" klicken
   - [ ] Status: ✅ LIVE

---

### **Phase 3: Zap 2 - info@ Email → Railway (5 min)**

**Quick Duplicate von Zap 1:**

1. **Zap 1 duplizieren:**
   - [ ] "AI Email Processor - mj@" → Duplicate
   - [ ] Umbenennen: "AI Email Processor - info@cdtechnologies.de"

2. **Nur Trigger ändern:**
   - [ ] Gmail Account: info@cdtechnologies.de
   - [ ] Payload anpassen: `"recipient": "info@cdtechnologies.de"`
   - [ ] Payload anpassen: `"priority": "medium"`

3. **Test + Aktivieren:**
   - [ ] Test-Email an info@
   - [ ] Railway Logs OK
   - [ ] Turn On

---

### **Phase 4: Notification Zap (Email Benachrichtigungen) (10 min)**

**Wenn noch nicht vorhanden:**

1. **Neuer Zap erstellen:**
   - [ ] Name: "Railway AI Notifications - Email"
   - [ ] Trigger: Webhooks by Zapier
   - [ ] Catch Hook URL kopieren

2. **Railway Webhook URL in .env eintragen:**
   ```bash
   # Zapier Notification Webhook
   ZAPIER_NOTIFICATION_WEBHOOK=https://hooks.zapier.com/hooks/catch/...
   ```

3. **Action: Email by Zapier:**
   - [ ] To: mj@cdtechnologies.de, info@cdtechnologies.de
   - [ ] Subject: `🤖 C&D AI: {{channel}} von {{sender_name}} - {{summary}}`
   - [ ] Body: (Template aus ZAPIER_INTEGRATION_GUIDE.md)

4. **Railway Code anpassen:**
   - [ ] production_langgraph_orchestrator.py
   - [ ] Notification-Call nach Task-Erstellung hinzufügen

---

## 🧪 **TESTS WÄHREND DER SESSION:**

### **Test 1: Einfache Email (Text-only)**
```bash
# Von: test@example.com
# An: mj@cdtechnologies.de
# Betreff: Test - Terminanfrage
# Body: Hallo, ich hätte gerne einen Termin für ein Aufmaß.

Erwartetes Ergebnis:
✅ Zapier Trigger: ~2s
✅ Railway Processing: ~6s
✅ WeClapp Task erstellt: "Termin vereinbaren"
✅ Notification Email: an mj@ + info@
```

### **Test 2: Email mit PDF Attachment**
```bash
# Von: test@example.com
# An: info@cdtechnologies.de
# Betreff: Test - Rechnung
# Anhang: test_rechnung.pdf

Erwartetes Ergebnis:
✅ Zapier Trigger: ~2s
✅ Railway: Attachment detected
✅ Apify Actor Call: mail2zapier2apify2gpt2onedrive
✅ OCR Processing: ~12s
✅ OneDrive Upload: /Test/...
✅ WeClapp Task: "Rechnung prüfen"
✅ Notification Email: mit OneDrive Link
```

### **Test 3: Railway Logs Live-Check**
```bash
# Terminal Command bereit halten:
railway logs --tail

# Oder im Browser:
https://railway.app/project/.../logs
```

---

## 📝 **NOTIZEN WÄHREND DER SESSION:**

### **Existierende Zaps gefunden:**
```
1. Name: _________________
   Trigger: _____________
   Action: ______________
   Status: ______________

2. Name: _________________
   ...
```

### **Anpassungen notwendig:**
```
- [ ] ___________________
- [ ] ___________________
- [ ] ___________________
```

### **Probleme/Errors:**
```
Problem 1: _______________
Lösung: _________________

Problem 2: _______________
Lösung: _________________
```

---

## ✅ **NACH DEM SCREEN SHARING:**

### **Dokumentation aktualisieren:**
- [ ] ZAPIER_INTEGRATION_GUIDE.md mit finalen URLs
- [ ] Screenshots hinzufügen (optional)
- [ ] Zap-Namen dokumentieren

### **Production Validation:**
- [ ] 3 Test-Emails an mj@ senden
- [ ] 3 Test-Emails an info@ senden
- [ ] Railway Logs prüfen (alle erfolgreich?)
- [ ] WeClapp Tasks prüfen (6 Tasks erstellt?)

### **Railway Environment Variables:**
```bash
# Falls Notification Webhook hinzugefügt:
railway variables set ZAPIER_NOTIFICATION_WEBHOOK="https://hooks.zapier.com/..."
```

### **Git Commit:**
```bash
git add .env
git commit -m "Config: Add Zapier notification webhook URL"
git push origin main
```

---

## 🎯 **ERFOLGS-KRITERIEN:**

Nach der Session sollten folgende Zaps **LIVE** sein:

1. ✅ **AI Email Processor - mj@cdtechnologies.de**
   - Trigger: Gmail New Email (mj@)
   - Action: POST to Railway /webhook/ai-email
   - Status: ON

2. ✅ **AI Email Processor - info@cdtechnologies.de**
   - Trigger: Gmail New Email (info@)
   - Action: POST to Railway /webhook/ai-email
   - Status: ON

3. ✅ **Railway AI Notifications - Email** (optional)
   - Trigger: Webhooks by Zapier (Catch Hook)
   - Action: Email by Zapier to mj@ + info@
   - Status: ON

**End-to-End Test erfolgreich:**
- Email senden → Zapier → Railway → WeClapp → Notification ✅

---

## 🚀 **NÄCHSTE SCHRITTE NACH SESSION:**

1. **Phase 2: SipGate Integration**
   - SipGate Webhooks konfigurieren
   - Railway /webhook/ai-call testen

2. **Phase 3: WhatsApp Integration**
   - WhatsApp Business API Setup
   - Railway /webhook/whatsapp testen

3. **Phase 4: Monitoring**
   - Railway Alerts einrichten
   - Zapier Task History überwachen

---

**Session Ready!** 🎉  
**Lass uns loslegen sobald du bereit bist!**
