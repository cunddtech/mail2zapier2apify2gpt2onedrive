"""
Email Tracking Database - Duplikatprüfung & Verarbeitungsstatus
Separate DB für Email-Processing neben weclapp_sync.db
"""
import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, List
import os


class EmailTrackingDB:
    """Verwaltet Email Processing History & Duplikatprüfung"""
    
    def __init__(self, db_path: str = "/tmp/email_tracking.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Erstellt Database Schema wenn nicht vorhanden"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Haupttabelle für Email-Verarbeitung
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL UNIQUE,
                user_email TEXT NOT NULL,
                from_address TEXT,
                subject TEXT,
                received_date TEXT,
                processed_date TEXT NOT NULL,
                
                -- Duplikatprüfung
                subject_hash TEXT,
                content_hash TEXT,
                
                -- Verarbeitungsstatus
                workflow_path TEXT,
                document_type TEXT,
                is_duplicate BOOLEAN DEFAULT 0,
                duplicate_of_message_id TEXT,
                
                -- AI Analysis Ergebnisse
                kunde TEXT,
                lieferant TEXT,
                projektnummer TEXT,
                ordnerstruktur TEXT,
                summe TEXT,
                
                -- OneDrive Upload
                onedrive_uploaded BOOLEAN DEFAULT 0,
                onedrive_path TEXT,
                onedrive_link TEXT,
                
                -- Metadaten
                attachment_count INTEGER DEFAULT 0,
                total_size_bytes INTEGER DEFAULT 0,
                processing_time_seconds REAL
            )
        """)
        
        # Anhänge-Tabelle (1:N Beziehung)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_message_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                content_type TEXT,
                size_bytes INTEGER,
                file_hash TEXT NOT NULL,
                
                -- OCR Ergebnisse
                ocr_text TEXT,
                ocr_route TEXT,
                
                -- OneDrive
                onedrive_path TEXT,
                onedrive_link TEXT,
                
                processed_date TEXT NOT NULL,
                
                FOREIGN KEY (email_message_id) REFERENCES processed_emails(message_id)
            )
        """)
        
        # Indizes für schnelle Suche
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_id ON processed_emails(message_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subject_hash ON processed_emails(subject_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON processed_emails(content_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON email_attachments(file_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_from_address ON processed_emails(from_address)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_received_date ON processed_emails(received_date)")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Email Tracking DB initialized: {self.db_path}")
    
    @staticmethod
    def calculate_content_hash(subject: str, body: str, from_address: str) -> str:
        """Berechnet Content-Hash für Duplikatprüfung"""
        # Normalisiere Strings (lowercase, strip whitespace)
        normalized = f"{subject.lower().strip()}|{body[:500].lower().strip()}|{from_address.lower().strip()}"
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Berechnet SHA256 Hash eines Files"""
        return hashlib.sha256(file_bytes).hexdigest()[:16]
    
    def check_duplicate_by_message_id(self, message_id: str) -> Optional[Dict]:
        """Prüft ob message_id bereits verarbeitet wurde"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message_id, processed_date, workflow_path, document_type, 
                   ordnerstruktur, onedrive_link
            FROM processed_emails 
            WHERE message_id = ?
        """, (message_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "message_id": row[0],
                "processed_date": row[1],
                "workflow_path": row[2],
                "document_type": row[3],
                "ordnerstruktur": row[4],
                "onedrive_link": row[5]
            }
        return None
    
    def check_duplicate_by_content(
        self, 
        subject: str, 
        body: str, 
        from_address: str,
        hours_window: int = 24
    ) -> Optional[Dict]:
        """
        Prüft ob ähnliche Email bereits verarbeitet wurde (Content-basiert)
        
        Args:
            subject: Email Betreff
            body: Email Body
            from_address: Absender
            hours_window: Zeitfenster in Stunden (default 24h)
        """
        content_hash = self.calculate_content_hash(subject, body, from_address)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message_id, subject, from_address, processed_date, 
                   ordnerstruktur, onedrive_link
            FROM processed_emails 
            WHERE content_hash = ? 
            AND datetime(processed_date) > datetime('now', '-' || ? || ' hours')
        """, (content_hash, hours_window))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "message_id": row[0],
                "subject": row[1],
                "from_address": row[2],
                "processed_date": row[3],
                "ordnerstruktur": row[4],
                "onedrive_link": row[5]
            }
        return None
    
    def check_duplicate_attachment(self, file_hash: str) -> Optional[Dict]:
        """Prüft ob Anhang-Hash bereits existiert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.filename, a.processed_date, a.onedrive_link, 
                   e.message_id, e.subject
            FROM email_attachments a
            JOIN processed_emails e ON a.email_message_id = e.message_id
            WHERE a.file_hash = ?
            ORDER BY a.processed_date DESC
            LIMIT 1
        """, (file_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "filename": row[0],
                "processed_date": row[1],
                "onedrive_link": row[2],
                "email_message_id": row[3],
                "email_subject": row[4]
            }
        return None
    
    def save_email(
        self,
        message_id: str,
        user_email: str,
        from_address: str,
        subject: str,
        body: str,
        received_date: str,
        workflow_path: str,
        ai_analysis: Dict,
        attachment_results: List[Dict] = None,
        processing_time: float = 0.0,
        is_duplicate: bool = False,
        duplicate_of: str = None
    ) -> int:
        """
        Speichert verarbeitete Email in Database
        
        Returns:
            Email ID (auto-increment primary key)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Berechne Hashes
        content_hash = self.calculate_content_hash(subject, body, from_address)
        subject_hash = hashlib.md5(subject.encode()).hexdigest()[:16]
        
        # Email speichern
        cursor.execute("""
            INSERT INTO processed_emails (
                message_id, user_email, from_address, subject, received_date,
                processed_date, subject_hash, content_hash,
                workflow_path, document_type, is_duplicate, duplicate_of_message_id,
                kunde, lieferant, projektnummer, ordnerstruktur, summe,
                attachment_count, processing_time_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message_id,
            user_email,
            from_address,
            subject,
            received_date,
            datetime.utcnow().isoformat(),
            subject_hash,
            content_hash,
            workflow_path,
            ai_analysis.get("dokumenttyp", ai_analysis.get("document_type")),
            is_duplicate,
            duplicate_of,
            ai_analysis.get("kunde"),
            ai_analysis.get("lieferant"),
            ai_analysis.get("projektnummer"),
            ai_analysis.get("ordnerstruktur"),
            ai_analysis.get("summe"),
            len(attachment_results) if attachment_results else 0,
            processing_time
        ))
        
        email_id = cursor.lastrowid
        
        # Anhänge speichern
        if attachment_results:
            for att in attachment_results:
                file_hash = att.get("file_hash", "")
                
                cursor.execute("""
                    INSERT INTO email_attachments (
                        email_message_id, filename, content_type, size_bytes,
                        file_hash, ocr_text, ocr_route, processed_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message_id,
                    att.get("filename", ""),
                    att.get("content_type", ""),
                    att.get("size", 0),
                    file_hash,
                    att.get("ocr_text", "")[:1000],  # Nur erste 1000 Zeichen
                    att.get("ocr_route", ""),
                    datetime.utcnow().isoformat()
                ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Email saved to tracking DB: {message_id} (ID: {email_id})")
        
        return email_id
    
    def update_onedrive_upload(
        self,
        message_id: str,
        onedrive_path: str,
        onedrive_link: str
    ):
        """Aktualisiert OneDrive Upload Status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE processed_emails 
            SET onedrive_uploaded = 1,
                onedrive_path = ?,
                onedrive_link = ?
            WHERE message_id = ?
        """, (onedrive_path, onedrive_link, message_id))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """Holt Verarbeitungs-Statistiken"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total verarbeitete Emails
        cursor.execute("SELECT COUNT(*) FROM processed_emails")
        stats["total_emails"] = cursor.fetchone()[0]
        
        # Duplikate
        cursor.execute("SELECT COUNT(*) FROM processed_emails WHERE is_duplicate = 1")
        stats["duplicates"] = cursor.fetchone()[0]
        
        # Nach Dokumenttyp
        cursor.execute("""
            SELECT document_type, COUNT(*) 
            FROM processed_emails 
            WHERE document_type IS NOT NULL
            GROUP BY document_type
        """)
        stats["by_document_type"] = dict(cursor.fetchall())
        
        # Nach Workflow
        cursor.execute("""
            SELECT workflow_path, COUNT(*) 
            FROM processed_emails 
            GROUP BY workflow_path
        """)
        stats["by_workflow"] = dict(cursor.fetchall())
        
        # OneDrive Uploads
        cursor.execute("SELECT COUNT(*) FROM processed_emails WHERE onedrive_uploaded = 1")
        stats["onedrive_uploads"] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats


# Globale Instanz (Singleton-Pattern)
_tracking_db_instance = None

def get_email_tracking_db() -> EmailTrackingDB:
    """Holt globale EmailTrackingDB Instanz"""
    global _tracking_db_instance
    if _tracking_db_instance is None:
        _tracking_db_instance = EmailTrackingDB()
    return _tracking_db_instance
