from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.routers import crop, weather, pest, soil, market, auth
from app.db.database import engine
from app.db import models

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kisaan Saathi API",
    description="AI-powered crop advisory backend for Punjab farmers (SIH25010)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,    prefix="/auth",    tags=["Auth"])
app.include_router(crop.router,    prefix="/crop",    tags=["Crop Advisory"])
app.include_router(weather.router, prefix="/weather", tags=["Weather"])
app.include_router(pest.router,    prefix="/pest",    tags=["Pest Detection"])
app.include_router(soil.router,    prefix="/soil",    tags=["Soil & Fertilizer"])
app.include_router(market.router,  prefix="/market",  tags=["Market Prices"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "app": "Kisaan Saathi",
        "version": "1.0.0",
        "modules": ["crop", "weather", "pest", "soil", "market", "auth"],
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
