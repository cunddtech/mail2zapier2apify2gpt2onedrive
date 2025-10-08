# 🚀 Enhanced Email Actor v3.4.1 - Webhook Extension

**Minimale SipGate/WhatsApp Webhook-Erweiterung für bestehendes v3.4 System**  
**Nutzt bestehende WeClapp Integration und Datenbank - Apify Compatible**

[![Version](https://img.shields.io/badge/version-3.4.1-blue.svg)](https://github.com/cunddtech/my-langgraph-agent)
[![Railway](https://img.shields.io/badge/Railway-LangGraph-success.svg)](https://my-langgraph-agent-production.up.railway.app)
[![Apify](https://img.shields.io/badge/Apify-Compatible-orange.svg)](https://console.apify.com/actors/cdtech~mail2zapier2apify2gpt2onedrive)
[![Webhook](https://img.shields.io/badge/Webhook-Extension-purple.svg)](https://github.com/cunddtech/my-langgraph-agent)

## 🎯 Überblick

Der Enhanced Email Actor v3.4.1 ist eine **minimale Webhook-Erweiterung** des bestehenden v3.4 Systems. Anstatt ein komplett neues Multi-Channel System zu entwickeln, erweitert diese Version nur die **Webhook-Unterstützung** für SipGate Calls und WhatsApp Messages, während alle **bestehenden Integrations** (WeClapp, Datenbank, v3.4 Pipeline) **unverändert** beibehalten werden.

### ✨ Minimale Erweiterungen

- **📞 SipGate Call Webhook Support** - Automatische Transformation zu Email-Format
- **💬 WhatsApp Message Webhook Support** - Seamless Integration in v3.4 Pipeline  
- **🔍 Smart Webhook Detection** - Automatische Erkennung der Webhook-Quelle
- **🔄 Format Transformation** - Konvertiert Webhook-Daten zu Email-Format
- **✅ Bestehende Integration** - Nutzt WeClapp, Datenbank, Railway AI ohne Änderungen
- **⚡ Minimal Footprint** - Nur 150 Zeilen zusätzlicher Code

## 🔗 Webhook Integration Flow

```
📞 SipGate Call Webhook ──┐
💬 WhatsApp Message ──────┼──► 🔍 Webhook Detection
📧 Standard Email ────────┘              ↓
                                🔄 Transform zu Email-Format
                                         ↓
                               🚀 Bestehende v3.4 Pipeline
                                         ↓ 
                        🤖 Railway AI + WeClapp + Database (unverändert)
```

## 📞 SipGate Webhook Support

### 🎯 Unterstützte SipGate Events

- `newCall` - Eingehender Anruf
- `answer` - Anruf angenommen  
- `hangup` - Anruf beendet
- `dtmf` - Tasteneingabe

### 📊 SipGate Webhook Input Beispiel

```json
{
  "callId": "sipgate-call-123",
  "event": "hangup",
  "from": "+49 30 12345678",
  "to": "+49 30 87654321",
  "user": "info@cdtech.de",
  "duration": 142,
  "answered": true,
  "transcription": "Kunde möchte Angebot für Website-Entwicklung"
}
```

### 🔄 Automatische Transformation

**SipGate Webhook wird automatisch transformiert zu:**

```json
{
  "message_id": "sipgate-call-123",
  "subject": "SipGate Call Hangup: +49 30 12345678", 
  "body_content": "SipGate Call Event: hangup\\nVon: +49 30 12345678\\nCall Transcript:\\nKunde möchte Angebot für Website-Entwicklung",
  "from_email_address_address": "+49 30 12345678",
  "from_email_address_name": "Caller +49 30 12345678",
  "source": "sipgate_webhook",
  "railway_integration": true
}
```

**➡️ Läuft durch bestehende v3.4 Pipeline mit Railway `/webhook/ai-call` Endpoint**

## 💬 WhatsApp Webhook Support

### 🎯 Unterstützte WhatsApp Message Types

- `text` - Text-Nachrichten
- `image` - Bild-Nachrichten  
- `document` - Dokument-Anhänge
- `audio` - Sprachnachrichten
- `video` - Video-Nachrichten

### 📊 WhatsApp Webhook Input Beispiel

```json
{
  "message_type": "text",
  "sender_phone": "+49 175 9876543",
  "sender_name": "Anna Müller", 
  "message_text": "Hallo! Ich brauche ein Angebot für Website-Entwicklung.",
  "chat_id": "wa-chat-business-001",
  "is_group": false
}
```

### 🔄 Automatische Transformation

**WhatsApp Webhook wird automatisch transformiert zu:**

```json
{
  "message_id": "whatsapp-wa-chat-business-001",
  "subject": "WhatsApp Text: Anna Müller",
  "body_content": "WhatsApp Message von Anna Müller (+49 175 9876543)\\n\\nHallo! Ich brauche ein Angebot für Website-Entwicklung.",
  "from_email_address_address": "+49 175 9876543", 
  "from_email_address_name": "Anna Müller",
  "source": "whatsapp_webhook",
  "railway_integration": true
}
```

**➡️ Läuft durch bestehende v3.4 Pipeline mit Railway `/webhook/ai-whatsapp` Endpoint**

## 🔧 Konfiguration

### 🔐 Environment Variables (Unverändert)

```bash
# Railway Integration (wie v3.4)
ORCHESTRATOR_URL=https://my-langgraph-agent-production.up.railway.app
RAILWAY_INTEGRATION=true

# System Settings (wie v3.4)
DEBUG=false
```

### 📥 Input Schema - Webhook Extension

**Standard Email Input (wie v3.4):**
```json
{
  "body_content": "E-Mail-Inhalt",
  "subject": "E-Mail-Betreff", 
  "from_email_address_address": "absender@example.com"
}
```

**SipGate Webhook Input (NEU):**
```json
{
  "callId": "sipgate-call-id",
  "event": "newCall|answer|hangup|dtmf",
  "from": "+49 30 12345678",
  "to": "+49 30 87654321",
  "transcription": "Call transcript here"
}
```

**WhatsApp Webhook Input (NEU):**
```json
{
  "message_type": "text|image|document|audio|video",
  "sender_phone": "+49 175 9876543",
  "sender_name": "Contact Name",
  "message_text": "WhatsApp message content"
}
```

## 🚀 Deployment zu Apify

### 📦 Minimale Apify Console Änderungen

**1. Actor Console öffnen:**
```
https://console.apify.com/actors/cdtech~mail2zapier2apify2gpt2onedrive
```

**2. Version 3.4.1 Webhook Extension erstellen:**
- Versions Tab → Create version  
- Version number: `3.4.1`
- Build tag: `3.4.1-webhook-extension`
- Source type: Source files

**3. Minimale Files Upload:**
```
main_v341.py → main.py
input_schema_v341.json → INPUT_SCHEMA.json
package_v341.json → package.json  
README_v341.md → README.md
```

**4. Environment Variables (Unverändert):**
```
ORCHESTRATOR_URL = https://my-langgraph-agent-production.up.railway.app
RAILWAY_INTEGRATION = true
DEBUG = false
```

**5. Build & Deploy:**
```bash
# Deploy Webhook Extension
apify push

# Test SipGate Webhook
apify call cdtech~mail2zapier2apify2gpt2onedrive --input '{
  "callId": "test-call-001",
  "event": "hangup",
  "from": "+49 30 12345678",
  "transcription": "Test call transcript"
}'

# Test WhatsApp Webhook  
apify call cdtech~mail2zapier2apify2gpt2onedrive --input '{
  "message_type": "text",
  "sender_phone": "+49 175 9876543",
  "sender_name": "Test User",
  "message_text": "Test WhatsApp message"
}'
```

## 🧪 Webhook Testing

### 📞 SipGate Call Test
```json
{
  "callId": "test-sipgate-001",
  "event": "hangup",
  "from": "+49 30 12345678",
  "to": "+49 30 87654321", 
  "duration": 125,
  "answered": true,
  "transcription": "Kunde ruft wegen Website-Projekt an"
}
```

### 💬 WhatsApp Message Test
```json
{
  "message_type": "document",
  "sender_phone": "+49 175 1234567",
  "sender_name": "Business Customer",
  "message_text": "Hier ist das Projektdokument",
  "media_url": "https://wa.me/document.pdf"
}
```

### ✅ Success Criteria

**Build Success:**
- ✅ Build Status = SUCCEEDED (minimale Dependencies)
- ✅ Webhook Extension Tests erfolgreich
- ✅ v3.4 Pipeline funktional
- ✅ Bestehende WeClapp/Database Integration unverändert

**Runtime Success:**  
- ✅ SipGate Webhooks automatisch zu Email transformiert
- ✅ WhatsApp Webhooks automatisch zu Email transformiert
- ✅ Railway AI verwendet richtige Endpoints (`/webhook/ai-call`, `/webhook/ai-whatsapp`)
- ✅ WeClapp Contact Matching funktional
- ✅ Bestehende Datenbank Integration funktional
- ✅ Backward compatibility mit allen v3.4 Features

## 🔮 Next Steps

### 🎯 Immediate (Post v3.4.1 Deployment):

1. **SipGate Webhook Konfiguration** - Webhook URL zu Apify Actor
2. **WhatsApp Business API Setup** - Webhook URL zu Apify Actor  
3. **Testing mit realen Daten** - SipGate/WhatsApp Integration
4. **Monitoring & Analytics** - Webhook Performance Tracking

### 🚀 Future Enhancements (Optional):

- **Enhanced Call Analytics** - Call Duration, Sentiment Analysis
- **WhatsApp Media Processing** - Advanced Image/Document Analysis
- **Cross-Channel Contact Matching** - Phone ↔ Email ↔ WhatsApp Linking
- **Unified Dashboard** - Multi-Channel Communication Overview

## ✅ Bestehende Integration Preservation

### 💾 WeClapp CRM Integration
- **✅ Unverändert** - Alle WeClapp Lookups funktionieren
- **✅ Contact Matching** - Phone/Email Cross-Reference  
- **✅ Opportunity Tracking** - Bestehende CRM Workflows

### 🗄️ Datenbank Integration
- **✅ Unverändert** - Alle Database Inserts funktionieren
- **✅ Webhook Source Tracking** - Zusätzliche Source-Info
- **✅ Bestehende Schemas** - Keine Breaking Changes

### 🤖 Railway LangGraph AI
- **✅ Enhanced** - Neue Endpoints für SipGate/WhatsApp
- **✅ Backward Compatible** - Alle v3.4 AI Features erhalten
- **✅ Smart Routing** - Automatische Endpoint-Auswahl

## 🆘 Support & Backup

### 💡 Ultra-Safe Fallback Plan

- **✅ v3.4 Compatibility** - Falls Webhook Extension Probleme macht
- **✅ Graceful Degradation** - Automatic Fallback zu Standard Email Processing
- **✅ Bestehende Integrations** - WeClapp/Database bleiben funktional
- **✅ Zero Downtime** - Hot-swap zwischen v3.4.1 und v3.4

### 📞 Support Kontakt

- **Repository:** https://github.com/cunddtech/my-langgraph-agent  
- **Railway Dashboard:** https://railway.app/project/my-langgraph-agent
- **Apify Console:** https://console.apify.com/actors/cdtech~mail2zapier2apify2gpt2onedrive

---

**🎯 Ready for Deployment: Enhanced Email Actor v3.4.1 Webhook Extension - Minimale Erweiterung, maximale Kompatibilität!**