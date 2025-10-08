import requests
import os
import json
from modules.utils.debug_log import debug_log

PDFCO_API_KEY = os.getenv("PDFCO_API_KEY")

def ocr_pdfco_standard(pdf_url: str, context: dict = None, lang: str = "deu+eng") -> dict:
    """
    Klassifiziert ein PDF mit PDF.co und führt je nach Klasse eine angepasste Dokumentenextraktion durch.
    Schreibt die wichtigsten Parserdaten zusätzlich in den Kontext (falls übergeben).
    """
    if not PDFCO_API_KEY:
        raise ValueError("PDFCO_API_KEY fehlt in der Umgebung!")

    debug_log("📄 Starte Dokumentklassifikation und angepasste Extraktion bei PDF.co...")

    # URLs und Header für die Anfragen
    classifier_url = "https://api.pdf.co/v1/pdf/classifier"
    parser_url = "https://api.pdf.co/v1/pdf/documentparser"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": PDFCO_API_KEY
    }

    # Prüfen, ob eine öffentliche URL im Kontext verfügbar ist
    if context and "public_url" in context:
        pdf_url = context["public_url"]
        debug_log(f"🌐 Verwende vorhandene öffentliche URL: {pdf_url}")

    rulescsv = """Rechnung, OR, Rechnung, Betrag, USt-IdNr, Lieferdatum
Angebot, OR, Angebot, Angebotsnummer, Preis, Kunde
Auftrag, OR, Auftrag, Auftragsnummer, Kunde, Lieferdatum
Auftragsbestätigung, OR, Auftragsbestätigung, Auftragsnummer, Kunde, Lieferdatum
Bestellung, OR, Bestellung, Bestellnummer, Kunde, Lieferdatum
Gutschrift, OR, Gutschrift, Erstattung, Rückzahlung
Lieferschein, OR, Lieferschein, Lieferdatum, Artikelnummer
Leistungsnachweis, OR, Leistungsnachweis, Stunden, Projekt
Aufmaßblatt, OR, Aufmaßblatt, Maße, Einheit, Beschreibung
Behörde, OR, Arbeitsamt, Amt, Jobcenter, Behörde
Versicherung, OR, Versicherung, Police, Schadensnummer, Beitrag
Tankbeleg, OR, Tankstelle, Literpreis, Fahrzeug, Kraftstoff
Vertrag, OR, Vertragspartner, Laufzeit, Kündigungsfrist
Quittung, OR, Quittung, Betrag, Datum, Empfänger
Mahnung, OR, Mahnung, Rechnungsnummer, Betrag, Fälligkeitsdatum
"""

    # Payload für die Klassifikation
    classifier_payload = {
        "url": pdf_url,
        "inline": True,
        "rulescsv": rulescsv
    }

    try:
        # 1. Dokumentklassifikation
        debug_log("📋 Starte Dokumentklassifikation...")
        classifier_response = requests.post(classifier_url, headers=headers, json=classifier_payload)

        if classifier_response.status_code == 200:
            classifier_result = classifier_response.json()
            document_classes = classifier_result.get("body", {}).get("classes", [])
            debug_log(f"✅ Dokumentklassifikation abgeschlossen: {document_classes}")
            debug_log(f"🔎 Vollständige Klassifikations-Response: {json.dumps(classifier_result, indent=2, ensure_ascii=False)}")

            # Prüfen, ob eine Klasse erkannt wurde
            if not document_classes:
                debug_log("⚠️ Keine Dokumentklasse erkannt. Abbruch.")
                return {
                    "document_classes": [],
                    "error": "Keine Dokumentklasse erkannt"
                }

            # 2. Angepasste Dokumentenextraktion basierend auf der Klasse
            primary_class = document_classes[0].get("class", "").strip().lower()  # Bereinigung der Klasse
            debug_log(f"📂 Primäre Dokumentklasse: {primary_class}")

            # Mapping von Klassen zu numerischen Template-IDs
            template_mapping = {
                "rechnung": 14220,  # Novoferm_AB
                "allgemein": 14221,  # Allgemeine schreiben
                "tankbeleg": 234567,  # Beispiel: Numerische ID für Tankbeleg
                "vertrag": 345678,  # Beispiel: Numerische ID für Vertrag
                "gutschrift": 456789,  # Beispiel: Numerische ID für Gutschrift
                "lieferschein": 567890,  # Beispiel: Numerische ID für Lieferschein
                "leistungsnachweis": 678901,  # Beispiel: Numerische ID für Leistungsnachweis
                "aufmaßblatt": 789012,  # Beispiel: Numerische ID für Aufmaßblatt
                "behörde": 890123,  # Beispiel: Numerische ID für Behörde
                "versicherung": 901234  # Beispiel: Numerische ID für Versicherung
            }

            template_id = template_mapping.get(primary_class)

            # Vorläufig: Überschreibe template_id mit allgemeinem Template
            debug_log(f"📂 Vorläufige Verarbeitung mit allgemeinem Template-ID: 14221")
            template_id = 14221  # Allgemeine schreiben

            # Payload für die Dokumentenextraktion
            parser_payload = {
                "url": pdf_url,
                "templateId": template_id
            }

            debug_log(f"📄 Starte Dokumentenextraktion mit Template '{template_id}'...")
            parser_response = requests.post(parser_url, headers=headers, json=parser_payload)

            if parser_response.status_code == 200:
                parser_result = parser_response.json()
                debug_log(f"✅ Dokumentenextraktion erfolgreich: {parser_result}")
                body = parser_result.get("body", {})

                # Fallbacks für verschiedene mögliche Feldnamen (Standard/Invoice-Parser)
                invoice_data = (
                    body.get("header") or
                    body.get("invoice") or
                    {}
                )
                vendor = (
                    body.get("company_information") or
                    body.get("vendor") or
                    {}
                )
                customer = (
                    body.get("customer_information") or
                    body.get("customer") or
                    {}
                )
                payment_details = (
                    body.get("payment_details") or
                    body.get("paymentDetails") or
                    {}
                )
                billing_address = (
                    body.get("billing_address") or
                    body.get("billingAddress") or
                    {}
                )
                shipping_address = (
                    body.get("shipping_address") or
                    body.get("shippingAddress") or
                    {}
                )

                # Falls payment_details leer ist, aus Einzelteilen zusammensetzen (Standard-Parser)
                if not payment_details:
                    payment_details = {
                        "totals": body.get("totals", {}),
                        "payment_terms": body.get("payment_terms", {}),
                        "order_details": body.get("order_details", {}),
                    }
                
                # >>> Kontext befüllen: Schreibe ALLE Felder aus body in context["pdf_processing"] <<<
                if context is not None and isinstance(context, dict):
                    context["pdf_processing"] = context.get("pdf_processing", {})
                    # Schreibe alle Felder aus body in den Kontext
                    for key, value in body.items():
                        context["pdf_processing"][key] = value
                    # Zusätzlich die wichtigsten Fallbacks für Kompatibilität
                    context["pdf_processing"]["invoice_data"] = body.get("header") or body.get("invoice") or {}
                    context["pdf_processing"]["vendor"] = body.get("company_information") or body.get("vendor") or {}
                    context["pdf_processing"]["customer"] = body.get("customer_information") or body.get("customer") or {}
                    context["pdf_processing"]["payment_details"] = (
                        body.get("payment_details") or
                        body.get("paymentDetails") or
                        {
                            "totals": body.get("totals", {}),
                            "payment_terms": body.get("payment_terms", {}),
                            "order_details": body.get("order_details", {}),
                        }
                    )
                    context["pdf_processing"]["billing_address"] = body.get("billing_address") or body.get("billingAddress") or {}
                    context["pdf_processing"]["shipping_address"] = body.get("shipping_address") or body.get("shippingAddress") or {}
                
                return {
                    "document_classes": document_classes,
                    "primary_class": primary_class,
                    "invoice_data": invoice_data,
                    "vendor": vendor,
                    "customer": customer,
                    "payment_details": payment_details,
                    "billing_address": billing_address,
                    "shipping_address": shipping_address,
                    "parsed_data": parser_result,
                    "raw_classifier_response": classifier_result,
                    "raw_parser_response": parser_result
                }
            else:
                debug_log(f"⚠️ Dokumentenextraktion fehlgeschlagen ({parser_response.status_code}): {parser_response.text}")
                return {
                    "document_classes": document_classes,
                    "error": parser_response.text,
                    "raw_classifier_response": classifier_result
                }

        else:
            debug_log(f"⚠️ Dokumentklassifikation fehlgeschlagen ({classifier_response.status_code}): {classifier_response.text}")
            return {
                "error": classifier_response.text
            }

    except Exception as e:
        debug_log(f"⚠️ Fehler bei der Klassifikation oder Extraktion: {e}")
        return {
            "error": str(e)
        }