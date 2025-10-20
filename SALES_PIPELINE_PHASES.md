# 🎯 C&D Sales Pipeline - Vollständige Phasen & Smart Actions

## 📋 ÜBERSICHT: 8 HAUPT-PHASEN

```
PHASE 1: Erstkontakt (Lead - 10-20%)
PHASE 2: Qualifizierung (Qualified - 30-40%)
PHASE 3: Aufmaß (Measurement - 50%)
PHASE 4: Angebot (Proposal - 60-70%)
PHASE 5: Auftrag (Order - 80-90%)
PHASE 6: Vorbereitung Montage (Pre-Installation - 90%)
PHASE 7: Montage (Installation - 95%)
PHASE 8: Abschluss & Rechnung (Won - 100%)
```

---

## 🔄 PHASE 1: ERSTKONTAKT (Lead - 10-20%)

**Trigger Intent:** `initial_contact`, `lead`, `first_inquiry`

**Was passiert:**
- Neuer Lead eingetroffen (WEG A oder WEG B)
- Opportunity angelegt mit Status "Lead"
- Erste Kontaktaufnahme erforderlich

**Smart Actions:**
1. 📞 **KONTAKT AUFNEHMEN** (Telefon bevorzugt)
   - Beschreibung: "Kunden telefonisch kontaktieren (bevorzugt)"
   - Action: `contact_phone`
   - Color: primary

2. 📧 **MAIL SENDEN** (Falls Telefon nicht möglich)
   - Beschreibung: "Email an Kunden senden (Fallback)"
   - Action: `contact_email`
   - Color: info

3. 📋 **DATEN VERVOLLSTÄNDIGEN**
   - Beschreibung: "Kundendaten in WeClapp vervollständigen"
   - Action: `complete_data`
   - Color: warning

4. 🤖 **AUTOMATISCHE ANTWORT** (Optional, später)
   - Beschreibung: "Automatische Erstantwort senden"
   - Action: `auto_reply`
   - Color: secondary
   - Note: "Kann später eingebaut werden"

**Expected Outcome:**
- Task: "Kunden kontaktieren (Telefon)"
- Opportunity: Lead → Qualifiziert (wenn Kontakt erfolgreich)

---

## 🔍 PHASE 2: QUALIFIZIERUNG (Qualified - 30-40%)

**Trigger Intent:** `qualification`, `data_collection`, `price_inquiry`

**Was passiert:**
- Erste Kontaktaufnahme erfolgreich
- Kundenbedarf erfassen
- Entscheidung: Richtpreis vs. Aufmaß

**Smart Actions:**
1. 💶 **RICHTPREIS ERSTELLEN**
   - Beschreibung: "Groben Richtpreis kalkulieren und senden"
   - Action: `create_rough_price`
   - Color: info

2. 📋 **DATEN AUFNEHMEN**
   - Beschreibung: "Detaillierte Projektdaten erfassen"
   - Action: `collect_data`
   - Color: primary

3. 📅 **AUFMASS TERMINIEREN**
   - Beschreibung: "Termin für Aufmaß vor Ort vereinbaren"
   - Action: `schedule_measurement`
   - Color: warning

4. 📄 **UNTERLAGEN PRÜFEN**
   - Beschreibung: "Vorhandene Unterlagen prüfen (evtl. ohne Aufmaß)"
   - Action: `check_documents`
   - Color: secondary

**Expected Outcome:**
- Opportunity: Qualifiziert → Measurement (40% → 50%)
- Task: "Aufmaßtermin vereinbaren" oder "Richtpreis erstellen"

---

## 📐 PHASE 3: AUFMASS (Measurement - 50%)

**Trigger Intent:** `measurement`, `site_visit`, `aufmass`

**Was passiert:**
- Aufmaßtermin vereinbart
- Vor-Ort-Besichtigung durchgeführt
- Genaue Maße erfasst

