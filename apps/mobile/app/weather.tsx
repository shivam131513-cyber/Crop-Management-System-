import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, ActivityIndicator,
  RefreshControl, TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, typography } from '../src/constants/theme';
import { weatherApi } from '../src/services/api';
import { useAppStore } from '../src/store/appStore';
import * as Speech from 'expo-speech';

const ALERT_ICONS: Record<string, { icon: string; color: string }> = {
  irrigation: { icon: 'water',       color: '#58A6FF' },
  frost:       { icon: 'snow',        color: '#A5D8FF' },
  heatwave:    { icon: 'sunny',       color: '#F85149' },
  pest_risk:   { icon: 'bug',         color: '#FFA657' },
};

const SEVERITY_COLORS: Record<string, string> = {
  high: colors.danger, medium: colors.warning, info: colors.info, none: colors.success,
};

function AlertCard({ alert }: { alert: any }) {
  const cfg = ALERT_ICONS[alert.type] || { icon: 'alert-circle', color: colors.warning };
  const borderColor = SEVERITY_COLORS[alert.severity] || colors.info;

  return (
    <View style={[styles.alertCard, { borderLeftColor: borderColor }]}>
      <Ionicons name={cfg.icon as any} size={20} color={cfg.color} style={{ marginRight: spacing.sm }} />
      <View style={{ flex: 1 }}>
        <Text style={[styles.alertTitle, { color: cfg.color }]}>
          {alert.type === 'irrigation' ? '⚡ ਸਿੰਚਾਈ ਵਿੰਡੋ' :
           alert.type === 'frost' ? '❄️ ਠੰਡ ਚੇਤਾਵਨੀ' :
           alert.type === 'heatwave' ? '🌡️ ਲੂ ਚੇਤਾਵਨੀ' : '🐛 ਕੀੜਾ ਖ਼ਤਰਾ'}
        </Text>
        <Text style={styles.alertMsg}>{alert.message_pa || alert.message}</Text>
      </View>
    </View>
  );
}

function WeatherCard({ item }: { item: any }) {
  const icon = item.weather?.[0]?.icon;
  const date = new Date(item.dt_txt);
  const day = date.toLocaleDateString('pa-IN', { weekday: 'short', day: 'numeric' });

  return (
    <View style={styles.weatherCard}>
      <Text style={styles.wDay}>{day}</Text>
      {icon && (
        // eslint-disable-next-line @typescript-eslint/no-require-imports
        <Text style={{ fontSize: 24 }}>
          {icon.includes('01') ? '☀️' : icon.includes('02') ? '⛅' : icon.includes('09') || icon.includes('10') ? '🌧️' : icon.includes('13') ? '❄️' : '☁️'}
        </Text>
      )}
      <Text style={styles.wMax}>{Math.round(item.main?.temp_max || 0)}°</Text>
      <Text style={styles.wMin}>{Math.round(item.main?.temp_min || 0)}°</Text>
      <Text style={styles.wHum}>💧{item.main?.humidity}%</Text>
    </View>
  );
}

function CurrentConditions({ current }: { current: any }) {
  if (!current) return null;
  const temp = Math.round(current.temp ?? 0);
  const feelsLike = Math.round(current.feels_like ?? 0);
  const humidity = current.humidity ?? '--';
  const wind = current.wind_speed ?? '--';
  const desc = current.weather?.[0]?.description ?? '';
  const sunrise = current.sunrise
    ? new Date(current.sunrise * 1000).toLocaleTimeString('pa-IN', { hour: '2-digit', minute: '2-digit' })
    : '--';
  const sunset = current.sunset
    ? new Date(current.sunset * 1000).toLocaleTimeString('pa-IN', { hour: '2-digit', minute: '2-digit' })
    : '--';

  return (
    <View style={styles.currentCard}>
      <View style={styles.currentMain}>
        <Text style={styles.currentTemp}>{temp}°C</Text>
        <View>
          <Text style={styles.currentDesc}>{desc}</Text>
          <Text style={styles.currentFeels}>ਮਹਿਸੂਸ: {feelsLike}°C</Text>
        </View>
      </View>
      <View style={styles.currentGrid}>
        <View style={styles.currentStat}>
          <Ionicons name="water" size={16} color="#58A6FF" />
          <Text style={styles.currentStatLabel}>ਨਮੀ</Text>
          <Text style={styles.currentStatValue}>{humidity}%</Text>
        </View>
        <View style={styles.currentStat}>
          <Ionicons name="speedometer" size={16} color="#FFA657" />
          <Text style={styles.currentStatLabel}>ਹਵਾ</Text>
          <Text style={styles.currentStatValue}>{wind} km/h</Text>
        </View>
        <View style={styles.currentStat}>
          <Text style={{ fontSize: 16 }}>🌅</Text>
          <Text style={styles.currentStatLabel}>ਸੂਰਜ ਚੜ੍ਹਾਈ</Text>
          <Text style={styles.currentStatValue}>{sunrise}</Text>
        </View>
        <View style={styles.currentStat}>
          <Text style={{ fontSize: 16 }}>🌇</Text>
          <Text style={styles.currentStatLabel}>ਸੂਰਜ ਡੁੱਬ</Text>
          <Text style={styles.currentStatValue}>{sunset}</Text>
        </View>
      </View>
    </View>
  );
}

