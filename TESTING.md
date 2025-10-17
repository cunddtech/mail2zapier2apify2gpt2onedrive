# 🧪 End-to-End Testing Guide

## Testing-Strategie

Nach Railway Deployment und Zapier Setup:
1. **Unit Tests** → Einzelne Komponenten
2. **Integration Tests** → Kompletter Workflow
3. **Production Tests** → Echte Emails

---

## 📋 Test-Szenarien

### ✅ Test 1: Eingehende Rechnung (Standard-Fall)

**Setup:**
1. Erstelle Test-PDF: `Rechnung_TestLieferant_12345.pdf`
2. Sende Email an `mj@cdtechnologies.de`:
   - Subject: "Rechnung 12345 von TestLieferant"
   - Body: "Anbei unsere Rechnung über 1.234,56 EUR"
   - Attachment: PDF mit OCR-lesbarem Text

**Erwartetes Ergebnis:**
- ✅ Zapier triggert (Zap History: Success)
- ✅ Railway empfängt Webhook (Logs: "Processing email...")
- ✅ OCR Route: `invoice_ocr` (PDF.co Invoice Parser)
- ✅ AI extrahiert:
  - Dokumenttyp: "rechnung"
  - Lieferant: "TestLieferant"
  - Summe: "1234.56"
  - Datum: heute
- ✅ Ordnerstruktur: `Scan/Buchhaltung/2025/10/Eingang/TestLieferant/`
- ✅ Dateiname: `Rechnung_TestLieferant_20251017_[UUID].pdf`
- ✅ OneDrive Upload: Datei in korrektem Ordner
- ✅ Tracking DB: Email gespeichert mit `onedrive_path`

**Prüfung:**
```bash
# Railway Logs:
grep "Ordnerstruktur generiert" railway.log
grep "Upload erfolgreich" railway.log
grep "Email saved to tracking DB" railway.log

# OneDrive:
# Öffne: OneDrive/Scan/Buchhaltung/2025/10/Eingang/TestLieferant/
# Sollte neue PDF enthalten
```

---

### ✅ Test 2: Ausgehende Rechnung (Sent Items)

**Setup:**
1. Sende Email VON `mj@cdtechnologies.de` an Kunde:
   - Subject: "Rechnung 98765 - Projekt XYZ"
   - Attachment: Ausgangsrechnung PDF

**Erwartetes Ergebnis:**
- ✅ Zapier triggert (Sent Items Zap)
- ✅ `email_direction = "outgoing"`
- ✅ AI extrahiert:
  - Dokumenttyp: "ausgangsrechnung"
  - Kunde: "[Kunde aus Email]"
- ✅ Ordnerstruktur: `Scan/Buchhaltung/2025/10/Ausgang/{Kunde}/`
- ✅ OneDrive Upload in Ausgang-Ordner

**Prüfung:**
```bash
# Railway Logs:
grep "email_direction.*outgoing" railway.log
grep "Ausgang" railway.log

# OneDrive:
# Öffne: OneDrive/Scan/Buchhaltung/2025/10/Ausgang/
```

---

### ✅ Test 3: Lieferschein mit Handschrift (OCR Route)

**Setup:**
1. Erstelle PDF mit handschriftlichen Notizen
2. Sende Email:
   - Subject: "Lieferschein Baustelle ABC"
   - Attachment: Handschriftlicher Lieferschein

**Erwartetes Ergebnis:**
- ✅ OCR Route: `handwriting_ocr` (PDF.co Handwriting)
- ✅ AI extrahiert Text trotz Handschrift
- ✅ Dokumenttyp: "lieferschein" oder "delivery_note"
- ✅ Ordnerstruktur korrekt

**Prüfung:**
```bash
# Railway Logs:
grep "handwriting_ocr" railway.log
grep "Using PDF.co Handwriting OCR" railway.log
```

---

### ✅ Test 4: Duplikat-Erkennung (3 Stages)

#### **Stage 1: Message ID Duplikat**

**Setup:**
1. Sende Email mit Rechnung
2. Warte auf Verarbeitung (30 Sekunden)
3. Sende EXAKT die gleiche Email nochmal (gleiche Message ID)

**Erwartetes Ergebnis:**
- ✅ 1. Email: Normal verarbeitet
- ✅ 2. Email: Early Exit
- ✅ Logs: "⚠️ DUPLICATE by Message ID"
- ✅ Kein 2. OneDrive Upload
- ✅ Tracking DB: `is_duplicate = True`

#### **Stage 2: Content Hash Duplikat**

**Setup:**
1. Sende Email mit Rechnung
2. Forwarde die Email (neue Message ID, gleicher Content)

