# 🚀 Zapier Railway Integration - Complete Setup Guide

## ✅ **Deine Railway Webhook URLs (LIVE & Ready):**

- **SipGate**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`
- **WhatsApp**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-whatsapp`  
- **Email**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-email` (bereits aktiv)

## 🎯 **Zapier Setup Steps:**

### **Step 1: SipGate Zap erstellen**
1. **Zapier öffnen**: https://zapier.com/app/dashboard
2. **"Create Zap"** klicken
3. **Trigger wählen**: 
   - App: "SipGate" (falls verfügbar) ODER "Webhooks by Zapier"
   - Event: "New Call" ODER "Catch Hook"

### **Step 2: SipGate Webhook konfigurieren**
**Falls SipGate App verfügbar:**
- SipGate Account verbinden
- Call Events aktivieren

**Falls nur Webhook:**
- Webhook URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`
- Method: POST
- Test mit Sample Call Data

### **Step 3: Action konfigurieren** 
**Option A: Direct Railway (empfohlen)**
- App: "Webhooks by Zapier"
- Action: "POST"
- URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`
- Data: SipGate Call Details weiterleiten

**Option B: Via Apify Actor**  
- App: "Apify"
- Action: "Run Actor"
- Actor: `cdtech~mail2zapier2apify2gpt2onedrive`
- Input: Transformed SipGate Data

### **Step 4: WhatsApp Zap erstellen**
1. **Neuer Zap**: "Create Zap"
2. **Trigger**: "WhatsApp Business" ODER "Webhooks by Zapier"
3. **Action**: Railway Webhook
4. **URL**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-whatsapp`

## 🧪 **Test Data Beispiele:**

### **SipGate Test Payload:**
```json
{
  "from": "+49123456789",
  "to": "+49987654321",
  "direction": "incoming", 
  "timestamp": "2025-10-09T10:00:00Z",
  "source": "sipgate",
  "call_duration": 120,
  "call_status": "answered"
}
```

### **WhatsApp Test Payload:**
```json
{
  "from": "+49123456789",
  "message": "Hallo, ich interessiere mich für Ihre Dienstleistungen",
  "timestamp": "2025-10-09T10:00:00Z", 
  "source": "whatsapp",
  "message_type": "text"
}
```

## 🎯 **Zapier Dashboard URLs:**

- **Create Zap**: https://zapier.com/app/editor
- **My Zaps**: https://zapier.com/app/zaps
- **Connected Apps**: https://zapier.com/app/connections

## ✅ **Vorteile Railway vs. ngrok:**

- ✅ **Permanent URLs** (keine Disconnects)
- ✅ **Bereits live** (sofort einsatzbereit) 
- ✅ **AI Processing** integriert
- ✅ **Production ready**

---

**🚀 READY! Gehe zu https://zapier.com/app/editor und erstelle deinen ersten SipGate Zap!**