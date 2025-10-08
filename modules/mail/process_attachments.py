import json
from modules.utils.debug_log import debug_log
from modules.msgraph.download_attachment_as_bytes import download_attachment_as_bytes
from modules.upload.upload_file_to_onedrive import upload_file_to_onedrive
from modules.filegen.move_file import move_files_to_final_folder
from modules.msgraph.attachment_manager import analyze_attachments
from modules.ocr.ocr_image_pdfco import ocr_image_pdfco
from modules.ocr.pdf_logic import process_pdf
from modules.gpt.analyze_document_with_gpt import analyze_document_with_gpt
from modules.utils.build_gpt_payload import build_gpt_payload

TEMP_FOLDER = "Temp"

def sanitize_path(text):
    """
    Bereinigt einen Text, um ihn als Teil eines Dateipfads zu verwenden.
    """
    import re
    cleaned = re.sub(r"[^\w\d\-./]", "-", text.strip())
    cleaned = re.sub(r"-{3,}", "--", cleaned)  # Maximal zwei Bindestriche
    return cleaned

async def process_attachments(attachments, user_email, message_id, access_token_mail, access_token_onedrive, context):
    """
    Verarbeitet Anhänge, lädt sie in den temporären Ordner hoch, analysiert sie basierend auf ihrem Typ und bereitet sie für die weitere Verarbeitung vor.
    """
    processed_attachments = []
    context["download_errors"] = []
    context["upload_errors"] = []
    context["file_bytes"] = {}  # Speichert die heruntergeladenen Dateien nach Dateiname

    # 1. Anhänge analysieren und Metadaten prüfen/vereinheitlichen
    debug_log("📎 Analysiere Anhänge...")
    analysis_result = await analyze_attachments(context, user_email, message_id, access_token_mail)
    if not analysis_result["valid"]:
        debug_log(f"❌ Ungültige Anhänge: {analysis_result['reason']}")
        return []

    valid_attachments = analysis_result["attachments"]

    # 2. Anhänge herunterladen (Bytes holen)
    for attachment in valid_attachments:
        filename = attachment.get("filename") or attachment.get("name", "unbekannt")
        if filename not in context["file_bytes"]:
            try:
                if user_email and message_id and access_token_mail and attachment.get("id"):
                    debug_log(f"⬇️ Lade Datei-Bytes für: {filename}")
                    file_bytes = await download_attachment_as_bytes(
                        user_email=user_email,
                        message_id=message_id,
                        attachment_id=attachment["id"],
                        access_token_mail=access_token_mail
                    )
                    if file_bytes:
                        context["file_bytes"][filename] = file_bytes
                    else:
                        debug_log(f"❌ Download fehlgeschlagen für Datei: {filename}")
                        context["download_errors"].append(f"Download fehlgeschlagen für Datei: {filename}")
                        continue
                else:
                    debug_log(f"❌ Fehlende Parameter für Download von Datei: {filename}")
                    context["download_errors"].append(f"Fehlende Parameter für Download von Datei: {filename}")
                    continue
            except Exception as e:
                debug_log(f"❌ Fehler beim Download von Datei: {filename} - {e}")
                context["download_errors"].append(f"Fehler beim Download von Datei: {filename} - {str(e)}")
                continue

    # 3. Anhänge verarbeiten und temporär hochladen
    temp_files = []
    for attachment in valid_attachments:
        try:
            filename = attachment.get("filename") or attachment.get("name", "unbekannt")
            content_type = attachment.get("contentType", "unknown")

            # Hole file_bytes aus dem Kontext (wurde vorher geladen)
            file_bytes = context["file_bytes"].get(filename)
            if not file_bytes:
                debug_log(f"❌ Keine Datei-Bytes gefunden für Datei: {filename}")
                context["download_errors"].append(f"Keine Datei-Bytes gefunden für Datei: {filename}")
                continue

            # 3. Verarbeitung basierend auf Dateityp
            if content_type == "application/pdf":
                debug_log(f"📄 Verarbeite PDF: {filename}")
                ocr_result = await process_pdf(
                    user_email=user_email,
                    file_bytes=file_bytes,
                    filename=filename,
                    context=context,
                    access_token_onedrive=access_token_onedrive
                )
                # HIER Parserdaten übernehmen:
                if ocr_result and isinstance(ocr_result, dict):
                    # Prüfe, ob body existiert, sonst direkt auf ocr_result zugreifen
                    body = ocr_result.get("body", ocr_result)
                    context["pdf_processing"]["invoice_data"] = body.get("header", {})
                    context["pdf_processing"]["vendor"] = body.get("company_information", {})
                    context["pdf_processing"]["customer"] = body.get("customer_information", {})
                    context["pdf_processing"]["payment_details"] = {
                        "totals": body.get("totals", {}),
                        "payment_terms": body.get("payment_terms", {}),
                        "order_details": body.get("order_details", {}),
                    }
                    context["pdf_processing"]["billing_address"] = body.get("billing_address", {})
                    context["pdf_processing"]["shipping_address"] = body.get("shipping_address", {})
            
            elif content_type in ["image/jpeg", "image/png"]:
                debug_log(f"🖼️ Verarbeite Bild: {filename}")
                ocr_result = ocr_image_pdfco(file_bytes)
            else:
                debug_log(f"⚠️ Unbekannter Dateityp: {filename} ({content_type})")
                ocr_result = None

            # 4. Datei in den temporären Ordner hochladen
            debug_log(f"⬆️ Lade Datei in den temporären Ordner hoch: {filename} -> {TEMP_FOLDER}")
            upload_result = await upload_file_to_onedrive(
                user_mail=user_email,
                folder_path=TEMP_FOLDER,
                filename=filename,
                file_bytes=file_bytes,
                access_token_onedrive=access_token_onedrive
            )
            if upload_result:
                temp_files.append({
                    "filename": filename,
                    "content_type": content_type,
                    "url": upload_result,
                    "ocr_result": ocr_result
                })
                debug_log(f"✅ Datei erfolgreich in Temp hochgeladen: {filename}")
            else:
                debug_log(f"❌ Upload in Temp fehlgeschlagen für Datei: {filename}")
                context["upload_errors"].append(f"Upload fehlgeschlagen für Datei: {filename}")

        except Exception as e:
            debug_log(f"❌ Fehler bei der Verarbeitung von Datei: {filename} - {e}")
            context["download_errors"].append(f"Fehler bei der Verarbeitung von Datei: {filename} - {str(e)}")

    # Ergebnisse dem Kontext hinzufügen
    try:
        debug_log(f"📋 Inhalt von temp_files vor Rückgabe: {temp_files}")
        json.dumps(temp_files)  # Test auf Serialisierbarkeit
        context["temp_files"] = temp_files
        #debug_log(f"✅ Verarbeitung der Anhänge abgeschlossen. Dateien im Temp-Ordner:\n{json.dumps(temp_files, indent=2, ensure_ascii=False)}")
    except TypeError as e:
        debug_log(f"❌ temp_files ist nicht JSON-kompatibel: {e}")
        raise

    return temp_files