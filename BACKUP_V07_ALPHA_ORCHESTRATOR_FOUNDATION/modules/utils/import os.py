import os
import asyncio
from modules.filegen.generate_folder_temp import generate_folder_temp
from modules.upload.upload_file_to_onedrive import upload_file_to_onedrive
from modules.utils.debug_log import debug_log
from modules.auth.get_graph_token import get_graph_token

# filepath: /Users/cdtechgmbh/Documents/lokal_test/apify_debug_template/actor_files/modules/filegen/test_generate_folder_temp.py


async def test_generate_folder_and_upload():
    # Step 1: Retrieve OneDrive access token
    access_token_onedrive = get_graph_token("onedrive")
    if not access_token_onedrive:
        debug_log("❌ Fehler: Zugriffstoken für OneDrive konnte nicht abgerufen werden.")
        return

    # Step 2: Create a temporary folder
    try:
        base_folder = "TestBase"
        temp_folder = "Temp"
        temp_path = generate_folder_temp(base_folder=base_folder, temp_folder=temp_folder)
        debug_log(f"✅ Temporärer Ordner erstellt: {temp_path}")
    except Exception as e:
        debug_log(f"❌ Fehler beim Erstellen des temporären Ordners: {e}")
        return

    # Step 3: Simulate a file download (mocked content)
    filename = "test_file.txt"
    file_content = b"Dies ist ein Testinhalt."
    temp_file_path = os.path.join(temp_path, filename)
    try:
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_content)
        debug_log(f"✅ Datei erfolgreich im temporären Ordner gespeichert: {temp_file_path}")
    except Exception as e:
        debug_log(f"❌ Fehler beim Speichern der Datei: {e}")
        return

    # Step 4: Upload the file to OneDrive
    try:
        debug_log("⬆️ Lade Datei zu OneDrive hoch...")
        upload_url = await upload_file_to_onedrive(
            folder_path=temp_folder,
            filename=filename,
            file_bytes=file_content,
            access_token_onedrive=access_token_onedrive
        )
        if upload_url:
            debug_log(f"✅ Datei erfolgreich zu OneDrive hochgeladen: {upload_url}")
        else:
            debug_log("❌ Fehler: Datei konnte nicht zu OneDrive hochgeladen werden.")
    except Exception as e:
        debug_log(f"❌ Fehler beim Hochladen der Datei zu OneDrive: {e}")

if __name__ == "__main__":
    asyncio.run(test_generate_folder_and_upload())
    
    
import os
import asyncio
from modules.msgraph.download_attachment_as_bytes import download_attachment_as_bytes
from modules.filegen.generate_folder_temp import generate_folder_temp
from modules.upload.upload_file_to_onedrive import upload_file_to_onedrive
from modules.utils.debug_log import debug_log
from modules.auth.get_graph_token import get_graph_token

# filepath: /Users/cdtechgmbh/Documents/lokal_test/apify_debug_template/test.py


async def main():
    # Step 1: Retrieve access tokens
    access_token_mail = get_graph_token("mail")
    access_token_onedrive = get_graph_token("onedrive")
    if not access_token_mail or not access_token_onedrive:
        debug_log("❌ Fehler: Zugriffstoken konnten nicht abgerufen werden.")
        return

    # Step 2: Define test parameters
    user_id = "test_user_id"
    message_id = "test_message_id"
    attachment_id = "test_attachment_id"
    filename = "test_file.pdf"

    # Step 3: Download the attachment
    try:
        debug_log("⬇️ Lade Anhang herunter...")
        file_bytes = await download_attachment_as_bytes(
            user_id=user_id,
            message_id=message_id,
            attachment_id=attachment_id,
            access_token_mail=access_token_mail
        )
        if not file_bytes:
            debug_log("❌ Fehler: Anhang konnte nicht heruntergeladen werden.")
            return
    except Exception as e:
        debug_log(f"❌ Fehler beim Herunterladen des Anhangs: {e}")
        return

    # Step 4: Create a temporary folder
    try:
        temp_folder = generate_folder_temp(base_folder="Temp")
        temp_file_path = os.path.join(temp_folder, filename)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_bytes)
        debug_log(f"✅ Datei erfolgreich im temporären Ordner gespeichert: {temp_file_path}")
    except Exception as e:
        debug_log(f"❌ Fehler beim Erstellen des temporären Ordners: {e}")
        return

    # Step 5: Upload the file to OneDrive
    try:
        debug_log("⬆️ Lade Datei zu OneDrive hoch...")
        upload_url = await upload_file_to_onedrive(
            folder_path="TestFolder",
            filename=filename,
            file_bytes=file_bytes,
            access_token_onedrive=access_token_onedrive
        )
        if upload_url:
            debug_log(f"✅ Datei erfolgreich zu OneDrive hochgeladen: {upload_url}")
        else:
            debug_log("❌ Fehler: Datei konnte nicht zu OneDrive hochgeladen werden.")
    except Exception as e:
        debug_log(f"❌ Fehler beim Hochladen der Datei zu OneDrive: {e}")

if __name__ == "__main__":
    asyncio.run(main())