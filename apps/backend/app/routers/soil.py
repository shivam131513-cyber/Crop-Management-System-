from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

# Punjab soil zone NPK profiles
ZONE_SOIL_DEFAULTS = {
    "majha": {"ph": 7.8, "n": "medium", "p": "medium", "k": "high", "zinc": "sufficient"},
    "malwa": {"ph": 7.5, "n": "low",    "p": "low",    "k": "medium", "zinc": "deficient"},
    "doaba": {"ph": 7.9, "n": "medium", "p": "low",    "k": "medium", "zinc": "deficient"},
}

# NPK recommendations per crop (kg/acre)
CROP_NPK = {
    "wheat":   {"N": 55, "P": 25, "K": 12},
    "rice":    {"N": 50, "P": 25, "K": 12},
    "maize":   {"N": 60, "P": 25, "K": 20},
    "cotton":  {"N": 60, "P": 30, "K": 25},
    "mustard": {"N": 40, "P": 20, "K": 10},
    "potato":  {"N": 80, "P": 40, "K": 60},
    "moong":   {"N": 10, "P": 20, "K": 10},  # legume — low N
}

# Crop water requirements (irrigations per season, litres/acre per irrigation)
CROP_IRRIGATION = {
    "wheat":   {"irrigations": 5,  "litres_per_irrigation": 45000, "critical_stages": ["CRI (21 days)", "tillering (40d)", "jointing (65d)", "flowering (90d)", "grain fill (110d)"]},
    "rice":    {"irrigations": 20, "litres_per_irrigation": 50000, "critical_stages": ["transplanting", "tillering", "panicle initiation", "flowering", "grain fill"]},
    "maize":   {"irrigations": 4,  "litres_per_irrigation": 40000, "critical_stages": ["V6 (knee-high)", "tasselling", "silking", "dough stage"]},
    "cotton":  {"irrigations": 8,  "litres_per_irrigation": 45000, "critical_stages": ["squaring", "first bloom", "peak bloom", "boll development"]},
    "mustard": {"irrigations": 2,  "litres_per_irrigation": 35000, "critical_stages": ["branching (30d)", "flowering (60d)"]},
    "potato":  {"irrigations": 7,  "litres_per_irrigation": 40000, "critical_stages": ["planting", "stolon initiation", "tuber bulking", "maturation"]},
    "moong":   {"irrigations": 3,  "litres_per_irrigation": 30000, "critical_stages": ["emergence", "flowering (25d)", "pod fill"]},
}

STUBBLE_ALTERNATIVES = {
    "rice": [
        {
            "method": "Happy Seeder",
            "description": "Direct wheat sowing into standing rice stubble. No burning needed.",
            "description_pa": "ਝੋਨੇ ਦੀ ਨਾੜ ਵਿੱਚ ਸਿੱਧੀ ਕਣਕ ਦੀ ਬਿਜਾਈ।",
            "govt_incentive": "₹2,500/acre under PPCB scheme",
        },
        {
            "method": "Bio-Decomposer",
            "description": "PUSA bio-decomposer converts stubble to compost in 20 days.",
            "description_pa": "PUSA ਬਾਇਓ-ਡੀਕੰਪੋਜ਼ਰ 20 ਦਿਨਾਂ ਵਿੱਚ ਨਾੜ ਨੂੰ ਖਾਦ ਬਣਾਉਂਦਾ ਹੈ।",
            "govt_incentive": "Free capsules from Punjab Agriculture Department",
        },
        {
            "method": "Crop Switching",
            "description": "Grow maize or vegetables instead of rice to eliminate stubble issue.",
            "description_pa": "ਝੋਨੇ ਦੀ ਥਾਂ ਮੱਕੀ ਜਾਂ ਸਬਜ਼ੀਆਂ ਉਗਾਓ।",
            "govt_incentive": "₹17,500/acre crop diversification incentive",
        },
    ]
}


class SoilRequest(BaseModel):
    crop: str
    district: str
    soil_zone: Optional[str] = None
    ph: Optional[float] = None
    nitrogen: Optional[str] = None   # low | medium | high
    phosphorus: Optional[str] = None
    potassium: Optional[str] = None
    land_size_acres: Optional[float] = 2.0
    water_table_depth_ft: Optional[float] = None  # depth to water table in feet


