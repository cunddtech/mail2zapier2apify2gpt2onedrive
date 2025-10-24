# 🚀 Development Setup Guide
## Komplettes Setup für neuen Rechner

> **Ziel:** VSCode Entwicklungsumgebung mit vollem Zugriff auf Railway, Apify, GitHub, Azure, WeClapp, OpenAI etc.

---

## 📋 OVERVIEW

**Was wird eingerichtet:**
- ✅ VSCode mit Extensions
- ✅ Git & GitHub Integration
- ✅ Python Environment
- ✅ Railway CLI & Deployment
- ✅ Apify CLI & Actors
- ✅ API Keys & Credentials
- ✅ Repository Clone & Setup

**Geschätzte Zeit:** ~45-60 Minuten

---

## 🔧 PHASE 1: SYSTEM BASICS

### 1.1 Homebrew installieren (macOS)

```bash
# Homebrew installieren
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Nach Installation: Homebrew zum PATH hinzufügen
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

### 1.2 Git installieren

```bash
# Git via Homebrew
brew install git

# Git konfigurieren
git config --global user.name "Markus Jaszczyk"
git config --global user.email "mj@cdtechnologies.de"

# Git Version prüfen
git --version
```

---

## 💻 PHASE 2: VSCODE INSTALLATION

### 2.1 VSCode herunterladen

**Option A: Website**
1. Gehe zu: https://code.visualstudio.com/
2. Download für macOS
3. DMG öffnen und VSCode nach /Applications verschieben

**Option B: Homebrew**
```bash
brew install --cask visual-studio-code
```

### 2.2 Code Command in PATH

```bash
# VSCode Command Line Tool aktivieren
# In VSCode: Cmd+Shift+P → "Shell Command: Install 'code' command in PATH"

# Test
code --version
```

---

## 🔌 PHASE 3: VSCODE EXTENSIONS

### 3.1 Essentielle Extensions

**Via Command Line installieren:**

```bash
# Python Development
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.debugpy

# GitHub Integration
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
code --install-extension GitHub.vscode-pull-request-github

# Git Tools
code --install-extension eamodio.gitlens
code --install-extension mhutchie.git-graph

# Docker & Containers
code --install-extension ms-azuretools.vscode-docker
code --install-extension ms-vscode-remote.remote-containers

# Formatters & Linters
code --install-extension ms-python.black-formatter
code --install-extension ms-python.flake8
code --install-extension esbenp.prettier-vscode

# Markdown
code --install-extension yzhang.markdown-all-in-one
code --install-extension DavidAnson.vscode-markdownlint

# Utilities
code --install-extension streetsidesoftware.code-spell-checker
code --install-extension wayou.vscode-todo-highlight
code --install-extension oderwat.indent-rainbow

# JSON & YAML
code --install-extension redhat.vscode-yaml
code --install-extension ZainChen.json
```

**Via VSCode Extensions Marketplace:**
1. Öffne VSCode
2. Klick auf Extensions Icon (Cmd+Shift+X)
3. Suche und installiere:
   - Python (Microsoft)
   - GitHub Copilot
   - GitLens
   - Docker
   - Prettier
   - Markdown All in One

---

## 🐍 PHASE 4: PYTHON SETUP

### 4.1 Python installieren

```bash
# Python via Homebrew
brew install python@3.11

# Python Version prüfen
python3 --version

# pip updaten
python3 -m pip install --upgrade pip
```

### 4.2 Virtual Environment Tools

```bash
# virtualenv installieren
pip3 install virtualenv

# pipenv (optional)
pip3 install pipenv
```

---

## 🐙 PHASE 5: GITHUB SETUP

### 5.1 GitHub Account & Authentication

**SSH Key erstellen:**

```bash
# SSH Key generieren
ssh-keygen -t ed25519 -C "mj@cdtechnologies.de"

# SSH Agent starten
eval "$(ssh-agent -s)"

# SSH Key zum Agent hinzufügen
ssh-add ~/.ssh/id_ed25519

# Public Key anzeigen
cat ~/.ssh/id_ed25519.pub
```

**GitHub SSH Key hinzufügen:**
1. Gehe zu: https://github.com/settings/keys
2. Click "New SSH key"
3. Paste den Public Key
4. Save

**Test SSH Connection:**
```bash
ssh -T git@github.com
# Sollte ausgeben: "Hi cunddtech! You've successfully authenticated..."
```

### 5.2 Repository clonen

```bash
# Repository URL kopieren
# GitHub: https://github.com/cunddtech/mail2zapier2apify2gpt2onedrive

# Clone via SSH
cd ~/Documents  # oder gewünschter Pfad
git clone git@github.com:cunddtech/mail2zapier2apify2gpt2onedrive.git

