import requests
import os
from modules.utils.debug_log import debug_log

DEEP_OCR_API_KEY = os.getenv("DEEP_OCR_API_KEY")

def deep_scan_controller(file_bytes: bytes, lang: str = "deu+eng") -> str:
    """
    Führt Deep OCR für schwer lesbare PDFs durch.
    - Nutzt den Endpoint /v1/pdf/documentparser für komplexe Dokumente.
    """
    if not DEEP_OCR_API_KEY:
        raise ValueError("DEEP_OCR_API_KEY fehlt in der Umgebung!")

    debug_log("📄 Starte Deep OCR für komplexe Dokumente...")

    # URL und Header für die Anfrage
    url = "https://api.deepocr.com/v1/pdf/documentparser"
    headers = {
        "Authorization": f"Bearer {DEEP_OCR_API_KEY}",
        "Content-Type": "application/pdf"
    }

    try:
        # Anfrage an die Deep OCR API
        response = requests.post(url, headers=headers, data=file_bytes, params={"lang": lang})
        if response.status_code == 200:
            debug_log("✅ Deep OCR erfolgreich abgeschlossen.")
            return response.json().get("text", "")
        else:
            debug_log(f"⚠️ Deep OCR fehlgeschlagen ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        debug_log(f"❌ Fehler bei Deep OCR: {str(e)}")
        return None