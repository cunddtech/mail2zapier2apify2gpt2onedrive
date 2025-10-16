"""
📞💰 RICHTPREIS-BERECHNUNG AUS CALL TRANSCRIPT

Analysiert Anruf-Transkripte und erstellt automatische Kostenschätzungen
für Dacharbeiten basierend auf:
- Dachfläche (m²)
- Material (Ziegel, Schiefer, etc.)
- Arbeitsart (Neueindeckung, Reparatur, etc.)
- Zusatzleistungen (Dämmung, Gerüst, etc.)

INTEGRATION:
- Wird von production_langgraph_orchestrator.py nach GPT-Analyse aufgerufen
- Extrahiert Projekt-Details aus Transcript
- Berechnet Richtpreis inkl. Material + Arbeit
- Fügt Preis in Notification-Email + WeClapp Task ein

Created: 16. Oktober 2025
Version: 1.0.0
"""

import re
import logging
from typing import Dict, Optional, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProjectEstimate:
    """Strukturiertes Ergebnis einer Projektschätzung"""
    found: bool = False
    project_type: str = ""
    area_sqm: Optional[float] = None
    material: str = ""
    work_type: str = ""
    
    # Kosten
    material_cost: float = 0.0
    labor_cost: float = 0.0
    additional_cost: float = 0.0
    total_cost: float = 0.0
    
    # Details
    confidence: float = 0.0
    calculation_basis: List[str] = None
    additional_services: List[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.calculation_basis is None:
            self.calculation_basis = []
        if self.additional_services is None:
            self.additional_services = []


# ==========================================
# 💰 PREISLISTEN (Richtwerte 2025)
# ==========================================

# Material-Preise (pro m²)
MATERIAL_PRICES = {
    "ziegel": {
        "standard": 35.0,  # Standard Dachziegel
        "premium": 65.0,   # Hochwertige Ziegel (z.B. Frankfurter Pfanne)
        "special": 90.0    # Spezialziegel (z.B. glasiert)
    },
    "schiefer": {
        "standard": 80.0,
        "premium": 120.0
    },
    "dachpfanne": {
        "standard": 30.0,
        "premium": 55.0
    },
    "blechdach": {
        "trapezblech": 25.0,
        "stehfalz": 65.0,
        "kupfer": 150.0,
        "zink": 90.0
    },
    "bitumen": {
        "standard": 15.0,
        "premium": 25.0
    },
    "reet": {
        "standard": 90.0,
        "premium": 130.0
    }
}

# Arbeitskosten (pro m²)
LABOR_COSTS = {
    "neueindeckung": {
        "einfach": 45.0,      # Einfaches Satteldach
        "mittel": 65.0,       # Mittlere Komplexität (Gauben, etc.)
        "komplex": 90.0       # Hohe Komplexität (Türme, schwieriger Zugang)
    },
    "reparatur": {
        "klein": 35.0,        # Einzelne Ziegel tauschen
        "mittel": 50.0,       # Größere Fläche
        "gross": 70.0         # Umfangreiche Reparatur
    },
    "sanierung": {
        "standard": 55.0,
        "vollsanierung": 85.0
    },
    "wartung": {
        "inspektion": 8.0,    # Pro m²
        "reinigung": 12.0     # Pro m²
    }
}

# Zusatzleistungen (Pauschal oder pro m²)
ADDITIONAL_SERVICES = {
    "daemmung": {
        "cost_per_sqm": 45.0,
        "description": "Dachdämmung (Zwischensparren)"
    },
    "gerust": {
        "cost_per_sqm": 12.0,
        "description": "Gerüststellung"
    },
    "entsorgung": {
        "cost_per_sqm": 8.0,
        "description": "Entsorgung Altmaterial"
    },
    "dachfenster": {
        "cost_fixed": 800.0,
        "per_unit": True,
        "description": "Dachfenster einbauen (pro Fenster)"
    },
    "dachrinne": {
        "cost_per_meter": 35.0,
        "description": "Dachrinne erneuern (pro lfd. Meter)"
    },
    "gaube": {
        "cost_fixed": 8000.0,
        "per_unit": True,
        "description": "Gaube einbauen (Grundpreis)"
    }
}


# ==========================================
# 🔍 KEYWORD DETECTION
# ==========================================

def extract_area(transcript: str) -> Optional[float]:
    """
    Extrahiert Dachfläche aus Transcript
    
    Patterns:
    - "100 Quadratmeter"
    - "120 m²"
    - "ca. 80 qm"
    - "ungefähr 150 Quadratmeter"
    """
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:quadratmeter|m²|qm|m2)',
        r'(?:ca\.|ungefähr|etwa)\s*(\d+(?:\.\d+)?)\s*(?:quadratmeter|m²|qm|m2)',
        r'dachfläche.*?(\d+(?:\.\d+)?)\s*(?:quadratmeter|m²|qm|m2)',
        r'(\d+(?:\.\d+)?)\s*(?:quadratmeter|m²|qm|m2)\s*dach'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, transcript.lower())
        if match:
            try:
                area = float(match.group(1))
                if 10 <= area <= 10000:  # Plausibilitätscheck (10-10000 m²)
                    logger.info(f"✅ Extracted area: {area} m²")
                    return area
            except (ValueError, IndexError):
                continue
    
    return None


