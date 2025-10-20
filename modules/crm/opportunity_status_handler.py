"""
Modul: opportunity_status_handler.py
Verantwortlich für: WeClapp Opportunity Status Abfrage und Phase-basierte Smart Actions

FUNKTIONEN:
1. Opportunity Status aus WeClapp abrufen
2. Phase-spezifische Smart Actions generieren basierend auf aktuellem Status
3. Opportunity Status aktualisieren nach Action

SALES PIPELINE PHASEN:
- Lead (10-20%) → Erstkontakt Actions
- Qualified (30-40%) → Qualifizierung Actions
- Measurement (50%) → Aufmaß Actions
- Proposal (60-70%) → Angebot Actions
- Order (80-90%) → Auftrag Actions (BEREITS IMPLEMENTIERT)
- Pre-Installation (90%) → Vorbereitung Actions
- Installation (95%) → Montage Actions
- Won (100%) → Abschluss Actions
"""

import os
import requests
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# WeClapp API Configuration
WECLAPP_API_KEY = os.environ.get("WECLAPP_API_KEY", "")
WECLAPP_TENANT = os.environ.get("WECLAPP_TENANT", "cundd")
WECLAPP_BASE_URL = f"https://{WECLAPP_TENANT}.weclapp.com/webapp/api/v1"

# WeClapp Sales Stage Mapping (WeClapp internal IDs)
WECLAPP_STAGES = {
    "LEAD": "Lead",
    "QUALIFIED": "Qualified",
    "MEASUREMENT": "Measurement",  # Custom stage
    "PROPOSAL": "Proposal",
    "ORDER": "Order",
    "PRE_INSTALLATION": "Pre-Installation",  # Custom stage
    "INSTALLATION": "Installation",  # Custom stage
    "WON": "Won",
    "LOST": "Lost"
}