**Erwartetes Ergebnis:**
- ✅ Logs: "⚠️ DUPLICATE by Content"
- ✅ Content Hash Match (24h window)
- ✅ Early Exit, kein Upload

#### **Stage 3: File Hash Duplikat**

**Setup:**
1. Sende Email mit PDF
2. Sende neue Email mit GLEICHEM PDF (anderer Betreff)

**Erwartetes Ergebnis:**
- ✅ Message ID + Content Hash verschieden
- ✅ Aber: File Hash identisch
- ✅ Logs: "⚠️ DUPLICATE ATTACHMENT"
- ✅ `att_result["is_duplicate"] = True`

**Prüfung:**
```bash
# Railway Logs:
grep "DUPLICATE" railway.log
grep "duplicate_of_message_id" railway.log

# Tracking DB:
sqlite3 /tmp/email_tracking.db "SELECT message_id, is_duplicate, duplicate_of_message_id FROM processed_emails WHERE is_duplicate = 1"
```

---

### ✅ Test 5: Email ohne Attachment (Filter stoppt)

**Setup:**
1. Sende Email an `mj@cdtechnologies.de`
   - Subject: "Test ohne Anhang"
   - Body: "Nur Text"
   - Attachment: KEINE

**Erwartetes Ergebnis:**
- ✅ Zapier Filter stoppt Zap
- ✅ Zapier History: "Filtered" (gelbes ⚠️)
- ✅ Railway empfängt KEINEN Webhook
- ✅ Keine Verarbeitung

**Prüfung:**
- Zapier Dashboard → Zap History → Sollte "Filtered" zeigen
- Railway Logs: Keine neue Email in Logs

---

### ✅ Test 6: Projekt-Dokument (Ordnerstruktur)

**Setup:**
1. Sende Email mit PDF:
   - Subject: "Projekt XYZ - Angebot für Kunde ABC"
   - Body: Erwähne "Projekt: XYZ-2025"

**Erwartetes Ergebnis:**
- ✅ AI extrahiert:
  - Kunde: "ABC"
  - Projektnummer: "XYZ-2025"
  - Dokumenttyp: "angebot"
- ✅ Ordnerstruktur: `Scan/Projekte/ABC/XYZ-2025/Angebot/`
- ✅ OneDrive Upload in Projekt-Ordner

**Prüfung:**
```bash
# Railway Logs:
grep "Projekte" railway.log

# OneDrive:
# Öffne: OneDrive/Scan/Projekte/
```

---

### ✅ Test 7: Mehrere Attachments

**Setup:**
1. Sende Email mit 3 PDFs:
   - Rechnung.pdf
   - Lieferschein.pdf
   - Angebot.pdf

**Erwartetes Ergebnis:**
- ✅ Alle 3 PDFs werden verarbeitet
- ✅ OCR für jedes PDF
- ✅ 3 separate Dateinamen generiert
- ✅ Alle 3 auf OneDrive hochgeladen
- ✅ Tracking DB: `attachment_count = 3`

**Prüfung:**
```bash
# Railway Logs:
grep "Processing: .*.pdf" railway.log | wc -l
# Sollte 3 zeigen

grep "Upload erfolgreich" railway.log | wc -l
# Sollte 3 zeigen
```

---

### ✅ Test 8: OCR Fehler (Fallback)

**Setup:**
1. Temporär `PDFCO_API_KEY` aus Railway entfernen
2. Sende Email mit PDF

**Erwartetes Ergebnis:**
- ✅ Logs: "⚠️ PDFCO_API_KEY not found"
- ✅ OCR Route: "invoice_placeholder"
- ✅ AI arbeitet mit Placeholder-Text
- ✅ Workflow läuft trotzdem durch
- ✅ Upload funktioniert

**Prüfung:**
```bash
# Railway Logs:
grep "PDFCO_API_KEY not found" railway.log
grep "OCR Placeholder" railway.log
```

---

### ✅ Test 9: Graph API Token Renewal

**Setup:**
1. Warte bis Graph API Token abläuft (1 Stunde)
2. Sende Email

**Erwartetes Ergebnis:**
- ✅ 401 Unauthorized Error
- ✅ Code erneuert Token automatisch
- ✅ Retry funktioniert
- ✅ Email wird verarbeitet

**Prüfung:**
```bash
# Railway Logs:
grep "401" railway.log
grep "Token renewal" railway.log
grep "Retry successful" railway.log
```

---

## 📊 Performance Tests

### Zeitmessung

**Erwartete Processing Times:**
- Email Download: < 2 Sekunden
- OCR (1 PDF): 5-10 Sekunden
- AI Analyse: 3-5 Sekunden
- OneDrive Upload: 2-5 Sekunden
- **Total:** ~15-25 Sekunden pro Email

**Test:**
```bash
# Railway Logs:
grep "processing_time_seconds" railway.log
```

