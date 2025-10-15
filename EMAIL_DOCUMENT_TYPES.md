# 📧 EMAIL & DOKUMENT TYPEN - ANALYSE MATRIX

## 🎯 DOKUMENTTYPEN

### **1. RECHNUNGEN (Invoices)**
- **MIT Anhang:** PDF-Rechnung → OCR Invoice Parser → WeClapp Payment Due Event
- **OHNE Anhang:** Email-Text mit Betrag → GPT-4 Extraktion → WeClapp Note
- **Schlagwörter:** "Rechnung", "Invoice", "RE:", "Betrag", "Zahlung", "fällig"
- **CRM-Aktion:** Payment Tracking, Fälligkeitsdatum

### **2. ANGEBOTE (Offers/Quotes)**
- **MIT Anhang:** PDF-Angebot → OCR Standard → Angebotsnummer extrahieren
- **OHNE Anhang:** Richtpreise im Email-Text → GPT-4 → WeClapp Opportunity
- **Schlagwörter:** "Angebot", "Offer", "Quote", "Preisanfrage", "Richtpreis"
- **CRM-Aktion:** Follow-up Task (7 Tage), Opportunity Status

### **3. AUFTRAGSBESTÄTIGUNGEN (Order Confirmations)**
- **MIT Anhang:** PDF-AB → OCR Standard → Auftragsnummer + Datum extrahieren
- **OHNE Anhang:** Email-Text mit Auftragsnummer → GPT-4 → WeClapp Order Event
- **Schlagwörter:** "Auftragsbestätigung", "AB:", "Order Confirmation", "Auftrag"
- **CRM-Aktion:** Order Confirmed, Liefer-Reminder Task

### **4. AUFMASS (Measurement/Delivery Notes)**
- **MIT Anhang:** PDF-Aufmaß/Lieferschein → OCR Handwriting → Mengen/Notizen
- **OHNE Anhang:** Mengenangaben im Email-Text → GPT-4 → WeClapp Delivery Note
- **Schlagwörter:** "Aufmaß", "Lieferschein", "Delivery Note", "Measurement"
- **CRM-Aktion:** Delivery Tracking, Invoice Generation Task

### **5. ALLGEMEINE ANFRAGEN**
- **Immer OHNE Anhang:** Fragen, Terminanfragen, Info-Requests
- **Schlagwörter:** "Anfrage", "Frage", "Termin", "Information"
- **CRM-Aktion:** Response Task (24h)

---

## 🔄 RICHTUNG: EIN- vs. AUSGEHEND

### **AKTUELLER STATUS:**
❌ Nur EINGEHENDE Mails werden verarbeitet (Zapier Trigger: "New Email in Folder")

### **PROBLEM:**
- ✅ Eingehende Rechnung von Lieferant → erkannt
- ❌ Ausgehende Rechnung an Kunde → NICHT erkannt
- ❌ Ausgehende Angebote → NICHT erfasst
- ❌ Ausgehende Auftragsbestätigungen → NICHT geloggt

### **LÖSUNG - ZWEI VERSCHIEDENE FLOWS:**

#### **📥 EINGEHENDE MAILS (von Kunden/Lieferanten an uns):**
```
Zapier: "New Email in Inbox"
  ↓
Filter: Folder = "Inbox" oder spezifische Label
  ↓
Webhook → /webhook/ai-email/incoming/{type}
  ↓
CRM-Aktion: Kundenkontakt aktualisieren, Task erstellen
```

#### **📤 AUSGEHENDE MAILS (von uns an Kunden/Lieferanten):**
```
Zapier: "New Email in Sent Items"
  ↓
Filter: Folder = "Sent Items"
  ↓
Webhook → /webhook/ai-email/outgoing/{type}
  ↓
CRM-Aktion: Verkaufsprozess tracken, Opportunity Update
```

---

## 🎯 EMPFOHLENE ZAPIER-STRUKTUR

### **VARIANTE A: VIELE SPEZIFISCHE ZAPS (präzise)**

