import requests
from modules.utils.debug_log import debug_log

async def download_attachments(user_email: str, message_id: str, attachments: list, access_token_mail: str) -> list:
    """
    Lädt die übergebenen Anhänge aus einer E-Mail via MS Graph API herunter.
    Gibt eine Liste von dicts zurück mit Dateinamen und Binärdaten.

    Args:
        user_email (str): E-Mail-Adresse des Benutzers.
        message_id (str): ID der Nachricht.
        attachments (list): Liste von Anhängen mit `attachment_id` und optional `filename`.
        access_token_mail (str): Zugriffstoken für Microsoft Graph.

    Returns:
        list: Liste von heruntergeladenen Dateien mit `filename` und `file_bytes`.
    """
    debug_log("⚙️ Starte Attachment-Download...")

    if not access_token_mail:
        debug_log("❌ Kein Zugriffstoken erhalten, Download abgebrochen.")
        return []

    headers = {
        "Authorization": f"Bearer {access_token_mail}"
    }

    downloaded_files = []

    for attachment in attachments:
        attachment_id = attachment.get("attachment_id")
        filename = attachment.get("filename", "anhang.pdf")
        url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}/attachments/{attachment_id}/$value"

        try:
            debug_log(f"⬇️ Lade Anhang {filename} von URL: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            file_bytes = response.content

            downloaded_files.append({
                "filename": filename,
                "file_bytes": file_bytes
            })

            debug_log(f"✅ Anhang {filename} erfolgreich geladen. Größe: {len(file_bytes)} Bytes")

        except requests.exceptions.RequestException as e:
            debug_log(f"❌ Fehler beim Download von {filename}: {e}")

    return downloaded_files