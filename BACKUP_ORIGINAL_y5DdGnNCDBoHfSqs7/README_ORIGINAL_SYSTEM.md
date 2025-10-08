# 🎯 BACKUP: Original Autarkes Email System 
**Build ID:** y5DdGnNCDBoHfSqs7  
**Backup Date:** 8. Oktober 2025  
**Reason:** Preserve original autarke system before microservice split

## 🚀 Original System Features:
- ✅ **Komplett autarke Apify App** - keine externen Dependencies
- ✅ **WeClapp CRM Integration** - vollständige API Integration
- ✅ **SQLite Email Database** - lokale Datenspeicherung
- ✅ **Microsoft Graph API** - Mail + OneDrive Integration
- ✅ **OpenAI GPT-4** - Dokumentenanalyse und Klassifikation
- ✅ **PDF.co OCR** - Scan-Verarbeitung
- ✅ **Automatische Ordnerstrukturen** - OneDrive File Management
- ✅ **Komplette Email Workflows** - End-to-End Processing

## 📁 Module Structure:
```
modules/
├── auth/                 # Graph Token Management
├── weclapp/             # WeClapp CRM Integration  
├── database/            # SQLite Email Database
├── msgraph/             # Microsoft Graph API
├── gpt/                 # OpenAI GPT Integration
├── ocr/                 # PDF.co OCR Integration
├── mail/                # Email Processing Workflows
├── filegen/             # OneDrive Folder Generation
├── upload/              # File Upload Management
├── utils/               # Helper Functions
└── validation/          # Input Validation
```

## 🔧 Key Components:
- **src/main.py** - Autarke Apify App Entry Point
- **Complete Module System** - Alle Integrationen in Modulen
- **Direct API Access** - Keine Orchestrator Dependencies
- **Full Email Processing** - Von Input bis CRM Integration

## 🎯 New Architecture Plan:
This system will be split into microservices:
1. **Email Processing Service** - Core email handling
2. **OCR Service** - Document scanning and analysis  
3. **WeClapp Sync Service** - CRM integration
4. **Database Operations** - Data persistence
5. **Orchestrator Communication** - Webhook integration

## 📡 Orchestrator Integration:
- Lead-Quellen (Email/SipGate/WhatsApp) → Webhook → Railway LangGraph
- Zentrale Intelligenz für alle Lead-Verarbeitung
- SQL-DB Performance für schnelle Abfragen
- CRM-Sync für zentrale Datenhaltung