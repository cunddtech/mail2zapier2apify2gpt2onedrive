# 🚀 ZAPIER RAILWAY AI INTEGRATION - SETUP GUIDE

## 📋 **Schnell-Setup für Railway AI Notifications**

### **🎯 Was diese Zap macht:**
- ✅ Empfängt Railway AI Webhook Daten
- ✅ Sendet formatierte Email-Benachrichtigungen  
- ✅ Funktioniert für ALLE Kanäle (Email, SipGate, WhatsApp)
- ✅ Schöne HTML + Plain Text Emails
- ✅ Vollständige Task und Contact Info

---

## 🔧 **Setup Optionen:**

### **Option A: Neue Zap erstellen** ⚡

1. **Zapier.com** → Create Zap
2. **Trigger:** Webhooks by Zapier → Catch Hook
3. **Webhook URL:** `https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/`
4. **Action:** Email by Zapier → Send Outbound Email
5. **Configuration:** Verwende `ZAPIER_RAILWAY_AI_ZAP_CONFIG.json`

### **Option B: Bestehende Zap erweitern** 🔄

1. Öffne: **"MAIL Scan Analyse von ChatGPT (Apify-PDFCO) zurück"**
2. **Add Step:** Webhooks → Catch Hook  
3. **Webhook URL:** `https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/`
4. **Add Action:** Email → Send Email (Railway Format)

---

## 📧 **Email Template (Copy & Paste):**

### **Subject:**
```
🤖 C&D AI: {{channel}} von {{from}} - {{summary}}
```

### **Email Body (HTML):**
```html
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
.header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
.content { padding: 20px; background: #f8f9fa; }
.status { padding: 10px; margin: 10px 0; border-radius: 5px; }
.success { background: #d4edda; border-left: 4px solid #28a745; }
.warning { background: #fff3cd; border-left: 4px solid #ffc107; }
.info { background: #e7f3ff; border-left: 4px solid #007bff; }
.details { background: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 5px; margin: 10px 0; }
</style>
</head>
<body>

<div class="header">
  <h1>🤖 C&D Technologies AI System</h1>
  <h2>{{channel}} Processing Complete</h2>
</div>

<div class="content">
  
  <div class="status success">
    <strong>Status:</strong> ✅ Erfolgreich verarbeitet
  </div>
  
  <div class="info">
    <h3>📞 Kontakt Details</h3>
    <strong>Von:</strong> {{from}}<br>
    <strong>Kanal:</strong> {{channel}}<br>
    <strong>Zeitstempel:</strong> {{timestamp}}<br>
    <strong>Workflow:</strong> {{workflow_path}}
  </div>
  
  <div class="details">
    <h3>💬 Nachricht</h3>
    <p>{{content_preview}}</p>
  </div>
  
  <div class="details">
    <h3>🎯 AI Analysis</h3>
    <strong>Contact Match:</strong> {{contact_match}}<br>
    <strong>Processing Complete:</strong> {{processing_complete}}<br>
  </div>
  
  <div class="details">
    <h3>📋 Generierte Tasks</h3>
    {{tasks_generated}}
  </div>
  
  <div class="info">
    <p><strong>🔗 System URLs:</strong><br>
    Railway Orchestrator: https://my-langgraph-agent-production.up.railway.app<br>
    WeClapp CRM: https://cdtech.weclapp.com</p>
  </div>
  
</div>

</body>
</html>
```

### **Email Recipients:**
```
mj@cdtechnologies.de, info@cdtechnologies.de
```

---

## 🧪 **Test nach Setup:**

1. **Zap aktivieren** (Status: ON)
2. **Test Webhook senden:**
```bash
curl -X POST "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/" \
-H "Content-Type: application/json" \
-d '{"test":"Zapier Setup Test","channel":"test","from":"setup@test.de","timestamp":"2025-10-09T18:00:00Z","summary":"Setup erfolgreich"}'
```

3. **Email sollte ankommen** bei mj@ und info@

---

## ✅ **Erfolgskriterien:**

- ✅ Zap Status: **ON/Activated**  
- ✅ Webhook URL korrekt: `17762912/2xh8rlk`
- ✅ Email Action konfiguriert
- ✅ Test Email empfangen
- ✅ Railway AI sendet `"notification_sent": true`

**Dann ist das komplette System LIVE! 🎉**