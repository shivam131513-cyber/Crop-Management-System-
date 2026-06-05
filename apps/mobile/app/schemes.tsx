/**
 * SchemesScreen — Government Agricultural Schemes
 * Shows eligible central and Punjab state schemes for farmers
 * with benefit details, eligibility criteria, application process,
 * and helpline numbers in Punjabi/Hindi/English.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  Linking, ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, typography } from '../src/constants/theme';
import * as Speech from 'expo-speech';

// ── Data ──────────────────────────────────────────────────────────────────────

interface Scheme {
  id: string;
  category: 'central' | 'state';
  name: string;
  name_pa: string;
  benefit: string;
  benefit_pa: string;
  eligibility: string[];
  eligibility_pa: string[];
  howToApply: string;
  howToApply_pa: string;
  deadline?: string;
  helpline?: string;
  url?: string;
  icon: string;
  color: string;
}

const SCHEMES: Scheme[] = [
  {
    id: 'pmkisan',
    category: 'central',
    name: 'PM-KISAN',
    name_pa: 'ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਕਿਸਾਨ ਸਮਮਾਨ ਨਿਧੀ',
    benefit: '₹6,000/year in 3 instalments of ₹2,000 directly to bank account.',
    benefit_pa: 'ਸਾਲਾਨਾ ₹6,000 — ਤਿੰਨ ₹2,000 ਦੀਆਂ ਕਿਸ਼ਤਾਂ ਵਿੱਚ ਸਿੱਧਾ ਖਾਤੇ ਵਿੱਚ।',
    eligibility: ['Small/marginal farmers with cultivable land', 'Aadhaar-linked bank account required'],
    eligibility_pa: ['ਛੋਟੇ/ਸੀਮਾਂਤ ਕਿਸਾਨ', 'ਆਧਾਰ ਨਾਲ ਜੋੜਿਆ ਬੈਂਕ ਖਾਤਾ ਜ਼ਰੂਰੀ'],
    howToApply: 'Register at pmkisan.gov.in or visit Common Service Centre (CSC).',
    howToApply_pa: 'pmkisan.gov.in ਤੇ ਰਜਿਸਟਰ ਕਰੋ ਜਾਂ CSC ਕੇਂਦਰ ਜਾਓ।',
    helpline: '155261',
    url: 'https://pmkisan.gov.in',
    icon: 'cash', color: '#4CAF50',
  },
  {
    id: 'fasal_bima',
    category: 'central',
    name: 'PM Fasal Bima Yojana',
    name_pa: 'ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਫ਼ਸਲ ਬੀਮਾ ਯੋਜਨਾ',
    benefit: 'Crop insurance: 1.5% premium for Rabi, 2% for Kharif, 5% for horticulture.',
    benefit_pa: 'ਫ਼ਸਲ ਬੀਮਾ: ਰਬੀ ਲਈ 1.5%, ਖ਼ਰੀਫ਼ ਲਈ 2%, ਬਾਗ਼ਬਾਨੀ ਲਈ 5% ਪ੍ਰੀਮੀਅਮ।',
    eligibility: ['All farmers growing notified crops', 'KCC loan farmers — auto enrolled'],
    eligibility_pa: ['ਸਾਰੇ ਕਿਸਾਨ ਜੋ ਸੂਚਿਤ ਫ਼ਸਲਾਂ ਉਗਾਉਂਦੇ ਹਨ', 'KCC ਕਰਜ਼ਾ ਧਾਰਕ — ਆਪਣੇ ਆਪ ਦਾਖਲ'],
    howToApply: 'Apply through bank/KCC at time of crop loan or via pmfby.gov.in.',
    howToApply_pa: 'ਬੈਂਕ/KCC ਰਾਹੀਂ ਅਰਜ਼ੀ ਦਿਓ ਜਾਂ pmfby.gov.in ਤੇ।',
    deadline: 'Enroll before sowing season ends',
    helpline: '1800-200-7710',
    url: 'https://pmfby.gov.in',
    icon: 'shield-checkmark', color: '#2196F3',
  },
  {
    id: 'kcc',
    category: 'central',
    name: 'Kisan Credit Card (KCC)',
    name_pa: 'ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ',
    benefit: 'Revolving credit up to ₹3 lakh at 4% interest (after 2% govt subsidy).',
    benefit_pa: '₹3 ਲੱਖ ਤੱਕ ਕ੍ਰੈਡਿਟ ਸਿਰਫ਼ 4% ਵਿਆਜ ਦਰ ਤੇ।',
    eligibility: ['All farmers, sharecroppers, tenant farmers', 'Minimum 1 acre cultivable land'],
    eligibility_pa: ['ਸਾਰੇ ਕਿਸਾਨ, ਬਟਾਈਦਾਰ, ਠੇਕੇ ਤੇ ਖੇਤੀ ਕਰਨ ਵਾਲੇ', 'ਘੱਟੋ-ਘੱਟ 1 ਏਕੜ ਜ਼ਮੀਨ'],
    howToApply: 'Apply at nearest nationalized bank or cooperative society with land documents.',
    howToApply_pa: 'ਨਜ਼ਦੀਕੀ ਰਾਸ਼ਟਰੀਕ੍ਰਿਤ ਬੈਂਕ ਜਾਂ ਸਹਿਕਾਰੀ ਸਭਾ ਵਿੱਚ ਜ਼ਮੀਨ ਦੇ ਦਸਤਾਵੇਜ਼ਾਂ ਨਾਲ ਜਾਓ।',
    helpline: '1800-1800-110',
    icon: 'card', color: '#FF9800',
  },
  {
    id: 'stubble_ppcb',
    category: 'state',
    name: 'Punjab Stubble Management Scheme',
    name_pa: 'ਪੰਜਾਬ ਪਰਾਲੀ ਪ੍ਰਬੰਧਨ ਸਕੀਮ',
    benefit: '₹2,500/acre incentive for not burning paddy stubble. Free Happy Seeder rental.',
    benefit_pa: 'ਪਰਾਲੀ ਨਾ ਸਾੜਨ ਤੇ ₹2,500/ਏਕੜ। ਮੁਫ਼ਤ ਹੈਪੀ ਸੀਡਰ ਕਿਰਾਏ ਤੇ।',
    eligibility: ['Punjab farmers with paddy fields', 'Must use alternative methods (Happy Seeder / bio-decomposer)'],
    eligibility_pa: ['ਝੋਨੇ ਵਾਲੇ ਪੰਜਾਬੀ ਕਿਸਾਨ', 'ਬਦਲਵੇਂ ਤਰੀਕੇ ਵਰਤਣੇ ਜ਼ਰੂਰੀ'],
    howToApply: 'Register at agripb.gov.in or contact Agriculture Block Officer.',
    howToApply_pa: 'agripb.gov.in ਤੇ ਰਜਿਸਟਰ ਕਰੋ ਜਾਂ ਬਲਾਕ ਖੇਤੀਬਾੜੀ ਅਫ਼ਸਰ ਨੂੰ ਮਿਲੋ।',
    deadline: 'Oct – Nov (Kharif harvest season)',
    helpline: '1800-180-1551',
    icon: 'leaf', color: '#8BC34A',
  },
  {
    id: 'crop_diversification',
    category: 'state',
    name: 'Punjab Crop Diversification Scheme',
    name_pa: 'ਪੰਜਾਬ ਫ਼ਸਲ ਵਿਭਿੰਨਤਾ ਸਕੀਮ',
    benefit: '₹17,500/acre incentive for switching from paddy to maize, moong, or vegetables.',
    benefit_pa: 'ਝੋਨੇ ਤੋਂ ਮੱਕੀ, ਮੂੰਗੀ ਜਾਂ ਸਬਜ਼ੀਆਂ ਵੱਲ ਜਾਣ ਤੇ ₹17,500/ਏਕੜ।',
    eligibility: ['Punjab farmers willing to shift from paddy cultivation', 'Minimum 1 acre land'],
    eligibility_pa: ['ਝੋਨੇ ਤੋਂ ਹਟਣ ਲਈ ਤਿਆਰ ਕਿਸਾਨ', 'ਘੱਟੋ-ਘੱਟ 1 ਏਕੜ'],
    howToApply: 'Apply through Agriculture Department before sowing alternate crop.',
    howToApply_pa: 'ਬਦਲਵੀਂ ਫ਼ਸਲ ਬੀਜਣ ਤੋਂ ਪਹਿਲਾਂ ਖੇਤੀਬਾੜੀ ਵਿਭਾਗ ਵਿੱਚ ਅਰਜ਼ੀ ਦਿਓ।',
    deadline: 'Before Kharif sowing (June)',
    helpline: '1800-180-1551',
    icon: 'swap-horizontal', color: '#9C27B0',
  },
  {
    id: 'solar_pump',
    category: 'central',
    name: 'PM-KUSUM (Solar Pump)',
    name_pa: 'PM-KUSUM ਸੋਲਰ ਪੰਪ',
    benefit: '60% subsidy on solar-powered irrigation pumps (up to 7.5 HP).',
    benefit_pa: 'ਸੋਲਰ ਸਿੰਚਾਈ ਪੰਪਾਂ ਤੇ 60% ਸਬਸਿਡੀ (7.5 HP ਤੱਕ)।',
    eligibility: ['Individual farmers with tube-well or bore-well', 'Land holding minimum 0.5 acre'],
    eligibility_pa: ['ਟਿਊਬਵੈੱਲ/ਬੋਰਵੈੱਲ ਵਾਲੇ ਕਿਸਾਨ', 'ਘੱਟੋ-ਘੱਟ 0.5 ਏਕੜ ਜ਼ਮੀਨ'],
    howToApply: 'Apply at mnre.gov.in or PEDA (Punjab Energy Development Agency).',
    howToApply_pa: 'mnre.gov.in ਜਾਂ PEDA ਤੇ ਅਰਜ਼ੀ ਦਿਓ।',
    helpline: '1800-180-3333',
    url: 'https://mnre.gov.in',
    icon: 'sunny', color: '#FFC107',
  },
];

// ── SchemeCard ────────────────────────────────────────────────────────────────

function SchemeCard({ scheme }: { scheme: Scheme }) {
  const [expanded, setExpanded] = useState(false);

  const speak = () => {
    Speech.speak(
      `${scheme.name_pa}। ਫ਼ਾਇਦਾ: ${scheme.benefit_pa}। ਅਰਜ਼ੀ: ${scheme.howToApply_pa}`,
      { language: 'pa-IN' },
    );
  };

  return (
    <View style={styles.card}>
      <TouchableOpacity onPress={() => setExpanded(!expanded)} activeOpacity={0.85}>
        <View style={styles.cardHeader}>
          <View style={[styles.iconWrap, { backgroundColor: scheme.color + '22' }]}>
            <Ionicons name={scheme.icon as any} size={22} color={scheme.color} />
          </View>
          <View style={styles.cardInfo}>
            <View style={styles.cardTitleRow}>
              <Text style={styles.cardName} numberOfLines={1}>{scheme.name_pa}</Text>
              <View style={[styles.catBadge, { backgroundColor: scheme.category === 'central' ? '#2196F344' : '#9C27B044' }]}>
                <Text style={[styles.catText, { color: scheme.category === 'central' ? '#2196F3' : '#9C27B0' }]}>
                  {scheme.category === 'central' ? 'ਕੇਂਦਰੀ' : 'ਰਾਜ'}
                </Text>
              </View>
            </View>
            <Text style={styles.cardBenefit} numberOfLines={expanded ? undefined : 2}>
              {scheme.benefit_pa}
            </Text>
          </View>
          <Ionicons
            name={expanded ? 'chevron-up' : 'chevron-down'}
            size={18}
            color={colors.textSecondary}
          />
        </View>
      </TouchableOpacity>

      {expanded && (
        <View style={styles.expandedBody}>
          {/* Eligibility */}
          <Text style={styles.sectionLabel}>✅ ਯੋਗਤਾ</Text>
          {scheme.eligibility_pa.map((e, i) => (
            <Text key={i} style={styles.bulletText}>• {e}</Text>
          ))}

          {/* How to apply */}
          <Text style={[styles.sectionLabel, { marginTop: spacing.sm }]}>📋 ਅਰਜ਼ੀ ਕਿਵੇਂ ਦਿੱਤੀ ਜਾਵੇ</Text>
          <Text style={styles.bodyText}>{scheme.howToApply_pa}</Text>

          {/* Deadline */}
          {scheme.deadline && (
            <View style={styles.deadlineRow}>
              <Ionicons name="calendar" size={13} color={colors.warning} />
              <Text style={styles.deadlineText}> {scheme.deadline}</Text>
            </View>
          )}

          {/* Actions */}
          <View style={styles.actionRow}>
            <TouchableOpacity onPress={speak} style={styles.actionBtn}>
              <Ionicons name="volume-high" size={15} color={colors.accent} />
              <Text style={styles.actionBtnText}>ਸੁਣੋ</Text>
            </TouchableOpacity>
            {scheme.helpline && (
              <TouchableOpacity
                style={styles.actionBtn}
                onPress={() => Linking.openURL(`tel:${scheme.helpline}`)}
              >
                <Ionicons name="call" size={15} color={colors.success} />
                <Text style={[styles.actionBtnText, { color: colors.success }]}>
                  {scheme.helpline}
                </Text>
              </TouchableOpacity>
            )}
            {scheme.url && (
              <TouchableOpacity
                style={styles.actionBtn}
                onPress={() => Linking.openURL(scheme.url!)}
              >
                <Ionicons name="open" size={15} color={colors.info} />
                <Text style={[styles.actionBtnText, { color: colors.info }]}>ਵੈੱਬਸਾਈਟ</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      )}
    </View>
  );
}

