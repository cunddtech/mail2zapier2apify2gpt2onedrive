from modules.utils.debug_log import debug_log
from modules.msgraph.onedrive_manager import move_file_onedrive

BASE_ONEDRIVE_URL = "https://cdtech1-my.sharepoint.com/personal"  # Ersetze dies durch die tatsächliche Basis-URL

def move_files_to_final_folder(access_token_onedrive, user_email, temp_folder, final_folder, processed_attachments, rename_files=False):
    """

    Verschiebt Dateien aus dem temporären Ordner auf OneDrive in den finalen Ordner.

    Args:
        access_token_onedrive (str): Der Zugriffstoken für OneDrive.
        temp_folder (str): Der Pfad zum temporären Ordner auf OneDrive.
        final_folder (str): Der Pfad zum finalen Ordner auf OneDrive.
        processed_attachments (list): Liste der verarbeiteten Anhänge mit URLs.
        rename_files (bool): Ob die Dateien umbenannt werden sollen.

    Returns:
        None
    """
    for attachment in processed_attachments:
        temp_url = attachment.get("url")
        filename = attachment.get("filename")
        new_filename = attachment.get("new_filename", filename) if rename_files else filename
        final_path = f"{final_folder}/{new_filename}"


        if not temp_url:
            debug_log(f"❌ Keine URL für Datei: {filename}")
            continue

        try:
            debug_log(f"📂 Verschiebe Datei auf OneDrive: {temp_url} -> {final_path}")
            move_file_onedrive(access_token_onedrive, user_email, source_item_id, destination_folder_id)
            
            debug_log(f"✅ Datei erfolgreich verschoben: {temp_url} -> {final_path}")
        except Exception as e:
            debug_log(f"❌ Fehler beim Verschieben der Datei {temp_url}: {e}")