# 📋 TASK LIFECYCLE MANAGEMENT SYSTEM

## 🎯 **VISION**

Ein **intelligentes Aufgaben-Tracking System** das JEDEN Lead/Input vom Erstkontakt bis zum Abschluss verfolgt und automatisch nächste Schritte vorschlägt.

---

## 🔄 **TASK LIFECYCLE (Typische Workflows)**

### **A. INTERESSENT → KUNDE (Neukunden-Akquise)**

```
1. ERSTKONTAKT (Email/Call/WhatsApp)
   ├─ Task: "Interessent kontaktieren"
   ├─ Zuständig: Vertrieb (mj/kt)
   ├─ Frist: 24h
   └─ Status: OFFEN
         ↓
2. ERSTKONTAKT ERFOLGT
   ├─ Task: "Termin für Aufmaß vereinbaren"
   ├─ Zuständig: Vertrieb (mj/kt)
   ├─ Frist: 48h
   └─ Status: OFFEN
         ↓
3. TERMIN VEREINBART
   ├─ Task: "Aufmaß durchführen"
   ├─ Zuständig: Techniker (lh)
   ├─ Frist: Termindatum
   └─ Status: GEPLANT
         ↓
4. AUFMASS DURCHGEFÜHRT
   ├─ Task: "Angebot erstellen"
   ├─ Zuständig: Vertrieb (mj)
   ├─ Frist: 3 Tage
   └─ Status: OFFEN
         ↓
5. ANGEBOT VERSENDET
   ├─ Task: "Follow-up: Angebot besprechen"
   ├─ Zuständig: Vertrieb (mj)
   ├─ Frist: 7 Tage nach Versand
   └─ Status: WARTEND
         ↓
6. AUFTRAG ERHALTEN
   ├─ Task: "Projekt planen & Material bestellen"
   ├─ Zuständig: Projektleitung (mj/lh)
   ├─ Frist: 2 Tage
   └─ Status: OFFEN
         ↓
7. PROJEKT ABGESCHLOSSEN
   ├─ Task: "Rechnung stellen"
   ├─ Zuständig: Buchhaltung
   ├─ Frist: Sofort
   └─ Status: OFFEN
         ↓
8. RECHNUNG BEZAHLT
   ├─ Status: ABGESCHLOSSEN ✅
   └─ Follow-up: "Kundenzufriedenheit (3 Monate später)"
```

---

## 📊 **TASK STATES (Status-Definitionen)**

| Status | Beschreibung | Aktion erforderlich | Auto-Eskalation |
|--------|--------------|---------------------|------------------|
| **OFFEN** | Task wartet auf Bearbeitung | Ja, sofort | Nach 24h → Reminder |
| **IN_BEARBEITUNG** | Jemand arbeitet dran | Nein | Nach 7 Tagen → Reminder |
| **WARTEND** | Warten auf externe Antwort | Nein | Follow-up nach X Tagen |
| **GEPLANT** | Termin bereits vereinbart | Nein | Reminder 1 Tag vorher |
| **BLOCKIERT** | Kann nicht fortfahren (fehlt Info) | Ja, Blocker lösen | Nach 3 Tagen → Eskalation |
| **ABGESCHLOSSEN** | Task erledigt | Nein | Nächste Task generieren |
| **STORNIERT** | Task nicht mehr relevant | Nein | - |

---

## 👥 **ZUSTÄNDIGKEITEN (Roles)**

| Rolle | Kürzel | Verantwortlich für | Typische Tasks |
|-------|--------|-------------------|----------------|
| **Vertrieb** | mj, kt | Kundenakquise, Angebote | Erstkontakt, Angebot, Follow-up |
| **Techniker** | lh | Aufmaße, Montage | Aufmaß, Installation, Service |
| **Projektleitung** | mj, lh | Projekt-Koordination | Planung, Material, Zeitplan |
| **Buchhaltung** | - | Rechnungen, Zahlungen | Rechnung erstellen, Mahnung |
| **Service** | lh | Wartung, Reparaturen | Service-Termin, Garantie |

---

## 🤖 **INTELLIGENTE FOLLOW-UP LOGIK**

### **Auto-Generated Next Tasks (Beispiele):**

#### **Nach: "Interessent kontaktiert"**
```python
if contact_successful:
    create_task("Termin für Aufmaß vereinbaren", assigned_to="mj", due_in_days=2)
else:
    create_task("Erneuter Kontaktversuch", assigned_to="mj", due_in_days=3)
```

#### **Nach: "Angebot versendet"**
```python
create_task(
    title="Follow-up: Angebot besprochen?",
    assigned_to="mj",
    due_in_days=7,
    priority="medium",
    auto_reminder=True
)
```

