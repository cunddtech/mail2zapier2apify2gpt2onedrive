# Debugging-Skript für schnelle Zusammenarbeit mit GitHub Copilot
import os
import sys
import sqlite3

# 1. Debugging-Log aktivieren
def debug_log(message):
    """
    Gibt Debugging-Informationen aus.
    """
    print(f"DEBUG: {message}")

# 2. Datenbank-Initialisierung testen
def test_initialize_database():
    """
    Testet die Funktion initialize_database.
    """
    try:
        from modules.database.email_database import initialize_database
        debug_log("📂 Funktion 'initialize_database' erfolgreich importiert.")
        initialize_database()
        debug_log("✅ Datenbank erfolgreich initialisiert.")
    except ImportError as e:
        debug_log(f"❌ ImportError: {e}")
    except Exception as e:
        debug_log(f"❌ Fehler bei der Initialisierung der Datenbank: {e}")

# 3. Datenbank-Debugging
def check_database_structure(db_path="email_data.db"):
    """
    Überprüft die Struktur der Datenbank und listet die Tabellen auf.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        debug_log(f"📋 Tabellen in der Datenbank: {tables}")
        conn.close()
    except sqlite3.Error as e:
        debug_log(f"❌ Datenbankfehler: {e}")

# 4. Import-Test
def test_imports():
    """
    Testet die Importe in der Datei process_email_workflow.py.
    """
    try:
        from modules.mail.process_email_workflow import process_email_workflow
        debug_log("✅ Funktion 'process_email_workflow' erfolgreich importiert.")
    except ImportError as e:
        debug_log(f"❌ ImportError: {e}")

# 5. Haupt-Debugging-Funktion
def main():
    """
    Führt alle Debugging-Tests aus.
    """
    debug_log("🚀 Starte Debugging...")
    
    # Teste die Datenbank-Initialisierung
    test_initialize_database()
    
    # Überprüfe die Datenbankstruktur
    check_database_structure()
    
    # Teste die Importe
    test_imports()
    
    debug_log("🏁 Debugging abgeschlossen.")

if __name__ == "__main__":
    main()