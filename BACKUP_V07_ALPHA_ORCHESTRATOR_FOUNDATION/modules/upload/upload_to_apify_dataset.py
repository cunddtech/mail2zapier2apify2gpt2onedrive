# Datei: modules/upload/upload_to_apify_dataset.py

from apify_client import ApifyClient
import os
from modules.utils.debug_log import debug_log

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

def upload_to_apify_dataset(dataset_id, item):
    if not APIFY_TOKEN:
        debug_log("❌ APIFY_TOKEN fehlt in den Umgebungsvariablen.")
        return

    if not dataset_id:
        debug_log("❌ Dataset ID fehlt.")
        return

    try:
        client = ApifyClient(APIFY_TOKEN)
        dataset = client.dataset(dataset_id)
        dataset.push_items([item])
        debug_log(f"✅ Upload erfolgreich: {item}")
    except Exception as e:
        debug_log(f"❌ Fehler beim Upload zu Apify Dataset: {e}")