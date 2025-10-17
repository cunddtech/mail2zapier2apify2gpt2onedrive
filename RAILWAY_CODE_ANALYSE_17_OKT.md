# Railway Code Analyse - 17. Oktober 2025

## ✅ BEREITS VORHANDEN

### 1. Document Type Classification
**Zeile 1435-1480 in production_langgraph_orchestrator.py:**
```python
"document_type": "invoice|offer|order_confirmation|delivery_note|general"
```

✅ **5 Dokumenttypen werden bereits klassifiziert:**
- `invoice` - Rechnung, Invoice, RE:
- `offer` - Angebot, Quote, Offer
- `order_confirmation` - Auftragsbestätigung, AB:, Order Confirmation
- `delivery_note` - Aufmaß, Lieferschein, Delivery Note
- `general` - Allgemeine Anfrage

### 2. Intelligent Attachment Processing
**Zeile 2700-2850:**
```python
async def process_attachments_intelligent(
    attachments, message_id, user_email, access_token, subject
)
```

✅ **Subject-basierte Klassifikation:**
- Klassifiziert Dokumenttyp aus Betreff
- Wählt OCR-Route basierend auf Typ:
  - `invoice` → PDF.co Invoice Parser
  - `delivery_note` → Handwriting OCR
  - `offer/order` → Standard OCR

### 3. Email Direction Detection
**Zeile 2631-2700:**
```python
data["email_direction"] = "incoming"  # /webhook/ai-email/incoming
data["email_direction"] = "outgoing"  # /webhook/ai-email/outgoing
```

✅ **Incoming/Outgoing bereits getrennt**

### 4. Folder Logic Module (Original Apify)
**modules/filegen/folder_logic.py:**

✅ **Ordnerstruktur-Generierung bereits vorhanden:**
```python
if dokumenttyp in ["rechnung", "eingangsrechnung"]:
    ordnerstruktur = f"Scan/Buchhaltung/{jahr}/{monat}/Eingang/{lieferant}"
elif dokumenttyp in ["ausgangsrechnung"]:
    ordnerstruktur = f"Scan/Buchhaltung/{jahr}/{monat}/Ausgang/{kunde}"
elif projekt != "unbekannt" and kunde != "unbekannt":
    ordnerstruktur = f"Scan/Projekte/{kunde}/{projekt}/{dokumenttyp.title()}"
```

✅ **Rechnungen werden automatisch in Buchhaltung abgelegt!**

### 5. GPT Prompts (Original Apify)

**modules/gpt/prompts/analyse_scan_prompt.py:**
- ✅ Detaillierte Dokumenttyp-Klassifikation
- ✅ Richtungs-Erkennung (Eingang/Ausgang, Kunde/Lieferant)
- ✅ Ordnerstruktur-Vorschlag
- ✅ Dateinamen-Generierung

**modules/gpt/prompts/analyse_mail_prompt.py:**
- ✅ Sales Phases Integration
- ✅ Buchhaltung-Ordnerstruktur
- ✅ Projekt-Ordnerstruktur
- ✅ "Zu prüfen" Fallback

---

## ❌ FEHLT NOCH

### 1. `document_type_hint` Parameter-Support
**Zeile 2631:** `/webhook/ai-email/incoming` akzeptiert **KEINEN** `document_type_hint` Parameter!

```python
# AKTUELL:
data = await request.json()
# message_id, user_email werden ausgelesen
# ABER: document_type_hint wird NICHT ausgelesen!
```

**BENÖTIGT:**
```python
data = await request.json()
document_type_hint = data.get("document_type_hint")  # Von Zapier
priority = data.get("priority", "medium")  # Von Zapier

# Fast-Path bei klarem Hint:
if document_type_hint in ["invoice", "offer", "order_confirmation", "delivery_note"]:
    # Überspringen: Subject-basierte Klassifikation
    # Direkt verwenden: document_type_hint
```

### 2. Original Apify Prompts NICHT im Railway verwendet
**Problem:** Railway verwendet EIGENE Prompts (Zeile 1435), NICHT die ausgereiften Apify Prompts!

**Apify Prompts (modules/gpt/prompts/):**
- ✅ `analyse_scan_prompt.py` - 200 Zeilen, sehr detailliert
- ✅ `analyse_mail_prompt.py` - Sales Phases, Ordnerstruktur
- ✅ `precheck_email_prompt.py` - Relevanz-Check

