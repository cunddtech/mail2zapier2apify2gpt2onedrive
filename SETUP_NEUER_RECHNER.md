# 🖥️ Setup auf neuem Rechner - VS Code Prompt

**Kopiere diesen Prompt und gib ihn GitHub Copilot auf dem neuen Rechner:**

---

```
Ich habe ein Railway-Orchestrator-Projekt auf einen neuen Mac kopiert.
Der Ordner liegt unter: /Users/[USERNAME]/railway-orchestrator-clean

Bitte hilf mir, das System komplett einzurichten. Hier ist was das Projekt macht:

PROJEKT-ÜBERSICHT:
==================

Das ist ein Multi-Channel AI Communication Orchestrator mit:
- FastAPI Server (Port 5001)
- LangGraph Workflow Engine
- Email/Call/WhatsApp Processing
- WeClapp CRM Integration
- Payment Matching System
- Fahrtenbuch GPS Management (NEU!)

TECHNISCHE DETAILS:
===================

Server:
- production_langgraph_orchestrator.py (FastAPI + LangGraph)
- Läuft auf Port 5001 (nicht 8000!)
- Python 3.11+
- SQLite Datenbanken (lokal in /tmp/)

Hauptkomponenten:
- modules/ (20+ Module für verschiedene Features)
- api_fahrtenbuch.py (Fahrtenbuch REST API)
- static/fahrtenbuch.html (Vue.js Dashboard)

SETUP-SCHRITTE DIE ICH BRAUCHE:
================================

1. PYTHON ENVIRONMENT
   - Python Version checken (mind. 3.11)
   - Virtual Environment erstellen
   - Dependencies installieren (requirements.txt)

2. ENVIRONMENT VARIABLES
   - .env File erstellen
   - Benötigte Keys:
     * OPENAI_API_KEY (für GPT-4)
     * WECLAPP_API_KEY (optional, für CRM)
     * APIFY_TOKEN (optional)
     * PAJ_GPS_EMAIL (für Fahrtenbuch)
     * PAJ_GPS_PASSWORD (für Fahrtenbuch)

3. DATENBANKEN
   - SQLite Datenbanken checken
   - Werden automatisch in /tmp/ erstellt beim ersten Start
   - trip_logs Tabelle für Fahrtenbuch
   - email_tracking.db für Email Duplikat-Check

4. SERVER STARTEN
   - Wie starte ich den Server richtig?
   - Welcher Port wird verwendet?
   - Wie öffne ich die Dashboards?

5. TESTEN
   - Health Check URL
   - Fahrtenbuch Dashboard URL
   - Payment Dashboard URL
   - API Endpoints testen

WICHTIGE BESONDERHEITEN:
=========================

⚠️ Port 5001, NICHT 8000!
⚠️ Environment Variables MÜSSEN gesetzt sein (OPENAI_API_KEY mindestens)
⚠️ Alte Programme (Apify Actors) NICHT anfassen
⚠️ Dokumentation liegt in *.md Dateien (FAHRTENBUCH_QUICKSTART.md etc.)

DASHBOARD URLS (nach Start):
=============================

Lokal:
- http://localhost:5001/ (Health Check)
- http://localhost:5001/fahrtenbuch (Fahrtenbuch GPS Management)
- http://localhost:5001/dashboard (Payment Matching)
- http://localhost:5001/docs (API Dokumentation)

ERWARTETES ERGEBNIS:
====================

Nach dem Setup sollte ich:
1. Den Server auf Port 5001 starten können
2. Alle Dashboards im Browser öffnen können
3. Die API Endpoints testen können
4. Keine Fehler bei fehlenden Dependencies haben

ZUSÄTZLICHE INFOS:
==================

Das Projekt ist Stand 11. November 2025.
Version: 1.5.0-fahrtenbuch
Git Repo: https://github.com/cunddtech/mail2zapier2apify2gpt2onedrive
Branch: main
Letzter Commit: 9b8cce1 (Fahrtenbuch Dashboard Phase 3)

Backup vorhanden unter: backups/fahrtenbuch_dashboard_20251111_194820/

BITTE HILF MIR MIT:
===================

1. Step-by-step Setup Commands
2. .env Template mit allen nötigen Keys
3. Wie starte ich den Server
4. Wie teste ich dass alles läuft
5. Troubleshooting häufiger Fehler

WICHTIG: Ich bin auf macOS, benutze zsh Shell.
```

---

## 📋 Was der neue Rechner haben muss:

### System Requirements:
```bash
- macOS (jede Version mit Python 3.11+)
- Homebrew (Package Manager)
- Python 3.11 oder höher
- Git (für Updates)
- ca. 2 GB freier Speicher
```

### Optional aber empfohlen:
```bash
- VS Code mit GitHub Copilot Extension
- Railway CLI (wenn du auf Railway deployen willst)
- ngrok (wenn du externe Zugriff brauchst)
```

---

## 🔧 Quick Setup (wenn Copilot zu langsam ist):

Falls du es selbst machen willst, hier die Commands:

