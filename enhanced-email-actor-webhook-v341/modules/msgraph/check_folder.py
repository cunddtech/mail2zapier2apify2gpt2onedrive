import requests
from modules.utils.debug_log import debug_log

async def ensure_folder_exists(folder_path, access_token_onedrive):
    """
    Stellt sicher, dass ein Ordner in OneDrive existiert. Falls nicht, wird er erstellt.

    Args:
        folder_path (str): Der Pfad des Ordners.
        access_token_onedrive (str): Der Zugriffstoken für OneDrive.

    Raises:
        Exception: Wenn der Ordner nicht erstellt werden konnte.
    """
    try:
        # Prüfe, ob der Ordner existiert
        folder_exists = await check_folder_exists(folder_path, access_token_onedrive)
        if not folder_exists:
            debug_log(f"📂 Ordner existiert nicht. Erstelle Ordner: {folder_path}")
            await create_folder_in_onedrive(folder_path, access_token_onedrive)
        else:
            debug_log(f"📂 Ordner existiert bereits: {folder_path}")
    except Exception as e:
        debug_log(f"❌ Fehler beim Überprüfen/Erstellen des Ordners: {folder_path} - {e}")
        raise
    


async def check_folder_exists(folder_path, access_token_onedrive):
    """
    Überprüft, ob ein Ordner in OneDrive existiert.

    Args:
        folder_path (str): Der Pfad des Ordners.
        access_token_onedrive (str): Der Zugriffstoken für OneDrive.

    Returns:
        bool: True, wenn der Ordner existiert, False sonst.
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token_onedrive}",
            "Content-Type": "application/json"
        }
        # API-Aufruf, um den Ordner zu überprüfen
        response = requests.get(f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}", headers=headers)
        return response.status_code == 200
    except Exception as e:
        debug_log(f"❌ Fehler beim Überprüfen des Ordners: {folder_path} - {e}")
        return False
    
async def create_folder_in_onedrive(folder_path, access_token_onedrive):
    """
    Erstellt einen Ordner in OneDrive.

    Args:
        folder_path (str): Der Pfad des Ordners.
        access_token_onedrive (str): Der Zugriffstoken für OneDrive.

    Raises:
        Exception: Wenn der Ordner nicht erstellt werden konnte.
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token_onedrive}",
            "Content-Type": "application/json"
        }
        # API-Aufruf, um den Ordner zu erstellen
        folder_name = folder_path.split("/")[-1]
        parent_path = "/".join(folder_path.split("/")[:-1])
        payload = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        response = requests.post(
            f"https://graph.microsoft.com/v1.0/me/drive/root:/{parent_path}:/children",
            headers=headers,
            json=payload
        )
        if response.status_code not in [200, 201]:
            raise Exception(f"Fehler beim Erstellen des Ordners: {response.status_code} - {response.text}")
        debug_log(f"✅ Ordner erfolgreich erstellt: {folder_path}")
    except Exception as e:
        debug_log(f"❌ Fehler beim Erstellen des Ordners: {folder_path} - {e}")
        raise