# 💰 Payment Matching System - API Documentation

## 🎯 Überblick

Das Payment Matching System automatisiert den Abgleich zwischen:
- **Bankumsätzen** (CSV Import oder API)
- **Rechnungen** aus der Invoice Tracking Database

### Features
✅ Automatisches Matching (Confidence-basiert)  
✅ CSV Import (Sparkasse, Volksbank, Generic)  
✅ Manuelles Matching (bei niedrigem Confidence)  
✅ Multi-Faktor Matching-Algorithmus  
✅ Payment Statistics Dashboard  

---

## 📊 Matching-Algorithmus

### Confidence Score Berechnung

| Faktor | Gewichtung | Bedingungen |
|--------|------------|-------------|
| **Betrag** | 40% | Exakt: 40%, Nah (<1€): 20% |
| **Rechnungsnummer** | 30% | Exakt: 30%, Partial: 15% |
| **Vendor/Kunde Name** | 20% | Exakt: 20%, Partial: 10% |
| **Datum** | 10% | ≤7 Tage: 10%, ≤30 Tage: 5% |

### Matching-Schwellwerte
- **≥ 70%** → Auto-Match (sofortige Buchung)
- **50-69%** → Manueller Review empfohlen
- **< 50%** → Kein Match, manuell erforderlich

### Beispiel-Matches

**High Confidence (95%)**
```
Transaction: -1500.00 EUR | "Rechnung RE-2025-101" | ACME GmbH
Invoice:     1500.00 EUR | RE-2025-101 | ACME GmbH | Fällig: +5 Tage
✅ Match: amount_exact + invoice_number_exact + name_exact + date_close
```

**Medium Confidence (50%)**
```
Transaction: -749.99 EUR | "Supplier payment" | Supplier XYZ GmbH
Invoice:     750.00 EUR | RE-2025-103 | Supplier XYZ | Fällig: +2 Tage
⚠️ Match: amount_exact + date_close (nur Betrag + Datum)
```

---

## 🔌 API Endpoints

### 1. CSV Import

**POST** `/api/payment/import-csv`

Import von Bank-Kontoauszügen im CSV-Format.

**Request Body:**
```json
{
  "csv_content": "QXVmdHJhZ3Nrb250bztCdWNod...",  // Base64 encoded CSV
  "format": "auto"  // "sparkasse" | "volksbank" | "generic" | "auto"
}
```

**Response:**
```json
{
  "status": "success",
  "stats": {
    "imported": 145,
    "skipped": 3,
    "errors": 0
  }
}
```

**Unterstützte CSV-Formate:**
- **Sparkasse** (Auftragskonto, Buchungstag, Betrag, Verwendungszweck)
- **Volksbank** (ähnlich Sparkasse)
- **Generic** (Date, Amount, Description, Sender, Receiver)

**Beispiel-Nutzung:**
```python
import base64
import requests

# CSV Datei lesen
with open('kontoauszug.csv', 'rb') as f:
    csv_bytes = f.read()
    csv_b64 = base64.b64encode(csv_bytes).decode('utf-8')

# Import
response = requests.post(
    'https://my-langgraph-agent-production.up.railway.app/api/payment/import-csv',
    json={
        'csv_content': csv_b64,
        'format': 'auto'  # Auto-Erkennung
    }
)

print(response.json())
# {'status': 'success', 'stats': {'imported': 145, 'skipped': 3, 'errors': 0}}
```

---

### 2. Einzelne Transaktion importieren

**POST** `/api/payment/import-transaction`

Import einer einzelnen Banktransaktion (z.B. von Banking API).

**Request Body:**
```json
{
  "transaction_id": "BANK-TX-2025-10-18-001",
  "transaction_date": "2025-10-18",
  "value_date": "2025-10-18",
  "amount": -1500.00,
  "currency": "EUR",
  "sender_name": "C&D Tech GmbH",
  "sender_iban": "DE89370400440532013000",
  "receiver_name": "ACME GmbH",
  "receiver_iban": "DE89370400440532099999",
  "purpose": "Rechnung RE-2025-101 vom 01.10.2025",
  "reference": "RE-2025-101"
}
```

**Response:**
```json
{
  "status": "success",
  "transaction_id": 1  // DB Primary Key
}
```

**Beispiel-Nutzung:**
```python
# Von HBCI/FinTS API
for transaction in banking_api.get_transactions(days=30):
    requests.post(
        'https://my-langgraph-agent-production.up.railway.app/api/payment/import-transaction',
        json={
            'transaction_id': transaction.id,
            'transaction_date': transaction.date.isoformat(),
            'amount': transaction.amount,
            'sender_name': transaction.sender,
            'purpose': transaction.purpose
        }
    )
```

---

### 3. Auto-Matching

**POST** `/api/payment/auto-match`

