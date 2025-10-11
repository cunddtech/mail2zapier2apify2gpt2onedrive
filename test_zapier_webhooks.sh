#!/bin/bash
# Zapier Integration Test Script
# Testet alle Production Webhooks

BASE_URL="https://my-langgraph-agent-production.up.railway.app"

echo "🧪 Testing Railway Production Webhooks"
echo "======================================="
echo ""

# Test 1: Status Check
echo "1️⃣  Testing Status Endpoint..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/status")
if [ "$STATUS" -eq 200 ]; then
    echo "✅ Status Endpoint: OK ($STATUS)"
    curl -s "$BASE_URL/status" | python3 -m json.tool 2>/dev/null
else
    echo "❌ Status Endpoint: FAILED ($STATUS)"
fi
echo ""

# Test 2: Email Webhook
echo "2️⃣  Testing Email Webhook..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/webhook/ai-email" \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "zapier-test@example.com",
    "sender_name": "Zapier Test User",
    "subject": "Test: Zapier Integration Check",
    "body": "This is an automated test to verify the Zapier integration is working correctly.",
    "attachments": [],
    "received_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ Email Webhook: OK ($HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null | head -20
else
    echo "❌ Email Webhook: FAILED ($HTTP_CODE)"
    echo "$BODY"
fi
echo ""

# Test 3: Call Webhook
echo "3️⃣  Testing Call Webhook..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/webhook/ai-call" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "newCall",
    "direction": "in",
    "from": "+4915199999999",
    "to": "+49301234567",
    "callId": "test-zapier-'$(date +%s)'",
    "user": ["test@company.de"],
    "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ Call Webhook: OK ($HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null | head -20
else
    echo "❌ Call Webhook: FAILED ($HTTP_CODE)"
    echo "$BODY"
fi
echo ""

# Test 4: WhatsApp Webhook
echo "4️⃣  Testing WhatsApp Webhook..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/webhook/ai-whatsapp" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+4915199999999",
    "message": "Test message from Zapier integration check",
    "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
    "message_id": "zapier-test-'$(date +%s)'"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ WhatsApp Webhook: OK ($HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null | head -20
else
    echo "❌ WhatsApp Webhook: FAILED ($HTTP_CODE)"
    echo "$BODY"
fi
echo ""

echo "======================================="
echo "🎯 Test Summary:"
echo "   - Check Railway logs for processing details"
echo "   - Verify Zapier notifications were sent"
echo "   - All webhooks should return success: true"
echo ""
echo "📊 View logs: railway logs --lines 50"
echo "🔗 Zapier setup: See ZAPIER_INTEGRATION_GUIDE.md"