**Railway Prompts (inline in Zeile 1435):**
- ❌ Nur ~30 Zeilen
- ❌ Keine Ordnerstruktur-Generierung
- ❌ Keine detaillierte Dokumenttyp-Differenzierung
- ❌ Keine Sales Phases
- ❌ Keine "Buchhaltung" Logik

### 3. Ordnerstruktur wird NICHT verwendet
**Problem:** `folder_logic.py` existiert, wird aber **NICHT** im Railway Code aufgerufen!

```python
# EXISTIERT in modules/filegen/folder_logic.py:
def generate_folder_and_filenames(context, gpt_result, attachments):
    if dokumenttyp in ["rechnung", "eingangsrechnung"]:
        ordnerstruktur = f"Scan/Buchhaltung/{jahr}/{monat}/Eingang/{lieferant}"
```

**ABER:** Railway Code (production_langgraph_orchestrator.py) ruft diese Funktion **NIRGENDS** auf!

### 4. OneDrive Upload fehlt
**Problem:** Keine Integration von `modules/upload/upload_file_to_drive.py`

Railway verarbeitet Emails, aber:
- ❌ Speichert PDFs NICHT auf OneDrive
- ❌ Generiert KEINE Ordnerstruktur
- ❌ Verschiebt NICHTS nach "Scan/Buchhaltung/..."

### 5. Classify Document Module wird nicht verwendet
**Problem:** `modules/gpt/classify_document_with_gpt.py` existiert, wird aber nicht genutzt

Railway verwendet **inline GPT-Calls** (Zeile 1435), NICHT die modularisierten Apify-Funktionen.

---

## 🎯 BENÖTIGTE ANPASSUNGEN

### 1. `document_type_hint` Support hinzufügen
**Datei:** `production_langgraph_orchestrator.py`
**Zeile:** 2631-2700

```python
@app.post("/webhook/ai-email/incoming")
async def process_email_incoming(request: Request):
    try:
        data = await request.json()
        data["email_direction"] = "incoming"
        
        # NEU: document_type_hint auslesen
        document_type_hint = data.get("document_type_hint")
        priority = data.get("priority", "medium")
        
        logger.info(f"📧 Email incoming: hint={document_type_hint}, priority={priority}")
        
        # An background task weitergeben
        asyncio.create_task(process_email_background(
            data, message_id, user_email, 
            document_type_hint=document_type_hint  # NEU
        ))
```

### 2. Original Apify Prompts integrieren
**Datei:** `production_langgraph_orchestrator.py`
**Zeile:** 1435

```python
# STATT inline Prompt:
from modules.gpt.prompts.analyse_mail_prompt import build_analyse_mail_prompt
from modules.gpt.prompts.analyse_scan_prompt import build_analyse_scan_prompt

# Email mit Anhang:
if attachment_results:
    ocr_text = "\n\n".join([att.get("ocr_text", "") for att in attachment_results])
    prompt = build_analyse_scan_prompt(
        ocr_text=ocr_text,
        handwriting_text="",
        metadata={"subject": subject, "from": from_contact}
    )
else:
    # Email ohne Anhang:
    prompt = build_analyse_mail_prompt(
        body_text=content,
        metadata={"subject": subject},
        ocr_text="",
        attachments=[]
    )
```

### 3. Ordnerstruktur-Generierung einbinden
**Datei:** `production_langgraph_orchestrator.py`
**Zeile:** Nach AI Analysis (~1500)

```python
from modules.filegen.folder_logic import generate_folder_and_filenames

# Nach GPT-Analyse:
gpt_result = {...}  # AI Analysis Ergebnis
context = {
    "dokumenttyp": gpt_result.get("document_type"),
    "kunde": ai_analysis.get("customer_name"),
    ...
}

# Ordnerstruktur generieren:
folder_info = generate_folder_and_filenames(
    context=context,
    gpt_result=gpt_result,
    attachments=attachment_results
)

logger.info(f"📂 Zielordner: {folder_info['ordnerstruktur']}")
logger.info(f"📄 Dateinamen: {folder_info['pdf_filenames']}")
```

### 4. OneDrive Upload integrieren
**Datei:** `production_langgraph_orchestrator.py`
**Nach:** Ordnerstruktur-Generierung

