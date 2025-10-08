# Datei: modules/gpt/run_gpt_prompt.py

import os
import openai
from modules.utils.debug_log import debug_log

# OpenAI Client initialisieren
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key)

def run_gpt_prompt(prompt: str) -> str:
    debug_log("💬 Starte Anfrage an OpenAI GPT (neues API-Format)...")

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein intelligenter Dokumentenanalyse-Assistent für einen Handwerksbetrieb."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )
        result_text = response.choices[0].message.content.strip()

        if not result_text:
            debug_log("⚠️ OpenAI hat eine leere Antwort geliefert. Setze Fallback-Text.")
            return "Fehler: Keine Antwort von GPT erhalten."
        
        debug_log("✅ OpenAI Antwort erfolgreich empfangen.")
        return result_text

    except Exception as e:
        debug_log(f"❌ Fehler bei Anfrage an OpenAI: {e}")
        return f"Fehler: OpenAI-Anfrage fehlgeschlagen ({str(e)})"