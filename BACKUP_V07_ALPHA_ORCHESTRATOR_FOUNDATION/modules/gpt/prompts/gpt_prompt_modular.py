import json
from modules.utils.debug_log import debug_log

def build_precheck_prompt(body_text: str, metadata: dict, attachments: list, analysis_results: dict = {}) -> str:
    analysis_results_section = (
        f"#### 🔎 Analyseergebnisse:\n{json.dumps(analysis_results, indent=2, ensure_ascii=False)}\n"
        if analysis_results else ""
    )
    return f"""
Du bist ein E-Mail-Filter für einen Handwerksbetrieb.

Analysiere die folgende E-Mail und bestimme:
- Dokumenttyp: Anfrage, Rechnung, Lieferschein, Reklamation, ...
- Richtung: Eingang oder Ausgang
- Rolle: Kunde oder Lieferant

Wenn C&D Tech GmbH, Torcenter Südwest oder Bauelemente Herbst der Empfänger ist → Richtung = Eingang, Rolle = Kunde.
Wenn diese Firmen Absender sind → Richtung = Ausgang, Rolle = Lieferant.

Antwortformat (im JSON-Format zurückgeben!):
{{
  "relevant": true/false,
  "grund": "kurze Begründung",
  "typ": "relevant/werbung/systemmail/newsletter/spam/...",
  "dokumenttyp": "...",
  "richtung": "Eingang/Ausgang",
  "rolle": "Kunde/Lieferant"
}}

E-Mail:
<<<BODY>>>
{body_text}
<<<END>>>

Metadaten:
{json.dumps(metadata, indent=2, ensure_ascii=False)}

Anzahl Anhänge: {len(attachments)}

{analysis_results_section}
""".strip()

def build_classification_prompt(
    body_text: str,
    metadata: dict,
    ocr_text: str,
    handwriting_text: str = "",
    attachments: list = [],
    email_from: str = "Unbekannt",
    email_recipient: str = "Unbekannt",
    email_subject: str = "Kein Betreff",
    precheck_results: dict = {},
    parser_data: dict = None
) -> str:
    attachments_summary = "\n".join([
        f"- Dateiname: {att.get('filename', 'Unbekannt')}, Typ: {att.get('type', 'Unbekannt')}, URL: {att.get('url', 'Keine URL')}"
        for att in attachments
    ])

    precheck_summary = json.dumps(precheck_results, indent=2, ensure_ascii=False)
    parser_data_section = (
        f"\n#### Parserdaten:\n{json.dumps(parser_data, indent=2, ensure_ascii=False)}\n"
        if parser_data else ""
    )

    return f"""
Du bist ein intelligenter Dokumentenanalyst für einen Handwerksbetrieb.

Nutze die Vorprüfung, OCR-Text, Mailtext, Metadaten, Anhänge und Parserdaten, um die relevanten Informationen zu extrahieren. Gib die Antwort ausschließlich im JSON-Format zurück. Das JSON-Format muss folgende Felder enthalten:

- **dokumenttyp**: Der Typ des Dokuments (z. B. "Anfrage", "Rechnung").
- **richtung**: Die Richtung der Kommunikation ("Eingang" oder "Ausgang").
- **rolle**: Die Rolle des Absenders ("Kunde" oder "Lieferant").
- **kunde**: Der Name des Kunden.
- **lieferant**: Der Name des Lieferanten.
- **projektnummer**: Die Projektnummer, falls vorhanden.
- **auftragsnummer**: Die Auftragsnummer, falls vorhanden.
- **kundennummer**: Die Kundennummer, falls vorhanden.
- **telefonnr**: Die Telefonnummer, falls vorhanden.
- **handynnr**: Die Handynummer, falls vorhanden.
- **emailadresse**: Die E-Mail-Adresse, falls vorhanden.
- **adresse**: Die Adresse, falls vorhanden.
- **abweichende_adresse**: Eine abweichende Adresse, falls vorhanden.
- **privat_geschaeftlich**: Ob es sich um eine private oder geschäftliche Anfrage handelt.
- **anliegen**: Das Anliegen der E-Mail.
- **status**: Der Status der Anfrage.
- **datum_eingang**: Das Eingangsdatum der E-Mail.
- **datum_dokument**: Das Datum des Dokuments.
- **dringend**: Ob die Anfrage dringend ist.
- **summe**: Der Gesamtbetrag, falls vorhanden.
- **notizen**: Zusätzliche Notizen.
- **mail_pdf_url**: Die URL des PDF-Dokuments, falls vorhanden.
- **dateiname**: Der Name der Datei, falls vorhanden.
- **ordnerstruktur**: Die Ordnerstruktur gemäß den definierten Regeln.
- **zu_pruefen**: Ein boolescher Wert, der angibt, ob die E-Mail manuell geprüft werden muss.
- **anhaenge**: Eine Liste der Anhänge mit Dateinamen und URLs.

### Regeln für die Ordnerstruktur:
- **Projekt**: `Scan/Projekte/{{kunde}}/{{projekt}}/{{typ}}`
- **Buchhaltung (Eingang)**: `Scan/Buchhaltung/{{jahr}}/{{monat}}/Eingang/{{lieferant}}`
- **Buchhaltung (Ausgang)**: `Scan/Buchhaltung/{{jahr}}/{{monat}}/Ausgang/{{kunde}}`
- **Zu prüfen**: `Scan/Zu prüfen/{{jahr}}/{{monat}}/Unbekannt`

Hier sind die Eingabedaten:

#### Vorprüfung:
{precheck_summary}

#### OCR-Text:
<<<OCR>>>
{ocr_text}
<<<END>>>

#### Mailtext:
<<<MAIL>>>
{body_text}
<<<END>>>

#### Handschrift:
<<<HANDSCHRIFT>>>
{handwriting_text}
<<<END>>>

#### Anhänge:
{attachments_summary}

#### Metadaten:
{json.dumps(metadata, indent=2, ensure_ascii=False)}

{parser_data_section}

Gib die Antwort ausschließlich im JSON-Format zurück!
""".strip()

