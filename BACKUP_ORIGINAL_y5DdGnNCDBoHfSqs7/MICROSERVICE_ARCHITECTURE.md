# 🏗️ MICROSERVICE ARCHITECTURE PLAN
**Datum:** 8. Oktober 2025  
**Original System:** y5DdGnNCDBoHfSqs7  

## 🎯 Neue Architektur - Orchestrator-basiert:

### 📡 **Orchestrator (Railway LangGraph):**
- **URL:** https://my-langgraph-agent-production.up.railway.app
- **Funktion:** Zentrale Intelligenz für alle Lead-Quellen
- **Endpoints:** 
  - `/webhook/email` - Email Processing
  - `/webhook/sipgate` - SipGate Calls  
  - `/webhook/whatsapp` - WhatsApp Messages

### 📱 **Microservices (Apify Apps):**

#### 1. **Email Processing Service** 
- **Source:** Modules aus y5DdGnNCDBoHfSqs7
- **Funktion:** Email + Attachment Processing
- **Kommunikation:** Webhook → Orchestrator
- **Module:** mail/, msgraph/, auth/

#### 2. **OCR Service**
- **Source:** modules/ocr/ + modules/gpt/
- **Funktion:** Document Scanning + AI Analysis
- **Kommunikation:** API Calls von Orchestrator
- **Module:** ocr/, gpt/analyze_document

#### 3. **WeClapp Sync Service** 
- **Source:** modules/weclapp/ + modules/database/
- **Funktion:** CRM Integration + SQL Sync
- **Kommunikation:** API Calls von Orchestrator
- **Module:** weclapp/, database/

#### 4. **File Management Service**
- **Source:** modules/filegen/ + modules/upload/
- **Funktion:** OneDrive File Operations
- **Kommunikation:** API Calls von Orchestrator
- **Module:** filegen/, upload/, msgraph/onedrive_manager

## 🔄 **Workflow Beispiel:**

### **Anruf-Szenario (SipGate):**
1. **SipGate App** → Webhook → **Orchestrator**
2. **Orchestrator** → SQL-DB Check (Performance!)  
3. **Orchestrator** → WeClapp API (falls mehr Daten nötig)
4. **Orchestrator** → Aktion: CRM Update, Task Creation
5. **Orchestrator** → Response an SipGate

### **WhatsApp Mitarbeiter-Anfrage:**
1. **WhatsApp App** → Webhook → **Orchestrator**
2. **Orchestrator** → SQL-DB Suche ("AB für Kunde X")
3. **Orchestrator** → Response: AB-Nummer gefunden
4. **Orchestrator** → CRM Log: Anfrage dokumentiert

## ⚡ **Performance-Vorteile:**
- **SQL-DB Queries** statt CRM-API (10x schneller)
- **Microservice Skalierung** je nach Bedarf
- **Zentrale Intelligenz** im Orchestrator
- **Parallel Processing** möglich

## 📊 **Datenfluss:**
```
Lead-Quellen → Orchestrator → SQL-DB (fast read)
                ↓
            WeClapp API (write/complex)
                ↓
            Aktionen (Tasks, Termine, etc.)
```

## 🔧 **Implementation Steps:**
1. ✅ Original System Backup
2. 🔄 Webhook-Integration in Email App
3. 🏗️ Microservice Aufspaltung  
4. 📡 Orchestrator Endpoints
5. 🚀 Deployment & Testing