**Smart Actions:**
1. 📅 **TERMIN BESTÄTIGEN**
   - Beschreibung: "Aufmaßtermin mit Kunden bestätigen"
   - Action: `confirm_measurement`
   - Color: primary

2. 📝 **AUFMASS ERFASSEN**
   - Beschreibung: "Maße und Details vor Ort dokumentieren"
   - Action: `record_measurement`
   - Color: info

3. 📸 **FOTOS HOCHLADEN**
   - Beschreibung: "Fotos vom Objekt in WeClapp hochladen"
   - Action: `upload_photos`
   - Color: secondary

4. 💰 **ANGEBOT VORBEREITEN**
   - Beschreibung: "Kalkulationsgrundlage für Angebot erstellen"
   - Action: `prepare_quote`
   - Color: success

**Expected Outcome:**
- Opportunity: Measurement → Proposal (50% → 60%)
- Task: "Angebot erstellen basierend auf Aufmaß"

---

## 💰 PHASE 4: ANGEBOT (Proposal - 60-70%)

**Trigger Intent:** `quote`, `proposal`, `angebot`, `offer`

**Was passiert:**
- Angebot kalkuliert
- Angebot erstellt (manuell oder automatisch)
- Angebot per Mail versendet

**Smart Actions:**
1. 📊 **ANGEBOT ERSTELLEN**
   - Beschreibung: "Detailliertes Angebot in WeClapp erstellen"
   - Action: `create_quote`
   - Color: create

2. 🤖 **ANGEBOT AUTOMATISCH GENERIEREN** (Optional, später)
   - Beschreibung: "Angebot automatisch aus Aufmaßdaten generieren"
   - Action: `auto_generate_quote`
   - Color: info
   - Note: "Später vorgesehen"

3. 📧 **ANGEBOT VERSENDEN**
   - Beschreibung: "Angebot per Mail an Kunden senden"
   - Action: `send_quote`
   - Color: primary

4. 📞 **NACHFASSEN**
   - Beschreibung: "Kunde zu Angebot kontaktieren (Follow-up)"
   - Action: `follow_up_quote`
   - Color: warning

**Expected Outcome:**
- Opportunity: Proposal → Order (70% → 80%)
- Task: "Angebot nachfassen in 3-5 Tagen"

---

## ✅ PHASE 5: AUFTRAG (Order - 80-90%)

**Trigger Intent:** `order`, `auftrag`, `auftragserteilung`

**Was passiert:**
- Kunde erteilt Auftrag
- Auftragsbestätigung erforderlich
- Lieferantenbestellung notwendig
- Anzahlung fällig

**Smart Actions:** ✅ **BEREITS IMPLEMENTIERT**
1. ✅ **AUFTRAG ANLEGEN**
   - Beschreibung: "Kundenauftrag in WeClapp erstellen"
   - Action: `create_order`
   - Color: create

2. 📦 **LIEFERANT BESTELLEN**
   - Beschreibung: "Material beim Lieferanten bestellen"
   - Action: `order_supplier`
   - Color: info

3. 📄 **AB VERSENDEN**
   - Beschreibung: "Auftragsbestätigung an Kunden senden"
   - Action: `send_order_confirmation`
   - Color: primary

4. 💶 **ANZAHLUNGSRECHNUNG**
   - Beschreibung: "Anzahlungsrechnung erstellen (30-50%)"
   - Action: `create_advance_invoice`
   - Color: success

5. 🔧 **MONTAGE TERMINIEREN**
   - Beschreibung: "Montagetermin mit Kunde vereinbaren"
   - Action: `schedule_installation`
   - Color: warning

**Expected Outcome:**
- Opportunity: Order → Pre-Installation (90%)
- Task: "Material bestellen und Montagetermin vereinbaren"

---

## 🔨 PHASE 6: VORBEREITUNG MONTAGE (Pre-Installation - 90%)

**Trigger Intent:** `pre_installation`, `preparation`, `vorbereitung`