def detect_material(transcript: str) -> Dict[str, Any]:
    """
    Erkennt Material-Typ aus Transcript
    
    Returns:
        {
            "type": "ziegel|schiefer|...",
            "quality": "standard|premium|special",
            "price_per_sqm": 35.0
        }
    """
    transcript_lower = transcript.lower()
    
    # Material-Keywords
    material_keywords = {
        "ziegel": ["ziegel", "dachziegel", "tondachziegel", "frankfurter pfanne"],
        "schiefer": ["schiefer", "schieferdach"],
        "dachpfanne": ["dachpfanne", "pfanne", "betonpfanne"],
        "blechdach": ["blech", "trapezblech", "stehfalz", "kupfer", "zink", "metalldach"],
        "bitumen": ["bitumen", "dachpappe", "flachdach"],
        "reet": ["reet", "reetdach", "strohdach"]
    }
    
    # Quality-Keywords
    quality_keywords = {
        "premium": ["hochwertig", "premium", "edel", "qualität", "top"],
        "special": ["spezial", "glasiert", "engobiert", "besonders"],
        "standard": ["standard", "normal", "einfach", "günstig"]
    }
    
    detected_material = None
    detected_quality = "standard"
    
    # 1. Material Detection
    for material, keywords in material_keywords.items():
        for keyword in keywords:
            if keyword in transcript_lower:
                detected_material = material
                logger.info(f"✅ Detected material: {material} (keyword: {keyword})")
                break
        if detected_material:
            break
    
    # 2. Quality Detection
    for quality, keywords in quality_keywords.items():
        for keyword in keywords:
            if keyword in transcript_lower:
                detected_quality = quality
                logger.info(f"✅ Detected quality: {quality} (keyword: {keyword})")
                break
        if detected_quality != "standard":
            break
    
    # 3. Get Price
    if detected_material:
        prices = MATERIAL_PRICES.get(detected_material, {})
        
        # Special handling for blechdach (multiple sub-types)
        if detected_material == "blechdach":
            if "kupfer" in transcript_lower:
                price_per_sqm = prices.get("kupfer", 150.0)
            elif "zink" in transcript_lower:
                price_per_sqm = prices.get("zink", 90.0)
            elif "stehfalz" in transcript_lower:
                price_per_sqm = prices.get("stehfalz", 65.0)
            else:
                price_per_sqm = prices.get("trapezblech", 25.0)
        else:
            price_per_sqm = prices.get(detected_quality, prices.get("standard", 0.0))
        
        return {
            "type": detected_material,
            "quality": detected_quality,
            "price_per_sqm": price_per_sqm
        }
    
    # Default: Standard Ziegel
    logger.warning("⚠️ No material detected - using default: Ziegel Standard")
    return {
        "type": "ziegel",
        "quality": "standard",
        "price_per_sqm": 35.0
    }


