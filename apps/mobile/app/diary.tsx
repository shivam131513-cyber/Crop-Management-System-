/**
 * Farm Diary Screen — ਖੇਤ ਡਾਇਰੀ
 *
 * Farmers can log daily field notes: watering, pesticide application,
 * fertilizer applied, observations, etc. All data is stored locally
 * using AsyncStorage (offline-first, no server needed).
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, Alert, Modal, KeyboardAvoidingView, Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { colors, spacing, radius, typography } from '../src/constants/theme';

// ── Types ─────────────────────────────────────────────────────────────────────

type ActivityTag =
  | 'irrigation'
  | 'fertilizer'
  | 'pesticide'
  | 'sowing'
  | 'harvest'
  | 'observation'
  | 'other';

interface DiaryEntry {
  id: string;
  date: string;         // ISO date string
  tag: ActivityTag;
  note: string;
  crop?: string;
  field?: string;
}

// ── Constants ─────────────────────────────────────────────────────────────────

const DIARY_KEY = 'ks_farm_diary';

const TAGS: { value: ActivityTag; label: string; icon: string; color: string }[] = [
  { value: 'irrigation',  label: 'ਸਿੰਚਾਈ',       icon: '💧', color: '#3B82F6' },
  { value: 'fertilizer',  label: 'ਖਾਦ',           icon: '🌿', color: '#10B981' },
  { value: 'pesticide',   label: 'ਕੀਟਨਾਸ਼ਕ',     icon: '🧪', color: '#F59E0B' },
  { value: 'sowing',      label: 'ਬਿਜਾਈ',         icon: '🌱', color: '#6366F1' },
  { value: 'harvest',     label: 'ਵਾਢੀ',           icon: '🌾', color: '#EAB308' },
  { value: 'observation', label: 'ਨਿਰੀਖਣ',        icon: '👁️', color: '#8B5CF6' },
  { value: 'other',       label: 'ਹੋਰ',            icon: '📝', color: '#6B7280' },
];

function tagMeta(tag: ActivityTag) {
  return TAGS.find(t => t.value === tag) ?? TAGS[TAGS.length - 1];
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('pa-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function todayISO(): string {
  return new Date().toISOString().split('T')[0];
}

// ── Sub-components ────────────────────────────────────────────────────────────

function TagPill({ tag, selected, onPress }: { tag: typeof TAGS[0]; selected: boolean; onPress: () => void }) {
  return (
    <TouchableOpacity
      style={[styles.tagPill, selected && { backgroundColor: tag.color + '33', borderColor: tag.color }]}
      onPress={onPress}
      accessibilityRole="button"
    >
      <Text style={{ marginRight: 4 }}>{tag.icon}</Text>
      <Text style={[styles.tagText, selected && { color: tag.color, fontWeight: '700' }]}>
        {tag.label}
      </Text>
    </TouchableOpacity>
  );
}

function EntryCard({ entry, onDelete }: { entry: DiaryEntry; onDelete: () => void }) {
  const meta = tagMeta(entry.tag);
  return (
    <View style={[styles.entryCard, { borderLeftColor: meta.color }]}>
      <View style={styles.entryHeader}>
        <View style={styles.entryTagRow}>
          <Text style={{ fontSize: 16, marginRight: 6 }}>{meta.icon}</Text>
          <Text style={[styles.entryTagLabel, { color: meta.color }]}>{meta.label}</Text>
          {entry.crop ? <Text style={styles.entryCrop}> · {entry.crop}</Text> : null}
        </View>
        <View style={styles.entryRight}>
          <Text style={styles.entryDate}>{formatDate(entry.date)}</Text>
          <TouchableOpacity onPress={onDelete} style={styles.deleteBtn} accessibilityLabel="ਮਿਟਾਓ">
            <Ionicons name="trash-outline" size={15} color={colors.danger} />
          </TouchableOpacity>
        </View>
      </View>
      <Text style={styles.entryNote}>{entry.note}</Text>
      {entry.field ? <Text style={styles.entryField}>📍 {entry.field}</Text> : null}
    </View>
  );
}

// ── Main Screen ───────────────────────────────────────────────────────────────

export default function DiaryScreen() {
  const [entries, setEntries] = useState<DiaryEntry[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [filterTag, setFilterTag] = useState<ActivityTag | null>(null);

  // New entry form state
  const [newTag, setNewTag] = useState<ActivityTag>('observation');
  const [newNote, setNewNote] = useState('');
  const [newCrop, setNewCrop] = useState('');
  const [newField, setNewField] = useState('');

  // ── Load from storage ───────────────────────────────────────────────────────
  const loadEntries = useCallback(async () => {
    try {
      const raw = await AsyncStorage.getItem(DIARY_KEY);
      if (raw) setEntries(JSON.parse(raw));
    } catch {}
  }, []);

  useEffect(() => { loadEntries(); }, [loadEntries]);

  // ── Save to storage ─────────────────────────────────────────────────────────
  const persist = async (updated: DiaryEntry[]) => {
    setEntries(updated);
    await AsyncStorage.setItem(DIARY_KEY, JSON.stringify(updated));
  };

  // ── Add entry ───────────────────────────────────────────────────────────────
  const addEntry = async () => {
    if (!newNote.trim()) {
      Alert.alert('', 'ਨੋਟ ਲਿਖਣਾ ਜ਼ਰੂਰੀ ਹੈ।');
      return;
    }
    const entry: DiaryEntry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      date: todayISO(),
      tag: newTag,
      note: newNote.trim(),
      crop: newCrop.trim() || undefined,
      field: newField.trim() || undefined,
    };
    await persist([entry, ...entries]);
    setNewNote('');
    setNewCrop('');
    setNewField('');
    setNewTag('observation');
    setModalVisible(false);
  };

  // ── Delete entry ────────────────────────────────────────────────────────────
  const deleteEntry = (id: string) => {
    Alert.alert(
      'ਮਿਟਾਓ?',
      'ਕੀ ਤੁਸੀਂ ਇਹ ਦਰਜ ਮਿਟਾਉਣਾ ਚਾਹੁੰਦੇ ਹੋ?',
      [
        { text: 'ਨਹੀਂ', style: 'cancel' },
        {
          text: 'ਹਾਂ, ਮਿਟਾਓ',
          style: 'destructive',
          onPress: async () => await persist(entries.filter(e => e.id !== id)),
        },
      ],
    );
  };

  // ── Filtered view ───────────────────────────────────────────────────────────
  const displayed = filterTag ? entries.filter(e => e.tag === filterTag) : entries;

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <View style={styles.container}>
      {/* Filter bar */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filterBar}
        contentContainerStyle={styles.filterBarContent}
      >
        <TouchableOpacity
          style={[styles.filterChip, !filterTag && styles.filterChipActive]}
          onPress={() => setFilterTag(null)}
        >
          <Text style={[styles.filterChipText, !filterTag && styles.filterChipTextActive]}>
            ਸਾਰੇ
          </Text>
        </TouchableOpacity>
        {TAGS.map(t => (
          <TouchableOpacity
            key={t.value}
            style={[styles.filterChip, filterTag === t.value && { backgroundColor: t.color + '33', borderColor: t.color }]}
            onPress={() => setFilterTag(prev => prev === t.value ? null : t.value)}
          >
            <Text style={{ marginRight: 3 }}>{t.icon}</Text>
            <Text style={[styles.filterChipText, filterTag === t.value && { color: t.color }]}>
              {t.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Entry list */}
      <ScrollView style={styles.list} contentContainerStyle={styles.listContent}>
        {displayed.length === 0 ? (
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>📒</Text>
            <Text style={styles.emptyTitle}>ਕੋਈ ਦਰਜ ਨਹੀਂ</Text>
            <Text style={styles.emptySubtitle}>
              ਹੇਠਾਂ + ਬਟਨ ਦਬਾ ਕੇ ਆਪਣੀ ਪਹਿਲੀ ਖੇਤ ਡਾਇਰੀ ਦਰਜ ਕਰੋ।
            </Text>
          </View>
        ) : (
          displayed.map(entry => (
            <EntryCard
              key={entry.id}
              entry={entry}
              onDelete={() => deleteEntry(entry.id)}
            />
          ))
        )}
      </ScrollView>

      {/* Floating Add Button */}
      <TouchableOpacity
        style={styles.fab}
        onPress={() => setModalVisible(true)}
        accessibilityLabel="ਨਵੀਂ ਦਰਜ ਜੋੜੋ"
      >
        <Ionicons name="add" size={28} color="#fff" />
      </TouchableOpacity>

      {/* Add Entry Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent
        onRequestClose={() => setModalVisible(false)}
      >
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.modalOverlay}
        >
          <View style={styles.modalSheet}>
            {/* Header */}
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>📝 ਨਵੀਂ ਦਰਜ</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Ionicons name="close" size={22} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false}>
              {/* Activity type */}
              <Text style={styles.fieldLabel}>ਗਤੀਵਿਧੀ ਦੀ ਕਿਸਮ</Text>
              <View style={styles.tagGrid}>
                {TAGS.map(t => (
                  <TagPill
                    key={t.value}
                    tag={t}
                    selected={newTag === t.value}
                    onPress={() => setNewTag(t.value)}
                  />
                ))}
              </View>

              {/* Note */}
              <Text style={styles.fieldLabel}>ਨੋਟ *</Text>
              <TextInput
                style={styles.textArea}
                value={newNote}
                onChangeText={setNewNote}
                placeholder="ਉਦਾਹਰਨ: ਅੱਜ ਕਣਕ ਨੂੰ ਯੂਰੀਆ 20 ਕਿਲੋ ਪ੍ਰਤੀ ਏਕੜ ਪਾਈ..."
                placeholderTextColor={colors.textSecondary + '80'}
                multiline
                numberOfLines={3}
                textAlignVertical="top"
              />

              {/* Crop (optional) */}
              <Text style={styles.fieldLabel}>ਫ਼ਸਲ (ਵਿਕਲਪਿਕ)</Text>
              <TextInput
                style={styles.input}
                value={newCrop}
                onChangeText={setNewCrop}
                placeholder="ਕਣਕ / ਚਾਵਲ / ਮੱਕੀ..."
                placeholderTextColor={colors.textSecondary + '80'}
              />

              {/* Field name (optional) */}
              <Text style={styles.fieldLabel}>ਖੇਤ / ਪਲਾਟ (ਵਿਕਲਪਿਕ)</Text>
              <TextInput
                style={styles.input}
                value={newField}
                onChangeText={setNewField}
                placeholder="ਉੱਤਰੀ ਖੇਤ / ਪਲਾਟ A..."
                placeholderTextColor={colors.textSecondary + '80'}
              />

              {/* Save button */}
              <TouchableOpacity style={styles.saveBtn} onPress={addEntry}>
                <Ionicons name="checkmark-circle" size={18} color="#fff" />
                <Text style={styles.saveBtnText}>  ਸੇਵ ਕਰੋ</Text>
              </TouchableOpacity>

              <View style={{ height: 24 }} />
            </ScrollView>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </View>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },

  filterBar: { maxHeight: 52, borderBottomWidth: 1, borderBottomColor: '#1F2937' },
  filterBarContent: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm, gap: spacing.sm, flexDirection: 'row' },
  filterChip: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 12, paddingVertical: 6,
    borderRadius: radius.full, borderWidth: 1,
    borderColor: colors.bgSurface, backgroundColor: colors.bgSurface,
  },
  filterChipActive: { borderColor: colors.accent, backgroundColor: colors.accent + '22' },
  filterChipText: { color: colors.textSecondary, fontSize: 12 },
  filterChipTextActive: { color: colors.accent, fontWeight: '700' },

  list: { flex: 1 },
  listContent: { padding: spacing.md, paddingBottom: 100 },

  empty: { alignItems: 'center', paddingTop: 80 },
  emptyIcon: { fontSize: 52, marginBottom: spacing.md },
  emptyTitle: { ...typography.h3, marginBottom: spacing.sm },
  emptySubtitle: { color: colors.textSecondary, fontSize: 13, textAlign: 'center', lineHeight: 20 },

  entryCard: {
    backgroundColor: colors.bgCard,
    borderRadius: radius.lg,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderLeftWidth: 4,
  },
  entryHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 },
  entryTagRow: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  entryTagLabel: { fontSize: 13, fontWeight: '700' },
  entryCrop: { color: colors.textSecondary, fontSize: 12 },
  entryRight: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  entryDate: { color: colors.textSecondary, fontSize: 11 },
  deleteBtn: { padding: 4 },
  entryNote: { color: colors.textPrimary, fontSize: 14, lineHeight: 20 },
  entryField: { color: colors.textSecondary, fontSize: 11, marginTop: 4 },

  fab: {
    position: 'absolute', right: spacing.lg, bottom: spacing.lg,
    width: 56, height: 56, borderRadius: 28,
    backgroundColor: colors.primary,
    alignItems: 'center', justifyContent: 'center',
    elevation: 6,
    shadowColor: colors.primary, shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.4, shadowRadius: 8,
  },

  modalOverlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: '#00000088' },
  modalSheet: {
    backgroundColor: colors.bgCard,
    borderTopLeftRadius: 24, borderTopRightRadius: 24,
    padding: spacing.lg,
    maxHeight: '90%',
  },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md },
  modalTitle: { ...typography.h2 },

  fieldLabel: { ...typography.label, marginTop: spacing.md, marginBottom: spacing.sm },
  tagGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  tagPill: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 12, paddingVertical: 7,
    borderRadius: radius.full, borderWidth: 1,
    borderColor: colors.bgSurface, backgroundColor: colors.bgSurface,
  },
  tagText: { color: colors.textSecondary, fontSize: 12 },

  textArea: {
    backgroundColor: colors.bgSurface, borderRadius: radius.md,
    padding: spacing.md, color: colors.textPrimary,
    fontSize: 14, minHeight: 80, lineHeight: 20,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  input: {
    backgroundColor: colors.bgSurface, borderRadius: radius.md,
    padding: spacing.md, color: colors.textPrimary,
    fontSize: 14, borderWidth: 1, borderColor: colors.bgSurface,
  },

  saveBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.primary, borderRadius: radius.lg,
    padding: spacing.md, marginTop: spacing.lg,
  },
  saveBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
});
