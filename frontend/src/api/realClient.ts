/**
 * Real backend client. Each method talks to the FastAPI backend on port 8081
 * and translates the response into the FE's expected shape using helpers from
 * `./adapter.ts`.
 *
 * Phase status (kept in sync with `task.md`):
 *   ✅  createUser             — Phase 2A
 *   ✅  getLeaderboard         — Phase 2B
 *   ⏳  getDeck                — Phase 3 (slug merge ready, not flipped)
 *   ⏳  getCharacter           — Phase 3
 *   ⏳  recordMatch / recordSkip — Phase 3
 *   ⏳  getChallenge / submit  — Phase 3 (needs backend `correct_answers` echo)
 *   ⏳  streamChat / history   — Phase 4 (SSE parser TBD)
 */

import type {
  Character,
  ChallengeQuestion,
  ChallengeResult,
  ChatMessage,
  ChatSource,
  LeaderboardEntry,
  OpenEndedGradeRequest,
  OpenEndedGradeResult,
  UserProfile,
} from "@/types";
import {
  ApiError,
  API_BASE_URL,
  apiFetch,
  handleSessionExpired,
  mergeBackendCharacter,
  rememberCharacterId,
  requireCurrentUserId,
  resolveSlugToUuid,
  type BackendCharacterCard,
} from "./adapter";
import { readSseStream } from "./sse";
import type {
  ApiClient,
  ChatRequest,
  ChatStreamEvent,
  CreateUserInput,
} from "./types";

interface BackendUser {
  id: string;
  username: string;
  grade_level: number;
  total_score: number;
  created_at: string;
}

interface BackendLeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  total_score: number;
  characters_unlocked: number;
}

interface BackendLeaderboardResponse {
  entries: BackendLeaderboardEntry[];
}

interface BackendDeckResponse {
  characters: BackendCharacterCard[];
}

interface BackendChallengeQuestion {
  id: number;
  question: string;
  options: string[];
  explanation?: string | null;
}

interface BackendChallengeQuestionsResponse {
  character_id: string;
  questions: BackendChallengeQuestion[];
}

interface BackendChallengeResult {
  score: number;
  total: number;
  passed: boolean;
  points_earned: number;
  explanations: string[];
  correct_answers: number[];
}

interface BackendOpenEndedGradeResult {
  score: 0 | 1;
  passed: boolean;
  feedback: string;
  matched_criteria: string[];
  missing_criteria: string[];
  confidence: number;
  retrieval_mode: string;
}

interface BackendSwipeResponse {
  matched: boolean;
  points_earned: number;
  match_status: string | null;
}

// Backend `sources` SSE event payload — see backend/api/routes/chat.py and
// backend/services/knowledge_retriever.py:_format_sources for the source
// of truth.
interface BackendSourceEntry {
  chunk_id?: string | null;
  source_path?: string | null;
  doc_type?: string | null;
  character_name?: string | null;
  work_title?: string | null;
  author?: string | null;
}

interface BackendSourcesPayload {
  retrieval_mode?: string;
  sources?: BackendSourceEntry[];
}

