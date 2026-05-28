import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, typography } from '../src/constants/theme';
import { soilApi } from '../src/services/api';
import { useAppStore } from '../src/store/appStore';
import * as Speech from 'expo-speech';

const CROPS = [
  { value: 'wheat',   label_pa: 'ਕਣਕ',    emoji: '🌾' },
  { value: 'rice',    label_pa: 'ਚੌਲ',    emoji: '🌾' },
  { value: 'maize',   label_pa: 'ਮੱਕੀ',   emoji: '🌽' },
  { value: 'cotton',  label_pa: 'ਕਪਾਹ',   emoji: '🌿' },
  { value: 'mustard', label_pa: 'ਸਰ੍ਹੋਂ', emoji: '🌻' },
  { value: 'potato',  label_pa: 'ਆਲੂ',    emoji: '🥔' },
  { value: 'moong',   label_pa: 'ਮੂੰਗ',   emoji: '🫘' },
];

function NPKBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <View style={styles.npkRow}>
      <Text style={styles.npkLabel}>{label}</Text>
      <View style={styles.npkBarBg}>
        <View style={[styles.npkBarFill, { width: `${pct}%` as any, backgroundColor: color }]} />
      </View>
      <Text style={styles.npkValue}>{value} kg/ਏਕੜ</Text>
    </View>
  );
}

