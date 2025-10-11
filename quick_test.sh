#!/bin/bash
echo "🧪 QUICK TEST - Railway Update Erfolg prüfen"
echo "=============================================="

echo "📧 Testing Email Processing..."
RESULT=$(curl -s -X POST "https://my-langgraph-agent-production.up.railway.app/webhook/ai-email" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "UPDATE-SUCCESS-TEST", 
    "sender": "success@test.com",
    "subject": "Railway Update Test",
    "content": "Test ob AI Analysis jetzt funktioniert. Brauche dringend Hilfe mit IT-Projekt, Budget 25000 Euro."
  }')

echo "📊 RESULT:"
echo "$RESULT" | python3 -m json.tool

# Check if AI analysis has proper JSON instead of error
if echo "$RESULT" | grep -q '"error":.*intent'; then
    echo "❌ NOCH IMMER JSON ERROR - Update fehlgeschlagen"
    echo "Versuche nächste Option!"
else
    echo "✅ AI ANALYSIS FUNKTIONIERT - Update erfolgreich!"
    echo "🎉 JSON Problem gelöst!"
fi
