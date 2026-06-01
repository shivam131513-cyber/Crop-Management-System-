import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, typography } from '../src/constants/theme';
import { cropApi } from '../src/services/api';
import { useAppStore } from '../src/store/appStore';
import * as Speech from 'expo-speech';

const SEASONS = [
  { value: 'kharif', label: 'Kharif', label_pa: 'ਖਰੀਫ਼', icon: '🌧️' },
  { value: 'rabi',   label: 'Rabi',   label_pa: 'ਰਬੀ',   icon: '❄️' },
  { value: 'zaid',   label: 'Zaid',   label_pa: 'ਜ਼ੈਦ',  icon: '☀️' },
];

const WATER = [
  { value: 'high',   label_pa: 'ਵੱਧ',         icon: '💧💧💧' },
  { value: 'medium', label_pa: 'ਦਰਮਿਆਨਾ',   icon: '💧💧' },
  { value: 'low',    label_pa: 'ਘੱਟ',         icon: '💧' },
];

const SOIL_TYPES = [
  { value: 'loamy',      label_pa: 'ਦੋਮਟ' },
  { value: 'sandy-loam', label_pa: 'ਰੇਤਲੀ ਦੋਮਟ' },
  { value: 'clay',       label_pa: 'ਮਿੱਟੀ' },
  { value: 'alluvial',   label_pa: 'ਕਾਂਪ' },
];

