import requests

def extract_data_with_template(pdf_url, template_id, api_key):
    """
    Extrahiert Daten aus einem PDF mit einem PDF.co-Template.

    Args:
        pdf_url (str): URL des PDF-Dokuments.
        template_id (str): ID des PDF.co-Templates.
        api_key (str): Ihr PDF.co API-Schlüssel.

    Returns:
        dict: Extrahierte Daten oder Fehlernachricht.
    """
    url = "https://api.pdf.co/v1/pdf/documentparser"
    headers = {
        "x-api-key": api_key
    }
    payload = {
        "url": pdf_url,
        "templateId": template_id
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}