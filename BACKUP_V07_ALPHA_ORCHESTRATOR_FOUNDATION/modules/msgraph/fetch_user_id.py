import requests
from modules.utils.debug_log import debug_log

async def fetch_user_id_by_email(email_address: str, access_token: str) -> str:
    """
    Ruft die Benutzer-ID (user_id) basierend auf der E-Mail-Adresse oder dem userPrincipalName ab.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    # Versuch 1: Benutzer anhand der E-Mail-Adresse im `mail`-Attribut finden
    url_filter = f"https://graph.microsoft.com/v1.0/users?$filter=mail eq '{email_address}'"
    debug_log(f"🔍 Suche Benutzer-ID mit Filter-URL: {url_filter}")
    try:
        response = requests.get(url_filter, headers=headers)
        debug_log(f"📥 Antwortstatus: {response.status_code}")
        debug_log(f"📥 Antwortinhalt: {response.text}")

        if response.status_code == 200:
            users = response.json().get("value", [])
            if users:
                user_id = users[0].get("id")
                debug_log(f"✅ Benutzer-ID gefunden: {user_id}")
                return user_id
            else:
                debug_log(f"⚠️ Keine Benutzer-ID für E-Mail-Adresse {email_address} im `mail`-Attribut gefunden.")
        else:
            debug_log(f"❌ Fehler beim Abrufen der Benutzer-ID mit Filter-URL: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        debug_log(f"❌ Ausnahme beim Abrufen der Benutzer-ID mit Filter-URL: {e}")

    # Versuch 2: Benutzer anhand des `userPrincipalName` finden
    url_direct = f"https://graph.microsoft.com/v1.0/users/{email_address}"
    debug_log(f"🔍 Suche Benutzer-ID mit Direkt-URL: {url_direct}")
    try:
        response = requests.get(url_direct, headers=headers)
        debug_log(f"📥 Antwortstatus: {response.status_code}")
        debug_log(f"📥 Antwortinhalt: {response.text}")

        if response.status_code == 200:
            user_id = response.json().get("id")
            debug_log(f"✅ Benutzer-ID gefunden: {user_id}")
            return user_id
        else:
            debug_log(f"❌ Fehler beim Abrufen der Benutzer-ID mit Direkt-URL: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        debug_log(f"❌ Ausnahme beim Abrufen der Benutzer-ID mit Direkt-URL: {e}")

    # Wenn beide Versuche fehlschlagen
    debug_log(f"❌ Benutzer-ID konnte für E-Mail-Adresse {email_address} nicht gefunden werden.")
    return None