Automatisches Matching aller ungematchten Transaktionen.

**Request Body (Optional):**
```json
{
  "min_confidence": 0.7  // Minimum Confidence (0.0-1.0), Default: 0.7
}
```

**Response:**
```json
{
  "status": "success",
  "stats": {
    "processed": 10,
    "matched": 7,
    "unmatched": 2,
    "low_confidence": 1
  }
}
```

**Workflow:**
1. Alle ungematchten Transaktionen laden
2. Für jede Transaktion passende offene Rechnung suchen
3. Confidence Score berechnen
4. Bei `confidence >= min_confidence`: Auto-Match + Rechnung als "paid" markieren
5. Bei niedrigem Confidence: Manuelle Review Queue

**Beispiel-Nutzung:**
```python
# Nach CSV-Import automatisch matchen
response = requests.post(
    'https://my-langgraph-agent-production.up.railway.app/api/payment/auto-match',
    json={'min_confidence': 0.75}  # 75% Minimum
)

stats = response.json()['stats']
print(f"✅ {stats['matched']} matched, ⚠️ {stats['low_confidence']} need review")
```

---

### 4. Manuelles Matching

**POST** `/api/payment/match`

Manuelle Zuordnung Transaktion → Rechnung.

**Request Body:**
```json
{
  "transaction_id": 3,  // DB ID der Transaktion
  "invoice_number": "RE-2025-103"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Transaction 3 matched to invoice RE-2025-103"
}
```

**Nutzungsfall:** Low-Confidence Matches manuell bestätigen.

**Beispiel-Nutzung:**
```python
# Review Queue durchgehen
unmatched = requests.get('.../api/payment/unmatched').json()

for tx in unmatched['transactions']:
    print(f"Transaction {tx['id']}: {tx['amount']} EUR - {tx['purpose']}")
    invoice_num = input("Invoice Number (oder Enter für Skip): ")
    
    if invoice_num:
        requests.post(
            '.../api/payment/match',
            json={
                'transaction_id': tx['id'],
                'invoice_number': invoice_num
            }
        )
```

---

### 5. Unmatched Transactions

**GET** `/api/payment/unmatched`

Liste aller noch nicht zugeordneten Transaktionen.

**Response:**
```json
{
  "status": "success",
  "count": 2,
  "transactions": [
    {
      "id": 3,
      "transaction_id": "BANK-TX-003",
      "transaction_date": "2025-10-16",
      "amount": -749.99,
      "sender_name": "C&D Tech GmbH",
      "receiver_name": "Supplier XYZ GmbH",
      "purpose": "Supplier invoice payment",
      "reference": "103",
      "matched_invoice_id": null
    },
    {
      "id": 4,
      "transaction_id": "BANK-TX-004",
      "transaction_date": "2025-10-15",
      "amount": -3500.00,
      "purpose": "Office supplies",
      "matched_invoice_id": null
    }
  ]
}
```

**Nutzungsfall:** Dashboard "Offene Zahlungen" oder Review Queue.

---

### 6. Payment Statistics

**GET** `/api/payment/statistics`

Gesamtstatistiken Payment Matching.

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_transactions": 150,
    "matched_count": 120,
    "unmatched_count": 30,
    "match_rate": 80.0,
    "matched_amount": 125000.50
  }
}
```

**Nutzungsfall:** Dashboard KPIs, Monitoring.

---

## 🗄️ Database Schema

### `bank_transactions` Table

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | INTEGER PK | Auto-Increment |
| `transaction_id` | TEXT UNIQUE | Bank-ID (eindeutig) |
| `transaction_date` | DATE | Buchungsdatum |
| `value_date` | DATE | Wertstellung |
| `amount` | REAL | Betrag (negativ=Abgang, positiv=Zugang) |
| `currency` | TEXT | Währung (EUR) |
| `sender_name` | TEXT | Absender |
| `sender_iban` | TEXT | IBAN Absender |
| `receiver_name` | TEXT | Empfänger |
| `receiver_iban` | TEXT | IBAN Empfänger |
| `purpose` | TEXT | Verwendungszweck |
| `reference` | TEXT | Referenz |
| `transaction_type` | TEXT | credit/debit |
| `matched_invoice_id` | INTEGER FK | Zugeordnete Rechnung |
| `matched_at` | DATETIME | Match-Zeitpunkt |
| `match_confidence` | REAL | Confidence Score (0.0-1.0) |
| `match_method` | TEXT | Matching-Methode |

### `payment_matches` Table

Historien-Tabelle aller Matches (auch manuelle).

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | INTEGER PK | |
| `transaction_id` | INTEGER FK | → bank_transactions |
| `invoice_id` | INTEGER FK | → invoices |
| `match_confidence` | REAL | Confidence Score |
| `match_method` | TEXT | amount+invoice#+name+date |
| `matched_by` | TEXT | auto/manual |
| `matched_at` | DATETIME | Zeitstempel |
| `status` | TEXT | confirmed/rejected/pending |

---

## 🧪 Testing

### Lokaler Test
```bash
python3 test_payment_matching.py
```

**Test-Szenarios:**
1. ✅ 3 Test-Rechnungen erstellen (incoming/outgoing)
2. ✅ 4 Bank-Transaktionen importieren
3. ✅ Invoice Number Extraction testen
4. ✅ Matching-Algorithmus testen (Confidence-Berechnung)
5. ✅ Auto-Match ausführen (min_confidence=0.6)
6. ✅ Unmatched Transactions abrufen
7. ✅ Payment Statistics abrufen
8. ✅ Rechnungen auf "paid" Status prüfen

**Erwartete Ergebnisse:**
- **3/4 Transactions** gematcht (75%)
- **RE-2025-101**: PAID ✅ (85% Confidence, amount+invoice#+name)
- **RE-2025-102**: PAID ✅ (95% Confidence, alle Faktoren)
- **RE-2025-103**: OPEN ❌ (50% Confidence, nur Betrag - unter Threshold)

---

## 🔄 Workflow Integration

### 1. Täglicher Batch-Import

**Zapier/n8n Workflow:**
```
Trigger: Täglich 08:00 Uhr
└─ Download Kontoauszug von Bank (HBCI/CSV)
   └─ POST /api/payment/import-csv
      └─ POST /api/payment/auto-match (min_confidence=0.7)
         └─ GET /api/payment/unmatched
            └─ Slack Notification: "5 Zahlungen benötigen Review"
