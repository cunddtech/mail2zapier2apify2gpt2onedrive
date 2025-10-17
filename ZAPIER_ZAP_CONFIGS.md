# 🚀 Zapier Zap Konfigurationen - Copy-Paste Ready

Komplette Konfigurationen für Zap 2, 3 und 4. Jedes Feld kann einzeln kopiert und in Zapier eingefügt werden.

---

## 📄 ZAP 2: LIEFERSCHEINE

### Zap Name
```
📄 Lieferscheine (Inbox → Railway)
```

### Trigger: Microsoft Outlook - New Email
- **Account:** mj@cdtechnologies.de
- **Folder:** Inbox

### Filter Conditions

**Subject contains (OR Logic):**
```
lieferschein
```
```
Lieferschein
```
```
aufmaß
```
```
Aufmaß
```

**AND Subject does NOT contain:**
```
newsletter
```
```
spam
```
```
werbung
```

### Action: Webhooks by Zapier - POST

**Webhook URL:**
```
https://my-langgraph-agent-production.up.railway.app/webhook/ai-email/incoming
```

**Payload Type:** Form

### Data Fields

Kopieren Sie jede Zeile einzeln (erst Key, dann Value):

**Field 1:**
```
document_type_hint
```
```
delivery_note
```

**Field 2:**
```
email_direction
```
```
incoming
```

**Field 3:**
```
priority
```
```
normal
```

**Field 4:**
```
sender
```
```
{{from__emailAddress__address}}
```

**Field 5:**
```
sender_email
```
```
{{from__emailAddress__address}}
```

**Field 6:**
```
sender_name
```
```
{{from__emailAddress__name}}
```

**Field 7:**
```
recipient
```
```
{{toRecipients[]emailAddress__address}}
```

**Field 8:**
```
recipient_email
```
```
{{toRecipients[]emailAddress__address}}
```

**Field 9:**
```
recipient_name
```
```
{{toRecipients[]emailAddress__name}}
```

**Field 10:**
```
subject
```
```
{{subject}}
```

**Field 11:**
```
body
```
```
{{body__content}}
```

**Field 12:**
```
body_content
```
```
{{body__content}}
```

**Field 13:**
```
body_preview
```
```
{{bodyPreview}}
```

**Field 14:**
```
attachment_names
```
```
{{attachments[]name}}
```

**Field 15:**
```
attachment_types
```
```
{{attachments[]contentType}}
```

**Field 16:**
```
received_time
```
```
{{receivedDateTime}}
```

**Field 17:**
```
message_id
```
```
{{id}}
```

**Field 18:**
```
conversation_id
```
```
{{conversationId}}
```

**Field 19:**
```
has_attachments
```
```
{{hasAttachments}}
```

---

## 💼 ZAP 3: ANGEBOTE

### Zap Name
```
💼 Angebote (Inbox → Railway)
```

### Trigger: Microsoft Outlook - New Email
- **Account:** mj@cdtechnologies.de
- **Folder:** Inbox

### Filter Conditions

**Subject contains (OR Logic):**
```
angebot
```
```
Angebot
```
```
Offer
```
```
offer
```

**AND Subject does NOT contain:**
```
newsletter
```
```
spam
```
```
werbung
```

### Action: Webhooks by Zapier - POST

**Webhook URL:**
```
https://my-langgraph-agent-production.up.railway.app/webhook/ai-email/incoming
```

**Payload Type:** Form

### Data Fields

**Field 1:**
```
document_type_hint
```
```
offer
```

**Field 2:**
```
email_direction
```
```
incoming
```

**Field 3:**
```
priority
```
```
normal
```

**Field 4:**
```
sender
```
```
{{from__emailAddress__address}}
```

**Field 5:**
```
sender_email
```
```
{{from__emailAddress__address}}
```

**Field 6:**
```
sender_name
```
```
{{from__emailAddress__name}}
```

**Field 7:**
```
recipient
```
```
{{toRecipients[]emailAddress__address}}
```

**Field 8:**
```
recipient_email
```
```
{{toRecipients[]emailAddress__address}}
```

**Field 9:**
```
recipient_name
```
```
{{toRecipients[]emailAddress__name}}
```

**Field 10:**
```
subject
```
```
{{subject}}
```

**Field 11:**
```
body
```
```
{{body__content}}
```

**Field 12:**
```
body_content
```
```
{{body__content}}
```

**Field 13:**
```
body_preview
```
```
{{bodyPreview}}
```

**Field 14:**
```
attachment_names
```
```
{{attachments[]name}}
```

**Field 15:**
```
attachment_types
```
```
{{attachments[]contentType}}
```

**Field 16:**
```
received_time
```
```
{{receivedDateTime}}
```

**Field 17:**
```
message_id
```
```
{{id}}
```