```bash
# 1. In den Ordner wechseln
cd /Users/[USERNAME]/railway-orchestrator-clean

# 2. Python Version checken
python3 --version  # Sollte 3.11+ sein

# 3. Virtual Environment (optional aber empfohlen)
python3 -m venv venv
source venv/bin/activate

# 4. Dependencies installieren
pip3 install -r requirements.txt

# Oder wenn keine requirements.txt:
pip3 install fastapi uvicorn langgraph langchain-openai openai \
    aiohttp httpx requests python-dotenv pytz pydantic \
    python-multipart

# 5. .env File erstellen
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
WECLAPP_API_KEY=your-weclapp-token
APIFY_TOKEN=your-apify-token
PAJ_GPS_EMAIL=your-email@example.com
PAJ_GPS_PASSWORD=your-password
EOF

# 6. .env mit echten Werten füllen (vom alten Mac kopieren)
nano .env

# 7. Server starten
python3 production_langgraph_orchestrator.py

# 8. Im Browser öffnen
open http://localhost:5001/fahrtenbuch
```

---

## 📦 Welche Dateien müssen kopiert werden?

### Mindestens diese Dateien/Ordner:

```
MUST HAVE:
✅ production_langgraph_orchestrator.py (Hauptserver)
✅ api_fahrtenbuch.py (Fahrtenbuch API)
✅ modules/ (ALLE Module!)
✅ static/ (Frontend Dashboards)
✅ .env (Environment Variables - WICHTIG!)

OPTIONAL:
⏳ data/ (Datenbanken - werden neu erstellt wenn nicht vorhanden)
⏳ backups/ (Nur wenn du alte Versionen brauchst)
⏳ *.md Dateien (Dokumentation - hilfreich!)
⏳ test_*.py (Test Scripts)
```

### Dateien die NICHT kopiert werden müssen:

```
❌ __pycache__/ (Python Cache)
❌ .git/ (Git History - nur wenn du kein git pull machst)
❌ venv/ (Virtual Environment - wird neu erstellt)
❌ *.pyc (Compiled Python)
❌ .DS_Store (Mac Metadata)
```

---

## 🚀 Alternative: Git Clone (EMPFOHLEN!)

Statt alles zu kopieren, besser Git Clone:

```bash
# Auf neuem Mac
cd ~
git clone https://github.com/cunddtech/mail2zapier2apify2gpt2onedrive.git railway-orchestrator-clean
cd railway-orchestrator-clean

# .env File vom alten Mac kopieren (USB/AirDrop/Cloud)
# Oder neu erstellen mit deinen Keys

# Dependencies installieren
pip3 install -r requirements.txt

# Server starten
python3 production_langgraph_orchestrator.py
```

**Vorteil:** Immer aktuellste Version via `git pull`

---

## 🔐 Environment Variables (.env Template):

```env
# ============================================
# RAILWAY ORCHESTRATOR - Environment Variables
# ============================================

# OpenAI (REQUIRED)
OPENAI_API_KEY=sk-proj-...

# WeClapp CRM (optional, aber empfohlen)
WECLAPP_API_KEY=your-token-here

# Apify (optional)
APIFY_TOKEN=apify_api_...

# PAJ GPS für Fahrtenbuch (optional)
PAJ_GPS_EMAIL=your-email@example.com
PAJ_GPS_PASSWORD=your-password

# Microsoft Graph (optional, für Email Processing)
MSGRAPH_CLIENT_ID=your-client-id
MSGRAPH_CLIENT_SECRET=your-secret
MSGRAPH_TENANT_ID=your-tenant-id

# PDF.co (optional, für OCR)
PDFCO_API_KEY=your-key

# Railway Webhook Token (optional)
RAILWAY_WEBHOOK_TOKEN=your-token
```

---

## ✅ Testen dass alles funktioniert:

```bash
# 1. Server läuft?
curl http://localhost:5001/

# Erwarte: {"status": "✅ AI Communication Orchestrator ONLINE", "version": "1.5.0-fahrtenbuch"}

# 2. Fahrtenbuch Dashboard
open http://localhost:5001/fahrtenbuch

# 3. Payment Dashboard
open http://localhost:5001/dashboard

# 4. API Docs
open http://localhost:5001/docs

# 5. Fahrtenbuch API
curl http://localhost:5001/api/fahrtenbuch/stats
```

---

## 🐛 Häufige Fehler beim Setup:

### "OPENAI_API_KEY environment variable required"
```bash
# .env File fehlt oder nicht geladen
export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d'=' -f2)
```

### "Port 5001 already in use"
```bash
# Anderer Prozess läuft auf Port 5001
lsof -ti:5001 | xargs kill -9
```

### "Module 'fastapi' not found"
```bash
# Dependencies nicht installiert
pip3 install -r requirements.txt
```

### "Permission denied" bei .env
```bash
# Falsche File Permissions
chmod 600 .env
```

---

## 📱 Nach dem Setup:

**Das kannst du dann machen:**

1. ✅ Server lokal auf Port 5001 laufen lassen
2. ✅ Alle 3 Dashboards nutzen (Fahrtenbuch, Payment, Parties)
3. ✅ API Endpoints testen
4. ✅ Änderungen am Code machen
5. ✅ Git Push für Railway Deployment

**Team-Zugriff:**
- Lokal: Nur auf deinem Mac
- Railway: Von überall (HTTPS)

---

**Gib diesen Prompt einfach GitHub Copilot im Chat und er wird dich Schritt für Schritt durch das Setup führen!** 🚀

Alternativ kannst du auch einfach die "Quick Setup" Commands oben ausführen.
