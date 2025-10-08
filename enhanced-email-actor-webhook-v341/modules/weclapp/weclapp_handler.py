from modules.weclapp.weclapp_lookup import (
    lookup_contact_priority,
    lookup_customer_priority,
    lookup_opportunity_priority
)
from modules.utils.debug_log import debug_log

def fetch_weclapp_data(email: str, customer_name: str) -> dict:
    """
    Ruft relevante WeClapp-Daten ab (Kontakt, Kunde, Opportunity).
    
    Args:
        email (str): Die E-Mail-Adresse des Absenders.
        customer_name (str): Der Name des Kunden.
    
    Returns:
        dict: WeClapp-Daten.
    """
    weclapp_info = {}

    # Kontakt abrufen
    contact_data = lookup_contact_priority(email=email, name=customer_name)
    if contact_data:
        weclapp_info["contactId"] = contact_data.get("id")
        debug_log(f"✅ Kontakt gefunden: {contact_data.get('displayName', 'Kein Name')}")

    # Kunde abrufen
    customer_data = lookup_customer_priority(name=customer_name)
    if customer_data:
        weclapp_info["customerId"] = customer_data.get("id")
        debug_log(f"✅ Kunde/Interessent gefunden: {customer_data.get('name', 'Kein Name')}")

    # Opportunity abrufen
    if weclapp_info.get("customerId"):
        opportunity_data = lookup_opportunity_priority(name=customer_name)
        if opportunity_data:
            weclapp_info["opportunityId"] = opportunity_data.get("id")
            weclapp_info["currentStage"] = opportunity_data.get("salesPhaseName", "unbekannt")
            debug_log(f"✅ Opportunity gefunden: {opportunity_data.get('title', 'Kein Titel')}")

    return weclapp_info