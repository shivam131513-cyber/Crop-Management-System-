"""
Notifications Router
In-memory notification subscription and listing system for Kisaan Saathi.
Farmers can subscribe to price alerts, weather warnings, and pest advisories.
In production, swap the in-memory store for Redis or a DB-backed queue.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter()

# ── In-memory store (replace with DB in production) ───────────────────────────
_subscriptions: dict[str, dict] = {}  # key: subscription_id
_notifications: list[dict] = []       # global notification feed

NOTIFICATION_TYPES = ["price_alert", "weather_warning", "pest_advisory", "market_update", "general"]
VALID_CROPS = ["wheat", "rice", "maize", "cotton", "mustard", "potato", "moong", "sunflower"]
VALID_DISTRICTS = [
    "ludhiana", "amritsar", "jalandhar", "patiala", "bathinda", "mohali",
    "gurdaspur", "pathankot", "hoshiarpur", "mansa", "muktsar", "ferozepur",
    "moga", "faridkot", "barnala", "sangrur", "kapurthala",
]


# ── Seed a few demo notifications ────────────────────────────────────────────
def _seed_demo():
    demos = [
        {
            "id": str(uuid.uuid4()),
            "type": "price_alert",
            "crop": "wheat",
            "district": "ludhiana",
            "title": "Wheat Price Alert",
            "title_pa": "ਕਣਕ ਭਾਅ ਸੂਚਨਾ",
            "message": "Wheat price in Ludhiana rose to ₹2310/qtl (+2.5%). Good time to sell.",
            "message_pa": "ਲੁਧਿਆਣਾ ਵਿੱਚ ਕਣਕ ₹2310/ਕੁਇੰਟਲ। ਵੇਚਣ ਦਾ ਵਧੀਆ ਮੌਕਾ।",
            "severity": "info",
            "created_at": datetime.now().isoformat(),
            "read": False,
        },
        {
            "id": str(uuid.uuid4()),
            "type": "weather_warning",
            "crop": None,
            "district": "bathinda",
            "title": "Heatwave Warning",
            "title_pa": "ਲੂ ਦੀ ਚੇਤਾਵਨੀ",
            "message": "Temperatures expected to reach 43°C in Bathinda. Irrigate crops early morning.",
            "message_pa": "ਬਠਿੰਡਾ ਵਿੱਚ 43°C ਦੀ ਸੰਭਾਵਨਾ। ਸਵੇਰੇ ਸਿੰਚਾਈ ਕਰੋ।",
            "severity": "high",
            "created_at": datetime.now().isoformat(),
            "read": False,
        },
        {
            "id": str(uuid.uuid4()),
            "type": "pest_advisory",
            "crop": "cotton",
            "district": "bathinda",
            "title": "Whitefly Risk: Cotton",
            "title_pa": "ਕਪਾਹ ਵਿੱਚ ਸਫੈਦ ਮੱਖੀ ਦਾ ਖ਼ਤਰਾ",
            "message": "High humidity in Bathinda. Spray imidacloprid 17.8% SL if whitefly count >6/leaf.",
            "message_pa": "ਨਮੀ ਵੱਧ — ਜੇ >6 ਮੱਖੀਆਂ/ਪੱਤਾ ਤਾਂ ਇਮੀਡਾਕਲੋਪ੍ਰਿਡ ਛਿੜਕੋ।",
            "severity": "medium",
            "created_at": datetime.now().isoformat(),
            "read": False,
        },
    ]
    _notifications.extend(demos)


_seed_demo()


# ── Pydantic models ───────────────────────────────────────────────────────────
class SubscribeRequest(BaseModel):
    farmer_id: str
    district: str
    crops: List[str]
    notification_types: List[str]
    phone: Optional[str] = None


class SubscriptionResponse(BaseModel):
    subscription_id: str
    farmer_id: str
    district: str
    crops: List[str]
    notification_types: List[str]
    created_at: str
    active: bool


class NotificationItem(BaseModel):
    id: str
    type: str
    crop: Optional[str]
    district: str
    title: str
    title_pa: str
    message: str
    message_pa: str
    severity: str
    created_at: str
    read: bool


class MarkReadRequest(BaseModel):
    notification_ids: List[str]


# ── Routes ────────────────────────────────────────────────────────────────────
@router.post("/subscribe", response_model=SubscriptionResponse, status_code=201)
async def subscribe(req: SubscribeRequest):
    """
    Subscribe a farmer to push notifications for selected crops, district,
    and notification types (price_alert, weather_warning, pest_advisory, etc.).
    Returns a subscription ID to use for listing personalised notifications.
    """
    # Validate
    invalid_crops = [c for c in req.crops if c.lower() not in VALID_CROPS]
    if invalid_crops:
        raise HTTPException(status_code=422, detail=f"Unknown crops: {invalid_crops}. Valid: {VALID_CROPS}")

    invalid_types = [t for t in req.notification_types if t not in NOTIFICATION_TYPES]
    if invalid_types:
        raise HTTPException(status_code=422, detail=f"Unknown types: {invalid_types}. Valid: {NOTIFICATION_TYPES}")

    sub_id = str(uuid.uuid4())
    sub = {
        "subscription_id": sub_id,
        "farmer_id": req.farmer_id,
        "district": req.district.lower(),
        "crops": [c.lower() for c in req.crops],
        "notification_types": req.notification_types,
        "phone": req.phone,
        "created_at": datetime.now().isoformat(),
        "active": True,
    }
    _subscriptions[sub_id] = sub

    return SubscriptionResponse(**sub)


@router.get("/list", response_model=List[NotificationItem])
async def list_notifications(
    district: Optional[str] = Query(None, description="Filter by district"),
    crop: Optional[str] = Query(None, description="Filter by crop"),
    notification_type: Optional[str] = Query(None, description="Filter by type"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    limit: int = Query(20, ge=1, le=100),
):
    """
    List all farm notifications, with optional filters.
    Notifications include price alerts, weather warnings, and pest advisories.
    """
    results = list(_notifications)

    if district:
        results = [n for n in results if n["district"] == district.lower()]
    if crop:
        results = [n for n in results if n.get("crop") == crop.lower() or n["crop"] is None]
    if notification_type:
        results = [n for n in results if n["type"] == notification_type]
    if unread_only:
        results = [n for n in results if not n["read"]]

    # Latest first
    results.sort(key=lambda x: x["created_at"], reverse=True)
    return [NotificationItem(**n) for n in results[:limit]]


@router.post("/mark-read")
async def mark_read(req: MarkReadRequest):
    """Mark one or more notifications as read by their IDs."""
    updated = 0
    for notif in _notifications:
        if notif["id"] in req.notification_ids:
            notif["read"] = True
            updated += 1

    return {"marked_read": updated, "requested": len(req.notification_ids)}


@router.get("/subscriptions/{farmer_id}", response_model=List[SubscriptionResponse])
async def get_subscriptions(farmer_id: str):
    """Retrieve all active subscriptions for a farmer."""
    subs = [
        SubscriptionResponse(**v)
        for v in _subscriptions.values()
        if v["farmer_id"] == farmer_id and v["active"]
    ]
    return subs