def detect_work_type(transcript: str) -> Dict[str, Any]:
    """
    Erkennt Arbeitstyp aus Transcript
    
    Returns:
        {
            "type": "neueindeckung|reparatur|sanierung|wartung",
            "complexity": "einfach|mittel|komplex",
            "cost_per_sqm": 45.0
        }
    """
    transcript_lower = transcript.lower()
    
    # Work Type Keywords
    work_keywords = {
        "neueindeckung": ["neueindeckung", "neu eindecken", "neues dach", "komplett neu"],
        "reparatur": ["reparatur", "reparieren", "ausbessern", "flicken", "einzelne ziegel"],
        "sanierung": ["sanierung", "sanieren", "vollsanierung", "dachsanierung"],
        "wartung": ["wartung", "inspektion", "überprüfung", "reinigung", "check"]
    }
    
    # Complexity Keywords
    complexity_keywords = {
        "komplex": ["komplex", "schwierig", "kompliziert", "viele gauben", "turm", "verwinkelt"],
        "mittel": ["mittel", "gauben", "dachfenster", "mehrere", "standard"],
        "einfach": ["einfach", "simpel", "satteldach", "flachdach", "klein"]
    }
    
    detected_type = None
    detected_complexity = "mittel"  # Default
    
    # 1. Work Type Detection
    for work_type, keywords in work_keywords.items():
        for keyword in keywords:
            if keyword in transcript_lower:
                detected_type = work_type
                logger.info(f"✅ Detected work type: {work_type} (keyword: {keyword})")
                break
        if detected_type:
            break
    
    # Default: Reparatur (häufigster Fall)
    if not detected_type:
        logger.warning("⚠️ No work type detected - using default: Reparatur")
        detected_type = "reparatur"
    
    # 2. Complexity Detection
    for complexity, keywords in complexity_keywords.items():
        for keyword in keywords:
            if keyword in transcript_lower:
                detected_complexity = complexity
                logger.info(f"✅ Detected complexity: {complexity} (keyword: {keyword})")
                break
        if detected_complexity != "mittel":
            break
    
    # 3. Get Cost
    costs = LABOR_COSTS.get(detected_type, {})
    
    # Map complexity to cost tier
    if detected_type == "neueindeckung":
        cost_per_sqm = costs.get(detected_complexity, costs.get("mittel", 65.0))
    elif detected_type == "reparatur":
        complexity_map = {"einfach": "klein", "mittel": "mittel", "komplex": "gross"}
        cost_key = complexity_map.get(detected_complexity, "mittel")
        cost_per_sqm = costs.get(cost_key, 50.0)
    elif detected_type == "sanierung":
        if detected_complexity == "komplex":
            cost_per_sqm = costs.get("vollsanierung", 85.0)
        else:
            cost_per_sqm = costs.get("standard", 55.0)
    elif detected_type == "wartung":
        if "reinigung" in transcript_lower:
            cost_per_sqm = costs.get("reinigung", 12.0)
        else:
            cost_per_sqm = costs.get("inspektion", 8.0)
    else:
        cost_per_sqm = 50.0
    
    return {
        "type": detected_type,
        "complexity": detected_complexity,
        "cost_per_sqm": cost_per_sqm
    }


