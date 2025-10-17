# 🚀 Railway Deployment Guide

## Änderungen in diesem Update (17. Oktober 2025)

### ✅ TODO 1-5 KOMPLETT implementiert:

1. **document_type_hint Parameter Support**
   - Zapier sendet `document_type_hint` + `priority` im Payload
   - Fast-Path für OCR-Route-Auswahl
   
2. **Original Apify Prompts Integration**
   - Bessere Dokumenten-Klassifikation
   - Mapping Layer Apify→Railway Format
   
3. **Ordnerstruktur-Generierung (folder_logic.py)**
   - Automatische Ordnerstruktur: `Scan/Buchhaltung/{jahr}/{monat}/Eingang/{lieferant}`
   - Generierte Dateinamen: `Rechnung_MusterGmbH_20251017_abc123.pdf`
   
4. **OneDrive Upload**
   - Upload in strukturierte Ordner
   - Duplikate werden übersprungen
   - Tracking DB wird aktualisiert
   
5. **Modulare GPT-Klassifikation**
   - `classify_document_with_gpt()` über Async Wrapper
   - Konsistente Klassifikation

### 🗄️ Neue Features:

#### **3-Stufen Duplikatprüfung**
- Stage 1: Message ID Check (instant)
- Stage 2: Content Hash Check (24h window)
- Stage 3: File Hash Check (SHA256)
- Early Exit → Spart OCR + AI Kosten!

#### **Email Tracking Database**
- Neue DB: `/tmp/email_tracking.db`
- Vollständiger Audit-Trail
- Duplikat-Historie
- OneDrive Upload Tracking

#### **Intelligente OCR-Route-Auswahl**
- Rechnung → PDF.co Invoice Parser
- Lieferschein/Aufmaß → Handwriting OCR ✍️
- Angebot/Auftrag → Standard OCR

---

## 📋 Railway Deployment Schritte

### 1. Environment Variables prüfen

Stelle sicher, dass diese Env Vars in Railway gesetzt sind:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Microsoft Graph API (Email + OneDrive)
MS_CLIENT_ID=...
MS_CLIENT_SECRET=...
MS_TENANT_ID=...

# WeClapp CRM
WECLAPP_API_TOKEN=...
WECLAPP_DOMAIN=cdtech

# PDF.co OCR
PDFCO_API_KEY=...

# Apify (optional)
APIFY_TOKEN=...
```

### 2. Git Commit + Push

```bash
git add .
git commit -m "✨ Added: Ordnerstruktur, OneDrive Upload, Duplikatprüfung, Email Tracking DB"
git push origin main
```

### 3. Railway Auto-Deploy

Railway erkennt den Push automatisch und deployed:
- Installiert Dependencies aus `requirements.txt`
- Startet mit: `uvicorn production_langgraph_orchestrator:app --host 0.0.0.0 --port $PORT`
- Health Check: `GET /health` sollte 200 zurückgeben

### 4. Deployment URL

Deine Railway URL (beispielhaft):
```
https://mail2zapier2apify2gpt2onedrive-production.up.railway.app
```

Diese URL brauchst du für die Zapier Webhooks!

---

## 🧪 Testing nach Deployment

### 1. Health Check
```bash
curl https://your-app.up.railway.app/health
# Sollte zurückgeben: {"status": "healthy"}
```

### 2. Test Email Processing
Sende eine Test-Email über Zapier (siehe Zapier Guide unten)

### 3. Logs überprüfen
```bash
# In Railway Dashboard → Logs Tab
# Schaue nach:
# - "📁 Ordnerstruktur generiert: ..."
# - "☁️ Upload erfolgreich: ..."
# - "💾 Email saved to tracking DB with ID: ..."
```

---

## 🔍 Debugging

### Häufige Probleme:

**1. "Access token expired"**
- Lösung: Graph API Token muss regelmäßig erneuert werden
- Code erneuert automatisch bei 401 Fehler

**2. "OneDrive upload failed"**
- Check: `MS_CLIENT_ID`, `MS_CLIENT_SECRET`, `MS_TENANT_ID`
- Check: OneDrive Permissions (Files.ReadWrite.All)

**3. "OCR route placeholder"**
- Check: `PDFCO_API_KEY` ist gesetzt
- Check: PDF.co Account hat Credits

**4. "Duplicate detection not working"**
- Check: `/tmp/email_tracking.db` existiert (wird automatisch erstellt)
- Check: File System Permissions auf Railway

---

## 📊 Database Schema

### email_tracking.db

**processed_emails:**
- message_id (UNIQUE)
- user_email, from_address, subject
- subject_hash, content_hash (für Duplikatprüfung)
- workflow_path, document_type
- kunde, lieferant, projektnummer, ordnerstruktur, summe
- onedrive_uploaded, onedrive_path, onedrive_link
- processing_time_seconds

**email_attachments:**
- email_message_id
- filename, content_type, size_bytes
- file_hash (SHA256)
- ocr_text, ocr_route
- onedrive_path, onedrive_link

---

## 🎯 Nächste Schritte nach Deployment

1. ✅ Railway Deployment abgeschlossen
2. ⏭️ Zapier Zaps erstellen (siehe ZAPIER_SETUP.md)
3. ⏭️ End-to-End Testing mit echten Emails
4. ⏭️ Monitoring + Optimierung

---

## 📝 Changelog

**v2.0.0 - 17. Oktober 2025**
- ✨ Added: Ordnerstruktur-Generierung (folder_logic.py)
- ✨ Added: OneDrive Upload in strukturierte Ordner
- ✨ Added: 3-Stufen Duplikatprüfung
- ✨ Added: Email Tracking Database
- ✨ Added: Handwriting OCR für Lieferscheine
- ✨ Added: Modulare GPT-Klassifikation
- ✨ Added: document_type_hint Fast-Path
- 🐛 Fixed: Doppelte Imports entfernt
- 📚 Added: Railway + Zapier Deployment Guides

**v1.0.0 - Baseline**
- ✅ LangGraph Orchestrator
- ✅ WeClapp CRM Integration
- ✅ Microsoft Graph API (Email + OneDrive)
- ✅ PDF.co OCR Integration
- ✅ OpenAI GPT-4 Analysis
