import os
import json
import requests
import asyncio
from openai import OpenAI
from bs4 import BeautifulSoup

# Initialisiere OpenAI-Client mit API-Key aus Umgebungsvariablen
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_mail_data(message_id: str, user_email: str, access_token_mail: str):
    """
    Ruft E-Mail-Daten von Microsoft Graph API ab.
    """
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}"
    headers = {"Authorization": f"Bearer {access_token_mail}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    mail = response.json()
    return {
        "subject": mail.get("subject", ""),
        "body_text": mail.get("body", {}).get("content", ""),
        "email_from": mail.get("from", {}).get("emailAddress", {}).get("address", "")
    }

async def precheck_relevance(context: dict, access_token_mail: str):
    """
    Führt eine Relevanzprüfung für eine E-Mail durch.
    """
    print("[DEBUG] Eingehender Kontext:")
    print(json.dumps(context, indent=2, ensure_ascii=False))

    message_id = context.get("message_id")
    user_email = context.get("user_email")
    rel_trigger = context.get("trigger", "")

    # E-Mail-Daten abrufen, falls message_id und user_email vorhanden sind
    if message_id and user_email:
        print("[INFO] MS Graph-Datenabruf aktiv…")
        try:
            mail_data = fetch_mail_data(message_id, user_email, access_token_mail)
        except Exception as e:
            print(f"[ERROR] MS Graph fehlgeschlagen: {e}")
            mail_data = {}
    else:
        print("[INFO] Fallback: E-Mail-Daten aus Kontext.")
        mail_data = {}

    # Betreff, Inhalt und Absender aus den Daten extrahieren
    subject = mail_data.get("subject") or context.get("subject")
    # Body-Text bereinigen: HTML entfernen, Fallback auf body_preview
    raw_body = mail_data.get("body_text") or context.get("body_content") or context.get("body_preview", "")
    if raw_body:
        # HTML zu Text
        body_text = BeautifulSoup(raw_body, "html.parser").get_text(separator="\n").strip()
    else:
        body_text = ""

    context["precheck_body_text"] = body_text  # falls du das bereinigte HTML speichern willst
    
    email_from = mail_data.get("email_from") or context.get("from_email_address_address")

    if not subject and not body_text:
        return {"relevant": False, "grund": "Weder Betreff noch E-Mail-Inhalt vorhanden."}

    # GPT-Prompt erstellen
    prompt = f"""
    Ich bin eine KI, die eingehende E-Mails eines Handwerks- und Bauelemente-Unternehmens analysiert und entscheide, ob diese für den weiteren Prozess relevant sind.

    Relevante Inhalte betreffen z. B.:
    - neue Anfragen (Vertrieb)
    - Rückfragen zu Angeboten
    - Auftragsabwicklung oder Reklamationen
    - Buchhaltungsdokumente (z. B. Eingangsrechnung → wenn von extern / Ausgangsrechnung → wenn von uns)
    - Lieferscheine, Aufmaßblätter, Montagetermine, Materiallieferung
    - Terminabsprachen mit Kunden oder Lieferanten

    Nicht relevant sind z. B.:
    - Werbung, Newsletter, SPAM
    - Autoresponder / automatische Empfangsbestätigungen
    - Statusnachrichten ohne Handlungsbedarf
    - interne Benachrichtigungen von Tools

    Wenn die E-Mail eine Rechnung **an C&D Tech GmbH** ist, handelt es sich um eine Eingangsrechnung → relevant.
    Wenn **wir** die Rechnung senden, handelt es sich um eine Ausgangsrechnung → ebenfalls relevant.

    Gib deine Entscheidung im folgenden JSON-Format zurück:
    {{
      "relevant": true oder false,
      "grund": "kurze Begründung"
    }}

    Absender: {email_from}
    Betreff: {subject}
    Inhalt:
    {body_text[:1000]}
    """

    print("[DEBUG] GPT Prompt:")
    print(prompt)

    # GPT-Abfrage durchführen
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein smarter Assistent für E-Mail-Relevanzprüfung. Antworte immer als JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        response_text = completion.choices[0].message.content.strip()
        print("[DEBUG] GPT Antwort (roh):")
        print(response_text)

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            result = {"relevant": False, "grund": "Fehlerhafte JSON-Antwort von GPT: " + response_text[:100]}

    except Exception as e:
        result = {"relevant": False, "grund": f"Fehler bei GPT-Abfrage: {str(e)}"}

    result["rel_trigger"] = rel_trigger

    print("[DEBUG] Entscheidungsergebnis:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    context["precheck_result"] = result 

    return result