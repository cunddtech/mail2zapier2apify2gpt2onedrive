import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ Kein API-Key gefunden. Bitte .env prüfen!")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)
try:
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",  # exakter Modellname laut Nutzer
        max_tokens=50,
        messages=[{"role": "user", "content": "Test: Funktioniert die API-Verbindung?"}]
    )
    print("✅ API-Verbindung erfolgreich! Antwort von Claude Sonnet:")
    print(response.content)
except Exception as e:
    print(f"❌ API-Verbindung fehlgeschlagen: {e}")
