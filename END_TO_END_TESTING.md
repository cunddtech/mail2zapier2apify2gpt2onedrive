# 🧪 End-to-End Testing Plan

**Date:** 17. Oktober 2025  
**System:** Email → Zapier → Railway → OneDrive → CRM  
**Status:** 🔄 IN PROGRESS

---

## 📋 Test Scenarios Overview

| # | Test | Status | Priority |
|---|------|--------|----------|
| 1 | Eingehende Rechnung (Invoice) | ⏳ PENDING | HIGH |
| 2 | Eingehender Lieferschein (Delivery Note) | ⏳ PENDING | HIGH |
| 3 | Eingehendes Angebot (Offer) | ⏳ PENDING | MEDIUM |
| 4 | Catch-All Dokument | ⏳ PENDING | MEDIUM |
| 5 | Ausgehende Email mit Anhang | ⏳ PENDING | MEDIUM |
| 6 | Duplikat-Erkennung | ⏳ PENDING | HIGH |
| 7 | OneDrive Upload Verifizierung | ⏳ PENDING | HIGH |
| 8 | CRM-Abgleich (Bekannter Kunde) | ⏳ PENDING | HIGH |
| 9 | CRM-Abgleich (Unbekannter Kunde) | ⏳ PENDING | MEDIUM |

---

## 🎯 Test 1: Eingehende Rechnung (Invoice)

### Objective
Prüfen, ob Rechnungen korrekt erkannt, per Invoice Parser OCR verarbeitet und in OneDrive abgelegt werden.

### Setup
- **Trigger:** Senden Sie eine Email mit "Rechnung" im Betreff an `mj@cdtechnologies.de` oder `info@cdtechnologies.de`
- **Attachment:** PDF-Rechnung (z.B. "Rechnung-12345.pdf")
- **Expected Zap:** 🧾 Rechnungen (mj@ oder info@)

### Expected Behavior
1. ✅ Zap triggert → `document_type_hint: "invoice"`
2. ✅ Railway empfängt Request mit `priority: "high"`
3. ✅ OCR Route: Invoice Parser (pdfco)
4. ✅ OneDrive Upload: `Scan/Buchhaltung/2025/Oktober/Eingang/{Lieferant}/Rechnung-12345.pdf`
5. ✅ Database Entry mit `document_type: "invoice"`
6. ✅ User Notification via Zapier

### Verification Steps
```bash
# 1. Check Railway Logs
railway logs --tail 50 | grep -E "document_type_hint.*invoice|Invoice Parser"

# 2. Check OneDrive
# Navigiere zu: OneDrive → Scan → Buchhaltung → 2025 → Oktober → Eingang → {Lieferant}

# 3. Check Database
# Prüfe email_tracking.db für den Eintrag
```

### Test Data
- **Subject:** "Rechnung 2025-001 - Müller GmbH"
- **From:** buchhaltung@mueller-gmbh.de
- **Attachment:** Rechnung-2025-001.pdf

### Result
- [ ] ✅ PASSED
- [ ] ❌ FAILED
- [ ] ⚠️ PARTIAL

**Notes:**
```
[Hier Testergebnisse eintragen]
```

---

## 🎯 Test 2: Eingehender Lieferschein (Delivery Note)

### Objective
Prüfen, ob Lieferscheine mit Handwriting OCR verarbeitet werden.

### Setup
- **Trigger:** Email mit "Lieferschein" oder "Aufmaß" im Betreff
- **Attachment:** PDF mit handschriftlichen Notizen
- **Expected Zap:** 📄 Lieferscheine

### Expected Behavior
1. ✅ Zap triggert → `document_type_hint: "delivery_note"`
2. ✅ Railway empfängt Request
3. ✅ OCR Route: Handwriting OCR (pdfco)
4. ✅ OneDrive Upload: `Scan/Buchhaltung/2025/Oktober/Eingang/{Lieferant}/Lieferschein-XYZ.pdf`
5. ✅ Database Entry mit `document_type: "delivery_note"`

### Verification Steps
```bash
railway logs --tail 50 | grep -E "document_type_hint.*delivery_note|Handwriting OCR"
```

### Test Data
- **Subject:** "Lieferschein LKW-123 mit Aufmaß"
- **From:** bauleitung@schmidt-bau.de
- **Attachment:** Lieferschein-LKW123.pdf

### Result
- [ ] ✅ PASSED
- [ ] ❌ FAILED
- [ ] ⚠️ PARTIAL

**Notes:**
```
[Hier Testergebnisse eintragen]
```

---

## 🎯 Test 3: Eingehendes Angebot (Offer)

### Objective
Prüfen, ob Angebote mit Standard OCR verarbeitet werden.

### Setup
- **Trigger:** Email mit "Angebot" im Betreff
- **Attachment:** PDF-Angebot
- **Expected Zap:** 💼 Angebote

