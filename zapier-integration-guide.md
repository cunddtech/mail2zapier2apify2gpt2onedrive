# Zapier Integration Setup Guide

## 🔑 Welche Keys brauchen wir?

### ✅ Deploy Key (für Custom Integration)
**Zweck**: SipGate/WhatsApp als neue Zapier Triggers erstellen
**Steps**:
1. Gehe zu: https://developer.zapier.com/
2. "Start a New Integration" → Sign in
3. Erstelle neue Integration: "SipGate Lead Capture"
4. Deploy Key wird generiert

### ✅ Platform API Key (für Automation)  
**Zweck**: Zaps automatisch erstellen und verwalten
**Steps**:
1. Gehe zu: https://zapier.com/app/developer
2. "Manage my Apps" → API Keys
3. "Create API Key" 
4. Für REST Client nutzen

## 🚀 Quick Start - Welchen Ansatz?

### Option A: **Webhook-basiert (einfacher)**
- SipGate → Webhook → ngrok → Apify
- WhatsApp → Webhook → ngrok → Apify  
- **Vorteil**: Schnell, keine Custom Integration nötig
- **Nachteil**: Technischer für Enduser

### Option B: **Custom Zapier Integration (professioneller)**
- Eigene SipGate/WhatsApp Triggers in Zapier
- **Vorteil**: User-friendly, Zapier Marketplace
- **Nachteil**: Mehr Setup, Deploy Key nötig

## 🎯 Empfehlung: **Start mit Option A!**

**Deine ngrok URL ist bereits bereit:**
```
https://nonequivocating-subsimian-hermina.ngrok-free.dev
```

**Soll ich dir zeigen wie du:**
1. **Webhook in Zapier konfigurierst** (5 Min Setup)
2. **Oder Custom Integration erstellst** (30 Min Setup)

**Was bevorzugst du?** 🤔