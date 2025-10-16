# 🔍 SYSTEM STABILITY AUDIT

**Datum:** 16. Oktober 2025  
**Version:** 1.4.0-sipgate-pricing  
**Ziel:** Sicherstellen dass alle Workflows fehlerfrei funktionieren

---

## ✅ TEST-CHECKLISTE

### **1. EMAIL WORKFLOWS**

#### **Test 1.1: Email WEG A (Unbekannter Kontakt)**
- [ ] Email mit unbekanntem Sender empfangen
- [ ] GPT-Analyse läuft erfolgreich
- [ ] Contact Matching findet nichts
- [ ] Notification Email wird verschickt
- [ ] Action Buttons funktionieren
- [ ] DB-Eintrag korrekt (workflow_path="WEG_A")

**Test-Command:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-email \
-H "Content-Type: application/json" \
-d '{
  "from": "test-unbekannt-$(date +%s)@example.com",
  "subject": "Test Anfrage",
  "body": "Dies ist ein Test mit unbekanntem Absender",
  "received": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'
```

---

#### **Test 1.2: Email WEG B (Bekannter Kontakt)**
- [ ] Email mit bekanntem Sender (mj@cdtechnologies.de)
- [ ] Contact Matching erfolgreich
- [ ] WeClapp CRM Event erstellt
- [ ] WeClapp Task angelegt
- [ ] Notification Email verschickt
- [ ] DB-Eintrag korrekt (workflow_path="WEG_B")

**Test-Command:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-email \
-H "Content-Type: application/json" \
-d '{
  "from": "mj@cdtechnologies.de",
  "subject": "Test Bekannter Kontakt",
  "body": "Dies ist ein Test mit bekanntem Absender",
  "received": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'
```

---

#### **Test 1.3: Email mit PDF-Attachment (OCR)**
- [ ] Email mit PDF-Rechnung
- [ ] Apify Actor triggered
- [ ] OCR läuft (Invoice Parser)
- [ ] Strukturierte Daten extrahiert
- [ ] OneDrive Upload erfolgreich
- [ ] Attachment-Details in Notification
- [ ] DB attachments Tabelle gefüllt

**Test-Command:**
```bash
# Manuelle Test - PDF hochladen via Zapier
# Oder: Mock-Data mit base64-encoded PDF
```

---

### **2. CALL WORKFLOWS**

#### **Test 2.1: Call WEG A (Unbekannte Nummer)**
- [ ] Anruf von unbekannter Nummer
- [ ] Transcript-Analyse läuft
- [ ] 💰 Richtpreis-Berechnung (wenn Dacharbeiten erwähnt)
- [ ] Contact Matching findet nichts
- [ ] Notification mit Richtpreis verschickt
- [ ] DB-Eintrag mit price_estimate_json

**Test-Command:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-call \
-H "Content-Type: application/json" \
-d '{
  "call": {
    "from": "+4917612345678",
    "to": "+498912345678",
    "duration": 180000,
    "direction": "in"
  },
  "assist": {
    "summary": {
      "content": "Kunde möchte Angebot für Dachsanierung. Dachfläche 100 Quadratmeter, Ziegel gewünscht, mit Dämmung."
    }
  }
}'
```

**Erwartetes Ergebnis:**
```json
{
  "price_estimate": {
    "found": true,
    "total_cost": 18700.0,
    "area_sqm": 100.0,
    "project_type": "neueindeckung"
  }
}
```

---

#### **Test 2.2: Call WEG B (Bekannte Nummer mit Richtpreis)**
- [ ] Anruf von bekannter Nummer (z.B. mj@)
- [ ] Contact Matching erfolgreich
- [ ] Richtpreis berechnet
- [ ] WeClapp CRM Event mit Richtpreis
- [ ] WeClapp Task "Angebot vorbereiten" mit Preis
- [ ] Notification an Account Manager

**Test-Command:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-call \
-H "Content-Type: application/json" \
-d '{
  "call": {
    "from": "+4989123456781",
    "to": "+498912345678",
    "duration": 300000,
    "direction": "in"
  },
  "assist": {
    "summary": {
      "content": "Max (bekannter Kunde) fragt nach Angebot für Neueindeckung. 150 Quadratmeter, Premium Ziegel, Gerüst und Entsorgung inklusive."
    }
  }
}'
```

---

#### **Test 2.3: Call ohne Dacharbeiten (kein Richtpreis)**
- [ ] Anruf mit anderem Thema
- [ ] Transcript-Analyse läuft
- [ ] Richtpreis-Berechnung findet nichts (found=false)
- [ ] Hinweis "Keine Fläche erwähnt"
- [ ] Normal processing ohne Preis

