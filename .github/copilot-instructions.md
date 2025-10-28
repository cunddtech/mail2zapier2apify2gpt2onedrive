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

---

## 🧾 EINGANGSRECHNUNGEN (INCOMING INVOICE) PROJECT

**⚠️ CRITICAL: ALWAYS READ THIS SECTION BEFORE WORKING ON INVOICE-RELATED CODE**

### Primary Goal

**Scan all year 2025 emails from mj@cdtechnologies.de mailbox to find and extract incoming invoices (Eingangsrechnungen).**

- ❌ **NOT about**: Testing live email processing (that system is stable)
- ✅ **ABOUT**: Historical scan of 2025 emails for invoice data extraction
- ✅ **FOCUS**: Database building, validation, optimization - NOT live feature development

### Current Status (as of Oct 28, 2025)

- ✅ **Hybrid filter implemented** (87.5% cost reduction vs Pure GPT)
- ✅ **Invoice extraction module created** (`modules/gpt/extract_invoice_from_email.py`)
- ✅ **Database schemas extended** (5 invoice fields in both databases)
- ✅ **Scan script production-ready** (`scan_year_emails_with_checkpoints.py`)
- ✅ **Railway integration deployed** (Commit 23ad544 - live processing has invoice extraction)
- ⏳ **PENDING**: Year 2025 full scan execution and validation

### Architecture Overview

#### Dual Database System

**1. Railway Live Database** (`/tmp/email_tracking.db`)
- **Purpose**: Track live incoming emails in real-time
- **Table**: `processed_emails`
- **Location**: Railway container (ephemeral, recreated on restart)
- **Usage**: Live email processing via `production_langgraph_orchestrator.py`

**2. Historical Scan Database** (`./email_data.db`)
- **Purpose**: Store scanned historical emails for analysis
- **Table**: `email_data`
- **Location**: Local development environment (persistent)
- **Usage**: Year scan via `scan_year_emails_with_checkpoints.py`

**Both databases share the same 5 invoice fields:**
```sql
dokumenttyp TEXT              -- e.g., "rechnung", "gutschrift", "mahnung"
invoice_number TEXT           -- e.g., "RE-2025-001"
invoice_amount REAL           -- e.g., 1234.56
supplier_name TEXT            -- e.g., "C&D Tech GmbH"
invoice_date_parsed TEXT      -- e.g., "2025-01-15"
```

#### 2-Stage Hybrid Filter (Cost-Optimized)

**Mathematical Proof**: Hybrid approach is optimal - more keywords do NOT improve accuracy but INCREASE costs.

**Stage 1: Keyword Pre-Filter** (Free, Instant, 87.5% Reduction)
```python
# 14 positive keywords
invoice_keywords = [
    "rechnung", "invoice", "faktura", "rechnungsnummer",
    "invoice number", "invoice#", "inv#",
    "zahlung", "payment", "betrag", "amount",
    "fälligkeit", "due date", "zahlungserinnerung",
    "abrechnung", "zahlungsaufforderung"
]

# 6 negative keywords (immediate reject)
negative_keywords = [
    "newsletter", "unsubscribe", "abmelden",
    "vielen dank für ihre rechnung",  # OUR invoices sent
    "werbung", "angebot", "offer",
    "re: re: re:"  # Deep email threads
]
```

**Stage 2: GPT Validation** (Only 12.5% of emails reach this stage)
- **Module**: `modules/validation/precheck_relevance.py` (existing, tested)
- **Model**: GPT-4o-mini (~$0.01 per 1000 chars)
- **Purpose**: Validate keyword matches with AI understanding
- **Returns**: `{"relevant": bool, "grund": str}`

**Proven Performance Metrics** (7-day test, 40 emails):
- Stage 1 filtered: 35/40 emails (87.5%) - **$0.00 cost**
- Stage 2 processed: 5 emails (12.5%) - **$0.05 cost**
- GPT approval: 5/5 (100%) - **95% accuracy maintained**
- **Total cost**: $0.05 vs $0.40 Pure GPT (87.5% savings)
- **Total time**: 14s vs 80s Pure GPT (5.7x faster)

