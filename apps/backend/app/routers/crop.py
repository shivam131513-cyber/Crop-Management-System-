from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.crop import (
    CropRecommendRequest, CropRecommendResponse,
    CropCalendarMonth, CropCalendarResponse, CalendarActivity,
    ProfitEstimateRequest, ProfitBreakdown,
)
from app.services.crop_service import recommend_crops
from app.services.crop_knowledge import CROP_CALENDAR, DISTRICT_ZONE_MAP, CROP_PROFILES

router = APIRouter()


@router.post("/recommend", response_model=CropRecommendResponse)
async def get_crop_recommendation(req: CropRecommendRequest):
    """
    Get personalized crop recommendations for Punjab farmers.
    Considers soil type, district zone, season, and water availability.
    Returns top-3 crops with Punjab-specific irrigation slots and stubble warning.
    """
    try:
        result = recommend_crops(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seasons")
async def get_seasons():
    """List available crop seasons."""
    return {
        "seasons": [
            {"value": "kharif", "label": "Kharif (Jun–Sep)", "label_hi": "खरीफ", "label_pa": "ਖਰੀਫ਼"},
            {"value": "rabi",   "label": "Rabi (Oct–Mar)",   "label_hi": "रबी",   "label_pa": "ਰਬੀ"},
            {"value": "zaid",   "label": "Zaid (Apr–Jun)",   "label_hi": "ज़ैद",  "label_pa": "ਜ਼ੈਦ"},
        ]
    }


@router.get("/soil-types")
async def get_soil_types():
    """List soil types relevant to Punjab."""
    return {
        "soil_types": [
            {"value": "loamy",      "label": "Loamy",       "label_pa": "ਦੋਮਟ"},
            {"value": "sandy-loam", "label": "Sandy Loam",  "label_pa": "ਰੇਤਲੀ ਦੋਮਟ"},
            {"value": "clay",       "label": "Clay",        "label_pa": "ਮਿੱਟੀ"},
            {"value": "alluvial",   "label": "Alluvial",    "label_pa": "ਕਾਂਪ"},
        ]
    }


@router.get("/calendar", response_model=CropCalendarResponse)
async def get_crop_calendar(
    district: Optional[str] = Query(
        None,
        description="Punjab district name (e.g. ludhiana, amritsar). Used to resolve soil zone.",
    ),
    month: Optional[int] = Query(
        None,
        ge=1, le=12,
        description="Filter to a single month (1-12). Omit for full 12-month calendar.",
    ),
):
    """
    Return a month-wise Punjab crop calendar with sowing, fertilization,
    irrigation, harvest, and pest-watch activities.

    Zone-specific notes are tailored to the farmer's district (Majha / Malwa / Doaba).
    All key tips are provided in English and Punjabi (Gurmukhi).
    """
    # Resolve zone from district
    zone = "malwa"  # default
    if district:
        zone = DISTRICT_ZONE_MAP.get(district.strip().lower(), "malwa")

    # Determine which months to return
    months_to_return = [month] if month else list(range(1, 13))

    calendar_months = []
    for m in months_to_return:
        data = CROP_CALENDAR.get(m)
        if not data:
            raise HTTPException(status_code=404, detail=f"Month {m} not found in calendar.")

        activities = data["activities"]
        calendar_months.append(
            CropCalendarMonth(
                month=m,
                month_name=data["month_name"],
                month_name_hi=data["month_name_hi"],
                month_name_pa=data["month_name_pa"],
                season=data["season"],
                activities=CalendarActivity(
                    sow=activities["sow"],
                    fertilize=activities["fertilize"],
                    irrigate=activities["irrigate"],
                    harvest=activities["harvest"],
                    pest_watch=activities["pest_watch"],
                    general_tip=activities["general_tip"],
                    general_tip_pa=activities["general_tip_pa"],
                ),
                zone_note=data["zone_notes"].get(zone),
            )
        )

    return CropCalendarResponse(
        zone=zone,
        district=district,
        calendar=calendar_months,
    )


@router.post("/profit-estimate", response_model=ProfitBreakdown)
async def get_profit_estimate(req: ProfitEstimateRequest):
    """
    Estimate profit/loss for a given crop and land size.

    - Uses MSP as the default selling price (official Govt. of India rate).
    - If the farmer provides `selling_price_per_quintal`, that is used instead.
    - Crops without a government MSP (e.g. potato, vegetables) use an estimated market price.
    - Returns full cost-revenue breakdown with net profit, margin %, and advice.
    """
    crop_key = req.crop.lower().strip()
    data = CROP_PROFILES.get(crop_key)

    if not data:
        available = ", ".join(CROP_PROFILES.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Crop '{req.crop}' not found. Available crops: {available}",
        )

    if req.land_size_acres <= 0:
        raise HTTPException(status_code=422, detail="land_size_acres must be greater than 0.")

    # Determine the price per quintal to use
    msp = data.get("msp_per_quintal")

    if req.selling_price_per_quintal is not None:
        price = req.selling_price_per_quintal
        price_source = "Market"
    elif msp is not None:
        price = msp
        price_source = "MSP"
    else:
        # No MSP crops: use a rough estimated market price
        # Potato: ₹800/qtl, Vegetables: ₹1200/qtl (conservative)
        estimated_prices = {
            "potato": 800.0,
            "vegetables_mixed": 1200.0,
        }
        price = estimated_prices.get(crop_key, 1000.0)
        price_source = "Estimated"

    # Financial calculations
    input_cost_total = round(data["input_cost_per_acre"] * req.land_size_acres, 2)
    expected_yield_total = round(data["expected_yield_qtl_per_acre"] * req.land_size_acres, 2)
    gross_revenue = round(expected_yield_total * price, 2)
    net_profit = round(gross_revenue - input_cost_total, 2)
    profit_per_acre = round(net_profit / req.land_size_acres, 2)
    profit_margin_pct = round((net_profit / gross_revenue) * 100, 1) if gross_revenue > 0 else 0.0

    # Stubble warning only for rice
    stubble_warning = None
    if not data["stubble_friendly"]:
        stubble_warning = data.get("stubble_warning")

    return ProfitBreakdown(
        crop_name=data["name"],
        crop_name_hi=data["local_name_hi"],
        crop_name_pa=data["local_name_pa"],
        land_size_acres=req.land_size_acres,
        input_cost_total=input_cost_total,
        expected_yield_total_qtl=expected_yield_total,
        price_used_per_quintal=price,
        price_source=price_source,
        gross_revenue=gross_revenue,
        net_profit=net_profit,
        profit_per_acre=profit_per_acre,
        profit_margin_pct=profit_margin_pct,
        is_profitable=net_profit > 0,
        msp_per_quintal=msp,
        stubble_warning=stubble_warning,
        advice=data["advice"],
    )
