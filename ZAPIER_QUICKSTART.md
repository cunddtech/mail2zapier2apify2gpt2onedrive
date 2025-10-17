# 🚀 ZAPIER ZAPS ERSTELLEN - SCHNELLANLEITUNG

## ✅ Railway ist ONLINE!

**Railway URL:** https://my-langgraph-agent-production.up.railway.app  
**Status:** ✅ ONLINE  
**Webhook Endpoint:** `/api/v1/process-email`

---

## 📧 Zap 1: Eingehende Mails (9 Minuten)

### Schritt-für-Schritt:

1. **Zapier öffnen:** https://zapier.com/app/zaps
2. **"Create Zap"** klicken

### TRIGGER:

3. **App:** Microsoft Outlook (oder Office 365 Mail)
4. **Event:** "New Email"
5. **Account:** `mj@cdtechnologies.de` verbinden
6. **Folder:** "Inbox" (Posteingang)
7. **Include Attachments:** YES ✅
8. **Test Trigger:** Letzte Email laden

### FILTER:

9. **Click:** + → Filter
10. **Condition:** 
    - Field: "Has Attachments" (Boolean)
    - Condition: "Equals"
    - Value: `true`

### ACTION (Webhook):

11. **App:** Webhooks by Zapier
12. **Event:** POST
13. **URL:** 
```
https://my-langgraph-agent-production.up.railway.app/api/v1/process-email
```

14. **Payload Type:** `json`

15. **Data (JSON):**
```json
{
  "email_id": "{{1__id}}",
  "message_id": "{{1__internetMessageId}}",
  "from": "{{1__from}}",
  "to": "{{1__to}}",
  "subject": "{{1__subject}}",
  "body": "{{1__bodyPreview}}",
  "body_type": "html",
  "received_date": "{{1__receivedDateTime}}",
  "has_attachments": true,
  "attachments": "{{1__attachments}}",
  "email_direction": "incoming",
  "document_type_hint": "",
  "priority": "normal"
}
```

16. **Headers:**
```
Content-Type: application/json
```

17. **Test Action:** Sollte Response 200 bekommen

18. **Zap benennen:** "📧 Eingehende Mails → Railway"

19. **Zap aktivieren:** Toggle ON

---

## 📤 Zap 2: Ausgehende Mails (9 Minuten)

### Schritt-für-Schritt:

1-8. **GLEICH wie Zap 1**, ABER:
   - **Folder:** "Sent Items" (Gesendete Elemente)

### ACTION (Webhook):

**URL:** (gleich wie Zap 1)
```
https://my-langgraph-agent-production.up.railway.app/api/v1/process-email
```

**Data (JSON):** (NUR `email_direction` ANDERS!)
```json
{
  "email_id": "{{1__id}}",
  "message_id": "{{1__internetMessageId}}",
  "from": "{{1__from}}",
  "to": "{{1__to}}",
  "subject": "{{1__subject}}",
  "body": "{{1__bodyPreview}}",
  "body_type": "html",
  "received_date": "{{1__sentDateTime}}",
  "has_attachments": true,
  "attachments": "{{1__attachments}}",
  "email_direction": "outgoing",
  "document_type_hint": "",
  "priority": "normal"
}
```

**Zap benennen:** "📤 Ausgehende Mails → Railway"

**Zap aktivieren:** Toggle ON

---

## ✅ Fertig!

**Total Zeit:** ~20 Minuten (2 Zaps × 9 Min)

### Nächster Schritt: Testing

Siehe: `TESTING.md` für 9 Test-Szenarien

### Test 1: Eingehende Rechnung

```
1. Sende Email an mj@cdtechnologies.de mit PDF-Rechnung
2. Check Railway Logs: railway logs --tail 50
3. Check OneDrive: Scan/Buchhaltung/2025/10/Eingang/{Lieferant}/
```

---

## 🔍 Monitoring

### Railway Logs live:
```bash
railway logs --tail 100
```

### Zapier Dashboard:
https://zapier.com/app/history

**Success:** Grünes ✅  
**Filtered:** Gelbes ⚠️ (kein Attachment - OK)  
**Error:** Rotes ❌ (Railway Logs checken)

---

## 🚨 Quick Troubleshooting

**Zap triggert nicht?**
- Check: Email Account Verbindung
- Check: Folder Name (Inbox vs. Posteingang)
- Test mit Email MIT Attachment

**Railway gibt 500?**
```bash
railway logs --tail 100
```
- Check: Alle Environment Variables gesetzt
- Check: OpenAI API Key, MS Graph API Credentials

**OneDrive Upload scheitert?**
- Check Railway Env Vars:
  - MS_CLIENT_ID
  - MS_CLIENT_SECRET
  - MS_TENANT_ID

---

## 📊 Erwartete Logs (Erfolg):

```
✅ Email processing complete: WEG_B
📁 Ordnerstruktur generiert: Scan/Buchhaltung/2025/10/Eingang/MusterGmbH
☁️ Upload erfolgreich: https://1drv.ms/...
💾 Email saved to tracking DB with ID: 123
```

---

**Los geht's!** 🚀
