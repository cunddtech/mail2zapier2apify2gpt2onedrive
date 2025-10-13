import os
import requests
from modules.utils.debug_log import debug_log
from modules.auth.get_graph_token import get_graph_token

async def download_attachments(user_email: str, message_id: str, attachments: list) -> list:
    """
    Lädt die übergebenen Anhänge aus einer E-Mail via MS Graph API herunter.
    Gibt eine Liste von dicts zurück mit Base64-kodiertem Inhalt.
    """

    debug_log("⚙️ Starte Attachment-Download...")

    token = get_graph_token("mail")
    if not token:
        debug_log("❌ Kein Token erhalten, Download abgebrochen.")
        return []

    headers = {
        "Authorization": f"Bearer {token}"
    }

    downloaded_files = []

    for attachment in attachments:
        attachment_id = attachment.get("attachment_id")
        filename = attachment.get("filename", "anhang.pdf")
        url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}/attachments/{attachment_id}/$value"

        try:
            debug_log(f"⬇️ Lade Anhang {filename}...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            file_bytes = response.content

            downloaded_files.append({
                "filename": filename,
                "file_bytes": file_bytes
            })

            debug_log(f"✅ Anhang {filename} erfolgreich geladen.")

        except Exception as e:
            debug_log(f"❌ Fehler beim Download von {filename}: {e}")

    return downloaded_files