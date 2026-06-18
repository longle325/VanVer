import type {
  Character,
  ChallengeQuestion,
  ChallengeResult,
  ChatMessage,
  ChatSource,
  Grade,
  LeaderboardEntry,
  OpenEndedGradeRequest,
  OpenEndedGradeResult,
  SyncedProgress,
  UserProfile,
} from "@/types";

export interface CreateUserInput {
  username: string;
  grade: Grade;
}

export interface ChatRequest {
  characterId: string;
  message: string;
  signal?: AbortSignal;
}

/**
 * Streamed chat output. Mock yields plain text chunks; the real client
 * yields the same string events but may also emit a `source` event with
 * retrieval citations to attach to the message once the stream ends.
 */
export type ChatStreamEvent =
  | { kind: "token"; text: string }
  | { kind: "source"; source: ChatSource }
  | { kind: "done" };

export interface ApiClient {
  createUser: (input: CreateUserInput) => Promise<UserProfile>;
  getCurrentUser: () => Promise<UserProfile>;
  getDeck: () => Promise<Character[]>;
  /** Full character catalog. Unlike `getDeck` this is NOT filtered by
   *  the current user's swipes — Collection needs every matched
   *  character, including ones the backend deck endpoint already pruned. */
  getAllCharacters: () => Promise<Character[]>;
  getCharacter: (id: string) => Promise<Character>;
  recordMatch: (id: string) => Promise<{ ok: true }>;
  recordSkip: (id: string) => Promise<{ ok: true }>;
  /** Authoritative list of slugs the user has right-swiped on. Real
   *  backend reads `GET /users/{id}/matches`; mock returns []. */
  getMatchedSlugs: () => Promise<string[]>;
  getProgress: () => Promise<SyncedProgress>;
  saveProgress: (progress: SyncedProgress) => Promise<SyncedProgress>;
  getChallenge: (id: string) => Promise<ChallengeQuestion[]>;
  submitChallenge: (
    id: string,
    answers: number[],
  ) => Promise<ChallengeResult>;
  gradeOpenEndedAnswer: (
    input: OpenEndedGradeRequest,
  ) => Promise<OpenEndedGradeResult>;
  getLeaderboard: () => Promise<LeaderboardEntry[]>;
  getChatHistory: (characterId: string) => Promise<ChatMessage[]>;
  /**
   * Streams a character reply as structured events. Mock yields a sequence
   * of `token` events and ends; real backend additionally emits `source`
   * events with retrieval citations once at the start of the stream.
   */
  streamChat: (input: ChatRequest) => AsyncIterable<ChatStreamEvent>;
}