**Was passiert:**
- Material bestellt und geliefert
- Montagetermin vereinbart
- Lieferschein vorbereiten
- Leistungsnachweis vorbereiten

**Smart Actions:** 🆕 **NEU ZU IMPLEMENTIEREN**
1. 📋 **LIEFERSCHEIN VORBEREITEN**
   - Beschreibung: "Lieferschein automatisch vorbereiten"
   - Action: `prepare_delivery_note`
   - Color: info

2. 📝 **LEISTUNGSNACHWEIS VORBEREITEN**
   - Beschreibung: "Leistungsnachweis-Dokument vorbereiten"
   - Action: `prepare_service_proof`
   - Color: info

3. 📦 **MATERIAL PRÜFEN**
   - Beschreibung: "Materiallieferung prüfen und bestätigen"
   - Action: `check_material`
   - Color: primary

4. 📅 **MONTAGE BESTÄTIGEN**
   - Beschreibung: "Montagetermin final mit Kunde bestätigen"
   - Action: `confirm_installation`
   - Color: warning

**Expected Outcome:**
- Opportunity: Pre-Installation → Installation (90% → 95%)
- Task: "Montage durchführen am [Datum]"

---

## 🔧 PHASE 7: MONTAGE (Installation - 95%)

**Trigger Intent:** `installation`, `montage`, `baustellentermin`

**Was passiert:**
- Montage durchgeführt
- Lieferschein unterschrieben
- Leistungsnachweis unterschrieben
- Abnahme durch Kunde

**Smart Actions:** 🆕 **NEU ZU IMPLEMENTIEREN**
1. ✅ **MONTAGE ABSCHLIESSEN**
   - Beschreibung: "Montage als abgeschlossen markieren"
   - Action: `complete_installation`
   - Color: success

2. 📋 **LIEFERSCHEIN ZURÜCK**
   - Beschreibung: "Unterschriebenen Lieferschein erfassen"
   - Action: `upload_delivery_note`
   - Color: primary

3. 📝 **LEISTUNGSNACHWEIS ZURÜCK**
   - Beschreibung: "Unterschriebenen Leistungsnachweis erfassen"
   - Action: `upload_service_proof`
   - Color: primary

4. 📸 **ABNAHME DOKUMENTIEREN**
   - Beschreibung: "Fotos der fertigen Montage hochladen"
   - Action: `document_completion`
   - Color: info

**Expected Outcome:**
- Opportunity: Installation → Won (95% → 100%)
- Task: "Rechnung erstellen"

---

## 💰 PHASE 8: ABSCHLUSS & RECHNUNG (Won - 100%)

**Trigger Intent:** `invoice`, `rechnung`, `completion`, `abschluss`

**Was passiert:**
- Montage abgeschlossen
- Alle Dokumente zurück
- Rechnung erstellen
- Restbetrag fällig

**Smart Actions:** 🆕 **NEU ZU IMPLEMENTIEREN**
1. 💶 **RECHNUNG ERSTELLEN**
   - Beschreibung: "Schlussrechnung erstellen (Restbetrag)"
   - Action: `create_final_invoice`
   - Color: create

2. 📧 **RECHNUNG VERSENDEN**
   - Beschreibung: "Rechnung per Mail an Kunden senden"
   - Action: `send_invoice`
   - Color: primary

3. 💳 **ZAHLUNG ERFASSEN**
   - Beschreibung: "Zahlungseingang in WeClapp erfassen"
   - Action: `record_payment`
   - Color: success

4. 😊 **FEEDBACK EINHOLEN**
   - Beschreibung: "Kundenfeedback per Mail anfordern"
   - Action: `request_feedback`
   - Color: info

5. ⭐ **BEWERTUNG ANFORDERN**
   - Beschreibung: "Google/Bewertung anfordern"
   - Action: `request_review`
   - Color: secondary

