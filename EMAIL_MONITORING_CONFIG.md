# 📧 Email-Überwachung Konfiguration - Complete Overview

## 🎯 **Aktuell überwachte Email-Adressen:**

### **📥 Haupt-Email (empfängt Leads):**
```
EMAIL_RECEIVER=info@cdtechnologies.de
```

### **📤 Sender-Email (für Benachrichtigungen):**
```
EMAIL_SENDER=mj@cdtechnologies.de
```

## 🔧 **Wo wird was konfiguriert:**

### **1. 🔑 Microsoft Graph API Konfiguration (.env):**
```env
GRAPH_TENANT_ID_MAIL=your_tenant_id_here
GRAPH_CLIENT_ID_MAIL=your_client_id_here
GRAPH_CLIENT_SECRET_MAIL=your_client_secret_here
EMAIL_RECEIVER=info@cdtechnologies.de
EMAIL_SENDER=mj@cdtechnologies.de
```

### **2. 🎯 Zapier Webhook Integration:**
```
Zapier URL: https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/
```

### **3. 🚀 Railway Orchestrator:**
```
Railway URL: https://my-langgraph-agent-production.up.railway.app/webhook/ai-email
```

## 📋 **Email Processing Flow:**

```
1. Email → info@cdtechnologies.de (Outlook)
2. Zapier → Erkennt neue Email
3. Zapier → Sendet an Railway Orchestrator
4. Railway → AI Processing (GPT + CRM)
5. Railway → Generiert Tasks & Leads
```

## 🎛️ **Konfiguration ändern:**

### **Neue Email-Adresse hinzufügen:**
1. **In .env Datei:** EMAIL_RECEIVER=neue@email.de
2. **Microsoft Graph:** App Registration erweitern
3. **Zapier:** Neuen Trigger für neue Email einrichten
4. **Deploy:** apify push

### **Mehrere Email-Adressen überwachen:**
```env
# Mehrere Empfänger (comma-separated)
EMAIL_RECEIVERS=info@cdtechnologies.de,sales@cdtechnologies.de,support@cdtechnologies.de
```

## 📊 **Aktueller Status:**

- ✅ **info@cdtechnologies.de**: Überwacht & Aktiv (412+ Runs)
- ✅ **SPAM Filter**: GPT-basiert aktiv
- ✅ **Multi-Channel**: Email + SipGate + WhatsApp
- ✅ **CRM Integration**: WeClapp automatisch

## ❓ **Was möchtest du ändern?**

1. **Neue Email-Adresse** hinzufügen?
2. **Bestehende Adresse** ändern?
3. **Mehrere Adressen** gleichzeitig überwachen?
4. **Filter-Regeln** anpassen?

**Sag mir, was du brauchst!** 😊