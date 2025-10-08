import requests
import os

PDFCO_API_KEY = os.getenv("PDFCO_API_KEY")

def extract_text_from_pdf(pdf_url):
    if not PDFCO_API_KEY:
        raise ValueError("PDFCO_API_KEY fehlt in der Umgebung!")

    url = "https://api.pdf.co/v1/pdf/convert/to/text"

    payload = {
        "url": pdf_url,
        "inline": True,
        "async": False,
        "lang": "deu+eng"
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": PDFCO_API_KEY
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json().get("body")
    else:
        raise Exception(f"OCR fehlgeschlagen: {response.text}")