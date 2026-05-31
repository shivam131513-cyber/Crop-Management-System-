from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

router = APIRouter()

# Punjab MSP data (2024–25)
MSP_2024 = {
    "wheat":     2275.0,
    "rice":      2300.0,
    "maize":     2090.0,
    "cotton":    7020.0,
    "mustard":   5650.0,
    "sunflower": 6760.0,
    "moong":     8558.0,
    "groundnut": 6377.0,
}

# Mock mandi price data (fallback when Agmarknet unavailable)
MOCK_MANDI_PRICES = {
    "ludhiana": {
        "wheat":   {"price": 2310.0, "trend": "+2.5%"},
        "rice":    {"price": 2280.0, "trend": "-0.8%"},
        "maize":   {"price": 2150.0, "trend": "+4.2%"},
        "mustard": {"price": 5720.0, "trend": "+1.1%"},
        "cotton":  {"price": 6850.0, "trend": "-2.4%"},
    },
    "amritsar": {
        "wheat":   {"price": 2290.0, "trend": "+1.8%"},
        "rice":    {"price": 2275.0, "trend": "0.0%"},
        "potato":  {"price": 1200.0, "trend": "+8.5%"},
    },
    "bathinda": {
        "cotton":  {"price": 6900.0, "trend": "+1.2%"},
        "wheat":   {"price": 2300.0, "trend": "+2.0%"},
        "mustard": {"price": 5680.0, "trend": "+0.5%"},
    },
    "jalandhar": {
        "wheat":   {"price": 2285.0, "trend": "+1.5%"},
        "potato":  {"price": 1150.0, "trend": "+10.2%"},
        "rice":    {"price": 2260.0, "trend": "-1.2%"},
    },
    "sangrur": {
        "wheat":   {"price": 2295.0, "trend": "+1.9%"},
        "rice":    {"price": 2270.0, "trend": "-0.5%"},
        "cotton":  {"price": 6780.0, "trend": "-1.8%"},
        "maize":   {"price": 2100.0, "trend": "+3.1%"},
        "mustard": {"price": 5700.0, "trend": "+0.8%"},
    },
}


