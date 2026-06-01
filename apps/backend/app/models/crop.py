from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class Season(str, Enum):
    kharif = "kharif"
    rabi = "rabi"
    zaid = "zaid"


class WaterAvailability(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class SoilZone(str, Enum):
    majha = "majha"
    malwa = "malwa"
    doaba = "doaba"


class CropRecommendRequest(BaseModel):
    district: str
    soil_type: str                          # loamy | sandy-loam | clay | alluvial
    season: Season
    water_availability: WaterAvailability
    land_size_acres: Optional[float] = 2.0
    soil_ph: Optional[float] = None
    soil_nitrogen: Optional[str] = None     # low | medium | high
    soil_phosphorus: Optional[str] = None
    soil_potassium: Optional[str] = None


class CropProfile(BaseModel):
    name: str
    local_name_hi: str
    local_name_pa: str
    expected_yield_qtl_per_acre: float
    water_req: str                # low | medium | high
    duration_days: int
    msp_per_quintal: Optional[float]
    input_cost_per_acre: float
    suitability_score: float      # 0–1
    stubble_friendly: bool
    advice: str


class CropRecommendResponse(BaseModel):
    recommended_crops: List[CropProfile]
    irrigation_slots: Optional[List[str]] = None   # Punjab electricity windows
    stubble_warning: Optional[str] = None
    season_tip: Optional[str] = None


class CalendarActivity(BaseModel):
    sow: List[str]
    fertilize: List[str]
    irrigate: List[str]
    harvest: List[str]
    pest_watch: List[str]
    general_tip: str
    general_tip_pa: str


class CropCalendarMonth(BaseModel):
    month: int
    month_name: str
    month_name_hi: str
    month_name_pa: str
    season: str
    activities: CalendarActivity
    zone_note: Optional[str] = None   # filtered for requested zone


class CropCalendarResponse(BaseModel):
    zone: str
    district: Optional[str] = None
    calendar: List[CropCalendarMonth]


# ── Profit Estimate Models ────────────────────────────────────────────────────

class ProfitEstimateRequest(BaseModel):
    crop: str               # must match a key in CROP_PROFILES (e.g. "wheat", "rice")
    land_size_acres: float  # farmer's field size
    selling_price_per_quintal: Optional[float] = None  # if None, MSP is used


class ProfitBreakdown(BaseModel):
    crop_name: str
    crop_name_hi: str
    crop_name_pa: str
    land_size_acres: float
    input_cost_total: float           # input_cost_per_acre * land_size_acres
    expected_yield_total_qtl: float   # yield_per_acre * land_size_acres
    price_used_per_quintal: float     # MSP or user-provided
    price_source: str                 # "MSP" | "Market" | "Estimated"
    gross_revenue: float              # yield_total * price_per_quintal
    net_profit: float                 # gross_revenue - input_cost_total
    profit_per_acre: float            # net_profit / land_size_acres
    profit_margin_pct: float          # (net_profit / gross_revenue) * 100
    is_profitable: bool
    msp_per_quintal: Optional[float]  # for reference
    stubble_warning: Optional[str] = None
    advice: str
