import os
import time
import requests
from modules.utils.debug_log import debug_log

AZURE_VISION_KEY = os.getenv("AZURE_VISION_KEY")
AZURE_VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT")

MAX_START_ATTEMPTS = 3
WAIT_BETWEEN_ATTEMPTS = 5  # Sekunden
MAX_POLL_ATTEMPTS = 10
WAIT_BETWEEN_POLLS = 2  # Sekunden

def ocr_pdfco_handwriting(pdf_url: str, context: dict = None, max_start_attempts=MAX_START_ATTEMPTS, max_poll_attempts=MAX_POLL_ATTEMPTS) -> dict:
    """
    Führt eine Handschrifterkennung über Azure OCR aus, mit Retry bei Startproblemen.
    """
    if not AZURE_VISION_KEY or not AZURE_VISION_ENDPOINT:
        debug_log("❌ Azure Credentials fehlen!")
        raise ValueError("Azure Vision Key oder Endpoint fehlt!")

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_VISION_KEY,
        "Content-Type": "application/json"
    }
    body = {"url": pdf_url}

    # Start der Handschriftenerkennung
    for attempt_start in range(max_start_attempts):
        debug_log(f"🖋️ Starte Azure Handschriftenerkennung (Versuch {attempt_start+1}/{max_start_attempts})...")
        response = requests.post(f"{AZURE_VISION_ENDPOINT}/vision/v3.2/read/analyze", json=body, headers=headers)

        if response.status_code == 202:
            operation_url = response.headers.get("Operation-Location")
            if not operation_url:
                debug_log("❌ Keine Operation-Location von Azure erhalten.")
                return _error_response("Keine Operation-Location von Azure erhalten.", "handwriting_failed")

            # Polling-Schleife
            for poll_attempt in range(max_poll_attempts):
                time.sleep(WAIT_BETWEEN_POLLS)
                poll_response = requests.get(operation_url, headers=headers)
                result = poll_response.json()
                debug_log(f"🔄 Azure OCR Status {poll_attempt+1}/{max_poll_attempts}: {result.get('status')}")

                if result.get("status") == "succeeded":
                    lines = [line["text"] for r in result["analyzeResult"]["readResults"] for line in r.get("lines", [])]
                    debug_log(f"✅ Azure OCR Erfolg, erste Zeilen: {lines[:3]}")
                    return {
                        "ocr_text": "\n".join(lines),
                        "route": "handwriting"
                    }
                elif result.get("status") == "failed":
                    return _error_response("Azure OCR fehlgeschlagen.", "handwriting_failed")

            return _error_response("Azure OCR Timeout nach Polling.", "handwriting_timeout")

        else:
            error_message = response.text
            debug_log(f"⚠️ Fehler bei Azure OCR Start: {error_message}")

            if any(x in error_message for x in ["InvalidImage", "ServerBusy", "503", "timeout"]):
                if attempt_start < max_start_attempts - 1:
                    debug_log(f"⏳ Warten {WAIT_BETWEEN_ATTEMPTS}s und neuer Versuch...")
                    time.sleep(WAIT_BETWEEN_ATTEMPTS)
                else:
                    return _error_response("Azure OCR konnte nach mehreren Versuchen nicht gestartet werden.", "handwriting_failed")
            else:
                return _error_response(f"Azure OCR Start fehlgeschlagen: {error_message}", "handwriting_failed")

    return _error_response("Unerwarteter Fehler: Alle Azure OCR Startversuche fehlgeschlagen.", "handwriting_failed")


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