class FertilizerSchedule(BaseModel):
    stage: str
    timing: str
    npk_kg_per_acre: dict
    note: str


class SoilResponse(BaseModel):
    crop: str
    zone: str
    npk_recommendation: dict
    fertilizer_schedule: List[FertilizerSchedule]
    zinc_correction: Optional[str]
    stubble_alternatives: Optional[list]
    organic_tip: str


class IrrigationScheduleItem(BaseModel):
    irrigation_number: int
    critical_stage: str
    recommended_slot: str       # morning | night
    slot_window: str
    water_litres_per_acre: float
    notes: str


class IrrigationScheduleResponse(BaseModel):
    crop: str
    district: str
    total_irrigations: int
    total_water_litres_per_acre: float
    water_source_tip: str
    schedule: List[IrrigationScheduleItem]
    electricity_reminder: str


@router.post("/recommend", response_model=SoilResponse)
async def get_soil_recommendation(req: SoilRequest):
    """
    Soil health + fertilizer recommendation for Punjab farmers.
    Includes NPK doses, schedule, zinc correction, and stubble management.
    """
    from app.services.crop_knowledge import DISTRICT_ZONE_MAP

    zone = req.soil_zone or DISTRICT_ZONE_MAP.get(req.district.lower(), "malwa")
    zone_data = ZONE_SOIL_DEFAULTS.get(zone, ZONE_SOIL_DEFAULTS["malwa"])

    crop_key = req.crop.lower().replace(" ", "_")
    npk = CROP_NPK.get(crop_key, {"N": 40, "P": 20, "K": 12})

    # Adjust N if soil nitrogen is high (avoid over-application)
    n_adj = req.nitrogen or zone_data["n"]
    if n_adj == "high":
        npk = {**npk, "N": int(npk["N"] * 0.75)}
    elif n_adj == "low":
        npk = {**npk, "N": int(npk["N"] * 1.15)}

    # Fertilizer schedule (split application)
    schedule = [
        FertilizerSchedule(
            stage="Basal (at sowing)",
            timing="Day 0",
            npk_kg_per_acre={"N": int(npk["N"] * 0.5), "P": npk["P"], "K": npk["K"]},
            note="Apply full P and K with half N as DAP + Urea basal.",
        ),
        FertilizerSchedule(
            stage="1st Top Dress",
            timing="21–25 days after sowing",
            npk_kg_per_acre={"N": int(npk["N"] * 0.3), "P": 0, "K": 0},
            note="Apply as urea @ CRI stage.",
        ),
        FertilizerSchedule(
            stage="2nd Top Dress",
            timing="45–50 days after sowing",
            npk_kg_per_acre={"N": int(npk["N"] * 0.2), "P": 0, "K": 0},
            note="Apply remaining nitrogen at boot leaf stage.",
        ),
    ]

    zinc_msg = None
    if zone_data["zinc"] == "deficient":
        zinc_msg = "Zinc deficiency detected in this zone. Apply Zinc Sulphate @ 10 kg/acre once every 3 years."

    return SoilResponse(
        crop=req.crop,
        zone=zone,
        npk_recommendation=npk,
        fertilizer_schedule=schedule,
        zinc_correction=zinc_msg,
        stubble_alternatives=STUBBLE_ALTERNATIVES.get(crop_key),
        organic_tip="Add 2–4 tonnes of FYM (Farm Yard Manure) per acre to improve organic carbon and soil health.",
    )


