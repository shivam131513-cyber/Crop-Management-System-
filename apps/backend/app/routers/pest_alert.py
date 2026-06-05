from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

router = APIRouter()

# Seasonal pest calendar for Punjab (month → active pests per crop)
PEST_CALENDAR = {
    "wheat": {
        (11, 12, 1): ["yellow_rust", "aphids"],
        (2, 3):      ["brown_rust", "aphids", "powdery_mildew"],
        (4,):        ["karnal_bunt"],
    },
    "rice": {
        (6, 7):      ["stem_borer", "leaf_folder"],
        (8, 9):      ["brown_plant_hopper", "blast"],
        (10,):       ["sheath_blight"],
    },
    "cotton": {
        (5, 6):      ["jassid", "thrips"],
        (7, 8):      ["whitefly", "pink_bollworm"],
        (9, 10):     ["pink_bollworm", "mealy_bug"],
    },
    "maize": {
        (6, 7, 8):   ["fall_armyworm", "stem_borer"],
        (9,):        ["cob_borer"],
    },
    "mustard": {
        (10, 11):    ["aphids", "sawfly"],
        (12, 1):     ["aphids"],
    },
    "potato": {
        (10, 11):    ["late_blight", "aphids"],
        (12, 1, 2):  ["early_blight", "cutworm"],
    },
}

