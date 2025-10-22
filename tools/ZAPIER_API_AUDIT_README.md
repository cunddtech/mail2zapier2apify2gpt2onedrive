# 🔧 Zapier Filter Audit Tool

## 📋 Übersicht

Dieses Script verwendet die **Zapier API**, um alle deine Zaps zu analysieren und herauszufinden, welche Zaps **Filter-Steps** haben, die manuell geprüft werden müssen.

## ⚠️ WICHTIGE LIMITATION

**Zapier API kann Filter-Conditions NICHT lesen!**

Das bedeutet:
- ❌ Script kann NICHT erkennen ob "Does not start with EMAIL:" existiert
- ✅ Script kann NUR erkennen WELCHE Zaps Filter haben
- 🔧 Du musst jeden gefundenen Filter dann MANUELL in der Zapier UI prüfen

## 🚀 SCHNELLSTART

### **1. API Key holen:**

```bash
# Gehe zu: https://zapier.com/app/settings/api
# Klicke: "Generate API Key"
# Kopiere den Key
```

### **2. Script ausführen:**

```bash
# Im Terminal:
cd /Users/cdtechgmbh/mail2zapier2apify2gpt2onedrive

# API Key setzen:
export ZAPIER_API_KEY="dein-api-key-hier"

# Script ausführen:
python tools/zapier_filter_audit.py
```

### **3. Ergebnisse prüfen:**

Das Script erstellt 2 Dateien:
- `zapier_filter_audit_report.txt` - Lesbarer Report
- `zapier_filter_audit_data.json` - JSON-Daten für weitere Analyse

## 📊 WAS DAS SCRIPT AUSGIBT

### **1. Liste aller Zaps:**

```
📋 ALL ZAPS IN YOUR ACCOUNT:
══════════════════════════════════════════════════════════════

1. ✅ Outgoing (Sent Items → Railway)
   ID: 12345 | Status: on
   URL: https://zapier.com/app/editor/12345

2. ✅ (Copy) Outgoing (Sent Items → Railway)
   ID: 67890 | Status: on
   URL: https://zapier.com/app/editor/67890

[... weitere Zaps ...]
```

### **2. Audit-Ergebnisse:**

```
🎯 Analyzing 10 relevant Zaps (Outgoing/Incoming/etc.)

📋 Outgoing (Sent Items → Railway)
   ID: 12345 | Status: on
   ⚠️  Step 2: Filter detected - MANUAL AUDIT REQUIRED
   🔧 Action: Open in UI and check Filter conditions

📋 (Copy) Outgoing (Sent Items → Railway)
   ID: 67890 | Status: on
   ⚠️  Step 2: Filter detected - MANUAL AUDIT REQUIRED
   🔧 Action: Open in UI and check Filter conditions

[... weitere Zaps ...]
```

### **3. Report:**

```
📊 ZAPIER FILTER AUDIT REPORT
══════════════════════════════════════════════════════════════

⚠️  Found 2 Zaps with Filter steps

🚨 CRITICAL: Zapier API does NOT expose Filter condition details!
   You MUST manually check each Zap in the Zapier UI.

──────────────────────────────────────────────────────────────

1. Outgoing (Sent Items → Railway)
   Zap ID: 12345
   Status: on
   Filter Step: #2
   Issue: Filter step found - Manual audit required
   🔧 Fix: Open Zap in UI → Check Filter step → Change 'Does not start with' to 'Does not contain'

2. (Copy) Outgoing (Sent Items → Railway)
   Zap ID: 67890
   Status: on
   Filter Step: #2
   Issue: Filter step found - Manual audit required
   🔧 Fix: Open Zap in UI → Check Filter step → Change 'Does not start with' to 'Does not contain'

──────────────────────────────────────────────────────────────

📋 MANUAL AUDIT CHECKLIST:

For EACH Zap with 'Outgoing' or 'Sent Items' in name:
  [ ] Open Zap in Zapier UI
  [ ] Find Filter step (usually Step 2)
  [ ] Look for condition: 'Subject | Does not start with | EMAIL:'
  [ ] Change to: 'Subject | Does not contain | EMAIL:'
  [ ] Test step (should show 'Filter would not have run')
  [ ] Publish Zap
```

## 🎯 NÄCHSTE SCHRITTE NACH DEM AUDIT

### **Für jeden gefundenen Zap:**

1. **Öffne Zap in Zapier UI:**
   ```
   Klicke auf den URL aus dem Report
   Oder gehe zu: https://zapier.com/app/editor/[ZAP_ID]
   ```

2. **Finde Filter-Step:**
   ```
   Meist Step 2 (zwischen Trigger und Webhook)
   ```

3. **Prüfe Conditions:**
   ```
   Suche nach: "Subject | Does not start with | EMAIL:"
   ```

4. **Ändere Operator:**
   ```
   Ändere: "Does not start with" → "Does not contain"
   ```

5. **Test & Publish:**
   ```
   Test step → "Filter would not have run" ✅
   Publish Zap
   ```

## 🔍 TROUBLESHOOTING

### **Problem: "Error fetching Zaps: 401"**

**Lösung:**
```bash
# API Key ist ungültig oder falsch gesetzt
# Prüfe:
echo $ZAPIER_API_KEY

# Neu setzen:
export ZAPIER_API_KEY="dein-neuer-key"
```

### **Problem: "No Zaps found"**

**Lösung:**
```bash
# Möglicherweise filtert das Script zu streng
# Alle Zaps werden aber trotzdem in der Liste angezeigt
# Prüfe die vollständige Liste im Output
```

### **Problem: "No Filter steps found"**

**Lösung:**
```bash
# Zapier API gibt nicht immer alle Step-Details zurück
# Das ist NORMAL bei der Zapier API
# Du musst trotzdem manuell in der UI prüfen!
```

## 📝 BEKANNTE LIMITATIONEN

1. **Filter-Conditions nicht lesbar:**
   - Zapier API gibt Filter-Steps zurück
   - Aber NICHT die einzelnen Conditions
   - Daher: Manuelles Audit zwingend erforderlich

2. **Step-Details manchmal leer:**
   - Manche Zaps geben keine Step-Details zurück
   - Das ist eine Zapier API Limitation
   - Trotzdem in UI prüfen!

3. **Keine automatische Änderung möglich:**
   - Zapier API erlaubt KEIN Editieren von Filter-Conditions
   - Alle Änderungen müssen über die UI gemacht werden

## 🎯 ZUSAMMENFASSUNG

**Was das Script KANN:**
- ✅ Alle Zaps auflisten
- ✅ Zaps mit Filter-Steps identifizieren
- ✅ Report erstellen welche Zaps zu prüfen sind
- ✅ Checkliste für manuelle Fixes

**Was das Script NICHT KANN:**
- ❌ Filter-Conditions lesen (API-Limitation)
- ❌ "Does not start with" automatisch erkennen
- ❌ Filter-Conditions automatisch ändern
- ❌ Zaps automatisch fixen

**Fazit:**
Das Script **spart Zeit** bei der Identifikation, aber **manuelle UI-Änderungen sind zwingend erforderlich**.

---

**Erstellt:** 22. Oktober 2025  
**Version:** 1.0  
**Für:** Zapier Filter Audit - "Does not start with" → "Does not contain" Fix  