@router.post("/irrigation", response_model=IrrigationScheduleResponse)
async def get_irrigation_schedule(req: SoilRequest):
    """
    Punjab-specific irrigation schedule aligned with free electricity slots.
    Accounts for water table depth (shallow = less irrigation needed) and
    recommends morning (5–8 AM) or night (10 PM–1 AM) tube-well windows.
    """
    from app.services.crop_knowledge import DISTRICT_ZONE_MAP

    crop_key = req.crop.lower().replace(" ", "_")
    irr_data = CROP_IRRIGATION.get(crop_key, {
        "irrigations": 4, "litres_per_irrigation": 40000,
        "critical_stages": ["sowing", "vegetative", "flowering", "maturity"],
    })

    total = irr_data["irrigations"]
    litres = irr_data["litres_per_irrigation"]

    # Reduce irrigation count if shallow water table (< 15 ft)
    depth = req.water_table_depth_ft
    water_source_tip = "Tube-well irrigation recommended. Use free electricity slots."
    if depth is not None and depth < 15:
        total = max(1, int(total * 0.75))
        water_source_tip = (
            f"Shallow water table detected ({depth:.0f} ft). "
            "Reduce irrigation frequency to avoid waterlogging. "
            "Prefer drip/sprinkler irrigation."
        )
    elif depth is not None and depth > 60:
        water_source_tip = (
            f"Deep water table ({depth:.0f} ft). Prioritise canal water if available. "
            "Use night electricity slot (10 PM–1 AM) for tube-well to reduce costs."
        )

    # Alternate morning / night slots
    slots_cycle = [
        ("morning", "05:00–08:00 AM"),
        ("night",   "10:00 PM–01:00 AM"),
    ]
    stages = irr_data["critical_stages"]

    schedule: List[IrrigationScheduleItem] = []
    for i in range(total):
        slot_name, slot_window = slots_cycle[i % 2]
        stage = stages[i] if i < len(stages) else f"Irrigation {i + 1}"
        schedule.append(IrrigationScheduleItem(
            irrigation_number=i + 1,
            critical_stage=stage,
            recommended_slot=slot_name,
            slot_window=slot_window,
            water_litres_per_acre=litres,
            notes=f"Apply {litres:,} L/acre at {stage} stage using {slot_name} free electricity window.",
        ))

    return IrrigationScheduleResponse(
        crop=req.crop,
        district=req.district,
        total_irrigations=total,
        total_water_litres_per_acre=total * litres,
        water_source_tip=water_source_tip,
        schedule=schedule,
        electricity_reminder=(
            "Punjab free electricity for tube-wells: Morning 05:00–08:00 and Night 22:00–01:00. "
            "Irrigating outside these slots incurs full tariff."
        ),
    )


@router.get("/zones")
async def get_zones():
    """Punjab soil zone profiles."""
    return {
        "zones": [
            {
                "id": "majha",
                "name": "Majha",
                "name_pa": "ਮਾਝਾ",
                "districts": ["Amritsar", "Gurdaspur", "Pathankot", "Tarn Taran"],
                "soil": "Loamy, low organic matter",
            },
            {
                "id": "malwa",
                "name": "Malwa",
                "name_pa": "ਮਾਲਵਾ",
                "districts": ["Ludhiana", "Bathinda", "Mansa", "Muktsar", "Sangrur"],
                "soil": "Sandy-loam, zinc deficient",
            },
            {
                "id": "doaba",
                "name": "Doaba",
                "name_pa": "ਦੋਆਬਾ",
                "districts": ["Jalandhar", "Hoshiarpur", "Nawanshahr", "Kapurthala"],
                "soil": "Alluvial, waterlogging tendency",
            },
        ]
    }


STUBBLE_ALTERNATIVES = {
    "rice": [
        {
            "method": "Happy Seeder",
            "description": "Direct wheat sowing into standing rice stubble. No burning needed.",
            "description_pa": "ਝੋਨੇ ਦੀ ਨਾੜ ਵਿੱਚ ਸਿੱਧੀ ਕਣਕ ਦੀ ਬਿਜਾਈ।",
            "govt_incentive": "₹2,500/acre under PPCB scheme",
        },
        {
            "method": "Bio-Decomposer",
            "description": "PUSA bio-decomposer converts stubble to compost in 20 days.",
            "description_pa": "PUSA ਬਾਇਓ-ਡੀਕੰਪੋਜ਼ਰ 20 ਦਿਨਾਂ ਵਿੱਚ ਨਾੜ ਨੂੰ ਖਾਦ ਬਣਾਉਂਦਾ ਹੈ।",
            "govt_incentive": "Free capsules from Punjab Agriculture Department",
        },
        {
            "method": "Crop Switching",
            "description": "Grow maize or vegetables instead of rice to eliminate stubble issue.",
            "description_pa": "ਝੋਨੇ ਦੀ ਥਾਂ ਮੱਕੀ ਜਾਂ ਸਬਜ਼ੀਆਂ ਉਗਾਓ।",
            "govt_incentive": "₹17,500/acre crop diversification incentive",
        },
    ]
}


