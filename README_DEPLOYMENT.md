# 🚀 DEPLOYMENT QUICK START

## 📦 Was wurde implementiert?

### ✅ 5 Hauptfeatures (TODO 1-5):
1. **document_type_hint** - Zapier sendet Dokumenttyp → Fast-Path OCR
2. **Apify Prompts** - Bessere AI-Klassifikation
3. **Ordnerstruktur** - Auto-Generierung: `Scan/Buchhaltung/{jahr}/{monat}/Eingang/{lieferant}`
4. **OneDrive Upload** - Upload in strukturierte Ordner
5. **Modulare GPT** - Konsistente Klassifikation via classify_document_with_gpt()

### 🆕 Bonus Features:
- **3-Stufen Duplikatprüfung** (Message ID → Content Hash → File Hash)
- **Email Tracking Database** (Vollständiger Audit-Trail)
- **Handschrift-OCR** (Für Lieferscheine/Aufmaß)
- **Intelligente OCR-Routen** (Invoice Parser, Standard, Handwriting)

---

## ⚡ 3-Schritte Deployment

### SCHRITT 1: Railway Deployment (5 Min) ☁️

```bash
# 1. Git commit + push
git add .
git commit -m "✨ v2.0: Ordnerstruktur, OneDrive Upload, Duplikatprüfung"
git push origin main

# 2. Railway auto-deploy (2-3 Min)
# Dashboard: https://railway.app

# 3. Health Check
curl https://your-app.up.railway.app/health
# Expected: {"status": "healthy"}
```

**Environment Variables prüfen:**
- ✅ OPENAI_API_KEY
- ✅ MS_CLIENT_ID, MS_CLIENT_SECRET, MS_TENANT_ID
- ✅ WECLAPP_API_TOKEN, WECLAPP_DOMAIN
- ✅ PDFCO_API_KEY

📖 Details: `RAILWAY_DEPLOYMENT.md`

---

### SCHRITT 2: Zapier Zaps erstellen (20 Min) 📧

**Zap 1: Eingehende Mails (9 Min)**
1. Trigger: Microsoft Outlook → New Email → Inbox
2. Filter: Has Attachments = true
3. Action: Webhook POST → Railway URL
   ```json
   {
     "email_direction": "incoming",
     "message_id": "{{trigger__internetMessageId}}",
     ...
   }
   ```

**Zap 2: Ausgehende Mails (9 Min)**
1. Trigger: Microsoft Outlook → New Email → Sent Items
2. Filter: Has Attachments = true
3. Action: Webhook POST → Railway URL
   ```json
   {
     "email_direction": "outgoing",
     ...
   }
   ```

📖 Details: `ZAPIER_SETUP.md`

---

### SCHRITT 3: Testing (30 Min) 🧪

**Test 1: Eingehende Rechnung**
```
Sende Email an mj@cdtechnologies.de mit PDF-Rechnung
→ Check OneDrive: Scan/Buchhaltung/2025/10/Eingang/{Lieferant}/
```

**Test 2: Ausgehende Rechnung**
```
Sende Email von mj@cdtechnologies.de mit PDF-Rechnung
→ Check OneDrive: Scan/Buchhaltung/2025/10/Ausgang/{Kunde}/
```

**Test 3: Duplikat**
```
Sende gleiche Email zweimal
→ Check Logs: "DUPLICATE by Message ID"
```

📖 Details: `TESTING.md` (9 Test-Szenarien)

---

## 📊 Monitoring

### Railway Logs überwachen:
```bash
# Erfolgreiche Verarbeitung:
✅ Email processing complete: WEG_B
📁 Ordnerstruktur generiert: Scan/Buchhaltung/2025/10/Eingang/MusterGmbH
☁️ Upload erfolgreich: https://1drv.ms/...
💾 Email saved to tracking DB with ID: 123

# Duplikat erkannt:
⚠️ DUPLICATE by Message ID: ...
⚠️ DUPLICATE by Content: ...
⚠️ DUPLICATE ATTACHMENT: ...

# Fehler:
❌ Upload fehlgeschlagen: ...
❌ OCR route placeholder (PDFCO_API_KEY missing)
```

### Zapier Dashboard:
- ✅ Success: Email verarbeitet
- ⚠️ Filtered: Kein Attachment (OK)
- ❌ Error: Railway Fehler → Logs checken

---

## 🎯 Success Criteria

Deployment erfolgreich wenn:

- [x] Railway Deployment: ✅ Status "Deployed"
- [x] Health Check: ✅ 200 Response
- [x] Zapier Zaps: ✅ 2 Zaps aktiv
- [x] Test 1 (Eingang): ✅ Ordner korrekt, Upload erfolgreich
- [x] Test 2 (Ausgang): ✅ Ausgang-Ordner, Upload erfolgreich
- [x] Test 3 (Duplikat): ✅ Early Exit, kein 2. Upload

---

## 📁 Ordnerstruktur-Logik

