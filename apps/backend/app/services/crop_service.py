"""
Crop Advisory Service — Rule-based engine + ML model inference
"""
from typing import List, Optional
import json

from app.services.crop_knowledge import CROP_PROFILES, ELECTRICITY_SLOTS, DISTRICT_ZONE_MAP
from app.models.crop import CropProfile, CropRecommendRequest, CropRecommendResponse


def get_soil_zone(district: str) -> str:
    return DISTRICT_ZONE_MAP.get(district.lower(), "malwa")  # default to malwa


def score_crop(crop_data: dict, req: CropRecommendRequest, zone: str) -> float:
    """Rule-based scoring: 0–1 based on fit for conditions."""
    score = 0.0

    # Season match (hard filter)
    if req.season.value not in crop_data["season"]:
        return 0.0

    # Soil type match
    if req.soil_type.lower() in crop_data["soil_types"]:
        score += 0.3
    elif any(s in req.soil_type.lower() for s in crop_data["soil_types"]):
        score += 0.15

    # Zone match
    if zone in crop_data["soil_zones"]:
        score += 0.25

    # Water availability alignment
    water_map = {"high": 3, "medium": 2, "low": 1}
    crop_water = water_map.get(crop_data["water_req"], 2)
    avail_water = water_map.get(req.water_availability.value, 2)
    water_diff = abs(crop_water - avail_water)
    score += max(0, 0.3 - (water_diff * 0.15))

    # Stubble-friendly bonus (Punjab policy)
    if crop_data["stubble_friendly"]:
        score += 0.15

    return round(min(score, 1.0), 3)


def recommend_crops(req: CropRecommendRequest) -> CropRecommendResponse:
    zone = get_soil_zone(req.district)
    scored = []

    for crop_key, crop_data in CROP_PROFILES.items():
        s = score_crop(crop_data, req, zone)
        if s > 0:
            scored.append((s, crop_key, crop_data))

    # Sort by score descending, take top 3
    scored.sort(key=lambda x: x[0], reverse=True)
    top3 = scored[:3]

    crops_out: List[CropProfile] = []
    has_rice = False

    for score, key, data in top3:
        if key == "rice":
            has_rice = True
        crops_out.append(CropProfile(
            name=data["name"],
            local_name_hi=data["local_name_hi"],
            local_name_pa=data["local_name_pa"],
            expected_yield_qtl_per_acre=data["expected_yield_qtl_per_acre"],
            water_req=data["water_req"],
            duration_days=data["duration_days"],
            msp_per_quintal=data.get("msp_per_quintal"),
            input_cost_per_acre=data["input_cost_per_acre"],
            suitability_score=score,
            stubble_friendly=data["stubble_friendly"],
            advice=data["advice"],
        ))

    # Build irrigation slots from Punjab electricity windows
    slots = [
        f"{v['label']}: {v['start']} – {v['end']}"
        for v in ELECTRICITY_SLOTS.values()
    ]

    stubble_warning = None
    if has_rice:
        stubble_warning = (
            "⚠️ Rice cultivation leads to stubble burning. Punjab government offers "
            "₹2500/acre incentive for in-situ straw management. Consider Happy Seeder "
            "or bio-decomposer. Maize and vegetables are eco-friendly alternatives."
        )

    return CropRecommendResponse(
        recommended_crops=crops_out,
        irrigation_slots=slots,
        stubble_warning=stubble_warning,
        season_tip=f"Current zone: {zone.capitalize()}. Optimal sowing window based on district data.",
    )