export default function SoilScreen() {
  const { profile } = useAppStore();
  const [selectedCrop, setSelectedCrop] = useState('wheat');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const getRecommendation = async () => {
    setLoading(true);
    try {
      const resp = await soilApi.recommend({
        crop: selectedCrop,
        district: profile.district,
        land_size_acres: profile.landAcres || 2,
      });
      setResult(resp.data);
    } catch {
      // Demo fallback
      setResult({
        crop: selectedCrop,
        zone: 'malwa',
        npk_recommendation: { N: 55, P: 25, K: 12 },
        fertilizer_schedule: [
          { stage: 'ਬਿਜਾਈ ਸਮੇਂ', timing: 'ਦਿਨ 0', npk_kg_per_acre: { N: 27, P: 25, K: 12 }, note: 'DAP + ਯੂਰੀਆ ਬੇਸਲ।' },
          { stage: '1ਲੀ ਉੱਪਰੀ ਖੁਰਾਕ', timing: '21–25 ਦਿਨ', npk_kg_per_acre: { N: 17, P: 0, K: 0 }, note: 'ਯੂਰੀਆ CRI ਪੜਾਅ।' },
          { stage: '2ਲੀ ਉੱਪਰੀ ਖੁਰਾਕ', timing: '45–50 ਦਿਨ', npk_kg_per_acre: { N: 11, P: 0, K: 0 }, note: 'ਬਾਕੀ ਨਾਈਟ੍ਰੋਜਨ।' },
        ],
        zinc_correction: 'ਜ਼ਿੰਕ ਸਲਫੇਟ @ 10 kg/ਏਕੜ — ਹਰ 3 ਸਾਲ ਵਿੱਚ ਇੱਕ ਵਾਰ।',
        stubble_alternatives: selectedCrop === 'rice' ? [
          { method: 'Happy Seeder', description: 'ਨਾੜ ਵਿੱਚ ਸਿੱਧੀ ਕਣਕ ਬਿਜਾਈ।', govt_incentive: '₹2,500/ਏਕੜ' },
          { method: 'ਬਾਇਓ-ਡੀਕੰਪੋਜ਼ਰ', description: 'PUSA 20 ਦਿਨਾਂ ਵਿੱਚ ਨਾੜ ਨੂੰ ਖਾਦ ਬਣਾਉਂਦਾ ਹੈ।', govt_incentive: 'ਮੁਫ਼ਤ ਕੈਪਸੂਲ' },
        ] : null,
        organic_tip: '2–4 ਟਨ ਰੂੜੀ ਖਾਦ ਪ੍ਰਤੀ ਏਕੜ ਪਾਓ।',
      });
    } finally {
      setLoading(false);
    }
  };

  const speakResult = () => {
    if (!result) return;
    Speech.speak(
      `${result.crop} ਲਈ NPK: ਨਾਈਟ੍ਰੋਜਨ ${result.npk_recommendation.N} ਕਿਲੋ, ਫਾਸਫੋਰਸ ${result.npk_recommendation.P} ਕਿਲੋ, ਪੋਟਾਸ਼ੀਅਮ ${result.npk_recommendation.K} ਕਿਲੋ ਪ੍ਰਤੀ ਏਕੜ।`,
      { language: 'pa-IN' }
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Crop selector */}
      <View style={styles.formCard}>
        <Text style={styles.fieldLabel}>ਫ਼ਸਲ ਚੁਣੋ</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.cropChips}>
            {CROPS.map(c => (
              <TouchableOpacity
                key={c.value}
                style={[styles.cropChip, selectedCrop === c.value && styles.cropChipActive]}
                onPress={() => setSelectedCrop(c.value)}
              >
                <Text style={{ fontSize: 20 }}>{c.emoji}</Text>
                <Text style={[styles.cropChipText, selectedCrop === c.value && styles.cropChipTextActive]}>
                  {c.label_pa}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
        <TouchableOpacity style={styles.submitBtn} onPress={getRecommendation} disabled={loading}>
          {loading
            ? <ActivityIndicator color="#fff" />
            : <Text style={styles.submitText}>🧪 ਖਾਦ ਸਲਾਹ ਲਓ</Text>
          }
        </TouchableOpacity>
      </View>

      {result && (
        <>
          {/* Zone badge */}
          <View style={styles.zoneBadge}>
            <Ionicons name="location" size={14} color={colors.accent} />
            <Text style={styles.zoneText}> ਜ਼ੋਨ: {result.zone?.charAt(0).toUpperCase() + result.zone?.slice(1)}</Text>
          </View>

          {/* NPK card */}
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>🧪 NPK ਸਿਫ਼ਾਰਸ਼</Text>
              <TouchableOpacity onPress={speakResult}>
                <Ionicons name="volume-high" size={20} color={colors.accent} />
              </TouchableOpacity>
            </View>
            <NPKBar label="N (ਨਾਈਟ੍ਰੋਜਨ)" value={result.npk_recommendation.N} max={100} color="#40C974" />
            <NPKBar label="P (ਫਾਸਫੋਰਸ)"   value={result.npk_recommendation.P} max={60}  color="#58A6FF" />
            <NPKBar label="K (ਪੋਟਾਸ਼ੀਅਮ)" value={result.npk_recommendation.K} max={60}  color="#FFA657" />
          </View>

          {/* Schedule */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>📅 ਖਾਦ ਸਮਾਂ-ਸੂਚੀ</Text>
            {result.fertilizer_schedule.map((s: any, i: number) => (
              <View key={i} style={styles.scheduleItem}>
                <View style={styles.scheduleNum}><Text style={styles.scheduleNumText}>{i + 1}</Text></View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.scheduleStage}>{s.stage} — {s.timing}</Text>
                  <Text style={styles.scheduleNote}>{s.note}</Text>
                </View>
              </View>
            ))}
          </View>

          {/* Zinc */}
          {result.zinc_correction && (
            <View style={[styles.card, styles.zincCard]}>
              <Text style={styles.cardTitle}>⚗️ ਜ਼ਿੰਕ ਸੁਧਾਰ</Text>
              <Text style={styles.infoText}>{result.zinc_correction}</Text>
            </View>
          )}

          {/* Stubble alternatives */}
          {result.stubble_alternatives && (
            <View style={[styles.card, styles.stubbleCard]}>
              <Text style={[styles.cardTitle, { color: colors.warning }]}>♻️ ਪਰਾਲੀ ਪ੍ਰਬੰਧਨ</Text>
              {result.stubble_alternatives.map((alt: any, i: number) => (
                <View key={i} style={styles.altItem}>
                  <Text style={styles.altMethod}>{alt.method}</Text>
                  <Text style={styles.altDesc}>{alt.description}</Text>
                  <View style={styles.incentiveBadge}>
                    <Ionicons name="cash" size={12} color={colors.success} />
                    <Text style={styles.incentiveText}> {alt.govt_incentive}</Text>
                  </View>
                </View>
              ))}
            </View>
          )}

          {/* Organic tip */}
          <View style={styles.organicBox}>
            <Text style={styles.organicText}>🌱 {result.organic_tip}</Text>
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },
  content: { padding: spacing.md, paddingBottom: 100 },
  formCard: { backgroundColor: colors.bgCard, borderRadius: radius.lg, padding: spacing.md, marginBottom: spacing.md },
  fieldLabel: { ...typography.label, marginBottom: spacing.sm },
  cropChips: { flexDirection: 'row', gap: spacing.sm },
  cropChip: {
    alignItems: 'center', padding: spacing.sm,
    backgroundColor: colors.bgSurface, borderRadius: radius.md,
    minWidth: 70, borderWidth: 1, borderColor: 'transparent',
  },
  cropChipActive: { borderColor: colors.accent, backgroundColor: colors.primary + '33' },
  cropChipText: { fontSize: 12, color: colors.textSecondary, marginTop: 4 },
  cropChipTextActive: { color: colors.accent, fontWeight: '600' },
  submitBtn: {
    backgroundColor: colors.primaryLighter, borderRadius: radius.lg,
    padding: spacing.md, alignItems: 'center', marginTop: spacing.md,
  },
  submitText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  zoneBadge: {
    flexDirection: 'row', alignItems: 'center',
    marginBottom: spacing.sm,
  },
  zoneText: { color: colors.accent, fontSize: 13, fontWeight: '600' },
  card: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, marginBottom: spacing.md,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md },
  cardTitle: { ...typography.h3, fontSize: 16, marginBottom: spacing.sm },
  npkRow: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.sm },
  npkLabel: { width: 100, fontSize: 12, color: colors.textSecondary },
  npkBarBg: { flex: 1, height: 8, backgroundColor: colors.bgSurface, borderRadius: 4, marginHorizontal: spacing.sm },
  npkBarFill: { height: 8, borderRadius: 4 },
  npkValue: { width: 80, fontSize: 12, color: colors.textPrimary, textAlign: 'right' },
  scheduleItem: {
    flexDirection: 'row', alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  scheduleNum: {
    width: 28, height: 28, borderRadius: 14,
    backgroundColor: colors.primaryLighter, justifyContent: 'center', alignItems: 'center',
    marginRight: spacing.sm,
  },
  scheduleNumText: { color: '#fff', fontWeight: '700', fontSize: 13 },
  scheduleStage: { ...typography.bodyBold, fontSize: 13 },
  scheduleNote: { ...typography.body, fontSize: 12, marginTop: 2 },
  zincCard: { borderColor: '#58A6FF33' },
  infoText: { color: colors.textPrimary, fontSize: 14, lineHeight: 20 },
  stubbleCard: { borderColor: colors.warning + '33', backgroundColor: '#1A1100' },
  altItem: { marginBottom: spacing.md },
  altMethod: { fontWeight: '700', color: colors.warning, fontSize: 14 },
  altDesc: { color: colors.textPrimary, fontSize: 13, marginTop: 2 },
  incentiveBadge: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: colors.success + '22', alignSelf: 'flex-start',
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: radius.full, marginTop: 4,
  },
  incentiveText: { color: colors.success, fontSize: 12 },
  organicBox: {
    backgroundColor: '#0D2818', borderRadius: radius.md,
    padding: spacing.md, borderLeftWidth: 3, borderLeftColor: colors.accent,
  },
  organicText: { color: colors.accentSoft, fontSize: 13 },
});
