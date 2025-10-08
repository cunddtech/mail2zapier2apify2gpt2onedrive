# 🔧 **SETUP INSTRUCTIONS**

## 📝 **Configuration Files Setup**

Diese Files sind von Git ausgeschlossen (.gitignore) und müssen manuell konfiguriert werden:

### **1. input.json** 
Beispiel-Struktur (mit echten Daten füllen):
```json
{
  "message_id": "test-message-id",
  "body_content": "Email body content here",
  "subject": "Test Subject",
  "from_email_address_address": "sender@example.com",
  "trigger": "webhook",
  "source": "mail",
  "url": "https://api.apify.com/v2/acts/cdtech~mail2zapier2apify2gpt2onedrive/runs?token=YOUR_APIFY_TOKEN_HERE"
}
```

### **2. input_schema.json**
Apify Input Schema mit Platzhaltern für API URLs:
```json
{
  "title": "URL Configuration",
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "title": "Apify Actor URL",
      "default": "https://api.apify.com/v2/acts/cdtech~mail2zapier2apify2gpt2onedrive/runs?token=YOUR_APIFY_TOKEN_HERE"
    }
  }
}
```

### **3. .actor/actor.json**
Actor Configuration (bereits in .gitignore):
```json
{
  "actorSpecification": 1,
  "name": "mail2zapier2apify2gpt2onedrive",
  "environmentVariables": {
    "APIFY_TOKEN": "YOUR_APIFY_TOKEN_HERE",
    "OPENAI_API_KEY": "YOUR_OPENAI_KEY_HERE",
    "GRAPH_CLIENT_SECRET_MAIL": "YOUR_GRAPH_SECRET_HERE"
  }
}
```

## 🔑 **Required API Keys**
- `APIFY_TOKEN`: Apify API Token  
- `OPENAI_API_KEY`: OpenAI GPT-4 API Key
- `GRAPH_CLIENT_SECRET_MAIL`: Microsoft Graph API Secret
- `GRAPH_CLIENT_SECRET_ONEDRIVE`: OneDrive Graph Secret
- `PDFCO_API_KEY`: PDF.co OCR API Key
- `WECLAPP_API_TOKEN`: WeClapp CRM API Token

## ⚠️ **SECURITY NOTICE**
Diese Konfiguration-Files enthalten sensible API Keys und dürfen **NIEMALS** in Git committed werden!