# 🌐 OneDrive Development Setup

**Zentrale Entwicklungsumgebung für Railway Orchestrator**

---

## 📍 Speicherort

```
~/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean/
```

**Vorteile:**
- ✅ Automatische Synchronisation über OneDrive
- ✅ Zugriff von allen Macs/PCs
- ✅ Automatisches Backup durch OneDrive
- ✅ Versionierung durch OneDrive + Git
- ✅ Team-Zugriff (C&D Tech GmbH OneDrive)

---

## 🖥️ Auf neuem Rechner einrichten

### Option 1: OneDrive Sync (EMPFOHLEN)

1. **OneDrive for Business installieren** (falls nicht vorhanden)
2. **Mit C&D Tech GmbH Account anmelden**
3. **Development Ordner synchronisieren**
4. **Fertig!** Alles ist automatisch da.

```bash
# Prüfen ob synchronisiert
ls -la "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean"

# In den Ordner wechseln
cd "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean"

# Git Status checken
git status
```

### Option 2: Manuelles Git Clone

Falls OneDrive noch nicht sync't:

```bash
# Ordner erstellen
mkdir -p "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development"
cd "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development"

# Repository klonen
git clone https://github.com/cunddtech/mail2zapier2apify2gpt2onedrive.git railway-orchestrator-clean
cd railway-orchestrator-clean

# .env File erstellen (mit deinen API Keys)
cp .env.example .env
nano .env
```

---

## 🔧 Environment Setup

### 1. Python Dependencies installieren

```bash
cd "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean"

# Virtual Environment (empfohlen)
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip3 install -r requirements.txt
```

### 2. Environment Variables prüfen

```bash
# .env File vorhanden?
ls -la .env

# Wichtigste Keys checken
grep "OPENAI_API_KEY" .env
grep "PAJ_GPS_EMAIL" .env
```

### 3. Server starten

```bash
# Mit aktiviertem venv
source venv/bin/activate
python3 production_langgraph_orchestrator.py

# Oder direkt
python3 production_langgraph_orchestrator.py
```

---

## 🌍 Von jedem Rechner arbeiten

### Workflow mit OneDrive + Git

**Auf Rechner A (z.B. MacBook):**
```bash
cd "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean"

# Änderungen machen
nano api_fahrtenbuch.py

# Git Commit
git add .
git commit -m "feat: neue Funktion"
git push

# OneDrive synchronisiert automatisch
```

**Auf Rechner B (z.B. iMac):**
```bash
cd "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean"

# OneDrive hat automatisch synchronisiert
# Git Pull für neueste Version
git pull

# Weiterarbeiten
```

### Wichtig: OneDrive + Git Kombination

- **OneDrive**: Synchronisiert ALLE Dateien (inkl. .env, venv/, __pycache__)
- **Git**: Versioniert nur Code (exkl. .env, venv/, __pycache__ via .gitignore)

**Best Practice:**
1. OneDrive für automatische Sync zwischen Rechnern
2. Git für Versionierung und Railway Deployment
3. `.env` wird via OneDrive synchronisiert (nicht in Git!)

---

## 📁 Ordnerstruktur

```
OneDrive-C&DTechGmbH/
└── Development/                          # Neuer Entwicklungsordner
    └── railway-orchestrator-clean/       # Hauptprojekt
        ├── .env                          # API Keys (OneDrive sync, NICHT in Git)
        ├── .git/                         # Git Repository
        ├── production_langgraph_orchestrator.py
        ├── api_fahrtenbuch.py
        ├── modules/                      # 20+ Module
        ├── static/                       # Dashboards
        ├── data/                         # Lokale Datenbanken (optional sync)
        └── venv/                         # Virtual Environment (pro Rechner neu)
```

---

## 🚀 Deployment Workflow

### Lokal entwickeln → Git Push → Railway Deploy

```bash
# 1. Auf MacBook: Änderungen machen
cd "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean"
nano api_fahrtenbuch.py

# 2. Lokal testen
python3 production_langgraph_orchestrator.py
# → http://localhost:5001/fahrtenbuch

# 3. Git Commit + Push
git add .
git commit -m "feat: neue Funktion"
git push origin main

# 4. Railway deployt automatisch
# → https://my-langgraph-agent-production.up.railway.app/fahrtenbuch

# 5. OneDrive synchronisiert zu anderen Rechnern
```

### Auf anderem Rechner weiterarbeiten

```bash
# 1. OneDrive hat bereits synchronisiert (automatisch)
cd "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean"

# 2. Git Pull für neueste Version
git pull

# 3. Dependencies aktualisieren (falls nötig)
pip3 install -r requirements.txt

# 4. Weiterarbeiten
```

