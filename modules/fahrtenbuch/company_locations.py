"""
Company Locations - C&D Tech GmbH Standorte

Definiert eigene Firmen-Standorte die vom Matching ausgeschlossen werden sollen.
Diese Fahrten sind interne Fahrten (Lager, Firmensitz, Werkstatt).
"""

COMPANY_LOCATIONS = [
    {
        "name": "Firmensitz / Privat",
        "address": "Untertorstraße 1, 76767 Hagenbach",
        "city": "Hagenbach",
        "zipcode": "76767",
        "street_variants": ["Untertorstraße", "Untertorstrasse", "Untertorstr."],
        "type": "headquarters",
        "notes": "Firmensitz und Privatadresse MJ"
    },
    {
        "name": "Lager Wörth",
        "address": "Obere Weide 4, 76744 Wörth am Rhein",
        "city": "Wörth am Rhein",
        "zipcode": "76744",
        "street_variants": ["Obere Weide"],
        "type": "warehouse",
        "notes": "Aktuelles Lager"
    }
]

def is_company_location(destination_address: str) -> tuple[bool, str]:
    """
    Prüft ob Zieladresse ein Firmen-Standort ist
    
    Args:
        destination_address: "Untertorstraße, 76767 Hagenbach, Deutschland"
        
    Returns:
        (is_internal, location_name): (True, "Firmensitz / Privat") oder (False, None)
    """
    address_lower = destination_address.lower()
    
    for location in COMPANY_LOCATIONS:
        # Check zipcode + city
        if location['zipcode'] in destination_address and location['city'].lower() in address_lower:
            # Check street variants
            for street in location['street_variants']:
                if street.lower() in address_lower:
                    return True, location['name']
    
    return False, None

def get_customer_trips_only(trips: list) -> tuple[list, list]:
    """
    Filtert interne Fahrten aus
    
    Returns:
        (customer_trips, internal_trips): Zwei Listen
    """
    customer_trips = []
    internal_trips = []
    
    for trip in trips:
        destination = trip.get('destination_address', '')
        is_internal, location_name = is_company_location(destination)
        
        if is_internal:
            trip['internal_location'] = location_name
            internal_trips.append(trip)
        else:
            customer_trips.append(trip)
    
    return customer_trips, internal_trips

if __name__ == "__main__":
    # Test
    test_addresses = [
        "Untertorstraße, 76767 Hagenbach, Deutschland",
        "Obere Weide 4, 76744 Wörth am Rhein, Deutschland",
        "Landauer Straße 32, 76870 Kandel, Deutschland"
    ]
    
    for addr in test_addresses:
        is_internal, name = is_company_location(addr)
        print(f"{addr}")
        print(f"  → {'🏢 INTERN: ' + name if is_internal else '👤 KUNDE'}\n")