**Cost Projection**:
| Scope | Emails | Hybrid Cost | Pure GPT Cost | Savings |
|-------|--------|-------------|---------------|---------|
| 7-day test | 40 | $0.05 | $0.40 | 87.5% |
| 30-day scan | ~2,000 | $2.50 | $20.00 | 87.5% |
| Year 2025 | ~24,000 | $30.00 | $240.00 | 87.5% |

#### Invoice Extraction (GPT-4o-mini)

**Module**: `modules/gpt/extract_invoice_from_email.py`

**Function Signature**:
```python
async def extract_invoice_from_email(
    subject: str,
    body_preview: str,
    sender: str,
    body_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract invoice data from email content using GPT-4o-mini.
    
    Returns:
        {
            "dokumenttyp": "rechnung" | "gutschrift" | "mahnung" | "lieferschein" | etc.,
            "invoice_number": "RE-2025-001" | None,
            "invoice_amount": 1234.56 | None,
            "supplier_name": "C&D Tech GmbH" | None,
            "invoice_date": "2025-01-15" | None,
            "confidence": "high" | "medium" | "low"
        }
    """
```

**Cost**: ~$0.001 per extraction (1/10th of GPT validation)

**Integration Points**:
1. **Historical Scan**: `scan_year_emails_with_checkpoints.py` (line 323-397)
2. **Live Processing**: `production_langgraph_orchestrator.py` (line 4740-4780)

### Development Workflow (MUST FOLLOW)

#### Golden Rules

