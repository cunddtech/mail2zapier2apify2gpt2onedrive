import re
import datetime
import uuid
from modules.utils.debug_log import debug_log

def sanitize_path(text):
    """
    Bereinigt einen Pfad, indem unerlaubte Zeichen ersetzt werden.
    """
    cleaned = re.sub(r"[^\w\d\-./]", "-", text.strip())
    cleaned = re.sub(r"-{3,}", "--", cleaned)  # Maximal zwei Bindestriche
    return cleaned

def generate_folder_and_filenames(context: dict, gpt_result: dict, attachments: list = None) -> dict:
    """
    Generiert Ordnerpfade und Dateinamen basierend auf dem Kontext, den GPT-Ergebnissen und allen Anhängen.
    Gibt für jeden Anhang einen eigenen Dateinamen zurück.
    """
    debug_log("📂 Starte Ordner- und Dateinamensgenerierung...")

    # === 1. Eingabewerte aus Kontext und GPT-Ergebnissen ===
    dokumenttyp = gpt_result.get("dokumenttyp", context.get("dokumenttyp", "unbekannt")).lower()
    kunde = (gpt_result.get("kunde") or context.get("kunde") or "Unbekannt").strip()
    lieferant = (gpt_result.get("lieferant") or context.get("lieferant") or "Unbekannt").strip()
    projekt = (gpt_result.get("projektnummer") or context.get("projekt") or "Unbekannt").strip()
    datum_raw = gpt_result.get("datum_dokument", context.get("datum_dokument", datetime.datetime.now().strftime("%d.%m.%Y")))
    ordnerstruktur = gpt_result.get("ordnerstruktur", "")
    dateiname = gpt_result.get("dateiname", "")

    # Debug: Eingabewerte loggen
    #debug_log(f"Eingabewerte: dokumenttyp={dokumenttyp}, kunde={kunde}, lieferant={lieferant}, projekt={projekt}, datum_raw={datum_raw}")

    # === 2. Datum verarbeiten ===
    try:
        dt = datetime.datetime.strptime(datum_raw[:10], "%Y-%m-%d")
    except:
        try:
            dt = datetime.datetime.strptime(datum_raw, "%d.%m.%Y")
        except:
            dt = datetime.datetime.now()

    datum = dt.strftime('%d.%m.%Y')
    jahr = dt.strftime('%Y')
    monat = dt.strftime('%m')

    # === 3. Dateinamen für alle Anhänge erzeugen ===
    pdf_filenames = []
    if attachments is None:
        attachments = context.get("valid_attachments", [])

    for i, att in enumerate(attachments):
        # Versuche, einen sprechenden Namen zu bauen, sonst fallback
        att_name = att.get("filename") or att.get("name") or f"Anhang_{i+1}"
        id_suffix = str(uuid.uuid4())[:6]
        kunde_clean = sanitize_path(kunde.split(",")[0] if kunde else "Unbekannt")
        dokumenttyp_clean = dokumenttyp.replace("ä", "ae").replace("ü", "ue").replace("ö", "oe").title()
        base_name = f"{dokumenttyp_clean}_{kunde_clean}_{dt.strftime('%Y%m%d')}_{id_suffix}"
        # Wenn mehrere Anhänge, nummerieren
        if len(attachments) > 1:
            base_name += f"_{i+1}"
        pdf_filenames.append(sanitize_path(base_name) + ".pdf")

    # === 4. Ordnerstruktur berechnen ===
    if not ordnerstruktur:
        projekt = sanitize_path(projekt)
        kunde = sanitize_path(kunde)
        lieferant = sanitize_path(lieferant)

        # WICHTIG: Unterscheidung Eingang vs Ausgang!
        if dokumenttyp in ["rechnung", "eingangsrechnung"]:
            ordnerstruktur = f"Scan/Buchhaltung/{jahr}/{monat}/Eingang/{lieferant}"
        elif dokumenttyp in ["ausgangsrechnung"]:
            ordnerstruktur = f"Scan/Buchhaltung/{jahr}/{monat}/Ausgang/{kunde}"
        elif dokumenttyp in ["lieferschein"]:
            ordnerstruktur = f"Scan/Buchhaltung/{jahr}/{monat}/Eingang/{lieferant}"
        elif dokumenttyp in ["angebot", "offer"]:
            ordnerstruktur = f"Scan/Angebote/{kunde}"
        elif projekt.lower() != "unbekannt" and kunde.lower() != "unbekannt":
            ordnerstruktur = f"Scan/Projekte/{kunde}/{projekt}/{dokumenttyp.title()}"
        else:
            # Fallback: Allgemeine Ablage
            ordnerstruktur = f"Scan/Sonstige/{jahr}/{monat}/{dokumenttyp.title()}"

    return {
        "ordnerstruktur": sanitize_path(ordnerstruktur),
        "pdf_filenames": pdf_filenames,
        "datum": datum,
        "dokumenttyp": dokumenttyp,
        "kunde": kunde,
        "projekt": projekt,
        "lieferant": lieferant
    }