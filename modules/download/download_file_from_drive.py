from modules.utils.debug_log import debug_log
from modules.msgraph.generate_public_link import generate_public_link
import requests

async def download_attachment_as_bytes(user_email, message_id, attachment_id, access_token_mail) -> bytes:
    """
    Lädt ein Attachment herunter und gibt den Inhalt als Bytes zurück.
    Nutzt `generate_public_link`, um die URL zu erstellen.
    """
    
    # Debugging-Logs für die Eingabeparameter
    debug_log(f"📧 User Email: {user_email}")
    debug_log(f"📨 Message ID: {message_id}")
    debug_log(f"📎 Attachment ID: {attachment_id}")
    
    # Generiere die öffentliche URL für den Anhang
    #debug_log("🌐 Generiere öffentliche URL für den Anhang...")
    public_link = await generate_public_link(user_email, message_id, attachment_id, access_token_mail)
    if not public_link:
        debug_log("❌ Fehler beim Generieren der öffentlichen URL.")
        raise Exception("Öffentliche URL konnte nicht generiert werden.")
    
    #debug_log(f"🌐 Öffentliche URL generiert: {public_link}")

    try:
        # Anfrage an die öffentliche URL
        debug_log(f"⬇️ Lade Anhang von der öffentlichen URL herunter...")
        response = requests.get(public_link)
        #debug_log(f"🌐 Antwortstatus: {response.status_code}")
        
        # Erfolgreiche Antwort
        if response.status_code == 200:
            debug_log(f"✅ Anhang erfolgreich heruntergeladen: {len(response.content)} Bytes")
            return response.content
        
        # Fehlerhafte Antwort
        else:
            debug_log(f"❌ Fehler beim Herunterladen des Anhangs: {response.status_code} - {response.text}")
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        # Ausnahmebehandlung und Debugging-Log
        debug_log(f"❌ Ausnahme beim Herunterladen des Anhangs: {str(e)}")
        raise e