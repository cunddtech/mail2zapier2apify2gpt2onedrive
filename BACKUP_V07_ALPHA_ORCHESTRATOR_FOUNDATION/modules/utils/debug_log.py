# Datei: modules/utils/debug_log.py

import datetime

def debug_log(message):
    """
    Gibt eine formatierte Debug-Nachricht mit Zeitstempel aus.
    """
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    print(f"[{timestamp}] {message}")