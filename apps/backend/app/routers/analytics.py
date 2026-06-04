"""
Analytics Summary Router
Provides a farm-season dashboard with aggregate stats: soil score,
estimated profit, water usage, and active weather alerts for a given
district and crop set. Single API call to power a farmer dashboard.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# ── Static reference data (mirrors values from other routers) ─────────────────
CROP_PROFILES_LITE = {
    "wheat":   {"msp": 2275, "input_cost": 18000, "yield_qtl": 18, "water_mm": 400,  "season": "rabi"},
    "rice":    {"msp": 2300, "input_cost": 28000, "yield_qtl": 22, "water_mm": 1200, "season": "kharif"},
    "maize":   {"msp": 2090, "input_cost": 14000, "yield_qtl": 20, "water_mm": 500,  "season": "kharif"},
    "cotton":  {"msp": 7020, "input_cost": 32000, "yield_qtl": 10, "water_mm": 700,  "season": "kharif"},
    "mustard": {"msp": 5650, "input_cost": 10000, "yield_qtl": 8,  "water_mm": 250,  "season": "rabi"},
    "potato":  {"msp": None, "input_cost": 55000, "yield_qtl": 120,"water_mm": 450,  "season": "rabi"},
    "moong":   {"msp": 8558, "input_cost": 9000,  "yield_qtl": 5,  "water_mm": 250,  "season": "kharif"},
    "sunflower":{"msp": 6760,"input_cost": 12000, "yield_qtl": 7,  "water_mm": 350,  "season": "rabi"},
}

SOIL_HEALTH_GRADES = {
    (9, 10): ("A+", "Excellent"),
    (7,  8): ("A",  "Good"),
    (5,  6): ("B",  "Fair — attention needed"),
    (3,  4): ("C",  "Poor — corrective action required"),
    (0,  2): ("D",  "Critical — urgent treatment needed"),
}


def get_soil_grade(score: int) -> tuple:
    for (lo, hi), (grade, label) in SOIL_HEALTH_GRADES.items():
        if lo <= score <= hi:
            return grade, label
    return "N/A", "Unknown"


class CropStat(BaseModel):
    crop: str
    season: str
    land_acres: float
    estimated_revenue: float
    estimated_profit: float
    water_required_liters: float
    msp_per_quintal: Optional[float]


class AnalyticsSummary(BaseModel):
    district: str
    season: str
    generated_at: str
    total_land_acres: float
    total_estimated_revenue: float
    total_estimated_profit: float
    total_water_liters: float
    avg_profit_per_acre: float
    crop_breakdown: List[CropStat]
    soil_health_score: int
    soil_grade: str
    soil_label: str
    active_alert_count: int
    top_recommendation: str
    top_recommendation_pa: str


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    district: str = Query("ludhiana", description="Punjab district"),
    crops: str = Query("wheat,rice", description="Comma-separated list of crops"),
    land_acres: float = Query(5.0, ge=0.1, le=1000.0, description="Total farm size in acres"),
    soil_health_score: int = Query(6, ge=0, le=10, description="Soil health score (0–10)"),
):
    """
    Farm-season analytics dashboard.

    Aggregates estimated profit, water usage, and soil health score for a
    farmer's crop portfolio. Returns a single summary object to power
    a mobile/web dashboard widget without multiple round-trips.

    - `crops`: comma-separated crop names (e.g. ``wheat,mustard``)
    - `soil_health_score`: pass the score from /soil/health-report
    """
    crop_list = [c.strip().lower() for c in crops.split(",") if c.strip()]
    acres_per_crop = land_acres / max(len(crop_list), 1)

    crop_stats: List[CropStat] = []
    total_revenue = 0.0
    total_profit = 0.0
    total_water = 0.0

    for crop in crop_list:
        profile = CROP_PROFILES_LITE.get(crop)
        if not profile:
            continue

        msp = profile["msp"] or 1000
        revenue = round(msp * profile["yield_qtl"] * acres_per_crop, 2)
        profit = round(revenue - (profile["input_cost"] * acres_per_crop), 2)
        water = round(profile["water_mm"] * 4050 * acres_per_crop, 0)  # mm → litres/acre

        total_revenue += revenue
        total_profit += profit
        total_water += water

        crop_stats.append(CropStat(
            crop=crop.capitalize(),
            season=profile["season"],
            land_acres=round(acres_per_crop, 2),
            estimated_revenue=revenue,
            estimated_profit=profit,
            water_required_liters=water,
            msp_per_quintal=profile["msp"],
        ))

    # Compute summary metrics
    avg_profit = round(total_profit / land_acres, 2) if land_acres > 0 else 0.0
    grade, label = get_soil_grade(soil_health_score)

    # Active alerts (simulated based on soil + season)
    current_month = datetime.now().month
    alert_count = 0
    if soil_health_score < 5:
        alert_count += 2
    if current_month in (6, 7, 8):
        alert_count += 1  # kharif pest season
    if current_month in (12, 1, 2):
        alert_count += 1  # rabi frost risk

    # Top recommendation
    if "rice" in crop_list and len(crop_list) == 1:
        rec_en = "Diversify: replace 50 % rice area with maize or moong to save groundwater."
        rec_pa = "50% ਝੋਨੇ ਦੀ ਥਾਂ ਮੱਕੀ ਜਾਂ ਮੂੰਗ ਲਾਓ — ਧਰਤੀ ਹੇਠਲਾ ਪਾਣੀ ਬਚੇਗਾ।"
    elif soil_health_score < 5:
        rec_en = "Apply FYM (10 t/acre) and green manure before next sowing to restore soil health."
        rec_pa = "ਅਗਲੀ ਬਿਜਾਈ ਤੋਂ ਪਹਿਲਾਂ 10 ਟਨ/ਏਕੜ FYM ਪਾਓ।"
    elif total_profit < 0:
        rec_en = "Consider high-value crops (potato, sunflower) to improve farm profitability."
        rec_pa = "ਆਲੂ ਜਾਂ ਸੂਰਜਮੁਖੀ ਵਰਗੀਆਂ ਉੱਚ-ਮੁੱਲ ਫ਼ਸਲਾਂ ਲਗਾਓ।"
    else:
        rec_en = "Farm looks profitable. Register on e-NAM for better mandi price discovery."
        rec_pa = "ਖੇਤ ਮੁਨਾਫ਼ੇਯੋਗ ਹੈ। e-NAM 'ਤੇ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਕਰੋ।"

    return AnalyticsSummary(
        district=district,
        season="kharif" if datetime.now().month in [6, 7, 8, 9] else "rabi",
        generated_at=datetime.now().isoformat(),
        total_land_acres=land_acres,
        total_estimated_revenue=round(total_revenue, 2),
        total_estimated_profit=round(total_profit, 2),
        total_water_liters=round(total_water, 0),
        avg_profit_per_acre=avg_profit,
        crop_breakdown=crop_stats,
        soil_health_score=soil_health_score,
        soil_grade=grade,
        soil_label=label,
        active_alert_count=alert_count,
        top_recommendation=rec_en,
        top_recommendation_pa=rec_pa,
    )
