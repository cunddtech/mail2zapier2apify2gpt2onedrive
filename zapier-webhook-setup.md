# Zapier Webhook Setup - Step by Step Guide

## 🚀 Zapier Webhook Konfiguration (5 Min Setup)

### **Deine URLs:**
- **SipGate Webhook**: `https://nonequivocating-subsimian-hermina.ngrok-free.dev/webhook/sipgate`
- **WhatsApp Webhook**: `https://nonequivocating-subsimian-hermina.ngrok-free.dev/webhook/whatsapp`
- **ngrok Web Interface**: `http://127.0.0.1:4040` (für Debugging)

## 📋 **Setup Steps:**

### **Step 1: Zapier Dashboard öffnen**
1. Gehe zu: https://zapier.com/app/dashboard
2. Klicke: **"Create Zap"**

### **Step 2: SipGate Integration**
1. **Trigger wählen**: "Webhooks by Zapier"
2. **Event**: "Catch Hook"  
3. **Webhook URL**: `https://nonequivocating-subsimian-hermina.ngrok-free.dev/webhook/sipgate`
4. **Test**: Webhook URL wird generiert

### **Step 3: Action konfigurieren**
1. **Action wählen**: "Webhooks by Zapier" ODER "Apify"
2. **Event**: "POST" Request
3. **URL**: Deine Apify Actor URL oder Railway Orchestrator
4. **Data**: SipGate Call-Daten weiterleiten

### **Step 4: WhatsApp Integration (separat)**
1. **Neuer Zap**: "Create Zap"
2. **Trigger**: "Webhooks by Zapier" → "Catch Hook"
3. **Webhook URL**: `https://nonequivocating-subsimian-hermina.ngrok-free.dev/webhook/whatsapp`
4. **Action**: Weiterleitung an Apify/Orchestrator

## 🧪 **Test Workflow:**

### **SipGate Test:**
```bash
curl -X POST https://nonequivocating-subsimian-hermina.ngrok-free.dev/webhook/sipgate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+49123456789",
    "to": "+49987654321", 
    "direction": "incoming",
    "timestamp": "2025-10-09T10:00:00Z"
  }'
```

### **WhatsApp Test:**
```bash
curl -X POST https://nonequivocating-subsimian-hermina.ngrok-free.dev/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+49123456789",
    "message": "Hallo, ich interessiere mich für Ihre Dienstleistungen",
    "timestamp": "2025-10-09T10:00:00Z"
  }'
```

## 🎯 **Nächste Schritte:**

1. **Zapier Dashboard öffnen** → Create Zap
2. **SipGate Webhook konfigurieren**  
3. **Integration testen** mit curl/Postman
4. **WhatsApp Webhook hinzufügen**
5. **Mit bestehendem Email-Flow verbinden**

**Ready? Sag Bescheid wenn du das Zapier Dashboard geöffnet hast!** 🚀