def fetch_latest_message_id(user_email: str, token: str) -> str:
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages?$top=1"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    items = r.json().get("value", [])
    return items[0]["id"] if items else ""