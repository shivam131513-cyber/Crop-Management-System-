import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, typography } from '../src/constants/theme';
import { marketApi } from '../src/services/api';
import { useAppStore } from '../src/store/appStore';
import * as Speech from 'expo-speech';

const DISTRICTS = ['ludhiana', 'amritsar', 'bathinda', 'jalandhar', 'patiala'];

function SparkLine({ history }: { history: Array<{ date: string; price: number }> }) {
  if (!history?.length) return null;
  const min = Math.min(...history.map(h => h.price));
  const max = Math.max(...history.map(h => h.price));
  const range = max - min || 1;

  return (
    <View style={styles.spark}>
      {history.map((h, i) => {
        const heightPct = ((h.price - min) / range) * 30 + 4;
        const isLast = i === history.length - 1;
        return (
          <View
            key={i}
            style={[
              styles.sparkBar,
              { height: heightPct, backgroundColor: isLast ? colors.accent : colors.primaryLight },
            ]}
          />
        );
      })}
    </View>
  );
}

function PriceCard({ item }: { item: any }) {
  const aboveMsp = item.above_msp;
  const trendUp = item.trend?.startsWith('+');
  const trendDown = item.trend?.startsWith('-');

  const speak = () => {
    Speech.speak(
      `${item.crop_pa}। ਭਾਅ ₹${item.price_per_quintal} ਪ੍ਰਤੀ ਕੁਇੰਟਲ। ${aboveMsp ? 'MSP ਤੋਂ ਉੱਪਰ।' : 'MSP ਤੋਂ ਹੇਠਾਂ।'}`,
      { language: 'pa-IN' }
    );
  };

  return (
    <View style={styles.priceCard}>
      <View style={styles.priceHeader}>
        <View style={{ flex: 1 }}>
          <Text style={styles.cropPa}>{item.crop_pa}</Text>
          <Text style={styles.cropEn}>{item.crop}</Text>
          <Text style={styles.mandiText}>📍 {item.mandi}</Text>
        </View>
        <View style={{ alignItems: 'flex-end' }}>
          <Text style={styles.price}>₹{item.price_per_quintal.toLocaleString()}</Text>
          <Text style={styles.priceUnit}>ਪ੍ਰਤੀ ਕੁਇੰਟਲ</Text>
          <TouchableOpacity onPress={speak} style={{ marginTop: 4 }}>
            <Ionicons name="volume-high" size={16} color={colors.accent} />
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.priceFooter}>
        {/* MSP comparison */}
        {item.msp_per_quintal != null && (
          <View style={[styles.mspBadge, { backgroundColor: aboveMsp ? colors.success + '22' : colors.danger + '22' }]}>
            <Ionicons
              name={aboveMsp ? 'checkmark-circle' : 'alert-circle'}
              size={12}
              color={aboveMsp ? colors.success : colors.danger}
            />
            <Text style={[styles.mspText, { color: aboveMsp ? colors.success : colors.danger }]}>
              {' '}MSP ₹{item.msp_per_quintal} {aboveMsp ? '✓' : '✗'}
            </Text>
          </View>
        )}

        {/* Trend */}
        <View style={[styles.trendBadge, {
          backgroundColor: trendUp ? colors.success + '22' : trendDown ? colors.danger + '22' : colors.bgSurface
        }]}>
          <Ionicons
            name={trendUp ? 'trending-up' : trendDown ? 'trending-down' : 'remove'}
            size={12}
            color={trendUp ? colors.success : trendDown ? colors.danger : colors.textSecondary}
          />
          <Text style={[styles.trendText, {
            color: trendUp ? colors.success : trendDown ? colors.danger : colors.textSecondary
          }]}>
            {' '}{item.trend}
          </Text>
        </View>

        {/* Sparkline */}
        <SparkLine history={item.price_history} />
      </View>
    </View>
  );
}

