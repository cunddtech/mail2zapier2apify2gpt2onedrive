# 🧪 TEST: Loop Prevention Filter

## 🎯 TEST ZIEL
Verifizieren, dass System-Emails NICHT mehr verarbeitet werden

---

## ✅ TEST 1: System Sender Check

**Simulation:** Email von mj@cdtechnologies.de (System Sender)

**Erwartetes Verhalten:**
```
🚫 LOOP PREVENTION: Ignoring email from system sender: mj@cdtechnologies.de
```

**Test Command:**
```bash
curl -X POST https://handsome-rejoicing-production.up.railway.app/webhook/ai-email/outgoing \
  -H "Content-Type: application/json" \
  -d '{
    "from": "mj@cdtechnologies.de",
    "subject": "Test System Email",
    "body": "This should be ignored",
    "message_id": "test-loop-prevention-1",
    "user_email": "info@cdtechnologies.de"
  }'
```

---

## ✅ TEST 2: System Marker Check

**Simulation:** Email mit "C&D AI" im Subject

**Erwartetes Verhalten:**
```
🚫 LOOP PREVENTION: Ignoring email with system marker in subject: C&D AI - Neue Anfrage
```

**Test Command:**
```bash
curl -X POST https://handsome-rejoicing-production.up.railway.app/webhook/ai-email/outgoing \
  -H "Content-Type: application/json" \
  -d '{
    "from": "customer@example.com",
    "subject": "C&D AI - Neue Anfrage",
    "body": "This should be ignored",
    "message_id": "test-loop-prevention-2",
    "user_email": "info@cdtechnologies.de"
  }'
```

---

## ✅ TEST 3: Normal Email (Should Process)

**Simulation:** Normale Kunden-Email

**Erwartetes Verhalten:**
```
📧 Email webhook: message_id=test-loop-prevention-3
✅ Email processing complete
```

**Test Command:**
```bash
curl -X POST https://handsome-rejoicing-production.up.railway.app/webhook/ai-email/outgoing \
  -H "Content-Type: application/json" \
  -d '{
    "from": "kunde@example.com",
    "subject": "Anfrage Dachausbau",
    "body": "Ich hätte gerne ein Angebot",
    "message_id": "test-loop-prevention-3",
    "user_email": "info@cdtechnologies.de"
  }'
```

---

## 🔍 LOG VALIDATION

Nach jedem Test ausführen:
```bash
railway logs --tail 50 | grep -E "LOOP PREVENTION|test-loop-prevention"
```

**Erwartete Ausgabe TEST 1 & 2:**
```
🚫 LOOP PREVENTION: Ignoring email from system sender: mj@cdtechnologies.de
🚫 LOOP PREVENTION: Ignoring email with system marker in subject: C&D AI - Neue Anfrage
```

**Erwartete Ausgabe TEST 3:**
```
📧 Email webhook: message_id=test-loop-prevention-3
✅ Email processing complete
```

---

## 📊 SUCCESS CRITERIA

✅ TEST 1: System sender emails are BLOCKED  
✅ TEST 2: System marker emails are BLOCKED  
✅ TEST 3: Normal emails are PROCESSED  
✅ No infinite loops detected  
✅ Zapier "Outgoing" Zap can stay ON without issues

---

## 🚨 ROLLBACK PLAN

Falls Tests fehlschlagen:
1. Zap "Outgoing (Sent Items → Railway)" sofort pausieren
2. Code überprüfen: `production_langgraph_orchestrator.py` Zeilen 4266-4281
3. Logs analysieren: `railway logs --tail 200`
4. Hotfix deployen wenn nötig

---

**Test Status:** ⏳ READY TO EXECUTE
**Date:** 21. Oktober 2025, 02:30 UTC
**Deployment:** 18 (Commit: 57dc908)
