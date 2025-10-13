# /test/fetch_apify_result.py

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
RUN_ID = "BJjVtlgCDOh6PZaUz"  # Deine aktuelle Run-ID

API_URL = f"https://api.apify.com/v2/actor-runs/{RUN_ID}"
DATASET_URL_TEMPLATE = "https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true"

headers = {
    "Authorization": f"Bearer {APIFY_TOKEN}"
}

def get_run_status(run_id):
    url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("data", {})

def get_dataset_items(dataset_id):
    url = DATASET_URL_TEMPLATE.format(dataset_id=dataset_id)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    print("[INFO] Warte auf Abschluss des Apify Runs...")

    while True:
        run_info = get_run_status(RUN_ID)
        status = run_info.get("status")
        print(f"[STATUS] Aktueller Status: {status}")

        if status in ["SUCCEEDED", "FAILED", "ABORTED"]:
            break

        time.sleep(5)  # alle 5 Sekunden prüfen

    if status != "SUCCEEDED":
        print(f"[ERROR] Run nicht erfolgreich abgeschlossen: {status}")
        return

    dataset_id = run_info.get("defaultDatasetId")
    if not dataset_id:
        print("[ERROR] Kein Dataset gefunden.")
        return

    print(f"[INFO] Lade Daten aus Dataset: {dataset_id}")
    data = get_dataset_items(dataset_id)

    print("[RESULT] Analyse-Ergebnis:")
    for item in data:
        print(item)

if __name__ == "__main__":
    main()