# In Projekt-Verzeichnis wechseln
cd mail2zapier2apify2gpt2onedrive

# VSCode öffnen
code .
```

---

## 🚂 PHASE 6: RAILWAY CLI SETUP

### 6.1 Railway CLI installieren

```bash
# Railway CLI via npm (benötigt Node.js)
brew install node
npm install -g @railway/cli

# Oder: Direct Binary Download
brew install railway
```

### 6.2 Railway Login & Projekt-Link

```bash
# Railway Login (öffnet Browser)
railway login

# In Projekt-Verzeichnis: Mit Railway Projekt verknüpfen
cd ~/Documents/mail2zapier2apify2gpt2onedrive
railway link

# Projekt auswählen: "handsome-rejoicing"
# Environment auswählen: "production"

# Status prüfen
railway status

# Logs ansehen
railway logs --tail 50
```

### 6.3 Railway Commands Testen

```bash
# Deployment Status
railway status

# Environment Variables ansehen
railway variables

# Service neu deployen
railway up

# Logs Real-Time
railway logs --tail
```

---

## 🕷️ PHASE 7: APIFY CLI SETUP

### 7.1 Apify CLI installieren

```bash
# Apify CLI via npm
npm install -g apify-cli

# Version prüfen
apify --version
```

### 7.2 Apify Login

```bash
# Apify Login (benötigt API Token)
apify login

# API Token von: https://console.apify.com/account/integrations
# Token eingeben wenn prompted
```

### 7.3 Apify Actor Link (falls benötigt)

```bash
# In Actor-Verzeichnis wechseln (falls vorhanden)
cd ~/Documents/mail2zapier2apify2gpt2onedrive

# Actor initialisieren (falls noch nicht verknüpft)
apify init

# Actor deployen
apify push
```

---

## 🔑 PHASE 8: API KEYS & CREDENTIALS

### 8.1 .env Datei Setup

**Erstelle `.env` im Projekt Root:**

```bash
cd ~/Documents/mail2zapier2apify2gpt2onedrive
touch .env
code .env
```

**Füge alle API Keys ein:**

```env
# Microsoft Graph API
AZURE_CLIENT_ID=138fb54c-a2ad-4d43-8455-1d4db6fad95a
AZURE_CLIENT_SECRET=[Dein Secret]
AZURE_TENANT_ID=fe87c2f4-700c-4a68-9bd7-218fde87a857

# OpenAI API
OPENAI_API_KEY=[Dein Key]

# Apify
APIFY_API_TOKEN=[Dein Token]

# PDF.co (OCR Service)
PDFCO_API_KEY=[Dein Key]

# Azure Computer Vision
AZURE_VISION_KEY=[Dein Key]
AZURE_VISION_ENDPOINT=[Dein Endpoint]

# WeClapp CRM
WECLAPP_API_KEY=[Dein Key]
WECLAPP_TENANT=cundd
WECLAPP_BASE_URL=https://cundd.weclapp.com/webapp/api/v1

# LangChain
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=[Dein Key]
LANGCHAIN_PROJECT=mail2zapier-agent

# Anthropic (Optional)
ANTHROPIC_API_KEY=[Dein Key]

# Email Accounts
EMAIL_USER_MJ=mj@cdtechnologies.de
EMAIL_USER_INFO=info@cdtechnologies.de

# Zapier (nur Login, keine API)
ZAPIER_USER=mj@cdtechnologies.de
ZAPIER_PASSWORD=[Dein Password]
```

**WICHTIG:** `.env` ist in `.gitignore` enthalten (nicht committen!)

### 8.2 API Keys beschaffen

**Wo findest du die Keys:**

1. **Microsoft Azure/Graph:**
   - Portal: https://portal.azure.com
   - App Registrations → "mail2zapier-app"
   - Certificates & secrets → Client secret

2. **OpenAI:**
   - https://platform.openai.com/api-keys
   - Create new secret key

3. **Apify:**
   - https://console.apify.com/account/integrations
   - API token kopieren

4. **PDF.co:**
   - https://app.pdf.co/
   - Dashboard → API Key

5. **WeClapp:**
   - https://cundd.weclapp.com/
   - Einstellungen → API Keys

6. **LangChain:**
   - https://smith.langchain.com/
   - Settings → API Keys

---

## 📦 PHASE 9: PYTHON DEPENDENCIES

### 9.1 Virtual Environment erstellen

```bash
# In Projekt-Verzeichnis
cd ~/Documents/mail2zapier2apify2gpt2onedrive

# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren
source venv/bin/activate

