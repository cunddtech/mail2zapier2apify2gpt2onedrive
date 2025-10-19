# 🧪 TEST EXECUTION GUIDE
## Railway Webhook Test Suite

Erstellt: 19. Oktober 2025

---

## 📋 ÜBERSICHT

Diese Test Suite ermöglicht vollständige Tests aller Railway Webhook Endpoints mit realen und Mock-Daten.

### ✅ Was wurde erstellt:

1. **`WEBHOOK_TRIGGER_OVERVIEW.md`** - Komplette Dokumentation aller Webhooks
2. **`test_suite/test_email_scenarios.py`** - Email Tests (6 Szenarien)
3. **`test_suite/test_call_scenarios_live.py`** - Call Tests (5 Szenarien)
4. **`test_suite/run_tests.sh`** - Interaktives Test Menu
5. **`test_results/`** - Automatische Result Storage

---

## 🚀 QUICK START

### Option 1: Interactive Menu (Empfohlen)
\`\`\`bash
cd /Users/cdtechgmbh/mail2zapier2apify2gpt2onedrive/test_suite
./run_tests.sh
\`\`\`

### Option 2: Direct Commands
\`\`\`bash
# Email Test - Rechnungen
python3 test_suite/test_email_scenarios.py --scenario invoice --count 10

# Email Test - Alle Szenarien
python3 test_suite/test_email_scenarios.py --scenario all

# Call Test - Bekannter Kontakt
python3 test_suite/test_call_scenarios_live.py --scenario known

# Call Test - Alle Szenarien
python3 test_suite/test_call_scenarios_live.py --scenario all
\`\`\`

---

## 📧 EMAIL TEST SZENARIEN

### 1. Eingangsrechnungen (\`invoice\`)
- **Keywords**: rechnung, invoice, bill
- **PDF**: Erforderlich
- **Expected**: Invoice DB Entry + OneDrive Upload
- **Test Command**:
  \`\`\`bash
  python3 test_suite/test_email_scenarios.py --scenario invoice --count 10
  \`\`\`

### 2. Angebote & Preisanfragen (\`offer\`)
- **Keywords**: angebot, offer, preis, anfrage
- **PDF**: Optional
- **Expected**: Opportunity in Sales Pipeline
- **Test Command**:
  \`\`\`bash
  python3 test_suite/test_email_scenarios.py --scenario offer --count 5
  \`\`\`

### 3. Auftragsbestätigungen (\`order_confirmation\`)
- **Keywords**: auftragsbestätigung, order confirmation
- **PDF**: Erforderlich
- **Expected**: OneDrive /Auftragsbestätigungen/

### 4. Lieferscheine (\`delivery_note\`)
- **Keywords**: lieferschein, delivery note
- **PDF**: Erforderlich
- **Expected**: OneDrive /Lieferscheine/

### 5. Allgemeine Anfragen (\`general\`)
- **Keywords**: anfrage, inquiry, frage
- **PDF**: Optional
- **Expected**: OneDrive /Allgemein/ + Email-to-PDF

### 6. Multi-Attachment (\`multi_attachment\`)
- **Filter**: 3+ Anhänge
- **Expected**: Alle PDFs separat verarbeitet

---

## 📞 CALL TEST SZENARIEN

### ⚠️ WICHTIG: Benötigt Konfiguration

Vor dem Ausführen der Call Tests:
\`\`\`python
# In test_call_scenarios_live.py anpassen:
KNOWN_CONTACT = {
    "phone": "+4930123456",  # MUSS in WeClapp existieren!
    "name": "Test Contact"
}

UNKNOWN_CONTACT = {
    "phone": "+491234567890",  # Darf NICHT in WeClapp existieren!
    "name": "Unknown Caller"
}
\`\`\`

### 1. Inbound Call - Bekannter Kontakt
- **Expected**: WEG B → CRM Log + Task Creation
- **Test Command**:
  \`\`\`bash
  python3 test_suite/test_call_scenarios_live.py --scenario known \\
    --known-phone "+4930123456"
  \`\`\`

### 2. Inbound Call - Unbekannter Kontakt
- **Expected**: WEG A → Notification Email + 4 Buttons
- **Test Command**:
  \`\`\`bash
  python3 test_suite/test_call_scenarios_live.py --scenario unknown \\
    --unknown-phone "+491234567890"
  \`\`\`

### 3. Outbound Call
- **Expected**: CRM Log als "Outbound Call"

### 4. FrontDesk Integration
- **Expected**: FrontDesk Detection → Standard Pipeline

### 5. Long Call mit Action Items
- **Expected**: 8 Tasks + Opportunity (€80,000)

---

## 📊 VALIDATION CHECKLIST

### Nach Email Tests:
- [ ] Dashboard öffnen: http://localhost:3000
- [ ] Invoice Statistics zeigen neue Entries
- [ ] Recent Invoices Liste aktualisiert
- [ ] OneDrive Ordner prüfen: /Eingang/Rechnungen/2025/10/
- [ ] Sharing Links testen

### Nach Call Tests:
- [ ] WeClapp Login
- [ ] Contact öffnen (bekannter Kontakt)
- [ ] Aktivitäten → Neues Call Event
- [ ] Aufgaben → Tasks aus Action Items
- [ ] Bei Unknown: Email Posteingang prüfen

### Nach Sales Pipeline Tests:
- [ ] Dashboard öffnen: http://localhost:3000/sales-pipeline
- [ ] Pipeline Statistics
- [ ] Recent Opportunities
- [ ] WeClapp Verkaufschancen

---

## 🔍 TROUBLESHOOTING

### Problem: "ModuleNotFoundError: httpx"
**Lösung**:
\`\`\`bash
pip3 install httpx msal requests
\`\`\`

### Problem: "No emails found"
**Lösung**:
- Datum Range erweitern: \`--days-back 60\`
- Keywords anpassen in \`SCENARIO_CONFIGS\`
- Graph API Token prüfen

### Problem: "401 Unauthorized" (Graph API)
**Lösung**:
1. \`.env\` öffnen
2. \`GRAPH_CLIENT_SECRET_MAIL\` prüfen
3. Token regenerieren wenn expired

### Problem: "Webhook timeout"
**Lösung**:
- Railway ist Async → Response kommt sofort (< 1s)
- Verarbeitung läuft im Hintergrund
- Check Railway Logs: \`railway logs --tail 100\`

---

## 📈 EXPECTED SUCCESS RATES

| Test Type | Expected Rate | Status |
|-----------|---------------|--------|
| Email Tests | 95%+ | ✅ Validiert (13/13) |
| Call Tests (Mock) | 100% | ✅ Webhook Akzeptanz |
| Call Tests (Live) | 90%+ | ⚠️ Abhängig von WeClapp |
| Integration | 85%+ | 🔄 End-to-End |

---

## 📁 TEST RESULTS

Alle Test Results werden automatisch gespeichert:

\`\`\`
test_results/
├── email_invoice_20251019_100523.json
├── email_offer_20251019_100645.json
├── call_tests_20251019_101203.json
└── integration_20251019_102345.json
\`\`\`

Format:
\`\`\`json
{
  "scenario": "invoice",
  "timestamp": "2025-10-19T10:05:23Z",
  "total_tests": 10,
  "successful": 9,
  "results": [...]
}
\`\`\`

---

## 🌐 WICHTIGE URLS

- **Dashboard**: http://localhost:3000
- **Sales Pipeline**: http://localhost:3000/sales-pipeline
- **Railway Production**: https://my-langgraph-agent-production.up.railway.app
- **Invoice API**: https://my-langgraph-agent-production.up.railway.app/api/invoice/statistics
- **Sales API**: https://my-langgraph-agent-production.up.railway.app/api/opportunity/statistics
- **Payment API**: https://my-langgraph-agent-production.up.railway.app/api/payment/statistics

---

## 🎯 NÄCHSTE SCHRITTE

1. ✅ **Email Tests ausführen** (bereits empfangene Emails)
   \`\`\`bash
   python3 test_suite/test_email_scenarios.py --scenario all
   \`\`\`

2. ⚠️ **SipGate Kontakte konfigurieren** (für Live Tests)
   - Bekannten Kontakt in WeClapp erstellen
   - Telefonnummer notieren
   - In test_call_scenarios_live.py eintragen

3. 🧪 **Call Tests ausführen** (Mock Webhooks)
   \`\`\`bash
   python3 test_suite/test_call_scenarios_live.py --scenario all
   \`\`\`

4. 📊 **Dashboard validieren**
   - http://localhost:3000 öffnen
   - Alle Statistics prüfen
   - Recent Lists validieren

5. 🔄 **Integration Tests** (End-to-End)
   - Email → Invoice DB → Dashboard
   - Call → CRM → Task
   - Payment Match Workflow

---

## 📞 LIVE TEST SETUP (SipGate)

### 1. SipGate Account Setup
1. Login: https://app.sipgate.com
2. Navigate zu: Settings → Webhooks
3. Add Webhook:
   - **URL**: \`https://my-langgraph-agent-production.up.railway.app/webhook/ai-call\`
   - **Events**: "Call Ended with Assist"
   - **Method**: POST

### 2. Test Call durchführen
1. Mit SipGate Number anrufen
2. Gespräch führen (min. 30 Sekunden)
3. Auflegen
4. Webhook wird automatisch getriggert

### 3. Validation
- Railway Logs prüfen
- WeClapp CRM Event prüfen
- Email bei Unknown Contact

---

## ✅ FERTIG!

Die komplette Test Suite ist einsatzbereit. Starte mit:

\`\`\`bash
cd /Users/cdtechgmbh/mail2zapier2apify2gpt2onedrive/test_suite
./run_tests.sh
\`\`\`

Bei Fragen oder Problemen: Siehe "Troubleshooting" Sektion.

