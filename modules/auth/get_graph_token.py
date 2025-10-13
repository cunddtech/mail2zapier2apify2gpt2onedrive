import os
import httpx
import sys

async def get_graph_token(source):
    """
    Holt das Zugriffstoken von Microsoft Graph für die angegebene Quelle.
    Gültige Quellen: "onedrive", "mail".
    """

    valid_sources = ["onedrive", "mail", "ONEDRIVE", "MAIL"]

    if source not in valid_sources:
        print(f"[FATAL] Ungültige Quelle für Token: {source} (erlaubt: {valid_sources})")
        sys.exit(1)

    tenant_id = os.getenv(f"GRAPH_TENANT_ID_{source.UPPER()}")
    client_id = os.getenv(f"GRAPH_CLIENT_ID_{source.UPPER()}")
    client_secret = os.getenv(f"GRAPH_CLIENT_SECRET_{source.UPPER()}")

    print(f"[DEBUG] [get_graph_token] Quelle: {source} | Tenant-ID: {tenant_id[:8]}..., Client-ID: {client_id[:8]}...")

    if not tenant_id or not client_id or not client_secret:
        print(f"[FATAL] Fehlende {source.capitalize()}-Graph API Zugangsdaten.")
        sys.exit(1)

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
            response = await client.post(url, headers=headers, data=data)
            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    print(f"[DEBUG] [get_graph_token] Token für {source} erfolgreich erhalten.")
                    return token
                else:
                    print(f"[ERROR] [get_graph_token] Token wurde nicht im Response gefunden.")
                    return None
            else:
                print(f"[ERROR] [get_graph_token] Tokenanforderung fehlgeschlagen: {response.status_code} {response.text}")
                return None
    except Exception as e:
        print(f"[ERROR] [get_graph_token] Fehler bei der Tokenanforderung: {str(e)}")
        return None