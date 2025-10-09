# 🎯 WEBHOOK KONFIGURATION - FINAL SETUP

## ✅ EINE APP FÜR ALLE KANÄLE

Die **cdtech~mail2zapier2apify2gpt2onedrive** App kann bereits ALLE drei Kanäle verarbeiten:

### 📧 EMAIL WEBHOOKS
```
Webhook URL: https://api.apify.com/v2/acts/cdtech~mail2zapier2apify2gpt2onedrive/runs?token=YOUR_TOKEN
```

### 📞 SIPGATE WEBHOOKS  
```
Webhook URL: https://api.apify.com/v2/acts/cdtech~mail2zapier2apify2gpt2onedrive/runs?token=YOUR_TOKEN
Input: SipGate Call Data → Automatisch erkannt → /webhook/ai-call
```

### 💬 WHATSAPP WEBHOOKS
```
Webhook URL: https://api.apify.com/v2/acts/cdtech~mail2zapier2apify2gpt2onedrive/runs?token=YOUR_TOKEN  
Input: WhatsApp Message Data → Automatisch erkannt → /webhook/ai-whatsapp
```

## 🔄 WIE ES FUNKTIONIERT

1. **Webhook erhält Daten** (Email/SipGate/WhatsApp)
2. **detect_lead_source()** erkennt automatisch die Quelle
3. **prepare_orchestrator_payload()** bereitet Daten für Railway vor
4. **send_to_orchestrator()** sendet an korrekten Endpoint:
   - Email → `/webhook/ai-email` 
   - SipGate → `/webhook/ai-call`
   - WhatsApp → `/webhook/ai-whatsapp`
5. **Railway Orchestrator** verarbeitet und sendet CRM-Aktionen zurück

## 🎉 SETUP KOMPLETT!

Keine separaten Apps nötig - die Email App ist bereits ein Universal Multi-Channel Processor!