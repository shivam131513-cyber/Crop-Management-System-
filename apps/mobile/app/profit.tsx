/**
 * ProfitScreen — Crop Profit Calculator
 * Lets farmers enter their crop, area, cost, and selling price
 * to estimate gross profit, cost of production, and break-even MSP.
 */
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, KeyboardAvoidingView, Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, typography } from '../src/constants/theme';
import * as Speech from 'expo-speech';

const CROPS = ['ਕਣਕ', 'ਝੋਨਾ', 'ਮੱਕੀ', 'ਕਪਾਹ', 'ਸਰ੍ਹੋਂ', 'ਆਲੂ', 'ਮੂੰਗੀ'];
const CROP_EN = ['wheat', 'rice', 'maize', 'cotton', 'mustard', 'potato', 'moong'];
// Approximate MSP (₹/quintal) — update yearly
const CROP_MSP: Record<string, number> = {
  wheat: 2275, rice: 2183, maize: 2090, cotton: 7121,
  mustard: 5650, potato: 800, moong: 8558,
};
// Average yield (quintals/acre)
const CROP_YIELD: Record<string, number> = {
  wheat: 18, rice: 28, maize: 20, cotton: 10,
  mustard: 8, potato: 100, moong: 5,
};

interface Result {
  grossRevenue: number;
  netProfit: number;
  profitPerAcre: number;
  roi: number;
  breakEven: number;
  aboveMsp: boolean;
}

function ResultCard({ result, crop }: { result: Result; crop: string }) {
  const profit = result.netProfit;
  const isProfit = profit >= 0;

  const speak = () => {
    Speech.speak(
      `ਤੁਹਾਡਾ ਕੁੱਲ ਮੁਨਾਫ਼ਾ ₹${profit.toLocaleString('en-IN')} ਹੈ। ` +
      `ਪ੍ਰਤੀ ਏਕੜ ₹${result.profitPerAcre.toLocaleString('en-IN')}। ` +
      (result.aboveMsp ? 'ਭਾਅ MSP ਤੋਂ ਉੱਪਰ ਹੈ।' : 'ਭਾਅ MSP ਤੋਂ ਹੇਠਾਂ ਹੈ — ਸਰਕਾਰੀ ਖ਼ਰੀਦ ਕੇਂਦਰ ਤੇ ਜਾਓ।'),
      { language: 'pa-IN' },
    );
  };

  return (
    <View style={styles.resultCard}>
      <View style={styles.resultHeader}>
        <Text style={styles.resultTitle}>ਹਿਸਾਬ ਕਿਤਾਬ</Text>
        <TouchableOpacity onPress={speak} style={styles.speakBtn}>
          <Ionicons name="volume-high" size={18} color={colors.accent} />
        </TouchableOpacity>
      </View>

      <View style={styles.resultRow}>
        <Text style={styles.resultLabel}>ਕੁੱਲ ਆਮਦਨ</Text>
        <Text style={styles.resultValue}>₹{result.grossRevenue.toLocaleString('en-IN')}</Text>
      </View>
      <View style={styles.resultRow}>
        <Text style={styles.resultLabel}>ਖ਼ਰਚਾ</Text>
        <Text style={[styles.resultValue, { color: colors.danger }]}>
          − ₹{(result.grossRevenue - result.netProfit).toLocaleString('en-IN')}
        </Text>
      </View>
      <View style={[styles.resultRow, styles.totalRow]}>
        <Text style={styles.totalLabel}>ਸ਼ੁੱਧ ਮੁਨਾਫ਼ਾ</Text>
        <Text style={[styles.totalValue, { color: isProfit ? colors.success : colors.danger }]}>
          {isProfit ? '+' : ''}₹{profit.toLocaleString('en-IN')}
        </Text>
      </View>

      <View style={styles.divider} />

      <View style={styles.metaGrid}>
        <View style={styles.metaItem}>
          <Ionicons name="trending-up" size={16} color={colors.accent} />
          <Text style={styles.metaLabel}>ਪ੍ਰਤੀ ਏਕੜ ਮੁਨਾਫ਼ਾ</Text>
          <Text style={styles.metaValue}>₹{result.profitPerAcre.toLocaleString('en-IN')}</Text>
        </View>
        <View style={styles.metaItem}>
          <Ionicons name="bar-chart" size={16} color={colors.accent} />
          <Text style={styles.metaLabel}>ROI</Text>
          <Text style={styles.metaValue}>{result.roi.toFixed(1)}%</Text>
        </View>
        <View style={styles.metaItem}>
          <Ionicons name="analytics" size={16} color={colors.accent} />
          <Text style={styles.metaLabel}>Break-even ਭਾਅ</Text>
          <Text style={styles.metaValue}>₹{result.breakEven}/qtl</Text>
        </View>
      </View>

      {/* MSP alert */}
      <View style={[
        styles.mspAlert,
        { borderColor: result.aboveMsp ? colors.success : colors.warning },
      ]}>
        <Ionicons
          name={result.aboveMsp ? 'checkmark-circle' : 'warning'}
          size={14}
          color={result.aboveMsp ? colors.success : colors.warning}
        />
        <Text style={[styles.mspAlertText, { color: result.aboveMsp ? colors.success : colors.warning }]}>
          {result.aboveMsp
            ? ' MSP ਤੋਂ ਉੱਪਰ — ਚੰਗਾ ਭਾਅ ਮਿਲ ਰਿਹਾ ਹੈ'
            : ' MSP ਤੋਂ ਹੇਠਾਂ — ਸਰਕਾਰੀ ਖ਼ਰੀਦ ਕੇਂਦਰ ਤੇ ਜਾਓ'}
        </Text>
      </View>
    </View>
  );
}

