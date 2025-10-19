#!/bin/bash
# 🚀 QUICK TEST EXECUTION SCRIPT
# ==============================

echo "🧪 RAILWAY WEBHOOK TEST SUITE"
echo "=============================="
echo ""

# Change to test_suite directory
cd "$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Menu
echo "Welches Test-Szenario möchtest du ausführen?"
echo ""
echo "📧 EMAIL TESTS (bereits empfangene Emails):"
echo "  1) Eingangsrechnungen (10 Emails)"
echo "  2) Angebote & Preisanfragen (5 Emails)"
echo "  3) Auftragsbestätigungen (3 Emails)"
echo "  4) Lieferscheine (3 Emails)"
echo "  5) Allgemeine Anfragen (5 Emails)"
echo "  6) Multi-Attachment Emails (2 Emails)"
echo "  7) ALLE Email Szenarien (30+ Emails)"
echo ""
echo "📞 CALL TESTS (Live oder Mock):"
echo "  8) Inbound Call - Bekannter Kontakt"
echo "  9) Inbound Call - Unbekannter Kontakt"
echo " 10) Outbound Call"
echo " 11) FrontDesk Integration"
echo " 12) Long Call mit Action Items"
echo " 13) ALLE Call Szenarien"
echo ""
echo "🔄 INTEGRATION TESTS:"
echo " 14) Email → Invoice DB → Dashboard"
echo " 15) Call → CRM → Task"
echo " 16) WhatsApp → Opportunity"
echo ""
echo "  0) Exit"
echo ""

read -p "Wähle eine Option (0-16): " choice

case $choice in
    1)
        echo -e "${GREEN}📄 Testing Eingangsrechnungen...${NC}"
        python3 test_email_scenarios.py --scenario invoice --count 10 --verbose
        ;;
    2)
        echo -e "${GREEN}💰 Testing Angebote & Preisanfragen...${NC}"
        python3 test_email_scenarios.py --scenario offer --count 5 --verbose
        ;;
    3)
        echo -e "${GREEN}✅ Testing Auftragsbestätigungen...${NC}"
        python3 test_email_scenarios.py --scenario order_confirmation --count 3 --verbose
        ;;
    4)
        echo -e "${GREEN}📦 Testing Lieferscheine...${NC}"
        python3 test_email_scenarios.py --scenario delivery_note --count 3 --verbose
        ;;
    5)
        echo -e "${GREEN}📧 Testing Allgemeine Anfragen...${NC}"
        python3 test_email_scenarios.py --scenario general --count 5 --verbose
        ;;
    6)
        echo -e "${GREEN}📎 Testing Multi-Attachment Emails...${NC}"
        python3 test_email_scenarios.py --scenario multi_attachment --count 2 --verbose
        ;;
    7)
        echo -e "${GREEN}🔥 Testing ALLE Email Szenarien...${NC}"
        python3 test_email_scenarios.py --scenario all --count 50
        ;;
    8)
        echo -e "${YELLOW}📞 Testing Inbound Call - Bekannter Kontakt${NC}"
        echo -e "${YELLOW}⚠️  HINWEIS: Bitte bekannte Telefonnummer in WeClapp prüfen${NC}"
        read -p "Bekannte Telefonnummer (z.B. +4930123456): " known_phone
        python3 test_call_scenarios_live.py --scenario known --known-phone "$known_phone"
        ;;
    9)
        echo -e "${YELLOW}⚠️  Testing Inbound Call - Unbekannter Kontakt${NC}"
        read -p "Unbekannte Telefonnummer (z.B. +491234567890): " unknown_phone
        python3 test_call_scenarios_live.py --scenario unknown --unknown-phone "$unknown_phone"
        ;;
    10)
        echo -e "${YELLOW}📤 Testing Outbound Call${NC}"
        python3 test_call_scenarios_live.py --scenario outbound
        ;;
    11)
        echo -e "${YELLOW}📱 Testing FrontDesk Integration${NC}"
        python3 test_call_scenarios_live.py --scenario frontdesk
        ;;
    12)
        echo -e "${YELLOW}⏱️  Testing Long Call mit Action Items${NC}"
        python3 test_call_scenarios_live.py --scenario long
        ;;
    13)
        echo -e "${YELLOW}🔥 Testing ALLE Call Szenarien${NC}"
        echo -e "${RED}⚠️  ACHTUNG: Benötigt konfigurierte Kontakte in WeClapp!${NC}"
        read -p "Fortfahren? (y/n): " confirm
        if [ "$confirm" == "y" ]; then
            python3 test_call_scenarios_live.py --scenario all
        fi
        ;;
    14)
        echo -e "${GREEN}🔄 Testing Email → Invoice DB → Dashboard${NC}"
        python3 test_integration.py --flow email-invoice-dashboard
        ;;
    15)
        echo -e "${GREEN}🔄 Testing Call → CRM → Task${NC}"
        python3 test_integration.py --flow call-crm-task
        ;;
    16)
        echo -e "${GREEN}🔄 Testing WhatsApp → Opportunity${NC}"
        python3 test_integration.py --flow whatsapp-opportunity
        ;;
    0)
        echo "Bye! 👋"
        exit 0
        ;;
    *)
        echo -e "${RED}Ungültige Option!${NC}"
        exit 1
        ;;
esac

echo ""
echo "✅ Test abgeschlossen!"
echo ""
echo "📊 Test Results gespeichert in: test_results/"
echo "🌐 Dashboard: http://localhost:3000"
echo "🚀 Railway: https://my-langgraph-agent-production.up.railway.app"
echo ""
