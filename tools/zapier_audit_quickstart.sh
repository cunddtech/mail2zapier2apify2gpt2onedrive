#!/bin/bash
# Zapier Filter Audit - Quick Start Script

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🔧 ZAPIER FILTER AUDIT - QUICK START                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if API key is set
if [ -z "$ZAPIER_API_KEY" ]; then
    echo "❌ Error: ZAPIER_API_KEY not set!"
    echo ""
    echo "📋 TO FIX:"
    echo "1. Go to: https://zapier.com/app/settings/api"
    echo "2. Click: 'Generate API Key'"
    echo "3. Copy the key"
    echo "4. Run:"
    echo "   export ZAPIER_API_KEY='your-key-here'"
    echo ""
    echo "5. Then run this script again:"
    echo "   ./tools/zapier_audit_quickstart.sh"
    echo ""
    exit 1
fi

echo "✅ API Key found: ${ZAPIER_API_KEY:0:10}...${ZAPIER_API_KEY: -10}"
echo ""

# Check if requests is installed
echo "📦 Checking Python dependencies..."
python3 -c "import requests" 2>/dev/null || {
    echo "⚠️  requests library not found"
    echo "📦 Installing requests..."
    pip3 install requests
}
echo "✅ Dependencies OK"
echo ""

# Run the audit script
echo "🔍 Running Zapier Filter Audit..."
echo "─────────────────────────────────────────────────────────────"
echo ""

python3 tools/zapier_filter_audit.py

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "✅ Audit complete!"
echo ""
echo "📋 CHECK THESE FILES:"
echo "   • zapier_filter_audit_report.txt  (Human-readable report)"
echo "   • zapier_filter_audit_data.json   (JSON data)"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Open: zapier_filter_audit_report.txt"
echo "2. For each Zap with Filter:"
echo "   → Open in Zapier UI"
echo "   → Find Filter step"
echo "   → Change 'Does not start with' to 'Does not contain'"
echo "   → Test & Publish"
echo ""
echo "📚 See also:"
echo "   • ZAPIER_FIX_FÜR_DEINE_ZAPS.md (Manual fix guide)"
echo "   • ZAPIER_MANUAL_FIX_ANLEITUNG.md (Detailed steps)"
echo ""