#### **Nach: "Aufmaß durchgeführt"**
```python
if measurement_data_complete:
    create_task("Angebot erstellen", assigned_to="mj", due_in_days=3, priority="high")
else:
    create_task("Fehlende Daten nachfordern", assigned_to="lh", due_in_days=1, priority="urgent")
```

---

## 📈 **DASHBOARD ÜBERSICHT (Was du sehen willst)**

### **1. MEINE OFFENEN AUFGABEN (Pro Mitarbeiter)**
```
Martin (mj):
  🔴 URGENT (0-24h):
    ├─ Angebot erstellen - Frank Zimmer (fällig: heute)
    └─ Follow-up - Projekt Müller (überfällig: 2 Tage)
  
  🟡 HIGH (1-3 Tage):
    ├─ Termin vereinbaren - Neukunde Jaszczyk
    └─ Rechnung prüfen - Lieferant XYZ
  
  🟢 MEDIUM (3-7 Tage):
    ├─ Material bestellen - Projekt Schmidt
    └─ Kundenzufriedenheit - Projekt Weber
```

### **2. PIPELINE ÜBERSICHT (Alle Leads)**
```
NEUKUNDEN-PIPELINE:
  Erstkontakt (5):
    ├─ Jaszczyk (Email, vor 2h)
    ├─ Müller GmbH (Call, vor 1 Tag)
    └─ ...
  
  Termin vereinbart (3):
    ├─ Frank Zimmer (Aufmaß, morgen 10:00)
    └─ ...
  
  Angebot versendet (7):
    ├─ Schmidt (vor 5 Tagen, Follow-up fällig!)
    └─ ...
  
  Auftrag erhalten (2):
    ├─ Weber (Installation nächste Woche)
    └─ ...
```

### **3. ÜBERFÄLLIGE TASKS (Eskalationen)**
```
⚠️ ÜBERFÄLLIG:
  ├─ Follow-up Projekt Müller (2 Tage überfällig) → mj
  ├─ Rechnung stellen - Projekt Weber (5 Tage überfällig) → Buchhaltung
  └─ Material bestellen - Projekt Schmidt (1 Tag überfällig) → lh
```

---

## 🔧 **TECHNISCHE IMPLEMENTATION**

### **Database Schema (SQLite - email_data.db erweitern):**

```sql
-- TASKS Tabelle
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'OFFEN',  -- OFFEN, IN_BEARBEITUNG, WARTEND, GEPLANT, etc.
    priority TEXT DEFAULT 'medium',  -- urgent, high, medium, low
    assigned_to TEXT,  -- mj, kt, lh
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME,
    completed_at DATETIME,
    parent_task_id INTEGER,  -- Für Follow-up Chain
    related_party_id INTEGER,  -- WeClapp Contact ID
    related_email_id INTEGER,  -- Email/Call/WhatsApp ID
    source_channel TEXT,  -- email, call, whatsapp
    auto_generated BOOLEAN DEFAULT 0,
    reminder_sent BOOLEAN DEFAULT 0,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
);

-- TASK LIFECYCLE (Workflow Tracking)
CREATE TABLE task_lifecycle (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    status TEXT,
    changed_by TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- FOLLOW-UP RULES (Automatische Next-Step Logik)
CREATE TABLE followup_rules (
    id INTEGER PRIMARY KEY,
    trigger_status TEXT,  -- z.B. "Angebot versendet"
    next_task_template TEXT,  -- z.B. "Follow-up: Angebot besprechen"
    delay_days INTEGER,  -- Wann nächste Task fällig
    assigned_to_role TEXT,  -- vertrieb, techniker, etc.
    priority TEXT
);
```

---

## 🚀 **RAILWAY ORCHESTRATOR - TASK GENERATION**

### **Erweitere `production_langgraph_orchestrator.py`:**

```python
# NEU: Task Management Modul
from datetime import datetime, timedelta

class TaskManager:
    """Intelligente Task-Generierung & Follow-up"""
    
    def create_task(self, title, description, assigned_to, 
                    due_in_days=3, priority="medium", 
                    related_party_id=None, source_channel="email"):
        """Task erstellen mit automatischem Follow-up"""
        
        due_date = datetime.now() + timedelta(days=due_in_days)
        
        task_data = {
            "title": title,
            "description": description,
            "assigned_to": assigned_to,
            "due_date": due_date.isoformat(),
            "priority": priority,
            "status": "OFFEN",
            "related_party_id": related_party_id,
            "source_channel": source_channel,
            "auto_generated": True
        }
        
        # In SQLite speichern
        task_id = self.save_to_db(task_data)
        
        # In WeClapp synchronisieren
        self.sync_to_weclapp(task_id, task_data)
        
        return task_id
    
    def get_next_tasks(self, current_task_status, party_id):
        """Automatische Follow-up Tasks basierend auf Status"""
        
        followup_rules = {
            "Interessent kontaktiert": {
                "next": "Termin für Aufmaß vereinbaren",
                "days": 2,
                "assigned": "mj"
            },
            "Angebot versendet": {
                "next": "Follow-up: Angebot besprechen",
                "days": 7,
                "assigned": "mj"
            },
            "Aufmaß durchgeführt": {
                "next": "Angebot erstellen",
                "days": 3,
                "assigned": "mj"
            }
        }
        
        if current_task_status in followup_rules:
            rule = followup_rules[current_task_status]
            return self.create_task(
                title=rule["next"],
                description=f"Automatisch generiert nach: {current_task_status}",
                assigned_to=rule["assigned"],
                due_in_days=rule["days"],
                related_party_id=party_id
            )
```

