import re
import json
from modules.utils.debug_log import debug_log

def classify_document_with_gpt(ocr_text: str, handwriting_text: str = "", metadata: dict = {}) -> dict:
    # Import innerhalb der Funktion, um zirkuläre Abhängigkeiten zu vermeiden
    from modules.gpt.prompts.analyse_scan_prompt import build_analyse_scan_prompt
    from modules.gpt.run_gpt_prompt import run_gpt_prompt

    debug_log("💬 Starte finale GPT-Dokumentenanalyse...")

    # Prompt erstellen
    prompt = build_analyse_scan_prompt(
        ocr_text=ocr_text,
        handwriting_text=handwriting_text,
        metadata=metadata
    )

    try:
        # GPT-Aufruf
        response = run_gpt_prompt(prompt)
        debug_log("✅ Finale GPT-Analyse abgeschlossen.")

        # JSON automatisch extrahieren
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            cleaned_response = match.group(0)
            gpt_result = json.loads(cleaned_response)
            #debug_log(f"✅ GPT-Ergebnis erfolgreich geparst: {json.dumps(gpt_result, indent=2, ensure_ascii=False)}")
            return gpt_result
        else:
            debug_log("⚠️ Kein JSON in der GPT-Antwort gefunden.")
            return {"error": "Kein JSON gefunden", "response": response}

    except json.JSONDecodeError as e:
        debug_log(f"❌ Fehler beim Parsen der GPT-Antwort: {e}")
        return {"error": "JSON-Parsing-Fehler", "response": response}

    except Exception as e:
        debug_log(f"❌ Fehler bei der GPT-Anfrage: {e}")
        return {"error": "GPT-Anfrage fehlgeschlagen", "details": str(e)}