interface BackendChatHistoryEntry {
  id: string;
  user_id: string;
  character_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

interface BackendChatHistoryResponse {
  messages: BackendChatHistoryEntry[];
}

function basenameNoExt(path?: string | null): string | undefined {
  if (!path) return undefined;
  const last = path.split("/").pop() ?? path;
  return last.replace(/\.[^.]+$/, "").replace(/_/g, " ");
}

function backendSourceToFe(entry: BackendSourceEntry): ChatSource | null {
  const title = entry.work_title ?? entry.character_name ?? basenameNoExt(entry.source_path);
  if (!title) return null;
  const snippetParts = [
    entry.author,
    entry.doc_type,
    basenameNoExt(entry.source_path),
  ].filter((part): part is string => Boolean(part) && part !== title);
  return {
    title,
    snippet: snippetParts.slice(0, 2).join(" · "),
  };
}

// ─── Client ───────────────────────────────────────────────────────────────

export const realClient: ApiClient = {
  async createUser(input: CreateUserInput): Promise<UserProfile> {
    const user = await apiFetch<BackendUser>("/users", {
      method: "POST",
      body: { username: input.username, grade_level: input.grade },
    });
    return {
      username: user.username,
      grade: input.grade,
      userId: user.id,
    };
  },

  async getDeck(): Promise<Character[]> {
    const res = await apiFetch<BackendDeckResponse>("/deck", {
      withUser: true,
    });
    return res.characters
      .map((card) => mergeBackendCharacter(card))
      .filter((c): c is Character => c !== undefined);
  },

  async getAllCharacters(): Promise<Character[]> {
    const cards = await apiFetch<BackendCharacterCard[]>("/characters");
    return cards
      .map((card) => mergeBackendCharacter(card))
      .filter((c): c is Character => c !== undefined);
  },

  async getCharacter(slug: string): Promise<Character> {
    const uuid = await resolveSlugToUuid(slug);
    const card = await apiFetch<BackendCharacterCard>(
      `/characters/${uuid}`,
    );
    const merged = mergeBackendCharacter(card);
    if (!merged) {
      throw new ApiError(`Không tìm thấy nhân vật ${slug}.`, 404);
    }
    return merged;
  },

  async recordMatch(slug: string): Promise<{ ok: true }> {
    const uuid = await resolveSlugToUuid(slug);
    const userId = requireCurrentUserId();
    await apiFetch<BackendSwipeResponse>("/interactions/swipe", {
      method: "POST",
      body: { user_id: userId, character_id: uuid, direction: "right" },
    });
    return { ok: true };
  },

  async getMatchedSlugs(): Promise<string[]> {
    const userId = requireCurrentUserId();
    const res = await apiFetch<{ characters: BackendCharacterCard[] }>(
      `/users/${userId}/matches`,
    );
    return res.characters
      .map((card) => mergeBackendCharacter(card)?.id)
      .filter((s): s is string => typeof s === "string");
  },

  async recordSkip(slug: string): Promise<{ ok: true }> {
    const uuid = await resolveSlugToUuid(slug);
    const userId = requireCurrentUserId();
    await apiFetch<BackendSwipeResponse>("/interactions/swipe", {
      method: "POST",
      body: { user_id: userId, character_id: uuid, direction: "left" },
    });
    return { ok: true };
  },

  async getChallenge(slug: string): Promise<ChallengeQuestion[]> {
    const uuid = await resolveSlugToUuid(slug);
    const res = await apiFetch<BackendChallengeQuestionsResponse>(
      `/characters/${uuid}/challenge`,
    );
    rememberCharacterId(slug, uuid);
    return res.questions.map((q, index) => ({
      // Backend `id` is an int; FE keys by `${slug}-q${index+1}` for parity
      // with the seed convention. The original int is not needed FE-side.
      id: `${slug}-q${index + 1}`,
      text: q.question,
      options: q.options,
      // `answer` is intentionally hidden by the backend pre-submission; FE
      // renders the question without it. The Challenge result page reads
      // `correct_answers` from the submission response (Phase 3 backend tweak).
      answer: -1,
      explanation: q.explanation ?? "",
    }));
  },

  async submitChallenge(
    slug: string,
    answers: number[],
  ): Promise<ChallengeResult> {
    const uuid = await resolveSlugToUuid(slug);
    const userId = requireCurrentUserId();
    const res = await apiFetch<BackendChallengeResult>(
      "/challenges/submit",
      {
        method: "POST",
        body: { user_id: userId, character_id: uuid, answers },
      },
    );
    return {
      score: res.score,
      passed: res.passed,
      perfect: res.score === res.total,
      awarded: res.points_earned,
      answers: [...answers],
      correctAnswers: res.correct_answers,
    };
  },

  async gradeOpenEndedAnswer(
    input: OpenEndedGradeRequest,
  ): Promise<OpenEndedGradeResult> {
    const res = await apiFetch<BackendOpenEndedGradeResult>(
      "/challenges/grade-open-ended",
      {
        method: "POST",
        body: {
          character_slug: input.characterId,
          character_name: input.characterName,
          work_title: input.workTitle,
          phase_title: input.phaseTitle ?? input.question.phaseTitle,
          question: input.question.text,
          answer: input.answer,
          rubric: input.question.rubric ?? "",
          evidence: input.question.evidence,
        },
      },
    );
    return {
      score: res.score,
      passed: res.passed,
      feedback: res.feedback,
      matchedCriteria: res.matched_criteria ?? [],
      missingCriteria: res.missing_criteria ?? [],
      confidence: res.confidence,
      retrievalMode: res.retrieval_mode,
    };
  },

  async getLeaderboard(): Promise<LeaderboardEntry[]> {
    const res = await apiFetch<BackendLeaderboardResponse>("/leaderboard");
    return res.entries.map((entry) => ({
      name: entry.username,
      points: entry.total_score,
      unlocked: entry.characters_unlocked,
      userId: entry.user_id,
    }));
  },

  async getChatHistory(slug: string): Promise<ChatMessage[]> {
    const uuid = await resolveSlugToUuid(slug);
    const userId = requireCurrentUserId();
    const res = await apiFetch<BackendChatHistoryResponse>("/chat/history", {
      query: { user_id: userId, character_id: uuid, limit: 100 },
    });
    return res.messages.map((m) => ({
      from: m.role === "assistant" ? "bot" : "user",
      text: m.content,
    }));
  },

  streamChat(input: ChatRequest): AsyncIterable<ChatStreamEvent> {
    return streamChatReal(input);
  },
};

async function* streamChatReal(
  input: ChatRequest,
): AsyncGenerator<ChatStreamEvent> {
  const uuid = await resolveSlugToUuid(input.characterId);
  const userId = requireCurrentUserId();
  const url = new URL("/api/v1/chat/stream", API_BASE_URL).toString();

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({
        user_id: userId,
        character_id: uuid,
        message: input.message,
      }),
      signal: input.signal,
    });
  } catch (err) {
    throw new ApiError(
      "Không kết nối được tới máy chủ trò chuyện.",
      0,
      err,
    );
  }

  if (!response.ok || !response.body) {
    let detail = `HTTP ${response.status}`;
    try {
      const payload = await response.json();
      if (payload?.detail) detail = String(payload.detail);
    } catch {
      // ignore
    }
    handleSessionExpired(response.status, detail);
    throw new ApiError(detail, response.status);
  }

  for await (const event of readSseStream(response.body, input.signal)) {
    if (event.event === "sources") {
      try {
        const payload = JSON.parse(event.data) as BackendSourcesPayload;
        const sources = payload.sources ?? [];
        for (const raw of sources) {
          const fe = backendSourceToFe(raw);
          if (fe) yield { kind: "source", source: fe };
        }
      } catch {
        // Malformed sources payload — ignore and keep streaming tokens.
      }
      continue;
    }
    if (event.event === "error") {
      let detail = event.data;
      try {
        const parsed = JSON.parse(event.data);
        detail = parsed.error ?? event.data;
      } catch { /* use raw */ }
      console.error("SSE error event from backend:", detail);
      throw new ApiError(detail, 500);
    }
    if (event.event === "message" && event.data) {
      yield { kind: "token", text: event.data };
    }
  }
  yield { kind: "done" };
}
