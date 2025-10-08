import json
from modules.utils.debug_log import debug_log

MAX_ATTACHMENTS = 5  # Maximale Anzahl von Anhängen, die in den Payload aufgenommen werden
MAX_OCR_TEXT_LENGTH = 1000  # Maximale Länge des OCR-Textes pro Anhang

def build_gpt_payload(context, attachments, weclapp_info, public_link=None, relevant=None):
    """
    Baut den Payload für die GPT-Analyse.

    Args:
        context (dict): Kontextdaten mit `email_from`, `subject`, `body_text`, `date`, etc.
        attachments (list): Liste der verarbeiteten Anhänge.
        weclapp_info (dict): WeClapp-Daten.
        public_link (str): Öffentlicher Link zur E-Mail (optional).
        relevant (bool): Ob die E-Mail als relevant eingestuft wurde (optional).

    Returns:
        dict: Der GPT-Payload.
    """
    debug_log("🛠 Baue GPT-Payload...")

    if len(attachments) > MAX_ATTACHMENTS:
        debug_log(f"⚠️ Zu viele Anhänge ({len(attachments)}). Begrenze auf {MAX_ATTACHMENTS}.")
        attachments = attachments[:MAX_ATTACHMENTS]

    for attachment in attachments:
        if "ocr_text" in attachment and isinstance(attachment["ocr_text"], dict):
            ocr_body = attachment["ocr_text"].get("ocr_text", "")
            if len(ocr_body) > MAX_OCR_TEXT_LENGTH:
                debug_log(f"⚠️ OCR-Text für {attachment['filename']} ist zu lang. Kürze auf {MAX_OCR_TEXT_LENGTH} Zeichen.")
                attachment["ocr_text"]["ocr_text"] = ocr_body[:MAX_OCR_TEXT_LENGTH] + "..."

    fallback_attachment = attachments[0] if attachments else {}

    payload = {
        "email_from": context.get("email_from") or fallback_attachment.get("email_from") or fallback_attachment.get("sender") or "unbekannt",
        "email_subject": context.get("subject") or fallback_attachment.get("subject") or "kein Betreff",
        "subject": context.get("subject") or fallback_attachment.get("subject") or "kein Betreff",
        "body_text": context.get("body_text", ""),
        "date": context.get("date") or fallback_attachment.get("date") or "Unbekannt",
        "attachments_count": len(attachments),
        "attachments": attachments,
        "precheck_result": context.get("precheck_result", {}),
        "weclapp_data": weclapp_info or {},
        "customer_name": weclapp_info.get("customer_name", ""),
        "opportunity_id": weclapp_info.get("opportunity_id", ""),
        "contact_id": weclapp_info.get("contact_id", ""),
        "public_link": public_link,
        "source": context.get("source", "unbekannt"),
        "relevant": True if str(relevant).lower() == "true" else False,
        "processed_attachments": attachments,
        "generated_documents": context.get("generated_documents", []),
        "errors": context.get("errors", []),
        "user_email": context.get("user_email") or fallback_attachment.get("user_email") or "unbekannt",
        "message_id": context.get("message_id", "unbekannt"),
        "attachment_id": context.get("attachment_id", "unbekannt"),
        "original_filename": context.get("original_filename") or fallback_attachment.get("filename", "unbekannt.pdf"),
        "mail_pdf_url": context.get("mail_pdf_url") or fallback_attachment.get("url"),
        "ocr_text": context.get("ocr_text") or fallback_attachment.get("ocr_text", {}).get("ocr_text", ""),
        "handwriting_text": context.get("handwriting_text") or fallback_attachment.get("ocr_text", {}).get("handwriting_text", ""),
        "metadata": context.get("metadata") or fallback_attachment.get("ocr_text", {}).get("metadata", {})
    }

    # 🧠 Rollenkorrektur bei Eingang
    if payload.get("richtung") == "Eingang" and payload.get("rolle") == "Lieferant":
        debug_log("🔁 Korrektur: Rolle auf 'Kunde' gesetzt (wegen Richtung = Eingang).")
        payload["rolle"] = "Kunde"

    payload_size = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    debug_log(f"📦 GPT-Payload-Größe: {payload_size} Bytes")
    #debug_log(f"📦 GPT-Payload erstellt:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    return payload

def debug_output_gpt_result(gpt_result):
    debug_log("\n✅ GPT-Analyse abgeschlossen. Ergebnisse (strukturiert):\n")

    debug_log("🧠 Klassifizierungs-Ergebnis:")
    for key in [
        "dokumenttyp", "richtung", "rolle", "kunde", "lieferant",
        "projektnummer", "summe", "notizen", "datum", "dateiname",
        "ordnerstruktur", "zu_pruefen"]:
        debug_log(f"  {key}: {gpt_result.get(key, '')}")

    debug_log("\n🧩 WeClapp-Phasen-Zuordnung:")
    debug_log(f"  Verkaufsphase: {gpt_result.get('verkaufsphase', '')}")
    debug_log(f"  Begründung: {gpt_result.get('verkaufsphase_begründung') or gpt_result.get('begründung', 'k.A.')}")

    debug_log("\n📧 E-Mail-Daten:")
    debug_log(f"  - Absender: {gpt_result.get('email_from', 'Unbekannt')}")
    debug_log(f"  - Betreff: {gpt_result.get('subject', 'Kein Betreff')}")
    debug_log(f"  - Datum: {gpt_result.get('date', 'Unbekannt')}")
    debug_log(f"  - Quelle: {gpt_result.get('source', 'Unbekannt')}")
    debug_log(f"  - Relevanz: {'Ja' if gpt_result.get('relevant') else 'Nein'}")
    debug_log(f"  - User E-Mail: {gpt_result.get('user_email', 'Unbekannt')}")

    debug_log("\n💬 E-Mail-Text:")
    debug_log(gpt_result.get("body_text", "Kein Text verfügbar"))

    debug_log("\n📎 Anhänge:")
    attachments = gpt_result.get("attachments", [])
    if attachments:
        for att in attachments:
            debug_log(f"  - {att.get('filename', 'Unbekannt')} ({att.get('type', 'Unbekannt')})")
    else:
        debug_log("  Keine Anhänge vorhanden.")

    debug_log("\n📂 Verarbeitete Anhänge:")
    processed = gpt_result.get("processed_attachments", [])
    if processed:
        for att in processed:
            debug_log(f"  - {att.get('filename', 'Unbekannt')} → {att.get('url', 'keine URL')}")
    else:
        debug_log("  Keine verarbeiteten Anhänge vorhanden.")

    debug_log("\n❌ Fehler:")
    errors = gpt_result.get("errors", [])
    if errors:
        for err in errors:
            debug_log(f"  - {err}")
    else:
        debug_log("  Keine Fehler.")

    debug_log("\n📊 Zusammenfassung der GPT-Analyse:")
    for key in ["dokumenttyp", "richtung", "rolle", "summe", "notizen"]:
        debug_log(f"  - {key.capitalize()}: {gpt_result.get(key, '')}")