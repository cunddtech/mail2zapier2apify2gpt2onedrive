import json
import os
import datetime
import requests
from modules.weclapp.weclapp_handler import fetch_weclapp_data
from modules.zapier.post_to_zapier import post_to_zapier_webhook
from modules.utils.debug_log import debug_log
from modules.mail.process_attachments import process_attachments
from modules.gpt.analyze_document_with_gpt import analyze_document_with_gpt
from modules.utils.build_gpt_payload import build_gpt_payload
from modules.msgraph.fetch_email_with_attachments import fetch_email_details_with_attachments
from modules.gpt.debug_output_gpt_result import debug_output_gpt_result
from modules.validation.precheck_relevance import precheck_relevance
from modules.utils.pdfco_api import extract_data_with_template
from modules.filegen.folder_logic import generate_folder_and_filenames
from modules.filegen.move_file import move_files_to_final_folder
from modules.msgraph.onedrive_manager import move_file_onedrive
from modules.upload.upload_file_to_onedrive import upload_file_to_onedrive
from modules.msgraph.check_folder import ensure_folder_exists
from modules.msgraph.onedrive_manager import delete_file_from_onedrive

def call_apify_actor(actor_id, api_token, payload):
    """
    Führt einen Aufruf an den Apify-Actor aus und gibt die Ergebnisse zurück.
    """
    if not actor_id or not api_token:
        debug_log("❌ Fehler: Apify-Umgebungsvariablen sind nicht korrekt gesetzt.")
        return {}

    apify_actor_url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
    try:
        response = requests.post(
            apify_actor_url,
            headers={"Authorization": f"Bearer {api_token}"},
            json=payload
        )
        if response.status_code == 200:
            debug_log(f"✅ Apify-Actor-Ergebnisse: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        elif response.status_code == 404:
            debug_log("❌ Fehler: Actor-Task wurde nicht gefunden. Überprüfe die Actor-ID.")
        else:
            debug_log(f"⚠️ Fehler beim Aufruf des Apify-Actors: {response.status_code} - {response.text}")
    except Exception as e:
        debug_log(f"❌ Ausnahme beim Aufruf des Apify-Actors: {str(e)}")
    return {}

async def process_email_workflow(public_link: str, input_data: dict, access_token_mail, access_token_onedrive, context: dict):
    debug_log("🔍 Starte vollständige Mail-Verarbeitung...")

    try:
        # 1. Relevanzprüfung
        debug_log("🧠 Starte Relevanzprüfung...")
        relevance_result = await precheck_relevance(context, access_token_mail)
        context["precheck_result"] = relevance_result
        context["relevant"] = relevance_result.get("relevant", False)

        if not relevance_result.get("relevant", False):
            debug_log(f"❌ Mail als nicht relevant eingestuft: {relevance_result.get('grund', 'Kein Grund angegeben')}")
            context["step"] = "irrelevant"
            return context
        context["step"] = "relevanz_geprüft"

        # 2. Anhänge prüfen und Metadaten ggf. nachladen
        attachments = context.get("attachments", [])
        if not attachments:
            debug_log("⚠️ Keine Anhänge gefunden. Fortsetzung der Analyse ohne Anhänge.")
            processed_attachments = []
        else:
            if attachments and isinstance(attachments[0], dict) and "filename" not in attachments[0]:
                debug_log("🔄 Lade Attachment-Metadaten von MS Graph nach...")
                email_data = await fetch_email_details_with_attachments(
                    user_email=context.get("user_email"),
                    message_id=context.get("message_id"),
                    access_token=access_token_mail
                )
                if email_data and "attachments" in email_data:
                    context["attachments"] = email_data["attachments"]
                    context["attachments_metadata"] = email_data["attachments"]
                else:
                    debug_log("⚠️ Konnte keine Attachment-Metadaten laden, fahre mit IDs fort.")

            processed_attachments = await process_attachments(
                attachments=context["attachments"],
                user_email=context.get("user_email"),
                message_id=context.get("message_id"),
                access_token_mail=access_token_mail,
                access_token_onedrive=access_token_onedrive,
                context=context
            )
            context["processed_attachments"] = processed_attachments
            if not processed_attachments:
                debug_log("⚠️ Keine Anhänge wurden verarbeitet. Fortsetzung der Analyse ohne Anhänge.")
                processed_attachments = []
        context["step"] = "attachments_processed"

        # 3. Generiere Ordner und Dateinamen
        gpt_input = build_gpt_payload(
            context=context,
            attachments=processed_attachments,
            weclapp_info=context.get("weclapp_info", {}),
            public_url=context.get("public_url", {}),
            relevant=context.get("relevant", False)
        )
        context["gpt_input"] = gpt_input
        context["step"] = "gpt_input_built"

        # 4. GPT-Analyse
        gpt_result = await analyze_document_with_gpt(gpt_input)
        if not gpt_result:
            debug_log(f"❌ GPT-Analyse fehlgeschlagen. Eingabedaten: {json.dumps(gpt_input, indent=2, ensure_ascii=False)}")
            context["step"] = "gpt_failed"
            return context
        context["gpt_result"] = gpt_result
        context["step"] = "gpt_analyzed"

        # 5. Apify-Actor-Aufruf (optional, falls benötigt)
        apify_actor_id = os.getenv("APIFY_ACTOR_ID")
        apify_api_token = os.getenv("APIFY_API_TOKEN")
        if apify_actor_id and apify_api_token:
            debug_log("🤖 Rufe Apify-Actor auf...")
            apify_result = call_apify_actor(apify_actor_id, apify_api_token, gpt_result)
            context["apify_result"] = apify_result
            context["step"] = "apify_called"

        # 6. Ordner und Dateinamen generieren
        folder_data = generate_folder_and_filenames(context, gpt_result)
        context["folder_data"] = folder_data
        debug_log(f"📂 Generierte Ordner und Dateinamen:\n{json.dumps(folder_data, indent=2, ensure_ascii=False)}")
        context["step"] = "folder_generated"

        # 7. Lade Dateien in den finalen Ordner hoch
        final_folder_path = folder_data["ordnerstruktur"]
        debug_log(f"⬆️ Lade Dateien in den finalen Ordner hoch: {final_folder_path}")

        for i, attachment in enumerate(processed_attachments):
            try:
                # Hole den passenden generierten Dateinamen, fallback auf Originalnamen
                pdf_filenames = folder_data.get("pdf_filenames", [])
                filename = pdf_filenames[i] if i < len(pdf_filenames) else attachment["filename"]
                debug_log(f"⬆️ Lade Datei hoch: {filename} -> {final_folder_path}")
                file_bytes = context["file_bytes"].get(attachment["filename"])
                if not file_bytes:
                    debug_log(f"⚠️ Keine Datei-Bytes gefunden für: {attachment['filename']}. Überspringe Upload.")
                    context.setdefault("upload_errors", []).append(f"Keine Datei-Bytes gefunden für: {attachment['filename']}")
                    continue
        
                final_upload_result = await upload_file_to_onedrive(
                    user_mail=context.get("user_email"),
                    folder_path=final_folder_path,
                    filename=filename,
                    file_bytes=file_bytes,
                    access_token_onedrive=access_token_onedrive
                )
                if final_upload_result:
                    debug_log(f"✅ Datei erfolgreich am Zielpfad hochgeladen: {filename}")
                else:
                    debug_log(f"❌ Fehler beim Hochladen der Datei am Zielpfad: {filename}")
                    context.setdefault("upload_errors", []).append(f"Fehler beim Hochladen der Datei am Zielpfad: {filename}")
            except Exception as e:
                debug_log(f"❌ Fehler beim Hochladen der Datei: {attachment['filename']} - {e}")
                context.setdefault("upload_errors", []).append(f"Fehler beim Hochladen der Datei: {attachment['filename']} - {str(e)}")     
        context["step"] = "attachments_uploaded"
        
        # Robust alle möglichen Felder abdecken
        pdf_proc = context.get("pdf_processing", {})
        invoice_data = (
            pdf_proc.get("invoice_data")
            or pdf_proc.get("invoice")
            or pdf_proc.get("header")
            or {}
        )
        vendor = (
            pdf_proc.get("vendor")
            or pdf_proc.get("vendor_data")
            or pdf_proc.get("company_information")
            or {}
        )
        customer = (
            pdf_proc.get("customer")
            or pdf_proc.get("customer_data")
            or pdf_proc.get("customer_information")
            or {}
        )
        payment_details = (
            pdf_proc.get("payment_details")
            or pdf_proc.get("paymentDetails")
            or {
                "totals": pdf_proc.get("totals", {}),
                "payment_terms": pdf_proc.get("payment_terms", {}),
                "order_details": pdf_proc.get("order_details", {}),
            }
        )
        billing_address = (
            pdf_proc.get("billing_address")
            or pdf_proc.get("billingAddress")
            or {}
        )
        shipping_address = (
            pdf_proc.get("shipping_address")
            or pdf_proc.get("shippingAddress")
            or {}
        )
        task_data = gpt_result.get("task_data", {})
        
        weclapp_info = context.get("weclapp_info", {})
        weclapp_kunde = weclapp_info.get("kunde", None)
        weclapp_lieferant = weclapp_info.get("lieferant", None)
        weclapp_projekt = weclapp_info.get("projekt", None)
        weclapp_auftragsnummer = weclapp_info.get("auftragsnummer", None)
        weclapp_id = weclapp_info.get("weclapp_id", None)
        
        def get_task_data(gpt_result, context):
            # Prüfe verschiedene mögliche Felder im gpt_result
            for key in ("task_data", "aufgabe", "task", "todo", "taskResult"):
                value = gpt_result.get(key)
                if value and isinstance(value, dict) and any(value.values()):
                    return value
                if value and isinstance(value, str) and value.strip():
                    return {"Beschreibung": value.strip(), "Fälligkeitsdatum": "", "Priorität": "niedrig"}
            # Prüfe auch im Kontext
            for key in ("task_data", "aufgabe", "task", "todo", "taskResult"):
                value = context.get(key)
                if value and isinstance(value, dict) and any(value.values()):
                    return value
                if value and isinstance(value, str) and value.strip():
                    return {"Beschreibung": value.strip(), "Fälligkeitsdatum": "", "Priorität": "niedrig"}
            # Fallback
            return {
                "Beschreibung": "Keine Aufgabe erforderlich",
                "Fälligkeitsdatum": "",
                "Priorität": "niedrig"
            }
        task_data = get_task_data(gpt_result, context)

        # 8. Erstelle den finalen Payload
        final_payload = {
            "Dokumenttyp": gpt_result.get("dokumenttyp", "Rechnung"),
            "Richtung": gpt_result.get("richtung", "Eingang"),
            "Rolle": gpt_result.get("rolle", "Lieferant"),
            "Rechnungsnummer": invoice_data.get("document_number") or invoice_data.get("invoiceNumber") or invoice_data.get("nummer") or "Unbekannt",
            "Rechnungsdatum": invoice_data.get("date") or invoice_data.get("invoiceDate") or "Unbekannt",
            "E-Mail-Eingang": context.get("created_date_time", "Unbekannt"),
            "Fälligkeit": payment_details.get("dueDate") or payment_details.get("fälligkeitsdatum") or "Unbekannt",
            "Lieferant": vendor.get("company_name") or vendor.get("name") or context.get("from_email_address_name", "Unbekannt"),
            "Kunde": customer.get("customer_name") or customer.get("name") or gpt_result.get("kunde", "Unbekannt"),
            "Projekt": payment_details.get("projectNumber") or invoice_data.get("project_number") or "Unbekannt",
            "WeClapp": {
                "Kunde": weclapp_kunde,
                "Lieferant": weclapp_lieferant,
                "Projekt": weclapp_projekt,
                "Auftragsnummer": weclapp_auftragsnummer,
                "WeClapp-ID": weclapp_id,
                "Weitere_Info": weclapp_info
            },
            "Beträge": {
                "Zwischensumme": (
                    payment_details.get("subtotal")
                    or payment_details.get("net_amount")
                    or payment_details.get("totals", {}).get("net_amount")
                    or "Unbekannt"
                ),
                "MwSt.": (
                    payment_details.get("tax")
                    or payment_details.get("tax_amount")
                    or payment_details.get("totals", {}).get("tax_amount")
                    or "Unbekannt"
                ),
                "Gesamtbetrag": (
                    payment_details.get("total")
                    or payment_details.get("total_amount")
                    or payment_details.get("totals", {}).get("total_amount")
                    or "Unbekannt"
                ),
            },
            "Zahlungsbedingungen": (
                payment_details.get("terms")
                or payment_details.get("payment_terms", {}).get("terms")
                or payment_details.get("payment_terms")
                or payment_details.get("payment_terms_text")
                or "Unbekannt"
            ),
            "Rechnungsadresse": billing_address,
            "Lieferadresse": shipping_address,
            "Ablageort": {
                "Ordner": folder_data.get("ordnerstruktur", ""),
                "Dateipfad": [
                    {
                        "Dateiname": name,
                        "Link": att.get("url", "Keine Datei")
                    }
                    for name, att in zip(folder_data.get("pdf_filenames", []), processed_attachments)
                ]
            },
            "Status": {
                "Relevanz": gpt_result.get("precheck_result", {}).get("relevant", True),
                "Manuell prüfen": gpt_result.get("zu_pruefen", True)
            },
            "Aufgabe": task_data
        }

        context["final_payload"] = final_payload
        context["step"] = "payload_created"
        debug_log(f"📦 Finaler Payload:\n{json.dumps(final_payload, indent=2, ensure_ascii=False)}")

        # 9. Übergabe an Zapier
        zapier_webhook_url = context.get("zapier_webhook")
        if zapier_webhook_url:
            debug_log("🌐 Sende Daten an Zapier...")
            try:
                headers = {"Content-Type": "application/json"}
                zapier_response = requests.post(zapier_webhook_url, data=json.dumps(final_payload), headers=headers)
                if zapier_response and zapier_response.status_code == 200:
                    debug_log("✅ Daten erfolgreich an Zapier gesendet.")
                else:
                    debug_log(f"⚠️ Fehler beim Senden an Zapier: {zapier_response.status_code if zapier_response else 'Keine Antwort'} - {zapier_response.text if zapier_response else 'Keine Details'}")
            except Exception as e:
                debug_log(f"❌ Fehler beim Verbinden mit dem Zapier-Webhook: {e}")
        else:
            debug_log("⚠️ Kein Zapier-Webhook-URL gefunden. Daten werden nicht gesendet.")
        context["step"] = "zapier_sent"

        # 10. Speichere die context-Datei als JSON im Zielpfad
        try:
            serializable_context = {k: v for k, v in context.items() if k != "file_bytes"}
            context_file_bytes = json.dumps(serializable_context, indent=2, ensure_ascii=False).encode("utf-8")
            verarbeitet_folder = "/scan/verarbeitet"
            pdf_filenames = context.get("folder_data", {}).get("pdf_filenames", [])
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            if pdf_filenames:
                for pdf_filename in pdf_filenames:
                    base_name = os.path.splitext(pdf_filename)[0]
                    json_filename = f"{base_name}_{timestamp}.json"
                    debug_log(f"⬆️ Speichere context-Datei unter neuem Namen: {json_filename} -> {verarbeitet_folder}")
                    verarbeitet_upload_result = await upload_file_to_onedrive(
                        user_mail=context.get("user_email"),
                        folder_path=verarbeitet_folder,
                        filename=json_filename,
                        file_bytes=context_file_bytes,
                        access_token_onedrive=access_token_onedrive
                    )
                    if verarbeitet_upload_result:
                        debug_log(f"✅ context-Datei erfolgreich unter neuem Namen gespeichert: {json_filename}")
                    else:
                        debug_log(f"❌ Fehler beim Speichern der context-Datei unter neuem Namen: {json_filename}")
                        context.setdefault("upload_errors", []).append(f"Fehler beim Speichern der context-Datei unter neuem Namen: {json_filename}")
            else:
                # Kein Anhang, also generischer Name
                json_filename = f"unbekannt_{timestamp}.json"
                debug_log(f"⬆️ Speichere context-Datei unter generischem Namen: {json_filename} -> {verarbeitet_folder}")
                verarbeitet_upload_result = await upload_file_to_onedrive(
                    user_mail=context.get("user_email"),
                    folder_path=verarbeitet_folder,
                    filename=json_filename,
                    file_bytes=context_file_bytes,
                    access_token_onedrive=access_token_onedrive
                )
                if verarbeitet_upload_result:
                    debug_log(f"✅ context-Datei erfolgreich unter generischem Namen gespeichert: {json_filename}")
                else:
                    debug_log(f"❌ Fehler beim Speichern der context-Datei unter generischem Namen: {json_filename}")
                    context.setdefault("upload_errors", []).append(f"Fehler beim Speichern der context-Datei unter generischem Namen: {json_filename}")
        except Exception as e:
            debug_log(f"❌ Fehler beim Speichern der context-Datei unter neuem Namen: {e}")
            context.setdefault("upload_errors", []).append(f"Fehler beim Speichern der context-Datei unter neuem Namen: {str(e)}")
        context["step"] = "context_saved"
        
        # 11. Lösche temporäre Dateien aus OneDrive
        try:
            temp_folder = "Temp"
            debug_log(f"🗑️ Lösche temporäre Dateien aus dem Temp-Ordner: {temp_folder}")
            for attachment in processed_attachments:
                try:
                    filename = attachment.get("filename")
                    if not filename:
                        debug_log(f"⚠️ Kein Dateiname gefunden für Anhang. Überspringe Löschen.")
                        context.setdefault("delete_errors", []).append(f"Kein Dateiname gefunden für Anhang.")
                        continue
                    await delete_file_from_onedrive(
                        access_token_onedrive=access_token_onedrive,
                        user_email=context.get("user_email"),
                        folder_path=temp_folder,
                        filename=filename,
                    )
                    debug_log(f"✅ Temporäre Datei erfolgreich gelöscht: {filename}")
                except Exception as e:
                    debug_log(f"❌ Fehler beim Löschen der temporären Datei: {filename} - {e}")
                    context.setdefault("delete_errors", []).append(f"Fehler beim Löschen der temporären Datei: {filename} - {str(e)}")
        except Exception as e:
            debug_log(f"❌ Fehler beim Löschen der temporären Dateien: {e}")
            context.setdefault("delete_errors", []).append(f"Fehler beim Löschen der temporären Dateien: {str(e)}")
        context["step"] = "temp_deleted"

    except Exception as e:
        debug_log(f"❌ Fehler im Hauptworkflow: {e}")
        context["workflow_errors"] = str(e)
        context["step"] = "error"

    return context