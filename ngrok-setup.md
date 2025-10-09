# ngrok Configuration für Zapier Webhook Testing
# Lokale Development mit Zapier verbinden

## 🎯 Setup Steps:

### 1. ngrok Account Setup
# Gehe zu: https://dashboard.ngrok.com/signup
# Hol dir deinen Authtoken: https://dashboard.ngrok.com/get-started/your-authtoken

### 2. VS Code Command Palette
# Cmd+Shift+P → "ngrok: set authtoken"
# Füge deinen ngrok authtoken ein

### 3. Lokaler Development Server
# Starte deinen lokalen Server auf einem Port (z.B. 3000, 8000, 5000)

### 4. ngrok Tunnel starten
# Cmd+Shift+P → "ngrok: start tunnel"
# Wähle deinen Port (z.B. 3000)
# ngrok generiert öffentliche URL: https://abc123.ngrok.io

### 5. Zapier Webhook konfigurieren
# In Zapier: Webhook by Zapier → POST Request
# URL: https://abc123.ngrok.io/webhook/sipgate
# Diese URL leitet an localhost:3000/webhook/sipgate weiter

## 🔄 Development Workflow:

1. **Code ändern** → automatisch neu geladen
2. **Zapier testet** → sendet an ngrok URL
3. **ngrok leitet weiter** → an localhost
4. **Du siehst sofort** → Ergebnisse in VS Code

## 🎯 Für SipGate/WhatsApp:

### SipGate Webhook Test:
```bash
# Lokaler Test-Server
curl -X POST http://localhost:3000/webhook/sipgate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+49123456789",
    "to": "+49987654321",
    "direction": "incoming"
  }'
```

### WhatsApp Webhook Test:
```bash
# Lokaler Test-Server  
curl -X POST http://localhost:3000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+49123456789",
    "message": "Hallo, ich interessiere mich für...",
    "timestamp": "2025-10-09T10:00:00Z"
  }'
```

## 🔍 ngrok Web Interface:
# http://localhost:4040
# Zeigt alle Requests in Echtzeit!

## 🛠️ Alternative: LocalTunnel
# Falls ngrok Probleme macht:
# npm install -g localtunnel
# lt --port 3000 --subdomain myapp