### Concurrent Processing

**Setup:**
1. Sende 5 Emails gleichzeitig
2. Alle mit Attachments

**Erwartetes Ergebnis:**
- ✅ Background Tasks verarbeiten parallel
- ✅ Keine Blocking zwischen Emails
- ✅ Alle 5 erfolgreich verarbeitet

---

## 🔍 Database Checks

### Tracking DB Queries

```bash
# SSH in Railway Container (oder lokal)
sqlite3 /tmp/email_tracking.db

# Alle verarbeiteten Emails
SELECT message_id, from_address, document_type, workflow_path, processing_time_seconds 
FROM processed_emails 
ORDER BY processed_date DESC 
LIMIT 10;

# Duplikate finden
SELECT message_id, is_duplicate, duplicate_of_message_id 
FROM processed_emails 
WHERE is_duplicate = 1;

# OneDrive Upload Status
SELECT message_id, onedrive_uploaded, onedrive_path 
FROM processed_emails 
WHERE onedrive_uploaded = 1;

# Attachments mit OCR Route
SELECT filename, ocr_route, onedrive_path 
FROM email_attachments 
ORDER BY processed_date DESC;

# Statistiken
SELECT 
    COUNT(*) as total_emails,
    SUM(CASE WHEN is_duplicate = 1 THEN 1 ELSE 0 END) as duplicates,
    SUM(CASE WHEN onedrive_uploaded = 1 THEN 1 ELSE 0 END) as uploaded,
    AVG(processing_time_seconds) as avg_processing_time
FROM processed_emails;
```

---

## ✅ Success Criteria

Ein erfolgreicher Test zeigt:

- [x] **Email Processing:** 100% Success Rate
- [x] **OCR Accuracy:** > 90% für Standard-PDFs
- [x] **Duplicate Detection:** 100% für Stage 1 (Message ID)
- [x] **OneDrive Upload:** 100% Success Rate
- [x] **Ordnerstruktur:** Korrekt für alle Dokumenttypen
- [x] **Performance:** < 30 Sekunden pro Email
- [x] **Error Handling:** Graceful Degradation bei Fehlern
- [x] **Database:** Alle Emails tracked

---

## 🚨 Failure Scenarios

### Was tun bei Fehlern?

#### **1. OCR schlägt fehl**
- Check PDF.co Credits
- Check API Key
- Fallback: Placeholder-Text funktioniert

#### **2. OneDrive Upload scheitert**
- Check Graph API Permissions
- Check Token Renewal
- Retry-Logik sollte greifen

#### **3. AI Analyse liefert falsches Ergebnis**
- Check Prompt Quality
- Erwäge Apify Prompt Anpassungen
- Manual Review via `zu_pruefen` Flag

#### **4. Duplikat wird nicht erkannt**
- Check Tracking DB Schema
- Check Hash Calculation
- File Hash sollte immer funktionieren

---

## 📝 Test Report Template

Nach Testing:

```markdown
# Test Report - [Datum]

## Environment
- Railway URL: [URL]
- Zapier Zaps: 2 (Eingang + Ausgang)
- Test Duration: [Zeit]

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| Test 1: Eingehende Rechnung | ✅ PASS | Ordner korrekt |
| Test 2: Ausgehende Rechnung | ✅ PASS | Ausgang/ Ordner |
| Test 3: Handschrift OCR | ✅ PASS | Route korrekt |
| Test 4: Duplikat Stage 1 | ✅ PASS | Early Exit |
| Test 5: Email ohne Attachment | ✅ PASS | Filter stoppt |
| Test 6: Projekt-Dokument | ✅ PASS | Projekte/ Ordner |
| Test 7: Mehrere Attachments | ✅ PASS | Alle 3 uploaded |
| Test 8: OCR Fehler | ✅ PASS | Fallback ok |

## Performance
- Avg Processing Time: 18.3 Sekunden
- Success Rate: 100%
- Duplicate Rate: 0% (alle neu)

## Issues Found
- Keine kritischen Fehler
- [Liste eventuelle Bugs]

## Next Steps
- Production Monitoring aktivieren
- Weekly Database Cleanup
- Performance Optimierung wenn > 100 Emails/Tag
```

---

## 🎯 Production Readiness Checklist

Vor Go-Live:

- [ ] Alle 9 Tests bestanden
- [ ] Railway Environment Variables gesetzt
- [ ] Zapier Zaps aktiviert
- [ ] OneDrive Ordnerstruktur vorbereitet
- [ ] Monitoring Dashboard setup
- [ ] Error Alerting konfiguriert
- [ ] Backup-Strategie definiert
- [ ] Documentation vollständig
- [ ] Team Training abgeschlossen

---

**Ready for Production!** 🚀
