# /test/simulate_apify_result.py

import json

# Beispiel-Dataset (kann natürlich angepasst oder erweitert werden)
example_dataset = [
    {
        "dokumenttyp": "Rechnung",
        "kunde": "Müller GmbH",
        "projekt": "Garage Frankfurt",
        "gesamtbetrag": "4.572,89 €",
        "rechnungsnummer": "RE-2025-0425",
        "rechnungsdatum": "2025-04-25",
        "zahlungsziel": "2025-05-25",
        "positionen": [
            { "beschreibung": "Industrietor 4000x4000 mm", "menge": 1, "einzelpreis": "3.900,00 €" },
            { "beschreibung": "Montagepauschale", "menge": 1, "einzelpreis": "500,00 €" },
            { "beschreibung": "Transportkosten", "menge": 1, "einzelpreis": "172,89 €" }
        ],
        "kontakt": {
            "name": "Max Mustermann",
            "telefon": "+49 721 1234567",
            "email": "max.mustermann@mueller-gmbh.de"
        },
        "notizen": "Kunde wünscht RAL 7016 anthrazitgrau."
    }
]

def main():
    print("[SIMULATED RESULT] Analyse-Ergebnis:")
    print(json.dumps(example_dataset, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()