**Test-Command:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-call \
-H "Content-Type: application/json" \
-d '{
  "call": {
    "from": "+4917698765432",
    "duration": 120000
  },
  "assist": {
    "summary": {
      "content": "Kunde fragt nach Status seiner Rechnung RE-2024-001."
    }
  }
}'
```

**Erwartetes Ergebnis:**
```json
{
  "price_estimate": {
    "found": false,
    "notes": "Keine Dachfläche im Gespräch erwähnt..."
  }
}
```

---

### **3. WHATSAPP WORKFLOWS**

#### **Test 3.1: WhatsApp von Kunde**
- [ ] Nachricht von Kunden-Nummer
- [ ] Contact Matching erfolgreich
- [ ] GPT-Analyse läuft
- [ ] WeClapp CRM Event erstellt
- [ ] Optional: Auto-Reply gesendet

**Test-Command:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/whatsapp \
-H "Content-Type: application/json" \
-d '{
  "from": "+491511234567 8",
  "message": "Hallo, wann kommt mein Angebot?",
  "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'
```

---

#### **Test 3.2: WhatsApp von Mitarbeiter (SQL Lookup)**
- [ ] Nachricht von Mitarbeiter-Nummer
- [ ] System erkennt Mitarbeiter
- [ ] SQL-Abfrage läuft
- [ ] Auto-Reply mit Kunden-Info

**Test-Command:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/whatsapp \
-H "Content-Type: application/json" \
-d '{
  "from": "+4989123456781",
  "message": "Wer ist +491511234567 8?",
  "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'
```

---

### **4. DATABASE & PERFORMANCE**

#### **Test 4.1: WEClapp Sync DB Status**
- [ ] `/tmp/weclapp_sync.db` existiert
- [ ] Datei nicht älter als 1 Stunde
- [ ] Parties Tabelle hat >100 Einträge
- [ ] Leads Tabelle hat Einträge

**Test-Command:**
```bash
# SSH zu Railway Container
railway run bash

# Im Container:
ls -lh /tmp/weclapp_sync.db
sqlite3 /tmp/weclapp_sync.db "SELECT COUNT(*) FROM parties;"
sqlite3 /tmp/weclapp_sync.db "SELECT COUNT(*) FROM leads;"
```

---

#### **Test 4.2: Contact Matching Performance**
- [ ] Cache Hit < 100ms
- [ ] Sync DB Hit < 200ms
- [ ] API Fallback < 3s

**Test-Command:**
```bash
# Railway Logs durchsuchen:
railway logs | grep "Contact Lookup"

# Erwartete Log-Lines:
# "✅ CACHE HIT (email_data) for kunde@firma.de - 45ms"
# "✅ WECLAPP SYNC DB HIT for kunde@firma.de - 127ms"
# "🔎 Cache Miss - Querying WeClapp for: neukunde@firma.de - 2341ms"
```

---

#### **Test 4.3: Database Persistence**
- [ ] email_data Einträge gespeichert
- [ ] attachments Einträge korrekt
- [ ] Foreign Keys intakt
- [ ] No Locks/Deadlocks

**Test-Command:**
```bash
railway run bash

# Im Container:
sqlite3 /app/email_data.db "SELECT COUNT(*) FROM email_data;"
sqlite3 /app/email_data.db "SELECT COUNT(*) FROM attachments;"
sqlite3 /app/email_data.db "SELECT workflow_path, COUNT(*) FROM email_data GROUP BY workflow_path;"
```

---

### **5. WECLAPP INTEGRATION**

#### **Test 5.1: CRM Event Creation**
- [ ] POST zu `/crmEvent` erfolgreich
- [ ] Event_ID zurück
- [ ] Event in WeClapp sichtbar
- [ ] Korrekt am Kontakt zugeordnet

**Manual Check:**
1. WeClapp öffnen
2. Kontakt suchen (z.B. Max Mustermann)
3. Kommunikations-Historie prüfen
4. Letzter Eintrag sollte Test-Email/Call sein

---

#### **Test 5.2: Task Creation**
- [ ] POST zu `/task` erfolgreich
- [ ] Task_ID zurück
- [ ] Task in WeClapp Aufgaben-Liste
- [ ] Richtig zugewiesen (Account Manager)
- [ ] Priority korrekt

**Manual Check:**
1. WeClapp → Aufgaben
2. Filter: Offen, Zugewiesen an mj@
3. Test-Task sollte erscheinen
4. Richtpreis in Description (bei Call)

---

#### **Test 5.3: Contact Search (API)**
- [ ] GET `/contact?email-eq=...` funktioniert
- [ ] Exact Match zurück
- [ ] Falls nicht gefunden: Empty result
- [ ] Keine Errors/Timeouts

**Test-Command:**
```bash
# Via Railway Shell:
railway run python3 -c "
import os
import httpx
import asyncio

async def test():
    token = os.getenv('WECLAPP_API_TOKEN')
    domain = os.getenv('WECLAPP_TENANT')
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f'https://{domain}.weclapp.com/webapp/api/v1/contact',
            headers={'AuthenticationToken': token},
            params={'email-eq': 'mj@cdtechnologies.de'}
        )
        print(resp.status_code, resp.json())