**Field 18:**
```
conversation_id
```
```
{{conversationId}}
```

**Field 19:**
```
has_attachments
```
```
{{hasAttachments}}
```

---

## 📬 ZAP 4: CATCH-ALL

### Zap Name
```
📬 Catch-All (Inbox → Railway)
```

### Trigger: Microsoft Outlook - New Email
- **Account:** mj@cdtechnologies.de
- **Folder:** Inbox

### Filter Conditions

**MUST HAVE:**
```
Has Attachments (Boolean) equals: true
```

**AND Subject does NOT contain:**
```
rechnung
```
```
invoice
```
```
lieferschein
```
```
angebot
```
```
offer
```
```
newsletter
```
```
spam
```
```
werbung
```

### Action: Webhooks by Zapier - POST

**Webhook URL:**
```
https://my-langgraph-agent-production.up.railway.app/webhook/ai-email/incoming
```

**Payload Type:** Form

### Data Fields

**Field 1:**
```
document_type_hint
```
⚠️ **LEER LASSEN!** (Kein Value eingeben - GPT entscheidet)

**Field 2:**
```
email_direction
```
```
incoming
```

**Field 3:**
```
priority
```
```
normal
```

**Field 4:**
```
sender
```
```
{{from__emailAddress__address}}
```

**Field 5:**
```
sender_email
```
```
{{from__emailAddress__address}}
```

**Field 6:**
```
sender_name
```
```
{{from__emailAddress__name}}
```

**Field 7:**
```
recipient
```
```
{{toRecipients[]emailAddress__address}}
```

**Field 8:**
```
recipient_email
```
```
{{toRecipients[]emailAddress__address}}
```

**Field 9:**
```
recipient_name
```
```
{{toRecipients[]emailAddress__name}}
```

**Field 10:**
```
subject
```
```
{{subject}}
```

**Field 11:**
```
body
```
```
{{body__content}}
```

**Field 12:**
```
body_content
```
```
{{body__content}}
```

**Field 13:**
```
body_preview
```
```
{{bodyPreview}}
```

**Field 14:**
```
attachment_names
```
```
{{attachments[]name}}
```

**Field 15:**
```
attachment_types
```
```
{{attachments[]contentType}}
```

**Field 16:**
```
received_time
```
```
{{receivedDateTime}}
```

**Field 17:**
```
message_id
```
```
{{id}}
```

**Field 18:**
```
conversation_id
```
```
{{conversationId}}
```

**Field 19:**
```
has_attachments
```
```
{{hasAttachments}}
```

---

## 📝 Anleitung zum Einfügen

### So fügen Sie die Data Fields in Zapier ein:

1. Im Webhook-Step: Scrollen Sie zu **"Data"**
2. Klicken Sie auf **"Show Options"** (falls versteckt)
3. Für jedes Feld:
   - Erste Code-Block = **Key** (z.B. `document_type_hint`)
   - Zweite Code-Block = **Value** (z.B. `delivery_note`)
4. Klicken Sie auf **"+ Add field"** für das nächste Feld
5. Wiederholen bis alle 19 Felder eingefügt sind

### ⚠️ Wichtige Unterschiede pro Zap

| Zap | document_type_hint | priority |
|-----|-------------------|----------|
| **Zap 1 (Rechnungen)** | `invoice` | `high` |
| **Zap 2 (Lieferscheine)** | `delivery_note` | `normal` |
| **Zap 3 (Angebote)** | `offer` | `normal` |
| **Zap 4 (Catch-All)** | *(LEER!)* | `normal` |

---

## ✅ Checkliste nach Erstellung

Nach Erstellung jedes Zaps prüfen:

- [ ] Zap-Name korrekt (mit Emoji)
- [ ] Trigger auf **Inbox**
- [ ] Filter korrekt konfiguriert
- [ ] Webhook URL: `/webhook/ai-email/incoming`
- [ ] Alle 19 Data Fields eingefügt
- [ ] `document_type_hint` hat richtigen Wert (oder leer bei Catch-All)
- [ ] `email_direction` = `incoming`
- [ ] `priority` korrekt gesetzt
- [ ] Test durchgeführt (200 OK Response)
- [ ] **Zap ON** geschaltet ✅

---

## 🔍 Verification nach Aktivierung

Alle Zaps aktiviert? Führen Sie diesen Befehl aus:

```bash
railway logs --tail 50 | grep "document_type_hint"
```

Sie sollten sehen:
- `document_type_hint: "invoice"` (Zap 1)
- `document_type_hint: "delivery_note"` (Zap 2)
- `document_type_hint: "offer"` (Zap 3)
- `document_type_hint: ""` (Zap 4 - leer)

---

## 📤 ZAP 5: OUTGOING (SENT ITEMS)

