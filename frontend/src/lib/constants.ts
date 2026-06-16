/* ── Point system (mirrors backend/core/config.py) ── */

export const POINTS = {
  MATCH: 10,
  CHALLENGE_COMPLETE: 50,
  CHALLENGE_PASS_BONUS: 40,
  PERFECT_SCORE_BONUS: 25,
  PASS_THRESHOLD: 4,
  TOTAL_QUESTIONS: 5,
} as const;

/* ── Storage key ── */
export const STORAGE_KEY = "peakverse-state";

/* ── API ── */
export const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8081/api/v1";
