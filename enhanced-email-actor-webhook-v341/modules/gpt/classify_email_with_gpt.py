import datetime
from modules.mail.fetch_email_details_with_attachments import fetch_email_details_with_attachments
from modules.mail.find_pdf_attachment import find_pdf_attachment
from modules.mail.download_attachment_as_bytes import download_attachment_as_bytes
from modules.ocr.ocr_pdfco_standard import ocr_pdfco_standard
from modules.gpt.precheck_email import precheck_email
from modules.gpt.classify_document_with_gpt import classify_document_with_gpt
from modules.utils.debug_log import debug_log
from modules.utils.build_result_payload import build_result_payload
from modules.zapier.post_to_zapier import post_to_zapier_webhook
from modules.weclapp.weclapp_lookup import (
    lookup_contact_priority,
    lookup_customer_priority,
    lookup_opportunity_priority
)
from modules.utils.analyze_status_difference import analyze_status_difference
from modules.utils.status_summary import add_status_summary
from modules.utils.save_status_summary import save_status_summary_to_onedrive

DEFAULT_ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

async def process_email_workflow(public_link: str, context: dict, input_data: dict, access_token: str):
    debug_log("🔍 Starte vollständige Mail-Verarbeitung...")

    user_email = context["msgraph_meta"]["user_email"]
    message_id = context["msgraph_meta"]["message_id"]

    # 1. Mail laden
    mail_data = await fetch_email_details_with_attachments(user_email, message_id, access_token)
    debug_log(f"📧 Maildaten geladen (Betreff: {mail_data.get('subject', 'kein Betreff')})")

    # 2. Anhang suchen
    pdf_attachment = find_pdf_attachment(mail_data)
    ocr_text = None

    if pdf_attachment:
        debug_log(f"📎 PDF-Anhang gefunden: {pdf_attachment['filename']}")
        file_bytes = await download_attachment_as_bytes(user_email, message_id, pdf_attachment['attachment_id'], access_token)
        ocr_text = ocr_pdfco_standard(file_bytes)
        debug_log("🧠 OCR-Text erfolgreich extrahiert.")
    else:
        debug_log("📄 Kein Anhang gefunden, nutze Mailtext direkt...")
        ocr_text = mail_data.get("body", {}).get("content", "")

    if not ocr_text:
        debug_log("⚠️ Kein Text verfügbar, Abbruch.")
        return

    # 3. Precheck starten
    precheck_result = precheck_email(
        email_from=mail_data.get("from", {}).get("emailAddress", {}).get("address", ""),
        subject=mail_data.get("subject", ""),
        body_text=ocr_text
    )
    debug_log(f"✅ Precheck abgeschlossen:\n{precheck_result}")

    if not precheck_result.get("relevant", False):
        debug_log("🚫 E-Mail als nicht relevant eingestuft, Workflow abgebrochen.")
        return

    # 4. Finale GPT-Dokumentenanalyse
    gpt_result = classify_document_with_gpt(ocr_text)
    debug_log(f"✅ Finale GPT-Analyse abgeschlossen:\n{gpt_result}")

    # 5. WeClapp-Suche starten
    weclapp_info = {}
    email = mail_data.get("from", {}).get("emailAddress", {}).get("address", "")
    customer_name = gpt_result.get("kunde", "")

    contact_data = lookup_contact_priority(email=email, name=customer_name)
    if contact_data:
        weclapp_info["contactId"] = contact_data.get("id")
        debug_log(f"✅ Kontakt gefunden: {contact_data.get('displayName', 'Kein Name')}")

    customer_data = lookup_customer_priority(email=email, name=customer_name)
    if customer_data:
        weclapp_info["customerId"] = customer_data.get("id")
        debug_log(f"✅ Kunde/Interessent gefunden: {customer_data.get('name', 'Kein Name')}")

    opportunity_data = None
    if weclapp_info.get("customerId"):
        opportunity_data = lookup_opportunity_priority(customer_id=weclapp_info["customerId"])
        if opportunity_data:
            weclapp_info["opportunityId"] = opportunity_data.get("id")
            weclapp_info["currentStage"] = opportunity_data.get("salesPhaseName", "unbekannt")
            debug_log(f"✅ Opportunity gefunden: {opportunity_data.get('title', 'Kein Titel')}")

    # 6. Status-Analyse
    status_analysis = None
    if weclapp_info.get("currentStage"):
        current_stage = weclapp_info["currentStage"]
        gpt_doc_type = gpt_result.get("dokumenttyp", "")
        status_analysis = analyze_status_difference(current_stage, gpt_doc_type)

    # 7. Payload bauen
    payload = build_result_payload(gpt_result, context, weclapp_info)
    debug_log(f"📦 Payload gebaut:\n{payload}")

    # 8. Senden an Zapier
    webhook_url = input_data.get("zapier_webhook") or DEFAULT_ZAPIER_WEBHOOK_URL
    debug_log(f"🌐 Sende an Zapier-Webhook: {webhook_url}")

    post_to_zapier_webhook(webhook_url, payload)
    debug_log("✅ Payload erfolgreich an Zapier gesendet.")

    # 9. Status-Summary erweitern
    summary_entry = {
        "mail_subject": mail_data.get("subject", "kein Betreff"),
        "mail_sender": email,
        "mail_received": mail_data.get("receivedDateTime", ""),
        "dokumenttyp": gpt_result.get("dokumenttyp", ""),
        "kunde": gpt_result.get("kunde", ""),
        "lieferant": gpt_result.get("lieferant", ""),
        "projektnummer": gpt_result.get("projektnummer", ""),
        "richtung": gpt_result.get("richtung", ""),
        "weclapp_contact_id": weclapp_info.get("contactId"),
        "weclapp_customer_id": weclapp_info.get("customerId"),
        "weclapp_opportunity_id": weclapp_info.get("opportunityId"),
        "weclapp_current_stage": weclapp_info.get("currentStage", "unbekannt"),
        "gpt_status_vorschlag": status_analysis.get("gpt_suggestion", "unbekannt") if status_analysis else None,
        "abweichung": status_analysis.get("abweichung", False) if status_analysis else False,
        "bemerkung": status_analysis.get("bemerkung", "") if status_analysis else "",
    }
    add_status_summary(summary_entry)
    debug_log("📝 Status-Summary hinzugefügt.")

    # 10. Auto-Save der aktuellen Status-Summary
    now = datetime.datetime.utcnow()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    save_status_summary_to_onedrive(access_token, year, month)

    debug_log("🏁 Mail-Workflow abgeschlossen.")