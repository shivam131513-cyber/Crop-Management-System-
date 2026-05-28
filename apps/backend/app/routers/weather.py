import os
import httpx
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()

OWM_KEY = os.getenv("OPENWEATHERMAP_KEY", "")
OWM_BASE = "https://api.openweathermap.org/data/2.5"

# Punjab district → lat/lon centroids
DISTRICT_COORDS = {
    "ludhiana":     (30.9010, 75.8573),
    "amritsar":     (31.6340, 74.8723),
    "jalandhar":    (31.3260, 75.5762),
    "patiala":      (30.3398, 76.3869),
    "bathinda":     (30.2110, 74.9455),
    "mohali":       (30.7046, 76.7179),
    "gurdaspur":    (32.0384, 75.4063),
    "pathankot":    (32.2643, 75.6527),
    "hoshiarpur":   (31.5143, 75.9113),
    "mansa":        (29.9989, 75.3948),
    "muktsar":      (30.4741, 74.5171),
    "ferozepur":    (30.9254, 74.6201),
    "moga":         (30.8163, 75.1697),
    "faridkot":     (30.6718, 74.7569),
    "barnala":      (30.3784, 75.5482),
    "sangrur":      (30.2447, 75.8440),
    "kapurthala":   (31.3800, 75.3800),
    "nawanshahr":   (31.1252, 76.1155),
    "fatehgarh sahib": (30.6491, 76.3902),
    "tarn taran":   (31.4510, 74.9275),
}


def get_coords(district: str):
    return DISTRICT_COORDS.get(district.lower(), (30.9010, 75.8573))  # default: Ludhiana


def build_alerts(forecast: dict) -> list:
    """Generate farm-relevant alerts from OWM forecast data."""
    alerts = []
    rain_hours = 0

    for item in forecast.get("list", [])[:16]:  # next 48h (3h intervals)
        temp_max = item["main"]["temp_max"]
        temp_min = item["main"]["temp_min"]
        humidity = item["main"]["humidity"]
        rain_3h = item.get("rain", {}).get("3h", 0)
        rain_hours += rain_3h

        if temp_min < 4:
            alerts.append({
                "type": "frost",
                "severity": "high",
                "message": f"Frost risk: {temp_min:.1f}°C expected. Cover sensitive crops.",
                "message_pa": "ਠੰਡ ਦਾ ਖ਼ਤਰਾ। ਫ਼ਸਲਾਂ ਨੂੰ ਢੱਕੋ।",
            })
        if temp_max > 42:
            alerts.append({
                "type": "heatwave",
                "severity": "high",
                "message": f"Heatwave: {temp_max:.1f}°C. Irrigate early morning.",
                "message_pa": "ਲੂ ਦਾ ਖ਼ਤਰਾ। ਸਵੇਰੇ ਸਿੰਚਾਈ ਕਰੋ।",
            })
        if humidity > 80:
            alerts.append({
                "type": "pest_risk",
                "severity": "medium",
                "message": "High humidity — risk of fungal disease and brown planthopper.",
                "message_pa": "ਨਮੀ ਵੱਧ ਹੈ — ਕੀੜਿਆਂ ਦਾ ਖ਼ਤਰਾ।",
            })

    if rain_hours < 2:
        alerts.append({
            "type": "irrigation",
            "severity": "info",
            "message": "No rain expected (48h). Use electricity slot: 05:00–08:00 or 22:00–01:00.",
            "message_pa": "ਬਾਰਸ਼ ਨਹੀਂ। ਬਿਜਲੀ ਸਲਾਟ ਵਰਤੋ: ਸਵੇਰੇ 5–8 ਜਾਂ ਰਾਤ 10–1।",
        })

    return alerts


@router.get("/forecast")
async def get_forecast(
    district: str = Query("ludhiana", description="Punjab district name"),
):
    """
    7-day weather forecast with farm-specific alerts.
    Uses Punjab district centroids; falls back to mock data if no API key.
    """
    if not OWM_KEY:
        return _mock_forecast(district)

    lat, lon = get_coords(district)
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                f"{OWM_BASE}/forecast",
                params={"lat": lat, "lon": lon, "appid": OWM_KEY, "units": "metric", "cnt": 40},
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError:
            return _mock_forecast(district)

    alerts = build_alerts(data)
    return {
        "district": district,
        "coordinates": {"lat": lat, "lon": lon},
        "forecast": data.get("list", [])[:16],
        "alerts": alerts,
        "irrigation_slots": [
            {"label": "Morning", "start": "05:00", "end": "08:00"},
            {"label": "Night",   "start": "22:00", "end": "01:00"},
        ],
    }


def _mock_forecast(district: str) -> dict:
    """Offline/demo mock weather for Ludhiana region."""
    return {
        "district": district,
        "coordinates": {"lat": 30.90, "lon": 75.85},
        "mock": True,
        "forecast": [
            {
                "dt_txt": "2025-06-01 06:00:00",
                "main": {"temp": 32.1, "temp_max": 38.0, "temp_min": 26.0, "humidity": 55},
                "weather": [{"description": "partly cloudy", "icon": "02d"}],
                "rain": {},
            },
            {
                "dt_txt": "2025-06-01 09:00:00",
                "main": {"temp": 36.5, "temp_max": 40.0, "temp_min": 29.0, "humidity": 48},
                "weather": [{"description": "clear sky", "icon": "01d"}],
                "rain": {},
            },
        ],
        "alerts": [
            {
                "type": "irrigation",
                "severity": "info",
                "message": "No rain expected. Use electricity slot: 05:00–08:00.",
                "message_pa": "ਬਾਰਸ਼ ਨਹੀਂ। ਬਿਜਲੀ ਸਲਾਟ: ਸਵੇਰੇ 5–8।",
            }
        ],
        "irrigation_slots": [
            {"label": "Morning", "start": "05:00", "end": "08:00"},
            {"label": "Night",   "start": "22:00", "end": "01:00"},
        ],
    }
