import os
import requests
from modules.utils.debug_log import debug_log

async def fetch_email_details_with_attachments(user_email, message_id, access_token):
    """
    Ruft die E-Mail-Daten und Anhänge von Microsoft Graph ab.
    Die Benutzer-ID (user_id) wird aus den Umgebungsvariablen geladen.
    """
    # Benutzer-ID aus Umgebungsvariable laden
    #user_id = os.getenv("USER_ID")
    #if not user_id:
    #    raise ValueError("❌ Fehler: Die Umgebungsvariable 'USER_ID' ist nicht gesetzt.")
    #debug_log(f"📧 Benutzer-ID (aus Umgebungsvariable): {user_id}")

    # URL für E-Mail-Details
    email_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}?$expand=attachments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    debug_log(f"🔍 Abrufe Maildetails für Benutzer-ID: {user_email}, Nachricht ID: {message_id}")
    try:
        response = requests.get(email_url, headers=headers)
        if response.status_code == 200:
            email_data = response.json()
            debug_log(f"✅ E-Mail-Daten erfolgreich abgerufen: Betreff='{email_data.get('subject', 'kein Betreff')}', Absender='{email_data.get('from', {}).get('emailAddress', {}).get('address', 'unbekannt')}'")
            return email_data
        else:
            debug_log(f"❌ Fehler beim Abrufen der Maildetails: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        debug_log(f"❌ Ausnahme beim Abrufen der Maildetails: {e}")
        return None