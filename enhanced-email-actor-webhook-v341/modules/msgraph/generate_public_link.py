import requests  # Hinzufügen des Imports
from modules.utils.debug_log import debug_log

async def generate_public_link(user_email: str, message_id: str, attachment_id: str, access_token: str) -> str:
    """
    Generiert einen öffentlichen Link für einen Anhang in einer E-Mail.
    """
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}/attachments/{attachment_id}/$value"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "view",
        "scope": "anonymous"
    }

    debug_log(f"🌐 Generiere Public Link für Anhang: {attachment_id} (Nachricht: {message_id})")

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        public_link = response.json().get("link", {}).get("webUrl")
        if public_link:
            debug_log(f"✅ Public Link erfolgreich generiert: {public_link}")
            return public_link
        else:
            raise Exception("Kein Public Link in der API-Antwort gefunden.")
    else:
        debug_log(f"❌ Fehler beim Generieren des Public Links: {response.status_code} - {response.text}")
        raise Exception(f"Fehler beim Generieren des Public Links: {response.status_code}")