def get_opportunity_by_contact(contact_id: int) -> Optional[Dict[str, Any]]:
    """
    Holt aktuelle Opportunity für einen Kontakt aus WeClapp
    
    Args:
        contact_id: WeClapp Party/Contact ID
        
    Returns:
        Dict mit Opportunity-Daten oder None
    """
    if not WECLAPP_API_KEY:
        logger.warning("⚠️ WECLAPP_API_KEY not configured")
        return None
    
    try:
        headers = {
            "AuthenticationToken": WECLAPP_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Suche nach offenen Opportunities für diesen Kontakt
        url = f"{WECLAPP_BASE_URL}/opportunity"
        params = {
            "partyId-eq": contact_id,
            "status-eq": "OPEN",  # Nur offene Opportunities
            "pageSize": 1,
            "sort": "-lastModifiedDate"  # Neueste zuerst
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("result") and len(data["result"]) > 0:
                opp = data["result"][0]
                logger.info(f"✅ Opportunity gefunden: ID={opp.get('id')}, Stage={opp.get('salesStage')}, Probability={opp.get('probability')}%")
                return opp
            else:
                logger.info(f"ℹ️ Keine offene Opportunity für Contact {contact_id}")
                return None
        else:
            logger.error(f"❌ WeClapp API Error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error fetching opportunity: {str(e)}")
        return None


def get_smart_actions_for_stage(
    sales_stage: str,
    contact_id: int,
    opportunity_id: Optional[int] = None,
    intent: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Generiert phase-spezifische Smart Actions basierend auf Opportunity Stage
    
    Args:
        sales_stage: WeClapp Sales Stage (Lead, Qualified, Proposal, etc.)
        contact_id: WeClapp Contact ID
        opportunity_id: WeClapp Opportunity ID (optional)
        intent: AI-erkannte Intent (optional für zusätzliche Actions)
        
    Returns:
        List von Smart Action Dictionaries
    """
    actions = []
    contact_url = f"https://cundd.weclapp.com/webapp/view/party/{contact_id}"
    opp_url = f"https://cundd.weclapp.com/webapp/view/opportunity/{opportunity_id}" if opportunity_id else contact_url
    
    # PHASE 1: LEAD (10-20%) - Erstkontakt
    if sales_stage in ["Lead", "LEAD"]:
        actions.extend([
            {
                "action": "contact_phone",
                "label": "📞 KONTAKT AUFNEHMEN",
                "description": "Kunden telefonisch kontaktieren (bevorzugt)",
                "color": "primary",
                "url": contact_url
            },
            {
                "action": "contact_email",
                "label": "📧 MAIL SENDEN",
                "description": "Email an Kunden senden (Fallback)",
                "color": "info",
                "url": contact_url
            },
            {
                "action": "complete_data",
                "label": "📋 DATEN VERVOLLSTÄNDIGEN",
                "description": "Kundendaten in WeClapp vervollständigen",
                "color": "warning",
                "url": contact_url
            }
        ])
    
    # PHASE 2: QUALIFIED (30-40%) - Qualifizierung
    elif sales_stage in ["Qualified", "QUALIFIED"]:
        actions.extend([
            {
                "action": "create_rough_price",
                "label": "💶 RICHTPREIS ERSTELLEN",
                "description": "Groben Richtpreis kalkulieren und senden",
                "color": "info",
                "url": opp_url
            },
            {
                "action": "collect_data",
                "label": "📋 DATEN AUFNEHMEN",
                "description": "Detaillierte Projektdaten erfassen",
                "color": "primary",
                "url": contact_url
            },
            {
                "action": "schedule_measurement",
                "label": "📅 AUFMASS TERMINIEREN",
                "description": "Termin für Aufmaß vor Ort vereinbaren",
                "color": "warning",
                "url": contact_url
            },
            {
                "action": "check_documents",
                "label": "📄 UNTERLAGEN PRÜFEN",
                "description": "Vorhandene Unterlagen prüfen (evtl. ohne Aufmaß)",
                "color": "secondary",
                "url": opp_url
            }
        ])
    
    # PHASE 3: MEASUREMENT (50%) - Aufmaß
    elif sales_stage in ["Measurement", "MEASUREMENT"]:
        actions.extend([
            {
                "action": "confirm_measurement",
                "label": "📅 TERMIN BESTÄTIGEN",
                "description": "Aufmaßtermin mit Kunden bestätigen",
                "color": "primary",
                "url": contact_url
            },
            {
                "action": "record_measurement",
                "label": "📝 AUFMASS ERFASSEN",
                "description": "Maße und Details vor Ort dokumentieren",
                "color": "info",
                "url": opp_url
            },
            {
                "action": "upload_photos",
                "label": "📸 FOTOS HOCHLADEN",
                "description": "Fotos vom Objekt in WeClapp hochladen",
                "color": "secondary",
                "url": opp_url
            },
            {
                "action": "prepare_quote",
                "label": "💰 ANGEBOT VORBEREITEN",
                "description": "Kalkulationsgrundlage für Angebot erstellen",
                "color": "success",
                "url": opp_url
            }
        ])
    
    # PHASE 4: PROPOSAL (60-70%) - Angebot
    elif sales_stage in ["Proposal", "PROPOSAL"]:
        actions.extend([
            {
                "action": "create_quote",
                "label": "📊 ANGEBOT ERSTELLEN",
                "description": "Detailliertes Angebot in WeClapp erstellen",
                "color": "create",
                "url": opp_url
            },
            {
                "action": "send_quote",
                "label": "📧 ANGEBOT VERSENDEN",
                "description": "Angebot per Mail an Kunden senden",
                "color": "primary",
                "url": opp_url
            },
            {
                "action": "follow_up_quote",
                "label": "📞 NACHFASSEN",
                "description": "Kunde zu Angebot kontaktieren (Follow-up)",
                "color": "warning",
                "url": contact_url
            }
        ])
    
    # PHASE 5: ORDER (80-90%) - Auftrag (BEREITS IMPLEMENTIERT)
    elif sales_stage in ["Order", "ORDER"]:
        actions.extend([
            {
                "action": "create_order",
                "label": "✅ AUFTRAG ANLEGEN",
                "description": "Kundenauftrag in WeClapp erstellen",
                "color": "create",
                "url": opp_url
            },
            {
                "action": "order_supplier",
                "label": "📦 LIEFERANT BESTELLEN",
                "description": "Material beim Lieferanten bestellen",
                "color": "info",
                "url": opp_url
            },
            {
                "action": "send_order_confirmation",
                "label": "📄 AB VERSENDEN",
                "description": "Auftragsbestätigung an Kunden senden",
                "color": "primary",
                "url": opp_url
            },
            {
                "action": "create_advance_invoice",
                "label": "💶 ANZAHLUNGSRECHNUNG",
                "description": "Anzahlungsrechnung erstellen (30-50%)",
                "color": "success",
                "url": opp_url
            },
            {
                "action": "schedule_installation",
                "label": "🔧 MONTAGE TERMINIEREN",
                "description": "Montagetermin mit Kunde vereinbaren",
                "color": "warning",
                "url": contact_url
            }
        ])
    
    # PHASE 6: PRE-INSTALLATION (90%) - Vorbereitung Montage
    elif sales_stage in ["Pre-Installation", "PRE_INSTALLATION"]:
        actions.extend([
            {
                "action": "prepare_delivery_note",
                "label": "📋 LIEFERSCHEIN VORBEREITEN",
                "description": "Lieferschein automatisch vorbereiten",
                "color": "info",
                "url": opp_url
            },
            {
                "action": "prepare_service_proof",
                "label": "📝 LEISTUNGSNACHWEIS VORBEREITEN",
                "description": "Leistungsnachweis-Dokument vorbereiten",
                "color": "info",
                "url": opp_url
            },
            {
                "action": "check_material",
                "label": "📦 MATERIAL PRÜFEN",
                "description": "Materiallieferung prüfen und bestätigen",
                "color": "primary",
                "url": opp_url
            },
            {
                "action": "confirm_installation",
                "label": "📅 MONTAGE BESTÄTIGEN",
                "description": "Montagetermin final mit Kunde bestätigen",
                "color": "warning",
                "url": contact_url
            }
        ])
    
    # PHASE 7: INSTALLATION (95%) - Montage
    elif sales_stage in ["Installation", "INSTALLATION"]:
        actions.extend([
            {
                "action": "complete_installation",
                "label": "✅ MONTAGE ABSCHLIESSEN",
                "description": "Montage als abgeschlossen markieren",
                "color": "success",
                "url": opp_url
            },
            {
                "action": "upload_delivery_note",
                "label": "📋 LIEFERSCHEIN ZURÜCK",
                "description": "Unterschriebenen Lieferschein erfassen",
                "color": "primary",
                "url": opp_url
            },
            {
                "action": "upload_service_proof",
                "label": "📝 LEISTUNGSNACHWEIS ZURÜCK",
                "description": "Unterschriebenen Leistungsnachweis erfassen",
                "color": "primary",
                "url": opp_url
            },
            {
                "action": "document_completion",
                "label": "📸 ABNAHME DOKUMENTIEREN",
                "description": "Fotos der fertigen Montage hochladen",
                "color": "info",
                "url": opp_url
            }
        ])
    
    # PHASE 8: WON (100%) - Abschluss & Rechnung
    elif sales_stage in ["Won", "WON"]:
        actions.extend([
            {
                "action": "create_final_invoice",
                "label": "💶 RECHNUNG ERSTELLEN",
                "description": "Schlussrechnung erstellen (Restbetrag)",
                "color": "create",
                "url": opp_url
            },
            {
                "action": "send_invoice",
                "label": "📧 RECHNUNG VERSENDEN",
                "description": "Rechnung per Mail an Kunden senden",
                "color": "primary",
                "url": opp_url
            },
            {
                "action": "record_payment",
                "label": "💳 ZAHLUNG ERFASSEN",
                "description": "Zahlungseingang in WeClapp erfassen",
                "color": "success",
                "url": opp_url
            },
            {
                "action": "request_feedback",
                "label": "😊 FEEDBACK EINHOLEN",
                "description": "Kundenfeedback per Mail anfordern",
                "color": "info",
                "url": contact_url
            },
            {
                "action": "request_review",
                "label": "⭐ BEWERTUNG ANFORDERN",
                "description": "Google/Bewertung anfordern",
                "color": "secondary",
                "url": contact_url
            }
        ])
    
    # Fallback: Wenn Stage unbekannt, generische Actions
    else:
        logger.warning(f"⚠️ Unknown sales stage: {sales_stage}, using generic actions")
        actions.extend([
            {
                "action": "contact_phone",
                "label": "📞 KUNDE ANRUFEN",
                "description": "Kunde telefonisch kontaktieren",
                "color": "primary",
                "url": contact_url
            },
            {
                "action": "send_email",
                "label": "📧 EMAIL SENDEN",
                "description": "Email an Kunden senden",
                "color": "info",
                "url": contact_url
            }
        ])
    
    # Immer: "IN CRM ÖFFNEN" Button
    actions.append({
        "action": "view_in_crm",
        "label": "📋 IN CRM ÖFFNEN",
        "description": f"Opportunity in WeClapp öffnen",
        "color": "secondary",
        "url": opp_url if opportunity_id else contact_url
    })
    
    logger.info(f"✅ Generated {len(actions)} smart actions for stage: {sales_stage}")
    return actions


def update_opportunity_stage(
    opportunity_id: int,
    new_stage: str,
    probability: Optional[int] = None
) -> bool:
    """
    Aktualisiert Opportunity Stage in WeClapp nach Smart Action
    
    Args:
        opportunity_id: WeClapp Opportunity ID
        new_stage: Neuer Sales Stage (z.B. "Proposal", "Order")
        probability: Neue Wahrscheinlichkeit in % (optional)
        
    Returns:
        True wenn erfolgreich, sonst False
    """
    if not WECLAPP_API_KEY:
        logger.warning("⚠️ WECLAPP_API_KEY not configured")
        return False
    
    try:
        headers = {
            "AuthenticationToken": WECLAPP_API_KEY,
            "Content-Type": "application/json"
        }
        
        url = f"{WECLAPP_BASE_URL}/opportunity/id/{opportunity_id}"
        
        update_data = {
            "salesStage": new_stage
        }
        
        if probability is not None:
            update_data["probability"] = probability
        
        response = requests.put(url, headers=headers, json=update_data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Opportunity {opportunity_id} updated: Stage={new_stage}, Probability={probability}%")
            return True
        else:
            logger.error(f"❌ WeClapp API Error updating opportunity: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error updating opportunity: {str(e)}")
        return False


# Stage Progression Mapping (für automatische Updates)
STAGE_PROGRESSION = {
    "Lead": {"next": "Qualified", "probability": 40},
    "Qualified": {"next": "Measurement", "probability": 50},
    "Measurement": {"next": "Proposal", "probability": 60},
    "Proposal": {"next": "Order", "probability": 80},
    "Order": {"next": "Pre-Installation", "probability": 90},
    "Pre-Installation": {"next": "Installation", "probability": 95},
    "Installation": {"next": "Won", "probability": 100}
}


def progress_opportunity_stage(opportunity_id: int, current_stage: str) -> bool:
    """
    Bewegt Opportunity zur nächsten Phase in der Pipeline
    
    Args:
        opportunity_id: WeClapp Opportunity ID
        current_stage: Aktueller Sales Stage
        
    Returns:
        True wenn erfolgreich, sonst False
    """
    if current_stage in STAGE_PROGRESSION:
        next_stage_info = STAGE_PROGRESSION[current_stage]
        return update_opportunity_stage(
            opportunity_id,
            next_stage_info["next"],
            next_stage_info["probability"]
        )
    else:
        logger.warning(f"⚠️ No progression defined for stage: {current_stage}")
        return False
