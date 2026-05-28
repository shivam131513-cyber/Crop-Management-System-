from fastapi import APIRouter, HTTPException
from app.models.crop import CropRecommendRequest, CropRecommendResponse
from app.services.crop_service import recommend_crops

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
