# Datei: modules/gpt/run_gpt_prompt.py

from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
import os
from modules.helpers.debug_log import debug_log

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def run_gpt_prompt(prompt: str) -> str:
    """
    Sendet einen Prompt an OpenAI (ChatGPT) und gibt die Antwort als String zurück.
    """

    debug_log("🚀 Sende Prompt an OpenAI...")

    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=750)

        answer = response.choices[0].message.content
        debug_log("✅ Antwort von OpenAI empfangen.")

        return answer

    except Exception as e:
        debug_log(f"❌ Fehler bei der Anfrage an OpenAI: {str(e)}")
        return '{"error": "Fehler beim Abrufen der Antwort von OpenAI."}'