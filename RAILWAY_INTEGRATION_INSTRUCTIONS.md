# 🚀 Railway Integration Instructions - C&D Technologies

## 📋 **INTEGRATION STEPS**

### **Step 1: Code Integration**

1. **Add the notification handler to your Railway project:**
```bash
# Copy railway_notification_handler.py to your Railway project
# Location: /app/handlers/notification_handler.py (oder ähnlich)
```

2. **Modify your existing endpoint:**
```python
# In your main orchestrator file (z.B. main.py oder app.py)

from handlers.notification_handler import enhance_orchestrator_response

@app.post("/webhook/ai-call")
async def process_call(request_data: dict):
    # Existing processing
    result = await your_existing_processing_function(request_data)
    
    # NEW: Add final notification
    enhanced_result = enhance_orchestrator_response(result, request_data)
    
    return enhanced_result
```

### **Step 2: Environment Variables**

**Railway Dashboard → Settings → Variables:**
```
ZAPIER_NOTIFICATION_WEBHOOK = https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/
NOTIFICATION_ENABLED = true
```

### **Step 3: Dependencies**

**Ensure requests is in requirements.txt:**
```
requests>=2.28.0
```

### **Step 4: Deploy**

**Option A: GitHub Auto-Deploy**
```bash
git add .
git commit -m "Add Zapier notification integration"
git push origin main
# Railway deploys automatically
```

**Option B: Railway CLI**
```bash
railway deploy
```

---

## 🧪 **TESTING**

### **Test the integration:**

1. **Send test call to your Railway endpoint:**
```bash
curl -X POST "https://my-langgraph-agent-production.up.railway.app/webhook/ai-call" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+49221987654321",
    "scenario_type": "Angebotsanfrage",
    "customer_name": "Test User",
    "anliegen": "Test Integration"
  }'
```

2. **Check Railway logs:**
```bash
railway logs
# Look for: "✅ Notification sent successfully"
```

3. **Check for email:**
   - Email should arrive at mj@cdtechnologies.de
   - Email should arrive at info@cdtechnologies.de

---

## 🔄 **ROLLBACK PLAN**

**If something goes wrong:**

1. **Disable notifications:**
```bash
railway variables:set NOTIFICATION_ENABLED=false
```

2. **Or remove the enhancement:**
```python
# Comment out in your endpoint:
# enhanced_result = enhance_orchestrator_response(result, request_data)
# return result  # Return original result
```

---

## 📊 **MONITORING**

**Check notification status in Railway logs:**
- ✅ `Notification sent successfully` = Working
- ⚠️ `Notification failed` = Check Zapier webhook
- ❌ `Notification error` = Check code/dependencies

**Railway Dashboard → Metrics:**
- Monitor response times
- Check error rates
- Watch memory usage

---

## 🎯 **SUCCESS CRITERIA**

- ✅ Railway processes calls successfully (existing)
- ✅ Railway generates tasks (existing)  
- 🔄 Railway sends Zapier notifications (NEW)
- 📧 Zapier sends emails to team (NEW)
- 🏢 Complete Lead Management Ecosystem (GOAL!)

---

**Nach dieser Integration habt ihr das komplette Orchestrator-Ecosystem aus eurem Master-Prompt! 🚀**