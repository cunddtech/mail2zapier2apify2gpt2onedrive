# 📧 Zapier Setup Guide - Mail2Railway2OneDrive

## Übersicht

Wir erstellen **2 Basis-Zaps** für eingehende und ausgehende Mails:

1. **Zap 1: Eingehende Mails (Inbox)** → `email_direction = "incoming"`
2. **Zap 2: Ausgehende Mails (Sent Items)** → `email_direction = "outgoing"`

---

## 🎯 Zap 1: Eingehende Mails (EINGANG)

### Übersicht
- **Trigger:** Neue Email in Inbox von mj@cdtechnologies.de
- **Filter:** Hat mindestens 1 Attachment
- **Action:** Webhook POST an Railway

### Setup (ca. 9 Minuten)

#### **SCHRITT 1: Trigger einrichten**

1. **Trigger wählen:**
   - App: **Microsoft Outlook** (oder Office 365 Mail)
   - Event: **New Email** ✉️
   - Account: `mj@cdtechnologies.de` verbinden

2. **Trigger Konfiguration:**
   - Folder: **Inbox** (Posteingang)
   - Include Attachments: **Yes** ✅

3. **Test Trigger:**
   - Zapier lädt letzte Email
   - Stelle sicher, dass Attachment-Daten vorhanden sind

#### **SCHRITT 2: Filter hinzufügen**

1. **Filter einfügen** (zwischen Trigger und Action)
   - Click: **+** → **Filter**

2. **Filter Bedingung:**
   ```
   (Zap will only continue if...)
   
   Has Attachments | (Boolean) Equals | true
   
   ODER alternativ:
   
   Number of Attachments | (Number) Greater than | 0
   ```

3. **Test Filter:**
   - Mit Test-Email sollte Filter "Allowed to continue" zeigen

#### **SCHRITT 3: Webhook Action einrichten**

1. **Action wählen:**
   - App: **Webhooks by Zapier**
   - Event: **POST** 📤

2. **Webhook Konfiguration:**

**URL:**
```
https://your-railway-app.up.railway.app/api/v1/process-email
```
*(Ersetze mit deiner echten Railway URL!)*

**Payload Type:** `json`

**Data:** (JSON Format)
```json
{
  "email_id": {{trigger__id}},
  "message_id": {{trigger__internetMessageId}},
  "from": {{trigger__from}},
  "to": {{trigger__to}},
  "subject": {{trigger__subject}},
  "body": {{trigger__bodyPreview}},
  "body_type": "html",
  "received_date": {{trigger__receivedDateTime}},
  "has_attachments": true,
  "attachments": {{trigger__attachments}},
  "email_direction": "incoming",
  "document_type_hint": "",
  "priority": "normal"
}
```

**Headers:**
```
Content-Type: application/json
```

3. **Test Action:**
   - Zapier sendet Test-Request an Railway
   - Sollte Response 200 mit `{"status": "accepted"}` erhalten

#### **SCHRITT 4: Zap aktivieren**

1. **Zap benennen:** "📧 Eingehende Mails → Railway"
2. **Zap aktivieren:** Toggle auf ON
3. **Test mit echter Email:**
   - Sende Email mit PDF-Attachment an `mj@cdtechnologies.de`
   - Check Railway Logs für Processing
   - Check OneDrive für Upload

---

## 📤 Zap 2: Ausgehende Mails (AUSGANG)

### Übersicht
- **Trigger:** Neue Email in "Sent Items" von mj@cdtechnologies.de
- **Filter:** Hat mindestens 1 Attachment
- **Action:** Webhook POST an Railway

### Setup (ca. 9 Minuten)

#### **SCHRITT 1: Trigger einrichten**

1. **Trigger wählen:**
   - App: **Microsoft Outlook** (oder Office 365 Mail)
   - Event: **New Email** ✉️
   - Account: `mj@cdtechnologies.de` (gleicher Account)

2. **Trigger Konfiguration:**
   - Folder: **Sent Items** (Gesendete Elemente)
   - Include Attachments: **Yes** ✅

3. **Test Trigger:**
   - Zapier lädt letzte gesendete Email
   - Stelle sicher, dass Attachment-Daten vorhanden sind

#### **SCHRITT 2: Filter hinzufügen**

Gleich wie Zap 1:
```
Has Attachments | (Boolean) Equals | true
```

#### **SCHRITT 3: Webhook Action einrichten**

**URL:** (gleiche wie Zap 1)
```
https://your-railway-app.up.railway.app/api/v1/process-email
```

**Data:** (JSON Format - **NUR email_direction anders!**)
```json
{
  "email_id": {{trigger__id}},
  "message_id": {{trigger__internetMessageId}},
  "from": {{trigger__from}},
  "to": {{trigger__to}},
  "subject": {{trigger__subject}},
  "body": {{trigger__bodyPreview}},
  "body_type": "html",
  "received_date": {{trigger__sentDateTime}},
  "has_attachments": true,
  "attachments": {{trigger__attachments}},
  "email_direction": "outgoing",
  "document_type_hint": "",
  "priority": "normal"
}
```

**⚠️ WICHTIG:** `"email_direction": "outgoing"` statt "incoming"!

#### **SCHRITT 4: Zap aktivieren**