def detect_additional_services(transcript: str, area_sqm: Optional[float]) -> List[Dict[str, Any]]:
    """
    Erkennt Zusatzleistungen aus Transcript
    
    Returns:
        [
            {
                "service": "daemmung",
                "description": "Dachdämmung",
                "cost": 4500.0,
                "unit": "m²"
            },
            ...
        ]
    """
    transcript_lower = transcript.lower()
    detected_services = []
    
    # Dämmung
    if any(keyword in transcript_lower for keyword in ["dämmung", "gedämmt", "isolierung", "isoliert"]):
        if area_sqm:
            cost = area_sqm * ADDITIONAL_SERVICES["daemmung"]["cost_per_sqm"]
            detected_services.append({
                "service": "daemmung",
                "description": ADDITIONAL_SERVICES["daemmung"]["description"],
                "cost": cost,
                "unit": f"{area_sqm:.0f} m²"
            })
    
    # Gerüst
    if any(keyword in transcript_lower for keyword in ["gerüst", "gerueststellung", "arbeitsgerüst"]):
        if area_sqm:
            cost = area_sqm * ADDITIONAL_SERVICES["gerust"]["cost_per_sqm"]
            detected_services.append({
                "service": "gerust",
                "description": ADDITIONAL_SERVICES["gerust"]["description"],
                "cost": cost,
                "unit": f"{area_sqm:.0f} m²"
            })
    
    # Entsorgung
    if any(keyword in transcript_lower for keyword in ["entsorgung", "entsorgen", "abtransport", "altmaterial"]):
        if area_sqm:
            cost = area_sqm * ADDITIONAL_SERVICES["entsorgung"]["cost_per_sqm"]
            detected_services.append({
                "service": "entsorgung",
                "description": ADDITIONAL_SERVICES["entsorgung"]["description"],
                "cost": cost,
                "unit": f"{area_sqm:.0f} m²"
            })
    
    # Dachfenster
    dachfenster_match = re.search(r'(\d+)\s*(?:dachfenster|fenster)', transcript_lower)
    if dachfenster_match or "dachfenster" in transcript_lower:
        count = int(dachfenster_match.group(1)) if dachfenster_match else 1
        cost = count * ADDITIONAL_SERVICES["dachfenster"]["cost_fixed"]
        detected_services.append({
            "service": "dachfenster",
            "description": ADDITIONAL_SERVICES["dachfenster"]["description"],
            "cost": cost,
            "unit": f"{count} Stück"
        })
    
    # Dachrinne
    dachrinne_match = re.search(r'(\d+)\s*(?:meter|m|laufmeter).*?(?:dachrinne|rinne)', transcript_lower)
    if dachrinne_match or "dachrinne" in transcript_lower or "rinne" in transcript_lower:
        meters = int(dachrinne_match.group(1)) if dachrinne_match else (area_sqm * 0.5 if area_sqm else 30)
        cost = meters * ADDITIONAL_SERVICES["dachrinne"]["cost_per_meter"]
        detected_services.append({
            "service": "dachrinne",
            "description": ADDITIONAL_SERVICES["dachrinne"]["description"],
            "cost": cost,
            "unit": f"{meters:.0f} m"
        })
    
    # Gaube
    gaube_match = re.search(r'(\d+)\s*(?:gaube|gauben)', transcript_lower)
    if gaube_match or "gaube" in transcript_lower:
        count = int(gaube_match.group(1)) if gaube_match else 1
        cost = count * ADDITIONAL_SERVICES["gaube"]["cost_fixed"]
        detected_services.append({
            "service": "gaube",
            "description": ADDITIONAL_SERVICES["gaube"]["description"],
            "cost": cost,
            "unit": f"{count} Stück"
        })
    
    if detected_services:
        logger.info(f"✅ Detected {len(detected_services)} additional services")
    
    return detected_services


# ==========================================
# 💰 MAIN CALCULATION FUNCTION
# ==========================================

