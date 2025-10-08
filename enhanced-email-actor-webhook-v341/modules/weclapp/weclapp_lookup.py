import requests
import os
from modules.utils.debug_log import debug_log

WECLAPP_API_TOKEN = os.getenv("WECLAPP_API_TOKEN")
WECLAPP_BASE_URL = os.getenv("WECLAPP_BASE_URL")

def search_weclapp_entity(entity, search_term, page_size=5):
    """
    Allgemeine Suchfunktion für WeClapp-Entities (contact, customer, opportunity).
    """
    if not WECLAPP_API_TOKEN or not WECLAPP_BASE_URL:
        debug_log("❌ WeClapp API Token oder Base URL fehlen!")
        return None

    url = f"{WECLAPP_BASE_URL}{entity}"
    headers = {
        "AuthenticationToken": WECLAPP_API_TOKEN
    }
    params = {
        "term": search_term,
        "pageSize": page_size
    }

    try:
        debug_log(f"🔎 Suche {entity} mit Suchbegriff: '{search_term}'...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("entities", [])

    except Exception as e:
        debug_log(f"❌ Fehler bei WeClapp-Suche ({entity}): {e}")
        return None

def lookup_contact_priority(email=None, telefon=None, adresse=None, name=None):
    """
    Sucht einen Kontakt in WeClapp:
    Priorität: Email → Telefon → Adresse → Name
    """
    fields = [("email", email), ("telefon", telefon), ("adresse", adresse), ("name", name)]
    for field, value in fields:
        if value:
            contacts = search_weclapp_entity("contact", value)
            if contacts:
                for contact in contacts:
                    if field == "email" and value.lower() in (contact.get("emailAddress", "") or "").lower():
                        debug_log(f"✅ Treffer bei Email: {contact.get('emailAddress')}")
                        return contact
                    if field == "telefon" and value.replace(" ", "") in (contact.get("phone", "") or "").replace(" ", ""):
                        debug_log(f"✅ Treffer bei Telefon: {contact.get('phone')}")
                        return contact
                    if field == "adresse" and value.lower() in (contact.get("address", {}).get("street", "") or "").lower():
                        debug_log(f"✅ Treffer bei Adresse: {contact.get('address', {}).get('street')}")
                        return contact
                    if field == "name" and value.lower() in (contact.get("displayName", "") or "").lower():
                        debug_log(f"✅ Treffer bei Name: {contact.get('displayName')}")
                        return contact
    debug_log("❌ Kein Kontakt gefunden.")
    return None

def lookup_customer_priority(name):
    """
    Sucht einen Kunden oder Interessenten in WeClapp.
    """
    customers = search_weclapp_entity("customer", name)
    if customers:
        debug_log(f"✅ Kunde/Interessent gefunden: {customers[0].get('name')}")
        return customers[0]
    debug_log("❌ Kein Kunde/Interessent gefunden.")
    return None

def lookup_opportunity_priority(name):
    """
    Sucht eine Verkaufschance (Opportunity) in WeClapp.
    """
    opportunities = search_weclapp_entity("opportunity", name)
    if opportunities:
        debug_log(f"✅ Verkaufschance gefunden: {opportunities[0].get('title')}")
        return opportunities[0]
    debug_log("❌ Keine Verkaufschance gefunden.")
    return None