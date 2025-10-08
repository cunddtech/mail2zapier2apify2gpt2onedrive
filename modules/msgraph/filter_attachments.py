from modules.utils.debug_log import debug_log

def filter_attachments(attachments: list, allowed_types: list = None, max_size: int = None) -> list:
    """
    Filtert Anhänge nach erlaubten Typen und Größen.
    """
    debug_log("🔍 Filtere Anhänge nach Typ und Größe...")

    # Standardwerte setzen
    allowed_types = allowed_types or ["application/pdf", "image/jpeg", "image/png"]
    max_size = max_size or 5 * 1024 * 1024  # 5 MB

    # Sicherstellen, dass max_size ein Integer ist
    try:
        max_size = int(max_size)
    except ValueError:
        debug_log(f"❌ Ungültiger Wert für max_size: {max_size}")
        return []

    filtered_attachments = []
    for attachment in attachments:
        content_type = attachment.get("contentType")
        size = attachment.get("size", 0)
        name = attachment.get("name", "unbekannt")

        # Filterkriterien prüfen
        if content_type in allowed_types and size <= max_size:
            filtered_attachments.append({
                "attachment_id": attachment.get("id"),
                "filename": name,
                "size": size,
                "content_type": content_type,
            })
        else:
            reason = []
            if content_type not in allowed_types:
                reason.append(f"Typ nicht erlaubt: {content_type}")
            if size > max_size:
                reason.append(f"Größe überschritten: {size} Bytes")
            debug_log(f"⚠️ Anhang übersprungen: {name} ({', '.join(reason)})")

    debug_log(f"✅ {len(filtered_attachments)} Anhänge nach Filterung verfügbar.")
    return filtered_attachments