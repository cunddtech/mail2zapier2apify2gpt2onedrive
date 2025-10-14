# 🎙️ FrontDesk Integration Guide

## Overview

Der `/webhook/ai-call` Endpoint unterstützt jetzt **ZWEI Webhook-Quellen**:

1. **SipGate Assist API** - AI-generierte Call Summaries mit SmartAnswers
2. **FrontDesk** - Call Recording & Transcription Service

## Webhook URL

```
https://my-langgraph-agent-production.up.railway.app/webhook/ai-call
```

## Auto-Detection

Der Orchestrator erkennt automatisch die Quelle anhand der Payload-Struktur:

### SipGate Assist Detection
```json
{
  "call": {...},
  "assist": {...}
}
```
→ Erkannt als **SipGate Assist**

### FrontDesk Detection
```json
{
  "recording_url": "https://...",
  "transcription": "..."
}
```
→ Erkannt als **FrontDesk**

## Supported FrontDesk Fields

### Required Fields
- `caller` / `from` / `phone` / `caller_number` - Telefonnummer des Anrufers
- `transcription` / `transcript` / `text` / `content` - Gesprächstranskription

### Optional Fields
- `call_id` / `id` - Eindeutige Call ID
- `duration` / `call_duration` - Gesprächsdauer in Sekunden
- `start_time` / `startTime` - Anrufstart (Timestamp)
- `end_time` / `endTime` - Anrufende (Timestamp)
- `caller_name` / `name` - Name des Anrufers
- `company` / `company_name` - Firmenname
- `request` / `purpose` - Anliegen/Zweck des Anrufs
- `recording_url` / `audio_url` - URL zur Audio-Aufnahme
- `call_direction` / `direction` - "inbound" oder "outbound"
- `key_points` - Array mit wichtigen Punkten
- `topics` - Array mit Themen

## Example FrontDesk Payload

```json
{
  "call_id": "fd-12345",
  "caller": "+49634152145",
  "caller_name": "Frau Jäger",
  "company": "Beispiel GmbH",
  "duration": 173,
  "direction": "inbound",
  "start_time": "2025-10-14T09:10:00Z",
  "transcription": "Guten Tag, ich hätte gerne ein Angebot für...",
  "recording_url": "https://frontdesk.example.com/recordings/12345.mp3",
  "key_points": [
    "Kunde benötigt Angebot",
    "Rückruf gewünscht bis Freitag"
  ],
  "topics": ["Angebot", "Rückruf"]
}
```

## Processing Flow

1. **Webhook empfangen** → Auto-Detection (SipGate vs FrontDesk)
2. **Daten extrahieren** → Telefonnummer, Name, Transkription
3. **Contact Matching** → WeClapp Suche nach Telefonnummer
4. **AI Analyse** → GPT-4 analysiert Transkription
5. **Workflow Routing**:
   - **WEG A** (Unbekannt): Notification Email mit Action Buttons
   - **WEG B** (Bekannt): CRM Log mit Tasks
6. **CRM Update** → WeClapp Communication Event erstellen

## Logging

Der Orchestrator loggt die erkannte Quelle:

```
✅ Detected: FrontDesk webhook
🎙️ FrontDesk Recording: https://...
📞 Call Details: Direction: inbound | Duration: 173s
   📞 External: +49634152145 | Our Number: +49211879744313
   📛 Caller Name: Frau Jäger
   🏢 Company: Beispiel GmbH
```

## Testing

### Test with curl
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/ai-call \
  -H "Content-Type: application/json" \
  -d '{
    "caller": "+49123456789",
    "transcription": "Test Anruf von FrontDesk",
    "duration": 60,
    "recording_url": "https://example.com/test.mp3"
  }'
```

### Expected Response
```json
{
  "status": "success",
  "message": "Call processing complete",
  "workflow_path": "WEG_A"
}
```

## FrontDesk Configuration

Konfiguriere in FrontDesk:

1. **Webhook URL**: `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`
2. **Method**: `POST`
3. **Content-Type**: `application/json`
4. **Trigger**: Nach Transkription fertig

## Unterschiede: SipGate vs FrontDesk

| Feature | SipGate Assist | FrontDesk |
|---------|---------------|-----------|
| **Struktur** | Nested (`call.from`) | Flat (`caller`) |
| **Duration** | Millisekunden | Sekunden |
| **AI Analysis** | SmartAnswers | Key Points |
| **Recording** | Nicht immer | URL vorhanden |
| **Transcription** | `assist.summary.content` | `transcription` |

## Railway Logs

Prüfe die Logs nach FrontDesk Webhooks:

```bash
railway logs --tail 100 | grep -i "frontdesk\|recording"
```

## Support

Bei Problemen:
1. Prüfe Railway Logs: `railway logs --tail 200`
2. Suche nach "Detected: FrontDesk webhook"
3. Prüfe ob alle erforderlichen Felder vorhanden sind
4. Kontaktiere Support mit Call ID

---

**Status**: ✅ Implementiert (Commit 6546adf)  
**Deployed**: Railway Production  
**Last Updated**: 2025-10-14