function InputRow({
  label, value, onChangeText, unit, keyboardType = 'numeric',
}: {
  label: string; value: string; onChangeText: (t: string) => void;
  unit?: string; keyboardType?: any;
}) {
  return (
    <View style={styles.inputRow}>
      <Text style={styles.inputLabel}>{label}</Text>
      <View style={styles.inputWrapper}>
        <TextInput
          style={styles.input}
          value={value}
          onChangeText={onChangeText}
          keyboardType={keyboardType}
          placeholderTextColor={colors.textMuted}
          placeholder="0"
        />
        {unit ? <Text style={styles.inputUnit}>{unit}</Text> : null}
      </View>
    </View>
  );
}

export default function ProfitScreen() {
  const [cropIdx, setCropIdx] = useState(0);
  const [acres, setAcres] = useState('2');
  const [costPerAcre, setCostPerAcre] = useState('');
  const [sellingPrice, setSellingPrice] = useState('');
  const [yieldQtl, setYieldQtl] = useState('');
  const [result, setResult] = useState<Result | null>(null);

  const cropKey = CROP_EN[cropIdx];
  const msp = CROP_MSP[cropKey] ?? 2000;
  const defaultYield = CROP_YIELD[cropKey] ?? 15;

  const calculate = () => {
    const a = parseFloat(acres) || 0;
    const c = parseFloat(costPerAcre) || 0;
    const s = parseFloat(sellingPrice) || msp;
    const y = parseFloat(yieldQtl) || defaultYield;

    const totalYield = y * a;          // total quintals
    const grossRevenue = s * totalYield;
    const totalCost = c * a;
    const netProfit = grossRevenue - totalCost;
    const roi = totalCost > 0 ? (netProfit / totalCost) * 100 : 0;
    const breakEven = totalYield > 0 ? Math.round(totalCost / totalYield) : 0;

    setResult({
      grossRevenue: Math.round(grossRevenue),
      netProfit: Math.round(netProfit),
      profitPerAcre: a > 0 ? Math.round(netProfit / a) : 0,
      roi,
      breakEven,
      aboveMsp: s >= msp,
    });
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.heading}>💰 ਮੁਨਾਫ਼ਾ ਕੈਲਕੂਲੇਟਰ</Text>
        <Text style={styles.subHeading}>Crop Profit Calculator</Text>

        {/* Crop selector */}
        <Text style={styles.sectionLabel}>ਫ਼ਸਲ ਚੁਣੋ</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: spacing.md }}>
          <View style={{ flexDirection: 'row', gap: spacing.sm }}>
            {CROPS.map((c, i) => (
              <TouchableOpacity
                key={c}
                style={[styles.cropChip, i === cropIdx && styles.cropChipActive]}
                onPress={() => {
                  setCropIdx(i);
                  setResult(null);
                  setYieldQtl('');
                }}
              >
                <Text style={[styles.cropChipText, i === cropIdx && styles.cropChipTextActive]}>
                  {c}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>

        {/* MSP tip */}
        <View style={styles.mspTip}>
          <Ionicons name="information-circle" size={14} color={colors.info} />
          <Text style={styles.mspTipText}>
            {' '}{CROPS[cropIdx]} MSP: ₹{msp.toLocaleString('en-IN')}/ਕੁਇੰਟਲ • ਔਸਤ ਝਾੜ: {defaultYield} qtl/acre
          </Text>
        </View>

        {/* Inputs */}
        <View style={styles.card}>
          <InputRow label="ਜ਼ਮੀਨ (ਏਕੜ)" value={acres} onChangeText={t => { setAcres(t); setResult(null); }} unit="ਏਕੜ" />
          <InputRow
            label={`ਝਾੜ (ਪ੍ਰਤੀ ਏਕੜ ਕੁਇੰਟਲ)`}
            value={yieldQtl}
            onChangeText={t => { setYieldQtl(t); setResult(null); }}
            unit="qtl/ਏਕੜ"
          />
          <InputRow
            label="ਖ਼ਰਚਾ (ਪ੍ਰਤੀ ਏਕੜ)"
            value={costPerAcre}
            onChangeText={t => { setCostPerAcre(t); setResult(null); }}
            unit="₹"
          />
          <InputRow
            label="ਵਿਕਰੀ ਭਾਅ (ਪ੍ਰਤੀ ਕੁਇੰਟਲ)"
            value={sellingPrice}
            onChangeText={t => { setSellingPrice(t); setResult(null); }}
            unit="₹/qtl"
          />
        </View>

        <TouchableOpacity style={styles.calcBtn} onPress={calculate}>
          <Ionicons name="calculator" size={20} color="#fff" />
          <Text style={styles.calcBtnText}>ਮੁਨਾਫ਼ਾ ਕੱਢੋ</Text>
        </TouchableOpacity>

        {result && <ResultCard result={result} crop={cropKey} />}

        {/* Guide box */}
        <View style={styles.guideBox}>
          <Text style={styles.guideTitle}>📌 ਮਦਦਗਾਰ ਜਾਣਕਾਰੀ</Text>
          <Text style={styles.guideText}>
            • ਖ਼ਰਚੇ ਵਿੱਚ ਬੀਜ, ਖਾਦ, ਦਵਾਈ, ਮਜ਼ਦੂਰੀ ਅਤੇ ਟਰੈਕਟਰ ਖ਼ਰਚ ਸ਼ਾਮਲ ਕਰੋ।{'\n'}
            • ਜੇ ਵਿਕਰੀ ਭਾਅ MSP ਤੋਂ ਘੱਟ ਹੈ, PAU ਖ਼ਰੀਦ ਕੇਂਦਰ ਜਾਂ ਸਰਕਾਰੀ PACS ਤੇ ਜਾਓ।{'\n'}
            • ਔਸਤ ਝਾੜ ਤੋਂ ਵੱਧ ਮਿਲਣ ਲਈ ਸਿਫਾਰਸ਼ੀ ਕਿਸਮਾਂ ਅਤੇ ਸਮੇਂ ਸਿਰ ਸਿੰਚਾਈ ਕਰੋ।
          </Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },
  content: { padding: spacing.md, paddingBottom: 120 },
  heading: { ...typography.h1, marginBottom: 2 },
  subHeading: { fontSize: 13, color: colors.textSecondary, marginBottom: spacing.md },
  sectionLabel: { fontSize: 13, color: colors.textSecondary, marginBottom: spacing.sm, fontWeight: '600' },
  cropChip: {
    paddingHorizontal: 16, paddingVertical: 8,
    backgroundColor: colors.bgCard, borderRadius: radius.full,
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  cropChipActive: { backgroundColor: colors.primary + '44', borderColor: colors.accent },
  cropChipText: { color: colors.textSecondary, fontSize: 14 },
  cropChipTextActive: { color: colors.accent, fontWeight: '700' },
  mspTip: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: colors.info + '18', borderRadius: radius.sm,
    paddingHorizontal: spacing.sm, paddingVertical: 6, marginBottom: spacing.md,
  },
  mspTipText: { fontSize: 12, color: colors.info, flex: 1 },
  card: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, marginBottom: spacing.md,
    borderWidth: 1, borderColor: colors.bgSurface,
    gap: spacing.sm,
  },
  inputRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  inputLabel: { fontSize: 14, color: colors.textPrimary, flex: 1 },
  inputWrapper: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  input: {
    backgroundColor: colors.bgSurface, color: colors.textPrimary,
    borderRadius: radius.sm, paddingHorizontal: 12, paddingVertical: 8,
    fontSize: 16, fontWeight: '600', width: 100, textAlign: 'right',
    borderWidth: 1, borderColor: colors.bgSurface,
  },
  inputUnit: { fontSize: 12, color: colors.textSecondary, width: 50 },
  calcBtn: {
    backgroundColor: colors.primary, borderRadius: radius.md,
    paddingVertical: 14, flexDirection: 'row', justifyContent: 'center',
    alignItems: 'center', gap: spacing.sm, marginBottom: spacing.md,
  },
  calcBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  resultCard: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, borderWidth: 1, borderColor: colors.accent + '40',
    marginBottom: spacing.md,
  },
  resultHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: spacing.md },
  resultTitle: { fontSize: 18, fontWeight: '700', color: colors.textPrimary },
  speakBtn: { padding: 4 },
  resultRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 4 },
  resultLabel: { fontSize: 14, color: colors.textSecondary },
  resultValue: { fontSize: 14, fontWeight: '600', color: colors.textPrimary },
  totalRow: {
    borderTopWidth: 1, borderTopColor: colors.bgSurface,
    paddingTop: spacing.sm, marginTop: spacing.sm,
  },
  totalLabel: { fontSize: 16, fontWeight: '700', color: colors.textPrimary },
  totalValue: { fontSize: 20, fontWeight: '800' },
  divider: { height: 1, backgroundColor: colors.bgSurface, marginVertical: spacing.sm },
  metaGrid: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: spacing.sm },
  metaItem: { alignItems: 'center', gap: 4 },
  metaLabel: { fontSize: 10, color: colors.textMuted, textAlign: 'center' },
  metaValue: { fontSize: 14, fontWeight: '700', color: colors.textPrimary },
  mspAlert: {
    flexDirection: 'row', alignItems: 'center',
    borderWidth: 1, borderRadius: radius.sm,
    padding: spacing.sm, marginTop: spacing.sm,
  },
  mspAlertText: { fontSize: 12, fontWeight: '600', flex: 1 },
  guideBox: {
    backgroundColor: colors.bgCard, borderRadius: radius.md,
    padding: spacing.md, borderLeftWidth: 3, borderLeftColor: colors.accent,
    marginTop: spacing.sm,
  },
  guideTitle: { fontSize: 14, fontWeight: '700', color: colors.accent, marginBottom: 8 },
  guideText: { fontSize: 13, color: colors.textSecondary, lineHeight: 22 },
});
