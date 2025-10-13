import requests
import aiohttp
import os
from modules.utils.debug_log import debug_log

def move_file_onedrive(access_token_onedrive, user_email, source_item_id, destination_folder_id, new_name=None):
    """
    Verschiebt eine Datei auf OneDrive von einem Quellpfad zu einem Zielpfad.

    Args:
        access_token_onedrive (str): Der Zugriffstoken für OneDrive.
        user_email (str): Die E-Mail-Adresse des Benutzers, dessen OneDrive verwendet wird.
        source_item_id (str): Die ID des Quell-Elements auf OneDrive.
        destination_folder_id (str): Die ID des Zielordners auf OneDrive.
        new_name (str, optional): Der neue Name der Datei. Standardmäßig bleibt der Name gleich.

    Returns:
        dict: Die Antwort der OneDrive-API bei Erfolg.
    """
    if not access_token_onedrive:
        raise Exception("❌ Fehler: Kein Zugriffstoken für OneDrive gefunden.")

    headers = {
        "Authorization": f"Bearer {access_token_onedrive}",
        "Content-Type": "application/json"
    }

    # Microsoft Graph API: Verschieben der Datei
    move_payload = {
        "parentReference": {
            "id": destination_folder_id
        }
    }
    if new_name:
        move_payload["name"] = new_name

    # API-Endpunkt für die Datei
    base_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{source_item_id}"
    response = requests.patch(base_url, json=move_payload, headers=headers)

    if response.status_code in [200, 201]:
        debug_log(f"✅ Datei erfolgreich verschoben: {source_item_id} -> {destination_folder_id}")
        return response.json()
    else:
        debug_log(f"❌ Fehler beim Verschieben der Datei: {response.status_code} - {response.text}")
        raise Exception(f"Fehler beim Verschieben der Datei: {response.status_code} - {response.text}")
    
async def delete_file_from_onedrive(access_token_onedrive, user_email, folder_path, filename):
    """
    Löscht eine Datei auf OneDrive basierend auf ihrem Ordnerpfad und Dateinamen.

    Args:
        access_token_onedrive (str): Der Zugriffstoken für OneDrive.
        user_email (str): Die E-Mail-Adresse des Benutzers, dessen OneDrive verwendet wird.
        folder_path (str): Der Pfad des Ordners, in dem sich die Datei befindet.
        filename (str): Der Name der Datei, die gelöscht werden soll.

    Raises:
        Exception: Wenn die Datei nicht gelöscht werden konnte.
    """
    if not access_token_onedrive:
        raise Exception("❌ Fehler: Kein Zugriffstoken für OneDrive gefunden.")

    headers = {
        "Authorization": f"Bearer {access_token_onedrive}",
        "Content-Type": "application/json"
    }

    # API-Endpunkt für das Löschen der Datei basierend auf dem Pfad
    file_path = f"{folder_path}/{filename}".strip("/")
    base_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/root:/{file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.delete(base_url, headers=headers) as response:
            if response.status in [200, 204]:
                debug_log(f"✅ Datei erfolgreich gelöscht: {file_path}")
            else:
                error_text = await response.text()
                debug_log(f"❌ Fehler beim Löschen der Datei: {response.status} - {error_text}")
                raise Exception(f"Fehler beim Löschen der Datei: {response.status} - {error_text}")