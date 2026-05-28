# ਕਿਸਾਨ ਸਾਥੀ — Kisaan Saathi

**AI-Powered Crop Advisory App for Punjab Farmers**

> SIH 2025 Problem Statement: **PS1 (SIH25010)** — Punjab

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Expo](https://img.shields.io/badge/Mobile-Expo%20React%20Native-000020)](https://expo.dev/)
[![Offline](https://img.shields.io/badge/Works-Offline%20%E2%9C%93-4CAF50)]()
[![Languages](https://img.shields.io/badge/Languages-ਪੰਜਾਬੀ%20%7C%20हिंदी%20%7C%20English-orange)]()

---

## 🎯 Problem It Solves

86% of Indian farmers are small or marginal. They lack access to:
- Expert crop selection guidance
- Real-time soil and weather data  
- Pest/disease identification
- Market price information
- All in their local language (Punjabi)

**Kisaan Saathi** solves this with an offline-first, multilingual, AI-powered mobile app.

---

## 🏆 Punjab-Specific Differentiators

| Feature | Description |
|---------|-------------|
| ⚡ **Electricity-Aware Irrigation** | Punjab tube-well free electricity slots (5 AM–8 AM, 10 PM–1 AM) integrated into weather alerts |
| ♻️ **Stubble Burning Alternatives** | Flags rice cultivation → suggests Happy Seeder, Bio-decomposer with govt incentives |
| 📱 **Offline-First** | SQLite cache, on-device TFLite disease detection, 2G-optimized API (GZip) |
| 🌾 **3 Soil Zones** | Majha / Malwa / Doaba with zone-specific NPK defaults |

---

## 🚀 Quick Start

### Backend

```bash
cd apps/backend
cp .env.example .env
# Edit .env: add your OPENWEATHERMAP_KEY

# Docker (recommended)
docker-compose up -d

# Local Python 3.11
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Mobile App

```bash
cd apps/mobile
npm install
npx expo start --android
```

---

## 📁 Structure

```
sih_ps_1/
├── apps/mobile/      # React Native (Expo SDK 56), TypeScript
│   ├── app/          # expo-router screens (index/crop/weather/disease/soil/market)
│   └── src/          # theme, API service, Zustand store, i18n
├── apps/backend/     # FastAPI + PostgreSQL + Redis
│   └── app/          # routers / services / models / db
├── docker-compose.yml
└── README.md
```

---

## 🧩 6 Modules

| Module | Key Punjab Feature |
|--------|--------------------|
| Crop Advisory | Electricity slot scheduling, stubble flag |
| Weather & Alerts | Irrigation slot alerts, frost/heatwave/pest-risk |
| Pest Detection | On-device TFLite (offline), 4 disease classes |
| Voice + i18n | Punjabi (Gurmukhi) / Hindi / English TTS |
| Soil & Fertilizer | Malwa zinc correction, split NPK schedule |
| Market Prices | MSP comparison, 7-day sparkline, Agmarknet |

---

*Made with ❤️ for Punjab's farmers — SIH 2025*
