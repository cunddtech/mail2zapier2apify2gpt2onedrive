"""
Generate OneDrive Sharing Links via Microsoft Graph API
"""
import httpx
from typing import Optional

async def generate_onedrive_sharing_link(
    user_email: str,
    file_id: str,
    access_token: str,
    link_type: str = "view",  # "view" or "edit"
    scope: str = "organization"  # "anonymous", "organization", or "users"
) -> Optional[str]:
    """
    Generates a sharing link for an OneDrive file using Microsoft Graph API.
    
    Args:
        user_email: Email of the OneDrive owner
        file_id: The ID of the file in OneDrive
        access_token: Microsoft Graph API access token
        link_type: "view" (read-only) or "edit"
        scope: "anonymous" (public), "organization" (internal), "users" (specific)
    
    Returns:
        The sharing link URL or None if failed
    """
    
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{file_id}/createLink"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "type": link_type,
        "scope": scope
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                data = response.json()
                share_link = data.get("link", {}).get("webUrl")
                
                if share_link:
                    return share_link
                else:
                    print(f"⚠️ No webUrl in response: {data}")
                    return None
            else:
                print(f"❌ Sharing link creation failed: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return None
                
    except Exception as e:
        print(f"❌ Exception creating sharing link: {e}")
        return None
