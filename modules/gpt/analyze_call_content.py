"""
🎯 SipGate Call Analysis - Task & Appointment Extraction
========================================================

Analysiert Call-Transkripte und extrahiert automatisch:
- Tasks (Angebot erstellen, Rückruf, etc.)
- Termine (nächste Woche Montag 14 Uhr)
- Follow-Up-Reminder (in 3 Tagen zurückrufen)
"""

import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser

# Deutsche Zeitzone
BERLIN_TZ = pytz.timezone('Europe/Berlin')

def now_berlin():
    """Return current datetime in Berlin timezone"""
    return datetime.now(BERLIN_TZ)


async def analyze_call_content(
    transcription: str,
    contact_name: str = "Unbekannt",
    duration_seconds: int = 0
) -> Dict:
    """
    Analysiert Gesprächsinhalt und extrahiert Tasks, Termine, Follow-Ups
    
    Args:
        transcription: Transkript des Gesprächs
        contact_name: Name des Kontakts
        duration_seconds: Dauer des Gesprächs
    
    Returns:
        {
            "tasks": [{"title": "...", "description": "...", "priority": "..."}],
            "appointments": [{"date": "...", "time": "...", "description": "..."}],
            "follow_ups": [{"action": "...", "due_date": "...", "reason": "..."}],
            "summary": "..."
        }
    """
    
    if not transcription or len(transcription.strip()) < 10:
        return {
            "tasks": [],
            "appointments": [],
            "follow_ups": [],
            "summary": "Kein Transkript verfügbar"
        }
    
    # OpenAI Model
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Aktuelles Datum für relative Zeitangaben
    heute = now_berlin()
    heute_str = heute.strftime("%d.%m.%Y")
    wochentag = heute.strftime("%A")
    
    # Wochentage-Mapping
    wochentage_map = {
        "Monday": "Montag",
        "Tuesday": "Dienstag",
        "Wednesday": "Mittwoch",
        "Thursday": "Donnerstag",
        "Friday": "Freitag",
        "Saturday": "Samstag",
        "Sunday": "Sonntag"
    }
    wochentag_de = wochentage_map.get(wochentag, wochentag)
    
    prompt = f"""
Analysiere dieses Telefonat und extrahiere ALLE wichtigen Informationen:

KONTAKT: {contact_name}
DAUER: {duration_seconds} Sekunden
DATUM: {heute_str} (Heute ist {wochentag_de})

TRANSKRIPT:
{transcription}

AUFGABE:
Extrahiere aus dem Gespräch:

1. TASKS (Konkrete Aufgaben die erledigt werden müssen):
   - Angebot erstellen
   - Rechnung schicken
   - Unterlagen zusenden
   - Projekt prüfen
   - etc.

2. TERMINE (Vereinbarte Termine):
   - "nächste Woche Montag 14 Uhr"
   - "morgen um 10"
   - "in 3 Tagen"
   - Berechne das EXAKTE Datum basierend auf Heute: {heute_str}

3. FOLLOW-UPS (Rückrufe/Erinnerungen):
   - "in 3 Tagen zurückrufen"
   - "Status prüfen nächste Woche"
   - "Angebot nachfassen"

4. ZUSAMMENFASSUNG (1-2 Sätze)

Antworte NUR als JSON ohne zusätzlichen Text:
{{
  "tasks": [
    {{
      "title": "Kurzer Task-Titel",
      "description": "Detaillierte Beschreibung",
      "priority": "low" | "medium" | "high" | "urgent",
      "due_date": "YYYY-MM-DD" (optional)
    }}
  ],
  "appointments": [
    {{
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "description": "Was ist der Termin",
      "location": "Wo" (optional)
    }}
  ],
  "follow_ups": [
    {{
      "action": "Was machen",
      "due_date": "YYYY-MM-DD",
      "reason": "Warum"
    }}
  ],
  "summary": "Zusammenfassung des Gesprächs"
}}

WICHTIG:
- Wenn keine Tasks/Termine/Follow-Ups: Leere Arrays zurückgeben
- Datum MUSS berechnet werden (nicht "nächste Woche" sondern "2025-10-20")
- Priorität MUSS gesetzt werden
"""

    try:
        # GPT Call
        messages = [HumanMessage(content=prompt)]
        response = await llm.ainvoke(messages)
        
        # Parse JSON
        result_text = response.content.strip()
        
        # Entferne Markdown-Codeblöcke falls vorhanden
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        import json
        result = json.loads(result_text)
        
        # Validierung & Defaults
        if "tasks" not in result:
            result["tasks"] = []
        if "appointments" not in result:
            result["appointments"] = []
        if "follow_ups" not in result:
            result["follow_ups"] = []
        if "summary" not in result:
            result["summary"] = "Telefonat mit " + contact_name
        
        return result
        
    except Exception as e:
        print(f"❌ Error analyzing call content: {e}")
        return {
            "tasks": [],
            "appointments": [],
            "follow_ups": [],
            "summary": f"Fehler bei der Analyse: {str(e)}"
        }