export default function MarketScreen() {
  const { profile } = useAppStore();
  const [district, setDistrict] = useState(profile.district);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState<any>(null);

  const load = async () => {
    setLoading(true);
    try {
      const resp = await marketApi.getPrices(district);
      setData(resp.data);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, [district]);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} tintColor={colors.accent} />}
    >
      {/* District chips */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: spacing.md }}>
        <View style={{ flexDirection: 'row', gap: spacing.sm }}>
          {DISTRICTS.map(d => (
            <TouchableOpacity
              key={d}
              style={[styles.distChip, d === district && styles.distChipActive]}
              onPress={() => setDistrict(d)}
            >
              <Text style={[styles.distChipText, d === district && styles.distChipTextActive]}>
                {d.charAt(0).toUpperCase() + d.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>

      {/* Loading */}
      {loading && (
        <View style={styles.centered}>
          <ActivityIndicator size="large" color={colors.accent} />
        </View>
      )}

      {/* Last updated */}
      {data && (
        <Text style={styles.lastUpdated}>
          🕐 {new Date(data.last_updated).toLocaleTimeString('pa-IN')} • {data.source}
        </Text>
      )}

      {/* Price cards */}
      {data?.prices?.map((p: any, i: number) => (
        <PriceCard key={i} item={p} />
      ))}

      {/* Empty state */}
      {!loading && (!data?.prices?.length) && (
        <View style={styles.empty}>
          <Text style={{ fontSize: 48 }}>📊</Text>
          <Text style={styles.emptyText}>ਕੋਈ ਡੇਟਾ ਨਹੀਂ</Text>
        </View>
      )}

      {/* MSP info box */}
      <View style={styles.mspInfoBox}>
        <Text style={styles.mspInfoTitle}>ℹ️ MSP ਬਾਰੇ</Text>
        <Text style={styles.mspInfoText}>
          MSP (Minimum Support Price) ਉਹ ਘੱਟੋ-ਘੱਟ ਭਾਅ ਹੈ ਜੋ ਸਰਕਾਰ ਤੁਹਾਡੀ ਫ਼ਸਲ ਲਈ ਦਿੰਦੀ ਹੈ।
          ਜੇ ਮੰਡੀ ਭਾਅ MSP ਤੋਂ ਘੱਟ ਹੈ, ਤਾਂ ਸਰਕਾਰੀ ਖ਼ਰੀਦ ਕੇਂਦਰ ਵਿੱਚ ਵੇਚੋ।
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },
  content: { padding: spacing.md, paddingBottom: 100 },
  centered: { paddingVertical: 60, alignItems: 'center' },
  distChip: {
    paddingHorizontal: 14, paddingVertical: 8,
    backgroundColor: colors.bgCard, borderRadius: radius.full,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  distChipActive: { backgroundColor: colors.primary + '44', borderColor: colors.accent },
  distChipText: { color: colors.textSecondary, fontSize: 13 },
  distChipTextActive: { color: colors.accent, fontWeight: '600' },
  lastUpdated: { fontSize: 11, color: colors.textMuted, marginBottom: spacing.sm },
  priceCard: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, marginBottom: spacing.md,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  priceHeader: { flexDirection: 'row', marginBottom: spacing.sm },
  cropPa: { fontSize: 20, fontWeight: '700', color: colors.textPrimary },
  cropEn: { fontSize: 12, color: colors.textSecondary },
  mandiText: { fontSize: 11, color: colors.textMuted, marginTop: 2 },
  price: { fontSize: 24, fontWeight: '700', color: colors.accent },
  priceUnit: { fontSize: 11, color: colors.textSecondary },
  priceFooter: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, flexWrap: 'wrap' },
  mspBadge: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: radius.full,
  },
  mspText: { fontSize: 11, fontWeight: '600' },
  trendBadge: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: radius.full,
  },
  trendText: { fontSize: 11, fontWeight: '600' },
  spark: { flex: 1, flexDirection: 'row', alignItems: 'flex-end', height: 36, gap: 2 },
  sparkBar: { flex: 1, borderRadius: 2 },
  empty: { alignItems: 'center', paddingVertical: 60 },
  emptyText: { ...typography.h3, marginTop: spacing.md, color: colors.textSecondary },
  mspInfoBox: {
    backgroundColor: '#0D1E35', borderRadius: radius.md,
    padding: spacing.md, borderLeftWidth: 3, borderLeftColor: colors.info,
    marginTop: spacing.sm,
  },
  mspInfoTitle: { color: colors.info, fontWeight: '700', marginBottom: 6 },
  mspInfoText: { color: colors.textSecondary, fontSize: 13, lineHeight: 20 },
});
