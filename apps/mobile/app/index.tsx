import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  Animated, Dimensions, StatusBar,
} from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, typography } from '../src/constants/theme';
import { useAppStore } from '../src/store/appStore';

const { width } = Dimensions.get('window');

const MODULE_CARDS = [
  {
    id: 'crop',
    route: '/crop',
    icon: 'leaf',
    title: 'ਫ਼ਸਲ ਸਲਾਹ',
    subtitle: 'Crop Advisory',
    color: '#40C974',
    bg: '#0D2818',
    description: 'ਆਪਣੀ ਮਿੱਟੀ ਲਈ ਸਹੀ ਫ਼ਸਲ',
  },
  {
    id: 'weather',
    route: '/weather',
    icon: 'partly-sunny',
    title: 'ਮੌਸਮ',
    subtitle: 'Weather & Alerts',
    color: '#58A6FF',
    bg: '#0D1E35',
    description: '7 ਦਿਨਾਂ ਦਾ ਖੇਤੀ ਮੌਸਮ',
  },
  {
    id: 'disease',
    route: '/disease',
    icon: 'camera',
    title: 'ਕੀੜਾ ਪਛਾਣ',
    subtitle: 'Pest Detection',
    color: '#FFA657',
    bg: '#2D1A0D',
    description: 'ਫ਼ੋਟੋ ਖਿੱਚੋ, ਬਿਮਾਰੀ ਜਾਣੋ',
  },
  {
    id: 'soil',
    route: '/soil',
    icon: 'earth',
    title: 'ਮਿੱਟੀ ਖਾਦ',
    subtitle: 'Soil & Fertilizer',
    color: '#7EE787',
    bg: '#0D1F10',
    description: 'NPK ਅਤੇ ਖਾਦ ਸਲਾਹ',
  },
  {
    id: 'market',
    route: '/market',
    icon: 'trending-up',
    title: 'ਮੰਡੀ ਭਾਅ',
    subtitle: 'Market Prices',
    color: '#BC8CFF',
    bg: '#1A0D2E',
    description: 'ਲਾਈਵ ਮੰਡੀ ਅਤੇ MSP ਭਾਅ',
  },
];

function getCurrentSlot(): { active: boolean; label: string } {
  const h = new Date().getHours();
  if ((h >= 5 && h < 8) || (h >= 22)) {
    return { active: true, label: h < 8 ? 'ਸਵੇਰੇ 5–8 ਵਜੇ (ਚਾਲੂ)' : 'ਰਾਤ 10–1 ਵਜੇ (ਚਾਲੂ)' };
  }
  return { active: false, label: 'ਅਗਲਾ ਸਲਾਟ: ਰਾਤ 10 ਵਜੇ' };
}