export default function WeatherScreen() {
  const { profile } = useAppStore();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const resp = await weatherApi.getForecast(profile.district);
      setData(resp.data);
    } catch (_) {
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);

  const speakAlerts = () => {
    if (!data?.alerts?.length) return;
    const text = data.alerts.map((a: any) => a.message_pa || a.message).join('। ');
    Speech.speak(text, { language: 'pa-IN' });
  };

  if (loading) return (
    <View style={styles.centered}>
      <ActivityIndicator size="large" color={colors.accent} />
    </View>
  );

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} tintColor={colors.accent} />}
    >
      {/* District header */}
      <View style={styles.districtRow}>
        <Ionicons name="location" size={16} color={colors.accent} />
        <Text style={styles.districtText}> {profile.district.charAt(0).toUpperCase() + profile.district.slice(1)}, ਪੰਜਾਬ</Text>
        {data?._fromCache && (
          <View style={styles.cacheBadge}><Text style={styles.cacheText}>📶 ਕੈਸ਼</Text></View>
        )}
      </View>

      {/* Alerts section */}
      {data?.alerts?.length > 0 && (
        <View style={styles.alertsSection}>
          <View style={styles.sectionRow}>
            <Text style={styles.sectionTitle}>⚠️ ਖੇਤੀ ਚੇਤਾਵਨੀਆਂ</Text>
            <TouchableOpacity onPress={speakAlerts}>
              <Ionicons name="volume-high" size={20} color={colors.accent} />
            </TouchableOpacity>
          </View>
          {data.alerts.map((a: any, i: number) => <AlertCard key={i} alert={a} />)}
        </View>
      )}

      {/* Irrigation slots */}
      {data?.irrigation_slots && (
        <View style={styles.slotBlock}>
          <Text style={styles.sectionTitle}>⚡ ਮੁਫ਼ਤ ਬਿਜਲੀ ਸਿੰਚਾਈ ਸਲਾਟ</Text>
          <View style={styles.slotRow}>
            {data.irrigation_slots.map((s: any, i: number) => (
              <View key={i} style={styles.slotChip}>
                <Ionicons name="flash" size={14} color="#FFD700" />
                <Text style={styles.slotChipText}>{s.label}: {s.start}–{s.end}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Current conditions */}
      <CurrentConditions current={data?.current} />

      {/* 7-day forecast */}
      <Text style={styles.sectionTitle}>📅 7 ਦਿਨਾਂ ਦਾ ਪੂਰਵਅਨੁਮਾਨ</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.forecastScroll}>
        {(data?.forecast || []).filter((_: any, i: number) => i % 2 === 0).map((item: any, i: number) => (
          <WeatherCard key={i} item={item} />
        ))}
      </ScrollView>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },
  content: { padding: spacing.md, paddingBottom: 100 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.bgDark },
  districtRow: {
    flexDirection: 'row', alignItems: 'center',
    marginBottom: spacing.md,
  },
  districtText: { ...typography.bodyBold, flex: 1 },
  cacheBadge: {
    backgroundColor: colors.bgSurface, borderRadius: radius.sm,
    paddingHorizontal: 8, paddingVertical: 3,
  },
  cacheText: { fontSize: 11, color: colors.textSecondary },
  alertsSection: { marginBottom: spacing.md },
  sectionRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: spacing.sm,
  },
  sectionTitle: { ...typography.h3, marginBottom: spacing.sm },
  alertCard: {
    flexDirection: 'row', alignItems: 'flex-start',
    backgroundColor: colors.bgCard, borderRadius: radius.md,
    padding: spacing.md, marginBottom: spacing.sm,
    borderLeftWidth: 3,
  },
  alertTitle: { fontWeight: '700', fontSize: 14, marginBottom: 4 },
  alertMsg: { color: colors.textSecondary, fontSize: 13, lineHeight: 18 },
  slotBlock: { marginBottom: spacing.lg },
  slotRow: { flexDirection: 'row', gap: spacing.sm },
  slotChip: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#1A1400', paddingHorizontal: 12, paddingVertical: 8,
    borderRadius: radius.full, borderWidth: 1, borderColor: '#FFD70033',
  },
  slotChipText: { color: '#FFD700', fontSize: 12, marginLeft: 4, fontWeight: '600' },
  forecastScroll: { marginBottom: spacing.lg },
  weatherCard: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, marginRight: spacing.sm,
    alignItems: 'center', minWidth: 80,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  wDay: { fontSize: 11, color: colors.textSecondary, marginBottom: 6 },
  wMax: { fontSize: 20, fontWeight: '700', color: colors.textPrimary },
  wMin: { fontSize: 14, color: colors.textSecondary },
  wHum: { fontSize: 11, color: colors.info, marginTop: 4 },
  currentCard: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, marginBottom: spacing.md,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  currentMain: { flexDirection: 'row', alignItems: 'center', gap: spacing.md, marginBottom: spacing.md },
  currentTemp: { fontSize: 56, fontWeight: '800', color: colors.textPrimary },
  currentDesc: { fontSize: 14, color: colors.textSecondary, textTransform: 'capitalize' },
  currentFeels: { fontSize: 12, color: colors.textMuted, marginTop: 4 },
  currentGrid: { flexDirection: 'row', justifyContent: 'space-around' },
  currentStat: { alignItems: 'center', gap: 4 },
  currentStatLabel: { fontSize: 10, color: colors.textMuted },
  currentStatValue: { fontSize: 13, fontWeight: '700', color: colors.textPrimary },
});