PEST_DETAILS = {
    "yellow_rust": {
        "name": "Yellow Rust (Stripe Rust)",
        "name_pa": "ਪੀਲਾ ਰਤੂਆ",
        "name_hi": "पीला रतुआ",
        "severity": "high",
        "threshold": "1 infected plant per sq meter",
        "action": "Spray Propiconazole 25 EC @ 0.1% or Triadimefon 25 WP @ 0.1% immediately.",
        "action_pa": "ਪ੍ਰੋਪੀਕੋਨਾਜ਼ੋਲ 25 EC @ 0.1% ਤੁਰੰਤ ਸਪਰੇਅ ਕਰੋ।",
    },
    "aphids": {
        "name": "Aphids",
        "name_pa": "ਮਾਹੂ",
        "name_hi": "माहू (चेपा)",
        "severity": "medium",
        "threshold": "10+ aphids per leaf",
        "action": "Spray Imidacloprid 17.8 SL @ 0.5 mL/L or Dimethoate 30 EC @ 1 mL/L.",
        "action_pa": "ਇਮੀਡਾਕਲੋਪ੍ਰਿਡ @ 0.5 mL/L ਸਪਰੇਅ ਕਰੋ।",
    },
    "brown_rust": {
        "name": "Brown Rust (Leaf Rust)",
        "name_pa": "ਭੂਰਾ ਰਤੂਆ",
        "name_hi": "भूरा रतुआ",
        "severity": "high",
        "threshold": "Pustules on lower leaves",
        "action": "Spray Propiconazole 25% EC @ 0.1%. Repeat after 15 days.",
        "action_pa": "ਪ੍ਰੋਪੀਕੋਨਾਜ਼ੋਲ 25% EC @ 0.1% ਸਪਰੇਅ ਕਰੋ। 15 ਦਿਨ ਬਾਅਦ ਦੁਬਾਰਾ।",
    },
    "brown_plant_hopper": {
        "name": "Brown Plant Hopper (BPH)",
        "name_pa": "ਭੂਰਾ ਕੀੜਾ",
        "name_hi": "भूरा फुदका",
        "severity": "high",
        "threshold": "5+ hoppers per hill",
        "action": "Drain field for 3-4 days. Spray Buprofezin 25 SC @ 1 mL/L at base of plants.",
        "action_pa": "ਖੇਤ 3-4 ਦਿਨ ਖਾਲੀ ਕਰੋ। ਬਿਊਪ੍ਰੋਫੈਜ਼ਿਨ @ 1 mL/L ਛਿੜਕੋ।",
    },
    "stem_borer": {
        "name": "Yellow Stem Borer",
        "name_pa": "ਤਣੇ ਦਾ ਕੀੜਾ",
        "name_hi": "तना छेदक",
        "severity": "medium",
        "threshold": "10% dead hearts at vegetative stage",
        "action": "Apply Cartap Hydrochloride 4G @ 8 kg/acre or Chlorpyriphos 20 EC @ 2 mL/L.",
        "action_pa": "ਕਾਰਟੈਪ 4G @ 8 ਕਿਲੋ/ਏਕੜ ਪਾਓ।",
    },
    "fall_armyworm": {
        "name": "Fall Armyworm (FAW)",
        "name_pa": "ਫੌਜੀ ਸੁੰਡੀ",
        "name_hi": "फाल आर्मी वर्म",
        "severity": "high",
        "threshold": "1 egg mass or 1 larva per 2 plants",
        "action": "Spray Emamectin benzoate 5 SG @ 0.4 g/L or Spinetoram 11.7 SC @ 0.5 mL/L.",
        "action_pa": "ਇਮਾਮੈਕਟਿਨ ਬੈਂਜ਼ੋਏਟ 5 SG @ 0.4 g/L ਸਪਰੇਅ ਕਰੋ।",
    },
    "pink_bollworm": {
        "name": "Pink Bollworm",
        "name_pa": "ਗੁਲਾਬੀ ਸੁੰਡੀ",
        "name_hi": "गुलाबी सुंडी",
        "severity": "high",
        "threshold": "5+ moths/pheromone trap/week",
        "action": "Install pheromone traps @ 5/acre. Spray Chlorpyriphos 20 EC @ 2 mL/L.",
        "action_pa": "ਫੇਰੋਮੋਨ ਟਰੈਪ 5/ਏਕੜ ਲਗਾਓ। ਕਲੋਰਪਾਈਰੀਫੋਸ @ 2 mL/L ਛਿੜਕੋ।",
    },
    "late_blight": {
        "name": "Late Blight (Phytophthora)",
        "name_pa": "ਝੁਲਸ ਰੋਗ",
        "name_hi": "अगेती झुलसा",
        "severity": "high",
        "threshold": "First spotted lesion",
        "action": "Spray Mancozeb 75 WP @ 2.5 g/L + Metalaxyl 8 WP @ 2 g/L immediately.",
        "action_pa": "ਮੈਨਕੋਜ਼ੇਬ + ਮੈਟਾਲੈਕਸਿਲ ਤੁਰੰਤ ਸਪਰੇਅ ਕਰੋ।",
    },
    "blast": {
        "name": "Rice Blast",
        "name_pa": "ਬਲਾਸਟ ਰੋਗ",
        "name_hi": "चावल का ब्लास्ट",
        "severity": "high",
        "threshold": "First diamond-shaped lesions on leaves",
        "action": "Spray Tricyclazole 75 WP @ 0.6 g/L at first sign. Repeat after 10 days.",
        "action_pa": "ਟ੍ਰਾਈਸਾਈਕਲਾਜ਼ੋਲ 75 WP @ 0.6 g/L ਸਪਰੇਅ ਕਰੋ।",
    },
    "whitefly": {
        "name": "Whitefly",
        "name_pa": "ਚਿੱਟੀ ਮੱਖੀ",
        "name_hi": "सफेद मक्खी",
        "severity": "high",
        "threshold": "6+ adults per leaf",
        "action": "Spray Spiromesifen 22.9 SC @ 0.75 mL/L or Pyriproxyfen 10 EC @ 0.5 mL/L.",
        "action_pa": "ਸਪਾਇਰੋਮੇਸੀਫੈਨ @ 0.75 mL/L ਸਪਰੇਅ ਕਰੋ।",
    },
    "powdery_mildew": {
        "name": "Powdery Mildew",
        "name_pa": "ਸਫੇਦ ਕੁੱਕੜ",
        "name_hi": "चूर्णिल आसिता",
        "severity": "medium",
        "threshold": "White powdery patches on leaves",
        "action": "Spray Sulfur 80 WP @ 3 g/L or Hexaconazole 5 EC @ 1 mL/L.",
        "action_pa": "ਸਲਫਰ 80 WP @ 3 g/L ਸਪਰੇਅ ਕਰੋ।",
    },
    "karnal_bunt": {
        "name": "Karnal Bunt",
        "name_pa": "ਕਰਨਾਲ ਬੰਟ",
        "name_hi": "करनाल बंट",
        "severity": "medium",
        "threshold": "Presence of black powder in grains",
        "action": "Use certified seed treated with Carboxin 37.5% + Thiram 37.5% @ 2.5 g/kg seed.",
        "action_pa": "ਪ੍ਰਮਾਣਿਤ ਬੀਜ ਵਰਤੋ। ਕਾਰਬੌਕਸਿਨ + ਥਾਈਰਮ @ 2.5 g/kg ਬੀਜ ਉਪਚਾਰ।",
    },
    "sheath_blight": {
        "name": "Sheath Blight",
        "name_pa": "ਥੈਲੀ ਝੁਲਸ",
        "name_hi": "शीथ ब्लाइट",
        "severity": "medium",
        "threshold": "Lesions on 10% of tillers",
        "action": "Spray Hexaconazole 5 EC @ 1 mL/L or Propiconazole 25 EC @ 1 mL/L.",
        "action_pa": "ਹੈਕਸਾਕੋਨਾਜ਼ੋਲ 5 EC @ 1 mL/L ਛਿੜਕੋ।",
    },
    "leaf_folder": {
        "name": "Rice Leaf Folder",
        "name_pa": "ਪੱਤਾ ਮੋੜੂ ਕੀੜਾ",
        "name_hi": "पत्ती मोड़क",
        "severity": "low",
        "threshold": "5% leaf damage",
        "action": "Spray Chlorpyriphos 20 EC @ 2 mL/L or Quinalphos 25 EC @ 2 mL/L.",
        "action_pa": "ਕਲੋਰਪਾਈਰੀਫੋਸ 20 EC @ 2 mL/L ਸਪਰੇਅ ਕਰੋ।",
    },
    "jassid": {
        "name": "Cotton Jassid",
        "name_pa": "ਜੈਸਿਡ",
        "name_hi": "जैसिड",
        "severity": "medium",
        "threshold": "3+ nymphs per leaf",
        "action": "Spray Imidacloprid 17.8 SL @ 0.3 mL/L.",
        "action_pa": "ਇਮੀਡਾਕਲੋਪ੍ਰਿਡ 17.8 SL @ 0.3 mL/L ਸਪਰੇਅ ਕਰੋ।",
    },
    "thrips": {
        "name": "Thrips",
        "name_pa": "ਥ੍ਰਿਪਸ",
        "name_hi": "थ्रिप्स",
        "severity": "low",
        "threshold": "20+ thrips per leaf",
        "action": "Spray Spinosad 45 SC @ 0.3 mL/L or Fipronil 5 SC @ 1.5 mL/L.",
        "action_pa": "ਸਪਾਈਨੋਸੈਡ 45 SC @ 0.3 mL/L ਸਪਰੇਅ ਕਰੋ।",
    },
    "mealy_bug": {
        "name": "Cotton Mealy Bug",
        "name_pa": "ਮੀਲੀਬੱਗ",
        "name_hi": "मीली बग",
        "severity": "medium",
        "threshold": "Visible waxy coating on stems",
        "action": "Release Cryptolaemus montrouzieri biocontrol beetles. Spray Buprofezin 25 SC.",
        "action_pa": "ਕ੍ਰਿਪਟੋਲੇਮਸ ਜੀਵਾਣੂ ਛੱਡੋ। ਬਿਊਪ੍ਰੋਫੈਜ਼ਿਨ ਸਪਰੇਅ ਕਰੋ।",
    },
    "cob_borer": {
        "name": "Maize Cob Borer",
        "name_pa": "ਭੁੱਟੇ ਦਾ ਕੀੜਾ",
        "name_hi": "मक्का भुट्टा कीड़ा",
        "severity": "medium",
        "threshold": "Frass on cobs",
        "action": "Apply Carbaryl 10 G into silk channel at milk stage.",
        "action_pa": "ਕਾਰਬੇਰਿਲ 10G ਮੱਕੀ ਦੇ ਰੇਸ਼ੇ ਵਿੱਚ ਦੁੱਧ ਅਵਸਥਾ 'ਤੇ ਪਾਓ।",
    },
    "sawfly": {
        "name": "Mustard Sawfly",
        "name_pa": "ਆਰਾ ਮੱਖੀ",
        "name_hi": "आरा मक्खी",
        "severity": "medium",
        "threshold": "4+ larvae per plant",
        "action": "Spray Malathion 50 EC @ 1.5 mL/L or Quinalphos 25 EC @ 2 mL/L.",
        "action_pa": "ਮੈਲਾਥੀਆਨ 50 EC @ 1.5 mL/L ਸਪਰੇਅ ਕਰੋ।",
    },
    "early_blight": {
        "name": "Early Blight (Potato)",
        "name_pa": "ਅਗੇਤਾ ਝੁਲਸ",
        "name_hi": "अगेती झुलसा",
        "severity": "medium",
        "threshold": "Dark concentric spots on lower leaves",
        "action": "Spray Mancozeb 75 WP @ 2.0 g/L every 7-10 days.",
        "action_pa": "ਮੈਨਕੋਜ਼ੇਬ 75 WP @ 2.0 g/L ਹਰ 7-10 ਦਿਨ ਸਪਰੇਅ ਕਰੋ।",
    },
    "cutworm": {
        "name": "Cutworm",
        "name_pa": "ਕੁੱਟ ਕੀੜਾ",
        "name_hi": "कट वर्म",
        "severity": "low",
        "threshold": "Wilted seedlings with cut stems",
        "action": "Apply Chlorpyriphos 20 EC mixed in sand @ 15 kg/acre in evening.",
        "action_pa": "ਕਲੋਰਪਾਈਰੀਫੋਸ 20 EC ਰੇਤ ਵਿੱਚ ਮਿਲਾ ਕੇ ਸ਼ਾਮ ਨੂੰ ਪਾਓ।",
    },
}


