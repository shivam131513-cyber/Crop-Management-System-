from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(15), unique=True, nullable=True)
    name = Column(String(100), nullable=True)
    district = Column(String(50), nullable=True)  # Punjab district
    village = Column(String(100), nullable=True)
    land_size_acres = Column(Float, nullable=True)
    soil_zone = Column(String(20), nullable=True)  # majha | malwa | doaba
    preferred_language = Column(String(5), default="pa")  # pa | hi | en
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CropRecommendation(Base):
    __tablename__ = "crop_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, nullable=True)
    district = Column(String(50))
    soil_type = Column(String(50))
    season = Column(String(20))  # kharif | rabi | zaid
    water_availability = Column(String(20))  # high | medium | low
    recommended_crops = Column(JSON)  # list of crop objects
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DiseaseDetection(Base):
    __tablename__ = "disease_detections"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, nullable=True)
    crop_name = Column(String(100))
    disease_name = Column(String(200))
    confidence = Column(Float)
    treatment = Column(Text)
    image_path = Column(String(500), nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String(100))
    mandi = Column(String(100))
    district = Column(String(50))
    price_per_quintal = Column(Float)
    msp_per_quintal = Column(Float, nullable=True)
    recorded_date = Column(DateTime(timezone=True), server_default=func.now())


class SyncQueue(Base):
    __tablename__ = "sync_queue"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(200))
    payload = Column(JSON)
    retries = Column(Integer, default=0)
    synced = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
