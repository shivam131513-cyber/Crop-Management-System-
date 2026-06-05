/**
 * NotificationsScreen — In-app notification centre
 * Shows advisory alerts, weather warnings, scheme deadlines, and market tips.
 * Reads notifications from the /notifications/list API and supports
 * mark-as-read, pull-to-refresh, and Punjabi voice readout.
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  RefreshControl, ActivityIndicator, Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, typography } from '../src/constants/theme';
import * as Speech from 'expo-speech';

// ── Types ─────────────────────────────────────────────────────────────────────

interface Notification {
  id: string;
  type: 'weather' | 'pest' | 'scheme' | 'market' | 'advisory' | 'water';
  title: string;
  title_pa: string;
  body: string;
  body_pa: string;
  timestamp: string;
  read: boolean;
  priority: 'high' | 'medium' | 'low';
}

// ── Mock data — replace with API call to /notifications/list ─────────────────

const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: '1', type: 'weather', priority: 'high',
    title: 'Heavy Rain Alert', title_pa: 'ਭਾਰੀ ਮੀਂਹ ਦੀ ਚੇਤਾਵਨੀ',
    body: 'Heavy rainfall expected in your district in the next 24 hours. Postpone any scheduled spraying.',
    body_pa: 'ਅਗਲੇ 24 ਘੰਟਿਆਂ ਵਿੱਚ ਭਾਰੀ ਮੀਂਹ ਆਉਣ ਦੀ ਸੰਭਾਵਨਾ ਹੈ। ਸਪਰੇਅ ਮੁਲਤਵੀ ਕਰੋ।',
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), read: false,
  },
  {
    id: '2', type: 'pest', priority: 'high',
    title: 'Yellow Rust Alert', title_pa: 'ਪੀਲੇ ਰਤੂਏ ਦੀ ਚੇਤਾਵਨੀ',
    body: 'Yellow rust (stripe rust) detected in nearby fields. Scout your wheat crop immediately.',
    body_pa: 'ਨੇੜੇ ਦੇ ਖੇਤਾਂ ਵਿੱਚ ਪੀਲਾ ਰਤੂਆ ਦੇਖਿਆ ਗਿਆ ਹੈ। ਹੁਣੇ ਕਣਕ ਦੀ ਜਾਂਚ ਕਰੋ।',
    timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), read: false,
  },
  {
    id: '3', type: 'scheme', priority: 'medium',
    title: 'PM-KISAN Instalment Due', title_pa: 'PM-KISAN ਕਿਸ਼ਤ ਆਉਣ ਵਾਲੀ ਹੈ',
    body: 'PM-KISAN 16th instalment will be released soon. Ensure your Aadhaar is linked to your bank account.',
    body_pa: 'PM-KISAN ਦੀ 16ਵੀਂ ਕਿਸ਼ਤ ਜਲਦੀ ਆਵੇਗੀ। ਆਧਾਰ ਨਾਲ ਖਾਤਾ ਜੋੜੋ।',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), read: true,
  },
  {
    id: '4', type: 'market', priority: 'medium',
    title: 'Wheat Prices Up 3%', title_pa: 'ਕਣਕ ਭਾਅ 3% ਵਧਿਆ',
    body: 'Wheat prices at Ludhiana mandi increased by ₹67/quintal today. Consider selling if you have stock.',
    body_pa: 'ਲੁਧਿਆਣਾ ਮੰਡੀ ਵਿੱਚ ਕਣਕ ਭਾਅ ₹67/ਕੁਇੰਟਲ ਵਧਿਆ। ਵੇਚਣ ਬਾਰੇ ਸੋਚੋ।',
    timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), read: true,
  },
  {
    id: '5', type: 'water', priority: 'medium',
    title: 'Free Electricity Slot Reminder', title_pa: 'ਮੁਫ਼ਤ ਬਿਜਲੀ ਯਾਦ-ਦਹਾਨੀ',
    body: 'Free tube-well electricity slot tonight: 10:00 PM – 1:00 AM. Irrigate your crops now.',
    body_pa: 'ਅੱਜ ਰਾਤ ਮੁਫ਼ਤ ਟਿਊਬਵੈੱਲ ਬਿਜਲੀ: 10 ਵਜੇ ਰਾਤ – 1 ਵਜੇ। ਹੁਣ ਸਿੰਜਾਈ ਕਰੋ।',
    timestamp: new Date(Date.now() - 18 * 60 * 60 * 1000).toISOString(), read: true,
  },
  {
    id: '6', type: 'advisory', priority: 'low',
    title: 'Sowing Window — Maize', title_pa: 'ਮੱਕੀ ਬਿਜਾਈ ਸਮਾਂ',
    body: 'Optimal maize sowing window begins next week (mid-June). Prepare land and procure certified seed.',
    body_pa: 'ਮੱਕੀ ਦੀ ਬਿਜਾਈ ਦਾ ਸਹੀ ਸਮਾਂ ਅਗਲੇ ਹਫ਼ਤੇ ਤੋਂ ਸ਼ੁਰੂ ਹੁੰਦਾ ਹੈ। ਜ਼ਮੀਨ ਤਿਆਰ ਕਰੋ ਅਤੇ ਪ੍ਰਮਾਣਿਤ ਬੀਜ ਲਓ।',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), read: true,
  },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

const TYPE_META: Record<string, { icon: any; color: string; label: string }> = {
  weather:  { icon: 'partly-sunny', color: '#FFB347', label: 'ਮੌਸਮ' },
  pest:     { icon: 'bug',          color: colors.danger, label: 'ਕੀੜੇ' },
  scheme:   { icon: 'document-text', color: '#7C83FD', label: 'ਸਕੀਮ' },
  market:   { icon: 'trending-up',  color: colors.success, label: 'ਮੰਡੀ' },
  advisory: { icon: 'leaf',         color: colors.accent, label: 'ਸਲਾਹ' },
  water:    { icon: 'water',         color: '#5BC8F5', label: 'ਪਾਣੀ' },
};

const PRIORITY_COLOR: Record<string, string> = {
  high:   colors.danger,
  medium: colors.warning,
  low:    colors.success,
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins} ਮਿੰਟ ਪਹਿਲਾਂ`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} ਘੰਟੇ ਪਹਿਲਾਂ`;
  return `${Math.floor(hrs / 24)} ਦਿਨ ਪਹਿਲਾਂ`;
}

// ── NotifCard ─────────────────────────────────────────────────────────────────

function NotifCard({
  item, onRead,
}: { item: Notification; onRead: (id: string) => void }) {
  const meta = TYPE_META[item.type] ?? TYPE_META.advisory;
  const fadeAnim = useRef(new Animated.Value(item.read ? 1 : 0.95)).current;

  const handlePress = () => {
    if (!item.read) onRead(item.id);
    Animated.timing(fadeAnim, { toValue: 1, duration: 300, useNativeDriver: true }).start();
  };

  const speak = () => {
    Speech.speak(`${item.title_pa}। ${item.body_pa}`, { language: 'pa-IN' });
  };

  return (
    <Animated.View style={{ opacity: fadeAnim }}>
      <TouchableOpacity
        style={[styles.card, !item.read && styles.cardUnread]}
        onPress={handlePress}
        activeOpacity={0.85}
      >
        {/* Unread dot */}
        {!item.read && <View style={styles.unreadDot} />}

        <View style={[styles.iconWrap, { backgroundColor: meta.color + '22' }]}>
          <Ionicons name={meta.icon} size={22} color={meta.color} />
        </View>

        <View style={styles.cardBody}>
          <View style={styles.cardRow}>
            <Text style={styles.cardTitle} numberOfLines={1}>{item.title_pa}</Text>
            <View style={[styles.priorityDot, { backgroundColor: PRIORITY_COLOR[item.priority] }]} />
          </View>
          <Text style={styles.cardBodyText} numberOfLines={2}>{item.body_pa}</Text>
          <View style={styles.cardFooter}>
            <Text style={styles.cardTime}>{timeAgo(item.timestamp)}</Text>
            <TouchableOpacity onPress={speak} style={styles.speakBtn}>
              <Ionicons name="volume-medium" size={14} color={colors.accent} />
            </TouchableOpacity>
          </View>
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

