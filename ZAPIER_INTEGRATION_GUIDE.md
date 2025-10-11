# 🔗 Zapier Integration Guide
## Railway Production Webhooks

**Datum**: 11. Oktober 2025  
**Environment**: Production  
**Base URL**: `https://my-langgraph-agent-production.up.railway.app`

---

## 📡 Webhook Endpoints für Zapier

### 1. Email Webhook
**URL**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-email`  
**Method**: POST  
**Content-Type**: application/json

**Payload Structure**:
```json
{
  "sender": "email@example.com",
  "sender_name": "John Doe",
  "subject": "Email Subject",
  "body": "Email content here...",
  "attachments": [],
  "received_at": "2025-10-11T14:00:00Z"
}
```

**Zapier Trigger**: 
- Gmail: New Email
- Microsoft Outlook: New Email
- Email Parser by Zapier

**Zap Setup**:
1. Trigger: New Email in Gmail/Outlook
2. Action: Webhooks by Zapier → POST Request
3. URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-email`
4. Payload Type: JSON
5. Data:
   - sender: {{Email Address}}
   - sender_name: {{From Name}}
   - subject: {{Subject}}
   - body: {{Body Plain}}
   - received_at: {{Received Time}}

---

### 2. Sipgate Call Webhook
**URL**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`  
**Method**: POST  
**Content-Type**: application/json

**Payload Structure**:
```json
{
  "event": "newCall",
  "direction": "in",
  "from": "+4915112345678",
  "to": "+49301234567",
  "callId": "unique-call-id",
  "user": ["user@company.de"],
  "timestamp": "2025-10-11T14:00:00Z"
}
```

**Sipgate Setup**:
1. Login to Sipgate Account
2. Go to: Settings → Webhooks
3. Create New Webhook
4. URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`
5. Events: ✅ New Call, ✅ Answer, ✅ Hang Up
6. Save Webhook

**Alternativ via Zapier**:
1. Trigger: Webhook by Zapier → Catch Hook
2. Test with Sipgate Webhook
3. Action: Webhooks by Zapier → POST Request
4. URL: Railway Production URL

---

### 3. WhatsApp Webhook
**URL**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-whatsapp`  
**Method**: POST  
**Content-Type**: application/json

**Payload Structure**:
```json
{
  "from": "+4915112345678",
  "message": "WhatsApp message content",
  "timestamp": "2025-10-11T14:00:00Z",
  "message_id": "unique-message-id"
}
```

**WhatsApp Business API Setup**:
1. WhatsApp Business API Account
2. Configure Webhook URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-whatsapp`
3. Subscribe to: messages.received

**Alternativ via Zapier**:
1. Trigger: Webhook by Zapier → Catch Hook
2. Connect WhatsApp Business
3. Action: Forward to Railway Production URL

---

## 🔑 Authentication (Optional)

Aktuell: **Keine Authentication** (öffentliche Webhooks)

**Empfohlen für Production**:
```bash
# Option 1: API Key in Header
curl -H "X-API-Key: your-secret-key" \
     -X POST https://...

# Option 2: Bearer Token
curl -H "Authorization: Bearer your-token" \
     -X POST https://...

# Option 3: Signature Verification
# HMAC-SHA256 signature in Header
```

---

## 📊 Response Format

**Erfolgreiche Response** (200 OK):
```json
{
  "ai_processing": {
    "success": true,
    "workflow_path": "WEG_A",
    "contact_match": {
      "found": false,
      "contact_id": null
    },
    "ai_analysis": {
      "intent": "sales",
      "urgency": "medium",
      "sentiment": "neutral",
      "key_topics": ["Topic1", "Topic2"]
    },
    "tasks_generated": [
      {
        "title": "Task Title",
        "description": "Task Description",
        "priority": "medium",
        "due_date": "2025-10-12T14:00:00"
      }
    ],
    "processing_complete": true,
    "notification_sent": true
  }
}
```

**Error Response** (500):
```json
{
  "detail": "Internal server error"
}
```

---

## 🧪 Test Zapier Integration

### Test Email Zap:
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test@example.com",
    "sender_name": "Test User",
    "subject": "Test Email from Zapier",
    "body": "This is a test email to verify Zapier integration.",
    "received_at": "2025-10-11T15:00:00Z"
  }'
```

### Test Call Zap:
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-call \
  -H "Content-Type: application/json" \
  -d '{
    "event": "newCall",
    "from": "+4915112345678",
    "to": "+49301234567",
    "timestamp": "2025-10-11T15:00:00Z"
  }'
```

