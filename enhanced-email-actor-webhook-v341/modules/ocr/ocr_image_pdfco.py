import os
import time
import requests
from modules.utils.debug_log import debug_log

AZURE_VISION_KEY = os.getenv("AZURE_VISION_KEY")
AZURE_VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT")

MAX_POLL_ATTEMPTS = 10
WAIT_BETWEEN_POLLS = 2  # Sekunden

def ocr_image_pdfco(image_url: str, max_poll_attempts=MAX_POLL_ATTEMPTS, wait_between_polls=WAIT_BETWEEN_POLLS) -> dict:
    """
    Führt eine Bildanalyse (OCR) mit Azure OCR durch.
    """
    if not AZURE_VISION_KEY or not AZURE_VISION_ENDPOINT:
        debug_log("❌ Azure Credentials fehlen!")
        raise ValueError("Azure Vision Key oder Endpoint fehlt!")

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_VISION_KEY,
        "Content-Type": "application/json"
    }
    body = {"url": image_url}

    try:
        debug_log(f"🖼️ Starte Bildanalyse für URL: {image_url}")
        response = requests.post(f"{AZURE_VISION_ENDPOINT}/vision/v3.2/read/analyze", json=body, headers=headers)

        if response.status_code == 202:
            operation_url = response.headers.get("Operation-Location")
            if not operation_url:
                return _error_response("Keine Operation-Location von Azure erhalten.", "image_ocr_failed")

            # Polling-Schleife
            for poll_attempt in range(max_poll_attempts):
                time.sleep(wait_between_polls)
                poll_response = requests.get(operation_url, headers=headers)
                result = poll_response.json()
                debug_log(f"🔄 Azure OCR Status {poll_attempt+1}/{max_poll_attempts}: {result.get('status')}")

                if result.get("status") == "succeeded":
                    lines = [line["text"] for r in result["analyzeResult"]["readResults"] for line in r.get("lines", [])]
                    debug_log(f"✅ Bildanalyse erfolgreich, erste Zeilen: {lines[:3]}")
                    return {
                        "ocr_text": "\n".join(lines),
                        "route": "image_ocr"
                    }

                elif result.get("status") == "failed":
                    return _error_response("Bildanalyse fehlgeschlagen.", "image_ocr_failed")

            return _error_response("Bildanalyse Timeout nach Polling.", "image_ocr_timeout")

        else:
            return _error_response(f"Fehler bei der Bildanalyse: {response.status_code} - {response.text}", "image_ocr_failed")

    except Exception as e:
        return _error_response(f"Fehler bei der Bildanalyse: {str(e)}", "image_ocr_error")


def _error_response(error_message: str, route: str) -> dict:
    """
    Hilfsfunktion zur Erstellung von Fehlerantworten.
    """
    debug_log(f"❌ {error_message}")
    return {
        "ocr_text": None,
        "route": route,
        "error": error_message
    }