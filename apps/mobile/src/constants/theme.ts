// Design tokens for Kisaan Saathi
// Green-first palette inspired by Punjab's agricultural landscape

export const colors = {
  // Brand
  primary: '#1B4332',      // Deep forest green
  primaryLight: '#2D6A4F',
  primaryLighter: '#40916C',
  accent: '#40C974',       // Vibrant lime green
  accentSoft: '#52B788',

  // Background
  bgDark: '#0D1117',
  bgCard: '#161B22',
  bgCardHover: '#1C2128',
  bgSurface: '#21262D',

  // Text
  textPrimary: '#E6EDF3',
  textSecondary: '#8B949E',
  textMuted: '#484F58',

  // Status
  success: '#3FB950',
  warning: '#E3B341',
  danger: '#F85149',
  info: '#58A6FF',

  // Zone colors
  majha: '#9ECBFF',
  malwa: '#FFA657',
  doaba: '#7EE787',

  // Overlay
  overlay: 'rgba(0,0,0,0.6)',
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 999,
};

export const typography = {
  h1: { fontSize: 28, fontWeight: '700' as const, color: '#E6EDF3' },
  h2: { fontSize: 22, fontWeight: '700' as const, color: '#E6EDF3' },
  h3: { fontSize: 18, fontWeight: '600' as const, color: '#E6EDF3' },
  body: { fontSize: 15, fontWeight: '400' as const, color: '#8B949E' },
  bodyBold: { fontSize: 15, fontWeight: '600' as const, color: '#E6EDF3' },
  caption: { fontSize: 12, fontWeight: '400' as const, color: '#484F58' },
  label: { fontSize: 13, fontWeight: '600' as const, color: '#8B949E' },
};