```python
from modules.upload.upload_file_to_drive import upload_file_to_drive

# Für jeden Anhang:
for i, att_result in enumerate(attachment_results):
    file_bytes = att_result.get("file_bytes")  # Muss gespeichert werden!
    filename = folder_info["pdf_filenames"][i]
    folder_path = folder_info["ordnerstruktur"]
    
    # Upload zu OneDrive:
    public_link = upload_file_to_drive(
        access_token=access_token,
        file_bytes=file_bytes,
        folder_path=folder_path,
        filename=filename
    )
    
    logger.info(f"☁️ OneDrive: {public_link}")
```

### 5. Classify Document Module verwenden
**Datei:** `production_langgraph_orchestrator.py`
**Zeile:** 1435 (AI Analysis)

```python
from modules.gpt.classify_document_with_gpt import classify_document_with_gpt

# STATT inline GPT-Call:
if attachment_results:
    ocr_text = "\n\n".join([att.get("ocr_text", "") for att in attachment_results])
    gpt_result = classify_document_with_gpt(
        ocr_text=ocr_text,
        handwriting_text="",
        metadata={"subject": subject, "from": from_contact}
    )
```

---

## 📋 ZUSAMMENFASSUNG

### ✅ BEREITS VORHANDEN (Railway Code):
1. ✅ Document Type Classification (5 Typen)
2. ✅ Intelligent Attachment Processing (Subject-based)
3. ✅ Email Direction (incoming/outgoing)
4. ✅ OCR Integration (PDF.co)
5. ✅ Contact Matching (WeClapp)

### ✅ BEREITS VORHANDEN (Apify Module, aber NICHT verwendet):
1. ✅ `folder_logic.py` - Ordnerstruktur "Scan/Buchhaltung/..."
2. ✅ `analyse_scan_prompt.py` - Detaillierte GPT-Analyse
3. ✅ `analyse_mail_prompt.py` - Sales Phases, Ordnerstruktur
4. ✅ `classify_document_with_gpt.py` - Modulare Klassifikation
5. ✅ `upload_file_to_drive.py` - OneDrive Upload

### ❌ FEHLT / MUSS INTEGRIERT WERDEN:
1. ❌ `document_type_hint` Parameter von Zapier auslesen
2. ❌ Original Apify Prompts verwenden (statt inline)
3. ❌ `folder_logic.generate_folder_and_filenames()` aufrufen
4. ❌ OneDrive Upload nach "Scan/Buchhaltung/..." aktivieren
5. ❌ `classify_document_with_gpt()` verwenden (statt inline)

---

## 🎯 NÄCHSTE SCHRITTE

### Phase 1: `document_type_hint` Support (5 Minuten)
```python
# Zeile 2631:
document_type_hint = data.get("document_type_hint")
priority = data.get("priority", "medium")

# Zeile 2935:
async def process_email_background(..., document_type_hint=None):
    if document_type_hint:
        logger.info(f"🎯 Fast-Path: {document_type_hint} (von Zapier)")
```

### Phase 2: Apify Prompts integrieren (15 Minuten)
```python
from modules.gpt.prompts.analyse_scan_prompt import build_analyse_scan_prompt
from modules.gpt.prompts.analyse_mail_prompt import build_analyse_mail_prompt
```

### Phase 3: Ordnerstruktur aktivieren (10 Minuten)
```python
from modules.filegen.folder_logic import generate_folder_and_filenames
folder_info = generate_folder_and_filenames(context, gpt_result, attachments)
```

### Phase 4: OneDrive Upload aktivieren (20 Minuten)
```python
from modules.upload.upload_file_to_drive import upload_file_to_drive
public_link = upload_file_to_drive(access_token, file_bytes, folder_path, filename)
```

### Phase 5: Modulare Klassifikation (10 Minuten)
```python
from modules.gpt.classify_document_with_gpt import classify_document_with_gpt
gpt_result = classify_document_with_gpt(ocr_text, handwriting_text, metadata)
```

**TOTAL: ~60 Minuten Entwicklungszeit**

---

## ⚡ KRITISCHE ERKENNTNIS

**Die LOGIK ist bereits da, wird aber NICHT verwendet!**

- ✅ `folder_logic.py` existiert → Rechnungen → `Scan/Buchhaltung/{jahr}/{monat}/Eingang/{lieferant}`
- ✅ `analyse_scan_prompt.py` existiert → Detaillierte Dokumenttyp-Klassifikation
- ✅ `upload_file_to_drive.py` existiert → OneDrive Upload

**Problem:** Railway Code (production_langgraph_orchestrator.py) **importiert diese Module NICHT**!

**Lösung:** Imports hinzufügen + Funktionen aufrufen = **FERTIG**!
