# 📧 Email & SipGate Datenflow Analysis

## 🎯 **1. Email-Konfiguration Update:**

### ✅ **mj@cdtechnologies.de jetzt überwacht!**
```env
EMAIL_RECEIVER=mj@cdtechnologies.de,info@cdtechnologies.de
```

### 🚀 **Deploy notwendig:**
```bash
apify push  # Updated .env deployen
```

## 📊 **2. Wo werden Daten gespeichert:**

### **📧 Email-Daten: SQLite Database**
```
Database: email_data.db
Tabelle: email_data
Felder:
- subject (Betreff)
- sender (Absender)  
- recipient (Empfänger)
- received_date (Datum)
- ocr_text (OCR Text)
- gpt_result (AI Analyse)
- weclapp_contact_id (CRM ID)
- current_stage (Status)
```

### **📞 SipGate-Daten: Gleiche Database + Railway**
```
Flow: SipGate → Zapier → Railway → SQLite
Zusätzliche Felder:
- call_duration (Gesprächsdauer)
- caller_id (Anrufer ID)
- direction (Ein-/Ausgehend)
```

### **💬 WhatsApp-Daten: Gleiche Database**
```
Flow: WhatsApp → Zapier → Railway → SQLite
Zusätzliche Felder:
- message_text (Nachricht)
- message_type (Text/Media)
- phone_number (Telefonnummer)
```

## 🔍 **3. Letzte verarbeitete Email finden:**

### **Database Query (lokale Prüfung):**
```python
# In email_database.py ausführen:
SELECT * FROM email_data ORDER BY id DESC LIMIT 1;
```

### **Railway Logs (Live System):**
```
https://railway.app → my-langgraph-agent → Logs
Letzter /webhook/ai-email Call
```

### **Apify Logs (Actor Runs):**
```
https://apify.com → Actors → cdtech~mail2zapier2apify2gpt2onedrive
Letzte 412+ Runs einsehen
```

## 🎯 **4. SipGate Datenflow Details:**

```
1. 📞 SipGate Call eingehend
2. 🔗 Zapier Webhook triggeriert
3. 📨 POST zu Railway: /webhook/ai-call
4. 🧠 Railway AI Processing:
   - Contact Matching (WeClapp)
   - GPT Analyse der Call-Daten
   - Task Generation
5. 💾 Speicherung in SQLite Database
6. 📋 Lead/Task zu CRM (WeClapp)
7. 🚨 Notifikation via Zapier Webhook
```

## ❓ **Was möchtest du sehen?**

1. **Letzte Email** aus Database anzeigen?
2. **SipGate Test-Call** durchführen?
3. **Database Struktur** inspizieren?
4. **Railway Logs** live prüfen?

**Sag mir, welche Details du brauchst!** 🔍