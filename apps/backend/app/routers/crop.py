from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.crop import (
    CropRecommendRequest, CropRecommendResponse,
    CropCalendarMonth, CropCalendarResponse, CalendarActivity,
)
from app.services.crop_service import recommend_crops
from app.services.crop_knowledge import CROP_CALENDAR, DISTRICT_ZONE_MAP

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
