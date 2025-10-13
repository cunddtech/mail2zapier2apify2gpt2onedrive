# 🔧 SIPGATE & MULTI-CONTACT FIXES - TODO MORGEN

## 🚨 **KRITISCHE BUGS ZU FIXEN:**

### **1. SIPGATE: Falsche Telefonnummer wird gesucht**

**Problem:**
```python
# Railway sucht nach "from" oder "caller" in Zapier Payload
phone_number = data.get("from", data.get("caller", ""))
```

**ABER:** SipGate sendet möglicherweise:
- `"from"` = **UNSERE Nummer** (Empfänger, z.B. +49123456mj)
- `"caller"` oder `"callerNumber"` = **Anrufer-Nummer** (Kunde)

**Fix:**
```python
# In production_langgraph_orchestrator.py, Zeile ~1040
# ALT:
phone_number = data.get("from", data.get("caller", ""))

# NEU:
phone_number = (
    data.get("caller", "") or 
    data.get("callerNumber", "") or 
    data.get("from", "")
)
logger.info(f"📞 Extracted phone: {phone_number} from payload: {json.dumps(data, ensure_ascii=False)}")
```

**Test:**
1. Ersten SipGate Call morgen machen
2. Railway Logs prüfen: Welche Nummer wird extrahiert?
3. Zapier Payload loggen: `logger.info(f"SipGate Payload: {data}")`

---

### **2. MULTI-KONTAKT ERKENNUNG**

**Szenarien:**

#### **A. Kunde ruft von neuer Nummer an (aber existiert schon)**
```
Beispiel:
- Frank Zimmer bekannt mit: +49123456789
- Ruft an von neuer Nummer: +49987654321

Railway findet:
- ❌ Keine direkte Treffer für +49987654321
- ✅ Aber Name "Frank Zimmer" existiert in WeClapp

Lösung:
→ WEG_A Notification mit Hinweis: "Möglicher Match: Frank Zimmer (+49123456789)"
→ Button: "KONTAKT ZUORDNEN" (statt "KONTAKT ANLEGEN")
```

#### **B. Email von Mitarbeiter einer bekannten Firma**
```
Beispiel:
- Firma "Müller GmbH" bekannt (ID 4500)
- Email von: neuer.mitarbeiter@mueller-gmbh.de
- Railway findet Firma aber nicht Mitarbeiter

Lösung:
→ WEG_A Notification mit Hinweis: "Firma bekannt: Müller GmbH"
→ Button: "MITARBEITER HINZUFÜGEN" (verknüpft mit Firma)
```

#### **C. Email von anderer Adresse eines bekannten Kontakts**
```
Beispiel:
- Frank Zimmer bekannt mit: frank@zimmer-bedachungen.de
- Email von: f.zimmer@privat.de

Lösung:
→ Fuzzy Matching auf Namen in Subject/Body
→ WEG_A Notification: "Möglicher Match: Frank Zimmer"
→ Button: "EMAIL ZUORDNEN"
```

---

## 🤖 **INTELLIGENTE MATCHING-LOGIK**

### **Phase 1: Direkte Suche (Aktuell)**
```python
# WeClapp Suche:
1. Email: email-eq=kunde@firma.de
2. Phone: phone-eq=+491234567890
```

### **Phase 2: Erweiterte Suche (NEU - Morgen)**
```python
# Wenn kein direkter Match:
1. Domain-Suche (Email):
   - kunde@mueller-gmbh.de → Suche alle @mueller-gmbh.de
   - Zeige Firma "Müller GmbH" als möglichen Match

2. Namens-Fuzzy-Matching:
   - Email: frank.zimmer.neu@gmail.com
   - Body enthält: "Frank Zimmer"
   - → Suche WeClapp nach "Frank" + "Zimmer"

3. Telefon-Prefix-Matching:
   - Neue Nummer: +491234567890
   - Bekannte Kontakte mit ähnlichem Prefix: +491234567***
   - → Zeige als "Mögliche Matches"
```

