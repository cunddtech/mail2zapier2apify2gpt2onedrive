from dotenv import load_dotenv
load_dotenv()

from download.find_file_in_drive import find_file_in_drive
from utils.build_driveitem_url import build_driveitem_url
from apify.trigger_apify_with_drivefile import trigger_apify_with_drivefile

def main():
    filename = "test_upload_cdtech.pdf"
    folder = "Automatisierung/upload_apify"

    print("[INFO] Suche Datei im Drive...")
    file_info = find_file_in_drive(filename, folder)
    item_id = file_info.get("id")
    if not item_id:
        print("[ERROR] Datei nicht gefunden!")
        return

    print("[INFO] Baue Download-URL...")
    download_url = build_driveitem_url(item_id)

    print("[INFO] Triggere Apify Actor...")
    response = trigger_apify_with_drivefile(download_url, filename)
    print("[SUCCESS] Apify Antwort:")
    print(response)

if __name__ == "__main__":
    main()