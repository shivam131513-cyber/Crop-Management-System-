import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { cacheSet, cacheGet, cachePurgeExpired, TTL } from '../services/offlineCache';

// ── Types ─────────────────────────────────────────────────────────────────────

interface FarmerProfile {
  name?: string;
  district: string;
  village?: string;
  landAcres?: number;
  soilZone?: string;
  language: 'pa' | 'hi' | 'en';
  onboardingDone: boolean;
}

export interface CropRecommendation {
  recommended_crops: Array<{
    name: string;
    local_name_hi: string;
    local_name_pa: string;
    expected_yield_qtl_per_acre: number;
    water_req: string;
    duration_days: number;
    msp_per_quintal: number | null;
    input_cost_per_acre: number;
    suitability_score: number;
    stubble_friendly: boolean;
    advice: string;
  }>;
  irrigation_slots: string[] | null;
  stubble_warning: string | null;
  season_tip: string | null;
  /** Set to true when loaded from local cache (no internet) */
  _fromCache?: boolean;
  _cachedAt?: number;
}

interface AppStore {
  profile: FarmerProfile;
  isOnline: boolean;

  // Last crop recommendation (persisted to cache)
  lastCropRecommendation: CropRecommendation | null;
  lastCropQuery: { district: string; season: string; soil: string; water: string } | null;

  // Actions
  setProfile: (p: Partial<FarmerProfile>) => void;
  setOnline: (v: boolean) => void;
  loadProfile: () => Promise<void>;

  /** Save a fresh crop recommendation from the API to cache. */
  saveCropRecommendation: (
    query: { district: string; season: string; soil: string; water: string },
    result: CropRecommendation,
  ) => Promise<void>;

  /** Try to restore the last crop recommendation from cache. */
  loadCachedCropRecommendation: (
    query: { district: string; season: string; soil: string; water: string },
  ) => Promise<CropRecommendation | null>;

  /** On app start: purge expired entries and restore profile. */
  initApp: () => Promise<void>;
}

// ── Store ─────────────────────────────────────────────────────────────────────

export const useAppStore = create<AppStore>((set, get) => ({
  profile: {
    district: 'ludhiana',
    language: 'pa',
    onboardingDone: false,
  },
  isOnline: true,
  lastCropRecommendation: null,
  lastCropQuery: null,

  // ── Profile ────────────────────────────────────────────────────────────────

  setProfile: async (p) => {
    const updated = { ...get().profile, ...p };
    set({ profile: updated });
    await AsyncStorage.setItem('farmer_profile', JSON.stringify(updated));
  },

  setOnline: (v) => set({ isOnline: v }),

  loadProfile: async () => {
    try {
      const stored = await AsyncStorage.getItem('farmer_profile');
      if (stored) set({ profile: JSON.parse(stored) });
    } catch (_) {}
  },

  // ── Crop recommendation cache ───────────────────────────────────────────────

  saveCropRecommendation: async (query, result) => {
    // Store in Zustand state
    set({ lastCropRecommendation: result, lastCropQuery: query });

    // Persist to AsyncStorage with 7-day TTL
    await cacheSet('crop_recommend', query, result, TTL.CROP_RECOMMENDATION);
  },

  loadCachedCropRecommendation: async (query) => {
    const cached = await cacheGet<CropRecommendation>('crop_recommend', query);
    if (!cached) return null;

    const result: CropRecommendation = {
      ...cached.data,
      _fromCache: true,
      _cachedAt: cached.cachedAt,
    };
    set({ lastCropRecommendation: result, lastCropQuery: query });
    return result;
  },

  // ── App initialisation ─────────────────────────────────────────────────────

  initApp: async () => {
    // Restore profile
    try {
      const stored = await AsyncStorage.getItem('farmer_profile');
      if (stored) set({ profile: JSON.parse(stored) });
    } catch (_) {}

    // Housekeeping: remove expired cache entries
    try {
      await cachePurgeExpired();
    } catch (_) {}
  },
}));