# (venv) sollte jetzt im Terminal erscheinen
```

### 9.2 Requirements installieren

```bash
# Requirements installieren
pip install -r requirements.txt

# Oder falls spezifische packages fehlen:
pip install fastapi uvicorn
pip install langgraph langchain-openai
pip install httpx requests
pip install python-dotenv
pip install azure-identity msgraph-sdk
pip install openai anthropic
pip install pillow pdf2image
pip install sqlalchemy
```

### 9.3 VSCode Python Interpreter setzen

1. In VSCode: `Cmd+Shift+P`
2. Type: "Python: Select Interpreter"
3. Wähle: `./venv/bin/python`

---

## 🔒 PHASE 10: ZUGANGSDATEN TESTEN

### 10.1 Graph API Test

```bash
# Test Script erstellen
cat << 'SCRIPT' > test_graph_api.py
import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

load_dotenv()

credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
)

client = GraphServiceClient(credentials=credential)
print("✅ Graph API Connection successful!")
SCRIPT

# Test ausführen
python test_graph_api.py
```

### 10.2 OpenAI Test

```bash
cat << 'SCRIPT' > test_openai.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Say hello!"}]
)
print(f"✅ OpenAI Response: {response.choices[0].message.content}")
SCRIPT

python test_openai.py
```

### 10.3 Railway Connection Test

```bash
# Railway Status
railway status

# Railway Variables ansehen (prüfen ob alle da sind)
railway variables

# Test Deployment
railway up --detach
```

---

## 🌐 PHASE 11: ZAPIER ZUGANG

### 11.1 Zapier Account

**Login:** https://zapier.com/app/login

**Credentials:**
- Email: mj@cdtechnologies.de
- Password: [In .env gespeichert]

### 11.2 Wichtige Zapier Links

```bash
# Zapier Zaps Overview
open https://zapier.com/app/zaps

# Zapier History
open https://zapier.com/app/history

# Zapier Account Settings
open https://zapier.com/app/settings/account
```

**Keine Zapier CLI oder API nötig** - Alle Änderungen manuell im Web UI!

---

## 📊 PHASE 12: WECLAPP ZUGANG

### 12.1 WeClapp Login

**URL:** https://cundd.weclapp.com/

**Test API Connection:**

```bash
cat << 'SCRIPT' > test_weclapp.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("WECLAPP_API_KEY")
base_url = os.getenv("WECLAPP_BASE_URL")

headers = {
    "AuthenticationToken": api_key,
    "Content-Type": "application/json"
}

response = requests.get(f"{base_url}/contact?pageSize=1", headers=headers)
print(f"✅ WeClapp Status: {response.status_code}")
print(f"Response: {response.json()}")
SCRIPT

python test_weclapp.py
```

---

## 🔄 PHASE 13: WORKFLOW SETUP

### 13.1 VSCode Workspace Settings

**Erstelle `.vscode/settings.json`:**

```bash
mkdir -p .vscode
cat << 'JSON' > .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true
  },
  "python.analysis.typeCheckingMode": "basic",
  "terminal.integrated.defaultProfile.osx": "zsh"
}
JSON
```

### 13.2 VSCode Launch Configuration

**Erstelle `.vscode/launch.json`:**

```bash
cat << 'JSON' > .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false,
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
JSON
```

---

## 🚀 PHASE 14: DEVELOPMENT WORKFLOW

### 14.1 Täglicher Start

```bash
# 1. Terminal öffnen
cd ~/Documents/mail2zapier2apify2gpt2onedrive

# 2. Virtual Environment aktivieren
source venv/bin/activate

# 3. VSCode öffnen
code .

# 4. Git Status prüfen
git status
git pull origin main

# 5. Railway Status prüfen
railway status
```

### 14.2 Code Changes & Deploy

```bash
# 1. Changes machen in VSCode

# 2. Testen lokal (optional)
python src/main.py

# 3. Git Commit
git add .
git commit -m "Feature: Beschreibung"
git push origin main

# 4. Railway Auto-Deploy wartet auf Push
# Oder manuell:
railway up
```

### 14.3 Logs Monitoring

```bash
# Railway Logs Real-Time
railway logs --tail 100

# Logs filtern
railway logs --tail 200 | grep "ERROR"
railway logs --tail 200 | grep "LOOP PREVENTION"
```

---

## 🧪 PHASE 15: TESTING SETUP

### 15.1 Test Email Workflow

**Incoming Email Test:**

```bash
# Email senden an: mj@cdtechnologies.de
# Subject: "Test Anfrage Projekt Z"
# Von: externe@beispiel.de

# Dann monitoren:
railway logs --tail 50
```

**Outgoing Email Test:**

```bash
# Email senden VON: mj@cdtechnologies.de
# Subject: "Angebot Test"
# An: externe@beispiel.de

