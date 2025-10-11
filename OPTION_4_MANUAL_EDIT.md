# 📝 OPTION 4: MANUAL FILE REPLACEMENT

## LETZTE OPTION - DIREKTE FILE BEARBEITUNG:

### 1. **Railway Dashboard → Deployments**
- Gehe zu aktueller Deployment
- Klicke "View Source" oder "Files"
- Du siehst alle Projekt-Dateien

### 2. **Ersetze diese Dateien:**

#### A. **production_langgraph_orchestrator.py**
- Klicke auf die Datei
- Klicke "Edit" 
- Ersetze Zeilen 277-295 mit:

```python
# AI Analysis Prompt (Fixed JSON escaping)
analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """Du bist ein AI Communication Analyst für ein deutsches Unternehmen.
    
Analysiere die eingehende Kommunikation und erstelle eine JSON-Antwort mit:

{{
    "intent": "support|sales|information|complaint|follow_up",
    "urgency": "low|medium|high|urgent", 
    "sentiment": "positive|neutral|negative",
    "key_topics": ["thema1", "thema2"],
    "suggested_tasks": [
        {{
            "title": "Aufgaben-Titel",
            "type": "follow_up|quote|support|meeting",
            "priority": "low|medium|high|urgent",
            "due_hours": 24
        }}
    ],
    "response_needed": true,
    "summary": "Kurze deutsche Zusammenfassung"
}}

Antworte nur mit dem JSON, keine zusätzlichen Texte."""),
```

#### B. **requirements.txt**
- Ersetze kompletten Inhalt mit:

```text
requests
python-dotenv
apify
urllib3>=2.0.0
aiohttp
asyncio
langchain>=0.1.0
langchain-openai>=0.1.0
langchain-core>=0.1.0
langgraph>=0.1.0
fastapi>=0.100.0
uvicorn>=0.20.0
openai
azure-cognitiveservices-vision-computervision
azure-ai-vision-imageanalysis  
Pillow
pypdf
pandas
openpyxl
SQLAlchemy
beautifulsoup4
lxml
```

### 3. **Save & Redeploy**
- Speichere beide Dateien
- Klicke "Redeploy" Button
- Warte 2-3 Minuten

---

## NACH JEDER OPTION: TEST AUSFÜHREN