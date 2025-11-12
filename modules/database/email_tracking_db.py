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
        
        # ========================================
        # UUID ACTION SYSTEM TABLES
        # ========================================
        
        # 1. User Communications - Alle gesendeten Notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_communications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                communication_uuid TEXT NOT NULL UNIQUE,
                email_message_id TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                sent_via TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                recipient_email TEXT,
                subject TEXT,
                html_content TEXT,
                text_content TEXT,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (email_message_id) REFERENCES processed_emails(message_id)
            )
        """)
        
        # 2. Action Buttons - Alle generierten Buttons mit UUIDs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                button_uuid TEXT NOT NULL UNIQUE,
                communication_uuid TEXT NOT NULL,
                email_message_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action_label TEXT NOT NULL,
                action_config TEXT,
                button_color TEXT,
                button_icon TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (communication_uuid) REFERENCES user_communications(communication_uuid),
                FOREIGN KEY (email_message_id) REFERENCES processed_emails(message_id)
            )
        """)
        
        # 3. Action History - Execution Log für alle Button-Klicks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_uuid TEXT NOT NULL UNIQUE,
                button_uuid TEXT NOT NULL,
                executed_at TEXT NOT NULL,
                executed_by TEXT,
                execution_status TEXT NOT NULL,
                execution_result TEXT,
                error_message TEXT,
                processing_time_seconds REAL,
                side_effects TEXT,
                FOREIGN KEY (button_uuid) REFERENCES action_buttons(button_uuid)
            )
        """)
        
        # 4. Workflow States - Status-Tracking für komplexe Workflows
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_uuid TEXT NOT NULL UNIQUE,
                email_message_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                current_stage TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                workflow_data TEXT,
                FOREIGN KEY (email_message_id) REFERENCES processed_emails(message_id)
            )
        """)
        
        # 5. Task Queue - Asynchrone Tasks für zeitversetzte Aktionen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_uuid TEXT NOT NULL UNIQUE,
                task_type TEXT NOT NULL,
                email_message_id TEXT,
                scheduled_at TEXT NOT NULL,
                execute_after TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                task_data TEXT,
                last_attempt_at TEXT,
                error_log TEXT,
                completed_at TEXT,
                FOREIGN KEY (email_message_id) REFERENCES processed_emails(message_id)
            )
        """)
        
        # 6. Trip-Opportunity Links - Verbindung zwischen Fahrtenbuch und WeClapp
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trip_opportunity_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_uuid TEXT NOT NULL UNIQUE,
                trip_id TEXT NOT NULL,
                opportunity_id TEXT NOT NULL,
                email_message_id TEXT,
                linked_at TEXT NOT NULL,
                linked_by TEXT,
                link_type TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (email_message_id) REFERENCES processed_emails(message_id)
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
        
        # Indizes für UUID Action System
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_communication_uuid ON user_communications(communication_uuid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_button_uuid ON action_buttons(button_uuid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_uuid ON action_history(execution_uuid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_uuid ON workflow_states(workflow_uuid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_uuid ON task_queue(task_uuid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_link_uuid ON trip_opportunity_links(link_uuid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_message_id_actions ON action_buttons(email_message_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_status ON task_queue(status, execute_after)")
        
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
    
    # ========================================
    # UUID ACTION SYSTEM METHODS
    # ========================================
    
    def register_communication(self, communication_uuid: str, email_message_id: str, 
                               notification_type: str, sent_via: str, recipient_email: str,
                               subject: str, html_content: str = None) -> bool:
        """Registriert eine gesendete Notification"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_communications 
                (communication_uuid, email_message_id, notification_type, sent_via, sent_at,
                 recipient_email, subject, html_content, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'sent')
            """, (communication_uuid, email_message_id, notification_type, sent_via,
                  datetime.now().isoformat(), recipient_email, subject, html_content))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error registering communication: {e}")
            return False
    
    def register_button(self, button_uuid: str, communication_uuid: str, email_message_id: str,
                       action_type: str, action_label: str, action_config: Dict = None,
                       button_color: str = None, button_icon: str = None, expires_at: str = None) -> bool:
        """Registriert einen Action Button mit UUID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO action_buttons
                (button_uuid, communication_uuid, email_message_id, action_type, action_label,
                 action_config, button_color, button_icon, created_at, expires_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (button_uuid, communication_uuid, email_message_id, action_type, action_label,
                  json.dumps(action_config) if action_config else None,
                  button_color, button_icon, datetime.now().isoformat(), expires_at))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error registering button: {e}")
            return False
    
    def get_button_info(self, button_uuid: str) -> Optional[Dict]:
        """Holt Button-Informationen für Action Execution"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ab.*, pe.from_address, pe.subject as email_subject, pe.received_date,
                       uc.recipient_email, uc.notification_type
                FROM action_buttons ab
                JOIN processed_emails pe ON ab.email_message_id = pe.message_id
                JOIN user_communications uc ON ab.communication_uuid = uc.communication_uuid
                WHERE ab.button_uuid = ?
            """, (button_uuid,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                result = dict(row)
                if result.get('action_config'):
                    result['action_config'] = json.loads(result['action_config'])
                return result
            return None
        except Exception as e:
            print(f"❌ Error getting button info: {e}")
            return None
    
    def log_action_execution(self, button_uuid: str, execution_status: str,
                            execution_result: str = None, error_message: str = None,
                            processing_time: float = None, side_effects: Dict = None,
                            executed_by: str = None) -> str:
        """Loggt eine Button Action Execution"""
        try:
            import uuid
            execution_uuid = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO action_history
                (execution_uuid, button_uuid, executed_at, executed_by, execution_status,
                 execution_result, error_message, processing_time_seconds, side_effects)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (execution_uuid, button_uuid, datetime.now().isoformat(), executed_by,
                  execution_status, execution_result, error_message, processing_time,
                  json.dumps(side_effects) if side_effects else None))
            
            conn.commit()
            conn.close()
            return execution_uuid
        except Exception as e:
            print(f"❌ Error logging action execution: {e}")
            return None
    
    def get_execution_history(self, button_uuid: str = None, email_message_id: str = None,
                             limit: int = 50) -> List[Dict]:
        """Holt Execution History für Button oder Email"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if button_uuid:
                cursor.execute("""
                    SELECT ah.*, ab.action_type, ab.action_label
                    FROM action_history ah
                    JOIN action_buttons ab ON ah.button_uuid = ab.button_uuid
                    WHERE ah.button_uuid = ?
                    ORDER BY ah.executed_at DESC
                    LIMIT ?
                """, (button_uuid, limit))
            elif email_message_id:
                cursor.execute("""
                    SELECT ah.*, ab.action_type, ab.action_label
                    FROM action_history ah
                    JOIN action_buttons ab ON ah.button_uuid = ab.button_uuid
                    WHERE ab.email_message_id = ?
                    ORDER BY ah.executed_at DESC
                    LIMIT ?
                """, (email_message_id, limit))
            else:
                cursor.execute("""
                    SELECT ah.*, ab.action_type, ab.action_label
                    FROM action_history ah
                    JOIN action_buttons ab ON ah.button_uuid = ab.button_uuid
                    ORDER BY ah.executed_at DESC
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                result = dict(row)
                if result.get('side_effects'):
                    result['side_effects'] = json.loads(result['side_effects'])
                results.append(result)
            return results
        except Exception as e:
            print(f"❌ Error getting execution history: {e}")
            return []
    
    def create_workflow(self, email_message_id: str, workflow_type: str, 
                       initial_stage: str, workflow_data: Dict = None) -> str:
        """Erstellt einen neuen Workflow State"""
        try:
            import uuid
            workflow_uuid = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO workflow_states
                (workflow_uuid, email_message_id, workflow_type, current_stage, status,
                 created_at, updated_at, workflow_data)
                VALUES (?, ?, ?, ?, 'active', ?, ?, ?)
            """, (workflow_uuid, email_message_id, workflow_type, initial_stage,
                  now, now, json.dumps(workflow_data) if workflow_data else None))
            
            conn.commit()
            conn.close()
            return workflow_uuid
        except Exception as e:
            print(f"❌ Error creating workflow: {e}")
            return None
    
    def update_workflow_state(self, workflow_uuid: str, new_stage: str = None,
                             status: str = None, workflow_data: Dict = None) -> bool:
        """Updated Workflow State"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if new_stage:
                updates.append("current_stage = ?")
                params.append(new_stage)
            if status:
                updates.append("status = ?")
                params.append(status)
                if status == 'completed':
                    updates.append("completed_at = ?")
                    params.append(datetime.now().isoformat())
            if workflow_data:
                updates.append("workflow_data = ?")
                params.append(json.dumps(workflow_data))
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(workflow_uuid)
            
            query = f"UPDATE workflow_states SET {', '.join(updates)} WHERE workflow_uuid = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error updating workflow: {e}")
            return False
    
    def queue_task(self, task_type: str, execute_after: str, task_data: Dict = None,
                  email_message_id: str = None, priority: int = 5) -> str:
        """Fügt Task zur Queue hinzu"""
        try:
            import uuid
            task_uuid = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO task_queue
                (task_uuid, task_type, email_message_id, scheduled_at, execute_after,
                 priority, status, task_data)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (task_uuid, task_type, email_message_id, datetime.now().isoformat(),
                  execute_after, priority, json.dumps(task_data) if task_data else None))
            
            conn.commit()
            conn.close()
            return task_uuid
        except Exception as e:
            print(f"❌ Error queueing task: {e}")
            return None
    
    def get_pending_tasks(self, limit: int = 100) -> List[Dict]:
        """Holt pending Tasks die ausgeführt werden sollen"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                SELECT * FROM task_queue
                WHERE status = 'pending'
                  AND execute_after <= ?
                  AND attempts < max_attempts
                ORDER BY priority DESC, execute_after ASC
                LIMIT ?
            """, (now, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                result = dict(row)
                if result.get('task_data'):
                    result['task_data'] = json.loads(result['task_data'])
                if result.get('error_log'):
                    result['error_log'] = json.loads(result['error_log'])
                results.append(result)
            return results
        except Exception as e:
            print(f"❌ Error getting pending tasks: {e}")
            return []
    
    def update_task_status(self, task_uuid: str, status: str, error_message: str = None) -> bool:
        """Updated Task Status nach Execution"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT attempts, error_log FROM task_queue WHERE task_uuid = ?", (task_uuid,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return False
            
            attempts = row[0] + 1
            error_log = json.loads(row[1]) if row[1] else []
            
            if error_message:
                error_log.append({
                    "attempt": attempts,
                    "timestamp": datetime.now().isoformat(),
                    "error": error_message
                })
            
            updates = [
                "status = ?",
                "attempts = ?",
                "last_attempt_at = ?",
                "error_log = ?"
            ]
            params = [status, attempts, datetime.now().isoformat(), json.dumps(error_log)]
            
            if status == 'completed':
                updates.append("completed_at = ?")
                params.append(datetime.now().isoformat())
            
            params.append(task_uuid)
            query = f"UPDATE task_queue SET {', '.join(updates)} WHERE task_uuid = ?"
            
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error updating task status: {e}")
            return False
    
    def link_trip_to_opportunity(self, trip_id: str, opportunity_id: str,
                                link_type: str, email_message_id: str = None,
                                linked_by: str = None, metadata: Dict = None) -> str:
        """Verknüpft Fahrtenbuch-Eintrag mit WeClapp Opportunity"""
        try:
            import uuid
            link_uuid = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO trip_opportunity_links
                (link_uuid, trip_id, opportunity_id, email_message_id, linked_at,
                 linked_by, link_type, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (link_uuid, trip_id, opportunity_id, email_message_id,
                  datetime.now().isoformat(), linked_by, link_type,
                  json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            return link_uuid
        except Exception as e:
            print(f"❌ Error linking trip to opportunity: {e}")
            return None


# Globale Instanz (Singleton-Pattern)
_tracking_db_instance = None

def get_email_tracking_db() -> EmailTrackingDB:
    """Holt globale EmailTrackingDB Instanz"""
    global _tracking_db_instance
    if _tracking_db_instance is None:
        _tracking_db_instance = EmailTrackingDB()
    return _tracking_db_instance
