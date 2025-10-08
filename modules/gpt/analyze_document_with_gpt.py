import os
import json
from typing import Dict, Any, Optional, Union

from modules.utils.debug_log import debug_log
from modules.gpt.prompts.gpt_prompt_modular import (
    build_precheck_prompt,
    build_classification_prompt,
    build_weclapp_phase_prompt,
    build_task_prompt
)
from modules.gpt.utils.validate import validate_payload, validate_gpt_response
from openai import AsyncOpenAI

aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MAX_PAYLOAD_SIZE = 20000  # Sicherheitsgrenze für Payload-Größe

async def analyze_document_with_gpt(payload: Dict[str, Any], timeout: int = 30) -> Optional[Dict[str, Any]]:
    if not payload or not isinstance(payload, dict):
        debug_log("[GPT] ❌ Ungültiger Payload")
        return {"error": "Ungültiger Payload"}

    payload = validate_payload(payload)
    #debug_log(f"[GPT] 📥 Eingabedaten validiert:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    # Robust alle möglichen Felder aus dem Payload abdecken
    invoice_data = (
        payload.get("invoice_data")
        or payload.get("invoice")
        or payload.get("header")
        or {}
    )
    vendor = (
        payload.get("vendor")
        or payload.get("vendor_data")
        or payload.get("company_information")
        or {}
    )
    customer = (
        payload.get("customer")
        or payload.get("customer_data")
        or payload.get("customer_information")
        or {}
    )
    payment_details = (
        payload.get("payment_details")
        or payload.get("paymentDetails")
        or {
            "totals": payload.get("totals", {}),
            "payment_terms": payload.get("payment_terms", {}),
            "order_details": payload.get("order_details", {}),
        }
    )
    billing_address = (
        payload.get("billing_address")
        or payload.get("billingAddress")
        or {}
    )
    shipping_address = (
        payload.get("shipping_address")
        or payload.get("shippingAddress")
        or {}
    )

    # Vor dem Payload-Size-Check:
    attachments = payload.get("attachments", [])
    for att in attachments:
        # Entferne große Binärdaten
        att.pop("file_bytes", None)
        att.pop("raw_pdf", None)
        att.pop("raw_image", None)
        # Optional: OCR-Text kürzen
        if "ocr_result" in att and "text" in att["ocr_result"]:
            att["ocr_result"]["text"] = att["ocr_result"]["text"][:10000]  # max 10.000 Zeichen
    
    payload["attachments"] = attachments

    payload_size = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    if payload_size > MAX_PAYLOAD_SIZE:
        debug_log(f"[GPT] ❌ Payload zu groß: {payload_size} Bytes")
        return {"error": "Payload zu groß", "size": payload_size}

    try:
        # === 1. Modul: Precheck
        precheck_prompt = build_precheck_prompt(
            body_text=payload.get("body_text", ""),
            metadata=payload.get("metadata", {}),
            attachments=payload.get("attachments", []),
            analysis_results={
                "ocr_text": " ".join([
                    att.get("ocr_result", {}).get("text", "") for att in payload.get("attachments", [])
                ]),
                "invoice_data": payload.get("invoice_data", {}),
                "customer": payload.get("customer", {}),
                "vendor": payload.get("vendor", {}),
                "payment_details": payload.get("payment_details", {}),
                "totals": {
                    "net_amount": payload.get("net_amount", ""),
                    "tax_amount": payload.get("tax_amount", ""),
                    "tax_rate": payload.get("tax_rate", ""),
                    "total_amount": payload.get("total_amount", "")
                },
                "billing_address": payload.get("billing_address", {}),
                "shipping_address": payload.get("shipping_address", {}),
                "order_reference": payload.get("order_reference", ""),
                "delivery_date": payload.get("delivery_date", ""),
                "payment_terms": payload.get("payment_terms", "")
            }
        )
        debug_log("[GPT] 🧪 Starte Vorprüfung (Precheck)...")
        precheck_response = await aclient.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[{"role": "user", "content": precheck_prompt}],
            temperature=0.2
        )
        precheck_data = json.loads(precheck_response.choices[0].message.content)
        debug_log(f"[GPT] ✅ Precheck Ergebnis:\n{json.dumps(precheck_data, indent=2, ensure_ascii=False)}")

        if not precheck_data.get("relevant", True):
            debug_log("[GPT] ⚠️ Mail als nicht relevant eingestuft. Analyse wird abgebrochen.")
            return {"relevant": False, "grund": precheck_data.get("grund", "Nicht angegeben")}

        payload["precheck_result"] = precheck_data

        # === 2. Modul: Klassifizierung
        ocr_text = " ".join([
            att.get("ocr_result", {}).get("text", "") for att in payload.get("attachments", [])
        ])

        classification_prompt = build_classification_prompt(
            body_text=payload.get("body_text", ""),
            metadata=payload.get("metadata", {}),
            attachments=payload.get("attachments", []),
            ocr_text=ocr_text,
            email_from=payload.get("email_from", "Unbekannt"),
            email_recipient=payload.get("email_recipient", "Unbekannt"),
            email_subject=payload.get("subject", "Kein Betreff"),
            parser_data={
                "invoice_data": payload.get("invoice_data", {}),
                "customer": payload.get("customer", {}),
                "vendor": payload.get("vendor", {}),
                "payment_details": payload.get("payment_details", {}),
                "totals": {
                    "net_amount": payload.get("net_amount", ""),
                    "tax_amount": payload.get("tax_amount", ""),
                    "tax_rate": payload.get("tax_rate", ""),
                    "total_amount": payload.get("total_amount", "")
                },
                "billing_address": payload.get("billing_address", {}),
                "shipping_address": payload.get("shipping_address", {}),
                "order_reference": payload.get("order_reference", ""),
                "delivery_date": payload.get("delivery_date", ""),
                "payment_terms": payload.get("payment_terms", "")
            }
        )
        debug_log("[GPT] 🧠 Starte Klassifizierung...")
        classification_response = await aclient.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[{"role": "user", "content": classification_prompt}],
            temperature=0.2
        )
        classification_data = json.loads(classification_response.choices[0].message.content)
        debug_log(f"[GPT] ✅ Klassifizierungs-Ergebnis:\n{json.dumps(classification_data, indent=2, ensure_ascii=False)}")

        payload["classification_result"] = classification_data

        # === 3. Modul: WeClapp-Phase
        rolle = classification_data.get("rolle", "").lower()
        weclapp_prompt = build_weclapp_phase_prompt(
            classification_data,
            parser_data={
                "invoice_data": payload.get("invoice_data", {}),
                "customer": payload.get("customer", {}),
                "vendor": payload.get("vendor", {}),
                "payment_details": payload.get("payment_details", {}),
                "totals": {
                    "net_amount": payload.get("net_amount", ""),
                    "tax_amount": payload.get("tax_amount", ""),
                    "tax_rate": payload.get("tax_rate", ""),
                    "total_amount": payload.get("total_amount", "")
                },
                "billing_address": payload.get("billing_address", {}),
                "shipping_address": payload.get("shipping_address", {}),
                "order_reference": payload.get("order_reference", ""),
                "delivery_date": payload.get("delivery_date", ""),
                "payment_terms": payload.get("payment_terms", "")
            }
        ) if rolle == "lieferant" else None

        if rolle == "lieferant":
            debug_log("[GPT] 🧩 Starte WeClapp-Phasen-Zuordnung...")
            weclapp_response = await aclient.chat.completions.create(
                model=os.getenv("GPT_MODEL", "gpt-4"),
                messages=[{"role": "user", "content": weclapp_prompt}],
                temperature=0.2
            )
            weclapp_data = json.loads(weclapp_response.choices[0].message.content)
            debug_log(f"[GPT] ✅ WeClapp Ergebnis:\n{json.dumps(weclapp_data, indent=2, ensure_ascii=False)}")
        else:
            weclapp_data = {
                "verkaufsphase": "nicht erforderlich",
                "begründung": f"Rolle ist '{rolle}', daher keine WeClapp-Phasen-Zuordnung erforderlich."
            }

        # === 4. Modul: Aufgabenprüfung
        task_prompt = build_task_prompt(
            classification_data,
            weclapp_data,
            parser_data={
                "invoice_data": payload.get("invoice_data", {}),
                "customer": payload.get("customer", {}),
                "vendor": payload.get("vendor", {}),
                "payment_details": payload.get("payment_details", {}),
                "totals": {
                    "net_amount": payload.get("net_amount", ""),
                    "tax_amount": payload.get("tax_amount", ""),
                    "tax_rate": payload.get("tax_rate", ""),
                    "total_amount": payload.get("total_amount", "")
                },
                "billing_address": payload.get("billing_address", {}),
                "shipping_address": payload.get("shipping_address", {}),
                "order_reference": payload.get("order_reference", ""),
                "delivery_date": payload.get("delivery_date", ""),
                "payment_terms": payload.get("payment_terms", "")
            }
        )
        debug_log("[GPT] 📝 Starte Aufgabenprüfung...")
        task_response = await aclient.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4"),
            messages=[{"role": "user", "content": task_prompt}],
            temperature=0.2
        )
        task_data = json.loads(task_response.choices[0].message.content)
        debug_log(f"[GPT] ✅ Aufgabenprüfung Ergebnis:\n{json.dumps(task_data, indent=2, ensure_ascii=False)}")

        # Ergebnis zusammenstellen
        result = {
            "relevant": True,
            **classification_data,
            "verkaufsphase": weclapp_data.get("verkaufsphase", "unbekannt"),
            "verkaufsphase_begründung": weclapp_data.get("begründung", ""),
            "precheck_result": precheck_data,
            "task": task_data.get("task", "Keine Aufgabe erforderlich"),
            "due_date": task_data.get("due_date", ""),
            "attachments": payload.get("attachments", []),
            "email": payload.get("email", {})
        }
                # ...vor return result...
        
        # Schreibe alle relevanten Ergebnisse in den Kontext, falls übergeben
        if "context" in payload and isinstance(payload["context"], dict):
            context = payload["context"]
            context["gpt_result"] = result
            context["classification_result"] = classification_data
            context["precheck_result"] = precheck_data
            context["weclapp_result"] = weclapp_data
            context["task_result"] = task_data
            # Optional: Schreibe alle Felder aus result in context["gpt_result_details"]
            context["gpt_result_details"] = result.copy()

        payload["gpt_result"] = result
        debug_log(f"[GPT] ✅ GPT-Ergebnis gespeichert:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
        return result

    except Exception as e:
        debug_log(f"[GPT] ❌ Fehler während der Analyse: {str(e)}")
        return {"error": str(e), "relevant": False}