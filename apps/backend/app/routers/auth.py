import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer(auto_error=False)

# Secret key — override via JWT_SECRET env var in production
SECRET_KEY = os.getenv("JWT_SECRET", "kisaan-saathi-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24       # 1 day
REFRESH_TOKEN_EXPIRE_DAYS = 30


# ── Schemas ──────────────────────────────────────────────────────────────────

class FarmerCreate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    district: str = "ludhiana"
    village: Optional[str] = None
    land_size_acres: Optional[float] = 2.0
    soil_zone: Optional[str] = None
    preferred_language: str = "pa"  # pa | hi | en


class LoginRequest(BaseModel):
    phone: str
    district: str = "ludhiana"
    preferred_language: str = "pa"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    farmer_id: int


class RefreshRequest(BaseModel):
    refresh_token: str


class FarmerResponse(BaseModel):
    id: int
    name: Optional[str]
    district: str
    preferred_language: str
    message: str


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires_delta
    payload["iat"] = datetime.utcnow()
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises HTTPException on failure."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_farmer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI dependency — validates Bearer token and returns payload."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_token(credentials.credentials)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def farmer_login(req: LoginRequest):
    """
    Phone-based login (OTP-less for MVP / rural low-connectivity use-case).
    Issues JWT access + refresh tokens scoped to the farmer's phone number.
    In production: verify OTP before issuing tokens.
    """
    # TODO: verify OTP in production; skip for MVP demo
    farmer_id = abs(hash(req.phone)) % 100_000  # deterministic demo ID

    access_token = create_token(
        {"sub": req.phone, "farmer_id": farmer_id, "district": req.district, "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_token(
        {"sub": req.phone, "farmer_id": farmer_id, "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        farmer_id=farmer_id,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(req: RefreshRequest):
    """Exchange a valid refresh token for a new access token."""
    payload = decode_token(req.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Not a refresh token.")

    new_access = create_token(
        {"sub": payload["sub"], "farmer_id": payload["farmer_id"],
         "district": payload.get("district", "ludhiana"), "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh = create_token(
        {"sub": payload["sub"], "farmer_id": payload["farmer_id"], "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        farmer_id=payload["farmer_id"],
    )


@router.post("/profile", response_model=FarmerResponse)
async def create_or_update_profile(farmer: FarmerCreate):
    """
    Create or update farmer profile (no strict auth required for MVP).
    Profile stored locally on device + synced to server when online.
    """
    return FarmerResponse(
        id=1,
        name=farmer.name or "Kisaan",
        district=farmer.district,
        preferred_language=farmer.preferred_language,
        message="Profile saved successfully. ਪ੍ਰੋਫਾਈਲ ਸੇਵ ਕੀਤੀ ਗਈ।",
    )


@router.get("/profile/{farmer_id}")
async def get_profile(
    farmer_id: int,
    current: dict = Depends(get_current_farmer),
):
    """Fetch farmer profile (requires valid JWT)."""
    return {
        "id": farmer_id,
        "name": "Demo Farmer",
        "district": current.get("district", "ludhiana"),
        "village": "Demo Village",
        "land_size_acres": 3.5,
        "soil_zone": "malwa",
        "preferred_language": "pa",
    }

