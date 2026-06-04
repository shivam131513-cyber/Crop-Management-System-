"""
Export Router
Provides CSV and JSON data exports for crop calendar, price history,
and farm analytics — useful for offline use on feature phones and
for integration with desktop spreadsheet tools.
"""

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional

from app.services.crop_knowledge import CROP_CALENDAR, DISTRICT_ZONE_MAP, CROP_PROFILES

router = APIRouter()


@router.get("/calendar.csv")
async def export_calendar_csv(
    district: Optional[str] = Query(None, description="Punjab district to resolve zone"),
    lang: str = Query("en", description="Language for tips: en | pa | hi"),
):
    """
    Export the 12-month Punjab crop calendar as a CSV file.
    Columns: Month, Season, Sow, Fertilize, Irrigate, Harvest, Pest Watch, Tip.
    Useful for printing and offline reference.
    """
    zone = "malwa"
    if district:
        zone = DISTRICT_ZONE_MAP.get(district.strip().lower(), "malwa")

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Month", "Month Name", "Season",
        "Sow", "Fertilize", "Irrigate", "Harvest", "Pest Watch",
        "General Tip", "Zone Note",
    ])

    for m in range(1, 13):
        data = CROP_CALENDAR.get(m)
        if not data:
            continue
        acts = data["activities"]
        tip = acts.get("general_tip_pa") if lang == "pa" else acts.get("general_tip", "")
        zone_note = data.get("zone_notes", {}).get(zone, "")
        writer.writerow([
            m,
            data.get("month_name", ""),
            data.get("season", ""),
            ", ".join(acts.get("sow", [])),
            ", ".join(acts.get("fertilize", [])),
            ", ".join(acts.get("irrigate", [])),
            ", ".join(acts.get("harvest", [])),
            ", ".join(acts.get("pest_watch", [])),
            tip,
            zone_note,
        ])

    output.seek(0)
    filename = f"kisaan_calendar_{zone}_{datetime.now().strftime('%Y%m')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/profits.csv")
async def export_profits_csv():
    """
    Export crop profit benchmarks (MSP, input cost, yield, net profit/acre)
    for all known crops as a CSV. Useful for farm planning spreadsheets.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Crop", "Crop (Punjabi)", "Season", "MSP (₹/qtl)",
        "Input Cost (₹/acre)", "Expected Yield (qtl/acre)",
        "Gross Revenue (₹/acre)", "Net Profit (₹/acre)",
        "Profit Margin (%)", "Stubble Friendly",
    ])

    for key, data in CROP_PROFILES.items():
        msp = data.get("msp_per_quintal") or 1000.0
        yield_q = data.get("expected_yield_qtl_per_acre", 0)
        cost = data.get("input_cost_per_acre", 0)
        revenue = round(msp * yield_q, 2)
        profit = round(revenue - cost, 2)
        margin = round((profit / revenue) * 100, 1) if revenue > 0 else 0.0
        writer.writerow([
            data.get("name", key),
            data.get("local_name_pa", ""),
            data.get("season", ""),
            msp,
            cost,
            yield_q,
            revenue,
            profit,
            margin,
            "Yes" if data.get("stubble_friendly") else "No",
        ])

    output.seek(0)
    filename = f"kisaan_profits_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/calendar.json")
async def export_calendar_json(
    district: Optional[str] = Query(None, description="Punjab district"),
):
    """
    Export full 12-month crop calendar as JSON (for offline mobile caching).
    Includes all languages and zone-specific notes.
    """
    zone = "malwa"
    if district:
        zone = DISTRICT_ZONE_MAP.get(district.strip().lower(), "malwa")

    result = []
    for m in range(1, 13):
        data = CROP_CALENDAR.get(m)
        if not data:
            continue
        result.append({
            "month": m,
            **data,
            "zone": zone,
            "zone_note": data.get("zone_notes", {}).get(zone, ""),
        })

    return JSONResponse(content={
        "zone": zone,
        "district": district,
        "exported_at": datetime.now().isoformat(),
        "calendar": result,
    })
