"""
Generate sharing links for OneDrive files using Microsoft Graph API
"""
import httpx
from modules.utils.debug_log import debug_log

async def generate_onedrive_sharing_link(
    user_email: str, 
    file_id: str, 
    access_token: str,
    link_type: str = "view",  # "view" or "edit"
    scope: str = "organization"  # "anonymous", "organization", or "users"
) -> dict:
    """
    Generiert einen Sharing Link für eine OneDrive-Datei
    
    Args:
        user_email: Email des Users (z.B. mj@cdtechnologies.de)
        file_id: Die OneDrive File ID (aus Upload Response)
        access_token: Graph API Access Token
        link_type: "view" (readonly) oder "edit"
        scope: "organization" (nur org), "anonymous" (öffentlich), "users" (specific users)
    
    Returns:
        dict: {"webUrl": "https://...", "link_id": "..."}
    """
    try:
        # Microsoft Graph API: Create Sharing Link
        # https://learn.microsoft.com/en-us/graph/api/driveitem-createlink
        url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{file_id}/createLink"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "type": link_type,  # "view" or "edit"
            "scope": scope      # "anonymous", "organization", "users"
        }
        
        debug_log(f"🔗 Creating sharing link for file: {file_id}")
        debug_log(f"   Type: {link_type}, Scope: {scope}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                data = response.json()
                sharing_link = data.get("link", {}).get("webUrl", "")
                link_id = data.get("id", "")
                
                debug_log(f"✅ Sharing link created: {sharing_link[:80]}...")
                
                return {
                    "webUrl": sharing_link,
                    "link_id": link_id,
                    "type": link_type,
                    "scope": scope
                }
            else:
                error_text = response.text if response.text else "No error message"
                debug_log(f"❌ Failed to create sharing link: {response.status_code}")
                debug_log(f"   Response: {error_text[:500]}")
                return {
                    "error": f"HTTP {response.status_code}",
                    "details": error_text[:500]
                }
                
    except Exception as e:
        debug_log(f"❌ Exception creating sharing link: {e}")
        return {
            "error": "Exception",
            "details": str(e)
        }
