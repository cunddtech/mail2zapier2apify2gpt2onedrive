# Datei: modules/mail/determine_source.py

def determine_source(email: str):
    """
    Bestimmt, ob die Quelle 'mail' oder 'onedrive' ist basierend auf der E-Mail-Adresse.
    """
    if "@cd_mail" in email:
        return "mail"
    else:
        return "onedrive"