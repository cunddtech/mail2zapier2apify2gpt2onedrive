# Datei: modules/gpt/prompts/scan_precheck_prompt.py

def build_scan_precheck_prompt(ocr_text: str) -> str:
    prompt = f"""
    Du bist eine KI, die eingescannte Dokumente eines Handwerks- und Bauelemente-Unternehmens analysiert. 
    Deine Aufgabe ist es, den Dokumenttyp zu erkennen und die wichtigsten Informationen zu erfassen.

    **Wichtige Hinweise:**
- Wenn Maße, Höhenangaben, Breitenangaben oder Torkennzeichnungen vorkommen (z. B. „Höhe: 2500 mm“, „Breite: 3000 mm“), handelt es sich **höchstwahrscheinlich um ein Aufmaßblatt**.
- Handschriftliche Werte sind typisch für Aufmaßblätter, auch wenn der Rest maschinengeschrieben ist. → Aufmaßverdacht setzen!
- Falls unsicher: als "Sonstiges Dokument" klassifizieren und "aufmass_verdacht": true/false entsprechend setzen.

    Mögliche Dokumenttypen:
    - Rechnung (Eingangsrechnung / Ausgangsrechnung)
    - Lieferschein
    - Aufmaßblatt (z.B. Novoferm und Breitenmaß oder Höhenmaß)
    - Leistungsnachweis
    - Tankbeleg
    - Angebot
    - Bestellung
    - Reklamation
    - Versicherungsdokument
    - Behördenschreiben / Amtliche Mitteilungen
    - Vereinsmitgliedschaft / Beitragsrechnung
    - Telefonrechnung
    - Softwarerechnung / Lizenzabrechnung
    - Steuerbescheid / Steuerdokument
    - Leasingvertrag
    - Bankdokument (z. B. Kontoauszug, Kreditvertrag)
    - Lohnabrechnung
    - Wartungsvertrag
    - Sonstiges Dokument

    Erkenne aus dem OCR-Text die wichtigsten Details:
    - Kunde oder Lieferant (wenn vorhanden)
    - Projektnummer oder Projektreferenz (wenn vorhanden)
    - Rechnungsdatum, Aufmaßdatum oder Lieferdatum (je nach Typ)
    - Gesamtsumme (nur bei Rechnungen oder Zahlungen relevant)

    Wenn keine klaren Daten vorhanden sind, schreibe "unbekannt".

    Antworte IMMER im folgenden JSON-Format:

    {{
      "dokumenttyp": "z. B. Rechnung, Lieferschein, Steuerbescheid, Aufmaß etc.",
      "kunde": "falls bekannt",
      "lieferant": "falls bekannt",
      "projektnummer": "falls bekannt",
      "datum": "falls bekannt",
      "summe": "falls relevant",
      "notizen": "kurze Zusammenfassung"
      "aufmass_verdacht": true/false
    }}

    OCR-Text:
    \"\"\"
    {ocr_text[:5000]}
    \"\"\"
    """
    return prompt.strip()