### Expected Behavior
1. ✅ Zap triggert → `document_type_hint: "offer"`
2. ✅ Railway empfängt Request
3. ✅ OCR Route: Standard OCR (pdfco)
4. ✅ OneDrive Upload: `Scan/Buchhaltung/2025/Oktober/Eingang/{Lieferant}/Angebot-ABC.pdf`
5. ✅ Database Entry mit `document_type: "offer"`

### Verification Steps
```bash
railway logs --tail 50 | grep -E "document_type_hint.*offer|Standard OCR"
```

### Test Data
- **Subject:** "Angebot für Projekt Neubau Halle 5"
- **From:** vertrieb@stahlbau-gmbh.de
- **Attachment:** Angebot-2025-456.pdf

### Result
- [ ] ✅ PASSED
- [ ] ❌ FAILED
- [ ] ⚠️ PARTIAL

**Notes:**
```
[Hier Testergebnisse eintragen]
```

---

## 🎯 Test 4: Catch-All Dokument

### Objective
Prüfen, ob unklare Dokumente von GPT klassifiziert werden.

### Setup
- **Trigger:** Email mit Anhang OHNE spezielle Keywords (Rechnung/Lieferschein/Angebot)
- **Attachment:** PDF (z.B. Vertrag, Bestellung, etc.)
- **Expected Zap:** 📬 Catch-All

### Expected Behavior
1. ✅ Zap triggert → `document_type_hint: ""` (leer!)
2. ✅ Railway empfängt Request
3. ✅ GPT klassifiziert Dokumententyp
4. ✅ OCR Route basierend auf GPT-Entscheidung
5. ✅ OneDrive Upload mit GPT-klassifiziertem Typ

### Verification Steps
```bash
railway logs --tail 50 | grep -E "GPT classif|AI analyzing"
```

### Test Data
- **Subject:** "Vertragsunterlagen Projekt XYZ"
- **From:** kunde@example.com
- **Attachment:** Vertrag-2025.pdf

### Result
- [ ] ✅ PASSED
- [ ] ❌ FAILED
- [ ] ⚠️ PARTIAL

**Notes:**
```
[Hier Testergebnisse eintragen]
```

---

## 🎯 Test 5: Ausgehende Email mit Anhang

### Objective
Prüfen, ob ausgehende E-Mails korrekt verarbeitet und im CRM abgelegt werden.

### Setup
- **Trigger:** Senden Sie eine Email VON `mj@cdtechnologies.de` oder `info@cdtechnologies.de`
- **To:** test-kunde@example.com
- **Subject:** "Angebot für Ihre Anfrage"
- **Attachment:** PDF-Angebot
- **Expected Zap:** 📤 Outgoing

### Expected Behavior
1. ✅ Zap triggert → `email_direction: "outgoing"`
2. ✅ Railway empfängt Request
3. ✅ GPT klassifiziert: "Angebot"
4. ✅ CRM-Abgleich: Empfänger bekannt?
5. ✅ OneDrive Upload: `Scan/Buchhaltung/2025/Oktober/Ausgang/{Empfänger}/Angebot-XYZ.pdf`
6. ✅ CRM-Eintrag erstellt (falls nicht vorhanden)

### Verification Steps
```bash
railway logs --tail 50 | grep -E "outgoing|CRM.*abgleich|Ausgang"
```

### Test Data
- **From:** mj@cdtechnologies.de
- **To:** max.mustermann@test-firma.de
- **Subject:** "Angebot Nr. 2025-789"
- **Attachment:** Angebot-2025-789.pdf

### Result
- [ ] ✅ PASSED
- [ ] ❌ FAILED
- [ ] ⚠️ PARTIAL

**Notes:**
```
[Hier Testergebnisse eintragen]
```

---

## 🎯 Test 6: Duplikat-Erkennung

### Objective
Prüfen, ob dieselbe Email/Attachment 2x gesendet wird und als Duplikat erkannt wird.

### Setup
1. Senden Sie eine Email mit Anhang
2. Warten Sie auf Verarbeitung
3. Senden Sie **dieselbe** Email nochmal (Forward)

### Expected Behavior
1. ✅ Erste Email: Normal verarbeitet → OneDrive Upload
2. ✅ Zweite Email: Als Duplikat erkannt → **KEIN** zweiter Upload
3. ✅ Database: `is_duplicate: true` für zweite Email
4. ✅ User Notification: "Duplikat erkannt - bereits vorhanden"

### Verification Steps
```bash
railway logs --tail 100 | grep -E "Duplikat|duplicate|hash.*exists"
```

### Test Data
- **Email 1:** "Rechnung Test-123.pdf" (20:00 Uhr)
- **Email 2:** "Rechnung Test-123.pdf" (20:05 Uhr, gleicher Anhang!)

