import requests
import base64
import os
from modules.utils.debug_log import debug_log

PDFCO_API_KEY = os.getenv("PDFCO_API_KEY")

def upload_to_pdfco(file_bytes: bytes, filename: str) -> str:
    """
    Lädt eine Datei zu PDF.co hoch und gibt die öffentliche URL zurück.
    """

    debug_log(f"🚀 Starte Upload zu PDF.co: {filename}")

    headers = {
        "x-api-key": PDFCO_API_KEY
    }
    files = {
        "file": (filename, file_bytes, "application/pdf")
    }

    response = requests.post("https://api.pdf.co/v1/file/upload", headers=headers, files=files)
    response.raise_for_status()

    uploaded_url = response.json().get("url")
    debug_log(f"✅ Upload abgeschlossen: {uploaded_url}")

    return uploaded_url

def extract_text_pdfco(uploaded_url: str) -> str:
    """
    Führt eine Standard-OCR Texterkennung mit PDF.co auf einer hochgeladenen Datei aus.
    """

    debug_log("🧠 Starte OCR Texterkennung...")

    headers = {
        "x-api-key": PDFCO_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "url": uploaded_url,
        "inline": True,
        "async": False,
        "lang": "deu+eng"
    }

    response = requests.post("https://api.pdf.co/v1/pdf/convert/to/text", headers=headers, json=payload)
    response.raise_for_status()

    extracted_text = response.text
    debug_log("✅ OCR abgeschlossen (Text gekürzt):")
    debug_log(extracted_text[:250])

    return extracted_text