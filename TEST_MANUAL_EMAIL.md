# 📧 MANUELLE TEST EMAIL

## 🎯 Bitte sende diese Email MANUELL

**Von:** Deine persönliche Email (NICHT mj@cdtechnologies.de!)  
**An:** info@cdtechnologies.de  
**Betreff:** `Auftragserteilung - Dachausbau Hamburg`

⚠️ **WICHTIG:** KEIN "TEST:" im Subject - sonst filtert Zapier die Email raus!

**Text:**
```
Guten Tag,

hiermit erteile ich Ihnen den Auftrag für den Dachausbau wie besprochen.

Bitte bestellen Sie das Material beim Lieferanten und schicken Sie mir die Auftragsbestätigung.

Wann können wir die Montage terminieren?

Mit freundlichen Grüßen
Max Mustermann
max.mustermann.test2025@gmail.com
```

---

## ✅ WAS GETESTET WIRD

### 1️⃣ INTENT OVERRIDE
**Erwartung:** Keyword "Auftrag" im Subject triggert ORDER Intent
```
🎯 INTENT OVERRIDE: Detected ORDER keywords in subject/body, forcing ORDER intent
```

### 2️⃣ WECLAPP OPPORTUNITY STATUS QUERY
**Erwartung:** System fragt WeClapp Opportunity Status ab
```
📊 Opportunity Status: ID=..., Stage=Order, Probability=80%
```

### 3️⃣ STAGE-BASED SMART ACTIONS
**Erwartung:** 5 ORDER-spezifische Smart Actions
- 📋 AUFTRAG ANLEGEN
- 📦 LIEFERANT BESTELLEN  
- 📄 AB VERSENDEN
- 💰 ANZAHLUNGSRECHNUNG
- 📅 MONTAGE TERMINIEREN

### 4️⃣ EMAIL NOTIFICATION
**Erwartung:** Email an mj@cdtechnologies.de mit grünem Header (WEG B)

---

## 🔍 LOGS ÜBERPRÜFEN

Nach dem Senden (warte 30-60 Sekunden):

```bash
railway logs --tail 200 | grep -E "INTENT OVERRIDE|Opportunity Status|stage-based smart actions|ORDER|Party ID"
```

**Erwartete Logs:**
```
🎯 INTENT OVERRIDE: Detected ORDER keywords
📊 Opportunity Status: ID=123, Stage=Order, Probability=80%
✅ Using 5 stage-based smart actions for: Order
```

---

## ⚠️ WICHTIG

- **NICHT** von mj@cdtechnologies.de senden (Loop Filter!)
- **NICHT** "C&D AI" im Subject verwenden
- Warte 30-60 Sekunden nach dem Senden
- Prüfe Railway logs UND Email inbox

---

## 📊 SUCCESS CRITERIA

✅ Email wird empfangen (nicht von Loop Filter geblockt)  
✅ INTENT OVERRIDE aktiviert (Keyword "Auftrag")  
✅ WeClapp API Query erfolgreich  
✅ Opportunity Status gelesen  
✅ 5 ORDER Smart Actions generiert  
✅ Email Notification mit grünem WEG B Header  
✅ Keine Duplikat-Buttons
