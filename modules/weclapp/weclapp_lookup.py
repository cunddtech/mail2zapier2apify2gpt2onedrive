import os
import re
from typing import Iterable, Tuple

import requests

from modules.utils.debug_log import debug_log


def _extract_entities(data, entity_type="contact") -> Iterable:
    """Normalize WeClapp responses that vary between result/entities/list."""

    entities = None

    if isinstance(data, dict):
        if isinstance(data.get("result"), list):
            entities = data["result"]
        elif isinstance(data.get("result"), dict) and isinstance(data["result"].get("entities"), list):
            entities = data["result"].get("entities")
        elif isinstance(data.get("entities"), list):
            entities = data.get("entities")

    if entities is None and isinstance(data, list):
        entities = data

    entities = entities or []

    if entity_type == "contact":
        for contact in entities:
            if isinstance(contact, dict) and not contact.get("displayName"):
                first_name = (contact.get("firstName") or "").strip()
                last_name = (contact.get("lastName") or "").strip()
                company = (contact.get("personCompany") or "").strip()
                if first_name or last_name:
                    contact["displayName"] = f"{first_name} {last_name}".strip()
                elif company:
                    contact["displayName"] = company
                else:
                    contact["displayName"] = f"Kontakt #{contact.get('id', 'unknown')}"

    return entities


def _resolve_weclapp_credentials() -> Tuple[str, str]:
    """Return base URL (with trailing slash) and token from env."""

    base_url = os.getenv("WECLAPP_BASE_URL") or ""
    token = os.getenv("WECLAPP_API_TOKEN") or ""

    if base_url:
        base_url = f"{base_url.rstrip('/')}/"
    else:
        # Fall back to domain-based configuration if explicit base URL is missing.
        domain = (
            os.getenv("WECLAPP_DOMAIN")
            or os.getenv("WECLAPP_TENANT")
            or "cundd"
        )
        base_url = f"https://{domain}.weclapp.com/webapp/api/v1/"

    return base_url, token


def search_weclapp_entity(entity, search_term, page_size=5):
    """Allgemeine Suchfunktion für WeClapp-Entities (contact, customer, opportunity)."""

    base_url, token = _resolve_weclapp_credentials()
    if not token or not base_url:
        debug_log("❌ WeClapp API Token oder Base URL fehlen!")
        return []

    url = f"{base_url}{entity}"
    headers = {"AuthenticationToken": token}

    # Contacts need a smarter lookup because WeClapp ignores `term` on /contact.
    if entity == "contact" and search_term:
        default_params = {"term": search_term, "pageSize": page_size}
        try:
            debug_log(f"🔎 Suche {entity} | params={default_params} | base='{base_url}'")
            response = requests.get(url, headers=headers, params=default_params)
            response.raise_for_status()
            data = response.json()
            entities = list(_extract_entities(data, entity))
            if entities:
                debug_log(f"📬 WeClapp Antwort (term) | Treffer: {len(entities)}")
                return entities[:page_size]
        except Exception as exc:
            debug_log(f"⚠️ Standardsuche fehlgeschlagen ({entity}): {exc}")

        parts = [p.strip() for p in re.split(r'[\s,]+', search_term) if p.strip()]

        def _wild(value: str) -> str:
            # WeClapp expects asterisks for wildcard matches (per API docs).
            return f"*{value}*"

        if len(parts) >= 2:
            params_options = [
                {"lastName-like": _wild(parts[0]), "firstName-like": _wild(parts[1]), "pageSize": page_size},
                {"lastName-like": _wild(parts[1]), "firstName-like": _wild(parts[0]), "pageSize": page_size},
            ]
        elif len(parts) == 1:
            wildcard = _wild(parts[0])
            params_options = [
                {"lastName-like": wildcard, "pageSize": page_size},
                {"firstName-like": wildcard, "pageSize": page_size},
                {"personCompany-like": wildcard, "pageSize": page_size},
            ]
        else:
            params_options = [default_params]

        all_entities = []
        seen_ids = set()

        for params in params_options:
            debug_log(f"🔎 Suche {entity} | params={params} | base='{base_url}'")
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                entities = list(_extract_entities(data, entity))

                for contact in entities:
                    contact_id = contact.get("id") if isinstance(contact, dict) else None
                    if contact_id and contact_id not in seen_ids:
                        seen_ids.add(contact_id)
                        all_entities.append(contact)

                if len(all_entities) >= page_size:
                    break

            except Exception as exc:
                debug_log(f"⚠️ Teilsuche fehlgeschlagen: {exc}")
                continue

        debug_log(f"📬 WeClapp Combined Results | Treffer: {len(all_entities)} aus {len(params_options)} Queries")
        return all_entities[:page_size]

    params = {"term": search_term, "pageSize": page_size}

    try:
        debug_log(f"🔎 Suche {entity} mit Suchbegriff: '{search_term}'...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return list(_extract_entities(data, entity))
    except requests.exceptions.HTTPError as exc:
        resp = exc.response
        status_code = resp.status_code if resp is not None else "unknown"
        body_preview = resp.text[:200] if resp is not None and resp.text else ""
        debug_log(f"❌ Fehler bei WeClapp-Suche ({entity}): {status_code} - {body_preview}")
        return []
    except Exception as exc:  # pragma: no cover - defensive logging
        debug_log(f"❌ Fehler bei WeClapp-Suche ({entity}): {exc}")
        return []

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