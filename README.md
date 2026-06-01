# ਕਿਸਾਨ ਸਾਥੀ — Kisaan Saathi

**AI-Powered Crop Advisory App for Punjab Farmers**

> SIH 2025 Problem Statement: **PS1 (SIH25010)** — Punjab Agriculture

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Expo](https://img.shields.io/badge/Mobile-Expo%20React%20Native-000020)](https://expo.dev/)
[![Offline](https://img.shields.io/badge/Works-Offline%20%E2%9C%93-4CAF50)](https://docs.expo.dev/guides/offline-support/)
[![Languages](https://img.shields.io/badge/Languages-ਪੰਜਾਬੀ%20%7C%20हिंदी%20%7C%20English-orange)](https://github.com/shivam131513-cyber/Crop-Management-System-)
[![License](https://img.shields.io/badge/License-MIT-blue)](./apps/mobile/LICENSE)

---

## 🎯 Problem It Solves

86% of Indian farmers are small or marginal. They lack access to:
- Expert crop selection guidance based on soil, zone, and season
- Real-time soil and weather data in their local language
- Pest and disease identification (without internet)
- Market price vs MSP comparison
- All of the above in **Punjabi (Gurmukhi)**

**Kisaan Saathi** solves this with an offline-first, multilingual, AI-powered mobile app tailored specifically for Punjab's three soil zones.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Mobile (Expo RN + TypeScript)                 │
│  Home ─ Crop ─ Weather ─ Disease ─ Soil ─ Market ─ Diary        │
│  Zustand store │ AsyncStorage cache (TTL) │ TFLite (on-device)   │
│  i18n: Punjabi (Gurmukhi) / Hindi / English  (3-way toggle)     │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS (GZip, 2G-optimized)
┌────────────────────────▼────────────────────────────────────────┐
│               FastAPI Backend (Python 3.11)                      │
│  /auth  /crop  /weather  /pest  /soil  /market                  │
│  JWT Auth │ Pydantic v2 │ SQLAlchemy 2 │ Rate Limiting           │
└──────┬────────────────────────────────────────┬─────────────────┘
       │                                        │
  PostgreSQL / SQLite                      Redis cache
  (farmers, crops,                     (rate-limit, session)
   diseases, prices)
       │
  External APIs:
  OpenWeatherMap │ Agmarknet (fallback: curated mock)
```

---

## 🏆 Punjab-Specific Differentiators

| Feature | Description |
|---------|-------------|
| ⚡ **Electricity-Aware Irrigation** | Punjab tube-well free electricity slots (5 AM–8 AM, 10 PM–1 AM) integrated into weather alerts and irrigation schedules |
| ♻️ **Stubble Burning Alternatives** | Flags rice cultivation → suggests Happy Seeder, Bio-decomposer with govt incentives (₹2,500–₹17,500/acre) |
| 📱 **Offline-First** | AsyncStorage TTL cache, on-device TFLite disease detection, 2G-optimized API (GZip) |
| 🌾 **3 Soil Zones** | Majha / Malwa / Doaba with zone-specific NPK defaults and zinc correction |
| 🌍 **3-Language Toggle** | One-tap PA/HI/EN switch with animated confirmation |
| 📊 **MSP Price Alerts** | `/market/alert` warns farmers below-MSP with helpline + e-NAM + storage advice |
| 🗓️ **12-Month Crop Calendar** | Month-wise Punjab sowing, fertilization, harvest calendar with zone-specific notes |
| 💰 **Profit Estimator** | Full cost-revenue breakdown (input cost, MSP revenue, net profit, margin %) per crop |
| 🧪 **Soil Health Report** | NPK/pH/zinc diagnosis → 0–100 health score + prioritized correction plan |
| 🛡️ **Rate Limiting** | Sliding-window rate limiter (Redis + in-memory fallback) protects all endpoints |
| 📒 **Farm Diary** | Offline activity log (irrigation, fertilizer, pesticide, sowing, harvest) with local persistence |
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
| `REDIS_URL` | `redis://localhost:6379` | Cache / rate-limiter (optional — falls back to in-memory) |

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
| `GET`  | `/crop/calendar` | Month-wise Punjab sowing calendar (`?district=ludhiana&month=6`) |
| `POST` | `/crop/profit-estimate` | Full profit/loss breakdown for a crop + land size |

### Weather `/weather`
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/weather/forecast` | 7-day forecast + farm alerts + monthly sowing advice |

### Pest & Disease `/pest`
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/pest/detect` | Upload leaf image → disease ID + treatment (8 disease classes) |
| `GET`  | `/pest/diseases` | List all detectable diseases |

### Soil & Fertilizer `/soil`
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/soil/recommend` | NPK fertilizer schedule + zinc correction |
| `POST` | `/soil/irrigation` | Irrigation schedule aligned to electricity slots |
| `POST` | `/soil/health-report` | Soil health diagnosis: NPK/pH/zinc → 0–100 score + correction plan |
| `GET`  | `/soil/zones` | Punjab soil zone profiles (Majha / Malwa / Doaba) |

### Market Prices `/market`
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/market/prices` | Mandi prices vs MSP for a district |
| `POST` | `/market/alert` | Below-MSP alert with recommended actions |
| `GET`  | `/market/msp` | Official MSP 2024–25 for all crops |

---

## 📁 Project Structure

```
sih_ps_1/
├── apps/
│   ├── mobile/                    # React Native (Expo SDK 56), TypeScript
│   │   ├── app/                   # expo-router screens
│   │   │   ├── index.tsx          # Home screen with language toggle
│   │   │   ├── crop.tsx           # Crop advisory + offline cache
│   │   │   ├── weather.tsx        # 7-day forecast + farm alerts
│   │   │   ├── disease.tsx        # Pest/disease detection
│   │   │   ├── soil.tsx           # Soil & fertilizer advisory
│   │   │   ├── market.tsx         # Mandi prices vs MSP
│   │   │   └── diary.tsx          # Farm diary (offline)
│   │   └── src/
│   │       ├── constants/theme.ts # Design tokens
│   │       ├── i18n/              # PA / HI / EN translations
│   │       ├── services/
│   │       │   ├── api.ts         # Axios API client
│   │       │   └── offlineCache.ts # AsyncStorage TTL cache
│   │       └── store/appStore.ts  # Zustand global state
│   └── backend/                   # FastAPI + PostgreSQL + Redis
│       └── app/
│           ├── main.py            # App entry + middleware registration
│           ├── middleware/
│           │   └── rate_limit.py  # Sliding-window rate limiter
│           ├── routers/           # auth, crop, weather, pest, soil, market
│           ├── services/          # crop_service, crop_knowledge (12-month calendar)
│           ├── models/            # Pydantic schemas
│           └── db/                # SQLAlchemy models + Alembic migrations
├── docker-compose.yml
└── README.md
```

---

## 🧩 8 Modules

| Module | Key Punjab Feature |
|--------|-------------------|
| **Auth** | JWT (HS256), phone login, refresh tokens |
| **Crop Advisory** | Zone scoring, stubble flag, electricity slot scheduling |
| **Crop Calendar** | 12-month sowing/fertilizer/harvest calendar (Majha/Malwa/Doaba) |
| **Profit Estimator** | Input cost vs MSP revenue → net profit, margin %, is_profitable |
| **Weather & Alerts** | Irrigation slot alerts, frost/heatwave, monthly sowing windows |
| **Pest Detection** | On-device TFLite (offline), 8 disease classes |
| **Soil & Fertilizer** | NPK schedule, zinc correction, soil health report (0–100 score) |
| **Market Prices** | MSP comparison, 7-day sparkline, below-MSP alert |
| **Farm Diary** | Offline activity log with 7 activity types, filter bar |
| **i18n** | Punjabi (Gurmukhi) / Hindi / English — complete 3-language coverage |

---

## 🔒 Security & Production Readiness

- **Rate Limiting**: Sliding-window rate limiter on all endpoints (Redis / in-memory fallback)
  - `/auth/login`: 10 req/60s (brute-force protection)
  - `/pest/detect`: 20 req/60s (image inference protection)
  - Global: 200 req/60s per IP
- **JWT**: HS256, 1-day access + 30-day refresh tokens; OTP-ready for production
- **GZip**: All API responses compressed (2G network optimized)
- **Offline**: 7-day crop recommendation cache; 6-hour weather cache

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit with conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
4. Open a Pull Request

---

*Made with ❤️ for Punjab's farmers — SIH 2025 (PS1 · SIH25010)*

[![Languages](https://img.shields.io/badge/Languages-ਪੰਜਾਬੀ%20%7C%20हिंदी%20%7C%20English-orange)]()
