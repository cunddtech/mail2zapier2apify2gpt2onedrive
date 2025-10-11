# 🚀 RAILWAY AI ZAPIER SETUP - STEP BY STEP ANLEITUNG

## ✨ **Neue Zap für Railway AI erstellen (5 Minuten)**

### **🎯 Schritt 1: Neue Zap erstellen**
1. Gehe zu **zapier.com/app/zaps**
2. Klick **Create Zap**
3. Name: **"Railway AI → Email Notifications"**

---

### **📡 Schritt 2: Trigger konfigurieren**

1. **App wählen:** "Webhooks by Zapier"
2. **Event:** "Catch Hook"
3. **Webhook URL wird generiert:** 
   - ⚠️ **WICHTIG:** Die URL muss **exakt** sein: `https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/`
   - Falls die generierte URL anders ist → **Custom Webhook** verwenden

4. **Test Data eingeben:**
```json
{
  "timestamp": "2025-10-09T18:00:00Z",
  "channel": "call",
  "from": "+4928615551234",
  "content_preview": "Guten Tag, ich bin Klaus Müller. Wir haben ein Problem mit der Terrassenüberdachung...",
  "success": true,
  "workflow_path": "WEG_A",
  "contact_match": {
    "found": false,
    "contact_name": null,
    "company": null
  },
  "tasks_generated": [
    {
      "title": "Unbekannter Kontakt zuordnen: +4928615551234",
      "description": "Neue call von unbekanntem Kontakt. Entscheidung über CRM-Aufnahme erforderlich.",
      "assigned_to": "sales_team",
      "priority": "medium"
    }
  ],
  "processing_complete": true,
  "notification_sent": true,
  "subject": "🤖 C&D AI System: CALL von +4928615551234",
  "summary": "AI hat 1 Tasks erstellt"
}
```

---

### **📧 Schritt 3: Email Action konfigurieren**

1. **App wählen:** "Email by Zapier" 
2. **Event:** "Send Outbound Email"

3. **Email Configuration:**
   - **To:** `mj@cdtechnologies.de, info@cdtechnologies.de`
   - **Subject:** `🤖 C&D AI: {{channel}} von {{from}} - {{summary}}`

4. **Email Body (HTML):**
```html
<!DOCTYPE html>
<html>
<head>
<style>
body { 
  font-family: Arial, sans-serif; 
  line-height: 1.6; 
  color: #333; 
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.header { 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
  color: white; 
  padding: 30px; 
  text-align: center; 
  border-radius: 10px 10px 0 0;
}
.content { 
  padding: 30px; 
  background: #f8f9fa; 
  border-radius: 0 0 10px 10px;
}
.status-success { 
  background: #d4edda; 
  color: #155724;
  padding: 15px; 
  margin: 15px 0; 
  border-radius: 5px; 
  border-left: 4px solid #28a745;
}
.info-box { 
  background: #e3f2fd; 
  color: #0d47a1;
  padding: 20px; 
  border-radius: 8px; 
  margin: 15px 0;
  border-left: 4px solid #2196f3;
}
.task-box { 
  background: white; 
  padding: 20px; 
  border: 1px solid #ddd; 
  border-radius: 8px; 
  margin: 15px 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.contact-info {
  background: #fff3cd;
  color: #856404; 
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
  border-left: 4px solid #ffc107;
}
h1 { margin: 0; font-size: 24px; }
h2 { color: #333; margin-top: 0; }
h3 { color: #555; margin-bottom: 10px; }
.emoji { font-size: 18px; margin-right: 8px; }
</style>
</head>
<body>

<div class="header">
  <h1>🤖 C&D Technologies AI System</h1>
  <p style="font-size: 18px; margin: 10px 0 0 0;">{{channel}} erfolgreich verarbeitet</p>
</div>

<div class="content">
  
  <div class="status-success">
    <span class="emoji">✅</span><strong>Status:</strong> Erfolgreich verarbeitet | Workflow: {{workflow_path}}
  </div>
  
  <div class="info-box">
    <h3><span class="emoji">📞</span>Kontakt Details</h3>
    <strong>Von:</strong> {{from}}<br>
    <strong>Kanal:</strong> {{channel}}<br>
    <strong>Zeitstempel:</strong> {{timestamp}}<br>
  </div>
  
  <div class="task-box">
    <h3><span class="emoji">💬</span>Nachricht</h3>
    <p style="font-style: italic; background: #f1f3f4; padding: 15px; border-radius: 5px;">
      {{content_preview}}
    </p>
  </div>
  
  <div class="contact-info">
    <h3><span class="emoji">🎯</span>AI Analysis</h3>
    <strong>Contact Status:</strong> 
    {{#if contact_match.found}}
      ✅ Bekannter Kunde: {{contact_match.contact_name}}
      {{#if contact_match.company}}({{contact_match.company}}){{/if}}
    {{else}}
      🆕 Neuer Kontakt - Zuordnung erforderlich
    {{/if}}<br>
    <strong>Processing:</strong> {{#if processing_complete}}✅ Vollständig{{else}}⚠️ Teilweise{{/if}}
  </div>
  
  <div class="task-box">
    <h3><span class="emoji">📋</span>Generierte Tasks</h3>
    {{#each tasks_generated}}
    <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 3px solid #007bff;">
      <strong>{{title}}</strong><br>
      <em>{{description}}</em><br>
      <small style="color: #666;">
        👤 {{assigned_to}} | 🎯 {{priority}} | 📅 {{due_date}}
      </small>
    </div>
    {{/each}}
  </div>
  
  <div class="info-box">
    <h3><span class="emoji">🔗</span>System Links</h3>
    <p>
      <strong>Railway Orchestrator:</strong> <a href="https://my-langgraph-agent-production.up.railway.app">AI System</a><br>
      <strong>WeClapp CRM:</strong> <a href="https://cdtech.weclapp.com">CRM Dashboard</a><br>
      <strong>Notification Status:</strong> {{#if notification_sent}}✅ Gesendet{{else}}❌ Fehler{{/if}}
    </p>
  </div>
  
</div>

<div style="text-align: center; margin-top: 30px; color: #666; font-size: 14px;">
  <p>C&D Technologies GmbH - Intelligentes Lead Management System</p>
  <p>Powered by Railway AI + Zapier Integration</p>
</div>

</body>
</html>
```

---

### **🧪 Schritt 4: Test & Aktivierung**

1. **Test the Zap** klicken
2. **Zap aktivieren** (Status: ON)
3. **Test Webhook senden:**

```bash
curl -X POST "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/" \
-H "Content-Type: application/json" \
-d '{
  "test": "Zapier Setup Complete",
  "channel": "test",
  "from": "setup@cdtechnologies.de",
  "timestamp": "2025-10-09T18:30:00Z",
  "summary": "Zap Setup erfolgreich",
  "subject": "🎉 Railway AI Zap ist LIVE!"
}'
```

4. **Email sollte ankommen!**

---

## ✅ **Erfolgskontrolle:**

- ✅ Zap Status: **ON**
- ✅ Webhook URL: `17762912/2xh8rlk` 
- ✅ Email Action konfiguriert
- ✅ Test Email empfangen
- ✅ Railway sendet `"notification_sent": true`

**Dann funktioniert das komplette System! 🚀**

---

## 🔄 **Integration mit bestehender App:**

Die neue Zap läuft **parallel** zur bestehenden "MAIL Scan Analyse" App:
- **Alte App:** Apify Email Processing
- **Neue App:** Railway AI Notifications  
- **Beide Apps:** Ergänzen sich perfekt!

**Das ist die sauberste Lösung! 💪**