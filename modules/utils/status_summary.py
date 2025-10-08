import requests
import io
import json
import pandas as pd
from modules.utils.debug_log import debug_log

ONEDRIVE_BASE_FOLDER = "/Email/zapier/verarbeitet"  # Hier wird der Base-Ordner definiert

def save_status_summary_to_onedrive(access_token: str, year: str, month: str):
    """
    Speichert die aktuelle Status-Summary automatisch als XLSX und JSON auf OneDrive.
    """

    debug_log(f"💾 Speichere Status-Summary für {year}-{month}...")

    summary = get_status_summary()

    if not summary:
        debug_log("⚠️ Keine Status-Daten vorhanden, nichts zu speichern.")
        return

    # Vorbereitung der Dateinamen
    folder_path = f"{ONEDRIVE_BASE_FOLDER}/{year}/{month}"  # Ordnerstruktur nach Zapier-Protokoll
    filename_xlsx = f"status_summary_{year}-{month}.xlsx"
    filename_json = f"status_summary_{year}-{month}.json"

    try:
        # Erstelle Ordner, falls nicht vorhanden
        create_onedrive_folder(access_token, folder_path)

        # DataFrame erstellen
        df = pd.DataFrame(summary)

        # In-Memory Excel schreiben
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        # Upload zu OneDrive (XLSX)
        upload_to_onedrive(access_token, folder_path, filename_xlsx, excel_buffer.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        debug_log(f"✅ Excel-Datei erfolgreich hochgeladen: {folder_path}/{filename_xlsx}")

    except Exception as e:
        debug_log(f"⚠️ Fehler beim Excel-Speichern: {e}")
        debug_log("➡️ Versuche stattdessen JSON-Backup hochzuladen...")

        try:
            # JSON-Backup schreiben
            json_buffer = io.BytesIO(json.dumps(summary, indent=2).encode("utf-8"))

            # Upload zu OneDrive (JSON)
            upload_to_onedrive(access_token, folder_path, filename_json, json_buffer.read(), content_type="application/json")
            debug_log(f"✅ JSON-Datei erfolgreich hochgeladen: {folder_path}/{filename_json}")

        except Exception as ex:
            debug_log(f"❌ Fehler auch beim JSON-Speichern: {ex}")

def upload_to_onedrive(access_token: str, folder_path: str, filename: str, file_bytes: bytes, content_type: str):
    """
    Hilfsfunktion: Datei auf OneDrive hochladen.
    """

    base_url = "https://graph.microsoft.com/v1.0/me/drive/root:"
    upload_url = f"{base_url}{folder_path}/{filename}:/content"  # Verwende den Ordnerpfad, der erstellt wird

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": content_type
    }

    response = requests.put(upload_url, headers=headers, data=file_bytes)
    response.raise_for_status() 

def create_onedrive_folder(access_token: str, folder_path: str):
    """
    Erstellt einen Ordner auf OneDrive, falls er noch nicht existiert.
    """
    base_url = "https://graph.microsoft.com/v1.0/me/drive/root:"
    folder_url = f"{base_url}{folder_path}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "name": folder_path.split("/")[-1],  # Der Ordnername wird aus dem folder_path extrahiert
        "folder": {},
        "@microsoft.graph.conflictBehavior": "replace"
    }

    response = requests.post(folder_url, headers=headers, json=data)

    if response.status_code == 409:
        debug_log(f"Ordner existiert bereits: {folder_path}")
    elif response.status_code != 201:
        raise Exception(f"Fehler beim Erstellen des Ordners: {response.json()}")
    else:
        debug_log(f"Ordner erfolgreich erstellt: {folder_path}")