# ਕਿਸਾਨ ਸਾਥੀ — Kisaan Saathi

**AI-Powered Crop Advisory App for Punjab Farmers**

> SIH 2025 Problem Statement: **PS1 (SIH25010)** — Punjab

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Expo](https://img.shields.io/badge/Mobile-Expo%20React%20Native-000020)](https://expo.dev/)
[![Offline](https://img.shields.io/badge/Works-Offline%20%E2%9C%93-4CAF50)](https://docs.expo.dev/guides/offline-support/)
[![Languages](https://img.shields.io/badge/Languages-ਪੰਜਾਬੀ%20%7C%20हिंदी%20%7C%20English-orange)](https://github.com/shivam131513-cyber/Crop-Management-System-)
[![License](https://img.shields.io/badge/License-MIT-blue)](./apps/mobile/LICENSE)

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
| ⚡ **Electricity-Aware Irrigation** | Punjab tube-well free electricity slots (5 AM–8 AM, 10 PM–1 AM) integrated into weather alerts and irrigation schedules |
| ♻️ **Stubble Burning Alternatives** | Flags rice cultivation → suggests Happy Seeder, Bio-decomposer with govt incentives (₹2,500–₹17,500/acre) |
| 📱 **Offline-First** | SQLite cache, on-device TFLite disease detection, 2G-optimized API (GZip) |
| 🌾 **3 Soil Zones** | Majha / Malwa / Doaba with zone-specific NPK defaults and zinc correction |
| 🌍 **3-Language Toggle** | One-tap PA/HI/EN switch on home screen with animated confirmation |
| 📊 **MSP Price Alerts** | `/market/alert` warns farmers below-MSP with helpline + e-NAM + storage advice |
| 🗓️ **Sowing Windows** | Weather forecast includes month-specific Punjab crop sowing calendars |
| 🔐 **JWT Auth** | Phone-based login, access + refresh token flow (OTP-ready for production) |

---

## 🚀 Quick Start

### Backend

```bash
cd apps/backend
cp .env.example .env
# Edit .env: set OPENWEATHERMAP_KEY and JWT_SECRET

# Docker (recommended)
docker-compose up -d

# Local Python 3.11+
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

## 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./kisaan.db` | PostgreSQL or SQLite URI |
| `OPENWEATHERMAP_KEY` | *(empty)* | OWM API key for live forecast |
| `JWT_SECRET` | `kisaan-saathi-secret-key-...` | HS256 signing key — **change in production** |
| `REDIS_URL` | `redis://localhost:6379` | Cache / rate-limiter |

---

## 📡 API Endpoints

### Auth `/auth`
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/login` | Phone-based login → returns JWT access + refresh tokens |
| `POST` | `/auth/refresh` | Exchange refresh token for new access token |
| `POST` | `/auth/profile` | Create / update farmer profile |
| `GET`  | `/auth/profile/{id}` | Fetch farmer profile *(requires Bearer token)* |

### Crop Advisory `/crop`
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/crop/recommend` | Top-3 crop recommendations (soil, season, water, zone) |
| `GET`  | `/crop/seasons` | Kharif / Rabi / Zaid season list |
| `GET`  | `/crop/soil-types` | Punjab soil type list |

### Weather `/weather`
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/weather/forecast` | 7-day forecast + farm alerts + **monthly sowing advice** |

### Pest & Disease `/pest`
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/pest/detect` | Upload leaf image → disease ID + treatment (8 disease classes) |
| `GET`  | `/pest/diseases` | List all detectable diseases |

### Soil & Fertilizer `/soil`
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/soil/recommend` | NPK fertilizer schedule + zinc correction |
| `POST` | `/soil/irrigation` | Irrigation schedule aligned to electricity slots + water table depth |
| `GET`  | `/soil/zones` | Punjab soil zone profiles (Majha / Malwa / Doaba) |

### Market Prices `/market`
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/market/prices` | Mandi prices vs MSP for a district (5 districts) |
| `POST` | `/market/alert` | Below-MSP alert with recommended actions in Punjabi |
| `GET`  | `/market/msp` | Official MSP 2024–25 for all crops |

---

## 🧱 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Mobile (Expo RN + TS)                    │
│  Home ─ Crop ─ Weather ─ Disease ─ Soil ─ Market           │
│  Zustand store │ SQLite cache │ TFLite (on-device ML)       │
│  i18n: Punjabi / Hindi / English (3-way toggle)             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS (GZip, 2G-optimized)
┌────────────────────────▼────────────────────────────────────┐
│               FastAPI Backend (Python 3.11)                 │
│  /auth  /crop  /weather  /pest  /soil  /market             │
│  JWT Auth │ Pydantic v2 │ SQLAlchemy 2 │ Alembic            │
└──────┬────────────────────────────────────────┬─────────────┘
       │                                        │
  PostgreSQL                              Redis cache
  (farmers, crops,                    (rate-limit, session)
   diseases, prices)
       │
  External APIs:
  OpenWeatherMap │ Agmarknet (fallback: curated mock)
```

---

## 📁 Structure

```
sih_ps_1/
├── apps/mobile/          # React Native (Expo SDK 56), TypeScript
│   ├── app/              # expo-router screens (index/crop/weather/disease/soil/market)
│   └── src/              # theme, API service, Zustand store, i18n (pa/hi/en)
├── apps/backend/         # FastAPI + PostgreSQL + Redis
│   └── app/
│       ├── routers/      # auth, crop, weather, pest, soil, market
│       ├── services/     # crop_service, crop_knowledge
│       ├── models/       # Pydantic schemas
│       └── db/           # SQLAlchemy models + Alembic
├── docker-compose.yml
└── README.md
```

---

## 🧩 7 Modules

| Module | Key Punjab Feature |
|--------|--------------------|
| **Auth** | JWT (HS256), phone login, refresh tokens |
| **Crop Advisory** | Electricity slot scheduling, stubble flag, zone scoring |
| **Weather & Alerts** | Irrigation slot alerts, frost/heatwave, sowing windows |
| **Pest Detection** | On-device TFLite (offline), 8 disease classes |
| **Soil & Fertilizer** | Malwa zinc correction, split NPK, irrigation schedule |
| **Market Prices** | MSP comparison, 7-day sparkline, below-MSP alert |
| **i18n** | Punjabi (Gurmukhi) / Hindi / English, 3-way toggle |

---

## 👥 Team

SIH 2025 — Problem Statement **SIH25010**

*Made with ❤️ for Punjab's farmers*

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
