# 📞 SipGate Frontdesk Integration - Setup Guide

## 🔧 **SipGate Frontdesk Einstellungen**

### 1. **Webhook Configuration**
```
SipGate Account → Frontdesk → Webhooks
URL: https://my-langgraph-agent-production.up.railway.app/webhook/sipgate
Events: hangup, answered, dtmf
```

### 2. **Required SipGate Settings**
- ✅ **Transcription Service**: Aktiviert für automatische Gesprächstranskription
- ✅ **Webhook Events**: `hangup`, `answered`, `newCall`
- ✅ **Data Format**: JSON
- ✅ **Authentication**: Bearer Token oder API Key

### 3. **Frontdesk Display Integration**
Die generierten Conversation Prompts können auf zwei Wege angezeigt werden:

#### Option A: **Webhook zu Frontdesk-Display**
```javascript
// SipGate kann Custom Display Content empfangen
{
  "event": "answered",
  "callId": "123456",
  "display_prompts": [
    "🎯 BEKANNTER KONTAKT: Max Mustermann",
    "💬 Letzte Anfrage: Dachsanierung München", 
    "❓ Nachfragen: Kostenvoranschlag fertig?"
  ]
}
```

#### Option B: **Manual Dashboard Check**
Mitarbeiter öffnen parallel das Dashboard:
```
https://my-langgraph-agent-production.up.railway.app/dashboard/sales?token=cdtech2025
```

### 4. **API Integration Status**
Current webhook endpoint active:
- **URL**: `/webhook/sipgate` ✅ Live
- **Processing**: Automatic conversation prompt generation ✅
- **CRM Lookup**: WeClapp contact matching ✅
- **Display Push**: Needs SipGate Frontdesk API integration ⚠️

**Next Step**: SipGate Frontdesk API Documentation prüfen für Display-Push Integration