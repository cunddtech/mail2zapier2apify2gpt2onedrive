# filepath: /Users/cdtechgmbh/Documents/lokal_test/apify_debug_template/actor_files/modules/filegen/generate_filename_temp.py
import uuid

def generate_filename_temp(dokumenttyp="Temp", kunde="Temp", extension=".pdf"):
    """
    Generiert einen temporären Dateinamen.

    Args:
        dokumenttyp (str): Der Dokumenttyp (z. B. Rechnung, Lieferschein).
        kunde (str): Der Name des Kunden.
        extension (str): Die Dateiendung (z. B. ".pdf").

    Returns:
        str: Der generierte Dateiname.
    """
    # Eingabevalidierung
    if not dokumenttyp:
        dokumenttyp = "Unbekannt"
    if not kunde:
        kunde = "Unbekannt"
    if not extension.startswith("."):
        extension = f".{extension}"
    
    # Ungültige Zeichen entfernen
    dokumenttyp = dokumenttyp.replace("/", "-").replace("\\", "-")
    kunde = kunde.replace("/", "-").replace("\\", "-")

    # Eindeutige ID generieren
    unique_id = str(uuid.uuid4())[:8]
    return f"{dokumenttyp}_{kunde}_{unique_id}{extension}"