---

## ⚠️ Wichtige Hinweise

### Was wird NICHT synchronisiert (via .gitignore)?

- `__pycache__/` (Python Cache)
- `venv/` (Virtual Environment - **pro Rechner neu erstellen!**)
- `*.pyc` (Compiled Python)
- `data/*.db` (SQLite Datenbanken - optional)

**Diese Dateien sind nur auf deinem Rechner**, nicht in Git:
- `.env` - **WIRD aber via OneDrive synchronisiert!**
- Lokale Datenbanken in `data/`
- Test-Files in `.storage/`

### Virtual Environment pro Rechner

```bash
# Auf jedem neuen Rechner:
cd "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean"

# Neues venv erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip3 install -r requirements.txt
```

### Merge-Konflikte vermeiden

**Niemals gleichzeitig** auf 2 Rechnern am **gleichen File** arbeiten!

OneDrive kann Merge-Konflikte nicht automatisch auflösen (im Gegensatz zu Git).

**Best Practice:**
1. Git Pull vor Arbeitsbeginn
2. Arbeiten
3. Git Commit + Push
4. Zum anderen Rechner wechseln
5. Git Pull dort

---

## 🔐 Security

### .env File Protection

```bash
# .env ist in OneDrive, NICHT in Git
# Permissions prüfen
ls -la .env

# Sollte sein: -rw-------  (nur du kannst lesen/schreiben)
# Falls nicht:
chmod 600 .env
```

### API Keys Backup

Die `.env` Datei wird via OneDrive gesichert, aber:

**Zusätzliches Backup empfohlen:**
- 1Password / Bitwarden für API Keys
- Oder separates Backup auf NAS

---

## 📊 Dashboard URLs

### Lokal (nach Start)
```
http://localhost:5001/                    # Health Check
http://localhost:5001/fahrtenbuch         # Fahrtenbuch GPS
http://localhost:5001/dashboard           # Payment Matching
http://localhost:5001/docs                # API Docs
```

### Railway (Live Production)
```
https://my-langgraph-agent-production.up.railway.app/
https://my-langgraph-agent-production.up.railway.app/fahrtenbuch
https://my-langgraph-agent-production.up.railway.app/dashboard
https://my-langgraph-agent-production.up.railway.app/docs
```

---

## 🆘 Troubleshooting

### "OneDrive folder not found"

```bash
# OneDrive Pfad finden
ls -la "$HOME/Library/CloudStorage/" | grep OneDrive

# Fallback: Manuell zu OneDrive navigieren
cd "$HOME/OneDrive - C&D Tech GmbH/Development/railway-orchestrator-clean"
```

### "Git: permission denied"

```bash
# Git Credentials neu setzen
git config --global user.email "your@email.com"
git config --global user.name "Your Name"

# SSH Key einrichten (einmalig)
ssh-keygen -t ed25519 -C "your@email.com"
# Zu GitHub hinzufügen
```

### "Python module not found"

```bash
# Vermutlich venv nicht aktiviert
source venv/bin/activate

# Dependencies neu installieren
pip3 install -r requirements.txt
```

### "Port 5001 already in use"

```bash
# Prozess finden und beenden
lsof -ti:5001 | xargs kill -9

# Server neu starten
python3 production_langgraph_orchestrator.py
```

---

## 🎯 Quick Commands

```bash
# Alias für schnellen Zugriff (in ~/.zshrc)
alias cddev='cd "$HOME/Library/CloudStorage/OneDrive-C&DTechGmbH/Development/railway-orchestrator-clean"'
alias startserver='cddev && source venv/bin/activate && python3 production_langgraph_orchestrator.py'

# Nach Reload verfügbar
source ~/.zshrc

# Dann einfach:
cddev           # Springt in Development Ordner
startserver     # Startet Server
```

---

## 📚 Weitere Dokumentation

- `SETUP_NEUER_RECHNER.md` - Kompletter Setup Prompt für VS Code Copilot
- `FAHRTENBUCH_QUICKSTART.md` - Fahrtenbuch System Anleitung
- `DEPLOYMENT_SUCCESS.md` - Railway Deployment Details
- `MASTER_PLAN_FINAL_2025-10-17.md` - Komplette Projektdokumentation

---

**Stand:** 11. November 2025  
**Version:** 1.5.0-fahrtenbuch  
**Letzter Commit:** 9b8cce1 (Fahrtenbuch Dashboard Phase 3 COMPLETE)
