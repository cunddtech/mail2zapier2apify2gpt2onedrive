import json
from modules.msgraph.fetch_mail_metadata import fetch_mail_metadata
from modules.msgraph.download_mail_attachments import download_mail_attachments
from modules.ocr.ocr_pdfco_standard import ocr_pdfco_standard
from modules.gpt.precheck_mail import precheck_mail_with_gpt
from modules.gpt.classify_document_with_gpt import classify_document_with_gpt
from modules.utils.build_result_payload import build_result_payload
from modules.zapier.post_to_zapier import post_to_zapier_webhook
from modules.utils.debug_log import debug_log

DEFAULT_ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

async def mail_main_workflow(public_link, context, input_data):
    debug_log("🚀 Starte Mail-Hauptworkflow...")

    # 1. Mail-Metadaten und Anhänge laden
    mail_metadata = fetch_mail_metadata(context["msgraph_meta"]["user_email"], context["msgraph_meta"]["message_id"])
    debug_log(f"📩 Mail-Metadaten geladen: {json.dumps(mail_metadata, indent=2, ensure_ascii=False)[:512]}")

    attachments_info = download_mail_attachments(mail_metadata)
    debug_log(f"📎 Anhänge gefunden: {len(attachments_info)}")

    if not attachments_info:
        debug_log("⚠️ Keine Anhänge gefunden. Abbruch.")
        return

    # 2. OCR auf Anhänge anwenden
    full_ocr_text = ""
    for attachment in attachments_info:
        try:
            ocr_text = ocr_pdfco_standard(attachment["public_link"])
            full_ocr_text += f"\n\n[Datei: {attachment['filename']}]\n{ocr_text}"
            debug_log(f"✅ OCR abgeschlossen für Anhang: {attachment['filename']}")
        except Exception as e:
            debug_log(f"⚠️ OCR fehlgeschlagen für {attachment['filename']}: {e}")

    if not full_ocr_text.strip():
        debug_log("❌ Kein OCR-Text extrahiert. Abbruch.")
        return

    # 3. Precheck-GPT
    precheck_output = precheck_mail_with_gpt(full_ocr_text)
    try:
        precheck_result = json.loads(precheck_output)
        debug_log(f"✅ Precheck erfolgreich:\n{json.dumps(precheck_result, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        debug_log(f"❌ Precheck-Antwort ist kein valides JSON:\n{precheck_output}")
        return

    # 4. Finale GPT-Analyse
    gpt_output = classify_document_with_gpt(
        ocr_text=full_ocr_text,
        handwriting_text="",
        metadata={
            **context,
            "precheck_dokumenttyp": precheck_result.get("dokumenttyp", ""),
            "aufmass_verdacht": precheck_result.get("aufmass_verdacht", False)
        }
    )

    try:
        gpt_result = json.loads(gpt_output)
        debug_log(f"✅ Finale GPT-Analyse erfolgreich:\n{json.dumps(gpt_result, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        debug_log(f"❌ Finale GPT-Antwort ist kein valides JSON:\n{gpt_output}")
        return

    # 5. Payload aufbauen
    payload = build_result_payload(gpt_result, context)

    # 6. An Zapier senden
    zapier_webhook_url = input_data.get("webhook_url") or DEFAULT_ZAPIER_WEBHOOK_URL
    debug_log(f"🌐 Verwende Zapier Webhook: {zapier_webhook_url}")

    success = post_to_zapier_webhook(zapier_webhook_url, payload)

    if success:
        debug_log("✅ Payload erfolgreich an Zapier gesendet.")
    else:
        debug_log("❌ Fehler beim Senden an Zapier.")

    debug_log("🏁 Mail-Workflow abgeschlossen.")