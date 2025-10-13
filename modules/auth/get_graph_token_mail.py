import os
import httpx
from modules.utils.debug_log import debug_log

async def get_graph_token_mail():
    """
    Holt das Zugriffstoken von Microsoft Graph für Mail.
    """
    tenant_id = os.getenv("GRAPH_TENANT_ID_MAIL")
    client_id = os.getenv("GRAPH_CLIENT_ID_MAIL")
    client_secret = os.getenv("GRAPH_CLIENT_SECRET_MAIL")

    if not tenant_id or not client_id or not client_secret:
        debug_log("[FATAL] Fehlende Mail-Graph API Zugangsdaten.")
        return None

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }

    try:
        async with httpx.AsyncClient() as client:
            #debug_log(f"[DEBUG] Fordere Token für Mail an...")
            response = await client.post(url, headers=headers, data=data)
            if response.status_code == 200:
                token = response.json().get("access_token")
                #debug_log(f"[DEBUG] Zugriffstoken für Mail erfolgreich erhalten.")
                return token
            else:
                debug_log(f"[ERROR] Fehler bei der Tokenanforderung für Mail: {response.status_code} {response.text}")
                return None
    except Exception as e:
        debug_log(f"[ERROR] Fehler bei der Tokenanforderung für Mail: {str(e)}")
        return None