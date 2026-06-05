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


# ---------------------------------------------------------------------------
# Seasonal crop tips — month-specific, Punjab-focused
# ---------------------------------------------------------------------------

MONTHLY_TIPS: dict[int, dict] = {
    1:  {"title": "January Tips", "title_pa": "ਜਨਵਰੀ ਸਲਾਹ",
         "tips": ["Scout wheat fields weekly for yellow and brown rust.", "Apply 2nd urea top-dress for wheat at tillering stage.", "Sow vegetables (peas, carrot) in open fields."],
         "tips_pa": ["ਕਣਕ ਦੇ ਖੇਤਾਂ ਵਿੱਚ ਹਫ਼ਤੇਵਾਰ ਰਤੂਏ ਦੀ ਜਾਂਚ ਕਰੋ।", "ਕਣਕ ਨੂੰ ਟਿਲਰਿੰਗ ਵੇਲੇ ਦੂਜੀ ਯੂਰੀਆ ਖੁਰਾਕ ਦਿਓ।", "ਮਟਰ, ਗਾਜਰ ਖੁੱਲ੍ਹੇ ਖੇਤਾਂ ਵਿੱਚ ਬੀਜੋ।"]},
    2:  {"title": "February Tips", "title_pa": "ਫਰਵਰੀ ਸਲਾਹ",
         "tips": ["Apply last nitrogen dose to wheat.", "Monitor mustard for aphid infestation.", "Protect crops from late frost (cover seedlings at night)."],
         "tips_pa": ["ਕਣਕ ਨੂੰ ਆਖਰੀ ਨਾਈਟ੍ਰੋਜਨ ਖੁਰਾਕ ਦਿਓ।", "ਸਰ੍ਹੋਂ ਵਿੱਚ ਮਾਹੂ ਦੀ ਜਾਂਚ ਕਰੋ।", "ਦੇਰੀ ਨਾਲ ਠੰਡ ਤੋਂ ਬਚਾਓ — ਰਾਤ ਨੂੰ ਪੌਦੇ ਢੱਕੋ।"]},
    3:  {"title": "March Tips", "title_pa": "ਮਾਰਚ ਸਲਾਹ",
         "tips": ["Harvest mustard when pods turn yellow-brown.", "Stop wheat irrigation 3 weeks before harvest.", "Prepare land for summer vegetables."],
         "tips_pa": ["ਸਰ੍ਹੋਂ ਦੀਆਂ ਫਲੀਆਂ ਪੀਲੀਆਂ-ਭੂਰੀਆਂ ਹੋਣ 'ਤੇ ਵੱਢੋ।", "ਕਟਾਈ ਤੋਂ 3 ਹਫ਼ਤੇ ਪਹਿਲਾਂ ਕਣਕ ਦੀ ਸਿੰਜਾਈ ਬੰਦ ਕਰੋ।", "ਗਰਮੀ ਦੀਆਂ ਸਬਜ਼ੀਆਂ ਲਈ ਜ਼ਮੀਨ ਤਿਆਰ ਕਰੋ।"]},
    4:  {"title": "April Tips", "title_pa": "ਅਪ੍ਰੈਲ ਸਲਾਹ",
         "tips": ["Harvest wheat at 12-14% moisture to avoid shattering.", "Begin land preparation for kharif (paddy/maize).", "Apply bio-decomposer on wheat stubble."],
         "tips_pa": ["ਕਣਕ 12-14% ਨਮੀ 'ਤੇ ਵੱਢੋ।", "ਖ਼ਰੀਫ਼ (ਝੋਨਾ/ਮੱਕੀ) ਲਈ ਜ਼ਮੀਨ ਤਿਆਰ ਕਰੋ।", "ਕਣਕ ਦੀ ਨਾੜ 'ਤੇ ਬਾਇਓ-ਡੀਕੰਪੋਜ਼ਰ ਲਗਾਓ।"]},
    5:  {"title": "May Tips", "title_pa": "ਮਈ ਸਲਾਹ",
         "tips": ["Sow moong/mash (Zaid crop) in early May.", "Deep plough fields to expose soil pests to heat.", "Procure paddy nursery seeds — use PR-126 or Pusa Basmati 1509."],
         "tips_pa": ["ਮਈ ਦੇ ਸ਼ੁਰੂ ਵਿੱਚ ਮੂੰਗੀ/ਮਾਂਹ ਬੀਜੋ।", "ਮਿੱਟੀ ਦੇ ਕੀੜੇ ਨਸ਼ਟ ਕਰਨ ਲਈ ਡੂੰਘੀ ਵਾਹੀ ਕਰੋ।", "ਝੋਨੇ ਦੀ ਨਰਸਰੀ ਲਈ PR-126 ਜਾਂ ਪੂਸਾ ਬਾਸਮਤੀ 1509 ਬੀਜ ਲਓ।"]},
    6:  {"title": "June Tips", "title_pa": "ਜੂਨ ਸਲਾਹ",
         "tips": ["Sow paddy nursery (1st–15th June). Transplant after 25-30 days.", "Sow maize in first week of June.", "Apply DAP as basal fertilizer for kharif crops."],
         "tips_pa": ["ਝੋਨੇ ਦੀ ਨਰਸਰੀ ਲਾਓ (1-15 ਜੂਨ)। 25-30 ਦਿਨ ਬਾਅਦ ਲਵਾਈ।", "ਮੱਕੀ ਜੂਨ ਦੇ ਪਹਿਲੇ ਹਫ਼ਤੇ ਬੀਜੋ।", "ਖ਼ਰੀਫ਼ ਫ਼ਸਲਾਂ ਲਈ ਅਧਾਰ ਖੁਰਾਕ ਵਜੋਂ DAP ਪਾਓ।"]},
    7:  {"title": "July Tips", "title_pa": "ਜੁਲਾਈ ਸਲਾਹ",
         "tips": ["Transplant paddy before July 15 (PAU recommendation).", "Monitor fall armyworm in maize weekly.", "Apply zinc sulphate if leaves show interveinal chlorosis."],
         "tips_pa": ["15 ਜੁਲਾਈ ਤੋਂ ਪਹਿਲਾਂ ਝੋਨੇ ਦੀ ਲਵਾਈ ਕਰੋ (PAU ਸਿਫਾਰਸ਼)।", "ਮੱਕੀ ਵਿੱਚ ਫ਼ੌਜੀ ਸੁੰਡੀ ਦੀ ਹਫ਼ਤੇਵਾਰ ਜਾਂਚ ਕਰੋ।", "ਪੱਤੇ ਪੀਲੇ ਹੋਣ ਤੇ ਜ਼ਿੰਕ ਸਲਫ਼ੇਟ ਲਗਾਓ।"]},
    8:  {"title": "August Tips", "title_pa": "ਅਗਸਤ ਸਲਾਹ",
         "tips": ["Watch for BPH (brown plant hopper) in rice. Drain fields for 3-4 days.", "Apply 2nd urea dose to paddy (45-50 days after transplant).", "Install pheromone traps for cotton bollworm @ 5/acre."],
         "tips_pa": ["ਝੋਨੇ ਵਿੱਚ ਭੂਰੇ ਕੀੜੇ (BPH) ਦੀ ਜਾਂਚ ਕਰੋ। 3-4 ਦਿਨ ਪਾਣੀ ਬੰਦ ਕਰੋ।", "ਲਵਾਈ ਤੋਂ 45-50 ਦਿਨ ਬਾਅਦ ਝੋਨੇ ਨੂੰ ਦੂਜੀ ਯੂਰੀਆ ਖੁਰਾਕ ਦਿਓ।", "ਕਪਾਹ ਵਿੱਚ 5/ਏਕੜ ਫੇਰੋਮੋਨ ਟਰੈਪ ਲਗਾਓ।"]},
    9:  {"title": "September Tips", "title_pa": "ਸਤੰਬਰ ਸਲਾਹ",
         "tips": ["Harvest maize at 18-20% moisture to reduce field losses.", "Drain paddy fields 15-20 days before harvest.", "Procure zero-till or happy seeder machines in advance."],
         "tips_pa": ["ਮੱਕੀ 18-20% ਨਮੀ 'ਤੇ ਵੱਢੋ।", "ਕਟਾਈ ਤੋਂ 15-20 ਦਿਨ ਪਹਿਲਾਂ ਝੋਨੇ ਦੇ ਖੇਤਾਂ ਵਿੱਚੋਂ ਪਾਣੀ ਕੱਢੋ।", "ਜ਼ੀਰੋ-ਟਿੱਲ ਜਾਂ ਹੈਪੀ ਸੀਡਰ ਮਸ਼ੀਨਾਂ ਪਹਿਲਾਂ ਤੋਂ ਬੁੱਕ ਕਰੋ।"]},
    10: {"title": "October Tips", "title_pa": "ਅਕਤੂਬਰ ਸਲਾਹ",
         "tips": ["Sow wheat using Zero-Till Drill after paddy harvest.", "Apply PAU bio-decomposer on paddy stubble (do NOT burn).", "Sow potato (Oct 15 – Nov 15) using certified seed."],
         "tips_pa": ["ਝੋਨੇ ਤੋਂ ਬਾਅਦ ਜ਼ੀਰੋ-ਟਿੱਲ ਨਾਲ ਕਣਕ ਬੀਜੋ।", "ਝੋਨੇ ਦੀ ਨਾੜ 'ਤੇ PAU ਬਾਇਓ-ਡੀਕੰਪੋਜ਼ਰ ਲਗਾਓ — ਸਾੜੋ ਨਾ।", "ਪ੍ਰਮਾਣਿਤ ਬੀਜ ਨਾਲ ਆਲੂ ਬੀਜੋ (15 ਅਕਤੂਬਰ – 15 ਨਵੰਬਰ)।"]},
    11: {"title": "November Tips", "title_pa": "ਨਵੰਬਰ ਸਲਾਹ",
         "tips": ["Apply basal fertilizer (DAP + urea) for wheat at sowing.", "Sow mustard (Raya/Gobhi sarson) before Nov 15.", "Do not burn paddy stubble — ₹2,500/acre incentive available."],
         "tips_pa": ["ਕਣਕ ਬੀਜਾਈ ਵੇਲੇ DAP + ਯੂਰੀਆ ਅਧਾਰ ਖੁਰਾਕ ਦਿਓ।", "15 ਨਵੰਬਰ ਤੋਂ ਪਹਿਲਾਂ ਸਰ੍ਹੋਂ ਬੀਜੋ।", "ਪਰਾਲੀ ਨਾ ਸਾੜੋ — ₹2,500/ਏਕੜ ਪ੍ਰੋਤਸਾਹਨ ਮਿਲਦਾ ਹੈ।"]},
    12: {"title": "December Tips", "title_pa": "ਦਸੰਬਰ ਸਲਾਹ",
         "tips": ["Apply 1st urea top-dress to wheat at CRI stage (21 days after sowing).", "Irrigate wheat at crown root initiation stage.", "Protect potato crop from late blight using Mancozeb sprays."],
         "tips_pa": ["ਕਣਕ ਨੂੰ CRI ਅਵਸਥਾ (21 ਦਿਨ) 'ਤੇ ਪਹਿਲੀ ਯੂਰੀਆ ਖੁਰਾਕ ਦਿਓ।", "CRI ਅਵਸਥਾ 'ਤੇ ਕਣਕ ਦੀ ਸਿੰਜਾਈ ਕਰੋ।", "ਝੁਲਸ ਰੋਗ ਤੋਂ ਬਚਾਓ ਲਈ ਆਲੂ 'ਤੇ ਮੈਨਕੋਜ਼ੇਬ ਸਪਰੇਅ ਕਰੋ।"]},
}


@router.get("/tips")
async def get_seasonal_tips(
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (1-12). Defaults to current month."),
    lang: Optional[str] = Query("pa", description="Language: pa | en"),
):
    """
    Return 3 actionable farm management tips for the given month.
    Tailored to Punjab's crop calendar (Rabi/Kharif/Zaid cycle).
    All tips available in Punjabi (Gurmukhi) and English.
    """
    from datetime import date as _date
    target = month or _date.today().month
    data = MONTHLY_TIPS.get(target)
    if not data:
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=404, detail=f"No tips found for month {target}.")

    tips_out = data["tips_pa"] if lang == "pa" else data["tips"]
    return {
        "month": target,
        "title": data["title_pa"] if lang == "pa" else data["title"],
        "language": lang,
        "tips": tips_out,
        "tips_en": data["tips"],
        "tips_pa": data["tips_pa"],
        "source": "PAU (Punjab Agricultural University) seasonal advisory",
    }
