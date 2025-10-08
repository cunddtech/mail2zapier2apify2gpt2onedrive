from modules.utils.debug_log import debug_log

def find_pdf_attachment(mail_data: dict) -> dict or None:
    """Durchsucht Mail-Daten nach PDF-Attachment und gibt die wichtigsten Infos zurück."""
    
    attachments = mail_data.get("attachments", [])
    
    # Prüfe, ob Anhänge ein einzelnes Dictionary sind
    if isinstance(attachments, dict):
        attachments = [attachments]  # In eine Liste umwandeln
    
    debug_log(f"📎 Anhänge in der Mail gefunden: {len(attachments)} Anhänge.")

    for att in attachments:
        debug_log(f"📎 Anhang gefunden: {att}")  # Logge den gesamten Anhang
        if att.get("contentType") == "application/pdf":
            debug_log(f"📎 PDF-Anhang gefunden: {att.get('name')} - ID: {att.get('id')}")
            return {
                "attachment_id": att.get("id"),
                "filename": att.get("name"),
                "user_email": mail_data.get("from", {}).get("emailAddress", {}).get("address", "")
            }
    
    debug_log("📄 Kein PDF-Anhang gefunden.")
    return None  # Kein PDF gefunden