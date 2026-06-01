/**
 * offlineCache.ts — Offline-first SQLite-style cache for Kisaan Saathi
 *
 * Uses AsyncStorage with structured keys and TTL expiry.
 * Designed to serve crop recommendations, weather, and market data
 * when the device is offline or the API is unreachable.
 *
 * Cache key format:  "ks_cache::<namespace>::<hash>"
 * Metadata key:      "ks_cache_index"  (list of all cached keys + expiry)
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const CACHE_PREFIX = 'ks_cache::';
const INDEX_KEY = 'ks_cache_index';

// TTL constants (milliseconds)
export const TTL = {
  CROP_RECOMMENDATION: 7 * 24 * 60 * 60 * 1000,   // 7 days
  WEATHER:              6 * 60 * 60 * 1000,         // 6 hours
  MARKET_PRICES:       24 * 60 * 60 * 1000,         // 1 day
  SOIL_ZONES:          30 * 24 * 60 * 60 * 1000,    // 30 days (rarely changes)
  CROP_SEASONS:        30 * 24 * 60 * 60 * 1000,    // 30 days
} as const;

export interface CacheEntry<T = unknown> {
  data: T;
  cachedAt: number;       // Unix ms
  expiresAt: number;      // Unix ms
  namespace: string;
  key: string;
}

export interface CacheIndex {
  [storageKey: string]: { expiresAt: number };
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function storageKey(namespace: string, key: string): string {
  return `${CACHE_PREFIX}${namespace}::${key}`;
}

function hashKey(obj: object): string {
  // Simple deterministic string hash for objects
  return JSON.stringify(obj)
    .split('')
    .reduce((acc, ch) => ((acc << 5) - acc + ch.charCodeAt(0)) | 0, 0)
    .toString(36)
    .replace('-', 'n');
}

// ── Index management ─────────────────────────────────────────────────────────

async function readIndex(): Promise<CacheIndex> {
  try {
    const raw = await AsyncStorage.getItem(INDEX_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

async function writeIndex(index: CacheIndex): Promise<void> {
  try {
    await AsyncStorage.setItem(INDEX_KEY, JSON.stringify(index));
  } catch {}
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Save data to the offline cache.
 */
export async function cacheSet<T>(
  namespace: string,
  keyObj: string | object,
  data: T,
  ttlMs: number,
): Promise<void> {
  const key = typeof keyObj === 'string' ? keyObj : hashKey(keyObj);
  const sk = storageKey(namespace, key);
  const now = Date.now();
  const entry: CacheEntry<T> = {
    data,
    cachedAt: now,
    expiresAt: now + ttlMs,
    namespace,
    key,
  };

  try {
    await AsyncStorage.setItem(sk, JSON.stringify(entry));

    // Update index
    const index = await readIndex();
    index[sk] = { expiresAt: entry.expiresAt };
    await writeIndex(index);
  } catch {}
}

/**
 * Retrieve data from the offline cache.
 * Returns null if the entry is missing or expired.
 */
export async function cacheGet<T>(
  namespace: string,
  keyObj: string | object,
): Promise<{ data: T; cachedAt: number; isStale: boolean } | null> {
  const key = typeof keyObj === 'string' ? keyObj : hashKey(keyObj);
  const sk = storageKey(namespace, key);

  try {
    const raw = await AsyncStorage.getItem(sk);
    if (!raw) return null;

    const entry: CacheEntry<T> = JSON.parse(raw);
    const now = Date.now();

    if (now > entry.expiresAt) {
      // Expired — clean up
      await AsyncStorage.removeItem(sk);
      const index = await readIndex();
      delete index[sk];
      await writeIndex(index);
      return null;
    }

    return {
      data: entry.data,
      cachedAt: entry.cachedAt,
      isStale: false,
    };
  } catch {
    return null;
  }
}

/**
 * Check if a valid (non-expired) cache entry exists.
 */
export async function cacheHas(namespace: string, keyObj: string | object): Promise<boolean> {
  const result = await cacheGet(namespace, keyObj);
  return result !== null;
}

/**
 * Delete a specific cache entry.
 */
export async function cacheDelete(namespace: string, keyObj: string | object): Promise<void> {
  const key = typeof keyObj === 'string' ? keyObj : hashKey(keyObj);
  const sk = storageKey(namespace, key);
  try {
    await AsyncStorage.removeItem(sk);
    const index = await readIndex();
    delete index[sk];
    await writeIndex(index);
  } catch {}
}

/**
 * Purge all expired entries from the cache (housekeeping).
 * Call on app startup.
 */
export async function cachePurgeExpired(): Promise<number> {
  const index = await readIndex();
  const now = Date.now();
  const expiredKeys: string[] = [];

  for (const [sk, meta] of Object.entries(index)) {
    if (now > meta.expiresAt) expiredKeys.push(sk);
  }

  if (expiredKeys.length > 0) {
    await AsyncStorage.multiRemove(expiredKeys);
    const newIndex = { ...index };
    for (const k of expiredKeys) delete newIndex[k];
    await writeIndex(newIndex);
  }

  return expiredKeys.length;
}

/**
 * Get a summary of all cached namespaces and entry counts.
 * Useful for a "Offline Data" settings screen.
 */
export async function cacheStats(): Promise<Record<string, { count: number; oldestMs: number }>> {
  const index = await readIndex();
  const now = Date.now();
  const stats: Record<string, { count: number; oldestMs: number }> = {};

  for (const [sk, meta] of Object.entries(index)) {
    if (now > meta.expiresAt) continue; // skip expired
    const parts = sk.replace(CACHE_PREFIX, '').split('::');
    const ns = parts[0] || 'unknown';
    if (!stats[ns]) stats[ns] = { count: 0, oldestMs: now };
    stats[ns].count++;
    stats[ns].oldestMs = Math.min(stats[ns].oldestMs, meta.expiresAt - (meta.expiresAt - now));
  }

  return stats;
}
