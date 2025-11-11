"""
Fahrtenbuch-Integration für C&D Tech GmbH

Automatische Erfassung und Abrechnung von Montagefahrten:
- PAJ GPS Integration (Echtzeit-Tracking)
- Adress-Matching gegen WeClapp CRM
- Automatische Rechnungserstellung
- Freigabe-Workflow
"""

from .paj_gps_client import PAJGPSClient
from .trip_manager import TripManager

__all__ = [
    'PAJGPSClient',
    'TripManager'
]
