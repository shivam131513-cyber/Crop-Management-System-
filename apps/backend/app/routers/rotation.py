"""
Crop Rotation Plan Router
Provides scientifically-backed, zone-specific crop rotation sequences for
Punjab farmers to improve soil health, break pest cycles, and reduce input costs.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# ── Zone-specific rotation plans ───────────────────────────────────────────────
# Each entry: list of seasons in order (kharif → rabi → zaid), repeated over years
ROTATION_PLANS = {
    # Wheat–Rice is the dominant (but unsustainable) sequence in Punjab
    "wheat-rice": {
        "name": "Wheat–Rice (Conventional)",
        "zone": ["majha", "malwa", "doaba"],
        "years": 2,
        "sequence": [
            {"year": 1, "season": "kharif", "crop": "rice",    "crop_pa": "ਝੋਨਾ"},
            {"year": 1, "season": "rabi",   "crop": "wheat",   "crop_pa": "ਕਣਕ"},
            {"year": 2, "season": "kharif", "crop": "rice",    "crop_pa": "ਝੋਨਾ"},
            {"year": 2, "season": "rabi",   "crop": "wheat",   "crop_pa": "ਕਣਕ"},
        ],
        "pros": ["High guaranteed MSP", "Well-established procurement chain"],
        "cons": ["Depletes groundwater rapidly", "Leaves residue (stubble burning)", "Reduces soil organic carbon"],
        "recommendation": "Transition at least 1 rabi crop to mustard or potato to break cycle.",
        "recommendation_pa": "ਘੱਟੋ-ਘੱਟ 1 ਰਬੀ ਫ਼ਸਲ ਸਰ੍ਹੋਂ ਜਾਂ ਆਲੂ ਵਿੱਚ ਬਦਲੋ।",
        "water_saving_pct": 0,
        "soil_health_score": 3,  # out of 10
    },
    "wheat-maize": {
        "name": "Wheat–Maize (Water-Smart)",
        "zone": ["malwa", "doaba"],
        "years": 2,
        "sequence": [
            {"year": 1, "season": "kharif", "crop": "maize",  "crop_pa": "ਮੱਕੀ"},
            {"year": 1, "season": "rabi",   "crop": "wheat",  "crop_pa": "ਕਣਕ"},
            {"year": 2, "season": "kharif", "crop": "maize",  "crop_pa": "ਮੱਕੀ"},
            {"year": 2, "season": "rabi",   "crop": "wheat",  "crop_pa": "ਕਣਕ"},
        ],
        "pros": ["50 % less water than rice", "No stubble burning", "Growing demand for poultry feed"],
        "cons": ["No MSP procurement guarantee for maize in Punjab", "Price volatility"],
        "recommendation": "Best for Malwa sandy loam soils. Sell to local poultry/starch industry.",
        "recommendation_pa": "ਮਾਲਵੇ ਦੀਆਂ ਰੇਤਲੀ ਦੋਮਟ ਮਿੱਟੀਆਂ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ।",
        "water_saving_pct": 50,
        "soil_health_score": 6,
    },
    "wheat-cotton": {
        "name": "Wheat–Cotton (Malwa Classic)",
        "zone": ["malwa"],
        "years": 2,
        "sequence": [
            {"year": 1, "season": "kharif", "crop": "cotton", "crop_pa": "ਕਪਾਹ"},
            {"year": 1, "season": "rabi",   "crop": "wheat",  "crop_pa": "ਕਣਕ"},
            {"year": 2, "season": "kharif", "crop": "cotton", "crop_pa": "ਕਪਾਹ"},
            {"year": 2, "season": "rabi",   "crop": "wheat",  "crop_pa": "ਕਣਕ"},
        ],
        "pros": ["Higher cotton MSP (₹7020/qtl)", "Malwa cotton belt advantage", "Less water than rice"],
        "cons": ["Prone to whitefly and bollworm", "Requires careful pest management"],
        "recommendation": "Use Bt-cotton and IPM. Maintain field hygiene to reduce bollworm.",
        "recommendation_pa": "Bt-ਕਪਾਹ ਅਤੇ IPM ਵਰਤੋ। ਬੋਲਵਰਮ ਤੋਂ ਬਚਣ ਲਈ ਖੇਤ ਸਾਫ਼ ਰੱਖੋ।",
        "water_saving_pct": 35,
        "soil_health_score": 5,
    },
    "wheat-moong-rice": {
        "name": "Wheat–Moong–Rice (3-Crop Diversified)",
        "zone": ["majha", "doaba", "malwa"],
        "years": 1,
        "sequence": [
            {"year": 1, "season": "rabi",   "crop": "wheat",  "crop_pa": "ਕਣਕ"},
            {"year": 1, "season": "zaid",   "crop": "moong",  "crop_pa": "ਮੂੰਗ"},
            {"year": 1, "season": "kharif", "crop": "rice",   "crop_pa": "ਝੋਨਾ"},
        ],
        "pros": ["Moong fixes nitrogen (saves ₹1500/acre in fertiliser)", "3 income streams per year",
                 "Stubble decomposed by moong residue"],
        "cons": ["Labour-intensive", "Tight window between wheat harvest and moong sowing"],
        "recommendation": "Harvest wheat by April 15 → sow moong immediately → rice by June 10.",
        "recommendation_pa": "15 ਅਪ੍ਰੈਲ ਕਣਕ ਵੱਢੋ → ਮੂੰਗ ਬੀਜੋ → 10 ਜੂਨ ਝੋਨਾ ਲਾਓ।",
        "water_saving_pct": 10,
        "soil_health_score": 8,
        "nitrogen_saving_kg_per_acre": 20,
    },
    "mustard-rice": {
        "name": "Mustard–Rice (Malwa Dryland)",
        "zone": ["malwa"],
        "years": 2,
        "sequence": [
            {"year": 1, "season": "rabi",   "crop": "mustard", "crop_pa": "ਸਰ੍ਹੋਂ"},
            {"year": 1, "season": "kharif", "crop": "rice",    "crop_pa": "ਝੋਨਾ"},
            {"year": 2, "season": "rabi",   "crop": "mustard", "crop_pa": "ਸਰ੍ਹੋਂ"},
            {"year": 2, "season": "kharif", "crop": "rice",    "crop_pa": "ਝੋਨਾ"},
        ],
        "pros": ["Mustard uses 60 % less water than wheat", "Breaks wheat-borne soil pathogens",
                 "Oil seed crop with growing demand"],
        "cons": ["Mustard MSP lower than wheat", "Aphid risk in dry winters"],
        "recommendation": "Ideal for tube-well deficit areas in Malwa. IARI mustard varieties PM-21/RH-749.",
        "recommendation_pa": "ਮਾਲਵੇ ਵਿੱਚ ਟਿਊਬਵੈੱਲ ਘੱਟ ਵਾਲੇ ਖੇਤਰਾਂ ਲਈ ਢੁੱਕਵਾਂ।",
        "water_saving_pct": 40,
        "soil_health_score": 7,
    },
    "potato-wheat": {
        "name": "Potato–Wheat (Doaba Intensive)",
        "zone": ["doaba", "majha"],
        "years": 2,
        "sequence": [
            {"year": 1, "season": "rabi",   "crop": "potato", "crop_pa": "ਆਲੂ"},
            {"year": 1, "season": "kharif", "crop": "moong",  "crop_pa": "ਮੂੰਗ"},
            {"year": 2, "season": "rabi",   "crop": "wheat",  "crop_pa": "ਕਣਕ"},
            {"year": 2, "season": "kharif", "crop": "maize",  "crop_pa": "ਮੱਕੀ"},
        ],
        "pros": ["Potato gives ₹80,000–1,20,000/acre gross", "Doaba cool climate ideal for potato",
                 "Wheat benefits from potato-loosened soil"],
        "cons": ["High input cost for potato", "Cold storage needed for price realisation"],
        "recommendation": "Book cold storage in advance. Use Kufri Pukhraj / Jyoti variety.",
        "recommendation_pa": "ਕੋਲਡ ਸਟੋਰੇਜ ਪਹਿਲਾਂ ਬੁੱਕ ਕਰੋ। ਕੁਫ਼ਰੀ ਪੁਖਰਾਜ / ਜਯੋਤੀ ਕਿਸਮ ਵਰਤੋ।",
        "water_saving_pct": 20,
        "soil_health_score": 7,
    },
}

ZONE_MAP = {
    "ludhiana": "malwa", "bathinda": "malwa", "sangrur": "malwa",
    "mansa": "malwa", "muktsar": "malwa", "ferozepur": "malwa",
    "moga": "malwa", "faridkot": "malwa", "barnala": "malwa",
    "amritsar": "majha", "gurdaspur": "majha", "pathankot": "majha",
    "tarn taran": "majha",
    "jalandhar": "doaba", "hoshiarpur": "doaba", "kapurthala": "doaba",
    "nawanshahr": "doaba", "patiala": "doaba", "mohali": "doaba",
    "fatehgarh sahib": "doaba",
}


class RotationSequenceItem(BaseModel):
    year: int
    season: str
    crop: str
    crop_pa: str


class RotationPlanResponse(BaseModel):
    plan_id: str
    name: str
    zone: str
    district: Optional[str]
    years: int
    sequence: List[RotationSequenceItem]
    pros: List[str]
    cons: List[str]
    recommendation: str
    recommendation_pa: str
    water_saving_pct: int
    soil_health_score: int
    nitrogen_saving_kg_per_acre: Optional[int] = None


@router.get("/rotation-plan", response_model=RotationPlanResponse)
async def get_rotation_plan(
    plan: Optional[str] = Query(None, description="Rotation plan key (e.g. wheat-rice, wheat-moong-rice)"),
    district: Optional[str] = Query(None, description="Punjab district to auto-select best plan"),
    current_crop: Optional[str] = Query(None, description="Current main crop (e.g. wheat) to suggest alternatives"),
):
    """
    Return a crop rotation plan with pros/cons, water savings, and soil health score.

    - If `district` is provided, returns the best sustainable rotation for that agro-zone.
    - If `plan` is provided, returns details for that specific rotation.
    - If `current_crop` is wheat or rice, recommends diversification alternatives.
    """
    # Auto-select best plan by district zone
    if not plan and district:
        zone = ZONE_MAP.get(district.lower(), "malwa")
        # Prefer diversified > water-smart plans over wheat-rice monoculture
        priority = ["wheat-moong-rice", "wheat-maize", "wheat-cotton", "mustard-rice", "potato-wheat", "wheat-rice"]
        for p in priority:
            plan_data = ROTATION_PLANS[p]
            if zone in plan_data["zone"]:
                plan = p
                break

    # Auto-select by current_crop
    if not plan and current_crop:
        crop_lower = current_crop.lower()
        if crop_lower in ("wheat", "rice"):
            plan = "wheat-moong-rice"  # best diversification
        elif crop_lower == "cotton":
            plan = "wheat-cotton"
        else:
            plan = "wheat-maize"

    if not plan:
        plan = "wheat-moong-rice"  # default

    plan_data = ROTATION_PLANS.get(plan)
    if not plan_data:
        available = ", ".join(ROTATION_PLANS.keys())
        raise HTTPException(status_code=404, detail=f"Plan '{plan}' not found. Available: {available}")

    zone = ZONE_MAP.get(district.lower(), plan_data["zone"][0]) if district else plan_data["zone"][0]

    return RotationPlanResponse(
        plan_id=plan,
        name=plan_data["name"],
        zone=zone,
        district=district,
        years=plan_data["years"],
        sequence=[RotationSequenceItem(**s) for s in plan_data["sequence"]],
        pros=plan_data["pros"],
        cons=plan_data["cons"],
        recommendation=plan_data["recommendation"],
        recommendation_pa=plan_data["recommendation_pa"],
        water_saving_pct=plan_data["water_saving_pct"],
        soil_health_score=plan_data["soil_health_score"],
        nitrogen_saving_kg_per_acre=plan_data.get("nitrogen_saving_kg_per_acre"),
    )


@router.get("/rotation-plan/list")
async def list_rotation_plans(
    zone: Optional[str] = Query(None, description="Filter by agro-zone: majha | malwa | doaba"),
):
    """List all available rotation plans, optionally filtered by agro-zone."""
    results = []
    for plan_id, data in ROTATION_PLANS.items():
        if zone and zone.lower() not in data["zone"]:
            continue
        results.append({
            "plan_id": plan_id,
            "name": data["name"],
            "zones": data["zone"],
            "water_saving_pct": data["water_saving_pct"],
            "soil_health_score": data["soil_health_score"],
            "years": data["years"],
        })
    return {"plans": results, "total": len(results)}
