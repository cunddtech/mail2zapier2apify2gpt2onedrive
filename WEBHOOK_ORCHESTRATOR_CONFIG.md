# 🔗 **WEBHOOK CONFIGURATION - ORCHESTRATOR INTEGRATION**

## 🎯 **CURRENT ISSUE**
Die einzelnen Apify Apps senden ihre Webhooks noch nicht korrekt an den Railway Orchestrator. Wir müssen die Webhook-Konfigurationen anpassen.

## 🏗️ **ORCHESTRATOR ENDPOINTS (BEREITS LIVE)**

### **Railway LangGraph Orchestrator:**
```
Base URL: https://my-langgraph-agent-production.up.railway.app

Available Endpoints:
✅ /webhook/ai-email    - für Email Processing  
✅ /webhook/ai-call     - für SipGate Calls
✅ /webhook/ai-whatsapp - für WhatsApp Messages  
✅ /health             - Health Check
```

---

## ⚙️ **ERFORDERLICHE KONFIGURATIONEN**

### **1. 📧 EMAIL APP (cdtech~mail2zapier2apify2gpt2onedrive)**
```python
# Aktuell: Interne Verarbeitung + Optional Orchestrator
# ÄNDERN ZU: Primary Orchestrator + Fallback Internal

ORCHESTRATOR_URL = "https://my-langgraph-agent-production.up.railway.app/webhook/ai-email"
FALLBACK_MODE = True  # Bei Orchestrator-Ausfall → interne Verarbeitung
```

**Webhook Flow:**
```
Zapier → Email App → Orchestrator /webhook/ai-email → AI Processing → Response
                ↓ (bei Fehler)
                Internal Processing (Fallback)
```

### **2. 📞 SIPGATE APP**
```python
# Neu zu erstellen oder bestehende App konfigurieren
SIPGATE_WEBHOOK_URL = "https://my-langgraph-agent-production.up.railway.app/webhook/ai-call"

# SipGate Admin Panel Konfiguration:
# Webhook URL: https://apify.com/api/v2/acts/cdtech~sipgate-integration/run-sync
# Method: POST
# Events: newCall, answer, hangup, dtmf
```

**Webhook Flow:**
```
SipGate → Apify SipGate App → Orchestrator /webhook/ai-call → AI Processing → Actions
```

### **3. 💬 WHATSAPP APP**  
```python  
# Neu zu erstellen oder bestehende App konfigurieren
WHATSAPP_WEBHOOK_URL = "https://my-langgraph-agent-production.up.railway.app/webhook/ai-whatsapp"

# WhatsApp Business API Konfiguration:
# Webhook URL: https://apify.com/api/v2/acts/cdtech~whatsapp-integration/run-sync  
# Events: messages, message_deliveries, messaging_optins
```

**Webhook Flow:**
```
WhatsApp → Apify WhatsApp App → Orchestrator /webhook/ai-whatsapp → AI Processing → Response
```

---

## 🔧 **IMPLEMENTATION STEPS**

### **Phase 1: Email App Orchestrator Integration**
```bash
1. Modify src/main_orchestrator.py:
   - Primary Orchestrator call
   - Fallback zu internem System
   - Error handling & logging

2. Environment Variables:
   ORCHESTRATOR_URL="https://my-langgraph-agent-production.up.railway.app"
   RAILWAY_INTEGRATION="true"
   FALLBACK_MODE="true"

3. Deploy to Apify:
   apify push cdtech~mail2zapier2apify2gpt2onedrive
```

### **Phase 2: SipGate Integration**
```bash
1. Create/Configure SipGate App:
   - Payload transformation (SipGate → Orchestrator format)
   - Call event handling
   - Transcription integration

2. SipGate Admin Setup:
   - Webhook endpoint konfigurieren
   - Event subscriptions aktivieren
   - Authentication setup
```

### **Phase 3: WhatsApp Integration**
```bash  
1. Create/Configure WhatsApp App:
   - WhatsApp Business API setup
   - Message type handling
   - Media processing

2. WhatsApp Business Setup:
   - Webhook verification
   - Access token konfiguration
   - Business phone number setup
```

---

## 📊 **PAYLOAD FORMATS**

### **Unified Orchestrator Input Format:**
```json
{
  "lead_source": "email|sipgate|whatsapp",
  "timestamp": "2025-10-08T20:30:00Z", 
  "actor_version": "2.0",
  "data": {
    "email": {
      "subject": "...",
      "sender": "...",
      "content": "...",
      "attachments": [...]
    },
    "sipgate": {
      "call_id": "...",
      "event": "newCall|answer|hangup", 
      "caller": "...",
      "called": "...",
      "duration": 0
    },
    "whatsapp": {
      "sender_phone": "...",
      "message_text": "...",
      "message_type": "text|image|document",
      "chat_id": "..."
    }
  }
}
```

### **Expected Orchestrator Response:**
```json
{
  "success": true,
  "workflow_path": "WEG_A|WEG_B|WEG_C",
  "actions": [
    {
      "type": "create_task",
      "assignee": "sales_team",
      "title": "Follow-up Lead",
      "priority": "high"
    },
    {
      "type": "crm_update", 
      "contact_id": "12345",
      "status": "qualified_lead"
    },
    {
      "type": "calendar_invite",
      "datetime": "2025-10-09T14:00:00Z",
      "participants": ["lead@example.com"]
    }
  ],
  "processing_time": 1.2
}
```

---

## 🚨 **KRITISCHE TODOS**

1. **✅ Email App:** `main_orchestrator.py` als primary deployment
2. **🔧 SipGate:** Webhook endpoint zu Orchestrator umleiten  
3. **🔧 WhatsApp:** Business API + Orchestrator integration
4. **🧪 Testing:** End-to-end Webhook flows validieren
5. **📊 Monitoring:** Error handling + Fallback mechanisms

**Next Action:** Email App Orchestrator Integration deployen?