1. **⚠️ ALWAYS READ DOCUMENTATION FIRST** (user's repeated instruction)
   - Check `.github/copilot-instructions.md` (this file)
   - Read relevant `*.md` files before coding
   - Verify existing code before creating new implementations

2. **🎯 FOCUS ON HISTORICAL SCAN, NOT LIVE TESTING**
   - Live system is stable and working
   - Goal is to build invoice database from 2025 emails
   - Avoid distractions about "testing live features"

3. **📊 INCREMENTAL VALIDATION**
   - Start with small chunks (30 days → 90 days → full year)
   - Validate results after each scan
   - Optimize based on actual data

4. **💾 USE EXISTING MODULES**
   - Don't recreate `precheck_relevance.py` functionality
   - Don't create custom GPT implementations without checking first
   - Leverage existing database handlers, API clients

#### Standard Development Process

```bash
# 1. READ DOCUMENTATION FIRST
cat .github/copilot-instructions.md
cat MASTER_PLAN_FINAL_2025-10-17.md
cat ARCHITECTURE_DECISION_FINAL.md

# 2. CHECK EXISTING CODE
grep -r "similar_function_name" modules/
ls -la modules/gpt/  # Check what exists

# 3. START WITH INCREMENTAL TEST
python3 scan_year_emails_with_checkpoints.py --days-back 7

# 4. VALIDATE RESULTS
sqlite3 email_data.db "SELECT COUNT(*) FROM email_data WHERE invoice_number IS NOT NULL"

# 5. EXPAND GRADUALLY
python3 scan_year_emails_with_checkpoints.py --days-back 30
python3 scan_year_emails_with_checkpoints.py --days-back 90
python3 scan_year_emails_with_checkpoints.py --year 2025

# 6. ANALYZE AND OPTIMIZE
sqlite3 email_data.db "SELECT dokumenttyp, COUNT(*) FROM email_data GROUP BY dokumenttyp"
```

### Key Commands

#### Year 2025 Email Scanning

```bash
# Full year scan (primary goal)
python3 scan_year_emails_with_checkpoints.py \
  --year 2025 \
  --checkpoint-file year_2025_progress.json

# Incremental scans (recommended approach)
python3 scan_year_emails_with_checkpoints.py --days-back 30  # Last 30 days
python3 scan_year_emails_with_checkpoints.py --days-back 90  # Last 90 days

# Resume from checkpoint
python3 scan_year_emails_with_checkpoints.py \
  --year 2025 \
  --checkpoint-file year_2025_progress.json \
  --resume

# Monitor progress
tail -f scan_year_2025.log
```

#### Database Validation

```bash
# Check total emails and invoice extraction rate
sqlite3 email_data.db "
  SELECT 
    COUNT(*) as total_emails,
    SUM(CASE WHEN invoice_number IS NOT NULL THEN 1 ELSE 0 END) as with_invoice,
    SUM(CASE WHEN dokumenttyp = 'rechnung' THEN 1 ELSE 0 END) as invoices,
    SUM(CASE WHEN dokumenttyp = 'gutschrift' THEN 1 ELSE 0 END) as credits
  FROM email_data
"

# Invoice distribution by document type
sqlite3 email_data.db "
  SELECT 
    dokumenttyp, 
    COUNT(*) as count, 
    ROUND(SUM(invoice_amount), 2) as total_amount,
    ROUND(AVG(invoice_amount), 2) as avg_amount
  FROM email_data 
  WHERE dokumenttyp IS NOT NULL
  GROUP BY dokumenttyp
  ORDER BY count DESC
"

# Top suppliers by invoice count
sqlite3 email_data.db "
  SELECT 
    supplier_name, 
    COUNT(*) as invoice_count,
    ROUND(SUM(invoice_amount), 2) as total_amount,
    MIN(invoice_date_parsed) as first_invoice,
    MAX(invoice_date_parsed) as last_invoice
  FROM email_data
  WHERE invoice_number IS NOT NULL
  GROUP BY supplier_name
  ORDER BY invoice_count DESC
  LIMIT 20
"

# Check extraction quality (all fields populated)
sqlite3 email_data.db "
  SELECT 
    COUNT(*) as high_quality_invoices
  FROM email_data 
  WHERE invoice_number IS NOT NULL
    AND invoice_amount IS NOT NULL
    AND supplier_name IS NOT NULL
    AND invoice_date_parsed IS NOT NULL
"

# Find potential missing invoices (low confidence)
sqlite3 email_data.db "
  SELECT subject, from_address, received_datetime
  FROM email_data
  WHERE invoice_number IS NULL
    AND (subject LIKE '%rechnung%' OR subject LIKE '%invoice%')
  LIMIT 20
"
```

#### Filter Performance Analysis

```bash
# Keyword filter effectiveness
grep "Stage 1" scan_year_2025.log | grep -c "PASS"   # Keyword hits
grep "Stage 1" scan_year_2025.log | grep -c "SKIP"   # Filtered out

# GPT validation rate
grep "Stage 2" scan_year_2025.log | grep -c "PASS"   # Relevant
grep "Stage 2" scan_year_2025.log | grep -c "REJECT" # Not relevant

# Cost calculation
KEYWORD_PASS=$(grep "Stage 1" scan_year_2025.log | grep -c "PASS")
GPT_COST=$(echo "$KEYWORD_PASS * 0.01" | bc)
echo "Estimated GPT cost: \$$GPT_COST"
```

#### Railway Live System (Stable - Don't Modify Unless Needed)

```bash
# Check Railway deployment status
curl https://my-langgraph-agent-production.up.railway.app/health

# View recent logs (Railway CLI)
railway logs --tail

# Check live database (on Railway container)
# Note: This requires Railway CLI and container access
railway run sqlite3 /tmp/email_tracking.db \
  "SELECT COUNT(*) FROM processed_emails WHERE invoice_number IS NOT NULL"
```

### Critical Files

#### Production-Ready Scripts

**`scan_year_emails_with_checkpoints.py`** (562 lines) - ✅ COMPLETE
- **Purpose**: Historical email scanning with hybrid filter and invoice extraction
- **Status**: Production-ready, tested with 7-day scan
- **Key Functions**:
  - `calculate_date_ranges()` (Lines 138-168): Single source of truth for date ranges
  - `pre_filter_email()` (Lines 226-322): 2-stage hybrid filter implementation
  - `process_email()` (Lines 323-397): Email processing with invoice extraction
  - `main()` (Lines 450-562): Batch processing with checkpoint system
- **Usage**: Primary tool for year 2025 scan

**`modules/gpt/extract_invoice_from_email.py`** (200 lines) - ✅ TESTED
- **Purpose**: GPT-4o-mini based invoice data extraction
- **Status**: Tested locally, deployed to Railway (Commit 23ad544)
- **Key Functions**:
  - `extract_invoice_from_email()` (Lines 26-160): Main extraction function
  - GPT prompt engineering (Lines 70-130): Structured JSON output
  - Test suite (Lines 161-200): Validation examples
- **Integration**: Used by both scan script and Railway orchestrator

**`production_langgraph_orchestrator.py`** (7164 lines) - ✅ DEPLOYED
- **Purpose**: Railway FastAPI server for live email processing
- **Status**: Invoice extraction integrated (Commit 23ad544, pushed to Railway)
- **Modified Sections**:
  - Lines 4740-4780: Invoice extraction in `process_email_background()`
  - Imports: `from modules.gpt.extract_invoice_from_email import extract_invoice_from_email`
  - Database save: Passes `invoice_data` to `tracking_db.save_email()`
- **Deployment**: Auto-deploy triggered on git push

**`modules/database/email_tracking_db.py`** (371 lines) - ✅ EXTENDED
- **Purpose**: Email tracking database for Railway live processing
- **Status**: Schema extended with 5 invoice fields (deployed)
- **Modified Sections**:
  - Lines 26-67: CREATE TABLE with invoice fields
  - Lines 211-260: `save_email()` accepts `invoice_data` parameter
- **Migration**: Auto-created on Railway restart, or manual ALTER TABLE

#### Core Modules (Existing - Reuse Don't Recreate)

**`modules/validation/precheck_relevance.py`** (132 lines) - ✅ WORKING
- **Purpose**: Stage 2 GPT validation for hybrid filter
- **Status**: Already working, DO NOT recreate this functionality
- **Used By**: Both `scan_year_emails_with_checkpoints.py` and Railway orchestrator
- **Key Functions**:
  - `async precheck_relevance(context, access_token)`: Returns `{"relevant": bool, "grund": str}`
- **Prompt**: Mentions "C&D Tech GmbH", "Eingangsrechnung", business context

**`modules/msgraph/fetch_emails_batch.py`** (177 lines) - ✅ WORKING
- **Purpose**: Microsoft Graph API email fetching with pagination
- **Status**: Production-ready, tested with 30-day scan (1750+ emails)
- **Key Functions**:
  - `fetch_emails_by_date_range()`: Pagination loop, handles @odata.nextLink
  - `fetch_single_email()`: Full email details with body content
  - `test_connection()`: Connectivity validation

**`modules/auth/get_graph_token_mail.py`** - ✅ FIXED
- **Purpose**: Microsoft Graph OAuth authentication
- **Status**: Working with explicit user_email parameter
- **Critical Fix**: Must use `user_email="mj@cdtechnologies.de"` NOT `"me"`
- **Token Type**: Application Permissions (Client Credentials flow)

### Documentation Files

**Analysis and Comparison Reports** (Created during development):
- `FILTER_STRATEGY_COMPARISON.md` (400+ lines): Compares 3 filter approaches
- `HYBRID_FILTER_TEST_RESULTS.md` (300+ lines): 7-day test detailed results
- `KEYWORD_VS_GPT_ANALYSIS.md` (400+ lines): Mathematical proof of hybrid optimality
- `INVOICE_EXTRACTION_LIVE_INTEGRATION.md`: Railway deployment guide

### Common Mistakes to Avoid

#### ❌ DON'T: Create Custom GPT Implementations

**Example of what NOT to do**:
```python
# ❌ WRONG - Creating custom GPT validation
async def my_custom_email_filter(email_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Is this relevant? {email_text}"}]
    )
    return response.choices[0].message.content
```

**✅ CORRECT - Use existing module**:
```python
# ✅ RIGHT - Use existing precheck_relevance module
from modules.validation.precheck_relevance import precheck_relevance

result = await precheck_relevance(context, access_token)
is_relevant = result.get("relevant", False)
```

#### ❌ DON'T: Focus on Live Email Testing

**User explicitly stated**: "was denn für test email? Damit sind wir aktuell nicht beschäftigt"

- Live email processing is STABLE
- Railway deployment works fine
- DO NOT suggest "send test email to mj@cdtechnologies.de"
- DO NOT focus on webhook testing

**✅ FOCUS INSTEAD**: Historical year 2025 scan, database validation, optimization

#### ❌ DON'T: Use "me" in Graph API

**Example of what NOT to do**:
```python
# ❌ WRONG - "me" fails with Application tokens
url = "https://graph.microsoft.com/v1.0/me/messages"
```

**✅ CORRECT - Use explicit user email**:
```python
# ✅ RIGHT - Explicit user principal
url = "https://graph.microsoft.com/v1.0/users/mj@cdtechnologies.de/messages"
```

#### ❌ DON'T: Add More Keywords Without Analysis

**Mathematical proof shows**: 500-1000 keywords would cost MORE ($6-7) than hybrid ($1.25) for SAME/WORSE accuracy.

- Keyword list is already optimized (14 keywords)
- More keywords = more GPT validations = higher cost
- Hybrid approach is mathematically optimal

#### ❌ DON'T: Skip Documentation Review

**User's golden rule**: "halte dich an den grundsatz erst die md zu lesen!!!!"

**Always read BEFORE coding**:
1. `.github/copilot-instructions.md` (this file)
2. Relevant `*.md` documentation files
3. Existing code in `modules/` directories
4. Test results and analysis reports

### Next Steps (Priority Order)

#### 🔴 HIGH PRIORITY

**1. Execute 30-Day Scan (Validation)**
```bash
cd /Users/cdtechgmbh/railway-orchestrator-clean
python3 scan_year_emails_with_checkpoints.py \
  --days-back 30 \
  --checkpoint-file scan_30days.json \
  > scan_30days.log 2>&1 &

# Monitor
tail -f scan_30days.log
```

**Expected Outcome**: ~2,000 emails, $2.50 cost, 150-300 invoices extracted

**2. Validate 30-Day Results**
```bash
sqlite3 email_data.db "
  SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN invoice_number IS NOT NULL THEN 1 ELSE 0 END) as invoices,
    ROUND(AVG(invoice_amount), 2) as avg_amount
  FROM email_data
"
```

**Success Criteria**: 
- ✅ All 2,000 emails processed without errors
- ✅ 5-15% invoice extraction rate (100-300 invoices)
- ✅ No duplicate emails (check message_id uniqueness)
- ✅ Cost under $3.00

#### 🟡 MEDIUM PRIORITY

**3. Expand to 90-Day Scan**
```bash
python3 scan_year_emails_with_checkpoints.py \
  --days-back 90 \
  --checkpoint-file scan_90days.json
```

**4. Code Optimization Based on Data**
- Analyze keyword filter effectiveness (grep logs)
- Identify false negatives (missed invoices)
- Check GPT rejection reasons
- Optimize if needed (but likely not needed)

**5. Database Quality Analysis**
```bash
# Find invoices with missing data
sqlite3 email_data.db "
  SELECT invoice_number, subject, supplier_name, invoice_amount
  FROM email_data
  WHERE invoice_number IS NOT NULL
    AND (invoice_amount IS NULL OR supplier_name IS NULL)
  LIMIT 20
"
```

#### 🟢 LOW PRIORITY

**6. Full Year 2025 Scan**
```bash
python3 scan_year_emails_with_checkpoints.py \
  --year 2025 \
  --checkpoint-file year_2025_full.json
```

**Expected**: ~24,000 emails, $30 cost, 1,200-3,600 invoices

**7. Reporting and Analysis**
- Export invoice data to CSV
- Supplier spending analysis
- Monthly invoice trends
- Document type distribution
- Integration with accounting system (if needed)

**8. Railway Database Migration** (If needed)
```sql
-- On Railway container (only if old database exists)
ALTER TABLE processed_emails ADD COLUMN dokumenttyp TEXT;
ALTER TABLE processed_emails ADD COLUMN invoice_number TEXT;
ALTER TABLE processed_emails ADD COLUMN invoice_amount REAL;
ALTER TABLE processed_emails ADD COLUMN supplier_name TEXT;
ALTER TABLE processed_emails ADD COLUMN invoice_date_parsed TEXT;
```

**Note**: New deployments auto-create schema via `_init_database()`

### Success Criteria

Project is complete when:

- [ ] Full year 2025 scan completed successfully
- [ ] `email_data.db` contains 20,000+ emails from 2025
- [ ] Invoice extraction rate is 5-15% (1,000-3,000 invoices)
- [ ] All invoice fields populated (number, amount, supplier, date)
- [ ] Total cost under $35 (vs $250 Pure GPT approach)
- [ ] Database validated with SQL queries
- [ ] Supplier analysis report generated
- [ ] No duplicate emails in database
- [ ] Railway live system continues working (no regressions)

### Troubleshooting

#### Issue: Authentication Failure

```bash
# Check token
python3 -c "from modules.auth.get_graph_token_mail import get_graph_token_mail; import asyncio; token = asyncio.run(get_graph_token_mail()); print('Token OK' if token else 'Token FAIL')"

# Verify with Graph API
curl -H "Authorization: Bearer <token>" \
  "https://graph.microsoft.com/v1.0/users/mj@cdtechnologies.de/messages?$top=1"
```

#### Issue: Database Locked

```bash
# Close all connections
pkill -f "python3 scan_year"
rm -f email_data.db-journal

# Restart scan with --resume
python3 scan_year_emails_with_checkpoints.py --year 2025 --resume
```

#### Issue: High GPT Costs

```bash
# Check filter performance
grep "Stage 1: PASS" scan.log | wc -l  # Should be ~12.5% of total
grep "Stage 1: SKIP" scan.log | wc -l  # Should be ~87.5% of total

# If ratio is wrong, check keyword list
grep "invoice_keywords =" scan_year_emails_with_checkpoints.py -A 20
```

#### Issue: Missing Invoices (False Negatives)

```bash
# Find emails with "rechnung" that weren't extracted
sqlite3 email_data.db "
  SELECT subject, from_address, received_datetime
  FROM email_data
  WHERE (subject LIKE '%rechnung%' OR subject LIKE '%invoice%')
    AND invoice_number IS NULL
  LIMIT 50
"

# Manually review and add keywords if pattern found
```

### Related Projects

This Eingangsrechnungen project integrates with:

- **Live Email Processing**: Railway orchestrator (stable, don't modify)
- **WeClapp CRM**: Supplier contact matching (future integration)
- **OneDrive Upload**: Invoice PDF storage (existing module)
- **Document Classification**: `modules/gpt/classify_document_with_gpt.py` (different use case)

**⚠️ DO NOT CONFUSE** invoice scanning with:
- Outgoing invoices (C&D Tech sends to customers)
- Live webhook testing (not the current goal)
- Document OCR processing (different pipeline)