def generate_price_history(base_price: float, days: int = 7) -> List[dict]:
    """Generate synthetic price trend for demo."""
    history = []
    price = base_price * 0.96
    for i in range(days):
        change = random.uniform(-0.02, 0.03)
        price = round(price * (1 + change), 2)
        date = (datetime.now() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        history.append({"date": date, "price": price})
    return history


class PriceCard(BaseModel):
    crop: str
    crop_pa: str
    mandi: str
    district: str
    price_per_quintal: float
    msp_per_quintal: Optional[float]
    above_msp: Optional[bool]
    trend: str
    price_history: List[dict]


class AlertRequest(BaseModel):
    crop: str
    district: str
    current_price: Optional[float] = None  # if provided, use instead of mock data


class PriceAlertResponse(BaseModel):
    crop: str
    district: str
    current_price: float
    msp: Optional[float]
    below_msp: bool
    deficit_per_quintal: Optional[float]
    severity: str              # "ok" | "warning" | "critical"
    message: str
    message_pa: str
    recommended_actions: List[str]


@router.get("/prices")
async def get_prices(
    district: str = Query("ludhiana", description="Punjab district"),
    crop: Optional[str] = Query(None, description="Filter by crop"),
):
    """
    Mandi prices for Punjab districts.
    Compares with MSP and shows 7-day price trend.
    Falls back to curated mock data if Agmarknet unavailable.
    """
    district_lower = district.lower()
    mandi_data = MOCK_MANDI_PRICES.get(district_lower, MOCK_MANDI_PRICES["ludhiana"])

    crop_pa_map = {
        "wheat": "ਕਣਕ", "rice": "ਚੌਲ", "maize": "ਮੱਕੀ",
        "cotton": "ਕਪਾਹ", "mustard": "ਸਰ੍ਹੋਂ", "potato": "ਆਲੂ",
        "moong": "ਮੂੰਗ", "groundnut": "ਮੂੰਗਫਲੀ",
    }

    results = []
    for crop_name, price_data in mandi_data.items():
        if crop and crop.lower() != crop_name:
            continue
        msp = MSP_2024.get(crop_name)
        price = price_data["price"]
        history = generate_price_history(price)
        results.append(PriceCard(
            crop=crop_name.capitalize(),
            crop_pa=crop_pa_map.get(crop_name, crop_name),
            mandi=f"{district.capitalize()} Grain Market",
            district=district,
            price_per_quintal=price,
            msp_per_quintal=msp,
            above_msp=(price >= msp) if msp else None,
            trend=price_data["trend"],
            price_history=history,
        ))

    return {
        "district": district,
        "last_updated": datetime.now().isoformat(),
        "source": "Agmarknet (mock fallback)",
        "prices": [r.dict() for r in results],
    }


@router.post("/alert", response_model=PriceAlertResponse)
async def check_price_alert(req: AlertRequest):
    """
    Check if a crop's mandi price is below MSP and return a structured alert.
    Farmers can use this to decide whether to hold stock or sell immediately.
    Provides Punjabi message + recommended actions (PM Fasal Bima, helplines).
    """
    crop_lower = req.crop.lower()
    district_lower = req.district.lower()

    # Resolve current price: use provided value or look up mock data
    if req.current_price is not None:
        price = req.current_price
    else:
        district_data = MOCK_MANDI_PRICES.get(district_lower, MOCK_MANDI_PRICES["ludhiana"])
        price_entry = district_data.get(crop_lower)
        if price_entry is None:
            price = MSP_2024.get(crop_lower, 2000.0)  # fallback
        else:
            price = price_entry["price"]

    msp = MSP_2024.get(crop_lower)
    below_msp = (msp is not None) and (price < msp)
    deficit = round(msp - price, 2) if (msp and below_msp) else None

    if not msp:
        severity = "ok"
        message = f"{req.crop.capitalize()} has no MSP. Current price: ₹{price}/quintal."
        message_pa = f"ਇਸ ਫ਼ਸਲ ਦਾ MSP ਨਿਰਧਾਰਿਤ ਨਹੀਂ। ਮੌਜੂਦਾ ਭਾਅ: ₹{price}/ਕੁਇੰਟਲ।"
        actions = ["Check local mandi rates daily.", "Consider direct buyer or FPO sale."]
    elif below_msp:
        severity = "critical" if deficit and deficit > 200 else "warning"
        message = f"⚠️ {req.crop.capitalize()} price ₹{price}/qtl is ₹{deficit} BELOW MSP (₹{msp}). Do not sell yet."
        message_pa = f"⚠️ ਭਾਅ ₹{price}/ਕੁਇੰਟਲ — MSP ₹{msp} ਤੋਂ ₹{deficit} ਘੱਟ। ਹੁਣ ਨਾ ਵੇਚੋ।"
        actions = [
            f"Contact Punjab Mandi Board helpline: 1800-180-1551",
            "Register on e-NAM (enam.gov.in) for better price discovery.",
            "Store grain in PACS/cooperative warehouse for 2–4 weeks.",
            "Claim PM Fasal Bima Yojana if crop damage caused the loss.",
            f"Nearest Procurement Centre: {req.district.capitalize()} district office.",
        ]
    else:
        surplus = round(price - msp, 2)
        severity = "ok"
        message = f"✅ {req.crop.capitalize()} price ₹{price}/qtl is ₹{surplus} ABOVE MSP. Good time to sell."
        message_pa = f"✅ ਭਾਅ ₹{price}/ਕੁਇੰਟਲ — MSP ਤੋਂ ₹{surplus} ਵੱਧ। ਵੇਚਣ ਦਾ ਚੰਗਾ ਸਮਾਂ।"
        actions = [
            "Sell within 2–3 days to lock in the premium.",
            "Check e-NAM for even higher bids from other mandis.",
        ]

    return PriceAlertResponse(
        crop=req.crop,
        district=req.district,
        current_price=price,
        msp=msp,
        below_msp=below_msp,
        deficit_per_quintal=deficit,
        severity=severity,
        message=message,
        message_pa=message_pa,
        recommended_actions=actions,
    )


@router.get("/msp")
async def get_msp():
    """Current Minimum Support Prices (MSP) 2024–25."""
    return {
        "season": "2024-25",
        "msp": [
            {"crop": k, "msp_per_quintal": v, "crop_pa": {"wheat": "ਕਣਕ", "rice": "ਚੌਲ",
             "maize": "ਮੱਕੀ", "cotton": "ਕਪਾਹ", "mustard": "ਸਰ੍ਹੋਂ",
             "sunflower": "ਸੂਰਜਮੁਖੀ", "moong": "ਮੂੰਗ", "groundnut": "ਮੂੰਗਫਲੀ"}.get(k, k)}
            for k, v in MSP_2024.items()
        ]
    }



def generate_price_history(base_price: float, days: int = 7) -> List[dict]:
    """Generate synthetic price trend for demo."""
    history = []
    price = base_price * 0.96
    for i in range(days):
        change = random.uniform(-0.02, 0.03)
        price = round(price * (1 + change), 2)
        date = (datetime.now() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        history.append({"date": date, "price": price})
    return history


class PriceCard(BaseModel):
    crop: str
    crop_pa: str
    mandi: str
    district: str
    price_per_quintal: float
    msp_per_quintal: Optional[float]
    above_msp: Optional[bool]
    trend: str
    price_history: List[dict]


@router.get("/prices")
async def get_prices(
    district: str = Query("ludhiana", description="Punjab district"),
    crop: Optional[str] = Query(None, description="Filter by crop"),
):
    """
    Mandi prices for Punjab districts.
    Compares with MSP and shows 7-day price trend.
    Falls back to curated mock data if Agmarknet unavailable.
    """
    district_lower = district.lower()
    mandi_data = MOCK_MANDI_PRICES.get(district_lower, MOCK_MANDI_PRICES["ludhiana"])

    crop_pa_map = {
        "wheat": "ਕਣਕ", "rice": "ਚੌਲ", "maize": "ਮੱਕੀ",
        "cotton": "ਕਪਾਹ", "mustard": "ਸਰ੍ਹੋਂ", "potato": "ਆਲੂ",
        "moong": "ਮੂੰਗ", "groundnut": "ਮੂੰਗਫਲੀ",
    }

    results = []
    for crop_name, price_data in mandi_data.items():
        if crop and crop.lower() != crop_name:
            continue
        msp = MSP_2024.get(crop_name)
        price = price_data["price"]
        history = generate_price_history(price)
        results.append(PriceCard(
            crop=crop_name.capitalize(),
            crop_pa=crop_pa_map.get(crop_name, crop_name),
            mandi=f"{district.capitalize()} Grain Market",
            district=district,
            price_per_quintal=price,
            msp_per_quintal=msp,
            above_msp=(price >= msp) if msp else None,
            trend=price_data["trend"],
            price_history=history,
        ))

    return {
        "district": district,
        "last_updated": datetime.now().isoformat(),
        "source": "Agmarknet (mock fallback)",
        "prices": [r.dict() for r in results],
    }


@router.get("/msp")
async def get_msp():
    """Current Minimum Support Prices (MSP) 2024–25."""
    return {
        "season": "2024-25",
        "msp": [
            {"crop": k, "msp_per_quintal": v, "crop_pa": {"wheat": "ਕਣਕ", "rice": "ਚੌਲ",
             "maize": "ਮੱਕੀ", "cotton": "ਕਪਾਹ", "mustard": "ਸਰ੍ਹੋਂ",
             "sunflower": "ਸੂਰਜਮੁਖੀ", "moong": "ਮੂੰਗ", "groundnut": "ਮੂੰਗਫਲੀ"}.get(k, k)}
            for k, v in MSP_2024.items()
        ]
    }
