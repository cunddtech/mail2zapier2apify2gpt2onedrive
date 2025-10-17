# 🧪 QUICK SYSTEM TEST

**Datum:** 17. Oktober 2025 ⚡ UPDATED  
**Version:** 1.4.2-feedback-enhancement (Railway Production)  
**Status:** ✅ All Systems Operational + New Features

---

## 🎯 **NEUE TEST-SZENARIEN (17. Oktober 2025)**

### **Test 1: Invoice from Unknown Supplier (WEG A)**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-email/test \
-H "Content-Type: application/json" \
-d '{
  "from": "buchhaltung@ziegelwerke-mueller.de",
  "to": "info@cdtechnologies.de",
  "subject": "Rechnung Nr. 2024-1234 - Ziegellieferung",
  "body": "Sehr geehrte Damen und Herren,\n\nanbei erhalten Sie unsere Rechnung Nr. 2024-1234 über die Lieferung von 500 Ziegel am 10.10.2024.\n\nRechnungsbetrag: 2.450,00 EUR netto\nMwSt. 19%: 465,50 EUR\nGesamtbetrag: 2.915,50 EUR\n\nZahlbar innerhalb 14 Tagen.\n\nMit freundlichen Grüßen\nZiegelwerke Müller GmbH",
  "attachments": [
    {
      "filename": "Rechnung_2024-1234.pdf",
      "size": 145000,
      "content_type": "application/pdf"
    }
  ]
}'
```

**Erwartetes Ergebnis:**
- ✅ Workflow: WEG_A (Unknown Contact)
- ✅ AI Intent: "support" oder "invoice"
- ✅ Attachment: Classified as "invoice"
- ✅ OCR: Simulated invoice data
- ✅ Notification sent with NEW BUTTONS:
  - ✅ KONTAKT ANLEGEN
  - 🏭 **LIEFERANT ANLEGEN** (NEW!)
  - ➕ ZU BESTEHENDEM HINZUFÜGEN
  - ✅ **DATEN OK** (NEW!)
  - ⚠️ **FEHLER MELDEN** (NEW!)
  - 🐛 PROBLEM MELDEN
- ✅ Database saved (with known error: attachments table missing)

**Logs prüfen:**
```bash
railway logs --tail 50 | grep "WEG_A\|invoice\|Ziegelwerke"
```

---

### **Test 2: Price Estimation from Call (WEG A)**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-call \
-H "Content-Type: application/json" \
-d '{
  "from": "+491234567890",
  "to": "+4962337069990",
  "direction": "inbound",
  "status": "completed",
  "duration": 180,
  "transcription": "Guten Tag, ich brauche 120 Quadratmeter Ziegel in guter Qualität und eine Dämmung"
}'
```

**Erwartetes Ergebnis:**
- ✅ Workflow: WEG_A
- ✅ Contact: Not found
- 💰 **Price Estimate:** ~19.200 EUR
  - Area: 120 m²
  - Material: Ziegel (premium)
  - Additional: Dämmung
  - Confidence: 90%
- ✅ Notification with price breakdown
- ✅ All action buttons including feedback options

**Logs prüfen:**
```bash
railway logs --tail 30 | grep "💰\|Price\|19200"
```

---

### **Test 3: Feedback Button Test**
```bash
# Test "DATEN OK" feedback
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/feedback \
-H "Content-Type: application/json" \
-d '{
  "action": "data_good",
  "context": {
    "email_id": "test-123",
    "sender": "+491234567890",
    "workflow": "WEG_A"
  }
}'
```

**Erwartetes Ergebnis:**
```json
{
  "status": "success",
  "message": "✅ Danke für die Bestätigung! Datenqualität dokumentiert.",
  "feedback_id": "fb-1760636721",
  "priority": "low"
}
```

**Test "FEHLER MELDEN":**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/feedback \
-H "Content-Type: application/json" \
-d '{
  "action": "data_error",
  "message": "Material wurde falsch erkannt",
  "context": {
    "email_id": "test-124",
    "sender": "buchhaltung@ziegelwerke-mueller.de",
    "workflow": "WEG_A"
  }
}'
```

**Erwartetes Ergebnis:**
```json
{
  "status": "success",
  "message": "⚠️ Fehler dokumentiert. Wir werden das überprüfen.",
  "feedback_id": "fb-1760636732",
  "priority": "high"
}
```

**Feedback Log prüfen:**
```bash
railway logs --tail 20 | grep "FEEDBACK"
```

---

## 📊 AKTUELLER SYSTEM-STATUS

### **Health Check Result:**
```json
{
  "status": "✅ AI Communication Orchestrator ONLINE",
  "version": "1.4.2-feedback-enhancement",
  "environment": "production",
  "weclapp_sync_db": "⚠️ OneDrive 403 (non-critical)",
  "endpoints": [
    "/webhook/ai-email/incoming",
    "/webhook/ai-email/outgoing",
    "/webhook/ai-email/test",
    "/webhook/ai-call",
    "/webhook/frontdesk",
    "/webhook/feedback",
    "/webhook/ai-whatsapp"
  ],
  "features": [
    "Email Direction Detection",
    "Document Type Classification",
    "Intelligent Attachment Processing",
    "Type-specific OCR Routes",
    "💰 Automatic Price Estimation (WEG A)",
    "🏭 Supplier Creation Button (WEG A)",
    "✅ Data Quality Feedback System",
    "🧪 Test Endpoint with JSON Attachments"
  ]
}
```

### **Beobachtungen:**
1. ✅ **Version:** 1.4.2-feedback-enhancement deployed
2. ⚠️ **WEClapp Sync DB:** OneDrive 403 (bekanntes Issue, nicht kritisch - fallback zu WeClapp API)
3. ✅ **Server:** Alle Endpoints operational
4. ✅ **New Features:** Feedback system, supplier button, test endpoint
5. ✅ **Price Estimation:** Working for WEG A (calls)
6. 📊 **LangSmith:** Active tracing (https://smith.langchain.com/o/cdtech/projects/production-ai-orchestrator)

---

## 🔍 CLASSIC TESTS (Updated)

### **Test 4: Email WEG B (Bekannter Kontakt)**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-email/test \
-H "Content-Type: application/json" \
-d '{
  "from": "known.customer@example.com",
  "to": "info@cdtechnologies.de",
  "subject": "Terminanfrage - Aufmaß",
  "body": "Guten Tag, ich hätte gerne einen Termin für ein Aufmaß nächste Woche. Wann hätten Sie Zeit?",
  "attachments": []
}'
```

