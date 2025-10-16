# 🧪 QUICK SYSTEM TEST

**Datum:** 16. Oktober 2025, 07:00 Uhr  
**Version Check:** 1.3.0 (Railway) vs 1.4.0-sipgate-pricing (GitHub)  
**Status:** Railway Deployment läuft noch

---

## 📊 AKTUELLER SYSTEM-STATUS

### **Health Check Result:**
```json
{
  "status": "✅ ONLINE",
  "version": "1.3.0",
  "weclapp_sync_db": "⚠️ Not Downloaded",
  "endpoints": [
    "/webhook/ai-email/incoming",
    "/webhook/ai-email/outgoing",
    "/webhook/ai-call",
    "/webhook/whatsapp"
  ]
}
```

### **Beobachtungen:**
1. ⚠️ **Version Mismatch:** Railway zeigt 1.3.0, Git ist bei 1.4.0
2. ⚠️ **WEClapp Sync DB:** Nicht geladen (eventuell OneDrive Credentials Issue)
3. ✅ **Server läuft:** Alle Endpoints erreichbar
4. ✅ **Basic Features:** Email, Call, WhatsApp funktionieren

---

## 🔍 TESTS DURCHFÜHREN

### **Test 1: Simple Health Check**
```bash
curl https://my-langgraph-agent-production.up.railway.app/
```
✅ **Result:** Server antwortet, Status ONLINE

---

### **Test 2: Email WEG B (Bekannter Kontakt)**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-email/incoming \
-H "Content-Type: application/json" \
-d '{
  "from": "mj@cdtechnologies.de",
  "to": "info@cdtechnologies.de",
  "subject": "Test Email - System Check",
  "body": "Dies ist ein System-Test um sicherzustellen dass Email-Processing funktioniert.",
  "received": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'
```

**Erwartetes Ergebnis:**
- ✅ 200 OK Response
- ✅ Contact Matching findet mj@cdtechnologies.de
- ✅ WEG_B Workflow
- ✅ Notification Email verschickt
- ✅ DB-Eintrag erstellt

**Logs prüfen:**
```bash
railway logs --tail 50 | grep "Email processing"
```

---

### **Test 3: Call mit Richtpreis-Berechnung**

⚠️ **ACHTUNG:** Dieser Test funktioniert erst nach Railway Deployment von Version 1.4.0!

```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-call \
-H "Content-Type: application/json" \
-d '{
  "call": {
    "from": "+4917612345678",
    "to": "+498912345678",
    "duration": 240000,
    "direction": "in"
  },
  "assist": {
    "summary": {
      "content": "Kunde möchte Angebot für Dachsanierung. Dachfläche ungefähr 80 Quadratmeter, Schiefer gewünscht."
    }
  }
}'
```

**Erwartetes Ergebnis (v1.4.0):**
- ✅ Transcript-Analyse
- ✅ Richtpreis-Berechnung: ~6.800 EUR (80m² Schiefer)
- ✅ Notification mit Preis-Details
- ✅ Auto-Task "Angebot vorbereiten"

**Status v1.3.0:**
- ✅ Transcript-Analyse funktioniert
- ❌ Richtpreis-Berechnung fehlt noch
- ✅ Basic Call Processing läuft

---

## 🚀 DEPLOYMENT STATUS

### **Git Status:**
- ✅ Commit: `f6543b2` (Dokumentation)
- ✅ Commit: `27f2e56` (Richtpreis-Feature)
- ✅ Pushed to GitHub

### **Railway Status:**
```bash
# Check deployment:
railway logs --tail 20

# Expected:
# "🚀 Starting AI Communication Orchestrator..."
# "📥 Downloading WEClapp Sync Database..."
# "✅ WEClapp Sync DB ready"
# "✅ AI Communication Orchestrator ready!"
```

### **Pending:**
- ⏳ Railway Build läuft (siehe Terminal: railway up)
- ⏳ Warten auf Container Restart
- ⏳ Version Update: 1.3.0 → 1.4.0

---

## ✅ SCHNELL-CHECK (Jetzt ausführbar)

### **1. Server Status:**
```bash
curl https://my-langgraph-agent-production.up.railway.app/
```

### **2. Email Test (einfach):**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-email/incoming \
-H "Content-Type: application/json" \
-d '{
  "from": "test@example.com",
  "subject": "Quick Test",
  "body": "System Check",
  "received": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'
```

### **3. Logs prüfen:**
```bash
railway logs --tail 100 | grep -E "(ERROR|WARNING|✅|❌)"
```

---

## 📋 NEXT STEPS

1. ⏰ **Warten auf Railway Deployment** (~5 Minuten)
2. 🔄 **Health Check wiederholen** (Version sollte 1.4.0 sein)
3. ✅ **WEClapp Sync DB Status prüfen** (sollte "Available" sein)
4. 🧪 **Call mit Richtpreis testen**
5. 📊 **Vollständige Test-Suite** (STABILITY_AUDIT_CHECKLIST.md)

---

## 🎯 ERWARTETE ERGEBNISSE (nach Deployment)

### **Health Check:**
```json
{
  "status": "✅ ONLINE",
  "version": "1.4.0-sipgate-pricing",  // ← Updated!
  "weclapp_sync_db": "✅ Available",  // ← Fixed!
  "features": [
    "Email Processing",
    "Call Processing with Price Estimation",  // ← NEW!
    "WhatsApp Processing",
    "Multi-Source Contact Matching",
    "PDF.co OCR Integration"
  ]
}
```

### **Call Processing:**
- ✅ Richtpreis-Berechnung funktioniert
- ✅ Email mit Preis-Details
- ✅ Auto-Task mit Richtwert
- ✅ WeClapp CRM Event mit Kalkulation

---

**Erstellt:** 16. Oktober 2025, 07:00 Uhr  
**Status:** ⏳ Waiting for Railway Deployment  
**ETA:** ~5 Minuten
