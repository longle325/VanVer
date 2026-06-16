/**
 * Boundary between the FE and the real backend.
 *
 * Concerns this file owns:
 *   1. Per-endpoint mock/real flag (`useReal`)
 *   2. Base URL + fetch wrapper (`apiFetch`)
 *   3. Slug ↔ UUID translation (backend uses UUIDs everywhere; FE uses slugs)
 *   4. Current-user identity (`getCurrentUserId`) — single place that reads
 *      the OAuth-backed user id persisted after `/auth/me`.
 *   5. Character merge (backend dynamic fields + FE static lore)
 */

import { useAppStore } from "@/stores/useAppStore";
import { getCharacter as getSeedCharacter } from "@/data/characters";
import type { Character } from "@/types";

// ─── Env-driven configuration ─────────────────────────────────────────────

const DEFAULT_BASE_URL = "http://localhost:8081";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") ?? DEFAULT_BASE_URL;

const API_PREFIX = "/api/v1";

export type EndpointKey =
  | "auth"
  | "deck"
  | "characters"
  | "match"
  | "challenge"
  | "leaderboard"
  | "chat";

const ALL_ENDPOINTS: EndpointKey[] = [
  "auth", "deck", "characters", "match", "challenge", "leaderboard", "chat",
];

const realFlag = (import.meta.env.VITE_REAL_ENDPOINTS ?? "").trim();

const realEndpoints = new Set<EndpointKey>(
  // "all" or empty-when-backend-URL-is-set → every endpoint hits real backend
  realFlag === "all" || (realFlag === "" && import.meta.env.VITE_API_BASE_URL)
    ? ALL_ENDPOINTS
    : (realFlag
        .split(",")
        .map((entry: string) => entry.trim())
        .filter(Boolean) as EndpointKey[]),
);

export function useReal(endpoint: EndpointKey): boolean {
  return realEndpoints.has(endpoint);
}

// ─── Identity ─────────────────────────────────────────────────────────────

/**
 * Returns the current backend user id.
 *
 * Pulls the backend user id that RequireProfile stores after `/auth/me`.
 */
export function getCurrentUserId(): string | undefined {
  return useAppStore.getState().profile?.userId;
}

export function requireCurrentUserId(): string {
  const id = getCurrentUserId();
  if (!id) {
    throw new ApiError(
      "Chưa có phiên người dùng. Vui lòng vào lại phần giới thiệu.",
      401,
    );
  }
  return id;
}

// ─── Fetch wrapper ────────────────────────────────────────────────────────

export class ApiError extends Error {
  status: number;
  body?: unknown;
  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

/**
 * Detect a "session no longer valid" backend response (typically the user
 * row was wiped while localStorage still holds its UUID). Clears local
 * profile and bounces to onboarding so downstream calls don't keep crashing.
 * Idempotent and safe to call multiple times.
 */
export function handleSessionExpired(status: number, detail: string): void {
  if (status !== 404 || !/user not found/i.test(detail)) return;
  if (typeof window === "undefined") return;
  try {
    useAppStore.getState().resetAll();
  } catch {
    // even if Zustand fails, the redirect below still recovers.
  }
  if (!window.location.hash.includes("/onboarding")) {
    window.location.replace("/#/onboarding");
  }
}

interface FetchOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  query?: Record<string, string | number | undefined>;
  signal?: AbortSignal;
  /** If true, automatically appends `?user_id=` from the current session. */
  withUser?: boolean;
}

export async function apiFetch<T = unknown>(
  path: string,
  options: FetchOptions = {},
): Promise<T> {
  const url = new URL(API_PREFIX + path, API_BASE_URL);

  const query: Record<string, string | number | undefined> = {
    ...(options.query ?? {}),
  };
  if (options.withUser) {
    query.user_id = requireCurrentUserId();
  }
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined) continue;
    url.searchParams.set(key, String(value));
  }

  const init: RequestInit = {
    method: options.method ?? "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    signal: options.signal,
  };
  if (options.body !== undefined) {
    init.body = JSON.stringify(options.body);
  }

  let response: Response;
  try {
    response = await fetch(url.toString(), init);
  } catch (err) {
    throw new ApiError(
      "Không kết nối được tới máy chủ. Kiểm tra backend đang chạy chưa.",
      0,
      err,
    );
  }

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json().catch(() => undefined) : undefined;

  if (!response.ok) {
    const detail =
      (typeof payload === "object" && payload !== null && "detail" in payload
        ? String((payload as { detail: unknown }).detail)
        : undefined) ?? `HTTP ${response.status}`;

    handleSessionExpired(response.status, detail);
    throw new ApiError(detail, response.status, payload);
  }

  return payload as T;
}

