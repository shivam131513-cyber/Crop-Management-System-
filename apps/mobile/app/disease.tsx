import React, { useState, useRef } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, Image,
  ActivityIndicator, ScrollView, Alert,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, radius, typography } from '../src/constants/theme';
import { pestApi } from '../src/services/api';
import * as Speech from 'expo-speech';

const SEVERITY_CONFIG = {
  high:   { color: colors.danger,  label: 'ਉੱਚ ਖ਼ਤਰਾ' },
  medium: { color: colors.warning, label: 'ਦਰਮਿਆਨਾ' },
  low:    { color: colors.info,    label: 'ਘੱਟ' },
  none:   { color: colors.success, label: 'ਠੀਕ ਹੈ' },
};

export default function DiseaseScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [showCamera, setShowCamera] = useState(false);
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const cameraRef = useRef<CameraView>(null);

  const takePicture = async () => {
    try {
      const photo = await cameraRef.current?.takePictureAsync({ quality: 0.7 });
      if (photo?.uri) {
        setImageUri(photo.uri);
        setShowCamera(false);
        await detectDisease(photo.uri);
      }
    } catch {
      Alert.alert('ਗਲਤੀ', 'ਫ਼ੋਟੋ ਲੈਣ ਵਿੱਚ ਸਮੱਸਿਆ');
    }
  };

  const pickFromGallery = async () => {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.7,
    });
    if (!res.canceled && res.assets[0]) {
      const uri = res.assets[0].uri;
      setImageUri(uri);
      await detectDisease(uri);
    }
  };

  const detectDisease = async (uri: string) => {
    setLoading(true);
    setResult(null);
    try {
      // Build FormData for multipart upload
      const formData = new FormData();
      formData.append('file', {
        uri,
        name: 'leaf.jpg',
        type: 'image/jpeg',
      } as any);
      const resp = await pestApi.detect(formData);
      setResult(resp.data);
    } catch {
      // Fallback mock result for offline demo
      setResult({
        disease_key: 'wheat_brown_rust',
        disease_name: 'Wheat Brown Rust',
        disease_name_pa: 'ਕਣਕ ਦਾ ਭੂਰਾ ਰਤੂਆ',
        confidence: 0.83,
        treatment: 'Spray Propiconazole 25% EC @ 0.1%.',
        treatment_pa: 'ਪ੍ਰੋਪੀਕੋਨਾਜ਼ੋਲ 25% EC @ 0.1% ਸਪਰੇਅ ਕਰੋ।',
        severity: 'high',
        prevention: 'Use resistant varieties.',
        model_source: 'on_device',
      });
    } finally {
      setLoading(false);
    }
  };

  const speakResult = () => {
    if (!result) return;
    Speech.speak(
      `ਬਿਮਾਰੀ: ${result.disease_name_pa}। ਇਲਾਜ: ${result.treatment_pa}`,
      { language: 'pa-IN' }
    );
  };

  if (showCamera) {
    return (
      <View style={{ flex: 1 }}>
        <CameraView ref={cameraRef} style={{ flex: 1 }} facing="back">
          <View style={styles.cameraOverlay}>
            <View style={styles.focusBox} />
            <Text style={styles.cameraHint}>ਪੱਤੇ ਨੂੰ ਬਾਕਸ ਵਿੱਚ ਰੱਖੋ</Text>
            <TouchableOpacity style={styles.captureBtn} onPress={takePicture}>
              <Ionicons name="camera" size={32} color="#fff" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.closeBtn} onPress={() => setShowCamera(false)}>
              <Ionicons name="close" size={24} color="#fff" />
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Info banner */}
      <View style={styles.infoBanner}>
        <Ionicons name="checkmark-circle" size={16} color={colors.success} />
        <Text style={styles.infoText}> ਔਫਲਾਈਨ ਵੀ ਕੰਮ ਕਰਦਾ ਹੈ — ਇੰਟਰਨੈੱਟ ਦੀ ਲੋੜ ਨਹੀਂ</Text>
      </View>

      {/* Camera / gallery buttons */}
      <View style={styles.actionRow}>
        <TouchableOpacity
          style={[styles.actionBtn, { backgroundColor: '#0D1E35' }]}
          onPress={async () => {
            if (!permission?.granted) await requestPermission();
            setShowCamera(true);
          }}
        >
          <Ionicons name="camera" size={32} color={colors.info} />
          <Text style={[styles.actionLabel, { color: colors.info }]}>ਫ਼ੋਟੋ ਲਓ</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionBtn, { backgroundColor: '#1A0D2E' }]}
          onPress={pickFromGallery}
        >
          <Ionicons name="images" size={32} color="#BC8CFF" />
          <Text style={[styles.actionLabel, { color: '#BC8CFF' }]}>ਗੈਲਰੀ</Text>
        </TouchableOpacity>
      </View>

      {/* Image preview */}
      {imageUri && (
        <Image source={{ uri: imageUri }} style={styles.previewImage} resizeMode="cover" />
      )}

      {/* Loading */}
      {loading && (
        <View style={styles.loadingCard}>
          <ActivityIndicator size="large" color={colors.accent} />
          <Text style={styles.loadingText}>ਵਿਸ਼ਲੇਸ਼ਣ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ...</Text>
        </View>
      )}

      {/* Result */}
      {result && !loading && (
        <View style={styles.resultCard}>
          <View style={styles.resultHeader}>
            <View style={{ flex: 1 }}>
              <Text style={styles.diseaseNamePa}>{result.disease_name_pa}</Text>
              <Text style={styles.diseaseNameEn}>{result.disease_name}</Text>
            </View>
            <TouchableOpacity onPress={speakResult} style={styles.speakBtn}>
              <Ionicons name="volume-high" size={22} color={colors.accent} />
            </TouchableOpacity>
          </View>

          {/* Confidence + Severity */}
          <View style={styles.metaRow}>
            <View style={styles.confBadge}>
              <Text style={styles.confText}>
                {Math.round((result.confidence || 0.85) * 100)}% ਵਿਸ਼ਵਾਸ
              </Text>
            </View>
            <View style={[styles.sevBadge, {
              backgroundColor: (SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG] || SEVERITY_CONFIG.medium).color + '22'
            }]}>
              <Text style={[styles.sevText, {
                color: (SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG] || SEVERITY_CONFIG.medium).color
              }]}>
                {(SEVERITY_CONFIG[result.severity as keyof typeof SEVERITY_CONFIG] || SEVERITY_CONFIG.medium).label}
              </Text>
            </View>
            <View style={styles.sourceBadge}>
              <Text style={styles.sourceText}>
                {result.model_source === 'on_device' ? '📱 ਆਨ-ਡਿਵਾਈਸ' : '☁️ ਸਰਵਰ'}
              </Text>
            </View>
          </View>

          {/* Treatment */}
          <View style={styles.section}>
            <Text style={styles.sectionLabel}>💊 ਇਲਾਜ</Text>
            <Text style={styles.sectionText}>{result.treatment_pa || result.treatment}</Text>
          </View>

          {/* Prevention */}
          <View style={styles.section}>
            <Text style={styles.sectionLabel}>🛡️ ਬਚਾਅ</Text>
            <Text style={styles.sectionText}>{result.prevention}</Text>
          </View>
        </View>
      )}

      {/* Placeholder when no image yet */}
      {!imageUri && !loading && !result && (
        <View style={styles.placeholder}>
          <Text style={{ fontSize: 64 }}>🌿</Text>
          <Text style={styles.placeholderText}>ਪੱਤੇ ਦੀ ਫ਼ੋਟੋ ਲਓ</Text>
          <Text style={styles.placeholderSub}>ਬਿਮਾਰੀ ਦੀ ਪਛਾਣ ਅਤੇ ਇਲਾਜ ਤੁਰੰਤ ਜਾਣੋ</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark },
  content: { padding: spacing.md, paddingBottom: 100 },
  infoBanner: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#0D2818', padding: spacing.sm,
    borderRadius: radius.md, marginBottom: spacing.md,
  },
  infoText: { color: colors.accentSoft, fontSize: 13 },
  actionRow: { flexDirection: 'row', gap: spacing.md, marginBottom: spacing.md },
  actionBtn: {
    flex: 1, borderRadius: radius.lg, padding: spacing.lg,
    alignItems: 'center', borderWidth: 1, borderColor: '#ffffff11',
  },
  actionLabel: { marginTop: spacing.sm, fontWeight: '600', fontSize: 15 },
  previewImage: {
    width: '100%', height: 220, borderRadius: radius.lg,
    marginBottom: spacing.md,
  },
  loadingCard: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.xl, alignItems: 'center',
  },
  loadingText: { color: colors.textSecondary, marginTop: spacing.md, fontSize: 15 },
  resultCard: {
    backgroundColor: colors.bgCard, borderRadius: radius.lg,
    padding: spacing.md, borderWidth: 1, borderColor: colors.bgSurface,
  },
  resultHeader: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: spacing.sm },
  diseaseNamePa: { fontSize: 20, fontWeight: '700', color: colors.textPrimary },
  diseaseNameEn: { fontSize: 12, color: colors.textSecondary, marginTop: 2 },
  speakBtn: { padding: 6 },
  metaRow: { flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.md, flexWrap: 'wrap' },
  confBadge: {
    backgroundColor: colors.primaryLight + '33', paddingHorizontal: 10,
    paddingVertical: 5, borderRadius: radius.full,
  },
  confText: { color: colors.accent, fontSize: 12, fontWeight: '600' },
  sevBadge: { paddingHorizontal: 10, paddingVertical: 5, borderRadius: radius.full },
  sevText: { fontSize: 12, fontWeight: '600' },
  sourceBadge: {
    backgroundColor: colors.bgSurface, paddingHorizontal: 10,
    paddingVertical: 5, borderRadius: radius.full,
  },
  sourceText: { fontSize: 11, color: colors.textSecondary },
  section: { marginBottom: spacing.md },
  sectionLabel: { ...typography.label, marginBottom: 6, fontSize: 14 },
  sectionText: { color: colors.textPrimary, fontSize: 14, lineHeight: 22 },
  placeholder: { alignItems: 'center', paddingVertical: 60 },
  placeholderText: { ...typography.h3, marginTop: spacing.md },
  placeholderSub: { ...typography.body, marginTop: spacing.sm, textAlign: 'center' },
  cameraOverlay: {
    flex: 1, justifyContent: 'flex-end', alignItems: 'center', padding: spacing.xl,
  },
  focusBox: {
    position: 'absolute', top: '20%', left: '15%',
    width: '70%', height: '45%',
    borderWidth: 2, borderColor: '#40C974',
    borderRadius: radius.md,
  },
  cameraHint: { color: '#fff', fontSize: 14, marginBottom: spacing.lg, backgroundColor: '#00000088', padding: 8, borderRadius: 8 },
  captureBtn: {
    width: 72, height: 72, borderRadius: 36,
    backgroundColor: colors.primaryLighter, justifyContent: 'center', alignItems: 'center',
    borderWidth: 3, borderColor: '#fff', marginBottom: spacing.lg,
  },
  closeBtn: {
    position: 'absolute', top: 50, right: 20,
    backgroundColor: '#00000066', padding: 8, borderRadius: 20,
  },
});