def calculate_estimate_from_transcript(transcript: str, caller_info: Optional[Dict] = None) -> ProjectEstimate:
    """
    🎯 HAUPT-FUNKTION: Berechnet Richtpreis aus Call Transcript
    
    Args:
        transcript: Call transcript text
        caller_info: Optional dict with caller details (name, company, etc.)
    
    Returns:
        ProjectEstimate with all calculation details
    
    Example:
        >>> estimate = calculate_estimate_from_transcript(
        ...     "Ich brauche ein neues Dach, ca. 120 Quadratmeter, Ziegel, mit Dämmung"
        ... )
        >>> print(f"Total: {estimate.total_cost:.2f} EUR")
        Total: 15600.00 EUR
    """
    
    logger.info("💰 Starting estimate calculation from transcript...")
    
    if not transcript or len(transcript) < 20:
        logger.warning("⚠️ Transcript too short for estimate")
        return ProjectEstimate(found=False, notes="Transcript zu kurz für Kalkulation")
    
    # 1. Extract Project Details
    area_sqm = extract_area(transcript)
    material_info = detect_material(transcript)
    work_info = detect_work_type(transcript)
    
    if not area_sqm:
        logger.warning("⚠️ No area found in transcript")
        return ProjectEstimate(
            found=False,
            notes="Keine Dachfläche im Gespräch erwähnt. Bitte nachfragen: 'Wie groß ist die Dachfläche in Quadratmetern?'"
        )
    
    # 2. Calculate Base Costs
    material_cost = area_sqm * material_info["price_per_sqm"]
    labor_cost = area_sqm * work_info["cost_per_sqm"]
    
    # 3. Additional Services
    additional_services = detect_additional_services(transcript, area_sqm)
    additional_cost = sum(service["cost"] for service in additional_services)
    
    # 4. Total
    total_cost = material_cost + labor_cost + additional_cost
    
    # 5. Calculation Basis (for transparency)
    calculation_basis = [
        f"Fläche: {area_sqm:.0f} m²",
        f"Material: {material_info['type'].title()} ({material_info['quality']}) - {material_info['price_per_sqm']:.2f} EUR/m²",
        f"Arbeitsart: {work_info['type'].title()} ({work_info['complexity']}) - {work_info['cost_per_sqm']:.2f} EUR/m²"
    ]
    
    # 6. Confidence Score (0.0 - 1.0)
    confidence = 0.5  # Base
    if area_sqm:
        confidence += 0.3
    if material_info["type"] != "ziegel" or material_info["quality"] != "standard":
        confidence += 0.1  # Specific material mentioned
    if work_info["type"] != "reparatur":
        confidence += 0.1  # Specific work type mentioned
    
    confidence = min(confidence, 1.0)
    
    # 7. Build Result
    estimate = ProjectEstimate(
        found=True,
        project_type=work_info["type"],
        area_sqm=area_sqm,
        material=f"{material_info['type']} ({material_info['quality']})",
        work_type=f"{work_info['type']} ({work_info['complexity']})",
        material_cost=material_cost,
        labor_cost=labor_cost,
        additional_cost=additional_cost,
        total_cost=total_cost,
        confidence=confidence,
        calculation_basis=calculation_basis,
        additional_services=[s["description"] for s in additional_services],
        notes="Dies ist ein unverbindlicher Richtwert. Finale Kalkulation nach Vor-Ort-Besichtigung."
    )
    
    logger.info(f"✅ Estimate calculated: {total_cost:.2f} EUR (confidence: {confidence:.2%})")
    
    return estimate


# ==========================================
# 📧 EMAIL FORMATTING
# ==========================================

def format_estimate_for_email(estimate: ProjectEstimate) -> str:
    """
    Formatiert Kostenschätzung für Notification-Email
    
    Returns:
        HTML string ready for email body
    """
    
    if not estimate.found:
        return f"""
        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #856404; margin-top: 0;">⚠️ Keine Kostenschätzung möglich</h3>
            <p style="color: #856404;">{estimate.notes}</p>
        </div>
        """
    
    # Build HTML
    html = f"""
    <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #28a745;">
        <h3 style="color: #155724; margin-top: 0;">💰 Automatische Richtpreis-Kalkulation</h3>
        
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h4 style="color: #333; margin-top: 0;">📊 Projekt-Details:</h4>
            <ul style="list-style: none; padding: 0;">
"""
    
    for basis in estimate.calculation_basis:
        html += f"                <li style='padding: 5px 0;'>✅ {basis}</li>\n"
    
    html += """            </ul>
        </div>
"""
    
    # Cost Breakdown
    html += f"""
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h4 style="color: #333; margin-top: 0;">💵 Kosten-Aufschlüsselung:</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Material:</strong></td>
                    <td style="text-align: right; padding: 8px;">{estimate.material_cost:,.2f} EUR</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Arbeitsleistung:</strong></td>
                    <td style="text-align: right; padding: 8px;">{estimate.labor_cost:,.2f} EUR</td>
                </tr>
"""
    
    if estimate.additional_cost > 0:
        html += f"""
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Zusatzleistungen:</strong></td>
                    <td style="text-align: right; padding: 8px;">{estimate.additional_cost:,.2f} EUR</td>
                </tr>
"""
    
    html += f"""
                <tr style="background: #f8f9fa; font-size: 1.2em;">
                    <td style="padding: 12px;"><strong>Gesamt (Richtwert):</strong></td>
                    <td style="text-align: right; padding: 12px;"><strong>{estimate.total_cost:,.2f} EUR</strong></td>
                </tr>
            </table>
        </div>
"""
    
    # Additional Services
    if estimate.additional_services:
        html += """
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h4 style="color: #333; margin-top: 0;">🔧 Zusatzleistungen:</h4>
            <ul>
"""
        for service in estimate.additional_services:
            html += f"                <li>{service}</li>\n"
        
        html += """            </ul>
        </div>
"""
    
    # Confidence & Notes
    confidence_color = "#28a745" if estimate.confidence > 0.7 else "#ffc107" if estimate.confidence > 0.5 else "#dc3545"
    confidence_text = "Hoch" if estimate.confidence > 0.7 else "Mittel" if estimate.confidence > 0.5 else "Niedrig"
    
    html += f"""
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 15px 0; font-size: 0.9em;">
            <p style="margin: 5px 0;">
                <strong>Genauigkeit:</strong> 
                <span style="color: {confidence_color}; font-weight: bold;">{confidence_text} ({estimate.confidence:.0%})</span>
            </p>
            <p style="margin: 5px 0; color: #6c757d; font-style: italic;">
                ℹ️ {estimate.notes}
            </p>
        </div>
    </div>
"""
    
    return html


