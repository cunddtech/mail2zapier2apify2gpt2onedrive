# AI Coding Agent Instructions

## Project Architecture

This is a **multi-channel communication orchestrator** that processes emails, phone calls, and WhatsApp messages through an AI-powered workflow system. The architecture consists of:

### Core Components
- **Railway Orchestrator** (`production_langgraph_orchestrator.py`): LangGraph-based FastAPI server running on Railway at `https://my-langgraph-agent-production.up.railway.app`
- **Apify Actors** (`src/main*.py`): Containerized processors for email/attachment handling, OCR, and webhook transformations
- **WeClapp CRM Integration** (`modules/weclapp/`): Contact matching and opportunity management
- **Modular Processing Pipeline** (`modules/`): 20+ specialized modules for different processing stages

### Data Flow Pattern
```
Webhook/Email → Source Detection → Format Transformation → Railway AI Analysis → CRM Lookup → Workflow Routing (WEG_A/WEG_B) → Action Generation → Notifications
```

## Development Workflows

### Testing Multi-Channel Processing
```bash
# Test SipGate webhook (phone calls)
apify call cdtech~mail2zapier2apify2gpt2onedrive --input '{"callId": "test-001", "event": "hangup", "from": "+49301234567", "transcription": "Customer inquiry"}'

# Test WhatsApp webhook
apify call cdtech~mail2zapier2apify2gpt2onedrive --input '{"message_type": "text", "sender_phone": "+49175123456", "message_text": "Website inquiry"}'

# Test email processing via Railway
curl -X POST https://my-langgraph-agent-production.up.railway.app/webhook/email \
  -H "Content-Type: application/json" \
  -d '{"subject": "Test", "body_content": "Test message", "from_email_address_address": "test@example.com"}'
```

### Railway Deployment
```bash
# Check deployment status
railway status
railway logs --tail

# Environment variables required
export ORCHESTRATOR_URL="https://my-langgraph-agent-production.up.railway.app"
export RAILWAY_INTEGRATION="true"
export OPENAI_API_KEY="your_key"
```

### Apify Actor Development
```bash
# Deploy new actor version
apify push

# Test locally
apify run --input-file input.json

# Version management: main.py → main_v34X.py for each version
```

## Project-Specific Patterns

### Webhook Source Detection
The system auto-detects input source using `detect_webhook_source()` in `src/main.py`:
- **SipGate**: Look for `callId`, `event`, `from`, `to` keys
- **WhatsApp**: Look for `message_type`, `sender_phone`, `chat_id` keys  
- **Email**: Look for `body_content`, `subject`, `from_email_address_address` keys

### Workflow Routing (WEG_A vs WEG_B)
Critical business logic in Railway orchestrator:
- **WEG_A**: Unknown contacts → Lead generation workflow
- **WEG_B**: Known contacts → Opportunity progression based on WeClapp status
- Route determined by `modules/weclapp/weclapp_handler.py` contact matching

### Document Processing Pipeline
1. **Download** (`modules/download/`) → **OCR** (`modules/ocr/`) → **GPT Classification** (`modules/gpt/classify_document_with_gpt.py`) → **OneDrive Upload** (`modules/upload/`)
2. Document types auto-detected: `invoice`, `offer`, `delivery_note`, `contract` via GPT-4 analysis
3. Folder structure auto-generated in `modules/filegen/folder_logic.py`

### Price Estimation Engine
Phone calls trigger automatic price estimation using `modules/pricing/estimate_from_call.py`:
- Analyzes call transcripts for project scope
- Returns structured estimates (e.g., "120m² roof = €19,200")
- Integrated into CRM opportunity creation

## Critical Integration Points

### WeClapp CRM
- Contact lookup by email/phone: `modules/weclapp/weclapp_handler.py`
- Opportunity status drives action generation (8 sales pipeline phases)
- Communication logging for all channels

### Database Layer
- SQLite for local caching: `modules/database/email_tracking_db.py`
- Email deduplication via message_id tracking
- Attachment metadata storage

### External APIs
- **PDF.co**: OCR processing with multipart upload pattern
- **Microsoft Graph**: Email/attachment download and OneDrive upload
- **OpenAI GPT-4**: Document classification and intent analysis
- **SipGate**: Call webhook processing and transcription

## Error Handling Patterns

### Memory Management
Railway container has 512MB-1GB RAM limits. Use:
- `REQUEST_SEMAPHORE = Semaphore(3)` for concurrent request limiting
- Streaming for large file processing
- Immediate memory cleanup after processing

### Graceful Degradation
- If WeClapp API fails → Fall back to Apify contact database
- If Railway orchestrator fails → Direct email processing
- Version compatibility maintained across `main_v34*.py` files

## Key Files to Reference

- `production_langgraph_orchestrator.py`: Main Railway server with LangGraph state management
- `src/main_v341.py`: Latest Apify actor with webhook extensions
- `MASTER_PLAN_FINAL_2025-10-17.md`: Complete system documentation
- `ARCHITECTURE_DECISION_FINAL.md`: Architecture decisions and component catalog
- `modules/*/`: Specialized processing modules (20+ directories)
- `input_schema_v341.json`: API contract definition