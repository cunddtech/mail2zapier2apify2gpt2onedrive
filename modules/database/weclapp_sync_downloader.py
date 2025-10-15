"""
WeClapp Sync Database Downloader
Downloads the latest WEClapp sync database from OneDrive to Railway
"""
import os
import asyncio
import requests
from datetime import datetime
from modules.utils.debug_log import debug_log


async def download_weclapp_db_from_onedrive(
    access_token_onedrive: str,
    user_email: str = "mj@cdtechnologies.de",
    onedrive_path: str = "/Temp/weclapp_sync.db",
    local_path: str = "/tmp/weclapp_sync.db"
) -> str:
    """
    Downloads the WEClapp sync database from OneDrive
    
    Args:
        access_token_onedrive: OneDrive API token
        user_email: OneDrive user email
        onedrive_path: Path to DB file on OneDrive (try multiple locations)
        local_path: Where to save locally
        
    Returns:
        Local path to downloaded DB file, or None if failed
    """
    debug_log(f"📥 Downloading WEClapp DB from OneDrive...")
    debug_log(f"   OneDrive path: {onedrive_path}")
    debug_log(f"   Local path: {local_path}")
    
    # Try multiple possible OneDrive locations
    possible_paths = [
        "/Temp/weclapp_sync.db",
        "/scan/weclapp_sync.db", 
        "/Email/weclapp_sync.db",
        "/Temp/weclapp_data.db",
        "/scan/weclapp_data.db"
    ]
    
    for try_path in possible_paths:
        debug_log(f"🔍 Trying path: {try_path}")
        
        # Microsoft Graph API URL for file download
        download_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/root:{try_path}:/content"
        
        headers = {
            "Authorization": f"Bearer {access_token_onedrive}"
        }
        
        try:
            response = requests.get(download_url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                # Success! Save file locally
                file_bytes = response.content
                file_size_kb = len(file_bytes) / 1024
                
                debug_log(f"✅ Found DB file at {try_path} ({file_size_kb:.1f} KB)")
                
                # Save to local path
                with open(local_path, 'wb') as f:
                    f.write(file_bytes)
                
                debug_log(f"💾 Saved WEClapp DB to {local_path}")
                
                return local_path
            
            elif response.status_code == 404:
                debug_log(f"⚠️ Not found at {try_path}, trying next location...")
                continue
                
            else:
                debug_log(f"❌ Error {response.status_code}: {response.text[:200]}")
                continue
                    
        except Exception as e:
            debug_log(f"❌ Download error for {try_path}: {str(e)}")
            continue
    
    debug_log("❌ Could not find WEClapp DB at any expected location")
    return None


async def query_weclapp_contact(sender_email: str, db_path: str = "/tmp/weclapp_sync.db") -> dict:
    """
    Query WEClapp sync database for contact information
    
    Args:
        sender_email: Email address to lookup
        db_path: Path to WEClapp sync database
        
    Returns:
        Contact info dict or None if not found
    """
    if not os.path.exists(db_path):
        debug_log(f"⚠️ WEClapp DB not found at {db_path}")
        return None
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Try parties table first (customers/suppliers)
        cursor.execute("""
            SELECT id, name, email, phone, customerNumber, partyType, raw_data
            FROM parties 
            WHERE email = ? COLLATE NOCASE
        """, (sender_email,))
        
        row = cursor.fetchone()
        
        if row:
            debug_log(f"✅ Found contact in WEClapp DB: {row[1]} (Party ID: {row[0]})")
            
            conn.close()
            
            return {
                "party_id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "customer_number": row[4],
                "party_type": row[5],
                "raw_data": row[6],
                "source": "weclapp_sync_db"
            }
        
        # Try leads table
        cursor.execute("""
            SELECT id, firstName, lastName, email, phone, company, leadStatus, raw_data
            FROM leads
            WHERE email = ? COLLATE NOCASE
        """, (sender_email,))
        
        row = cursor.fetchone()
        
        if row:
            debug_log(f"✅ Found lead in WEClapp DB: {row[1]} {row[2]} (Lead ID: {row[0]})")
            
            conn.close()
            
            return {
                "lead_id": row[0],
                "name": f"{row[1]} {row[2]}",
                "email": row[3],
                "phone": row[4],
                "company": row[5],
                "lead_status": row[6],
                "raw_data": row[7],
                "source": "weclapp_sync_db"
            }
        
        conn.close()
        
        debug_log(f"⚠️ No contact found for {sender_email} in WEClapp DB")
        return None
        
    except Exception as e:
        debug_log(f"❌ WEClapp DB query error: {str(e)}")
        return None


async def get_weclapp_contact_cached(
    sender_email: str,
    access_token_onedrive: str = None,
    force_refresh: bool = False
) -> dict:
    """
    Get WEClapp contact info with caching
    Downloads DB from OneDrive if not cached or force_refresh=True
    
    Args:
        sender_email: Email to lookup
        access_token_onedrive: OneDrive token (required for download)
        force_refresh: Force re-download from OneDrive
        
    Returns:
        Contact info dict or None
    """
    local_db_path = "/tmp/weclapp_sync.db"
    
    # Check if we need to download
    needs_download = force_refresh or not os.path.exists(local_db_path)
    
    if needs_download and access_token_onedrive:
        debug_log("🔄 Refreshing WEClapp DB from OneDrive...")
        
        downloaded_path = await download_weclapp_db_from_onedrive(
            access_token_onedrive=access_token_onedrive,
            local_path=local_db_path
        )
        
        if not downloaded_path:
            debug_log("❌ Could not download WEClapp DB")
            return None
    
    # Query the database
    return await query_weclapp_contact(sender_email, local_db_path)


# For testing
async def test_downloader():
    """Test the downloader with environment credentials"""
    from modules.auth.get_graph_token_onedrive import get_graph_token_onedrive
    
    # Get OneDrive token
    access_token = await get_graph_token_onedrive()
    
    if not access_token:
        print("❌ Could not get OneDrive token")
        return
    
    # Try downloading
    db_path = await download_weclapp_db_from_onedrive(access_token)
    
    if db_path:
        print(f"✅ Downloaded to {db_path}")
        
        # List tables
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Tables in DB: {[t[0] for t in tables]}")
        
        # Count records
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   {table[0]}: {count} records")
        
        conn.close()


if __name__ == "__main__":
    asyncio.run(test_downloader())