1. **Zap benennen:** "📤 Ausgehende Mails → Railway"
2. **Zap aktivieren:** Toggle auf ON
3. **Test mit echter Email:**
   - Sende Email MIT PDF-Attachment an einen Kunden
   - Check Railway Logs
   - Check OneDrive: Sollte in `Ausgang/` landen

---

## 🔄 Optional: Dokumenttyp-spezifische Zaps

Falls du SPEZIELLE Behandlung für bestimmte Dokumenttypen brauchst:

### Zap 3: Rechnungen (Invoice-Specific)

**Trigger:** New Email in Inbox
**Filter:**
```
Subject | (Text) Contains | Rechnung
OR
Subject | (Text) Contains | Invoice
```

**Webhook Data:**
```json
{
  ...
  "document_type_hint": "invoice",
  "priority": "high"
}
```

### Zap 4: Lieferscheine (Handwriting OCR)

**Trigger:** New Email in Inbox
**Filter:**
```
Subject | (Text) Contains | Lieferschein
OR
Subject | (Text) Contains | Aufmaß
```

**Webhook Data:**
```json
{
  ...
  "document_type_hint": "delivery_note",
  "priority": "normal"
}
```

### Zap 5: Angebote (Offers)

**Trigger:** New Email in Inbox
**Filter:**
```
Subject | (Text) Contains | Angebot
OR
Subject | (Text) Contains | Offer
```

**Webhook Data:**
```json
{
  ...
  "document_type_hint": "offer",
  "priority": "normal"
}
```

---

## 🧪 Testing Checkliste

### Nach Zap-Aktivierung:

- [ ] **Test 1: Eingehende Rechnung**
  - Sende Email mit PDF-Rechnung an `mj@cdtechnologies.de`
  - Erwartung: `Scan/Buchhaltung/2025/10/Eingang/{Lieferant}/`
  
- [ ] **Test 2: Ausgehende Rechnung**
  - Sende Email mit PDF-Rechnung von `mj@cdtechnologies.de`
  - Erwartung: `Scan/Buchhaltung/2025/10/Ausgang/{Kunde}/`
  
- [ ] **Test 3: Lieferschein mit Handschrift**
  - Sende Email mit handschriftlichem Lieferschein
  - Erwartung: OCR Route = "handwriting_ocr"
  
- [ ] **Test 4: Duplikat-Erkennung**
  - Sende gleiche Email zweimal
  - Erwartung: 2. Email wird übersprungen (Logs: "DUPLICATE")
  
- [ ] **Test 5: Email ohne Attachment**
  - Sende Email ohne PDF
  - Erwartung: Zap stoppt bei Filter (keine Webhook-Action)

---

## 📊 Monitoring

### Railway Logs überprüfen:

Gute Logs zeigen:
```
✅ Email processing complete: WEG_B
📁 Ordnerstruktur generiert: Scan/Buchhaltung/2025/10/Eingang/MusterGmbH
☁️ Upload erfolgreich: https://1drv.ms/...
💾 Email saved to tracking DB with ID: 123
```

Fehler-Logs:
```
❌ DUPLICATE by Message ID: ...
❌ Upload fehlgeschlagen für ...
❌ OCR route placeholder (PDFCO_API_KEY missing)
```

### Zapier Logs:

In Zapier Dashboard → Zap History:
- **Success:** Grünes ✅ → Email verarbeitet
- **Filtered:** Gelbes ⚠️ → Kein Attachment (OK)
- **Error:** Rotes ❌ → Railway Fehler → Logs checken

---

## 🚨 Troubleshooting

### Problem 1: Zap triggert nicht

**Lösung:**
- Check: Email Account Verbindung in Zapier
- Check: Folder Name korrekt (Inbox vs. Posteingang)
- Check: "Include Attachments" = Yes

### Problem 2: Filter stoppt alle Emails

**Lösung:**
- Test: Sende Email MIT Attachment
- Check: Filter Bedingung (has_attachments = true)
- Check: Zapier Test lädt Attachment-Daten

### Problem 3: Railway gibt 500 Error

**Lösung:**
- Check Railway Logs für Stack Trace
- Check: Alle Environment Variables gesetzt
- Check: Database `/tmp/email_tracking.db` erstellt

### Problem 4: OneDrive Upload scheitert

**Lösung:**
- Check: `MS_CLIENT_ID`, `MS_CLIENT_SECRET`, `MS_TENANT_ID`
- Check: OneDrive Permissions (Files.ReadWrite.All)
- Check: Graph API Token Renewal funktioniert

---

## 📝 Zusammenfassung

### Minimal Setup (2 Zaps):
1. ✅ Eingehende Mails → Railway → OneDrive Eingang/
2. ✅ Ausgehende Mails → Railway → OneDrive Ausgang/

### Erweitert (5 Zaps):
3. 🧾 Rechnungen (mit document_type_hint)
4. 📦 Lieferscheine (Handwriting OCR)
5. 📋 Angebote (Standard OCR)

### Total Zeit:
- Minimal: ~20 Minuten (2 Zaps × 9 Min)
- Erweitert: ~45 Minuten (5 Zaps × 9 Min)

---

## 🎯 Nächster Schritt

Nach Zap-Setup:
→ **End-to-End Testing** mit echten Emails!

Siehe: `TESTING.md` für Test-Szenarien
