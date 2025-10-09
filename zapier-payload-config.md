# 🚀 Zapier Webhook Configuration - Complete Guide

## 📋 **SipGate Zap Einstellungen:**

### **1. Trigger Setup:**
- **App**: "Webhooks by Zapier"
- **Event**: "Catch Hook"
- **Webhook URL**: Wird von Zapier generiert (z.B. `https://hooks.zapier.com/hooks/catch/123456/abcdef/`)

### **2. Action Setup:**
- **App**: "Webhooks by Zapier" 
- **Action**: "POST"
- **URL**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`
- **Method**: POST
- **Content Type**: application/json

### **3. Payload Mapping (wichtig!):**

```json
{
  "from": "{{from}}",
  "to": "{{to}}",
  "direction": "{{direction}}",
  "timestamp": "{{timestamp}}",
  "source": "sipgate",
  "call_duration": "{{duration}}",
  "call_status": "{{status}}",
  "caller_id": "{{caller_id}}",
  "called_number": "{{called_number}}"
}
```

## 🎯 **WhatsApp Zap Einstellungen:**

### **1. Trigger Setup:**
- **App**: "Webhooks by Zapier" ODER "WhatsApp Business"
- **Event**: "Catch Hook" ODER "New Message"

### **2. Action Setup:**
- **URL**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-whatsapp`
- **Method**: POST
- **Content Type**: application/json

### **3. Payload Mapping:**

```json
{
  "from": "{{from}}",
  "message": "{{message}}",
  "timestamp": "{{timestamp}}",
  "source": "whatsapp",
  "message_type": "{{message_type}}",
  "contact_name": "{{contact_name}}",
  "phone_number": "{{phone_number}}"
}
```

## ⚙️ **Zusätzliche Zapier Einstellungen:**

### **Headers (optional aber empfohlen):**
```
Authorization: Bearer YOUR_SECRET_TOKEN
X-Zapier-Source: sipgate-integration
Content-Type: application/json
```

### **Error Handling:**
- ✅ **Retry on Failure**: Aktivieren (3x)
- ✅ **Send Error Notifications**: An deine Email
- ✅ **Log Webhook Calls**: Für Debugging

### **Filters (optional):**
```
Only continue if:
- Direction = "incoming" 
- Duration > 10 seconds (für SipGate)
- Message nicht leer (für WhatsApp)
```

## 🧪 **Test Payloads für Zapier:**

### **SipGate Test:**
```json
{
  "from": "+49123456789",
  "to": "+49987654321",
  "direction": "incoming",
  "timestamp": "2025-10-09T10:30:00Z",
  "source": "sipgate",
  "call_duration": 120,
  "call_status": "answered",
  "caller_id": "Max Mustermann",
  "called_number": "+49987654321"
}
```

### **WhatsApp Test:**
```json
{
  "from": "+49123456789", 
  "message": "Hallo, ich interessiere mich für Ihre Dienstleistungen. Können Sie mir mehr Infos schicken?",
  "timestamp": "2025-10-09T10:30:00Z",
  "source": "whatsapp",
  "message_type": "text",
  "contact_name": "Max Mustermann",
  "phone_number": "+49123456789"
}
```

## 🔧 **In Zapier Dashboard:**

1. **Data Mapping**: Verwende `{{fieldname}}` für dynamische Werte
2. **Static Values**: Setze "source" immer auf "sipgate"/"whatsapp" 
3. **Format**: JSON (nicht Form Data!)
4. **Test**: Immer vor Aktivierung testen!

## ✅ **Empfohlene Reihenfolge:**

1. **SipGate Trigger** einrichten
2. **Test Sample** erstellen 
3. **Railway Action** konfigurieren
4. **Payload** mit obigen Werten mappen
5. **Test Run** durchführen
6. **Zap aktivieren**

**Soll ich dir beim Payload Mapping in Zapier helfen?** 🚀