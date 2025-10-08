# Original src/main.py - Autarkes Email System
# Build y5DdGnNCDBoHfSqs7 - Backup vom 8. Oktober 2025

import sys
import os
import asyncio
import json
from apify import Actor
from modules.mail.process_email_workflow import process_email_workflow
from modules.utils.debug_log import debug_log
from modules.auth.get_graph_token_onedrive import get_graph_token_onedrive
from modules.auth.get_graph_token_mail import get_graph_token_mail
from modules.msgraph.download_attachment import download_attachments

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
            if not input_data:
                debug_log("❌ Keine Eingabedaten empfangen. Abbruch.")
                await Actor.exit(91)
                return

            # Fallback für Zapier-Webhook definieren
            debug_log("🔧 Fallback für Zapier-Webhook prüfen...")
            input_data["zapier_webhook"] = input_data.get("zapier_webhook") or ALERT_WEBHOOK_URL

            # Daten aus dem verschachtelten "data"-Feld extrahieren
            data = input_data.get("data", input_data)
            debug_log(f"📂 Extrahierte Daten: {json.dumps(data, indent=2)}")

            # Public Link erstellen
            context = {
                "public_link": data.get("public_link", ""),
                "step": "initialized"
            }

            # Zugriffstoken für Mail holen
            debug_log("📧 Versuche, Zugriffstoken für Mail abzurufen...")
            access_token_mail = get_graph_token_mail()
            if not access_token_mail:
                debug_log("❌ Zugriffstoken für Mail konnte nicht geholt werden. Abbruch.")
                await Actor.exit(91)
                return

            # Zugriffstoken für OneDrive holen
            debug_log("📂 Versuche, Zugriffstoken für OneDrive abzurufen...")
            access_token_onedrive = get_graph_token_onedrive()
            if not access_token_onedrive:
                debug_log("❌ Zugriffstoken für OneDrive konnte nicht geholt werden. Abbruch.")
                await Actor.exit(91)
                return

            # Haupt-Workflow starten
            debug_log(f"🔍 Starte Haupt-Workflow mit public_link={context['public_link']}")
            try:
                gpt_result = await process_email_workflow(
                    public_link=context["public_link"],
                    input_data=data,
                    access_token_mail=access_token_mail,
                    access_token_onedrive=access_token_onedrive,
                    context=context
                )

                # Ergebnisse an Apify senden
                if gpt_result:
                    debug_log("✅ Workflow erfolgreich abgeschlossen.")
                    await Actor.push_data(gpt_result)
                    
                    # Optional: Zapier Webhook aufrufen
                    zapier_webhook = data.get("zapier_webhook")
                    if zapier_webhook:
                        debug_log(f"🔗 Sende Ergebnis an Zapier: {zapier_webhook}")
                        # Webhook call implementation hier
                        
                else:
                    debug_log("⚠️ Workflow abgeschlossen, aber kein Ergebnis erhalten.")
                    
            except Exception as e:
                debug_log(f"❌ Fehler im Haupt-Workflow: {str(e)}")
                await Actor.exit(1)
                return

    except Exception as e:
        debug_log(f"❌ Kritischer Fehler in der Hauptlogik: {str(e)}")
        await Actor.exit(1)
        return

    debug_log("🏁 Mail-Actor abgeschlossen.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())