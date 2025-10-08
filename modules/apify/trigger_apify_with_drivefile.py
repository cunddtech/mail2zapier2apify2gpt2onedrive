import os
import requests

def trigger_apify_with_drivefile(file_url: str, filename: str):
    apify_token = os.getenv("APIFY_TOKEN")
    actor_id = os.getenv("APIFY_ACTOR_ID")
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
    headers = {
        "Authorization": f"Bearer {apify_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "token": apify_token,
        "input": {
            "msgraph_url": file_url,
            "filename": filename,
            "source": "onedrive"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()