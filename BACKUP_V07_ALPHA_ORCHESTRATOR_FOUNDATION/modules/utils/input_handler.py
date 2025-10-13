import os
import json
import time
from modules.utils.debug_log import debug_log

# Webhook für Notfall-Alarm
ALERT_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

def process_input_data(input_data):
    """
    Verarbeitet die Eingabedaten und fügt zusätzliche Felder hinzu.
    """
    if not input_data:
        debug_log("❌ Keine Eingabedaten empfangen.")
        return None

    # Fallback für Zapier-Webhook definieren
    input_data["zapier_webhook"] = input_data.get("zapier_webhook") or ALERT_WEBHOOK_URL

    # Zusätzliche Felder hinzufügen
    input_data["processed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())  # Zeitstempel
    input_data["actor_run_id"] = os.getenv("APIFY_ACTOR_RUN_ID", "unknown")  # Actor-Run-ID
    input_data["status"] = "pending"  # Initialer Status

    debug_log(f"📥 Eingabedaten erweitert: {json.dumps(input_data, indent=2, ensure_ascii=False)}")
    return input_data

def validate_input_data(input_data):
    """
    Validiert die Eingabedaten und prüft auf erforderliche Felder.
    """
    user_email = input_data.get("user_email")
    message_id = input_data.get("message_id")

    if not user_email or not message_id:
        debug_log("❌ user_email oder message_id fehlen.")
        return False

    return True