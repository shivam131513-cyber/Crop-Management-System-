"""
Water Usage & Irrigation Schedule Router
Provides crop-specific water consumption benchmarks and an optimised
irrigation schedule for Punjab farmers, accounting for season,
soil type, and Punjab's rationed power supply slots.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter()

# ── Water requirements (mm per season) & canals/tubewell mix ──────────────────
WATER_PROFILES: dict = {
    "wheat": {
        "name": "Wheat", "name_pa": "ਕਣਕ", "season": "rabi",
        "total_water_mm": 400,
        "irrigations": 4,
        "critical_stages": ["CRI (21 DAS)", "Tillering (40 DAS)", "Jointing (60 DAS)", "Grain-fill (90 DAS)"],
        "method": "Flood / Furrow",
        "efficiency_tip": "Skip irrigation if >15 mm rain received. SRI drip saves 25 %.",
        "efficiency_tip_pa": "15 mm ਬਾਰਸ਼ ਤੋਂ ਬਾਅਦ ਸਿੰਚਾਈ ਛੱਡੋ। ਡਰਿੱਪ ਨਾਲ 25% ਪਾਣੀ ਬਚਦਾ ਹੈ।",
        "water_per_acre_liters": 1_620_000,
    },
    "rice": {
        "name": "Rice (Paddy)", "name_pa": "ਝੋਨਾ", "season": "kharif",
        "total_water_mm": 1200,
        "irrigations": 20,
        "critical_stages": ["Transplant", "Tillering", "Panicle initiation", "Flowering"],
        "method": "Continuous flooding / SRI",
        "efficiency_tip": "Alternate wetting & drying (AWD) saves 30 % water with no yield loss.",
        "efficiency_tip_pa": "AWD ਤਕਨੀਕ ਨਾਲ 30% ਪਾਣੀ ਬਚਾਓ — ਝਾੜ ਨਹੀਂ ਘਟਦਾ।",
        "water_per_acre_liters": 4_860_000,
    },
    "maize": {
        "name": "Maize", "name_pa": "ਮੱਕੀ", "season": "kharif",
        "total_water_mm": 500,
        "irrigations": 5,
        "critical_stages": ["Germination", "Knee-high (30 DAS)", "Tasselling", "Silking", "Grain fill"],
        "method": "Furrow / Sprinkler",
        "efficiency_tip": "Sprinkler irrigation increases water-use efficiency by 40 %.",
        "efficiency_tip_pa": "ਸਪ੍ਰਿੰਕਲਰ ਨਾਲ 40% ਵੱਧ ਕੁਸ਼ਲਤਾ।",
        "water_per_acre_liters": 2_025_000,
    },
    "cotton": {
        "name": "Cotton", "name_pa": "ਕਪਾਹ", "season": "kharif",
        "total_water_mm": 700,
        "irrigations": 8,
        "critical_stages": ["Germination", "Squaring", "Flowering", "Boll development"],
        "method": "Flood / Drip",
        "efficiency_tip": "Drip irrigation with fertigation cuts water by 40 % and boosts lint.",
        "efficiency_tip_pa": "ਡਰਿੱਪ ਅਤੇ ਫਰਟੀਗੇਸ਼ਨ ਨਾਲ 40% ਪਾਣੀ ਬਚਦਾ ਹੈ।",
        "water_per_acre_liters": 2_835_000,
    },
    "mustard": {
        "name": "Mustard", "name_pa": "ਸਰ੍ਹੋਂ", "season": "rabi",
        "total_water_mm": 250,
        "irrigations": 3,
        "critical_stages": ["Branching (25 DAS)", "Flowering (45 DAS)", "Pod fill (65 DAS)"],
        "method": "Flood / Sprinkler",
        "efficiency_tip": "Mustard is drought-tolerant. Avoid excess water at flowering.",
        "efficiency_tip_pa": "ਸਰ੍ਹੋਂ ਸੋਕਾ ਸਹਿੰਦੀ ਹੈ। ਫੁੱਲਾਂ ਵੇਲੇ ਜ਼ਿਆਦਾ ਪਾਣੀ ਨਾ ਦਿਓ।",
        "water_per_acre_liters": 1_012_500,
    },
    "potato": {
        "name": "Potato", "name_pa": "ਆਲੂ", "season": "rabi",
        "total_water_mm": 450,
        "irrigations": 7,
        "critical_stages": ["Emergence", "Stolon formation", "Tuber initiation", "Tuber bulking"],
        "method": "Furrow / Drip",
        "efficiency_tip": "Furrow irrigation every 10–12 days. Avoid waterlogging (causes rot).",
        "efficiency_tip_pa": "10–12 ਦਿਨਾਂ ਬਾਅਦ ਸਿੰਚਾਈ। ਪਾਣੀ ਖੜ੍ਹਾ ਨਾ ਹੋਣ ਦਿਓ।",
        "water_per_acre_liters": 1_822_500,
    },
    "moong": {
        "name": "Moong (Green Gram)", "name_pa": "ਮੂੰਗ", "season": "kharif/zaid",
        "total_water_mm": 250,
        "irrigations": 3,
        "critical_stages": ["Germination", "Flowering (35 DAS)", "Pod fill (50 DAS)"],
        "method": "Sprinkler / Flood",
        "efficiency_tip": "Short-duration crop — finish with 3 irrigations only.",
        "efficiency_tip_pa": "ਥੋੜੇ ਸਮੇਂ ਦੀ ਫ਼ਸਲ — ਕੇਵਲ 3 ਸਿੰਚਾਈਆਂ।",
        "water_per_acre_liters": 1_012_500,
    },
    "sunflower": {
        "name": "Sunflower", "name_pa": "ਸੂਰਜਮੁਖੀ", "season": "rabi/zaid",
        "total_water_mm": 350,
        "irrigations": 4,
        "critical_stages": ["Germination", "Vegetative (30 DAS)", "Bud (50 DAS)", "Flowering (65 DAS)"],
        "method": "Furrow / Drip",
        "efficiency_tip": "Critical water need at flowering. Drought after flowering cuts oil content.",
        "efficiency_tip_pa": "ਫੁੱਲ ਸਮੇਂ ਪਾਣੀ ਜ਼ਰੂਰੀ। ਬਾਅਦ ਵਿੱਚ ਸੋਕਾ ਤੇਲ ਘਟਾਉਂਦਾ ਹੈ।",
        "water_per_acre_liters": 1_417_500,
    },
}

# Punjab power-supply irrigation slots (PSPCL schedule)
IRRIGATION_SLOTS = [
    {"label": "Morning",   "start": "05:00", "end": "08:00", "recommended": True},
    {"label": "Evening",   "start": "17:00", "end": "20:00", "recommended": True},
    {"label": "Night",     "start": "22:00", "end": "01:00", "recommended": True},
    {"label": "Afternoon", "start": "12:00", "end": "15:00", "recommended": False,
     "note": "High evaporation — avoid unless necessary"},
]


class WaterScheduleEntry(BaseModel):
    irrigation_no: int
    growth_stage: str
    days_after_sowing: str
    water_depth_mm: int
    preferred_slot: str


class WaterUsageResponse(BaseModel):
    crop: str
    crop_pa: str
    season: str
    land_size_acres: float
    total_water_mm: int
    total_water_liters: float
    irrigations_count: int
    method: str
    efficiency_tip: str
    efficiency_tip_pa: str
    schedule: List[WaterScheduleEntry]
    power_slots: list
    savings_tip: str


def build_schedule(crop_key: str, profile: dict, land_acres: float) -> List[WaterScheduleEntry]:
    """Generate a per-irrigation schedule from critical stages."""
    stages = profile["critical_stages"]
    n = len(stages)
    mm_each = profile["total_water_mm"] // n
    slots = ["05:00–08:00", "22:00–01:00", "17:00–20:00", "05:00–08:00"]

    schedule = []
    for i, stage in enumerate(stages):
        schedule.append(WaterScheduleEntry(
            irrigation_no=i + 1,
            growth_stage=stage,
            days_after_sowing=f"~{(i + 1) * (90 // n)} DAS",
            water_depth_mm=mm_each,
            preferred_slot=slots[i % len(slots)],
        ))
    return schedule


@router.get("/water-usage", response_model=WaterUsageResponse)
async def get_water_usage(
    crop: str = Query(..., description="Crop name (e.g. wheat, rice, cotton)"),
    land_size_acres: float = Query(1.0, ge=0.1, le=500.0, description="Land size in acres"),
):
    """
    Return water consumption benchmarks and an optimised irrigation schedule
    for the requested crop and land size.

    - Provides total water requirement (mm and litres per acre)
    - Lists critical growth stages to irrigate
    - Aligns schedule with Punjab PSPCL power-supply slots
    - Includes efficiency tips in English and Punjabi (Gurmukhi)
    """
    crop_key = crop.lower().strip()
    profile = WATER_PROFILES.get(crop_key)
    if not profile:
        available = ", ".join(WATER_PROFILES.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Crop '{crop}' not found. Available: {available}",
        )

    total_liters = round(profile["water_per_acre_liters"] * land_size_acres, 0)
    schedule = build_schedule(crop_key, profile, land_size_acres)

    return WaterUsageResponse(
        crop=profile["name"],
        crop_pa=profile["name_pa"],
        season=profile["season"],
        land_size_acres=land_size_acres,
        total_water_mm=profile["total_water_mm"],
        total_water_liters=total_liters,
        irrigations_count=profile["irrigations"],
        method=profile["method"],
        efficiency_tip=profile["efficiency_tip"],
        efficiency_tip_pa=profile["efficiency_tip_pa"],
        schedule=schedule,
        power_slots=IRRIGATION_SLOTS,
        savings_tip=(
            "Use Punjab's free power slots (5–8 AM, 10 PM–1 AM) for tubewell operation. "
            "Drip/sprinkler systems reduce water use by 30–40 % on average."
        ),
    )


@router.get("/water-usage/crops")
async def list_water_crops():
    """List all crops with water usage data."""
    return {
        "crops": [
            {
                "key": k,
                "name": v["name"],
                "name_pa": v["name_pa"],
                "season": v["season"],
                "total_water_mm": v["total_water_mm"],
                "irrigations": v["irrigations"],
            }
            for k, v in WATER_PROFILES.items()
        ]
    }
