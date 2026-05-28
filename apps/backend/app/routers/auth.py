from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class FarmerCreate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    district: str = "ludhiana"
    village: Optional[str] = None
    land_size_acres: Optional[float] = 2.0
    soil_zone: Optional[str] = None
    preferred_language: str = "pa"  # pa | hi | en


class FarmerResponse(BaseModel):
    id: int
    name: Optional[str]
    district: str
    preferred_language: str
    message: str


@router.post("/profile", response_model=FarmerResponse)
async def create_or_update_profile(farmer: FarmerCreate):
    """
    Create or update farmer profile (no auth required for MVP).
    Profile stored locally on device + synced to server when online.
    """
    # In production: upsert to PostgreSQL
    # For demo: return mock response
    return FarmerResponse(
        id=1,
        name=farmer.name or "Kisaan",
        district=farmer.district,
        preferred_language=farmer.preferred_language,
        message="Profile saved successfully. ਪ੍ਰੋਫਾਈਲ ਸੇਵ ਕੀਤੀ ਗਈ।",
    )


@router.get("/profile/{farmer_id}")
async def get_profile(farmer_id: int):
    """Fetch farmer profile."""
    return {
        "id": farmer_id,
        "name": "Demo Farmer",
        "district": "ludhiana",
        "village": "Demo Village",
        "land_size_acres": 3.5,
        "soil_zone": "malwa",
        "preferred_language": "pa",
    }