---

## 📋 **IMPLEMENTATION PLAN (MORGEN):**

### **SCHRITT 1: SipGate Caller Extraction Fix (30 Min)**
```python
# File: production_langgraph_orchestrator.py
# Zeile: ~1040

@app.post("/webhook/ai-call")
async def process_call(request: Request):
    data = await request.json()
    logger.info(f"📞 SipGate Full Payload: {json.dumps(data, ensure_ascii=False)}")
    
    # Extract caller number (NICHT unsere Nummer!)
    caller_number = (
        data.get("caller") or 
        data.get("callerNumber") or 
        data.get("remote") or
        data.get("from")
    )
    
    # Our number (recipient)
    our_number = (
        data.get("to") or 
        data.get("recipient") or 
        data.get("callee")
    )
    
    logger.info(f"📞 Caller: {caller_number}, Our Number: {our_number}")
```

### **SCHRITT 2: Multi-Contact Matching (2 Std)**
```python
# Neue Funktion in AILeadOrchestrator:

async def _fuzzy_contact_search(self, contact_identifier: str) -> List[Dict]:
    """
    Erweiterte Kontakt-Suche wenn kein direkter Match
    
    Returns:
    [
        {
            "match_type": "domain" | "name" | "phone_prefix",
            "confidence": 0.7,
            "contact_id": "4500",
            "contact_name": "Frank Zimmer",
            "company": "Müller GmbH",
            "existing_contact": "+491234567890"
        }
    ]
    """
    
    potential_matches = []
    
    # 1. Domain-basierte Suche (Email)
    if "@" in contact_identifier:
        domain = contact_identifier.split("@")[1]
        # WeClApp: company-domain enthält domain
        # Oder: Alle Kontakte mit @domain.de
    
    # 2. Telefon-Prefix Suche
    if contact_identifier.startswith("+"):
        prefix = contact_identifier[:8]  # z.B. +4912345
        # WeClApp: phone LIKE '+4912345%'
    
    return potential_matches
```

### **SCHRITT 3: WEG_A Notification erweitern (1 Std)**
```python
# In notification_data für WEG_A:

if potential_matches:
    notification_data["potential_matches"] = potential_matches
    notification_data["action_options"].append({
        "action": "assign_to_existing",
        "label": "KONTAKT ZUORDNEN",
        "description": f"Zu existierendem Kontakt zuordnen: {potential_matches[0]['contact_name']}"
    })
```

---

## 📊 **ZAPIER PAYLOAD ANALYSE (MORGEN ZUERST):**

### **Test 1: SipGate Call - Payload loggen**
```bash
# Railway Logs während erstem Call:
railway logs --follow | grep "SipGate"
```

**Prüfen:**
- Welche Fields hat der SipGate Webhook?
- Wo steht die **Anrufer-Nummer**?
- Wo steht **unsere Nummer** (Empfänger)?
- Gibt es `direction` Field? (inbound/outbound)

---

## ✅ **FÜR HEUTE ERLEDIGT:**

1. ✅ Zapier Loop gefixt (Filter aktiv)
2. ✅ Email Processing funktioniert
3. ✅ WeClapp Contact Creation funktioniert (Party-ID 386944)
4. ✅ Unknown Contact Workflow (WEG_A) getestet
5. ✅ SipGate Code vorbereitet (Phone Matching + CRM Log)
6. ✅ Commit 4f5224b deployed

---

## 🎯 **MORGEN FRÜH:**

1. **SipGate Test Call** → Payload analysieren
2. **Caller Extraction Fix** → Richtige Nummer extrahieren
3. **Multi-Contact Matching** → Fuzzy Search implementieren
4. **Test mit echten Szenarien**

---

## 💤 **GUT NACHT & BIS MORGEN!** 🌙

*Dokumentiert: 13. Oktober 2025, 23:55 Uhr*
*Status: Bereit für Testing morgen*
