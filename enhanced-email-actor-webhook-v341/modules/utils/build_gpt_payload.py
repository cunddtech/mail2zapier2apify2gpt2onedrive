import json
from modules.utils.debug_log import debug_log

MAX_ATTACHMENTS = 10  # Maximale Anzahl von Anhängen, die in den Payload aufgenommen werden
MAX_OCR_TEXT_LENGTH = 5000  # Maximale Länge des OCR-Textes pro Anhang

def build_gpt_payload(context, attachments, weclapp_info, public_url=None, relevant=None):
    """
    Baut den Payload für die GPT-Analyse mit allen relevanten und geparsten Daten.
    """
    debug_log("🛠 Baue GPT-Payload mit allen relevanten und geparsten Daten...")

    # Begrenze die Anzahl der Anhänge
    if len(attachments) > MAX_ATTACHMENTS:
        debug_log(f"⚠️ Zu viele Anhänge ({len(attachments)}). Begrenze auf {MAX_ATTACHMENTS}.")
        attachments = attachments[:MAX_ATTACHMENTS]

    # Kürze den OCR-Text für jeden Anhang
    for attachment in attachments:
        if "ocr_text" in attachment and isinstance(attachment["ocr_text"], dict):
            ocr_body = attachment["ocr_text"].get("ocr_text", "")
            if len(ocr_body) > MAX_OCR_TEXT_LENGTH:
                debug_log(f"⚠️ OCR-Text für {attachment['filename']} ist zu lang. Kürze auf {MAX_OCR_TEXT_LENGTH} Zeichen.")
                attachment["ocr_text"]["ocr_text"] = ocr_body[:MAX_OCR_TEXT_LENGTH] + "..."

    # Extrahiere nur relevante Daten aus dem Kontext
    email_from = context.get("from_email_address_address", "unbekannt")
    subject = context.get("subject", "kein Betreff")
    body_text = context.get("precheck_body_text", "")[:1500]  # Nur die ersten 1500 Zeichen
    date = context.get("sent_date_time", "")
    errors = context.get("errors", [])
    user_email = context.get("user_email", "unbekannt")
    message_id = context.get("message_id", "unbekannt")

    # Parserdaten aus pdf_processing
    pdf_processing = context.get("pdf_processing", {})
    primary_class = pdf_processing.get("primary_class", "")
    document_classes = pdf_processing.get("document_classes", [])
    invoice_data = pdf_processing.get("invoice_data", {})
    customer = pdf_processing.get("customer", {})
    vendor = pdf_processing.get("vendor", {})
    payment_details = pdf_processing.get("payment_details", {})

    # Zusätzliche Felder aus Invoice-Parser, falls vorhanden
    document_number = invoice_data.get("document_number") or invoice_data.get("invoiceNumber") or ""
    invoice_date = invoice_data.get("date") or invoice_data.get("invoiceDate") or ""
    due_date = payment_details.get("dueDate") or payment_details.get("due_date") or ""
    totals = invoice_data.get("totals", {}) or payment_details.get("totals", {})
    net_amount = totals.get("net_amount", "")
    tax_amount = totals.get("tax_amount", "")
    total_amount = totals.get("total_amount", "")
    tax_rate = totals.get("tax_rate", "")
    customer_number = customer.get("customer_number") or invoice_data.get("customer_number") or ""
    company_name = vendor.get("company_name") or vendor.get("name") or ""
    customer_name = customer.get("customer_name") or customer.get("name") or ""
    billing_address = invoice_data.get("billing_address", {})
    shipping_address = invoice_data.get("shipping_address", {})
    payment_terms = payment_details.get("payment_terms", {}).get("terms") or ""
    order_details = payment_details.get("order_details", {}) or invoice_data.get("order_details", {})
    order_reference = order_details.get("reference", "")
    delivery_date = order_details.get("delivery_date", "")

    # Erstelle den Payload mit allen relevanten und geparsten Daten
    payload = {
        "email_from": email_from,
        "subject": subject,
        "body_text": body_text,
        "date": date,
        "attachments_count": len(context.get("valid_attachments", [])),
        "attachments": context.get("processed_attachments", []),
        "weclapp_data": weclapp_info or {},
        "public_url": context.get("processed_attachments", [{}])[0].get("url", ""),
        "relevant": relevant if relevant is not None else context.get("relevant", False),
        "errors": errors,
        "user_email": user_email,
        "message_id": message_id,
        # Parserdaten explizit
        "primary_class": primary_class,
        "document_classes": document_classes,
        "invoice_data": invoice_data,
        "customer": customer,
        "vendor": vendor,
        "payment_details": payment_details,
        # Wichtige Rechnungsfelder explizit
        "document_number": document_number,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "net_amount": net_amount,
        "tax_amount": tax_amount,
        "tax_rate": tax_rate,
        "total_amount": total_amount,
        "customer_number": customer_number,
        "company_name": company_name,
        "customer_name": customer_name,
        "billing_address": billing_address,
        "shipping_address": shipping_address,
        "payment_terms": payment_terms,
        "order_reference": order_reference,
        "delivery_date": delivery_date,
        # Optional: alle Rohdaten aus pdf_processing für maximale Nachvollziehbarkeit
        "parser_data": pdf_processing,
    }

    # Debugging: Logge die Größe des Payloads
    payload_size = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    debug_log(f"📦 GPT-Payload-Größe: {payload_size} Bytes")
    #debug_log(f"📦 GPT-Payload erstellt:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    return payload