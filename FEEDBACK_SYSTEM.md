# 🐛 Feedback & Optimization System

## Overview

Jeder Mitarbeiter kann direkt aus den AI-Notifications Feedback geben:
- **Fehlverhalten melden** (Bug Reports)
- **Fehlende Funktionen** vorschlagen
- **Falsche Zuordnungen** korrigieren
- **Verbesserungen** einreichen

## Feedback-Buttons in Notifications

### Unbekannte Kontakte (WEG A)
```
✅ KONTAKT ANLEGEN
➕ ZU BESTEHENDEM HINZUFÜGEN  ← NEU!
🔒 PRIVAT MARKIEREN
🚫 SPAM MARKIEREN
📨 INFO ANFORDERN
🐛 PROBLEM MELDEN  ← NEU!
```

### Bekannte Kontakte (WEG B)
```
📋 IN CRM ÖFFNEN
🐛 PROBLEM MELDEN  ← NEU!
```

## Feedback-Typen

### 1. Bug (Fehlverhalten)
**Beispiele:**
- "AI hat falsche Absicht erkannt (Angebot statt Anfrage)"
- "Email wurde doppelt verarbeitet"
- "WeClapp Event wurde nicht erstellt"

### 2. Wrong Match (Falsche Zuordnung)
**Beispiele:**
- "Kontakt wurde falsch zugeordnet (sollte Firma X sein)"
- "Telefonnummer gehört zu anderem Kontakt"
- "Email-Domain falsch interpretiert"

### 3. Feature Request (Fehlende Funktion)
**Beispiele:**
- "Button zum Termin erstellen fehlt"
- "Automatische Rechnungserstellung wäre hilfreich"
- "Priorität sollte änderbar sein"

### 4. Improvement (Verbesserungsvorschlag)
**Beispiele:**
- "AI-Zusammenfassung könnte kürzer sein"
- "Notification-Email zu lang"
- "Bessere Formatierung für Tasks"

## Webhook Payload

```json
{
  "type": "bug|feature|improvement|wrong_match",
  "message": "Beschreibung des Problems oder Vorschlags",
  "reporter": "mj@cdtechnologies.de",
  "context": {
    "email_id": "railway-1234567890",
    "contact_id": "386796",
    "workflow_path": "WEG_B",
    "message_type": "email",
    "from_contact": "kunde@example.com"
  }
}
```

## Feedback Storage

Alle Feedbacks werden gespeichert in:
```
feedback_log.jsonl
```

Format (JSONL - eine Zeile pro Feedback):
```json
{"timestamp": "2025-10-14T17:30:00+02:00", "type": "bug", "message": "...", "context": {...}, "reporter": "...", "status": "new"}
{"timestamp": "2025-10-14T17:45:00+02:00", "type": "feature", "message": "...", "context": {...}, "reporter": "...", "status": "new"}
```

## Feedback abrufen

### Via Railway CLI
```bash
railway run cat feedback_log.jsonl | jq '.'
```

### Via Python
```python
import json

with open("feedback_log.jsonl", "r") as f:
    for line in f:
        feedback = json.loads(line)
        print(f"{feedback['timestamp']} - {feedback['type']}: {feedback['message']}")
```

### Filtern nach Typ
```bash
railway run grep '"type":"bug"' feedback_log.jsonl | jq '.'
```

## Optimization Workflow

1. **Feedback gesammelt** → Automatisch in `feedback_log.jsonl` gespeichert
2. **Wöchentliche Review** → Alle neuen Feedbacks durchgehen
3. **Prioritisierung** → Nach Impact und Häufigkeit
4. **Implementierung** → Features/Fixes umsetzen
5. **Status Update** → In Feedback-Eintrag markieren als "done"

## API Endpoints

### POST /webhook/feedback
Empfängt Feedback von Mitarbeitern

**Request:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "type": "bug",
    "message": "AI hat Priorität falsch eingeschätzt",
    "reporter": "mj@cdtechnologies.de",
    "context": {
      "email_id": "railway-1234567890",
      "workflow_path": "WEG_B"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback erfasst - Vielen Dank!",
  "feedback_id": "fb-1728923400"
}
```

## Statistiken

### Feedback nach Typ
```bash
cat feedback_log.jsonl | jq -r '.type' | sort | uniq -c
```

### Top Reporter
```bash
cat feedback_log.jsonl | jq -r '.reporter' | sort | uniq -c | sort -rn
```

### Neueste Feedbacks (letzte 10)
```bash
tail -10 feedback_log.jsonl | jq '.'
```

## Zapier Integration

In Zapier können die Buttons so konfiguriert werden:

**Feedback Button:**
```
Action: Webhook POST
URL: https://my-langgraph-agent-production.up.railway.app/webhook/feedback
Method: POST
Data:
{
  "type": "bug",  # Oder Dropdown mit Optionen
  "message": "{user_input}",
  "reporter": "mj@cdtechnologies.de",
  "context": {
    "email_id": "{email_id}",
    "contact_id": "{contact_id}",
    "workflow_path": "{workflow_path}"
  }
}
```

## Best Practices

### Für Mitarbeiter:
- **Konkret sein**: "AI erkannte 'Anfrage' als 'Bestellung'" statt "AI falsch"
- **Kontext angeben**: Welche Email, welcher Kontakt, wann?
- **Vorschläge machen**: Was wäre besser gewesen?

### Für Entwickler:
- **Schnell reagieren**: Kritische Bugs innerhalb 24h fixen
- **Kommunizieren**: Feedback-Geber informieren wenn umgesetzt
- **Priorisieren**: Häufige Probleme zuerst

## Archivierung

Alte Feedbacks (> 90 Tage) archivieren:
```bash
# Feedbacks älter als 90 Tage
grep '"status":"done"' feedback_log.jsonl > feedback_archive_$(date +%Y%m).jsonl

# Aktive Feedbacks behalten
grep -v '"status":"done"' feedback_log.jsonl > feedback_log_active.jsonl
mv feedback_log_active.jsonl feedback_log.jsonl
```

---

**Status**: ✅ Implementiert  
**Version**: 1.2.0  
**Last Updated**: 2025-10-14
