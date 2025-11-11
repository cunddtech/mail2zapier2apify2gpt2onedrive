"""
PAJ GPS API Client

Authentifizierung und Datenabruf von PAJ GPS Tracker-System.
API-Dokumentation: https://connect.paj-gps.de/api/documentation
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PAJGPSClient:
    """Client für PAJ GPS API Integration"""
    
    BASE_URL = "https://connect.paj-gps.de/api/v1"
    
    def __init__(self, email: str = None, password: str = None):
        """
        Initialize PAJ GPS Client
        
        Args:
            email: PAJ GPS Account Email (oder aus ENV)
            password: PAJ GPS Account Password (oder aus ENV)
        """
        self.email = email or os.getenv("PAJ_GPS_EMAIL")
        self.password = password or os.getenv("PAJ_GPS_PASSWORD")
        
        if not self.email or not self.password:
            raise ValueError("PAJ GPS credentials missing! Set PAJ_GPS_EMAIL and PAJ_GPS_PASSWORD env vars.")
        
        self.token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        # ClientSession mit Cookie-Jar (für Session-basierte Auth)
        cookie_jar = aiohttp.CookieJar(unsafe=True)  # unsafe=True für Domain-übergreifende Cookies
        self.session = aiohttp.ClientSession(cookie_jar=cookie_jar)
        await self.login()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def login(self) -> Dict[str, Any]:
        """
        Authentifizierung bei PAJ GPS API
        
        Returns:
            Dict mit Token-Daten
        """
        url = f"{self.BASE_URL}/login"
        payload = {
            "email": self.email,
            "password": self.password
        }
        
        logger.info(f"🔑 PAJ GPS Login: {self.email}")
        
        try:
            async with self.session.post(url, json=payload) as response:
                response_text = await response.text()
                logger.info(f"📥 Login Response: Status {response.status}")
                logger.debug(f"Response Body: {response_text[:200]}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # PAJ GPS gibt Token in {"success": {"token": "..."}} zurück
                    if "success" in data and isinstance(data["success"], dict):
                        success_data = data["success"]
                        self.token = success_data.get("token")
                        self.refresh_token = success_data.get("refresh_token")
                        self.user_id = success_data.get("userID")
                        
                        if self.token:
                            # Token expires in (default 30 Tage = 2592000 sekunden)
                            expires_in_seconds = success_data.get("expires_in", 2592000)
                            self.token_expires = datetime.now() + timedelta(seconds=expires_in_seconds - 300)  # 5 min Puffer
                            
                            logger.info(f"✅ PAJ GPS Login erfolgreich!")
                            logger.info(f"   User ID: {self.user_id}")
                            logger.info(f"   Token expires in: {expires_in_seconds / 86400:.1f} days")
                            logger.info(f"   Token preview: {self.token[:30]}...")
                            return data
                    
                    # Fallback für altes Response-Format
                    if data.get("success"):
                        logger.info("✅ PAJ GPS Login erfolgreich (Cookie-basiert)")
                        
                        # Check ob Token in Cookies
                        cookies = response.cookies
                        if cookies:
                            logger.info(f"🍪 Cookies erhalten: {list(cookies.keys())}")
                            # Token könnte in Cookie sein
                            self.token = cookies.get('token', {}).value if 'token' in cookies else "SESSION"
                        else:
                            # Kein Token, aber Success - verwende Session-basierte Auth
                            self.token = "SESSION_BASED_AUTH"
                            logger.info("📝 Verwende Session-basierte Authentifizierung (keine Tokens)")
                        
                        self.token_expires = datetime.now() + timedelta(hours=24)  # Session-basiert
                        return data
                    
                    # Fallback: Token in Response Body
                    self.token = data.get("token") or data.get("access_token") or data.get("accessToken")
                    self.refresh_token = data.get("refreshToken") or data.get("refresh_token")
                    
                    if not self.token:
                        logger.error(f"❌ No token in response: {data.keys()}")
                        logger.error(f"Full response: {data}")
                        raise Exception("No token received from PAJ GPS API")
                    
                    self.token_expires = datetime.now() + timedelta(minutes=55)
                    
                    logger.info(f"✅ PAJ GPS Login erfolgreich - Token expires: {self.token_expires}")
                    logger.info(f"🔑 Token preview: {self.token[:20]}...")
                    return data
                else:
                    logger.error(f"❌ PAJ GPS Login fehlgeschlagen: {response.status} - {response_text}")
                    raise Exception(f"PAJ GPS Login failed: {response_text}")
        
        except Exception as e:
            logger.error(f"❌ PAJ GPS Login Error: {e}")
            raise
    
    async def ensure_token(self):
        """Stelle sicher dass Token gültig ist (refresh falls nötig)"""
        if not self.token:
            await self.login()
            return
        
        # Token abgelaufen? Refresh!
        if self.token_expires and datetime.now() >= self.token_expires:
            logger.info("🔄 PAJ GPS Token expired - Refreshing...")
            await self.refresh_access_token()
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh abgelaufenen Token
        
        Returns:
            Dict mit neuen Token-Daten
        """
        url = f"{self.BASE_URL}/updatetoken"
        headers = {"Authorization": f"Bearer {self.refresh_token}"}
        
        try:
            async with self.session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("token")
                    self.token_expires = datetime.now() + timedelta(minutes=55)
                    
                    logger.info(f"✅ PAJ GPS Token refreshed - expires: {self.token_expires}")
                    return data
                else:
                    # Refresh failed → Full re-login
                    logger.warning("⚠️ PAJ GPS Token refresh failed - Re-logging in...")
                    await self.login()
        
        except Exception as e:
            logger.error(f"❌ PAJ GPS Token Refresh Error: {e}")
            await self.login()  # Fallback: Full login
    
    async def get_devices(self) -> List[Dict[str, Any]]:
        """
        Hole alle GPS-Geräte (Fahrzeuge)
        
        Returns:
            List[Dict]: Geräte-Liste
        """
        await self.ensure_token()
        
        url = f"{self.BASE_URL}/device"
        
        # Bearer Token Auth (PAJ GPS erwartet "Bearer {token}")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        logger.info("📡 Fetching PAJ GPS devices...")
        logger.info(f"   URL: {url}")
        logger.info(f"   Auth: Bearer Token")
        
        try:
            async with self.session.get(url, headers=headers) as response:
                response_text = await response.text()
                logger.info(f"📥 Devices Response: Status {response.status}")
                
                if response.status == 200:
                    devices = await response.json()
                    # PAJ GPS gibt verschachtelte Response zurück
                    if isinstance(devices, dict) and "success" in devices:
                        devices = devices["success"]
                    
                    logger.info(f"✅ Found {len(devices)} PAJ GPS device(s)")
                    return devices if isinstance(devices, list) else [devices]
                else:
                    logger.error(f"❌ Failed to fetch devices: {response.status} - {response_text[:200]}")
                    return []
        
        except Exception as e:
            logger.error(f"❌ Error fetching devices: {e}")
            return []
    
    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Hole einzelnes Gerät (Fahrzeug)
        
        Args:
            device_id: PAJ GPS Device ID
            
        Returns:
            Dict mit Geräte-Daten
        """
        await self.ensure_token()
        
        url = f"{self.BASE_URL}/device/{device_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"❌ Failed to fetch device {device_id}: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"❌ Error fetching device {device_id}: {e}")
            return None
    
    async def get_all_routes(self, device_id: str) -> List[Dict[str, Any]]:
        """
        Hole alle Fahrtenbuch-Routen eines Geräts
        
        Args:
            device_id: PAJ GPS Device ID
            
        Returns:
            List[Dict]: Routen-Daten (Fahrten)
        """
        await self.ensure_token()
        
        url = f"{self.BASE_URL}/logbook/getAllRoutes/{device_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        logger.info(f"📖 Fetching all routes for device {device_id}...")
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # PAJ GPS returns paginated format: {"data": {"Date": [routes]}}
                    routes = []
                    if isinstance(data, dict) and "data" in data:
                        # Flatten all routes from all date groups
                        date_groups = data["data"]
                        if isinstance(date_groups, dict):
                            for date_key, date_routes in date_groups.items():
                                if isinstance(date_routes, list):
                                    routes.extend(date_routes)
                    
                    logger.info(f"✅ Found {len(routes)} route(s) for device {device_id}")
                    return routes
                else:
                    error = await response.text()
                    logger.error(f"❌ Failed to fetch routes: {response.status} - {error}")
                    return []
        
        except Exception as e:
            logger.error(f"❌ Error fetching routes: {e}")
            return []
    
    async def generate_routes(
        self, 
        device_id: str,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generiere Fahrtenbuch-Routen für Zeitraum
        
        Args:
            device_id: PAJ GPS Device ID
            start_date: Start-Datum (ISO 8601) - Default: Heute
            end_date: End-Datum (ISO 8601) - Default: Heute
            
        Returns:
            List[Dict]: Generierte Routen
        """
        await self.ensure_token()
        
        # Default: Heute
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        url = f"{self.BASE_URL}/logbook/generateSingleDeviceRoutes/{device_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "startDate": start_date,
            "endDate": end_date
        }
        
        logger.info(f"🔄 Generating routes for {device_id} ({start_date} to {end_date})...")
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    routes = await response.json()
                    logger.info(f"✅ Generated {len(routes)} route(s)")
                    return routes
                else:
                    error = await response.text()
                    logger.error(f"❌ Failed to generate routes: {response.status} - {error}")
                    return []
        
        except Exception as e:
            logger.error(f"❌ Error generating routes: {e}")
            return []
    
    async def get_tracking_data_range(
        self,
        device_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Hole Tracking-Daten für Datumsbereich
        
        Args:
            device_id: PAJ GPS Device ID
            start_date: Start-Datum (ISO 8601)
            end_date: End-Datum (ISO 8601)
            
        Returns:
            List[Dict]: Tracking-Punkte
        """
        await self.ensure_token()
        
        url = f"{self.BASE_URL}/trackerdata/{device_id}/date_range"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "startDate": start_date,
            "endDate": end_date
        }
        
        logger.info(f"📍 Fetching tracking data for {device_id} ({start_date} to {end_date})...")
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Found {len(data)} tracking point(s)")
                    return data
                else:
                    error = await response.text()
                    logger.error(f"❌ Failed to fetch tracking data: {response.status} - {error}")
                    return []
        
        except Exception as e:
            logger.error(f"❌ Error fetching tracking data: {e}")
            return []
    
    async def get_last_positions(self) -> List[Dict[str, Any]]:
        """
        Hole letzte Positionen aller Geräte
        
        Returns:
            List[Dict]: Letzte Positionen
        """
        await self.ensure_token()
        
        url = f"{self.BASE_URL}/trackerdata/getalllastpositions"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            async with self.session.post(url, headers=headers) as response:
                if response.status == 200:
                    positions = await response.json()
                    logger.info(f"✅ Found last positions for {len(positions)} device(s)")
                    return positions
                else:
                    error = await response.text()
                    logger.error(f"❌ Failed to fetch last positions: {response.status} - {error}")
                    return []
        
        except Exception as e:
            logger.error(f"❌ Error fetching last positions: {e}")
            return []


# Convenience Function
async def get_paj_client() -> PAJGPSClient:
    """
    Factory function für PAJ GPS Client (async context manager)
    
    Usage:
        async with get_paj_client() as paj:
            devices = await paj.get_devices()
    """
    client = PAJGPSClient()
    await client.login()
    return client


# Test-Funktion
async def test_paj_gps():
    """Test PAJ GPS API Connection"""
    try:
        async with PAJGPSClient() as paj:
            # Test 1: Geräte abrufen
            devices = await paj.get_devices()
            print(f"\n✅ Devices: {len(devices)}")
            for device in devices:
                print(f"   - {device.get('name')} (ID: {device.get('idNo')})")
            
            # Test 2: Routen abrufen (erstes Gerät)
            if devices:
                device_id = devices[0].get('idNo')
                routes = await paj.get_all_routes(device_id)
                print(f"\n✅ Routes: {len(routes)}")
                
                # Test 3: Routen generieren (heute)
                today = datetime.now().strftime("%Y-%m-%d")
                generated = await paj.generate_routes(device_id, today, today)
                print(f"\n✅ Generated routes (today): {len(generated)}")
            
            print("\n🎉 PAJ GPS API Test successful!")
    
    except Exception as e:
        print(f"\n❌ PAJ GPS API Test failed: {e}")


if __name__ == "__main__":
    # Test ausführen
    asyncio.run(test_paj_gps())
