def fetch_email_details_with_attachments(message_id: str, user_email: str, token: str):
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{message_id}?$expand=attachments"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()