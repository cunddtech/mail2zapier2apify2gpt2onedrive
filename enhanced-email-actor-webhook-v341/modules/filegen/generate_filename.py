# filepath: /Users/cdtechgmbh/Documents/lokal_test/apify_debug_template/actor_files/modules/filegen/generate_filename.py
def generate_filename(dokumenttyp, kunde, datum, projekt, extension=".pdf"):
    """
    Generiert einen finalen Dateinamen basierend auf den Eingaben.

    Args:
        dokumenttyp (str): Der Dokumenttyp (z. B. Rechnung, Lieferschein).
        kunde (str): Der Name des Kunden.
        datum (str): Das Datum im Format YYYY-MM-DD.
        projekt (str): Der Name des Projekts.
        extension (str): Die Dateiendung (z. B. ".pdf").

    Returns:
        str: Der generierte Dateiname.
    """
    return f"{dokumenttyp}_{kunde}_{datum}_{projekt}{extension}".replace(" ", "_")