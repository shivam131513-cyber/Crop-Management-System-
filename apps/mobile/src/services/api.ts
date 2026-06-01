import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000'; // Android emulator

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor: attach district from stored profile
api.interceptors.request.use(async (config) => {
  try {
    const profile = await AsyncStorage.getItem('farmer_profile');
    if (profile) {
      const p = JSON.parse(profile);
      if (p.district) {
        config.headers['X-District'] = p.district;
      }
    }
  } catch (_) {}
  return config;
});

// Response interceptor: cache to AsyncStorage on success
api.interceptors.response.use(
  async (response) => {
    const cacheKey = `cache_${response.config.url}_${JSON.stringify(response.config.params)}`;
    try {
      await AsyncStorage.setItem(cacheKey, JSON.stringify({
        data: response.data,
        ts: Date.now(),
      }));
    } catch (_) {}
    return response;
  },
  async (error) => {
    // On network error, try cache
    if (!error.response) {
      const cacheKey = `cache_${error.config?.url}_${JSON.stringify(error.config?.params)}`;
      try {
        const cached = await AsyncStorage.getItem(cacheKey);
        if (cached) {
          const parsed = JSON.parse(cached);
          return { data: { ...parsed.data, _fromCache: true, _cachedAt: parsed.ts } };
        }
      } catch (_) {}
    }
    return Promise.reject(error);
  }
);

// ── API methods ───────────────────────────────────────────
export const cropApi = {
  recommend: (payload: object) => api.post('/crop/recommend', payload),
  getSeasons: () => api.get('/crop/seasons'),
  getSoilTypes: () => api.get('/crop/soil-types'),
  getCalendar: (district?: string, month?: number) =>
    api.get('/crop/calendar', { params: { district, month } }),
  getProfitEstimate: (payload: object) => api.post('/crop/profit-estimate', payload),
};

export const weatherApi = {
  getForecast: (district: string) => api.get('/weather/forecast', { params: { district } }),
};

export const pestApi = {
  detect: (formData: FormData) =>
    api.post('/pest/detect', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  listDiseases: () => api.get('/pest/diseases'),
};

export const soilApi = {
  recommend: (payload: object) => api.post('/soil/recommend', payload),
  getZones: () => api.get('/soil/zones'),
  healthReport: (payload: object) => api.post('/soil/health-report', payload),
};

export const marketApi = {
  getPrices: (district: string, crop?: string) =>
    api.get('/market/prices', { params: { district, crop } }),
  getMsp: () => api.get('/market/msp'),
};

export default api;