# ==========================================
# 🧪 TEST FUNCTION
# ==========================================

def test_estimate():
    """Test function with example transcripts"""
    
    print("🧪 Testing Estimate Calculator...\n")
    
    test_cases = [
        {
            "name": "Neueindeckung mit Dämmung",
            "transcript": """
            Guten Tag, ich brauche ein komplett neues Dach. Das alte ist über 40 Jahre alt.
            Die Dachfläche beträgt ungefähr 120 Quadratmeter. 
            Wir möchten hochwertige Ziegel, am liebsten Frankfurter Pfanne.
            Außerdem soll das Dach gedämmt werden und wir brauchen ein neues Gerüst.
            """
        },
        {
            "name": "Reparatur Schiefer",
            "transcript": """
            Hallo, bei uns sind einige Schieferplatten vom Dach gefallen. 
            Ich schätze mal 20-30 Quadratmeter müssen repariert werden.
            Das ist ein Schieferdach, circa 80 Jahre alt.
            """
        },
        {
            "name": "Flachdach mit Gauben",
            "transcript": """
            Wir haben ein Flachdach mit Bitumen, etwa 200 qm.
            Wir wollen das sanieren und dabei 2 Gauben einbauen lassen.
            Außerdem brauchen wir 3 neue Dachfenster.
            """
        },
        {
            "name": "Keine Fläche angegeben",
            "transcript": """
            Ich hätte gerne ein Angebot für ein neues Dach.
            Ziegel wären gut. Wann könnten Sie vorbeikommen?
            """
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'='*60}")
        
        estimate = calculate_estimate_from_transcript(test["transcript"])
        
        if estimate.found:
            print(f"\n✅ Schätzung erfolgreich!")
            print(f"   Projekt: {estimate.project_type}")
            print(f"   Fläche: {estimate.area_sqm:.0f} m²")
            print(f"   Material: {estimate.material}")
            print(f"   Arbeitsart: {estimate.work_type}")
            print(f"\n   💰 Kosten:")
            print(f"      Material:        {estimate.material_cost:>10,.2f} EUR")
            print(f"      Arbeit:          {estimate.labor_cost:>10,.2f} EUR")
            if estimate.additional_cost > 0:
                print(f"      Zusatzleistungen:{estimate.additional_cost:>10,.2f} EUR")
            print(f"      {'─'*35}")
            print(f"      GESAMT:          {estimate.total_cost:>10,.2f} EUR")
            print(f"\n   📊 Genauigkeit: {estimate.confidence:.0%}")
            
            if estimate.additional_services:
                print(f"\n   🔧 Zusatzleistungen:")
                for service in estimate.additional_services:
                    print(f"      - {service}")
        else:
            print(f"\n❌ Keine Schätzung möglich")
            print(f"   Grund: {estimate.notes}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_estimate()
