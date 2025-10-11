# 🚀 GITHUB REPOSITORY COMMANDS (Nach Repository-Erstellung ausführen)

## WICHTIG: Erst GitHub Repository erstellen, dann diese Commands:

```bash
cd /Users/cdtechgmbh/mail2zapier2apify2gpt2onedrive/railway_clean_deploy

# GitHub Repository hinzufügen (URL nach Repository-Erstellung anpassen!)
git remote add origin https://github.com/cunddtech/railway-orchestrator-clean.git

# Push zu GitHub
git branch -M main
git push -u origin main
```

## NACH ERFOLGREICHEM PUSH:

### 3. **Railway Dashboard connecten:**
1. Gehe zu: https://railway.app/dashboard
2. Finde Projekt: "my-langgraph-agent" (handsome-rejoicing)
3. Settings → Source Repository
4. **Disconnect** aktuelles Repository (falls connected)
5. **Connect Repository**
6. Wähle: `cunddtech/railway-orchestrator-clean`
7. ✅ Auto-Deploy startet automatisch

### 4. **Deployment überwachen:**
- Railway zeigt Build-Logs
- Warte auf: "✅ Build successful" 
- Warte auf: "✅ Deploy successful"

### 5. **TESTEN:**
```bash
cd /Users/cdtechgmbh/mail2zapier2apify2gpt2onedrive
./quick_test.sh
```

---

## ✅ READY TO GO!