class SoilRequest(BaseModel):
    crop: str
    district: str
    soil_zone: Optional[str] = None
    ph: Optional[float] = None
    nitrogen: Optional[str] = None   # low | medium | high
    phosphorus: Optional[str] = None
    potassium: Optional[str] = None
    land_size_acres: Optional[float] = 2.0


class FertilizerSchedule(BaseModel):
    stage: str
    timing: str
    npk_kg_per_acre: dict
    note: str


class SoilResponse(BaseModel):
    crop: str
    zone: str
    npk_recommendation: dict
    fertilizer_schedule: List[FertilizerSchedule]
    zinc_correction: Optional[str]
    stubble_alternatives: Optional[list]
    organic_tip: str


@router.post("/recommend", response_model=SoilResponse)
async def get_soil_recommendation(req: SoilRequest):
    """
    Soil health + fertilizer recommendation for Punjab farmers.
    Includes NPK doses, schedule, zinc correction, and stubble management.
    """
    from app.services.crop_knowledge import DISTRICT_ZONE_MAP

    zone = req.soil_zone or DISTRICT_ZONE_MAP.get(req.district.lower(), "malwa")
    zone_data = ZONE_SOIL_DEFAULTS.get(zone, ZONE_SOIL_DEFAULTS["malwa"])

    crop_key = req.crop.lower().replace(" ", "_")
    npk = CROP_NPK.get(crop_key, {"N": 40, "P": 20, "K": 12})

    # Adjust N if soil nitrogen is high (avoid over-application)
    n_adj = req.nitrogen or zone_data["n"]
    if n_adj == "high":
        npk = {**npk, "N": int(npk["N"] * 0.75)}
    elif n_adj == "low":
        npk = {**npk, "N": int(npk["N"] * 1.15)}

    # Fertilizer schedule (split application)
    schedule = [
        FertilizerSchedule(
            stage="Basal (at sowing)",
            timing="Day 0",
            npk_kg_per_acre={"N": int(npk["N"] * 0.5), "P": npk["P"], "K": npk["K"]},
            note="Apply full P and K with half N as DAP + Urea basal.",
        ),
        FertilizerSchedule(
            stage="1st Top Dress",
            timing="21–25 days after sowing",
            npk_kg_per_acre={"N": int(npk["N"] * 0.3), "P": 0, "K": 0},
            note="Apply as urea @ CRI stage.",
        ),
        FertilizerSchedule(
            stage="2nd Top Dress",
            timing="45–50 days after sowing",
            npk_kg_per_acre={"N": int(npk["N"] * 0.2), "P": 0, "K": 0},
            note="Apply remaining nitrogen at boot leaf stage.",
        ),
    ]

    zinc_msg = None
    if zone_data["zinc"] == "deficient":
        zinc_msg = "Zinc deficiency detected in this zone. Apply Zinc Sulphate @ 10 kg/acre once every 3 years."

    return SoilResponse(
        crop=req.crop,
        zone=zone,
        npk_recommendation=npk,
        fertilizer_schedule=schedule,
        zinc_correction=zinc_msg,
        stubble_alternatives=STUBBLE_ALTERNATIVES.get(crop_key),
        organic_tip="Add 2–4 tonnes of FYM (Farm Yard Manure) per acre to improve organic carbon and soil health.",
    )


@router.get("/zones")
async def get_zones():
    """Punjab soil zone profiles."""
    return {
        "zones": [
            {
                "id": "majha",
                "name": "Majha",
                "name_pa": "ਮਾਝਾ",
                "districts": ["Amritsar", "Gurdaspur", "Pathankot", "Tarn Taran"],
                "soil": "Loamy, low organic matter",
            },
            {
                "id": "malwa",
                "name": "Malwa",
                "name_pa": "ਮਾਲਵਾ",
                "districts": ["Ludhiana", "Bathinda", "Mansa", "Muktsar", "Sangrur"],
                "soil": "Sandy-loam, zinc deficient",
            },
            {
                "id": "doaba",
                "name": "Doaba",
                "name_pa": "ਦੋਆਬਾ",
                "districts": ["Jalandhar", "Hoshiarpur", "Nawanshahr", "Kapurthala"],
                "soil": "Alluvial, waterlogging tendency",
            },
        ]
    }
