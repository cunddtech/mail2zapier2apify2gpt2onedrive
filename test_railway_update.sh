#!/bin/bash
# Test Script nach Railway Update

echo "🔍 Testing Railway after update..."

# Warte kurz für deployment
sleep 30

# Test AI Analysis
echo "📧 Testing Email with AI Analysis..."
curl -X POST "https://my-langgraph-agent-production.up.railway.app/webhook/ai-email" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "POST-UPDATE-TEST", 
    "sender": "ai-test@example.com",
    "subject": "AI Analysis Test nach Update",
    "content": "Hallo, ich brauche dringend IT-Beratung für mein Startup. Budget: 75000 Euro. Kann ich heute noch ein Gespräch haben?"
  }' | jq '.'

echo ""
echo "📞 Testing SipGate Call..."
curl -X POST "https://my-langgraph-agent-production.up.railway.app/webhook/ai-call" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+49-30-UPDATE-TEST", 
    "to": "+49-40-12345678",
    "direction": "incoming",
    "timestamp": "2025-10-11T06:00:00Z"
  }' | jq '.'

echo ""
echo "✅ Tests complete! Check if ai_analysis now has proper JSON instead of error."