**Erwartetes Ergebnis:**
- ✅ Workflow: WEG_B (wenn Kontakt in WeClapp existiert)
- ✅ AI Intent: "appointment" oder "quote_request"
- ✅ Task Generated: "Termin vereinbaren"
- ✅ Notification with buttons:
  - 📋 IN CRM ÖFFNEN
  - ✅ **DATEN OK** (NEW!)
  - ⚠️ **FEHLER MELDEN** (NEW!)
  - 🐛 PROBLEM MELDEN

---

### **Test 5: WhatsApp Message Processing**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-whatsapp \
-H "Content-Type: application/json" \
-d '{
  "from": "+491234567890",
  "message": "Hallo, können Sie mir ein Angebot für eine Dachsanierung machen?",
  "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'
```

**Erwartetes Ergebnis:**
- ✅ Contact lookup
- ✅ AI analysis
- ✅ Task creation
- ✅ Notification sent

---

## 🚀 DEPLOYMENT STATUS

### **Git Status:**
- ✅ Latest Commit: `dbe6142` (Test endpoint fix)
- ✅ Version: 1.4.2-feedback-enhancement
- ✅ Features:
  - 🏭 Supplier creation button
  - ✅ Data quality feedback (good/error)
  - 🧪 Test endpoint with JSON attachments
  - 💰 Price estimation (WEG A)
  - 📊 Priority-based feedback logging

### **Railway Status:**
```bash
# Check current deployment:
railway logs --tail 20

# Expected output:
# "✅ AI Communication Orchestrator ready!"
# "� Environment Check: OpenAI API Key configured: True"
# "🔍 Environment Check: WeClapp API Token configured: True"
# "INFO: Uvicorn running on 0.0.0.0:5001"
```

### **Current Version:**
- ✅ Railway: 1.4.2-feedback-enhancement
- ✅ GitHub: In Sync
- ✅ All Features: Deployed & Tested

### **Known Issues (Non-Critical):**
- ⚠️ Database: `attachments` table missing (emails still process)
- ⚠️ OneDrive: 403 errors (fallback to WeClapp API works)
- 📎 Attachments HTML: Cosmetic duplicate in notification

---

## 📊 MONITORING & DEBUGGING

### **LangSmith Traces:**
```
URL: https://smith.langchain.com/o/cdtech/projects/production-ai-orchestrator
```
- ✅ Real-time workflow tracing
- ✅ Performance metrics per node
- ✅ Input/Output inspection
- ✅ Error tracking

### **Feedback Log:**
```bash
# View feedback entries (if accessible)
cat feedback_log.jsonl | jq '.'

# Railway logs for feedback:
railway logs --tail 50 | grep "FEEDBACK"
```

### **Database Check:**
```bash
# Railway environment (if sqlite accessible)
sqlite3 email_data.db "SELECT COUNT(*) FROM email_data;"
```

---

## ✅ QUICK VERIFICATION CHECKLIST

### **1. Server Health:**
```bash
curl https://my-langgraph-agent-production.up.railway.app/ | jq '.status'
# Expected: "✅ AI Communication Orchestrator ONLINE"
```

### **2. Test Endpoint:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-email/test \
-H "Content-Type: application/json" \
-d '{"from":"test@test.com","subject":"Test","body":"Quick check"}' \
| jq '.status'
# Expected: "success"
```

### **3. Feedback System:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/feedback \
-H "Content-Type: application/json" \
-d '{"action":"data_good","context":{"test":true}}' \
| jq '.message'
# Expected: "✅ Danke für die Bestätigung! Datenqualität dokumentiert."
```

### **4. Price Estimation:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-call \
-H "Content-Type: application/json" \
-d '{"from":"+49123","transcription":"50 Quadratmeter Ziegel"}' \
| jq '.ai_processing.price_estimate.total_cost'
# Expected: Number (e.g., 4000.0)
```

---

## 🎯 NEXT STEPS

### **Immediate (Today):**
1. ✅ Test invoice email notification in Zapier
2. ✅ Verify "LIEFERANT ANLEGEN" button appears
3. ✅ Click feedback buttons and check Railway logs
4. ⚠️ Fix `attachments` table creation

### **This Week:**
1. 🔧 Verify SipGate phone number extraction
2. 📊 Implement pricing for WEG B (known contacts)
3. 🔍 Fix attachment HTML duplication
4. 📱 Test WhatsApp media processing

### **Monitoring:**
1. 📊 Review LangSmith traces daily
2. 📝 Analyze feedback_log.jsonl weekly
3. 🐛 Track error patterns
4. ⚡ Monitor performance metrics### **3. Logs prüfen:**
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