---

## 📱 **DASHBOARD INTEGRATION (Optionen)**

### **Option 1: WeClapp Native (Empfohlen für Start)**
- ✅ Tasks direkt in WeClapp verwalten
- ✅ Keine separate App nötig
- ✅ WeClapp Mobile App für unterwegs
- ❌ Begrenzte Custom-Logik

### **Option 2: Zapier Tables (Quick & Dirty)**
- ✅ Schnell aufgesetzt
- ✅ Integration mit allen Zaps
- ❌ Begrenzte Visualisierung

### **Option 3: Airtable (Flexibel & Schön)**
- ✅ Perfekte Visualisierung (Kanban, Kalender, etc.)
- ✅ Automations möglich
- ✅ Mobile App sehr gut
- ❌ Extra Kosten

### **Option 4: Custom Dashboard (Railway + Streamlit)**
- ✅ Vollständige Kontrolle
- ✅ Echtzeit-Updates
- ✅ Custom Analytics
- ❌ Mehr Entwicklungsaufwand

---

## 🎯 **EMPFOHLENE IMPLEMENTATION (Phase 1)**

### **JETZT (Diese Woche):**
1. ✅ Railway: Task-Generierung in Code implementieren
2. ✅ SQLite: tasks & task_lifecycle Tabellen erstellen
3. ✅ WeClapp: Tasks automatisch synchronisieren
4. ✅ Email Notification: Bei neuen Tasks an Zuständigen

### **PHASE 2 (Nächste Woche):**
1. Dashboard: Airtable oder WeClapp Views
2. Follow-up Automation: Auto-Reminders
3. Eskalation: Überfällige Tasks → Management Notification

### **PHASE 3 (In 2 Wochen):**
1. Analytics: Pipeline-Metriken
2. AI Predictions: "Wahrscheinlichkeit Auftrag" Score
3. Capacity Planning: Team-Auslastung überwachen

---

## 📋 **BEISPIEL: VOLLSTÄNDIGER WORKFLOW**

### **Input: Email von Neukunde**
```
Von: neukunde@firma.de
Betreff: Anfrage Terrassendach
Body: "Hallo, ich interessiere mich für ein Terrassendach..."
```

### **Railway Processing:**
```python
1. AI Analysis: Intent = "quote_request", Urgency = "medium"
2. Contact Match: NOT FOUND → WEG_A (Unknown)
3. Task Generation:
   ├─ Task 1: "Neukunde kontaktieren - neukunde@firma.de"
   │   ├─ Assigned: mj
   │   ├─ Due: Heute + 24h
   │   ├─ Priority: HIGH
   │   └─ Status: OFFEN
   │
   └─ Follow-up Rule: 
       "Wenn Task 1 = ABGESCHLOSSEN"
       → Task 2: "Termin für Aufmaß vereinbaren"
4. WeClapp Sync: Task in WeClapp erstellen
5. Notification: Email an mj@ mit Task-Details
```

### **Mitarbeiter (mj) Actions:**
```
1. Email-Notification empfangen: "Neue Aufgabe: Neukunde kontaktieren"
2. WeClapp öffnen: Task sehen mit allen Infos
3. Kunde anrufen: Termin vereinbart für nächste Woche
4. Task Status: OFFEN → ABGESCHLOSSEN
5. Railway: Automatisch nächste Task generieren:
   → "Aufmaß durchführen - neukunde@firma.de (Termin: nächste Woche Di 10:00)"
   → Assigned: lh (Techniker)
```

---

## 🎯 **WAS SOLL ICH JETZT BAUEN?**

Sag mir welche **Phase/Option** du zuerst willst:

1. **Quick Start:** WeClapp-basiertes Task Management (2-3 Stunden)
2. **Flexible:** Airtable Dashboard mit Automations (1 Tag)
3. **Custom:** Eigenes Dashboard (Railway + Streamlit) (2-3 Tage)

**Oder soll ich erstmal Phase 1 implementieren (Railway Code + SQLite + WeClapp Sync)?** 🚀
