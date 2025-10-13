import os

def generate_folder_path(base_folder, kunde, projekt, dokumenttyp, rolle=None, richtung=None, temp_folder="Temp"):
    """
    Generiert einen sicheren Ordnerpfad und erstellt einen Ordner für die Ablage.

    Args:
        base_folder (str): Der Basisordner, z. B. "Scan".
        kunde (str): Der Name des Kunden.
        projekt (str): Der Name des Projekts.
        dokumenttyp (str): Der Dokumenttyp (z. B. Rechnung, Lieferschein).
        rolle (str): Die Rolle (z. B. "Vertrieb", "Einkauf") (optional).
        richtung (str): Die Richtung (z. B. "Eingang", "Ausgang") (optional).
        temp_folder (str): Der Name des temporären Ordners (Standard: "Temp").

    Returns:
        str: Der vollständige Pfad zum Zielordner.
    """
    # Pfade bereinigen
    safe_kunde = kunde.replace("/", "-").strip() if kunde else "Unbekannt"
    safe_projekt = projekt.replace("/", "-").strip() if projekt else "Allgemein"
    safe_typ = dokumenttyp.replace("/", "-").strip() if dokumenttyp else "Sonstiges"
    safe_rolle = rolle.replace("/", "-").strip() if rolle else "Allgemein"
    safe_richtung = richtung.replace("/", "-").strip() if richtung else "Neutral"

    # Zielordnerpfad generieren
    folder_path = os.path.join(base_folder, safe_kunde, safe_projekt, safe_typ, safe_rolle, safe_richtung)
    os.makedirs(folder_path, exist_ok=True)

    return folder_path