// ── Screen ────────────────────────────────────────────────────────────────────

export default function SchemesScreen() {
  const [filter, setFilter] = useState<'all' | 'central' | 'state'>('all');

  const filtered = filter === 'all' ? SCHEMES : SCHEMES.filter(s => s.category === filter);

  return (
    <View style={styles.container}>
      <View style={styles.headerWrap}>
        <Text style={styles.headerTitle}>🏛️ ਸਰਕਾਰੀ ਸਕੀਮਾਂ</Text>
        <Text style={styles.headerSub}>Government Agricultural Schemes</Text>

        <View style={styles.filterRow}>
          {(['all', 'central', 'state'] as const).map(f => (
            <TouchableOpacity
              key={f}
              style={[styles.filterChip, f === filter && styles.filterChipActive]}
              onPress={() => setFilter(f)}
            >
              <Text style={[styles.filterChipText, f === filter && styles.filterChipTextActive]}>
                {f === 'all' ? 'ਸਭ' : f === 'central' ? 'ਕੇਂਦਰੀ' : 'ਰਾਜ'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <FlatList
        data={filtered}
        keyExtractor={s => s.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => <SchemeCard scheme={item} />}
        ListFooterComponent={
          <View style={styles.footer}>
            <Ionicons name="information-circle" size={14} color={colors.textMuted} />
            <Text style={styles.footerText}>
              {' '}ਸਾਰੀਆਂ ਸਕੀਮਾਂ ਦੀ ਜਾਣਕਾਰੀ PAU ਅਤੇ ਭਾਰਤ ਸਰਕਾਰ ਦੀਆਂ ਅਧਿਕਾਰਤ ਵੈੱਬਸਾਈਟਾਂ ਤੋਂ।
            </Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },
  headerWrap: { padding: spacing.md, paddingBottom: spacing.sm },
  headerTitle: { ...typography.h2, marginBottom: 2 },
  headerSub: { fontSize: 12, color: colors.textSecondary, marginBottom: spacing.sm },
  filterRow: { flexDirection: 'row', gap: spacing.sm },
  filterChip: {
    paddingHorizontal: 16, paddingVertical: 7,
    backgroundColor: colors.bgCard, borderRadius: radius.full,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  filterChipActive: { borderColor: colors.accent, backgroundColor: colors.accent + '18' },
  filterChipText: { fontSize: 13, color: colors.textSecondary },
  filterChipTextActive: { color: colors.accent, fontWeight: '700' },
  list: { padding: spacing.md, gap: spacing.sm, paddingBottom: 100 },
  card: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.bgSurface, overflow: 'hidden',
  },
  cardHeader: { flexDirection: 'row', alignItems: 'flex-start', padding: spacing.md, gap: spacing.sm },
  iconWrap: { width: 44, height: 44, borderRadius: radius.md, justifyContent: 'center', alignItems: 'center' },
  cardInfo: { flex: 1 },
  cardTitleRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: 4 },
  cardName: { fontSize: 15, fontWeight: '700', color: colors.textPrimary, flex: 1 },
  catBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: radius.full },
  catText: { fontSize: 10, fontWeight: '700' },
  cardBenefit: { fontSize: 12, color: colors.textSecondary, lineHeight: 18 },
  expandedBody: {
    borderTopWidth: 1, borderTopColor: colors.bgSurface,
    padding: spacing.md, gap: 4,
  },
  sectionLabel: { fontSize: 13, fontWeight: '700', color: colors.accent, marginBottom: 4 },
  bulletText: { fontSize: 13, color: colors.textSecondary, lineHeight: 20 },
  bodyText: { fontSize: 13, color: colors.textSecondary, lineHeight: 20 },
  deadlineRow: { flexDirection: 'row', alignItems: 'center', marginTop: 6 },
  deadlineText: { fontSize: 12, color: colors.warning, fontWeight: '600' },
  actionRow: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.sm, flexWrap: 'wrap' },
  actionBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: colors.bgSurface, borderRadius: radius.full,
    paddingHorizontal: 12, paddingVertical: 6,
  },
  actionBtnText: { fontSize: 12, color: colors.accent, fontWeight: '600' },
  footer: {
    flexDirection: 'row', alignItems: 'flex-start',
    padding: spacing.md, gap: 4,
  },
  footerText: { fontSize: 11, color: colors.textMuted, flex: 1, lineHeight: 16 },
});
