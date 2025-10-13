from modules.msgraph.attachment_manager import analyze_attachments
from modules.msgraph.filter_attachments import filter_attachments
from modules.utils.debug_log import debug_log

def validate_and_prepare_attachments(attachments: list, allowed_types=None, max_size=None) -> dict:
    """
    Hauptlogik zur Prüfung und Vorbereitung von Anhängen:
    - Analysiert Anhänge (Art, Anzahl, Größe)
    - Filtert nach erlaubten Typen und Größen
    - Gibt Entscheidung + ggf. Liste zurück
    """
    debug_log("⚙️ Starte Attachment-Logik...")

    # Standardwerte für erlaubte Typen und maximale Größe
    if allowed_types is None:
        allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if max_size is None:
        max_size = 5 * 1024 * 1024  # 5 MB

    # Sicherstellen, dass max_size ein Integer ist
    try:
        max_size = int(max_size)
    except ValueError:
        debug_log(f"❌ Ungültiger Wert für max_size: {max_size}")
        return {
            "proceed": False,
            "reason": "Ungültiger Wert für max_size.",
            "attachments": []
        }
    debug_log(f"🔍 Verwende max_size: {max_size} Bytes")

    # 1. Anhänge analysieren
    check_result = analyze_attachments(attachments)

    if not check_result.get("valid"):
        debug_log(f"❌ Anhänge ungültig: {check_result.get('reason')}")
        return {
            "proceed": False,
            "reason": check_result.get("reason"),
            "attachments": []
        }

    # 2. Anhänge filtern
    prepared_attachments = filter_attachments(attachments, allowed_types, max_size)

    debug_log(f"✅ {len(prepared_attachments)} Anhänge bereit für Download.")
    for attachment in prepared_attachments:
        debug_log(f"  - {attachment.get('name')} ({attachment.get('contentType')}, {attachment.get('size')} Bytes)")

    return {
        "proceed": True if prepared_attachments else False,
        "reason": "Keine gültigen Anhänge gefunden." if not prepared_attachments else None,
        "attachments": prepared_attachments
    }