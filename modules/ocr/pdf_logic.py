from modules.ocr.ocr_pdfco_standard import ocr_pdfco_standard
from modules.ocr.upload_and_ocr_pdfco import upload_to_pdfco, extract_text_pdfco
from modules.ocr.ocr_pdfco_handwriting import ocr_pdfco_handwriting
from modules.ocr.ocr_pdfco_invoice import ocr_pdfco_invoice
from modules.upload.upload_file_to_onedrive import upload_file_to_onedrive
from modules.utils.debug_log import debug_log

async def process_pdf(user_email, file_bytes: bytes, filename: str, context: dict, access_token_onedrive: str) -> dict:
    """
    Verarbeitet ein PDF und entscheidet, welche Analyse durchgeführt wird:
    - Klassifikation -> PDF.co-Classifier
    - Extraktion -> PDF.co-Parser
    - Handschrift -> Azure OCR
    - Fallback -> Keine Ergebnisse
    """
    debug_log(f"📄 Starte Verarbeitung für PDF: {filename}")

    try:
        # Prüfen, ob eine öffentliche URL im Kontext verfügbar ist
        public_url = context.get("public_url")
        if public_url:
            debug_log(f"🌐 Verwende vorhandene öffentliche URL: {public_url}")
        else:
            debug_log("⬆️ Keine öffentliche URL gefunden, Datei wird hochgeladen...")
            public_url = upload_to_pdfco(file_bytes, filename)
            if not public_url:
                debug_log("❌ Fehler beim Hochladen der Datei.")
                return {
                    "filename": filename,
                    "type": "pdf",
                    "ocr_text": None,
                    "route": "upload_failed",
                    "error": "Fehler beim Hochladen der Datei"
                }

        # 1. Klassifikation des Dokuments
        debug_log(f"🔍 Starte Klassifikation des Dokuments...")
        classifier_result = ocr_pdfco_standard(public_url, context)
        document_classes = classifier_result.get("document_classes", [])
        primary_class = document_classes[0].get("class", "").strip().lower() if document_classes else "unbekannt"

        # Ergebnisse initialisieren
        context["pdf_processing"] = {
            "filename": filename,
            "document_classes": document_classes,
            "primary_class": primary_class,
            "ocr_text": "",
            "routes": []
        }

        debug_log(f"✅ Klassifikation abgeschlossen: {document_classes}")

        # 2. Extraktion basierend auf der Klassifikation
        debug_log(f"📑 Starte Extraktion basierend auf der Klassifikation...")
        parser_result = ocr_pdfco_invoice(public_url, context)
        if parser_result:
            debug_log(f"✅ Extraktion erfolgreich für {filename}.")
            context["pdf_processing"]["invoice_data"] = parser_result.get("invoice", {})
            context["pdf_processing"]["vendor"] = parser_result.get("vendor", {})
            context["pdf_processing"]["customer"] = parser_result.get("customer", {})
            context["pdf_processing"]["payment_details"] = parser_result.get("payment_details", {})
            context["pdf_processing"]["line_items"] = parser_result.get("line_items", [])
            context["pdf_processing"]["ocr_text"] += f"\n{parser_result.get('invoice_text', '')}"
            context["pdf_processing"]["routes"].append("invoice_parser")

        # 3. Handschriftenerkennung bei relevanten Klassen
        if primary_class in ["lieferschein", "leistungsnachweis"]:
            debug_log(f"✍️ Relevante Klasse erkannt ({primary_class}), starte Handschriftenerkennung...")
            handwriting_text = ocr_pdfco_handwriting(public_url, context)
            if handwriting_text:
                debug_log(f"✅ Handschriftenerkennung erfolgreich für {filename}.")
                context["pdf_processing"]["ocr_text"] += f"\n{handwriting_text}"
                context["pdf_processing"]["routes"].append("handwriting")

        # 4. Ergebnisse in OneDrive hochladen
        debug_log(f"⬆️ Lade verarbeitete Daten in OneDrive hoch...")
        upload_result = await upload_file_to_onedrive(
            user_mail=user_email,
            folder_path="Temp",
            filename=filename,
            file_bytes=file_bytes,
            access_token_onedrive=access_token_onedrive
        )
        if upload_result:
            debug_log(f"✅ Upload erfolgreich: {upload_result}")
            context["pdf_processing"]["onedrive_url"] = upload_result
        else:
            debug_log(f"❌ Upload fehlgeschlagen für {filename}.")
            context["pdf_processing"]["onedrive_url"] = None

        return context["pdf_processing"]

    except Exception as e:
        debug_log(f"❌ Fehler bei der Verarbeitung von {filename}: {str(e)}")
        context["pdf_processing"]["error"] = str(e)
        return {
            "filename": filename,
            "type": "pdf",
            "ocr_text": context["pdf_processing"].get("ocr_text", None),
            "route": "error",
            "error": str(e)
        }