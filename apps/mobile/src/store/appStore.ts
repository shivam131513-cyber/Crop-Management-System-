import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface FarmerProfile {
  name?: string;
  district: string;
  village?: string;
  landAcres?: number;
  soilZone?: string;
  language: 'pa' | 'hi' | 'en';
  onboardingDone: boolean;
}

interface AppStore {
  profile: FarmerProfile;
  isOnline: boolean;
  setProfile: (p: Partial<FarmerProfile>) => void;
  setOnline: (v: boolean) => void;
  loadProfile: () => Promise<void>;
}

export const useAppStore = create<AppStore>((set, get) => ({
  profile: {
    district: 'ludhiana',
    language: 'pa',
    onboardingDone: false,
  },
  isOnline: true,

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
}));