// ── Screen ────────────────────────────────────────────────────────────────────

export default function NotificationsScreen() {
  const [notifs, setNotifs] = useState<Notification[]>(MOCK_NOTIFICATIONS);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  const unreadCount = notifs.filter(n => !n.read).length;

  const load = useCallback(async () => {
    setLoading(true);
    // TODO: replace with real API call
    await new Promise(r => setTimeout(r, 500));
    setNotifs([...MOCK_NOTIFICATIONS]);
    setLoading(false);
    setRefreshing(false);
  }, []);

  useEffect(() => { load(); }, []);

  const markRead = (id: string) => {
    setNotifs(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const markAllRead = () => {
    setNotifs(prev => prev.map(n => ({ ...n, read: true })));
  };

  const filtered = filter === 'all' ? notifs : notifs.filter(n => n.type === filter);
  const filterTypes = ['all', 'weather', 'pest', 'scheme', 'market', 'advisory', 'water'];
  const filterLabels: Record<string, string> = {
    all: 'ਸਭ', ...Object.fromEntries(filterTypes.slice(1).map(t => [t, TYPE_META[t].label])),
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>🔔 ਸੂਚਨਾਵਾਂ</Text>
          {unreadCount > 0 && (
            <Text style={styles.headerSub}>{unreadCount} ਨਵੀਆਂ ਸੂਚਨਾਵਾਂ</Text>
          )}
        </View>
        {unreadCount > 0 && (
          <TouchableOpacity onPress={markAllRead} style={styles.markAllBtn}>
            <Text style={styles.markAllText}>ਸਭ ਪੜ੍ਹੀਆਂ</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Filter chips */}
      <FlatList
        horizontal
        data={filterTypes}
        keyExtractor={i => i}
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.filterList}
        renderItem={({ item: f }) => (
          <TouchableOpacity
            style={[styles.filterChip, f === filter && styles.filterChipActive]}
            onPress={() => setFilter(f)}
          >
            {f !== 'all' && (
              <Ionicons
                name={TYPE_META[f]?.icon}
                size={12}
                color={f === filter ? colors.accent : colors.textSecondary}
              />
            )}
            <Text style={[styles.filterChipText, f === filter && styles.filterChipTextActive]}>
              {' '}{filterLabels[f]}
            </Text>
          </TouchableOpacity>
        )}
      />

      {/* List */}
      {loading ? (
        <ActivityIndicator size="large" color={colors.accent} style={{ marginTop: 60 }} />
      ) : (
        <FlatList
          data={filtered}
          keyExtractor={n => n.id}
          contentContainerStyle={styles.list}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} tintColor={colors.accent} />}
          renderItem={({ item }) => <NotifCard item={item} onRead={markRead} />}
          ListEmptyComponent={
            <View style={styles.empty}>
              <Text style={{ fontSize: 48 }}>🔕</Text>
              <Text style={styles.emptyText}>ਕੋਈ ਸੂਚਨਾ ਨਹੀਂ</Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: spacing.md, paddingTop: spacing.md, paddingBottom: spacing.sm,
  },
  headerTitle: { ...typography.h2 },
  headerSub: { fontSize: 12, color: colors.accent, marginTop: 2 },
  markAllBtn: {
    backgroundColor: colors.accent + '22', borderRadius: radius.full,
    paddingHorizontal: 12, paddingVertical: 6,
  },
  markAllText: { fontSize: 12, color: colors.accent, fontWeight: '600' },
  filterList: { paddingHorizontal: spacing.md, paddingBottom: spacing.sm, gap: spacing.sm },
  filterChip: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 12, paddingVertical: 6,
    backgroundColor: colors.bgCard, borderRadius: radius.full,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  filterChipActive: { borderColor: colors.accent, backgroundColor: colors.accent + '18' },
  filterChipText: { fontSize: 12, color: colors.textSecondary },
  filterChipTextActive: { color: colors.accent, fontWeight: '600' },
  list: { padding: spacing.md, gap: spacing.sm, paddingBottom: 100 },
  card: {
    flexDirection: 'row', alignItems: 'flex-start',
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, borderWidth: 1, borderColor: colors.bgSurface,
    gap: spacing.sm, position: 'relative',
  },
  cardUnread: { borderColor: colors.accent + '50', backgroundColor: colors.bgCard },
  unreadDot: {
    position: 'absolute', top: 14, left: 14,
    width: 8, height: 8, borderRadius: 4,
    backgroundColor: colors.accent,
  },
  iconWrap: {
    width: 44, height: 44, borderRadius: radius.md,
    justifyContent: 'center', alignItems: 'center',
  },
  cardBody: { flex: 1 },
  cardRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 },
  cardTitle: { fontSize: 14, fontWeight: '700', color: colors.textPrimary, flex: 1 },
  priorityDot: { width: 8, height: 8, borderRadius: 4, marginLeft: 8 },
  cardBodyText: { fontSize: 13, color: colors.textSecondary, lineHeight: 18 },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 },
  cardTime: { fontSize: 11, color: colors.textMuted },
  speakBtn: { padding: 4 },
  empty: { alignItems: 'center', paddingVertical: 80 },
  emptyText: { ...typography.h3, color: colors.textSecondary, marginTop: spacing.md },
});
