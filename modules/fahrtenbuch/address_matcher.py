"""
Address Matcher - Fahrtenadressen mit WeClapp CRM abgleichen

Matching-Strategien:
1. Exact Match: PLZ + Stadt + Straße (100%)
2. Fuzzy Match: Levenshtein Distance auf Adresse (70-95%)
3. GPS Match: Koordinaten-Radius <500m (80-100%)
"""

import os
import requests
import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
import logging
import math

logger = logging.getLogger(__name__)

class AddressMatcher:
    """Matcher für Fahrtenadressen gegen WeClapp CRM"""
    
    def __init__(self):
        """Initialize WeClapp API credentials"""
        self.api_token = os.getenv("WECLAPP_API_TOKEN")
        self.base_url = os.getenv("WECLAPP_BASE_URL")
        
        if not self.api_token or not self.base_url:
            raise ValueError("WeClapp credentials missing! Set WECLAPP_API_TOKEN and WECLAPP_BASE_URL")
    
    def parse_german_address(self, address: str) -> Dict[str, str]:
        """
        Parse deutsche Adresse in Komponenten
        
        Args:
            address: "Landauer Straße 32, 76870 Kandel, Deutschland"
            
        Returns:
            {
                "street": "Landauer Straße",
                "house_number": "32",
                "zipcode": "76870",
                "city": "Kandel",
                "country": "Deutschland"
            }
        """
        parts = {}
        
        # Remove country
        address_clean = address.replace(", Deutschland", "").strip()
        
        # PLZ + Stadt pattern: "76870 Kandel"
        zipcode_match = re.search(r'\b(\d{5})\s+([A-Za-zäöüÄÖÜß\s-]+)$', address_clean)
        if zipcode_match:
            parts['zipcode'] = zipcode_match.group(1)
            parts['city'] = zipcode_match.group(2).strip()
            
            # Street + number: everything before PLZ
            street_part = address_clean[:zipcode_match.start()].strip().rstrip(',')
            
            # Extract house number
            number_match = re.search(r'\s+(\d+[a-zA-Z]?)\s*$', street_part)
            if number_match:
                parts['house_number'] = number_match.group(1)
                parts['street'] = street_part[:number_match.start()].strip()
            else:
                parts['street'] = street_part
        
        parts['country'] = 'Deutschland'
        return parts
    
    def calculate_gps_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Berechne Distanz zwischen zwei GPS-Koordinaten (Haversine)
        
        Returns:
            Distanz in Metern
        """
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def fuzzy_match_score(self, str1: str, str2: str) -> float:
        """
        Fuzzy string matching score (0-100%)
        
        Uses SequenceMatcher for similarity
        """
        if not str1 or not str2:
            return 0.0
        
        # Normalize: lowercase, remove extra spaces
        s1 = ' '.join(str1.lower().split())
        s2 = ' '.join(str2.lower().split())
        
        return SequenceMatcher(None, s1, s2).ratio() * 100
    
    def search_weclapp_customers(self, search_term: str) -> List[Dict]:
        """
        Suche Kunden in WeClapp
        
        Args:
            search_term: Stadt, PLZ, oder Straße
            
        Returns:
            Liste von Kunden-Dicts
        """
        url = f"{self.base_url}customer"
        headers = {"AuthenticationToken": self.api_token}
        params = {"term": search_term, "pageSize": 20}
        
        try:
            logger.info(f"🔎 WeClapp Suche: '{search_term}'")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            customers = data.get("result", [])
            logger.info(f"✅ Gefunden: {len(customers)} Kunden")
            return customers
        
        except Exception as e:
            logger.error(f"❌ WeClapp API Error: {e}")
            return []
    
    def match_address(
        self, 
        destination_address: str,
        destination_lat: Optional[float] = None,
        destination_lon: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Match Fahrten-Adresse gegen WeClapp CRM
        
        Args:
            destination_address: "Landauer Straße 32, 76870 Kandel, Deutschland"
            destination_lat: GPS Latitude (optional)
            destination_lon: GPS Longitude (optional)
            
        Returns:
            {
                "customer_id": "12345",
                "customer_name": "Mustermann GmbH",
                "match_confidence": 95,
                "match_type": "exact_address",
                "customer_address": "Landauer Str. 32, 76870 Kandel"
            }
        """
        # Parse address
        parsed = self.parse_german_address(destination_address)
        if not parsed.get('city'):
            logger.warning(f"⚠️ Konnte Adresse nicht parsen: {destination_address}")
            return None
        
        logger.info(f"🏠 Matching: {parsed.get('street', '')} {parsed.get('house_number', '')}, {parsed.get('zipcode', '')} {parsed.get('city', '')}")
        
        # Search WeClapp by city
        city = parsed.get('city', '')
        customers = self.search_weclapp_customers(city)
        
        if not customers:
            # Try zipcode
            zipcode = parsed.get('zipcode', '')
            if zipcode:
                customers = self.search_weclapp_customers(zipcode)
        
        if not customers:
            logger.info("❌ Keine Kunden gefunden")
            return None
        
        # Find best match
        best_match = None
        best_score = 0
        
        for customer in customers:
            # Get customer addresses (embedded in customer object)
            addresses = customer.get('addresses', [])
            if not addresses:
                continue
            
            # Check each address
            for addr in addresses:
                addr_line1 = addr.get('street1', '')
                addr_city = addr.get('city', '')
                addr_zipcode = addr.get('zipcode', '')
                
                # Build full address for comparison
                customer_address = f"{addr_line1}, {addr_zipcode} {addr_city}"
                
                # Scoring
                score = 0
                match_type = ""
                
                # 1. Exact PLZ + Stadt match (40 points)
                if parsed.get('zipcode') == addr_zipcode and parsed.get('city', '').lower() == addr_city.lower():
                    score += 40
                    match_type = "zipcode_city"
                
                # 2. Street fuzzy match (40 points)
                if parsed.get('street'):
                    street_score = self.fuzzy_match_score(parsed['street'], addr_line1)
                    score += (street_score / 100) * 40
                    
                    if street_score > 80:
                        match_type = "exact_address"
                
                # 3. GPS distance (20 points)
                if destination_lat and destination_lon:
                    cust_lat = addr.get('latitude')
                    cust_lon = addr.get('longitude')
                    
                    if cust_lat and cust_lon:
                        distance = self.calculate_gps_distance(
                            destination_lat, destination_lon,
                            float(cust_lat), float(cust_lon)
                        )
                        
                        if distance < 500:  # <500m = good match
                            score += 20 * (1 - distance / 500)
                            match_type = "gps_radius"
                
                # Update best match
                if score > best_score and score >= 50:  # Minimum 50% confidence
                    best_score = score
                    
                    # Get customer name: company -> contact name -> customer number -> address
                    customer_name = customer.get('company', '').strip()
                    if not customer_name:
                        # Try contact name
                        contacts = customer.get('contacts', [])
                        if contacts:
                            contact = contacts[0]
                            first_name = contact.get('firstName', '')
                            last_name = contact.get('lastName', '')
                            customer_name = f"{first_name} {last_name}".strip()
                    
                    if not customer_name:
                        # Use customer number as fallback
                        customer_name = f"Kunde #{customer.get('customerNumber', customer.get('id'))}"
                    
                    best_match = {
                        "customer_id": customer.get('id'),
                        "customer_name": customer_name,
                        "match_confidence": int(score),
                        "match_type": match_type,
                        "customer_address": customer_address.strip()
                    }
        
        if best_match:
            logger.info(f"✅ Match: {best_match['customer_name']} ({best_match['match_confidence']}%)")
        else:
            logger.info("❌ Kein Match über 50% Confidence")
        
        return best_match
    
    def match_all_trips(self, trips: List[Dict]) -> Dict[str, int]:
        """
        Match alle Fahrten gegen WeClapp CRM
        
        Args:
            trips: Liste von trip dicts mit destination_address, lat, lon
            
        Returns:
            {"matched": 10, "unmatched": 13}
        """
        stats = {"matched": 0, "unmatched": 0}
        
        for trip in trips:
            trip_id = trip.get('id')
            address = trip.get('destination_address')
            lat = trip.get('destination_latitude')
            lon = trip.get('destination_longitude')
            
            logger.info(f"\n🚗 Trip #{trip_id}: {address}")
            
            match = self.match_address(address, lat, lon)
            
            if match:
                stats['matched'] += 1
                logger.info(f"   ✅ {match['customer_name']} ({match['match_confidence']}%)")
            else:
                stats['unmatched'] += 1
                logger.info(f"   ❌ Kein Match gefunden")
        
        return stats


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    matcher = AddressMatcher()
    
    # Test address parsing
    test_addr = "Landauer Straße 32, 76870 Kandel, Deutschland"
    parsed = matcher.parse_german_address(test_addr)
    print(f"Parsed: {parsed}")
    
    # Test matching
    match = matcher.match_address(test_addr, 49.08858, 8.1925)
    print(f"Match: {match}")
