import json
from modules.utils.debug_log import debug_log  # Sicherstellen, dass debug_log korrekt importiert wird

def build_analyse_mail_prompt(body_text: str, metadata: dict, ocr_text: str, handwriting_text: str = "", attachments: list = []) -> str:
    """
    Generiert einen flachen GPT-Prompt zur Extraktion strukturierter Metadaten aus einer E-Mail + Anhängen.
    """

    sales_phases = """
    - Verloren (0%)
    - Anfrage (4%)
    - Nicht erreicht (5%)
    - Später anrufen / Telefontermin vereinbart (6%)
    - Richtpreis senden (7%)
    - Aufmaßtermin vor Ort nach Richtpreis (8%)
    - Vor Ort Termin bestätigt (9%)
    - Aufmaß (10%)
    - Anfrage extern (20%)
    - Erstes Angebot erstellt (25%)
    - Wiedervorlage (30%)
    - Auftragsbestätigung Kunde an uns (35%)
    - Bestellung an Lieferanten (40%)
    - Warten auf Material (50%)
    - Terminierung Montage (60%)
    - Probleme / Fehler beheben (70%)
    - Rechnung (75%)
    - Zahlungseingang (80%)
    - Kundenfragebogen (90%)
    - Abgeschlossen (100%)
    """

    attachments_section = "\n".join([
        f"- Dateiname: {att.get('filename', 'Unbekannt')}, Typ: {att.get('type', 'Unbekannt')}, URL: {att.get('url', 'Keine URL')}"
        for att in attachments
    ])

    prompt = f"""
Du bist ein intelligenter Dokumentenanalyst für einen Handwerksbetrieb.

Analysiere den Inhalt und gib ein JSON zurück mit allen Feldern.
Fehlende Informationen bitte sinnvoll schätzen oder mit Standardwerten belegen:
- Texte: "Unbekannt"
- Zahlen: "0,00 €"
- Datum: aktuelles Datum
- Boolean: true/false

Wenn C&D Tech GmbH, Torcenter Südwest oder Bauelemente Herbst als Empfänger erscheinen, ist "richtung": "Eingang".
Wenn sie als Absender erscheinen, ist "richtung": "Ausgang".
Die zugehörige "rolle" ist dann entsprechend "Kunde" oder "Lieferant".

Verwende bei bekannten Begriffen folgende Zuordnung für Ordnerstruktur:
- Projekt: Scan/Projekte/{{kunde}}/{{projekt}}/{{typ}}
- Buchhaltung (Eingang): Scan/Buchhaltung/{{jahr}}/{{monat}}/Eingang/{{lieferant}}
- Buchhaltung (Ausgang): Scan/Buchhaltung/{{jahr}}/{{monat}}/Ausgang/{{kunde}}
- Zu prüfen: Scan/Zu prüfen/{{jahr}}/{{monat}}/Unbekannt

Rückgabeformat:
{{
  "dokumenttyp": "",
  "richtung": "",
  "rolle": "",
  "kunde": "",
  "lieferant": "",
  "projektnummer": "",
  "auftragsnummer": "",
  "kundennummer": "",
  "telefonnr": "",
  "handynnr": "",
  "emailadresse": "",
  "adresse": "",
  "abweichende_adresse": "",
  "privat_geschaeftlich": "",
  "anliegen": "",
  "status": "",
  "datum_eingang": "",
  "datum_dokument": "",
  "dringend": false,
  "summe": "",
  "notizen": "",
  "mail_pdf_url": "",
  "dateiname": "",
  "ordnerstruktur": "",
  "zu_pruefen": false,
  "anhaenge": [
    {{ "dateiname": "...", "typ": "PDF/Bild/..." }}
  ],
  "verkaufsphase": "..."
}}

### Inhalt der E-Mail:
{body_text}

### OCR-Texterkennung:
{ocr_text}

### Handschrift:
{handwriting_text}

### Anhänge:
{attachments_section}

### Metadaten:
{json.dumps(metadata, indent=2, ensure_ascii=False)}

### Verkaufsphasen:
{sales_phases}
"""
    return prompt.strip()