// ─── Slug ↔ UUID map ──────────────────────────────────────────────────────

// Matches the backend `CharacterCard` shape — only the fields we need to
// build the slug↔UUID map. Backend names the UUID field `id`.
interface CharacterIdRecord {
  slug: string;
  id: string;
}

const slugToUuid = new Map<string, string>();
const uuidToSlug = new Map<string, string>();

export function rememberCharacterId(slug: string, uuid: string): void {
  slugToUuid.set(slug, uuid);
  uuidToSlug.set(uuid, slug);
}

export function getCachedUuidBySlug(slug: string): string | undefined {
  return slugToUuid.get(slug);
}

export function getCachedSlugByUuid(uuid: string): string | undefined {
  return uuidToSlug.get(uuid);
}

let mapPromise: Promise<void> | null = null;

/**
 * Lazily fetches `GET /characters` once and seeds the slug↔UUID map. Subsequent
 * calls return the same in-flight promise. Necessary on cold deep-links where
 * the FE has only a slug (e.g. `/characters/chi-pheo`) and no deck call has
 * populated the map yet.
 */
export async function ensureSlugMap(): Promise<void> {
  if (slugToUuid.size > 0) return;
  if (!mapPromise) {
    mapPromise = apiFetch<CharacterIdRecord[]>("/characters")
      .then((rows) => {
        for (const row of rows) {
          if (!row?.slug || !row?.id) continue;
          const normalized = row.slug.replace(/_/g, "-");
          rememberCharacterId(normalized, row.id);
          if (normalized !== row.slug) rememberCharacterId(row.slug, row.id);
        }
      })
      .catch((err) => {
        mapPromise = null; // allow retry
        throw err;
      });
  }
  return mapPromise;
}

export async function resolveSlugToUuid(slug: string): Promise<string> {
  const cached = slugToUuid.get(slug);
  if (cached) return cached;
  await ensureSlugMap();
  const resolved = slugToUuid.get(slug);
  if (!resolved) {
    throw new ApiError(`Không tìm thấy nhân vật với slug "${slug}".`, 404);
  }
  return resolved;
}

// ─── Character merging ────────────────────────────────────────────────────

/**
 * Backend ships a small `CharacterCard`. The FE keeps the rich, presentational
 * lore (images, art colors, themes, suggested questions, challenge prompts) in
 * `src/data/characters.ts`. This merger uses the backend slug to look up the
 * full FE seed, then overlays any dynamic fields from the backend on top.
 */
export interface BackendCharacterCard {
  id: string; // UUID
  slug: string;
  name: string;
  author: string;
  work_title: string;
  short_bio?: string | null;
  avatar_url?: string | null;
  difficulty_level: number;
  personality_traits?: string[] | null;
  emotional_conflicts?: string | null;
  social_context?: string | null;
  famous_quote?: string | null;
  voice_instructions?: string | null;
}

/**
 * Backend stores slugs with underscores (`chi_pheo`) while the FE seed and
 * URL convention use hyphens (`chi-pheo`). Normalize to the FE form at the
 * boundary so the rest of the codebase only ever sees kebab-case.
 */
function normalizeSlug(slug: string): string {
  return slug.replace(/_/g, "-");
}

export function mergeBackendCharacter(
  card: BackendCharacterCard,
): Character | undefined {
  const slug = normalizeSlug(card.slug);
  rememberCharacterId(slug, card.id);
  // Also remember the raw backend slug so a server that sometimes returns
  // either form still resolves to the same UUID.
  if (slug !== card.slug) rememberCharacterId(card.slug, card.id);
  const seed = getSeedCharacter(slug);
  if (!seed) {
    // No matching seed — caller should treat this as an unknown character.
    // (E.g. the backend introduced a new character before the FE seed
    // shipped.) Return undefined so the deck can filter it out.
    return undefined;
  }
  return {
    ...seed,
    // Prefer backend ground-truth for the few fields it owns; fall back to
    // seed defaults when the backend leaves them null.
    name: card.name || seed.name,
    work: card.work_title || seed.work,
    author: card.author || seed.author,
    bio: card.short_bio ?? seed.bio,
    quote: card.famous_quote ?? seed.quote,
    conflict: card.emotional_conflicts ?? seed.conflict,
    context: card.social_context ?? seed.context,
    personality: card.personality_traits?.length
      ? card.personality_traits.join(", ")
      : seed.personality,
    voice: card.voice_instructions ?? seed.voice,
    image: card.avatar_url ?? seed.image,
  };
}
