# Datei: modules/utils/build_result_payload.py
import json

from modules.utils.debug_log import debug_log

def build_result_payload(context: dict, gpt_result: dict = None, weclapp_info: dict = None, status_analysis: dict = None, additional_fields: dict = None):
    """
    Befüllt den Kontext mit den Ergebnissen für Zapier/Webhook.
    """
    debug_log("🛠 Aktualisiere Kontext mit Payload-Daten...")

    # GPT-Ergebnisse in den Kontext schreiben
    if gpt_result:
        context.update(gpt_result)

    # Basisdaten aus dem Kontext
    context.update({
        "source": context.get("quelle", "unbekannt"),
        "user_email": context.get("msgraph_meta", {}).get("user_email", "unbekannt"),
        "message_id": context.get("msgraph_meta", {}).get("message_id", "unbekannt"),
        "attachment_id": context.get("attachment_id", "unbekannt"),
        "original_filename": context.get("original_filename", "unbekannt.pdf"),
        "mail_pdf_url": context.get("public_link", ""),
    })

    # WeClapp-Daten ergänzen
    if weclapp_info:
        context.update({
            "weclapp_contact_id": weclapp_info.get("contactId"),
            "weclapp_customer_id": weclapp_info.get("customerId"),
            "weclapp_opportunity_id": weclapp_info.get("opportunityId"),
        })

    # Status-Analyse ergänzen
    if status_analysis:
        context["status_check"] = status_analysis

    # Zusätzliche Felder dynamisch hinzufügen
    if additional_fields:
        context.update(additional_fields)

    debug_log(f"📦 Aktualisierter Kontext:\n{json.dumps(context, indent=2, ensure_ascii=False)}")