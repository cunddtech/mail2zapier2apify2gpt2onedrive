def build_analyse_scan_prompt(ocr_text: str, handwriting_text: str, metadata: dict) -> str:
    import json

    debug_input = json.dumps({
        "OCR_Text_vorhanden": bool(ocr_text.strip()),
        "Handschrift_Text_vorhanden": bool(handwriting_text.strip()),
        "Metadaten_vorhanden": bool(metadata),
    }, indent=2, ensure_ascii=False)

    aufmass_hint = ""
    if metadata.get("aufmass_verdacht"):
        aufmass_hint = "\n⚡️ Achtung: Typische Aufmaß-Muster (z. B. Maße Höhe/Breite) erkannt. Bitte Aufmaß als bevorzugten Dokumenttyp prüfen!"

    prompt = f"""
Du bist ein intelligenter Dokumentenanalyst für einen Handwerksbetrieb.

Am Anfang deiner Ausgabe steht eine Zusammenfassung der Eingabedaten:
{debug_input}

{aufmass_hint}

Analysiere OCR- und Handschrift-Texte aus Scans und klassifiziere:
- Eingangsrechnungen, Ausgangsrechnungen
- Aufmaßblätter, Baustellenbilder
- Lieferscheine, Leistungsnachweise
- Angebote, Bestellungen
- Quittungen, Tankbelege, sonstige Belege
- amtliche Schreiben, Steuerbescheide, Strafzettel

Ordne zu einer dieser Kategorien:
- Anfrage, Auftrag, Rechnung, Lieferschein, Leistungsnachweis, Reklamation, Behördlich, Sonstiges

**Fallback-Logik:**
Wenn keine klare Zuordnung möglich ist, setze "dokumenttyp": "Sonstiges" und erkläre warum.

Beachte:
- C&D Tech GmbH als Empfänger → Richtung: Eingang, Rolle: Kunde
- C&D Tech GmbH als Absender → Richtung: Ausgang, Rolle: Lieferant
- Domains cdtechnologies.de, torcentersuedwest.de und Name Markus Jaszczyk berücksichtigen.

Strukturiere die Ausgabe als JSON:

{{
"dokumenttyp": "...",
"richtung": "...",
"rolle": "...",
"kunde": "...",
"lieferant": "...",
"projektnummer": "...",
"datum": "...",
"datum_dokument": "...",
"summe": "...",
"notizen": "...",
"mail_pdf_url": "",
"dateiname": "...",
"ordnerstruktur": "...",
"zu_pruefen": true/false
}}

### Eingabedaten:

#### 📄 OCR-Texterkennung:
<<<OCR_TEXT>>>
{ocr_text}
<<<END>>>

#### ✍️ Handschrift (z.B. Aufmaßblatt):
<<<HANDSCHRIFT>>>
{handwriting_text}
<<<END>>>

#### 🔎 Kontext (Metadaten):
{json.dumps(metadata, indent=2, ensure_ascii=False)}
"""
    return prompt.strip()

# ➡️ WICHTIG: KEIN SONSTIGER CODE WURDE VERÄNDERT!