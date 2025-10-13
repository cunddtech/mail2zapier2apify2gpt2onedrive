from modules.utils.debug_log import debug_log
import aiohttp

async def download_attachment_as_bytes(user_email, message_id, attachment_id, access_token_mail) -> bytes:
    """Lädt ein Attachment herunter und gibt den Inhalt als Bytes zurück."""
    
    # Debugging-Logs für die Eingabeparameter
    #debug_log(f"📧 User Email: {user_email}")
    #debug_log(f"📨 Message ID: {message_id}")
    #debug_log(f"📎 Attachment ID: {attachment_id}")
    
    # URL und Header für die Anfrage
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}/attachments/{attachment_id}/$value"
    headers = {"Authorization": f"Bearer {access_token_mail}"}
    
    # Debugging-Log für die Anfrage-Details
    #debug_log(f"🌐 Download-Anfrage URL: {url}")
    #debug_log(f"🔑 Access Token (gekürzt): {access_token_mail[:8]}...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                debug_log(f"🌐 Antwortstatus: {response.status}")
                
                # Erfolgreiche Antwort
                if response.status == 200:
                    content = await response.read()
                    if not content:
                        debug_log(f"⚠️ Der heruntergeladene Anhang ist leer.")
                        raise ValueError("Der heruntergeladene Anhang ist leer.")
                    debug_log(f"✅ Anhang erfolgreich heruntergeladen: {len(content)} Bytes")
                    return content
                
                # Fehlerhafte Antwort
                else:
                    error_text = await response.text()
                    debug_log(f"❌ Fehler beim Herunterladen des Anhangs: {response.status} - {error_text}")
                    response.raise_for_status()

        except aiohttp.ClientError as e:
            # Ausnahmebehandlung und Debugging-Log
            debug_log(f"❌ Ausnahme beim Herunterladen des Anhangs: {str(e)}")
            raise e