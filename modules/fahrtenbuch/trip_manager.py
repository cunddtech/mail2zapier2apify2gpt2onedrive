"""
Trip Manager - Fahrtenverwaltung & Datenbank

Verwaltet Fahrten in trip_logs Tabelle:
- Speichern von PAJ GPS Routen
- Status-Tracking (OPEN/MATCHED/INVOICED)
- Duplikats-Erkennung
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TripManager:
    """Manager für Fahrtenbuch-Daten"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize Trip Manager
        
        Args:
            db_path: Pfad zur unified.db (default: Railway path)
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Railway: /tmp/email_tracking.db oder lokal unified.db
            railway_path = Path("/tmp/email_tracking.db")
            local_path = Path("data/databases/unified.db")
            
            if railway_path.exists():
                self.db_path = railway_path
            elif local_path.exists():
                self.db_path = local_path
            else:
                self.db_path = local_path
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Erstelle trip_logs Tabelle falls nicht vorhanden"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # trip_logs Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trip_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    -- Fahrt-Details
                    trip_date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_minutes INTEGER,
                    
                    -- Adressen
                    start_address TEXT,
                    destination_address TEXT NOT NULL,
                    destination_latitude REAL,
                    destination_longitude REAL,
                    
                    -- Distanz & Kosten
                    distance_km REAL,
                    fuel_cost_eur REAL,
                    toll_cost_eur REAL,
                    
                    -- Team & Fahrzeug
                    driver_name TEXT,
                    vehicle_plate TEXT,
                    paj_device_id TEXT,
                    paj_route_id TEXT,
                    
                    -- CRM-Matching
                    customer_id TEXT,
                    customer_name TEXT,
                    contact_id TEXT,
                    opportunity_id TEXT,
                    match_confidence REAL,
                    
                    -- Abrechnungs-Status
                    status TEXT DEFAULT 'OPEN',
                    invoice_id TEXT,
                    invoice_number TEXT,
                    invoice_date TEXT,
                    invoice_amount_eur REAL,
                    
                    -- Freigabe-Workflow
                    approval_status TEXT DEFAULT 'PENDING',
                    approval_date TEXT,
                    approval_by TEXT,
                    rejection_reason TEXT,
                    
                    -- Notizen
                    notes TEXT,
                    project_description TEXT,
                    
                    -- Meta
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Unique: Keine Duplikate
                    UNIQUE(trip_date, start_time, destination_address)
                )
            """)
            
            # Indizes für Performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trip_date ON trip_logs(trip_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON trip_logs(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_approval_status ON trip_logs(approval_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_id ON trip_logs(customer_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_paj_route_id ON trip_logs(paj_route_id)")
            
            conn.commit()
            logger.info(f"✅ trip_logs table initialized in {self.db_path}")
    
    def save_trip(self, trip_data: Dict[str, Any]) -> Optional[int]:
        """
        Speichere Fahrt in Datenbank
        
        Args:
            trip_data: Fahrt-Daten (Dict)
            
        Returns:
            int: Trip ID oder None bei Fehler/Duplikat
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check Duplikat (UNIQUE constraint)
                cursor.execute("""
                    SELECT id FROM trip_logs
                    WHERE trip_date = ? AND start_time = ? AND destination_address = ?
                """, (
                    trip_data.get('trip_date'),
                    trip_data.get('start_time'),
                    trip_data.get('destination_address')
                ))
                
                existing = cursor.fetchone()
                if existing:
                    logger.info(f"⚠️ Trip already exists: {trip_data.get('trip_date')} {trip_data.get('destination_address')}")
                    return existing[0]
                
                # Insert neue Fahrt
                cursor.execute("""
                    INSERT INTO trip_logs (
                        trip_date, start_time, end_time, duration_minutes,
                        start_address, destination_address, destination_latitude, destination_longitude,
                        distance_km, fuel_cost_eur, toll_cost_eur,
                        driver_name, vehicle_plate, paj_device_id, paj_route_id,
                        customer_id, customer_name, contact_id, opportunity_id, match_confidence,
                        status, invoice_id, invoice_number, invoice_date, invoice_amount_eur,
                        approval_status, approval_date, approval_by, rejection_reason,
                        notes, project_description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trip_data.get('trip_date'),
                    trip_data.get('start_time'),
                    trip_data.get('end_time'),
                    trip_data.get('duration_minutes'),
                    trip_data.get('start_address'),
                    trip_data.get('destination_address'),
                    trip_data.get('destination_latitude'),
                    trip_data.get('destination_longitude'),
                    trip_data.get('distance_km'),
                    trip_data.get('fuel_cost_eur'),
                    trip_data.get('toll_cost_eur'),
                    trip_data.get('driver_name'),
                    trip_data.get('vehicle_plate'),
                    trip_data.get('paj_device_id'),
                    trip_data.get('paj_route_id'),
                    trip_data.get('customer_id'),
                    trip_data.get('customer_name'),
                    trip_data.get('contact_id'),
                    trip_data.get('opportunity_id'),
                    trip_data.get('match_confidence'),
                    trip_data.get('status', 'OPEN'),
                    trip_data.get('invoice_id'),
                    trip_data.get('invoice_number'),
                    trip_data.get('invoice_date'),
                    trip_data.get('invoice_amount_eur'),
                    trip_data.get('approval_status', 'PENDING'),
                    trip_data.get('approval_date'),
                    trip_data.get('approval_by'),
                    trip_data.get('rejection_reason'),
                    trip_data.get('notes'),
                    trip_data.get('project_description')
                ))
                
                trip_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"✅ Trip saved: ID {trip_id} - {trip_data.get('destination_address')}")
                return trip_id
        
        except sqlite3.IntegrityError as e:
            logger.warning(f"⚠️ Duplicate trip (UNIQUE constraint): {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error saving trip: {e}")
            return None
    
    def get_trip(self, trip_id: int) -> Optional[Dict[str, Any]]:
        """Hole einzelne Fahrt"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trip_logs WHERE id = ?", (trip_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_trips(
        self,
        status: str = None,
        approval_status: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Hole Fahrten mit Filtern
        
        Args:
            status: OPEN/MATCHED/INVOICED/REJECTED
            approval_status: PENDING/APPROVED/REJECTED
            start_date: Filter ab Datum (ISO 8601)
            end_date: Filter bis Datum (ISO 8601)
            limit: Max Anzahl
            
        Returns:
            List[Dict]: Fahrten
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM trip_logs WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if approval_status:
                query += " AND approval_status = ?"
                params.append(approval_status)
            
            if start_date:
                query += " AND trip_date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND trip_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY trip_date DESC, start_time DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def update_trip(self, trip_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update Fahrt-Daten
        
        Args:
            trip_id: Trip ID
            updates: Dict mit zu aktualisierenden Feldern
            
        Returns:
            bool: Erfolg
        """
        try:
            # Dynamisches SQL UPDATE
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            set_clause += ", updated_at = CURRENT_TIMESTAMP"
            
            values = list(updates.values())
            values.append(trip_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE trip_logs SET {set_clause} WHERE id = ?",
                    values
                )
                conn.commit()
                
                logger.info(f"✅ Trip {trip_id} updated: {list(updates.keys())}")
                return True
        
        except Exception as e:
            logger.error(f"❌ Error updating trip {trip_id}: {e}")
            return False
    
    def delete_trip(self, trip_id: int) -> bool:
        """Lösche Fahrt (nur für Tests/Korrektur)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trip_logs WHERE id = ?", (trip_id,))
                conn.commit()
                logger.info(f"✅ Trip {trip_id} deleted")
                return True
        except Exception as e:
            logger.error(f"❌ Error deleting trip {trip_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Hole Statistiken über Fahrten"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total Fahrten
            cursor.execute("SELECT COUNT(*) FROM trip_logs")
            total = cursor.fetchone()[0]
            
            # Status-Breakdown
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM trip_logs 
                GROUP BY status
            """)
            status_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Approval-Breakdown
            cursor.execute("""
                SELECT approval_status, COUNT(*) as count 
                FROM trip_logs 
                GROUP BY approval_status
            """)
            approval_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Total Umsatz (abgerechnet)
            cursor.execute("""
                SELECT SUM(invoice_amount_eur) 
                FROM trip_logs 
                WHERE status = 'INVOICED'
            """)
            total_revenue = cursor.fetchone()[0] or 0.0
            
            # Durchschnitt pro Fahrt
            cursor.execute("""
                SELECT AVG(invoice_amount_eur) 
                FROM trip_logs 
                WHERE invoice_amount_eur IS NOT NULL
            """)
            avg_revenue = cursor.fetchone()[0] or 0.0
            
            return {
                "total_trips": total,
                "status_breakdown": status_breakdown,
                "approval_breakdown": approval_breakdown,
                "total_revenue_eur": round(total_revenue, 2),
                "avg_revenue_per_trip_eur": round(avg_revenue, 2)
            }


# Test-Funktion
def test_trip_manager():
    """Test Trip Manager"""
    manager = TripManager(db_path="test_trips.db")
    
    # Test 1: Fahrt speichern
    trip = {
        "trip_date": "2025-11-10",
        "start_time": "08:00",
        "end_time": "09:30",
        "duration_minutes": 90,
        "start_address": "Kandel",
        "destination_address": "Karlsruhe Musterstraße 12",
        "destination_latitude": 49.0094,
        "destination_longitude": 8.4044,
        "distance_km": 45.2,
        "driver_name": "Jaszczyk",
        "vehicle_plate": "LD-CD 123",
        "paj_device_id": "12345",
        "status": "OPEN"
    }
    
    trip_id = manager.save_trip(trip)
    print(f"✅ Trip saved: ID {trip_id}")
    
    # Test 2: Fahrt abrufen
    saved_trip = manager.get_trip(trip_id)
    print(f"✅ Trip retrieved: {saved_trip['destination_address']}")
    
    # Test 3: Update
    manager.update_trip(trip_id, {"status": "MATCHED", "customer_name": "Test GmbH"})
    print(f"✅ Trip updated")
    
    # Test 4: Stats
    stats = manager.get_stats()
    print(f"✅ Stats: {stats}")
    
    # Cleanup
    import os
    os.remove("test_trips.db")
    print("✅ Test completed!")


if __name__ == "__main__":
    test_trip_manager()
