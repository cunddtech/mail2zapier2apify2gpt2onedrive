import requests
from modules.utils.debug_log import debug_log

def post_to_zapier_webhook(data, zapier_webhook_url):
    """
    Sendet die Daten an den Zapier-Webhook.
    
    Args:
        data (dict): Die zu sendenden Daten.
        zapier_webhook_url (str): Die URL des Zapier-Webhooks.
    """
    if not zapier_webhook_url:
        debug_log("❌ Fehler: Zapier-Webhook-URL fehlt.")
        return

    try:
        response = requests.post(zapier_webhook_url, json=data)
        if response.status_code == 200:
            debug_log("✅ Daten erfolgreich an Zapier gesendet.")
        else:
            debug_log(f"❌ Fehler beim Senden der Daten an Zapier: {response.status_code} - {response.text}")
    except Exception as e:
        debug_log(f"❌ Fehler beim Verbinden mit dem Zapier-Webhook: {e}")