import requests
from modules.utils.debug_log import debug_log

async def upload_file_to_onedrive(user_mail: str, folder_path: str, filename: str, file_bytes: bytes, access_token_onedrive: str, timeout: int = 30) -> str:
    """
    Lädt eine Datei auf OneDrive hoch.
    Gibt die URL der hochgeladenen Datei zurück, falls erfolgreich.
    """

    # Eingabevalidierung
    if not user_mail or not folder_path or not filename or not file_bytes:
        debug_log("❌ Ungültige Eingaben für den Datei-Upload.")
        return None
    if not access_token_onedrive:
        debug_log("❌ Fehler: Access-Token für OneDrive fehlt.")
        return None

    debug_log("⚙️ Starte Datei-Upload zu OneDrive...")
    debug_log(f"📧 Benutzer: {user_mail}")
    debug_log(f"📂 Zielordner: {folder_path}")
    debug_log(f"📄 Dateiname: {filename}")
    debug_log(f"📦 Dateigröße: {len(file_bytes)} Bytes")

    # Basis-URL der Microsoft Graph API
    base_url = f"https://graph.microsoft.com/v1.0/users/{user_mail}/drive/root:/{folder_path}"
    debug_log(f"🌐 Basis-URL: {base_url}")

    # Endpunkt für den Datei-Upload
    upload_url = f"{base_url}/{filename}:/content"
    debug_log(f"🌐 Generierte Upload-URL: {upload_url}")

    headers = {
        "Authorization": f"Bearer {access_token_onedrive}",
        "Content-Type": "application/octet-stream"  # für binäre Daten
    }

    try:
        # Upload der Datei
        debug_log(f"⬆️ Lade Datei hoch: {filename} -> {folder_path}")
        response = requests.put(upload_url, headers=headers, data=file_bytes, timeout=timeout)
        
        # Überprüfen des Erfolgs des Uploads
        if response.status_code in [200, 201]:  # Akzeptiere sowohl 200 als auch 201
            response_data = response.json()
            file_url = response_data.get("webUrl", None)
            if file_url:
                debug_log(f"✅ Datei erfolgreich hochgeladen: {filename} -> {folder_path}")
                debug_log(f"🌐 URL der hochgeladenen Datei: {file_url}")
                return file_url
            else:
                debug_log(f"⚠️ Upload erfolgreich, aber keine Datei-URL erhalten: {response_data}")
                return None
        else:
            debug_log(f"❌ Fehler beim Hochladen der Datei {filename}. Status-Code: {response.status_code}, Antwort: {response.text}")
            return None

    except requests.exceptions.Timeout:
        debug_log(f"❌ Fehler: Timeout beim Hochladen der Datei {filename}.")
        return None
    except requests.exceptions.ConnectionError as e:
        debug_log(f"❌ Verbindungsfehler beim Hochladen der Datei {filename}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        debug_log(f"❌ Fehler beim Hochladen der Datei {filename}: {e}")
        return None