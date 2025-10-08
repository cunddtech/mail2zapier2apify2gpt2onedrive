import pandas as pd

def analyze_status_difference(weclapp_stage: str, gpt_dokumenttyp: str):
    """
    Vergleicht WeClapp-Verkaufsphase mit GPT-Analyse und erkennt Abweichungen.
    Gibt eine strukturierte Analyse zurück. Bei Fehlern wird ein Fallback in Excel gespeichert.
    """

    mapping = {
        "anfrage": "Anfrage",
        "angebot": "Erstes Angebot erstellt",
        "aufmaß": "Aufmaß",
        "ab": "Auftragsbestätigung Kunde an uns",
        "bestellung": "Bestellung an Lieferanten",
        "montage": "Terminierung Montage",
        "rechnung": "Rechnung",
        "zahlung": "Zahlungseingang",
    }

    # Fallback-Daten initialisieren
    fallback_data = {
        "weclapp_stage": weclapp_stage,
        "gpt_dokumenttyp": gpt_dokumenttyp,
        "gpt_suggestion": "unbekannt",
        "abweichung": False,
        "bemerkung": "Kein Dokumenttyp aus GPT verfügbar"
    }

    try:
        if not gpt_dokumenttyp:
            return fallback_data

        # GPT-Dokumenttyp zu WeClapp-Phase zuordnen
        gpt_expected_stage = mapping.get(gpt_dokumenttyp.lower(), "unbekannt")

        # Abweichung prüfen
        abweichung = (gpt_expected_stage.lower() != weclapp_stage.lower())

        return {
            "weclapp_stage": weclapp_stage,
            "gpt_suggestion": gpt_expected_stage,
            "abweichung": abweichung,
            "bemerkung": "Status weicht ab" if abweichung else "Status konsistent"
        }

    except Exception as e:
        # Fehlerbehandlung und Fallback in Excel speichern
        fallback_data["bemerkung"] = f"Fehler: {str(e)}"
        save_fallback_to_excel([fallback_data])
        return fallback_data


def save_fallback_to_excel(data):
    """
    Speichert die Fallback-Daten in einer Excel-Datei.
    
    Args:
        data (list): Eine Liste von Dictionaries mit den Fallback-Daten.
    """
    try:
        df = pd.DataFrame(data)
        df.to_excel("fallback_status_analysis.xlsx", index=False, engine="openpyxl")
        print("✅ Fallback-Daten wurden in 'fallback_status_analysis.xlsx' gespeichert.")
    except Exception as e:
        print(f"❌ Fehler beim Speichern der Fallback-Daten in Excel: {e}")