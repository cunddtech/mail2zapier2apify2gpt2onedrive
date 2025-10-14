# 🎙️ FrontDesk Integration Guide

## Overview

**Dedizierter FrontDesk Endpoint** für Call Recording & Transcription.

Separate URLs für unterschiedliche Call-Quellen:
1. **SipGate Assist API** → `/webhook/ai-call`
2. **FrontDesk** → `/webhook/frontdesk` ✨ NEW

## Webhook URL

```
https://my-langgraph-agent-production.up.railway.app/webhook/frontdesk
```

**Vorteile separater Endpoint:**
- ✅ Einfachere Payload-Struktur (keine Auto-Detection)
- ✅ Dediziertes Logging für FrontDesk
- ✅ Keine Konflikte mit SipGate Format
- ✅ Einfacheres Testing & Debugging

## Payload Format

FrontDesk sendet eine **flache JSON-Struktur** (keine verschachtelten Objekte):

```json
{
  "caller": "+49123456789",
  "transcription": "Gesprächstext...",
  "recording_url": "https://...",
  "duration": 120
}
```

**Viel einfacher als SipGate** (keine `call.from` oder `assist.summary` Navigation nötig)!

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

Der Orchestrator loggt dediziert für FrontDesk:

```
🎙️ FrontDesk Webhook: {"caller": "+49634152145", ...}
📞 FrontDesk Call: +49634152145
   📛 Name: Frau Jäger
   🏢 Company: Beispiel GmbH
   ⏱️ Duration: 173s
   🎙️ Recording: https://...
✅ FrontDesk call processing complete: WEG_A
```

## Testing

### Test with curl
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/frontdesk \
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
  "message": "FrontDesk call processed",
  "workflow_path": "WEG_A",
  "phone": "+49123456789"
}
```

## FrontDesk Configuration

Konfiguriere in FrontDesk:

1. **Webhook URL**: `https://my-langgraph-agent-production.up.railway.app/webhook/frontdesk`
2. **Method**: `POST`
3. **Content-Type**: `application/json`
4. **Trigger**: Nach Transkription fertig
5. **Authentication**: None (öffentlich erreichbar)

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

## Quick Start

**1. Konfiguriere FrontDesk:**
```
URL: https://my-langgraph-agent-production.up.railway.app/webhook/frontdesk
Method: POST
Content-Type: application/json
```

**2. Teste manuell:**
```bash
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/frontdesk \
  -H "Content-Type: application/json" \
  -d '{"caller": "+49123456789", "transcription": "Test"}'
```

**3. Prüfe Railway Logs:**
```bash
railway logs --tail 50 | grep "FrontDesk"
```

---

**Status**: ✅ Implementiert (Dedizierter Endpoint)  
**Deployed**: Railway Production  
**URL**: `/webhook/frontdesk`  
**Last Updated**: 2025-10-14
