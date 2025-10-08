import os
from modules.utils.debug_log import debug_log

def generate_folder_temp(base_folder, temp_folder="Temp"):
    """
    Erstellt einen flachen temporären Ordner für die Verarbeitung.

    Args:
        base_folder (str): Der Basisordner, z. B. "Scan".
        temp_folder (str): Der Name des temporären Ordners (Standard: "Temp").

    Returns:
        dict: Ein Dictionary mit Informationen über den temporären Ordner.
    """
    # Temporären Ordnerpfad erstellen
    temp_path = os.path.join(base_folder, temp_folder)
    os.makedirs(temp_path, exist_ok=True)
    debug_log(f"📂 Temporärer Ordner erstellt: {temp_path}")

    # Überprüfen, ob der Ordner existiert
    if not os.path.exists(temp_path):
        debug_log(f"❌ Fehler: Temporärer Ordner konnte nicht erstellt werden: {temp_path}")
        raise FileNotFoundError(f"Temporärer Ordner konnte nicht erstellt werden: {temp_path}")

    # Überprüfen, ob Schreibrechte vorhanden sind
    if not os.access(temp_path, os.W_OK):
        debug_log(f"❌ Fehler: Keine Schreibrechte für den temporären Ordner: {temp_path}")
        raise PermissionError(f"Keine Schreibrechte für den temporären Ordner: {temp_path}")

    # Rückgabe der Ordnerinformationen
    return {
        "base_folder": base_folder,
        "temp_folder": temp_folder,
        "full_path": temp_path
    }