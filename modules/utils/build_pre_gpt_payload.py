import json

def build_pre_gpt_payload(email_from, subject, body_text, attachments, weclapp_info=None):
    """
    Erstellt den Payload für die Vorvalidierung mit GPT.

    :param email_from: Absender der E-Mail.
    :param subject: Betreff der E-Mail.
    :param body_text: Inhalt der E-Mail.
    :param attachments: Liste der Anhänge.
    :param weclapp_info: (Optional) WeClapp-Daten.
    :return: Dictionary mit den Daten für die Vorvalidierung.
    """
    if weclapp_info is None:
        weclapp_info = {}
    return {
        "email_from": email_from,
        "subject": subject,
        "body_text": body_text,
        "attachments": attachments,
        "weclapp_info": weclapp_info
    }