```

### 2. Real-Time Banking Webhook

```python
# Banking Provider Webhook
@app.post("/webhook/bank-transaction")
async def bank_webhook(request: Request):
    data = await request.json()
    
    # Import Transaction
    tx_response = requests.post(
        'http://localhost:5001/api/payment/import-transaction',
        json={
            'transaction_id': data['id'],
            'transaction_date': data['booking_date'],
            'amount': data['amount'],
            'sender_name': data['counterpart']['name'],
            'purpose': data['purpose']
        }
    )
    
    # Immediate Auto-Match
    requests.post('http://localhost:5001/api/payment/auto-match')
    
    return {"status": "ok"}
```

### 3. Dashboard Integration

```javascript
// React Dashboard Component
const PaymentStats = () => {
  const [stats, setStats] = useState({});
  
  useEffect(() => {
    fetch('https://my-api.railway.app/api/payment/statistics')
      .then(r => r.json())
      .then(data => setStats(data.statistics));
  }, []);
  
  return (
    <div>
      <h2>Payment Matching</h2>
      <p>Match Rate: {stats.match_rate}%</p>
      <p>Unmatched: {stats.unmatched_count}</p>
      <p>Total Matched: {stats.matched_amount} EUR</p>
    </div>
  );
};
```

---

## 🎯 Best Practices

### 1. Confidence Threshold
- **Production**: 70% (Balance zwischen Automatisierung und Genauigkeit)
- **Testing**: 60% (mehr Matches sehen)
- **Conservative**: 80% (nur sehr sichere Matches)

### 2. CSV Import Frequency
- **Täglich**: Standard für Buchhaltung
- **Wöchentlich**: Kleinere Unternehmen
- **Real-Time**: Banking API Webhooks

### 3. Manual Review Queue
- Alle Low-Confidence Matches (50-70%) manuell prüfen
- Dashboard mit "Review Needed" Badge
- Wöchentliche Review-Session einplanen

### 4. Error Handling
- Duplicate Transaction IDs → Update statt Insert
- Missing Invoice → Unmatched Queue
- Invalid CSV → Log + Skip Row + Continue

---

## 📝 Changelog

### Version 1.0 (2025-10-18)
✅ Initial Release  
✅ Auto-Matching Algorithmus  
✅ CSV Import (Sparkasse/Volksbank/Generic)  
✅ 6 REST API Endpoints  
✅ Test Suite (9 Scenarios)  
✅ Production Deployment (Railway)  

### Roadmap
🔜 SEPA XML Import  
🔜 HBCI/FinTS Direct Integration  
🔜 Machine Learning Matching (Auto-Improve)  
🔜 Split Payments (1 Transaction → Multiple Invoices)  
🔜 Payment Plans (Partial Payments)  

---

## 🆘 Support

**Issues?**
- Check logs: `railway logs --tail 50`
- Verify DB: `sqlite3 /tmp/payment_tracking.db "SELECT * FROM bank_transactions LIMIT 5"`
- Test locally: `python3 test_payment_matching.py`

**API Errors?**
- 400: Missing required fields
- 500: Database error (check Railway logs)
- 404: Invalid endpoint

**Contact:**
📧 mj@cdtechnologies.de