class PestAlert(BaseModel):
    pest_key: str
    pest_name: str
    pest_name_pa: str
    pest_name_hi: str
    severity: str           # high | medium | low
    economic_threshold: str
    recommended_action: str
    recommended_action_pa: str


class DistrictAlertResponse(BaseModel):
    district: str
    month: int
    year: int
    crops_monitored: List[str]
    total_alerts: int
    alerts: List[PestAlert]
    advisory: str
    advisory_pa: str


@router.get("/alert", response_model=DistrictAlertResponse)
async def get_district_pest_alerts(
    district: str = Query(..., description="Punjab district name, e.g. ludhiana"),
    crops: Optional[str] = Query(
        None,
        description="Comma-separated crop list, e.g. wheat,rice. Defaults to seasonal crops.",
    ),
    month: Optional[int] = Query(None, description="Month (1-12). Defaults to current month."),
):
    """
    Return active pest alerts for a district based on the current season.
    Covers all major Punjab crops: wheat, rice, cotton, maize, mustard, potato.
    Alerts are derived from PAU (Punjab Agricultural University) seasonal pest calendars.
    """
    today = date.today()
    target_month = month or today.month
    target_year = today.year

    # Determine which crops to check
    if crops:
        crop_list = [c.strip().lower() for c in crops.split(",")]
    else:
        # Default to all crops in the calendar
        crop_list = list(PEST_CALENDAR.keys())

    active_alerts: List[PestAlert] = []
    monitored_crops: List[str] = []

    for crop in crop_list:
        calendar = PEST_CALENDAR.get(crop)
        if not calendar:
            continue
        monitored_crops.append(crop)

        for month_tuple, pest_keys in calendar.items():
            if target_month in month_tuple:
                for pest_key in pest_keys:
                    details = PEST_DETAILS.get(pest_key)
                    if details:
                        active_alerts.append(PestAlert(
                            pest_key=pest_key,
                            pest_name=details["name"],
                            pest_name_pa=details["name_pa"],
                            pest_name_hi=details["name_hi"],
                            severity=details["severity"],
                            economic_threshold=details["threshold"],
                            recommended_action=details["action"],
                            recommended_action_pa=details["action_pa"],
                        ))

    # Sort: high severity first
    severity_order = {"high": 0, "medium": 1, "low": 2}
    active_alerts.sort(key=lambda a: severity_order.get(a.severity, 3))

    advisory_en = (
        f"Scout fields weekly in {district.title()} this month. "
        "Apply sprays only at or above economic threshold to reduce resistance and costs."
    )
    advisory_pa = (
        f"{district.title()} ਵਿੱਚ ਇਸ ਮਹੀਨੇ ਹਫ਼ਤੇਵਾਰ ਖੇਤ ਦੇਖੋ। "
        "ਕੀਟਨਾਸ਼ਕ ਸਿਰਫ਼ ਆਰਥਿਕ ਸੀਮਾ ਤੋਂ ਉੱਪਰ ਵਰਤੋ।"
    )

    return DistrictAlertResponse(
        district=district,
        month=target_month,
        year=target_year,
        crops_monitored=monitored_crops,
        total_alerts=len(active_alerts),
        alerts=active_alerts,
        advisory=advisory_en,
        advisory_pa=advisory_pa,
    )