export default function HomeScreen() {
  const { profile, isOnline } = useAppStore();
  const slot = getCurrentSlot();
  const [fadeAnim] = useState(new Animated.Value(0));

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 600, useNativeDriver: true }).start();
  }, []);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.primary} />
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>

        {/* Header */}
        <Animated.View style={[styles.header, { opacity: fadeAnim }]}>
          <View>
            <Text style={styles.greeting}>ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ 🙏</Text>
            <Text style={styles.district}>📍 {profile.district.charAt(0).toUpperCase() + profile.district.slice(1)}</Text>
          </View>
          <View style={styles.langBadge}>
            <Text style={styles.langText}>{profile.language.toUpperCase()}</Text>
          </View>
        </Animated.View>

        {/* Offline banner */}
        {!isOnline && (
          <View style={styles.offlineBanner}>
            <Ionicons name="cloud-offline" size={16} color={colors.warning} />
            <Text style={styles.offlineText}> ਔਫਲਾਈਨ — ਕੈਸ਼ ਡੇਟਾ</Text>
          </View>
        )}

        {/* Electricity slot card */}
        <View style={[styles.slotCard, slot.active && styles.slotActive]}>
          <Ionicons
            name="flash"
            size={20}
            color={slot.active ? '#FFD700' : colors.textSecondary}
          />
          <View style={{ flex: 1, marginLeft: spacing.sm }}>
            <Text style={[styles.slotTitle, slot.active && { color: '#FFD700' }]}>
              {slot.active ? '⚡ ਬਿਜਲੀ ਸਲਾਟ ਚਾਲੂ — ਹੁਣੇ ਸਿੰਚਾਈ ਕਰੋ!' : '⏰ ਬਿਜਲੀ ਸਲਾਟ'}
            </Text>
            <Text style={styles.slotSub}>{slot.label}</Text>
          </View>
          {slot.active && <View style={styles.slotDot} />}
        </View>

        {/* Module grid */}
        <Text style={styles.sectionTitle}>ਸੇਵਾਵਾਂ</Text>
        <View style={styles.grid}>
          {MODULE_CARDS.map((card, idx) => (
            <Animated.View
              key={card.id}
              style={[
                { opacity: fadeAnim, transform: [{ translateY: fadeAnim.interpolate({ inputRange: [0, 1], outputRange: [20 * (idx + 1), 0] }) }] },
                styles.cardWrapper,
              ]}
            >
              <TouchableOpacity
                style={[styles.card, { backgroundColor: card.bg }]}
                onPress={() => router.push(card.route as any)}
                activeOpacity={0.8}
              >
                <View style={[styles.iconWrap, { backgroundColor: card.color + '22' }]}>
                  <Ionicons name={card.icon as any} size={28} color={card.color} />
                </View>
                <Text style={[styles.cardTitle, { color: card.color }]}>{card.title}</Text>
                <Text style={styles.cardSubtitle}>{card.subtitle}</Text>
                <Text style={styles.cardDesc}>{card.description}</Text>
              </TouchableOpacity>
            </Animated.View>
          ))}
        </View>

        {/* Footer tip */}
        <View style={styles.tipBox}>
          <Text style={styles.tipText}>
            💡 ਸੁਝਾਅ: ਔਫਲਾਈਨ ਵੀ ਕੰਮ ਕਰਦਾ ਹੈ — WiFi ਤੋਂ ਬਿਨਾਂ ਵੀ ਵਰਤੋ।
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },
  scroll: { padding: spacing.md, paddingBottom: 100 },
  header: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: spacing.md,
    paddingTop: spacing.sm,
  },
  greeting: { ...typography.h2, fontSize: 20 },
  district: { ...typography.body, marginTop: 2, color: colors.accent },
  langBadge: {
    backgroundColor: colors.primary, paddingHorizontal: 12,
    paddingVertical: 6, borderRadius: radius.full,
  },
  langText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  offlineBanner: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#2D2500', padding: spacing.sm,
    borderRadius: radius.md, marginBottom: spacing.md,
  },
  offlineText: { color: colors.warning, fontSize: 13 },
  slotCard: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: colors.bgCard, padding: spacing.md,
    borderRadius: radius.lg, marginBottom: spacing.lg,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  slotActive: {
    borderColor: '#FFD70066',
    backgroundColor: '#1A1400',
  },
  slotTitle: { ...typography.bodyBold, fontSize: 14 },
  slotSub: { ...typography.caption, marginTop: 2 },
  slotDot: {
    width: 10, height: 10, borderRadius: 5,
    backgroundColor: '#FFD700',
  },
  sectionTitle: { ...typography.h3, marginBottom: spacing.md },
  grid: {
    flexDirection: 'row', flexWrap: 'wrap',
    justifyContent: 'space-between', gap: spacing.sm,
  },
  cardWrapper: { width: (width - spacing.md * 2 - spacing.sm) / 2 },
  card: {
    borderRadius: radius.lg, padding: spacing.md,
    borderWidth: 1, borderColor: '#ffffff11',
    minHeight: 140,
  },
  iconWrap: {
    width: 48, height: 48, borderRadius: radius.md,
    justifyContent: 'center', alignItems: 'center',
    marginBottom: spacing.sm,
  },
  cardTitle: { fontSize: 16, fontWeight: '700', marginBottom: 2 },
  cardSubtitle: { fontSize: 11, color: colors.textSecondary, marginBottom: 4 },
  cardDesc: { fontSize: 12, color: colors.textMuted, lineHeight: 16 },
  tipBox: {
    marginTop: spacing.lg, padding: spacing.md,
    backgroundColor: '#0D2818', borderRadius: radius.md,
    borderLeftWidth: 3, borderLeftColor: colors.accent,
  },
  tipText: { color: colors.accentSoft, fontSize: 13 },
});