def build_weclapp_phase_prompt(gpt_data: dict, parser_data: dict = None) -> str:
    parser_data_section = (
        f"\n#### Parserdaten:\n{json.dumps(parser_data, indent=2, ensure_ascii=False)}\n"
        if parser_data else ""
    )
    return f"""
Du bist ein CRM-Analyst für einen Handwerksbetrieb.

Basierend auf den folgenden Daten, bestimme die passende WeClapp-Verkaufsphase:
{json.dumps(gpt_data, indent=2, ensure_ascii=False)}
{parser_data_section}

Verfügbare Verkaufsphasen:
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

Gib bitte ein JSON zurück:
{{
  "verkaufsphase": "...",
  "begründung": "..."
}}
""".strip()


def build_task_prompt(classification_data: dict, weclapp_data: dict, parser_data: dict = None) -> str:
    """
    Erstellt einen Prompt, um basierend auf Klassifizierungs- und WeClapp-Daten eine Aufgabe abzuleiten.

    Args:
        classification_data (dict): Die Ergebnisse der Klassifizierung.
        weclapp_data (dict): Die Ergebnisse der WeClapp-Phasen-Zuordnung.
        parser_data (dict): Die extrahierten Parserdaten.

    Returns:
        str: Der generierte Prompt.
    """
    parser_data_section = (
        f"\n#### Parserdaten:\n{json.dumps(parser_data, indent=2, ensure_ascii=False)}\n"
        if parser_data else ""
    )
    return f"""
Du bist ein intelligenter Aufgabenmanager für einen Handwerksbetrieb.

Basierend auf den folgenden Daten:
- Klassifizierung: {json.dumps(classification_data, indent=2, ensure_ascii=False)}
- WeClapp-Ergebnis: {json.dumps(weclapp_data, indent=2, ensure_ascii=False)}
{parser_data_section}

Leite eine Aufgabe ab, falls erforderlich. Gib das Ergebnis ausschließlich im JSON-Format zurück. Das JSON-Format muss folgende Felder enthalten:
- **task**: Eine Beschreibung der Aufgabe (z. B. "Rechnung prüfen", "Anfrage beantworten").
- **due_date**: Ein Fälligkeitsdatum im Format YYYY-MM-DD oder leer, falls kein Datum erforderlich ist.
- **priority**: Die Priorität der Aufgabe (hoch, mittel, niedrig).

Beispiele für Aufgaben:
- Wenn die Klassifizierung "Rechnung" ist und die WeClapp-Phase "Rechnung" lautet, könnte die Aufgabe sein: "Rechnung prüfen und freigeben".
- Wenn die Klassifizierung "Anfrage" ist, könnte die Aufgabe sein: "Anfrage beantworten".
- Wenn die Klassifizierung "Reklamation" ist, könnte die Aufgabe sein: "Reklamation bearbeiten".

Gib die Antwort ausschließlich im JSON-Format zurück.
""".strip()