# Zapier History checken:
open https://zapier.com/app/history
```

---

## 📚 PHASE 16: DOKUMENTATION REFERENZEN

### 16.1 Wichtige Dokumente

```bash
# Im Projekt verfügbar:
cat ZAPIER_FIX_FÜR_DEINE_ZAPS.md
cat ZAPIER_FILTER_SETUP.md
cat ZAPIER_MANUAL_FIX_ANLEITUNG.md
cat ZAPIER_FIX_MASTER_CHECKLISTE.md
```

### 16.2 API Dokumentation Links

```bash
# Microsoft Graph API
open https://learn.microsoft.com/en-us/graph/overview

# OpenAI API
open https://platform.openai.com/docs

# Apify Documentation
open https://docs.apify.com/

# Railway Documentation
open https://docs.railway.app/

# WeClapp API
open https://github.com/weclappcom/weclapp-api
```

---

## ✅ PHASE 17: VERIFICATION CHECKLIST

### 17.1 Alle Systeme Check

```bash
# ✅ Git & GitHub
git --version
ssh -T git@github.com

# ✅ Python & venv
python --version
source venv/bin/activate

# ✅ Railway
railway status
railway whoami

# ✅ Apify
apify --version
apify info

# ✅ Node.js (für Railway/Apify CLI)
node --version
npm --version

# ✅ VSCode
code --version

# ✅ .env existiert
ls -la .env

# ✅ Requirements installiert
pip list | grep fastapi
pip list | grep langgraph
```

### 17.2 API Connections Check

```bash
# Alle Test Scripts ausführen:
python test_graph_api.py
python test_openai.py
python test_weclapp.py

# Alle sollten "✅" ausgeben
```

---

## 🎯 QUICK START CHEATSHEET

### Täglicher Workflow

```bash
# 1. Start
cd ~/Documents/mail2zapier2apify2gpt2onedrive
source venv/bin/activate
code .

# 2. Latest Code holen
git pull origin main

# 3. Changes machen
# ... Code editieren in VSCode ...

# 4. Testen lokal (optional)
python src/main.py

# 5. Deploy
git add .
git commit -m "Update: ..."
git push origin main

# 6. Monitoring
railway logs --tail 50
```

### Wichtige Commands

```bash
# Railway
railway status              # Status check
railway logs --tail 100     # Logs ansehen
railway up                  # Manual deploy
railway variables           # Environment vars

# Git
git status                  # Änderungen anzeigen
git pull origin main        # Latest code holen
git push origin main        # Changes pushen

# Python
source venv/bin/activate    # venv aktivieren
pip install -r requirements.txt  # Dependencies
python src/main.py          # Local run

# Zapier (Browser)
# https://zapier.com/app/zaps     # Zaps verwalten
# https://zapier.com/app/history  # History checken
```

---

## 🆘 TROUBLESHOOTING

### Problem: "Permission denied (publickey)" bei Git

```bash
# SSH Key neu erstellen
ssh-keygen -t ed25519 -C "mj@cdtechnologies.de"
ssh-add ~/.ssh/id_ed25519

# Public Key zu GitHub hinzufügen
cat ~/.ssh/id_ed25519.pub
# → Kopieren und auf GitHub einfügen
```

### Problem: Railway CLI nicht gefunden

```bash
# Railway neu installieren
npm install -g @railway/cli

# Oder via Homebrew
brew install railway

# PATH prüfen
echo $PATH
```

### Problem: Python Module nicht gefunden

```bash
# Virtual Environment aktivieren!
source venv/bin/activate

# Requirements neu installieren
pip install -r requirements.txt

# In VSCode: Python Interpreter neu wählen
# Cmd+Shift+P → "Python: Select Interpreter"
```

### Problem: .env Datei nicht geladen

```bash
# Prüfen ob .env existiert
ls -la .env

# Prüfen ob python-dotenv installiert
pip list | grep dotenv

# In Code: load_dotenv() aufrufen
from dotenv import load_dotenv
load_dotenv()
```

---

## 🎉 FERTIG!

**Du hast jetzt:**
✅ Komplettes VSCode Setup  
✅ Git & GitHub Integration  
✅ Railway CLI & Deployment  
✅ Apify CLI  
✅ Alle API Keys konfiguriert  
✅ Python Environment  
✅ Repository geclont  
✅ Zugang zu Zapier, WeClapp, etc.  

**Nächste Schritte:**
1. Test Email senden (siehe Phase 15)
2. Railway Logs checken
3. Erste Code-Änderung machen
4. Deployment testen

**Bei Fragen:** Check die Dokumentation im Projekt oder die API Docs!

