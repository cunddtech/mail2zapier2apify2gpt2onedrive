import os
import requests
import time
from modules.utils.debug_log import debug_log

PDFCO_API_KEY = os.getenv("PDFCO_API_KEY")
PDFCO_INVOICE_PARSER_URL = "https://api.pdf.co/v1/ai-invoice-parser"
PDFCO_JOB_CHECK_URL = "https://api.pdf.co/v1/job/check"

def ocr_pdfco_invoice(public_url: str, context: dict) -> dict:
    """
    Führt eine Rechnungsanalyse mit PDF.co durch.
    - Verarbeitet eine einzelne öffentliche URL.
    - Fragt die Ergebnisse über /job/check ab.
    - Gibt die extrahierten Rechnungsdaten zurück.
    """
    if not PDFCO_API_KEY:
        raise ValueError("PDFCO_API_KEY fehlt in der Umgebung!")

    debug_log("📑 Starte Rechnungsanalyse mit PDF.co...")

    try:
        debug_log(f"🌐 Verarbeite öffentliche URL: {public_url}")

        # Anfrage an den AI-Invoice-Parser senden
        debug_log("📤 Sende Anfrage an den AI-Invoice-Parser...")
        response = requests.post(
            PDFCO_INVOICE_PARSER_URL,
            headers={
                "x-api-key": PDFCO_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "url": public_url
            }
        )

        if response.status_code != 200 or response.json().get("error"):
            debug_log(f"❌ Fehler bei der Rechnungsanalyse für {public_url}: {response.text}")
            return {"url": public_url, "error": response.text}

        # Job-ID aus der Antwort extrahieren
        result = response.json()
        job_id = result.get("jobId")
        debug_log(f"✅ Job erstellt mit ID: {job_id}")

        # Job-Status abfragen
        debug_log("⏳ Warte auf die Verarbeitung des Jobs...")
        for _ in range(10):  # Maximal 10 Versuche
            time.sleep(3)  # 3 Sekunden warten
            job_response = requests.post(
                PDFCO_JOB_CHECK_URL,
                headers={
                    "x-api-key": PDFCO_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "jobid": job_id
                }
            )

            if job_response.status_code != 200 or job_response.json().get("error"):
                debug_log(f"❌ Fehler bei der Job-Statusabfrage: {job_response.text}")
                return {"url": public_url, "error": job_response.text}

            job_result = job_response.json()
            debug_log(f"🔄 Job-Status: {job_result.get('status')}")

            if job_result.get("status") == "success":
                debug_log(f"✅ Job erfolgreich abgeschlossen: {job_result}")
            
                body = job_result.get("body", {})
                invoice_data = body.get("invoice") or body.get("header") or {}
                vendor = body.get("vendor") or body.get("company_information") or {}
                customer = body.get("customer") or body.get("customer_information") or {}
                payment_details = body.get("paymentDetails") or {
                    "totals": body.get("totals", {}),
                    "payment_terms": body.get("payment_terms", {}),
                    "order_details": body.get("order_details", {}),
                }
                billing_address = body.get("billingAddress") or body.get("billing_address") or {}
                shipping_address = body.get("shippingAddress") or body.get("shipping_address") or {}
                line_items = body.get("lineItems") or body.get("items") or []
            
                # >>> Kontext befüllen: Schreibe ALLE Felder aus body in context["pdf_processing"] <<<
                if context is not None and isinstance(context, dict):
                    context["pdf_processing"] = context.get("pdf_processing", {})
                    # Schreibe alle Felder aus body in den Kontext
                    for key, value in body.items():
                        context["pdf_processing"][key] = value
                    # Zusätzlich die wichtigsten Fallbacks für Kompatibilität
                    context["pdf_processing"]["invoice_data"] = invoice_data
                    context["pdf_processing"]["vendor"] = vendor
                    context["pdf_processing"]["customer"] = customer
                    context["pdf_processing"]["payment_details"] = payment_details
                    context["pdf_processing"]["billing_address"] = billing_address
                    context["pdf_processing"]["shipping_address"] = shipping_address
                    
                return {
                    "url": public_url,
                    "job_id": job_id,
                    "vendor": vendor,
                    "customer": customer,
                    "invoice": invoice_data,
                    "payment_details": payment_details,
                    "line_items": line_items,
                    "others": body.get("others", {}),
                    "invoice_data": invoice_data,
                    "vendor_data": vendor,
                    "customer_data": customer,
                    "payment_details_data": payment_details,
                    "billing_address": billing_address,
                    "shipping_address": shipping_address,
                    "raw_body": body
                }
            if job_result.get("status") in ["failed", "aborted"]:
                debug_log(f"❌ Job fehlgeschlagen: {job_result}")
                return {"url": public_url, "error": f"Job fehlgeschlagen: {job_result}"}

        # Timeout, wenn der Job nicht abgeschlossen wird
        debug_log(f"❌ Job nicht abgeschlossen nach 10 Versuchen: {job_id}")
        return {"url": public_url, "error": "Job nicht abgeschlossen"}

    except Exception as e:
        debug_log(f"❌ Fehler bei der Rechnungsanalyse für {public_url}: {str(e)}")
        return {"url": public_url, "error": str(e)}