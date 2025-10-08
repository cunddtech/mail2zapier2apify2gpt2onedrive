def build_precheck_email_prompt(email_from: str, subject: str, body_text: str) -> str:
    """
    Erzeugt den GPT-Prompt für die Relevanzprüfung eingehender E-Mails.
    """
    prompt = f"""
Du bist eine KI, die eingehende E-Mails eines Handwerks- und Bauelemente-Unternehmens analysiert 
und entscheidet, ob diese für den weiteren Prozess relevant sind.

Relevante Inhalte betreffen z. B.:
- neue Anfragen (Vertrieb)
- Rückfragen zu Angeboten
- Auftragsabwicklung oder Reklamationen
- Buchhaltungsdokumente (z. B. Eingangsrechnung → wenn von extern / Ausgangsrechnung → wenn von uns)
- Lieferscheine, Aufmaßblätter, Montagetermine, Materiallieferungen
- Terminabsprachen mit Kunden oder Lieferanten
- Versicherungsdokumente (z. B. Policen, Schadensmeldungen)
- Schreiben von Behörden oder Ämtern (z. B. Bescheide, Aufforderungen)
- Vereinskorrespondenz (z. B. Beitragsabrechnungen)
- Telefonrechnungen (z. B. von Anbietern wie Telekom, Sipgate)
- Softwarerechnungen oder Lizenzabrechnungen (z. B. Microsoft, Adobe)
- Steuerbescheide, Steuerdokumente (z. B. vom Finanzamt)
- Leasingverträge (z. B. für Fahrzeuge oder Maschinen)
- Bankdokumente (z. B. Kontoauszüge, Kreditunterlagen)
- Lohnabrechnungen oder Gehaltsmitteilungen
- Wartungsverträge oder Serviceverträge

Nicht relevant sind z. B.:
- Werbung, Newsletter, Spam
- Autoresponder / automatische Empfangsbestätigungen
- Statusnachrichten ohne Handlungsbedarf (z. B. erfolgreiche Anmeldung)
- interne Systembenachrichtigungen oder Tool-Updates

Sonderregeln:
- Wenn die E-Mail eine Rechnung **an C&D Tech GmbH** adressiert, ist es eine Eingangsrechnung → relevant.
- Wenn **wir** eine Rechnung an jemand senden, ist es eine Ausgangsrechnung → auch relevant.

Antworte IMMER in folgendem JSON-Format:

{{
  "relevant": true oder false,
  "grund": "kurze, klare Begründung"
}}

Hier die E-Mail zur Analyse:

---
Absender: {email_from}
Betreff: {subject}
Inhalt (maximal 1000 Zeichen):
\"\"\"
{body_text[:1000]}
\"\"\"
---
"""
    return prompt