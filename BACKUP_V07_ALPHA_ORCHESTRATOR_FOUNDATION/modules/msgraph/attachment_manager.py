import mimetypes
from modules.utils.debug_log import debug_log
from modules.msgraph.fetch_email_with_attachments import fetch_email_details_with_attachments

ALLOWED_MIME_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png"
]
MAX_ATTACHMENT_COUNT = 10
MAX_ATTACHMENT_SIZE_MB = 20

async def analyze_attachments(context: dict, user_email=None, message_id=None, access_token_mail=None) -> dict:
    """
    Holt und prüft die Metadaten aller Anhänge, speichert sie im Kontext und gibt das Prüfergebnis zurück.
    """
    # 1. Metadaten holen, falls nötig
    attachments = context.get("attachments", [])
    if (
        isinstance(attachments, str)
        or (isinstance(attachments, list) and attachments and isinstance(attachments[0], str))
        or (isinstance(attachments, list) and attachments and "filename" not in attachments[0])
    ):
        # Metadaten nachladen
        if user_email and message_id and access_token_mail:
            debug_log("🔄 Lade Attachment-Metadaten von MS Graph nach...")
            email_data = await fetch_email_details_with_attachments(user_email, message_id, access_token_mail)
            if email_data and "attachments" in email_data:
                attachments = email_data["attachments"]
                context["attachments"] = attachments
            else:
                debug_log("⚠️ Konnte keine Attachment-Metadaten laden.")
                attachments = []
        else:
            debug_log("⚠️ Keine Zugangsdaten für Metadaten-Nachladung vorhanden.")
            attachments = []

    # 2. Prüfung und Vereinheitlichung
    debug_log(f"📎 Analyse von {len(attachments)} Anhängen gestartet...")

    if not attachments:
        debug_log("⚠️ Keine Anhänge vorhanden.")
        context["valid_attachments"] = []
        return {"valid": False, "reason": "Keine Anhänge vorhanden", "attachments": []}

    if len(attachments) > MAX_ATTACHMENT_COUNT:
        debug_log(f"⚠️ Zuviele Anhänge: {len(attachments)}")
        context["valid_attachments"] = []
        return {"valid": False, "reason": f"Zu viele Anhänge ({len(attachments)} Anhänge)", "attachments": []}

    valid_attachments = []
    for i, attachment in enumerate(attachments):
        filename = attachment.get("filename") or attachment.get("name") or f"unbekannt_{i+1}"
        size_bytes = int(attachment.get("size", 0))
        mimetype = attachment.get("contentType") or mimetypes.guess_type(filename)[0] or ""

        debug_log(f"📄 Anhang: {filename} | {round(size_bytes/1024/1024, 2)} MB | MIME: {mimetype}")

        if size_bytes > MAX_ATTACHMENT_SIZE_MB * 1024 * 1024:
            debug_log(f"⚠️ Datei zu groß: {filename}")
            continue

        if mimetype not in ALLOWED_MIME_TYPES:
            debug_log(f"⚠️ Ungültiger Dateityp: {filename} ({mimetype})")
            continue

        # Schreibe die Werte zurück ins Attachment-Dict
        attachment["filename"] = filename
        attachment["size"] = size_bytes
        attachment["contentType"] = mimetype

        valid_attachments.append(attachment)

    debug_log(f"✅ {len(valid_attachments)} gültige Anhänge gefunden.")
    context["valid_attachments"] = valid_attachments
    return {
        "valid": bool(valid_attachments),
        "reason": "OK" if valid_attachments else "Keine gültigen Anhänge",
        "attachments": valid_attachments
    }