async def extract_appointment_datetime(
    natural_language: str,
    reference_date: Optional[datetime] = None
) -> Optional[Dict[str, str]]:
    """
    Extrahiert Datum/Zeit aus natürlicher Sprache
    
    Beispiele:
    - "nächste Woche Montag 14 Uhr" → 2025-10-20 14:00
    - "morgen um 10" → 2025-10-14 10:00
    - "übermorgen" → 2025-10-15
    - "in 3 Tagen" → 2025-10-16
    
    Args:
        natural_language: Text wie "nächste Woche Montag 14 Uhr"
        reference_date: Referenzdatum (default: heute)
    
    Returns:
        {"date": "2025-10-20", "time": "14:00"} oder None
    """
    
    if not reference_date:
        reference_date = now_berlin()
    
    text = natural_language.lower().strip()
    
    # Einfache Fälle
    if "heute" in text:
        date = reference_date
    elif "morgen" in text and "übermorgen" not in text:
        date = reference_date + timedelta(days=1)
    elif "übermorgen" in text:
        date = reference_date + timedelta(days=2)
    else:
        # Komplexere Fälle → GPT
        try:
            llm = ChatOpenAI(model="gpt-4", temperature=0)
            heute_str = reference_date.strftime("%d.%m.%Y (%A)")
            
            prompt = f"""
Heute ist: {heute_str}

Wandle diese Zeitangabe in ein konkretes Datum um:
"{natural_language}"

Antworte NUR mit JSON:
{{"date": "YYYY-MM-DD", "time": "HH:MM"}}

Falls keine Zeit angegeben: "time": null
"""
            
            messages = [HumanMessage(content=prompt)]
            response = await llm.ainvoke(messages)
            
            import json
            result_text = response.content.strip()
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"❌ Error extracting appointment: {e}")
            return None
    
    # Zeit extrahieren (Regex)
    time_match = re.search(r'(\d{1,2}):(\d{2})', text)
    if time_match:
        time_str = f"{time_match.group(1).zfill(2)}:{time_match.group(2)}"
    else:
        time_match = re.search(r'(\d{1,2})\s*(?:uhr|h)', text)
        if time_match:
            time_str = f"{time_match.group(1).zfill(2)}:00"
        else:
            time_str = None
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "time": time_str
    }


async def calculate_follow_up_date(
    follow_up_text: str,
    reference_date: Optional[datetime] = None
) -> str:
    """
    Berechnet Fälligkeitsdatum für Follow-Up
    
    Beispiele:
    - "in 3 Tagen zurückrufen" → 2025-10-16
    - "nächste Woche Status prüfen" → 2025-10-20
    - "morgen" → 2025-10-14
    
    Args:
        follow_up_text: Text wie "in 3 Tagen"
        reference_date: Referenzdatum (default: heute)
    
    Returns:
        "YYYY-MM-DD"
    """
    
    if not reference_date:
        reference_date = now_berlin()
    
    text = follow_up_text.lower().strip()
    
    # Einfache Pattern
    if "morgen" in text:
        return (reference_date + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # "in X Tagen"
    match = re.search(r'in\s+(\d+)\s+tag', text)
    if match:
        days = int(match.group(1))
        return (reference_date + timedelta(days=days)).strftime("%Y-%m-%d")
    
    # "nächste Woche" (7 Tage)
    if "nächste woche" in text or "nächster woche" in text:
        return (reference_date + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Default: 3 Tage
    return (reference_date + timedelta(days=3)).strftime("%Y-%m-%d")


# Test-Funktion
if __name__ == "__main__":
    async def test():
        # Test mit Beispiel-Transkript
        transcript = """
        Guten Tag Herr Müller, ja ich rufe an wegen dem Projekt Terrassendach.
        Können Sie mir ein Angebot schicken? Und könnten wir nächste Woche Montag
        um 14 Uhr einen Termin für das Aufmaß machen?
        Bitte rufen Sie mich in 3 Tagen zurück wenn Sie das Angebot fertig haben.
        """
        
        result = await analyze_call_content(
            transcription=transcript,
            contact_name="Frank Müller",
            duration_seconds=180
        )
        
        print("📞 CALL ANALYSIS RESULT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Test Appointment Extraction
        apt = await extract_appointment_datetime("nächste Woche Montag 14 Uhr")
        print(f"\n📅 APPOINTMENT: {apt}")
        
        # Test Follow-Up
        follow = await calculate_follow_up_date("in 3 Tagen zurückrufen")
        print(f"\n⏰ FOLLOW-UP: {follow}")
    
    asyncio.run(test())
