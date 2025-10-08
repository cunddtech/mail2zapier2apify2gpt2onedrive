# Datei: modules/gpt/precheck_email.py

import json
import os
from modules.gpt.run_gpt_prompt import run_gpt_prompt
from modules.utils.debug_log import debug_log

def precheck_email(email_from: str, subject: str, body_text: str) -> dict:
    """
    Führt einen Precheck mit GPT durch, um die Relevanz und den Dokumenttyp der E-Mail zu bestimmen.
    """

    debug_log("💬 Starte Precheck-Analyse für E-Mail...")

    prompt = f"""
Du bist eine KI, die den Inhalt einer E-Mail bewertet. 
Analysiere bitte die folgenden Daten:
- Absender: {email_from}
- Betreff: {subject}
- Text:
\"\"\"
{body_text}
\"\"\"

Antwortformat JSON:
{{
    "relevant": (true oder false),
    "dokumenttyp": ("Aufmaß", "Lieferschein", "Rechnung", "Tankbeleg", "Leistungsnachweis", "Sonstiges"),
    "aufmass_verdacht": (true oder false),
    "grund": (kurze Begründung warum)
}}
"""

    try:
        response = run_gpt_prompt(prompt)
        debug_log("✅ Precheck-Analyse abgeschlossen.")

        result = json.loads(response)
        debug_log(f"✅ Precheck-Antwort (gekürzt): {json.dumps(result, indent=2, ensure_ascii=False)[:250]}")
    except Exception as e:
        debug_log(f"❌ Fehler beim Precheck-Parsing: {e}")
        result = {
            "relevant": False,
            "dokumenttyp": "Sonstiges",
            "aufmass_verdacht": False,
            "grund": "Parsing-Fehler beim Precheck."
        }

    return result