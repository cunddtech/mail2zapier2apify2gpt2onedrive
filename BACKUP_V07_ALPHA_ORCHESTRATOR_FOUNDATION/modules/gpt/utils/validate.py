import json

# modules/gpt/validate.py

def validate_payload(payload: dict) -> dict:
    """
    Sicherstellung, dass alle erwarteten Felder im Payload enthalten sind.
    Fehlende Felder werden mit sinnvollen Defaults ergänzt.
    """
    defaults = {
        "body_text": "",
        "ocr_text": "",
        "handwriting_text": "",
        "metadata": {},
        "attachments": [],
        "source": "mail",
        "date": "",
        "email_from": "",
        "subject": "",
        "attachments_count": 0
    }

    for key, value in defaults.items():
        if key not in payload or payload[key] is None:
            payload[key] = value

    # Nachträgliche Korrektur
    if isinstance(payload.get("attachments"), str):
        try:
            payload["attachments"] = json.loads(payload["attachments"])
        except Exception:
            payload["attachments"] = []

    if isinstance(payload.get("metadata"), str):
        try:
            payload["metadata"] = json.loads(payload["metadata"])
        except Exception:
            payload["metadata"] = {}

    return payload

# modules/gpt/validate.py

def validate_gpt_response(response: dict) -> dict:
    """
    Überprüft, ob alle erwarteten Felder in der GPT-Antwort vorhanden sind.
    Fehlende Felder werden ergänzt oder sinnvoll geschätzt.
    """
    expected_keys = [
        "dokumenttyp", "richtung", "rolle",
        "kunde", "lieferant", "projektnummer", "auftragsnummer", "kundennummer",
        "telefonnr", "handynnr", "emailadresse", "adresse", "abweichende_adresse",
        "privat_geschaeftlich", "anliegen", "status", "datum", "datum_dokument", "datum_eingang",
        "dringend", "summe", "notizen", "dateiname", "ordnerstruktur",
        "zu_pruefen", "verkaufsphase", "anhaenge"
    ]

    validated = {}

    for key in expected_keys:
        value = response.get(key)

        if value is None:
            # Standardwerte setzen
            if key == "dringend":
                value = False
            elif key == "zu_pruefen":
                value = True
            elif key == "summe":
                value = "0,00 €"
            elif key == "anhaenge":
                value = []
            else:
                value = "Unbekannt"

        validated[key] = value

    return validated