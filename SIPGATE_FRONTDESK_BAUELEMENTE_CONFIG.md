# 🏗️ SipGate Frontdesk - Bauelemente Torcenter Südwest

## 🎯 **SZENARIO-MAPPING FÜR RAILWAY AI**

### **1. 📋 ANGEBOTSANFRAGE**
```json
{
  "scenario_type": "Angebotsanfrage",
  "priority": "high",
  "crm_category": "sales_lead",
  "required_data": ["anliegen", "name", "phone", "address", "address_details"],
  "next_actions": [
    {
      "type": "task_creation",
      "title": "Angebotserstellung für {customer_name}",
      "assigned_to": "sales_team",
      "due_date": "+2_business_days",
      "priority": "high"
    },
    {
      "type": "crm_contact",
      "action": "create_or_update",
      "category": "qualified_lead"
    },
    {
      "type": "notification_email",
      "template": "angebotsanfrage_summary",
      "recipients": ["sales@bauelemente-tc.de", "mj@cdtechnologies.de"]
    }
  ]
}
```

### **2. 🏠 BERATUNG ODER AUFMASS VOR ORT**
```json
{
  "scenario_type": "Beratung",
  "priority": "medium",
  "crm_category": "service_appointment",
  "required_data": ["anliegen", "name", "phone", "address"],
  "next_actions": [
    {
      "type": "task_creation", 
      "title": "Vor-Ort Termin vereinbaren: {customer_name}",
      "assigned_to": "service_team",
      "due_date": "+1_business_day",
      "priority": "medium"
    },
    {
      "type": "calendar_suggest",
      "service_type": "vor_ort_beratung",
      "duration": "2_hours"
    },
    {
      "type": "notification_email",
      "template": "beratung_vor_ort_summary"
    }
  ]
}
```

### **3. ⚠️ REKLAMATION ODER REPARATURANFRAGE**
```json
{
  "scenario_type": "Reklamation",
  "priority": "urgent",
  "crm_category": "service_case",
  "required_data": ["anliegen", "name", "phone"],
  "next_actions": [
    {
      "type": "task_creation",
      "title": "URGENT: Reklamation bearbeiten - {customer_name}",
      "assigned_to": "service_lead",
      "due_date": "+4_hours",
      "priority": "urgent"
    },
    {
      "type": "crm_case",
      "category": "reklamation",
      "status": "open"
    },
    {
      "type": "notification_email",
      "template": "reklamation_alert",
      "recipients": ["service@bauelemente-tc.de", "management@bauelemente-tc.de"]
    }
  ]
}
```

### **4. 📞 SONSTIGES**
```json
{
  "scenario_type": "Sonstiges",
  "priority": "low",
  "crm_category": "general_inquiry",
  "required_data": ["anliegen", "name", "phone", "callback_time"],
  "next_actions": [
    {
      "type": "task_creation",
      "title": "Rückruf für {customer_name} - {callback_time}",
      "assigned_to": "customer_service",
      "due_date": "custom_callback_time",
      "priority": "low"
    },
    {
      "type": "crm_contact",
      "action": "create_or_update",
      "category": "general_contact"
    },
    {
      "type": "notification_email",
      "template": "general_inquiry_summary"
    }
  ]
}
```

---

## 📧 **EMAIL TEMPLATES**

### **Angebotsanfrage Summary:**
```
Betreff: 🏗️ Neue Angebotsanfrage - {customer_name}

Hallo Team,

📋 ANGEBOTSANFRAGE EINGEGANGEN:

👤 Kunde: {customer_name}  
📞 Telefon: {phone}
📍 Adresse: {address}
🎯 Anliegen: {anliegen}

✅ NÄCHSTE SCHRITTE:
- Angebot erstellen bis: {due_date}
- Zuständig: {assigned_to}
- CRM-Status: Qualified Lead

📋 Aufgabe erstellt: {task_link}
💾 CRM-Eintrag: {crm_link}
```

### **Reklamation Alert:**
```
Betreff: ⚠️ URGENT: Reklamation - {customer_name}

🚨 REKLAMATION EINGEGANGEN:

👤 Kunde: {customer_name}
📞 Telefon: {phone}  
⚠️ Problem: {anliegen}

🔥 SOFORT HANDELN:
- Rückruf bis: {due_date}
- Zuständig: {assigned_to}
- Status: URGENT

📋 Task: {task_link}
```

---

## 🔗 **WEBHOOK FLOW ÜBERSICHT**

```
📞 SipGate Frontdesk Call
    ↓
🤖 KI erfasst Szenario + Daten
    ↓
📡 Webhook → Railway AI
    ↓
🧠 Szenario-Mapping & Priorisierung
    ↓
📋 WeClapp Task + CRM Update
    ↓
📧 Summary Email an Team
    ↓
👥 Sales/Service Team Notification
```

---

## ⚙️ **RAILWAY ENDPOINT CONFIGURATION**

**URL:** `https://my-langgraph-agent-production.up.railway.app/webhook/ai-call`

**Expected Payload Fields:**
- `scenario_type` (required)
- `anliegen` (required) 
- `customer_data.name` (required)
- `customer_data.phone` (required)
- `customer_data.address` (optional, required for Angebot/Beratung)
- `appointment_data.callback_time` (optional, required for Sonstiges)

**Response Format:**
```json
{
  "success": true,
  "workflow_path": "BAUELEMENTE_SZENARIO_{scenario_type}",
  "tasks_generated": [{
    "title": "...",
    "assigned_to": "...",
    "priority": "...",
    "due_date": "..."
  }],
  "crm_updated": true,
  "notifications_sent": ["email", "crm"]
}
```