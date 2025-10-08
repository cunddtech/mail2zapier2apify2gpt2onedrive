import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import json
import requests
from apify import Actor
from modules.mail.process_email_workflow import process_email_workflow
from modules.utils.debug_log import debug_log
from modules.auth.get_graph_token_onedrive import get_graph_token_onedrive
from modules.auth.get_graph_token_mail import get_graph_token_mail

# Webhook für Notfall-Alarm
ALERT_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

async def main():
    try:
        debug_log("🚀 Starte die Anwendung...")
        async with Actor:
            debug_log("✅ Actor erfolgreich initialisiert.")

            # Eingabedaten abrufen
            debug_log("📥 Versuche, Eingabedaten abzurufen...")
            input_data = await Actor.get_input()
            debug_log(f"📥 Eingabedaten: {json.dumps(input_data, indent=2)}")
            if not input_data:
                debug_log("❌ Keine Eingabedaten empfangen. Abbruch.")
                await Actor.exit(91)
                return

            # Fallback für Zapier-Webhook definieren
            debug_log("🔧 Fallback für Zapier-Webhook prüfen...")
            input_data["zapier_webhook"] = input_data.get("zapier_webhook") or ALERT_WEBHOOK_URL

            # Validierung der neuen Input-Felder
            debug_log("🔍 Überprüfe erforderliche Felder...")
            required_fields = ["payload_type", "wrap_in_array", "unflatten", "url", "data"]
            for field in required_fields:
                if field not in input_data:
                    debug_log(f"❌ Fehlendes erforderliches Feld: {field}. Abbruch.")
                    await Actor.exit(91)
                    return

            # Daten aus dem verschachtelten "data"-Feld extrahieren
            #debug_log("📋 Extrahiere Daten aus 'data'-Feld...")
            data = input_data.get("data", {})
            #debug_log(f"📋 Daten aus 'data'-Feld: {json.dumps(data, indent=2)}")

            # Kontext initialisieren
            debug_log("🔧 Initialisiere Kontext...")
            context = {
                "source": input_data.get("source", "mail"),
                "public_link": input_data.get("url", ""),
                "body_content": data.get("body_content", ""),
                "body_preview": data.get("body_preview", ""),
                "subject": data.get("subject", "kein Betreff"),
                "from_email_address_name": data.get("from_email_address_name", "unbekannt"),
                "from_email_address_address": data.get("from_email_address_address", "unbekannt"),
                "to_recipients_email_address_address": data.get("to_recipients_email_address_address", "unbekannt"),
                "to_recipients_email_address_name": data.get("to_recipients_email_address_name", "unbekannt"),
                "received_date_time": data.get("received_date_time", "unbekannt"),
                "attachments": data.get("attachments", []),
                "zapier_webhook": input_data.get("zapier_webhook", ""),
                "trigger": input_data.get("trigger", "unknown"),
            }
            #debug_log(f"📋 Initialisierter Kontext: {json.dumps(context, indent=2, ensure_ascii=False)}")

            # Zugriffstoken für Mail holen
            #debug_log("📧 Versuche, Zugriffstoken für Mail zu holen...")
            access_token_mail = await get_graph_token_mail()
            #debug_log(f"📧 Zugriffstoken für Mail: {'Erfolgreich' if access_token_mail else 'Fehlgeschlagen'}")
            if not access_token_mail:
                debug_log("❌ Zugriffstoken für Mail konnte nicht geholt werden. Abbruch.")
                await Actor.exit(91)
                return

            # Zugriffstoken für OneDrive holen
            #debug_log("📂 Versuche, Zugriffstoken für OneDrive zu holen...")
            access_token_onedrive = await get_graph_token_onedrive()
            #debug_log(f"📂 Zugriffstoken für OneDrive: {'Erfolgreich' if access_token_onedrive else 'Fehlgeschlagen'}")
            if not access_token_onedrive:
                debug_log("❌ Zugriffstoken für OneDrive konnte nicht geholt werden. Abbruch.")
                await Actor.exit(91)
                return

            # Haupt-Workflow starten
            debug_log(f"🔍 Starte Haupt-Workflow mit public_link={context['public_link']}, input_data={json.dumps(data, indent=2)}")
            try:
                gpt_result = await process_email_workflow(
                    public_link=context["public_link"],
                    input_data=data,
                    access_token_mail=access_token_mail,
                    access_token_onedrive=access_token_onedrive,
                    context=context
                )

                # Finales Ergebnis aus der GPT-Analyse loggen
                debug_log("📊 **Finale Ergebnisse der GPT-Analyse:**")
                debug_log(f"  - **Rolle:** {'Kunde' if gpt_result.get('relevant') == 'True' else 'Lieferant'}")
                debug_log(f"  - **E-Mail:** {gpt_result.get('email_from', 'Unbekannt')}")
                debug_log(f"  - **Betreff:** {gpt_result.get('subject', 'Kein Betreff')}")
                debug_log(f"  - **Datum:** {gpt_result.get('date', 'Unbekannt')}")
                debug_log(f"  - **Anzahl Anhänge:** {gpt_result.get('attachments_count', 0)}")
                debug_log(f"  - **Dateien:** {[attachment.get('filename') for attachment in gpt_result.get('attachments', [])]}")
                debug_log(f"  - **Ablage-URL:** {[attachment.get('url') for attachment in gpt_result.get('attachments', [])]}")
                debug_log(f"  - **Relevanz:** {'Ja' if gpt_result.get('relevant') == 'True' else 'Nein'}")
                debug_log(f"  - **WeClapp-Daten:** {gpt_result.get('weclapp_data', {})}")

            except Exception as e:
                debug_log(f"❌ Fehler in der Hauptlogik: {e}")
                await Actor.exit(1)
                return

        debug_log("🏁 Mail-Actor abgeschlossen.")
    except Exception as e:
        debug_log(f"❌ Unerwarteter Fehler: {str(e)}")
        raise