### Eingehende Rechnungen:
```
Scan/Buchhaltung/{jahr}/{monat}/Eingang/{lieferant}/
Beispiel: Scan/Buchhaltung/2025/10/Eingang/MusterGmbH/
```

### Ausgehende Rechnungen:
```
Scan/Buchhaltung/{jahr}/{monat}/Ausgang/{kunde}/
Beispiel: Scan/Buchhaltung/2025/10/Ausgang/KundeXYZ/
```

### Projekt-Dokumente:
```
Scan/Projekte/{kunde}/{projektnummer}/{dokumenttyp}/
Beispiel: Scan/Projekte/KundeXYZ/PRJ-2025-001/Angebot/
```

### Dateinamen:
```
{Dokumenttyp}_{Firma}_{YYYYMMDD}_{UUID6}.pdf
Beispiel: Rechnung_MusterGmbH_20251017_a3f8c2.pdf
```

---

## 🔄 Workflow-Übersicht

```
📧 Email eingeht
    ↓
🔍 Zapier Filter (has_attachments)
    ↓
📤 Webhook → Railway
    ↓
🗄️ Duplikatprüfung (3 Stufen)
    ├─ Duplikat? → ⏭️ Skip
    └─ Neu? → ⬇️ Weiter
    ↓
📎 Attachment Download (Graph API)
    ↓
🤖 OCR Processing (PDF.co)
    ├─ Rechnung → Invoice Parser
    ├─ Lieferschein → Handwriting OCR
    └─ Sonstige → Standard OCR
    ↓
🧠 AI Analyse (GPT-4)
    ├─ Dokumenttyp
    ├─ Kunde / Lieferant
    ├─ Summe, Datum
    └─ Projektnummer
    ↓
📁 Ordnerstruktur generieren
    ↓
☁️ OneDrive Upload
    ↓
💾 Tracking DB Update
    ↓
✅ Complete!
```

---

## 🚨 Troubleshooting

### Problem: Railway Deployment Failed
```bash
# Check Build Logs
# Häufige Ursachen:
# - requirements.txt Syntax Error
# - Python Version Mismatch
# - Missing Dependencies

# Lösung:
pip install -r requirements.txt  # Lokal testen
python3 -m py_compile production_langgraph_orchestrator.py
```

### Problem: Zapier triggert nicht
```
# Check:
1. Email Account Verbindung OK?
2. Folder Name korrekt (Inbox vs. Posteingang)?
3. "Include Attachments" = Yes?
4. Test mit Email MIT Attachment?
```

### Problem: OneDrive Upload scheitert
```bash
# Check Railway Environment Variables:
MS_CLIENT_ID=...
MS_CLIENT_SECRET=...
MS_TENANT_ID=...

# Check Graph API Permissions:
Files.ReadWrite.All ✅
Mail.Read ✅
```

### Problem: OCR liefert kein Ergebnis
```bash
# Check:
PDFCO_API_KEY gesetzt?
PDF.co Account hat Credits?

# Test:
curl -H "x-api-key: YOUR_KEY" https://api.pdf.co/v1/account
```

---

## 📚 Dokumentation

| Datei | Beschreibung |
|-------|-------------|
| `RAILWAY_DEPLOYMENT.md` | Railway Setup, Env Vars, Debugging |
| `ZAPIER_SETUP.md` | Zap-Konfiguration Schritt-für-Schritt |
| `TESTING.md` | 9 Test-Szenarien, Database Queries |
| `README.md` | (Dieser File) Quick Start |

---

## 🎉 Next Steps nach Go-Live

1. **Monitoring aktivieren** → Railway Logs + Alerts
2. **Weekly Cleanup** → Alte Tracking DB Einträge löschen
3. **Performance Optimierung** → Bei > 100 Emails/Tag
4. **Apify Prompts tunen** → Für bessere Extraktion
5. **Dokumenttyp-Zaps** → Optional für spezielle Fälle

---

## 🏆 Was ist neu in v2.0?

**v1.0 (Baseline):**
- ✅ LangGraph Orchestrator
- ✅ WeClapp CRM Integration
- ✅ Graph API (Email + OneDrive)
- ✅ PDF.co OCR
- ✅ GPT-4 AI Analysis

**v2.0 (Jetzt):**
- ✨ **Ordnerstruktur-Generierung** (Automatisch)
- ✨ **OneDrive Upload** (In strukturierte Ordner)
- ✨ **3-Stufen Duplikatprüfung** (Spart Kosten!)
- ✨ **Email Tracking DB** (Vollständiger Audit-Trail)
- ✨ **Handschrift-OCR** (Für Lieferscheine)
- ✨ **Modulare GPT-Klassifikation** (Wartbar)
- ✨ **document_type_hint** (Fast-Path von Zapier)
- 🐛 **Bug Fixes** (Imports, Error Handling)
- 📚 **Dokumentation** (3 Guides)

---

**Total Setup Zeit: ~1 Stunde** ⏱️
- Railway Deployment: 5 Min
- Zapier Zaps: 20 Min
- Testing: 30 Min
- Buffer: 5 Min

**Ready to go!** 🚀
