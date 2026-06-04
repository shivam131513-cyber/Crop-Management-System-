"""
Government Scheme Advisory Router
Lists all major central and Punjab state government agricultural schemes
with eligibility checks, benefit summaries, and application links.
Helps small and marginal farmers discover entitlements they may be missing.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# ── Scheme data ───────────────────────────────────────────────────────────────
SCHEMES = [
    {
        "id": "pmfby",
        "name": "PM Fasal Bima Yojana (PMFBY)",
        "name_pa": "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਫ਼ਸਲ ਬੀਮਾ ਯੋਜਨਾ",
        "type": "central",
        "category": "crop_insurance",
        "benefit": "Crop insurance covering 95 % of loss from natural calamities, pests, and disease.",
        "benefit_pa": "ਕੁਦਰਤੀ ਆਫ਼ਤਾਂ ਅਤੇ ਕੀੜਿਆਂ ਤੋਂ 95% ਨੁਕਸਾਨ ਦਾ ਮੁਆਵਜ਼ਾ।",
        "premium_farmer_pct": {"kharif": 2.0, "rabi": 1.5, "horticulture": 5.0},
        "eligible_crops": ["wheat", "rice", "maize", "cotton", "mustard", "potato", "moong", "sunflower", "groundnut"],
        "eligibility": {
            "land_max_acres": None,  # No upper limit
            "is_tenant_eligible": True,
            "categories": ["small", "marginal", "large"],
        },
        "apply_url": "https://pmfby.gov.in",
        "helpline": "1800-180-1551",
        "deadline_note": "Register before sowing. Enrol via nearest bank branch or CSC.",
        "deadline_note_pa": "ਬਿਜਾਈ ਤੋਂ ਪਹਿਲਾਂ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਕਰੋ। ਬੈਂਕ ਜਾਂ CSC ਤੋਂ।",
    },
    {
        "id": "pmkisan",
        "name": "PM Kisan Samman Nidhi",
        "name_pa": "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਕਿਸਾਨ ਸਨਮਾਨ ਨਿਧੀ",
        "type": "central",
        "category": "income_support",
        "benefit": "₹6,000/year direct income support in 3 equal instalments of ₹2,000.",
        "benefit_pa": "ਸਾਲ ਵਿੱਚ 3 ਵਾਰ ₹2,000 ਸਿੱਧੇ ਬੈਂਕ ਖਾਤੇ ਵਿੱਚ — ਕੁੱਲ ₹6,000।",
        "premium_farmer_pct": None,
        "eligible_crops": [],  # All crops
        "eligibility": {
            "land_max_acres": None,
            "is_tenant_eligible": False,
            "categories": ["small", "marginal", "large"],
            "note": "Land must be in farmer's own name. Govt employees not eligible.",
        },
        "apply_url": "https://pmkisan.gov.in",
        "helpline": "155261",
        "deadline_note": "Apply anytime via pmkisan.gov.in or nearest CSC.",
        "deadline_note_pa": "ਕਦੇ ਵੀ pmkisan.gov.in ਜਾਂ CSC ਤੋਂ ਅਪਲਾਈ ਕਰੋ।",
    },
    {
        "id": "kcc",
        "name": "Kisan Credit Card (KCC)",
        "name_pa": "ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ",
        "type": "central",
        "category": "credit",
        "benefit": "Short-term crop loans up to ₹3 lakh at 4% interest (with prompt repayment subsidy).",
        "benefit_pa": "₹3 ਲੱਖ ਤੱਕ ਸਸਤਾ ਕਰਜ਼ਾ — ਵੇਲੇ ਸਿਰ ਅਦਾਇਗੀ 'ਤੇ ਵਿਆਜ 4%।",
        "premium_farmer_pct": None,
        "eligible_crops": [],
        "eligibility": {
            "land_max_acres": None,
            "is_tenant_eligible": True,
            "categories": ["small", "marginal", "large"],
        },
        "apply_url": "https://www.nabard.org/content1.aspx?id=572",
        "helpline": "1800-180-1551",
        "deadline_note": "Apply at any cooperative bank, SBI, or Punjab National Bank branch.",
        "deadline_note_pa": "ਕਿਸੇ ਵੀ ਸਹਿਕਾਰੀ ਬੈਂਕ ਜਾਂ SBI ਤੋਂ ਅਪਲਾਈ ਕਰੋ।",
    },
    {
        "id": "ppcb_parali",
        "name": "Punjab In-Situ Crop Residue Management Scheme",
        "name_pa": "ਪਰਾਲੀ ਪ੍ਰਬੰਧਨ ਸਬਸਿਡੀ ਯੋਜਨਾ",
        "type": "state",
        "category": "residue_management",
        "benefit": "50 % subsidy on Happy Seeder, Super SMS, Rotavator for stubble management.",
        "benefit_pa": "ਹੈਪੀ ਸੀਡਰ, ਸੁਪਰ SMS, ਰੋਟਾਵੇਟਰ 'ਤੇ 50% ਸਬਸਿਡੀ।",
        "premium_farmer_pct": None,
        "eligible_crops": ["rice", "wheat"],
        "eligibility": {
            "land_max_acres": None,
            "is_tenant_eligible": False,
            "categories": ["small", "marginal", "large"],
            "note": "Machine purchase from empanelled dealers only.",
        },
        "apply_url": "https://agripb.gov.in",
        "helpline": "0172-2970001",
        "deadline_note": "Apply before kharif season starts. Limited slots per district.",
        "deadline_note_pa": "ਖਰੀਫ਼ ਤੋਂ ਪਹਿਲਾਂ ਅਪਲਾਈ ਕਰੋ। ਹਰ ਜ਼ਿਲ੍ਹੇ ਵਿੱਚ ਸੀਮਿਤ ਸਲਾਟ।",
    },
    {
        "id": "pmksy",
        "name": "PM Krishi Sinchai Yojana (PMKSY) – Drip/Sprinkler",
        "name_pa": "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਕ੍ਰਿਸ਼ੀ ਸਿੰਚਾਈ ਯੋਜਨਾ",
        "type": "central",
        "category": "irrigation",
        "benefit": "55 % subsidy on drip and sprinkler irrigation systems (up to 70 % for SC/ST farmers).",
        "benefit_pa": "ਡਰਿੱਪ/ਸਪ੍ਰਿੰਕਲਰ 'ਤੇ 55% ਸਬਸਿਡੀ (SC/ST ਲਈ 70%)।",
        "premium_farmer_pct": None,
        "eligible_crops": [],
        "eligibility": {
            "land_max_acres": 12.5,
            "is_tenant_eligible": False,
            "categories": ["small", "marginal"],
            "note": "Priority for small/marginal farmers under 5 acres.",
        },
        "apply_url": "https://pmksy.gov.in",
        "helpline": "1800-180-1551",
        "deadline_note": "Apply through Punjab Horticulture Dept or Agriculture Dept portal.",
        "deadline_note_pa": "ਪੰਜਾਬ ਬਾਗਬਾਨੀ ਵਿਭਾਗ ਜਾਂ ਖੇਤੀਬਾੜੀ ਪੋਰਟਲ ਤੋਂ ਅਪਲਾਈ ਕਰੋ।",
    },
    {
        "id": "enam",
        "name": "e-NAM (National Agriculture Market)",
        "name_pa": "ਇਲੈਕਟ੍ਰਾਨਿਕ ਰਾਸ਼ਟਰੀ ਖੇਤੀ ਮੰਡੀ",
        "type": "central",
        "category": "market_access",
        "benefit": "Online mandi platform for better price discovery. Farmers get bids from across India.",
        "benefit_pa": "ਔਨਲਾਈਨ ਮੰਡੀ — ਸਾਰੇ ਭਾਰਤ ਤੋਂ ਬੋਲੀਆਂ ਮਿਲਦੀਆਂ ਹਨ।",
        "premium_farmer_pct": None,
        "eligible_crops": [],
        "eligibility": {
            "land_max_acres": None,
            "is_tenant_eligible": True,
            "categories": ["small", "marginal", "large"],
        },
        "apply_url": "https://enam.gov.in",
        "helpline": "1800-270-0224",
        "deadline_note": "Register free at enam.gov.in. Bring Aadhaar + bank passbook.",
        "deadline_note_pa": "enam.gov.in 'ਤੇ ਮੁਫ਼ਤ ਰਜਿਸਟ੍ਰੇਸ਼ਨ। ਆਧਾਰ + ਬੈਂਕ ਪਾਸਬੁੱਕ ਲੈ ਜਾਓ।",
    },
    {
        "id": "pm_kusum",
        "name": "PM KUSUM (Solar Pump Scheme)",
        "name_pa": "ਸੂਰਜੀ ਪੰਪ ਯੋਜਨਾ PM KUSUM",
        "type": "central",
        "category": "energy",
        "benefit": "60 % subsidy on solar pumps (up to 7.5 HP). Sell surplus electricity to PSPCL.",
        "benefit_pa": "7.5 HP ਤੱਕ ਸੂਰਜੀ ਪੰਪ 'ਤੇ 60% ਸਬਸਿਡੀ। ਵਾਧੂ ਬਿਜਲੀ PSPCL ਨੂੰ ਵੇਚੋ।",
        "premium_farmer_pct": None,
        "eligible_crops": [],
        "eligibility": {
            "land_max_acres": None,
            "is_tenant_eligible": False,
            "categories": ["small", "marginal", "large"],
        },
        "apply_url": "https://pmkusum.mnre.gov.in",
        "helpline": "0172-2210005",
        "deadline_note": "Apply via Punjab Energy Development Agency (PEDA).",
        "deadline_note_pa": "PEDA (ਪੇਡਾ) ਦਫ਼ਤਰ ਤੋਂ ਅਪਲਾਈ ਕਰੋ।",
    },
    {
        "id": "prkvy",
        "name": "Pradhan Mantri Kisan Urja Suraksha evam Utthan Mahabhiyan (PM KUSUM – Component B)",
        "name_pa": "ਖੇਤੀ ਸੋਲਰ ਊਰਜਾ ਯੋਜਨਾ",
        "type": "central",
        "category": "energy",
        "benefit": "Solarise existing grid-connected pumps. Reduces electricity bills to zero.",
        "benefit_pa": "ਬਿਜਲੀ ਦਾ ਬਿੱਲ ਜ਼ੀਰੋ — ਮੌਜੂਦਾ ਪੰਪ ਸੋਲਰ ਨਾਲ ਜੋੜੋ।",
        "premium_farmer_pct": None,
        "eligible_crops": [],
        "eligibility": {
            "land_max_acres": None,
            "is_tenant_eligible": False,
            "categories": ["small", "marginal", "large"],
        },
        "apply_url": "https://pmkusum.mnre.gov.in",
        "helpline": "0172-2210005",
        "deadline_note": "Via PEDA. Grid-connected pump required.",
        "deadline_note_pa": "PEDA ਤੋਂ। ਗ੍ਰਿੱਡ ਨਾਲ ਜੁੜਿਆ ਪੰਪ ਜ਼ਰੂਰੀ।",
    },
]

CATEGORY_LABELS = {
    "crop_insurance":    "Crop Insurance",
    "income_support":    "Income Support",
    "credit":            "Farm Credit",
    "residue_management":"Stubble & Residue",
    "irrigation":        "Irrigation Subsidy",
    "market_access":     "Market Access",
    "energy":            "Solar / Energy",
}


class SchemeItem(BaseModel):
    id: str
    name: str
    name_pa: str
    type: str
    category: str
    category_label: str
    benefit: str
    benefit_pa: str
    apply_url: str
    helpline: str
    deadline_note: str
    deadline_note_pa: str
    is_eligible: Optional[bool] = None


class EligibilityRequest(BaseModel):
    land_acres: float
    farmer_category: str   # small | marginal | large
    is_tenant: bool
    crops: List[str]
    district: Optional[str] = None


# ── Routes ────────────────────────────────────────────────────────────────────
@router.get("/list", response_model=List[SchemeItem])
async def list_schemes(
    category: Optional[str] = Query(None, description="Filter: crop_insurance | income_support | credit | irrigation | market_access | energy | residue_management"),
    scheme_type: Optional[str] = Query(None, description="Filter: central | state"),
    crop: Optional[str] = Query(None, description="Filter by applicable crop"),
):
    """
    List all government agricultural schemes for Punjab farmers.
    Optionally filter by category, type (central/state), or crop.
    """
    results = []
    for s in SCHEMES:
        if category and s["category"] != category:
            continue
        if scheme_type and s["type"] != scheme_type:
            continue
        if crop:
            crop_lower = crop.lower()
            if s["eligible_crops"] and crop_lower not in s["eligible_crops"]:
                continue

        results.append(SchemeItem(
            **{k: v for k, v in s.items() if k in SchemeItem.model_fields},
            category_label=CATEGORY_LABELS.get(s["category"], s["category"]),
        ))

    return results


@router.post("/eligibility")
async def check_eligibility(req: EligibilityRequest):
    """
    Check which schemes a farmer is eligible for, given their land size,
    category (small/marginal/large), tenant status, and crop list.

    Returns a list of eligible schemes with application details.
    """
    if req.farmer_category not in ("small", "marginal", "large"):
        raise HTTPException(status_code=422, detail="farmer_category must be: small | marginal | large")

    eligible = []
    ineligible = []
    crops_lower = [c.lower() for c in req.crops]

    for s in SCHEMES:
        rules = s["eligibility"]

        # Check tenant eligibility
        if req.is_tenant and not rules.get("is_tenant_eligible", False):
            ineligible.append({"id": s["id"], "name": s["name"], "reason": "Tenant farmers not eligible."})
            continue

        # Check farmer category
        if req.farmer_category not in rules.get("categories", []):
            ineligible.append({"id": s["id"], "name": s["name"], "reason": f"{req.farmer_category} farmers not covered."})
            continue

        # Check land size limit
        max_acres = rules.get("land_max_acres")
        if max_acres and req.land_acres > max_acres:
            ineligible.append({"id": s["id"], "name": s["name"], "reason": f"Land limit is {max_acres} acres."})
            continue

        # Check crop match
        if s["eligible_crops"] and not any(c in s["eligible_crops"] for c in crops_lower):
            ineligible.append({"id": s["id"], "name": s["name"], "reason": "Crop not covered by this scheme."})
            continue

        eligible.append(SchemeItem(
            **{k: v for k, v in s.items() if k in SchemeItem.model_fields},
            category_label=CATEGORY_LABELS.get(s["category"], s["category"]),
            is_eligible=True,
        ))

    return {
        "farmer_profile": {
            "land_acres": req.land_acres,
            "category": req.farmer_category,
            "is_tenant": req.is_tenant,
            "crops": req.crops,
        },
        "eligible_schemes": [e.dict() for e in eligible],
        "ineligible_schemes": ineligible,
        "total_eligible": len(eligible),
        "summary": (
            f"You qualify for {len(eligible)} scheme(s). "
            f"Priority: enrol in PMFBY for insurance and PM-Kisan for income support."
            if eligible else
            "No schemes matched your profile. Visit your district agriculture office for personalised guidance."
        ),
        "summary_pa": (
            f"ਤੁਸੀਂ {len(eligible)} ਯੋਜਨਾਵਾਂ ਲਈ ਯੋਗ ਹੋ।"
            if eligible else
            "ਕੋਈ ਯੋਜਨਾ ਮੇਲ ਨਹੀਂ ਖਾਂਦੀ। ਜ਼ਿਲ੍ਹਾ ਖੇਤੀਬਾੜੀ ਦਫ਼ਤਰ ਜਾਓ।"
        ),
    }
