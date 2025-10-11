# 🚀 Railway Manual Update Anleitung

## SCHNELLER WEG: Railway Dashboard Update

### 1. **Bereite die gefixten Dateien vor:**

```bash
# Kopiere diese Dateien in einen separaten Ordner:
mkdir railway_upload
cp production_langgraph_orchestrator.py railway_upload/
cp requirements.txt railway_upload/
cp Dockerfile railway_upload/
```

### 2. **Railway Dashboard öffnen:**
1. Gehe zu: https://railway.app/dashboard
2. Finde dein Projekt: "my-langgraph-agent"
3. Klicke auf das Projekt

### 3. **Files direkt ersetzen:**
1. Gehe zu "Deployments" Tab
2. Klicke auf die neuste Deployment
3. Klicke "View Files" oder "Source"
4. Ersetze diese 3 Dateien:
   - `production_langgraph_orchestrator.py` (mit JSON Fix)
   - `requirements.txt` (mit LangChain Dependencies)
   - Dockerfile (falls nötig)

### 4. **Manual Redeploy:**
1. Gehe zurück zu "Deployments"
2. Klicke "Redeploy" Button
3. Warte 2-3 Minuten

---

## ALTERNATIVE: GitHub Clean Push

### Option A: Neue Repository
```bash
# Erstelle neues Repository ohne Secrets
mkdir railway_clean
cd railway_clean
git init
# Kopiere nur production Files ohne .env oder secrets
cp ../production_langgraph_orchestrator.py .
cp ../requirements.txt .
cp ../Dockerfile .
git add .
git commit -m "Clean railway deployment"
# Push zu neuem GitHub repo und verbinde mit Railway
```

### Option B: Git History bereinigen
```bash
# VORSICHT: Löscht Git History
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch *.env* input.json.template EMAIL_MONITORING_CONFIG.md' \
--prune-empty --tag-name-filter cat -- --all

git push origin --force --all
```

---

## SOFORT LÖSUNG: Direct File Update

**Gefixte Datei ist hier:** `/Users/cdtechgmbh/mail2zapier2apify2gpt2onedrive/production_langgraph_orchestrator.py`

**Geänderte Zeilen 277-295:** JSON Template mit {{ }} escaping

**Requirements.txt Update:** LangChain dependencies hinzugefügt