```
📥 EINGEHEND:
├─ Zap 1: Eingehende Rechnungen (mit Anhang)
│   Filter: Inbox + (Betreff enthält "Rechnung|RE:|Invoice") + Has Attachment
│   → /webhook/ai-email/incoming/invoice-attachment
│
├─ Zap 2: Eingehende Rechnungen (ohne Anhang - Textform)
│   Filter: Inbox + (Betreff enthält "Rechnung|Betrag") + No Attachment
│   → /webhook/ai-email/incoming/invoice-text
│
├─ Zap 3: Eingehende Angebote (mit Anhang)
│   Filter: Inbox + (Betreff enthält "Angebot|Offer") + Has Attachment
│   → /webhook/ai-email/incoming/offer-attachment
│
├─ Zap 4: Eingehende Angebote (ohne Anhang - Richtpreise)
│   Filter: Inbox + (Betreff enthält "Angebot|Preis") + No Attachment
│   → /webhook/ai-email/incoming/offer-text
│
├─ Zap 5: Eingehende Auftragsbestätigungen
│   Filter: Inbox + (Betreff enthält "Auftragsbestätigung|AB:|Order")
│   → /webhook/ai-email/incoming/order-confirmation
│
├─ Zap 6: Eingehende Aufmaß/Lieferscheine
│   Filter: Inbox + (Betreff enthält "Aufmaß|Lieferschein|Delivery")
│   → /webhook/ai-email/incoming/delivery
│
└─ Zap 7: Allgemeine eingehende Anfragen
    Filter: Inbox + (nicht von oben erfasst)
    → /webhook/ai-email/incoming/general

📤 AUSGEHEND:
├─ Zap 8: Ausgehende Rechnungen
│   Filter: Sent Items + (Betreff enthält "Rechnung|RE:")
│   → /webhook/ai-email/outgoing/invoice
│
├─ Zap 9: Ausgehende Angebote
│   Filter: Sent Items + (Betreff enthält "Angebot|Offer")
│   → /webhook/ai-email/outgoing/offer
│
├─ Zap 10: Ausgehende Auftragsbestätigungen
│   Filter: Sent Items + (Betreff enthält "Auftragsbestätigung|AB:")
│   → /webhook/ai-email/outgoing/order-confirmation
│
└─ Zap 11: Ausgehende Aufmaß/Lieferscheine
    Filter: Sent Items + (Betreff enthält "Aufmaß|Lieferschein")
    → /webhook/ai-email/outgoing/delivery
```

**VORTEILE:**
- ✅ Maximale Präzision
- ✅ Orchestrator weiß sofort, was zu tun ist
- ✅ Verschiedene OCR-Routen je nach Typ
- ✅ Verschiedene GPT-Prompts optimiert für Typ

**NACHTEILE:**
- ⚠️ 11 Zaps = mehr Management
- ⚠️ Zapier-Kosten (bei Task-Limits)

---

### **VARIANTE B: WENIGER ZAPS + INTELLIGENTE KLASSIFIKATION**

```
📥 EINGEHEND:
├─ Zap 1: Alle eingehenden Mails mit Anhang
│   Filter: Inbox + Has Attachment
│   → /webhook/ai-email/incoming
│
└─ Zap 2: Alle eingehenden Mails ohne Anhang
    Filter: Inbox + No Attachment
    → /webhook/ai-email/incoming

📤 AUSGEHEND:
├─ Zap 3: Alle ausgehenden Mails mit Anhang
│   Filter: Sent Items + Has Attachment
│   → /webhook/ai-email/outgoing
│
└─ Zap 4: Alle ausgehenden Mails ohne Anhang
    Filter: Sent Items + No Attachment
    → /webhook/ai-email/outgoing
```

**Dann im Orchestrator:**
```python
# GPT-4 klassifiziert den Typ anhand:
# - Betreff
# - Email-Text
# - Anhang-Dateinamen (wenn vorhanden)
# - Absender-Kontext

document_type = await classify_email_with_gpt(subject, body, attachments)
# → "invoice", "offer", "order_confirmation", "delivery", "general"
```

**VORTEILE:**
- ✅ Nur 4 Zaps statt 11
- ✅ Flexibler (neue Typen ohne Zap-Änderung)
- ✅ GPT-4 ist sehr gut in Klassifikation

**NACHTEILE:**
- ⚠️ Etwas mehr GPT-Kosten
- ⚠️ Fehlerrate bei unklaren Emails

---

## 🎯 MEINE EMPFEHLUNG: HYBRID-ANSATZ

```
ZAPIER (EINFACH):
├─ Zap 1: Eingehende Mails → /webhook/ai-email/incoming
└─ Zap 2: Ausgehende Mails → /webhook/ai-email/outgoing

ORCHESTRATOR (INTELLIGENT):
├─ 1. GPT-4 Klassifikation (Typ + Dringlichkeit)
├─ 2. Attachment-Analyse (wenn vorhanden)
├─ 3. OCR-Route wählen je nach Typ
├─ 4. CRM-Aktion je nach Typ + Richtung
└─ 5. Notification je nach Workflow
```

**WARUM?**
- ✅ Einfache Zapier-Struktur (2 Zaps)
- ✅ Maximale Flexibilität im Orchestrator
- ✅ Ein Ort für alle Business-Logik
- ✅ Einfach zu testen und zu debuggen
- ✅ Neue Typen ohne Zapier-Änderung

