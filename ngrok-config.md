# ngrok Configuration Steps

## 🔑 Authtoken Setup:

1. **Hol dir deinen Authtoken:** https://dashboard.ngrok.com/get-started/your-authtoken
2. **Führe aus:** `ngrok config add-authtoken YOUR_ACTUAL_TOKEN_HERE`

## ✅ Nach Token Setup:

```bash
# Test ngrok installation
ngrok version

# Start tunnel für Port 3000 (Standard für Express Server)
ngrok http 3000
```

## 🎯 Nächster Schritt:
Nach dem Authtoken Setup erstellen wir den lokalen Test-Server!

---

**Sobald du den Authtoken eingegeben hast, sag Bescheid!** 
Dann geht's weiter mit dem Express Server für SipGate/WhatsApp Webhook Testing! 🚀