**Expected Outcome:**
- Opportunity: Won (100%)
- Status: Abgeschlossen
- Task: "Follow-up in 6-12 Monaten (Wartung/Nachbestellung)"

---

## 🔄 AUTOMATISIERUNG (Optional, später)

**Phase 1:** Automatische Erstantwort
**Phase 2:** Automatischer Terminvorschlag
**Phase 4:** Automatische Angebotsgenerierung
**Phase 6:** Automatische Lieferschein/Leistungsnachweis-Generierung
**Phase 8:** Automatische Rechnung nach Montage

---

## 📊 INTENT MAPPING FÜR SMART ACTIONS

```python
# Phase 1: Erstkontakt
"initial_contact" → KONTAKT AUFNEHMEN, MAIL SENDEN, DATEN VERVOLLSTÄNDIGEN

# Phase 2: Qualifizierung
"qualification" → RICHTPREIS, DATEN AUFNEHMEN, AUFMASS TERMINIEREN

# Phase 3: Aufmaß
"measurement" → TERMIN BESTÄTIGEN, AUFMASS ERFASSEN, ANGEBOT VORBEREITEN

# Phase 4: Angebot
"quote", "proposal" → ANGEBOT ERSTELLEN, ANGEBOT VERSENDEN, NACHFASSEN

# Phase 5: Auftrag
"order" → AUFTRAG ANLEGEN, LIEFERANT BESTELLEN, AB VERSENDEN, ANZAHLUNG, MONTAGE TERMINIEREN

# Phase 6: Vorbereitung
"pre_installation" → LIEFERSCHEIN VORBEREITEN, LEISTUNGSNACHWEIS VORBEREITEN, MATERIAL PRÜFEN

# Phase 7: Montage
"installation" → MONTAGE ABSCHLIESSEN, LIEFERSCHEIN ZURÜCK, LEISTUNGSNACHWEIS ZURÜCK

# Phase 8: Abschluss
"invoice", "completion" → RECHNUNG ERSTELLEN, RECHNUNG VERSENDEN, ZAHLUNG ERFASSEN, FEEDBACK
```

---

## ✅ AKTUELLER STATUS

**✅ IMPLEMENTIERT (Deployment 11-16):**
- Phase 5: AUFTRAG (6 Smart Actions)
  - AUFTRAG ANLEGEN
  - LIEFERANT BESTELLEN
  - AB VERSENDEN
  - ANZAHLUNGSRECHNUNG
  - MONTAGE TERMINIEREN
  - IN CRM ÖFFNEN

**🔨 TODO - NÄCHSTE DEPLOYMENTS:**
- Phase 1: ERSTKONTAKT (4 Smart Actions)
- Phase 2: QUALIFIZIERUNG (4 Smart Actions)
- Phase 3: AUFMASS (4 Smart Actions)
- Phase 4: ANGEBOT (4 Smart Actions)
- Phase 6: VORBEREITUNG MONTAGE (4 Smart Actions)
- Phase 7: MONTAGE (4 Smart Actions)
- Phase 8: ABSCHLUSS & RECHNUNG (5 Smart Actions)

**Total: 35+ Smart Actions** für vollständigen Sales Workflow

---

## 🎯 PRIORISIERUNG

**HIGH PRIORITY (Deployment 17):**
1. Phase 1: ERSTKONTAKT (sofort nutzbar)
2. Phase 4: ANGEBOT (häufig benötigt)

**MEDIUM PRIORITY (Deployment 18):**
3. Phase 2: QUALIFIZIERUNG
4. Phase 3: AUFMASS

**LOW PRIORITY (Deployment 19-20):**
5. Phase 6: VORBEREITUNG MONTAGE
6. Phase 7: MONTAGE
7. Phase 8: ABSCHLUSS & RECHNUNG

---

**Erstellt:** 2025-10-21  
**Status:** 📋 Dokumentation für Implementierung  
**Version:** 1.0