---

## 🔧 Zapier Zap Templates

### Template 1: Gmail → AI Email Processing
**Name**: "AI Email Processor - Production"

**Trigger**: Gmail - New Email  
**Filter**: (Optional) Only Business Hours  
**Action**: Webhooks by Zapier - Custom Request

**Settings**:
- URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-email`
- Method: POST
- Data Pass-Through: No
- Unflatten: No
- Wrap Request in Array: No

**Data Mapping**:
| Zapier Field | Railway Field | Value |
|--------------|---------------|-------|
| sender | sender | {{From Email}} |
| sender_name | sender_name | {{From Name}} |
| subject | subject | {{Subject}} |
| body | body | {{Body Plain}} |
| received_at | received_at | {{Received Time}} |

---

### Template 2: Sipgate → AI Call Processing
**Name**: "AI Call Handler - Production"

**Setup in Sipgate**:
1. Go to: https://app.sipgate.com/
2. Settings → API & Webhooks
3. Create New Webhook
4. URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`
5. Events: New Call, Answer, Hangup

**Sipgate sends automatically**:
- event: newCall/answer/hangUp
- from: caller number
- to: called number
- callId: unique ID
- timestamp: ISO format

---

### Template 3: WhatsApp → AI Message Processing
**Name**: "AI WhatsApp Handler - Production"

**Requires**: WhatsApp Business API Access

**Setup**:
1. WhatsApp Business Platform → Configuration
2. Webhook URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-whatsapp`
3. Verify Token: (Optional, not implemented yet)
4. Subscription Fields: messages

---

## 📝 Schritt-für-Schritt Anleitung

### Email Integration (Gmail/Outlook):

1. **Login to Zapier**: https://zapier.com/
2. **Create New Zap**: Click "Create Zap"
3. **Choose Trigger**:
   - App: Gmail / Outlook
   - Event: New Email
   - Connect Account: Authorize Gmail/Outlook
4. **Set Filter** (Optional):
   - Only continue if: Label is "To Process"
   - Or: From contains specific domain
5. **Add Action**:
   - App: Webhooks by Zapier
   - Event: Custom Request
6. **Configure Webhook**:
   - Method: POST
   - URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-email`
   - Data: (See Data Mapping above)
7. **Test Zap**: Send test email
8. **Turn On Zap**: Activate

---

### Sipgate Integration (Direct):

1. **Login to Sipgate**: https://app.sipgate.com/
2. **Navigate**: Settings → Webhooks → Create New
3. **Configure**:
   - Name: "AI Call Handler Production"
   - URL: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`
   - Method: POST
   - Events: ✅ newCall, ✅ answer, ✅ hangUp
4. **Save**: Webhook is active immediately
5. **Test**: Make a test call

---

## 🚨 Troubleshooting

### Problem: Zapier says "Request failed with status code 500"
**Solution**: 
- Check Railway logs: `railway logs --lines 50`
- Verify JSON payload is correct
- Check if all required fields are present

### Problem: No response from webhook
**Solution**:
- Verify URL is correct (https, no typos)
- Check Railway deployment status
- Test with curl first

### Problem: AI Analysis fails
**Solution**:
- Check OpenAI API key in Railway variables
- Verify OpenAI account has credits
- Check Railway logs for specific error

---

## 📊 Monitoring Zapier Integrations

**In Zapier**:
- Zap History: See all runs
- Task History: See specific executions
- Errors: Get alerts for failed zaps

**In Railway**:
- Logs: `railway logs`
- Metrics: Railway Dashboard
- Alerts: Setup in Railway settings

---

## 🎯 Next Steps

1. ✅ Create Gmail → AI Email Zap
2. ✅ Setup Sipgate Webhook
3. ✅ Configure WhatsApp (if available)
4. ✅ Test all integrations
5. ✅ Monitor for 24h
6. ✅ Enable in production

---

## 📞 Support

**Railway URL**: https://my-langgraph-agent-production.up.railway.app  
**Status Endpoint**: https://my-langgraph-agent-production.up.railway.app/status  
**Railway Dashboard**: https://railway.app/project/03611984-78a4-458b-bd84-895906a2b149

**Bei Problemen**:
1. Check Railway Logs
2. Test with curl
3. Verify Zapier payload
4. Check API quotas (OpenAI, WeClapp, Apify)