### Zap Name
```
📤 Outgoing (Sent Items → Railway)
```

### Trigger: Microsoft Outlook - New Email
- **Account:** mj@cdtechnologies.de
- **Folder:** Sent Items (oder "Gesendete Elemente")

### Filter Conditions

**Optional - Subject does NOT contain:**
```
newsletter
```
```
spam
```
```
test
```
```
Out of Office
```
```
Abwesenheitsnotiz
```

⚠️ **KEIN "Has Attachments" Filter!** Wir wollen ALLE ausgehenden E-Mails erfassen!

### Action: Webhooks by Zapier - POST

**Webhook URL:**
```
https://my-langgraph-agent-production.up.railway.app/webhook/ai-email/outgoing
```

**Payload Type:** Form

### Data Fields

**Field 1:**
```
document_type_hint
```
⚠️ **LEER LASSEN!** (GPT klassifiziert: Angebot, Richtpreis, Auftragsbestätigung, etc.)

**Field 2:**
```
email_direction
```
```
outgoing
```

**Field 3:**
```
priority
```
```
normal
```

**Field 4:**
```
sender
```
```
{{from__emailAddress__address}}
```

**Field 5:**
```
sender_email
```
```
{{from__emailAddress__address}}
```

**Field 6:**
```
sender_name
```
```
{{from__emailAddress__name}}
```

**Field 7:**
```
recipient
```
```
{{toRecipients[]emailAddress__address}}
```

**Field 8:**
```
recipient_email
```
```
{{toRecipients[]emailAddress__address}}
```

**Field 9:**
```
recipient_name
```
```
{{toRecipients[]emailAddress__name}}
```

**Field 10:**
```
subject
```
```
{{subject}}
```

**Field 11:**
```
body
```
```
{{body__content}}
```

**Field 12:**
```
body_content
```
```
{{body__content}}
```

**Field 13:**
```
body_preview
```
```
{{bodyPreview}}
```

**Field 14:**
```
attachment_names
```
```
{{attachments[]name}}
```

**Field 15:**
```
attachment_types
```
```
{{attachments[]contentType}}
```

**Field 16:**
```
sent_time
```
```
{{sentDateTime}}
```

**Field 17:**
```
message_id
```
```
{{id}}
```

**Field 18:**
```
conversation_id
```
```
{{conversationId}}
```

**Field 19:**
```
has_attachments
```
```
{{hasAttachments}}
```

---

## 🔄 Outgoing Workflow-Logik

**Was passiert mit Outgoing E-Mails im Orchestrator:**

### 1️⃣ **GPT-Klassifikation**
```
- Angebot / Offer
- Richtpreis / Estimated Price
- Auftragsbestätigung / Order Confirmation
- Lieferschein / Delivery Note
- Rechnung / Invoice
- Allgemeine Kommunikation / General
```

### 2️⃣ **CRM-Abgleich**
```python
# Prüfe: Ist Empfänger im CRM bekannt?
customer_match = await weclapp_lookup(recipient_email)

if customer_match:
    # Kunde bekannt → Prüfe ob Vorgang schon im CRM existiert
    crm_entry_exists = await check_crm_entry(conversation_id, customer_id)
    
    if not crm_entry_exists:
        # NICHT im CRM → Ablegen!
        await create_crm_entry(
            customer_id=customer_id,
            doc_type=classified_type,  # "offer", "order_confirmation", etc.
            email_data=email_data,
            onedrive_link=onedrive_link
        )
        
        # User benachrichtigen
        await notify_user(
            "✅ Automatisch abgelegt: Angebot für Kunde XY wurde im CRM hinterlegt"
        )
    else:
        # Schon im CRM (aus CRM verschickt)
        logger.info("✅ Already in CRM - Only OneDrive backup")
else:
    # Kunde NICHT bekannt → Temporärer CRM-Eintrag + Notification
    await create_temp_crm_contact(recipient_email)
    await notify_user(
        "⚠️ Neuer Kontakt: Email an unbekannten Empfänger gesendet"
    )
```

### 3️⃣ **OneDrive-Ablage**
```
Scan/Buchhaltung/{jahr}/{monat}/Ausgang/{empfänger}/{dokument}.pdf
```

### 4️⃣ **User-Notification Beispiele**
- ✅ "Angebot für Müller GmbH wurde automatisch im CRM abgelegt"
- ✅ "Auftragsbestätigung für Projekt #12345 im CRM hinterlegt"
- ⚠️ "Email an neuen Kontakt test@example.com gesendet - Bitte CRM prüfen"
- ℹ️ "Email bereits aus CRM verschickt - Nur OneDrive Backup erstellt"

---

**🎉 Fertig! Alle Zaps sind einsatzbereit!**
