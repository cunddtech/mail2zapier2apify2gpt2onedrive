import os

def build_driveitem_url(item_id: str) -> str:
    drive_id = os.getenv("DRIVE_ID")
    return f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"