asyncio.run(test())
"
```

---

### **6. ERROR HANDLING**

#### **Test 6.1: WeClapp API Timeout**
- [ ] Simulate timeout (disconnect WiFi kurz)
- [ ] System graceful fallback
- [ ] Error logged
- [ ] User gets notification (evtl. ohne CRM Event)

---

#### **Test 6.2: OCR Failure**
- [ ] PDF upload mit ungültigem Format
- [ ] Apify Actor error
- [ ] System continues (Attachment ohne OCR)
- [ ] Error in Logs

---

#### **Test 6.3: Database Lock**
- [ ] Parallel requests
- [ ] SQLite Lock handling
- [ ] No deadlocks
- [ ] All requests processed

---

### **7. NOTIFICATION EMAILS**

#### **Test 7.1: WEG A Notification Layout**
- [ ] HTML korrekt (kein Plain Text)
- [ ] Buttons clickable
- [ ] Attachment-Details sichtbar (wenn vorhanden)
- [ ] Richtpreis prominent (wenn Call)
- [ ] Mobile-responsive

**Manual Check:**
1. Email öffnen in Outlook/Gmail
2. Desktop + Mobile prüfen
3. Alle Buttons testen

---

#### **Test 7.2: WEG B Notification Layout**
- [ ] HTML korrekt
- [ ] Kontakt-Info angezeigt
- [ ] Link zu WeClapp funktioniert
- [ ] Feedback-Button clickable

---

#### **Test 7.3: Email Delivery (nicht in Spam)**
- [ ] Emails kommen an
- [ ] Nicht im Spam-Ordner
- [ ] Absender korrekt
- [ ] Reply-To funktioniert

---

## 🚨 KRITISCHE FEHLER-SZENARIEN

### **Scenario 1: WEClapp API down**

**Was passiert:**
1. Contact Matching schlägt fehl
2. System fällt zurück auf Sync DB
3. Falls Sync DB auch leer: WEG_A Notification
4. User kann manuell Kontakt anlegen

**Erwartet:**
- ✅ System läuft weiter
- ✅ Email/Call wird verarbeitet
- ⚠️ Evtl. ohne CRM Event
- ✅ Notification verschickt

---

### **Scenario 2: OneDrive nicht erreichbar**

**Was passiert:**
1. WEClapp Sync DB Download schlägt fehl
2. System nutzt alte DB (falls vorhanden)
3. Falls keine DB: Fallback zu WeClapp API

**Erwartet:**
- ✅ System läuft weiter
- ⚠️ Performance schlechter (API calls)
- ✅ Alle Funktionen verfügbar

---

### **Scenario 3: GPT-4 API Timeout**

**Was passiert:**
1. _analyze_with_gpt() wirft Exception
2. Fallback zu simplified analysis
3. Intent/Urgency = "unknown"/"medium"
4. Processing continues

**Erwartet:**
- ✅ System läuft weiter
- ⚠️ Keine AI-Analyse
- ✅ Notification verschickt (ohne Analysis)

---

### **Scenario 4: Apify Actor Fehler**

**Was passiert:**
1. Attachment Processing schlägt fehl
2. Error logged
3. Attachment ohne OCR gespeichert
4. Processing continues

**Erwartet:**
- ✅ System läuft weiter
- ⚠️ Keine OCR-Daten
- ✅ Email/Attachment trotzdem verarbeitet

---

## 📊 MONITORING CHECKLIST

### **Daily Checks:**
- [ ] Health Check Endpoint: `GET /`
- [ ] WEClapp Sync DB Status (< 1h alt)
- [ ] Railway Logs auf Errors prüfen
- [ ] Notification Emails ankommen

### **Weekly Checks:**
- [ ] Database Size prüfen (email_data.db Growth)
- [ ] Cache Hit Rate (sollte >80%)
- [ ] WeClapp API Call Count
- [ ] Richtpreis-Berechnung Accuracy

### **Monthly Checks:**
- [ ] End-to-End Tests (alle Workflows)
- [ ] Performance Benchmarks
- [ ] Database Cleanup (alte Einträge)
- [ ] Documentation Update

---

## ✅ SIGN-OFF

### **System Ready for Production wenn:**
- [ ] Alle Email Tests bestanden
- [ ] Alle Call Tests bestanden (inkl. Richtpreis)
- [ ] WhatsApp Tests bestanden
- [ ] Database Tests bestanden
- [ ] WeClapp Integration funktioniert
- [ ] Error Handling robust
- [ ] Notification Emails korrekt
- [ ] Monitoring eingerichtet

### **Pending Items (nicht kritisch):**
- [ ] SipGate Echtzeit-Transkription
- [ ] Automatische SMS-Responses
- [ ] Call Recording Download
- [ ] WhatsApp Media Processing
- [ ] PostgreSQL Migration

---

**Status:** 🟡 IN TESTING  
**Nächster Schritt:** Alle Tests durchführen  
**Verantwortlich:** mj@cdtechnologies.de  
**Deadline:** 17. Oktober 2025