function SelectorRow({ label, options, selected, onSelect }: any) {
  return (
    <View style={styles.selectorBlock}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <View style={styles.chips}>
        {options.map((opt: any) => (
          <TouchableOpacity
            key={opt.value}
            style={[styles.chip, selected === opt.value && styles.chipActive]}
            onPress={() => onSelect(opt.value)}
          >
            {opt.icon && <Text style={{ marginRight: 4 }}>{opt.icon}</Text>}
            <Text style={[styles.chipText, selected === opt.value && styles.chipTextActive]}>
              {opt.label_pa || opt.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

function CropCard({ crop, index }: { crop: any; index: number }) {
  const medals = ['🥇', '🥈', '🥉'];
  const scoreColor = crop.suitability_score > 0.7 ? colors.success
    : crop.suitability_score > 0.4 ? colors.warning : colors.danger;

  const speakCrop = () => {
    Speech.speak(
      `${crop.local_name_pa}। ਝਾੜ ${crop.expected_yield_qtl_per_acre} ਕੁਇੰਟਲ ਪ੍ਰਤੀ ਏਕੜ। ${crop.advice}`,
      { language: 'pa-IN' }
    );
  };

  return (
    <View style={[styles.cropCard, !crop.stubble_friendly && styles.cropCardWarning]}>
      <View style={styles.cropHeader}>
        <Text style={styles.medal}>{medals[index] || '🌱'}</Text>
        <View style={{ flex: 1 }}>
          <Text style={styles.cropName}>{crop.local_name_pa}</Text>
          <Text style={styles.cropNameEn}>{crop.name}</Text>
        </View>
        <TouchableOpacity onPress={speakCrop} style={styles.speakBtn}>
          <Ionicons name="volume-high" size={20} color={colors.accent} />
        </TouchableOpacity>
        <View style={[styles.scoreBadge, { backgroundColor: scoreColor + '22' }]}>
          <Text style={[styles.scoreText, { color: scoreColor }]}>
            {Math.round(crop.suitability_score * 100)}%
          </Text>
        </View>
      </View>

      <View style={styles.cropStats}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>ਝਾੜ</Text>
          <Text style={styles.statValue}>{crop.expected_yield_qtl_per_acre} ਕਿ/ਏ</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>ਮਿਆਦ</Text>
          <Text style={styles.statValue}>{crop.duration_days} ਦਿਨ</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>ਪਾਣੀ</Text>
          <Text style={styles.statValue}>{crop.water_req === 'high' ? 'ਵੱਧ' : crop.water_req === 'medium' ? 'ਦਰਮਿਆਨਾ' : 'ਘੱਟ'}</Text>
        </View>
        {crop.msp_per_quintal && (
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>MSP</Text>
            <Text style={styles.statValue}>₹{crop.msp_per_quintal}</Text>
          </View>
        )}
      </View>

      <Text style={styles.advice}>💡 {crop.advice}</Text>

      {!crop.stubble_friendly && (
        <View style={styles.stubbleWarn}>
          <Ionicons name="warning" size={14} color={colors.warning} />
          <Text style={styles.stubbleText}> ਪਰਾਲੀ ਸਾੜਨ ਦਾ ਖ਼ਤਰਾ</Text>
        </View>
      )}
    </View>
  );
}

export default function CropScreen() {
  const { profile, saveCropRecommendation, loadCachedCropRecommendation } = useAppStore();
  const [season, setSeason] = useState('kharif');
  const [soil, setSoil] = useState('loamy');
  const [water, setWater] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [fromCache, setFromCache] = useState(false);
  const [cachedAt, setCachedAt] = useState<number | null>(null);

  const currentQuery = {
    district: profile.district,
    season,
    soil,
    water,
  };

  const getAdvice = async () => {
    setLoading(true);
    setFromCache(false);
    try {
      const resp = await cropApi.recommend({
        district: profile.district,
        soil_type: soil,
        season,
        water_availability: water,
        land_size_acres: profile.landAcres || 2,
      });
      setResult(resp.data);
      // Persist to offline cache so farmer can access without internet
      await saveCropRecommendation(currentQuery, resp.data);
    } catch (err: any) {
      // Network error — try the offline cache before showing error
      const cached = await loadCachedCropRecommendation(currentQuery);
      if (cached) {
        setResult(cached);
        setFromCache(true);
        setCachedAt(cached._cachedAt ?? null);
        Alert.alert(
          'ਆਫ਼ਲਾਈਨ ਮੋਡ',
          'ਇੰਟਰਨੈੱਟ ਨਹੀਂ ਮਿਲਿਆ। ਪਿਛਲੀ ਸੇਵ ਕੀਤੀ ਫ਼ਸਲ ਸਲਾਹ ਦਿਖਾਈ ਜਾ ਰਹੀ ਹੈ।',
        );
      } else {
        Alert.alert('ਗਲਤੀ', 'ਸਲਾਹ ਲੈਣ ਵਿੱਚ ਸਮੱਸਿਆ। ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Selector form */}
      <View style={styles.formCard}>
        <SelectorRow label="ਮੌਸਮ ਚੁਣੋ" options={SEASONS} selected={season} onSelect={setSeason} />
        <SelectorRow label="ਮਿੱਟੀ ਦੀ ਕਿਸਮ" options={SOIL_TYPES} selected={soil} onSelect={setSoil} />
        <SelectorRow label="ਪਾਣੀ ਦੀ ਉਪਲਬਧਤਾ" options={WATER} selected={water} onSelect={setWater} />

        <TouchableOpacity style={styles.submitBtn} onPress={getAdvice} disabled={loading}>
          {loading
            ? <ActivityIndicator color="#fff" />
            : <Text style={styles.submitText}>🌾 ਫ਼ਸਲ ਸਲਾਹ ਲਓ</Text>
          }
        </TouchableOpacity>
      </View>

      {/* Results */}
      {result && (
        <View>
          {/* Offline cache banner */}
          {fromCache && (
            <View style={styles.cacheBanner}>
              <Ionicons name="cloud-offline-outline" size={14} color="#7EC8E3" />
              <Text style={styles.cacheBannerText}>
                {' '}ਆਫ਼ਲਾਈਨ ਡੇਟਾ
                {cachedAt ? ` · ${new Date(cachedAt).toLocaleDateString('pa-IN')}` : ''}
              </Text>
            </View>
          )}

          {/* Stubble warning */}
          {result.stubble_warning && (
            <View style={styles.stubbleCard}>
              <Text style={styles.stubbleCardTitle}>⚠️ ਪਰਾਲੀ ਸਾੜਨ ਦੀ ਚੇਤਾਵਨੀ</Text>
              <Text style={styles.stubbleCardText}>{result.stubble_warning}</Text>
            </View>
          )}

          {/* Irrigation slots */}
          {result.irrigation_slots && (
            <View style={styles.slotsCard}>
              <Text style={styles.slotCardTitle}>⚡ ਮੁਫ਼ਤ ਬਿਜਲੀ ਸਿੰਚਾਈ ਸਲਾਟ</Text>
              {result.irrigation_slots.map((s: string, i: number) => (
                <Text key={i} style={styles.slotItem}>• {s}</Text>
              ))}
            </View>
          )}

          {/* Crops */}
          <Text style={styles.sectionTitle}>ਸਿਫ਼ਾਰਸ਼ੀ ਫ਼ਸਲਾਂ</Text>
          {result.recommended_crops.map((crop: any, i: number) => (
            <CropCard key={crop.name} crop={crop} index={i} />
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },
  content: { padding: spacing.md, paddingBottom: 100 },
  formCard: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, marginBottom: spacing.md,
  },
  selectorBlock: { marginBottom: spacing.md },
  fieldLabel: { ...typography.label, marginBottom: spacing.sm },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  chip: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 14, paddingVertical: 8,
    backgroundColor: colors.bgSurface, borderRadius: radius.full,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  chipActive: { backgroundColor: colors.primary + '44', borderColor: colors.accent },
  chipText: { color: colors.textSecondary, fontSize: 13 },
  chipTextActive: { color: colors.accent, fontWeight: '600' },
  submitBtn: {
    backgroundColor: colors.primaryLighter, borderRadius: radius.lg,
    padding: spacing.md, alignItems: 'center', marginTop: spacing.sm,
  },
  submitText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  sectionTitle: { ...typography.h3, marginVertical: spacing.md },
  cropCard: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, marginBottom: spacing.md,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  cropCardWarning: { borderColor: colors.warning + '44' },
  cropHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.sm },
  medal: { fontSize: 22, marginRight: spacing.sm },
  cropName: { fontSize: 18, fontWeight: '700', color: colors.textPrimary },
  cropNameEn: { fontSize: 12, color: colors.textSecondary },
  speakBtn: { padding: 6, marginRight: spacing.sm },
  scoreBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: radius.full },
  scoreText: { fontSize: 13, fontWeight: '700' },
  cropStats: {
    flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  statItem: {
    backgroundColor: colors.bgSurface, borderRadius: radius.sm,
    paddingHorizontal: 10, paddingVertical: 6, minWidth: 70,
  },
  statLabel: { fontSize: 10, color: colors.textSecondary },
  statValue: { fontSize: 13, fontWeight: '600', color: colors.textPrimary },
  advice: { fontSize: 13, color: colors.textSecondary, lineHeight: 18 },
  stubbleWarn: {
    flexDirection: 'row', alignItems: 'center',
    marginTop: spacing.sm, backgroundColor: colors.warning + '11',
    padding: spacing.sm, borderRadius: radius.sm,
  },
  stubbleText: { color: colors.warning, fontSize: 12 },
  stubbleCard: {
    backgroundColor: '#2D1A00', borderRadius: radius.lg,
    padding: spacing.md, marginBottom: spacing.md,
    borderLeftWidth: 3, borderLeftColor: colors.warning,
  },
  stubbleCardTitle: { color: colors.warning, fontWeight: '700', marginBottom: 6 },
  stubbleCardText: { color: '#D4A017', fontSize: 13, lineHeight: 18 },
  slotsCard: {
    backgroundColor: '#001A0D', borderRadius: radius.lg,
    padding: spacing.md, marginBottom: spacing.md,
    borderLeftWidth: 3, borderLeftColor: '#FFD700',
  },
  slotCardTitle: { color: '#FFD700', fontWeight: '700', marginBottom: 6 },
  slotItem: { color: colors.accentSoft, fontSize: 13, marginVertical: 2 },
  cacheBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0A1628',
    borderRadius: radius.sm,
    padding: spacing.sm,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: '#7EC8E344',
  },
  cacheBannerText: {
    color: '#7EC8E3',
    fontSize: 12,
    fontStyle: 'italic',
  },
});
