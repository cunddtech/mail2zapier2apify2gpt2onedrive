import sqlite3
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_PATH = "email_data.db"

def initialize_database():
    """
    Initialisiert die Datenbank und erstellt die Tabelle 'email_data', falls sie nicht existiert.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        sender TEXT,
        recipient TEXT,
        received_date TEXT,
        ocr_text TEXT,
        gpt_result TEXT,
        weclapp_contact_id TEXT,
        weclapp_customer_id TEXT,
        weclapp_opportunity_id TEXT,
        current_stage TEXT,
        gpt_status_suggestion TEXT,
        status_deviation BOOLEAN,
        remarks TEXT,
        -- Phase 2 Extensions
        message_type TEXT,
        direction TEXT,
        workflow_path TEXT,
        ai_intent TEXT,
        ai_urgency TEXT,
        ai_sentiment TEXT,
        attachments_count INTEGER DEFAULT 0,
        processing_timestamp TEXT,
        processing_duration_ms INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id INTEGER,
        filename TEXT,
        content_type TEXT,
        size_bytes INTEGER,
        document_type TEXT,
        ocr_route TEXT,
        ocr_text TEXT,
        ocr_structured_data TEXT,
        processing_timestamp TEXT,
        document_hash TEXT,
        onedrive_path TEXT,
        duplicate_of INTEGER,
        FOREIGN KEY (email_id) REFERENCES email_data (id),
        FOREIGN KEY (duplicate_of) REFERENCES attachments (id)
    )
    """)
    
    # Create index for fast duplicate lookups
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_document_hash ON attachments(document_hash)
    """)

    conn.commit()
    conn.close()

@app.route('/insert', methods=['POST'])
def insert_email_data():
    """
    Fügt die E-Mail-Daten in die Datenbank ein.
    """
    data = request.json
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO email_data (
            subject, sender, recipient, received_date, ocr_text, gpt_result,
            weclapp_contact_id, weclapp_customer_id, weclapp_opportunity_id,
            current_stage, gpt_status_suggestion, status_deviation, remarks
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["subject"], data["sender"], data["recipient"], data["received_date"],
            data["ocr_text"], data["gpt_result"], data["weclapp_contact_id"],
            data["weclapp_customer_id"], data["weclapp_opportunity_id"],
            data["current_stage"], data["gpt_status_suggestion"],
            data["status_deviation"], data["remarks"]
        ))

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Data inserted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    initialize_database()
    app.run(host='0.0.0.0', port=5000)