### Result
- [ ] ✅ PASSED
- [ ] ❌ FAILED
- [ ] ⚠️ PARTIAL

**Notes:**
```
[Hier Testergebnisse eintragen]
```

---

## 🎯 Test 7: OneDrive Upload Verifizierung

### Objective
Manuell prüfen, ob alle Uploads in der richtigen Ordnerstruktur landen.

### Verification Steps
1. Öffnen Sie OneDrive im Browser
2. Navigieren Sie zu: `Scan/Buchhaltung/2025/Oktober/`
3. Prüfen Sie:
   - ✅ Ordner `Eingang/` existiert
   - ✅ Ordner `Ausgang/` existiert
   - ✅ Unterordner nach Lieferant/Empfänger erstellt
   - ✅ PDFs korrekt benannt
   - ✅ Keine Duplikate vorhanden

### Expected Structure
```
Scan/
└── Buchhaltung/
    └── 2025/
        └── Oktober/
            ├── Eingang/
            │   ├── Müller GmbH/
            │   │   └── Rechnung-2025-001.pdf
            │   ├── Schmidt Bau/
            │   │   └── Lieferschein-LKW123.pdf
            │   └── Stahlbau GmbH/
            │       └── Angebot-2025-456.pdf
            └── Ausgang/
                └── Test Firma/
                    └── Angebot-2025-789.pdf
```

### Result
- [ ] ✅ PASSED
- [ ] ❌ FAILED
- [ ] ⚠️ PARTIAL

**Notes:**
```
[Hier OneDrive-Screenshots oder Notizen einfügen]
```

---

## 🎯 Test 8: CRM-Abgleich (Bekannter Kunde)

### Objective
Prüfen, ob bekannte Kunden im CRM gefunden werden.

### Setup
- **Prerequisite:** Kunde muss in WeClapp CRM existieren
- **Test Email:** Von bekannter Email-Adresse
- **Expected:** Contact Match = TRUE

### Expected Behavior
1. ✅ Railway ruft WeClapp API auf
2. ✅ Contact Match: TRUE
3. ✅ Workflow: WEG B (Bekannter Kunde)
4. ✅ CRM-Daten werden geladen
5. ✅ Dokument wird CRM-Kontakt zugeordnet

### Verification Steps
```bash
railway logs --tail 50 | grep -E "Contact match.*True|WEG B|bekannt"
```

### Test Data
- **From:** Eine Email-Adresse, die in WeClapp CRM existiert
- **Subject:** "Test - Bekannter Kunde"
- **Attachment:** Test.pdf

### Result
- [ ] ✅ PASSED
- [ ] ❌ FAILED
- [ ] ⚠️ PARTIAL

**Notes:**
```
[Hier Testergebnisse eintragen]
```

---

## 🎯 Test 9: CRM-Abgleich (Unbekannter Kunde)

### Objective
Prüfen, ob unbekannte Kontakte erkannt werden und temporärer CRM-Eintrag erstellt wird.

### Setup
- **Test Email:** Von NEUER, unbekannter Email-Adresse
- **Expected:** Contact Match = FALSE

### Expected Behavior
1. ✅ Railway ruft WeClapp API auf
2. ✅ Contact Match: FALSE
3. ✅ Workflow: WEG A (Unbekannter Kontakt)
4. ✅ Temporärer CRM-Eintrag erstellt
5. ✅ User Notification: "Neue Kontakt-Email von XYZ"

### Verification Steps
```bash
railway logs --tail 50 | grep -E "Contact match.*False|WEG A|unknown|unbekannt"
```

### Test Data
- **From:** new-contact-test-12345@example.com (NICHT in CRM!)
- **Subject:** "Test - Neuer Kontakt"
- **Attachment:** Test.pdf

### Result
- [ ] ✅ PASSED
- [ ] ❌ FAILED
- [ ] ⚠️ PARTIAL

**Notes:**
```
[Hier Testergebnisse eintragen]
```

---

## 📊 Test Summary

### Overall Results
- **Total Tests:** 9
- **Passed:** 0 ⏳
- **Failed:** 0 ⏳
- **Partial:** 0 ⏳
- **Pending:** 9 ⏳

### Critical Issues
```
[Hier kritische Probleme eintragen]
```

### Minor Issues
```
[Hier kleinere Probleme eintragen]
```

### Improvements Needed
```
[Hier Verbesserungsvorschläge eintragen]
```

---

## 🚀 Next Steps

After testing completion:
1. [ ] Fix critical issues
2. [ ] Address minor issues
3. [ ] Document known limitations
4. [ ] Update deployment documentation
5. [ ] Create user guide
6. [ ] Schedule production rollout

---

**Test Execution Start:** [TBD]  
**Test Execution End:** [TBD]  
**Tester:** CDTechGmbH Team  
**Environment:** Production (Railway)
