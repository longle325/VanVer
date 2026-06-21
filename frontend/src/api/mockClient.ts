import { characters, getCharacter } from "@/data/characters";
import { demoLeaders } from "@/data/leaderboard";
import { scoreChallenge } from "@/lib/scoring";
import type {
  Character,
  ChallengeQuestion,
  ChallengeResult,
  LeaderboardEntry,
  OpenEndedGradeRequest,
  OpenEndedGradeResult,
  SyncedProgress,
  UserProfile,
} from "@/types";
import type {
  ApiClient,
  ChatRequest,
  ChatStreamEvent,
  CreateUserInput,
} from "./types";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function* mockStreamChat({
  characterId,
  message,
  signal,
}: ChatRequest): AsyncIterable<ChatStreamEvent> {
  const character = getCharacter(characterId);
  if (!character) throw new Error(`Unknown character: ${characterId}`);

  const reply = composeReply(character, message);
  const chunks = reply.match(/\S+\s*/g) ?? [reply];
  for (const chunk of chunks) {
    if (signal?.aborted) return;
    await delay(35);
    yield { kind: "token", text: chunk };
  }
  yield { kind: "done" };
}

function composeReply(character: Character, text: string): string {
  const lower = text.toLowerCase();
  if (
    lower.includes("essay") ||
    lower.includes("bài văn mẫu") ||
    lower.includes("viết bài")
  ) {
    return "Mình không tạo bài văn mẫu hoàn chỉnh. Mình có thể giúp bạn lập dàn ý, tìm luận điểm và dẫn chứng để bạn tự viết bằng giọng của mình.";
  }
  if (lower.includes("không rõ") || lower.includes("ngoài tác phẩm")) {
    return "Phần này chưa có đủ nguồn trong bộ ghi chú hiện có, nên mình không khẳng định như sự thật văn bản. Ta có thể quay lại các chi tiết đã duyệt trước.";
  }
  const source =
    character.sources.find((item) =>
      lower
        .split(/\s+/)
        .some((word) => word.length > 3 && item.toLowerCase().includes(word)),
    ) ?? character.sources[0];
  return `Theo giọng của ${character.name}, câu trả lời nên xuất phát từ mâu thuẫn cốt lõi: ${character.conflict} Ghi chú nguồn liên quan: ${source} Đây là diễn giải học tập, không phải trích dẫn nguyên văn toàn bộ tác phẩm.`;
}

export const mockClient: ApiClient = {
  async createUser(input: CreateUserInput): Promise<UserProfile> {
    await delay(0);
    return {
      username: input.username,
      grade: input.grade,
      // Mock UUID so callers expecting `userId` still get a stable value.
      userId: `mock-${input.username}`,
    };
  },
  async getCurrentUser(): Promise<UserProfile> {
    await delay(0);
    return {
      username: "Demo",
      grade: 10,
      userId: "mock-demo",
    };
  },
  async updateDisplayName(input): Promise<UserProfile> {
    await delay(0);
    return {
      username: input.displayName.trim(),
      grade: 10,
      userId: `mock-${input.displayName.trim()}`,
    };
  },
  async logout(): Promise<{ ok: true }> {
    await delay(0);
    return { ok: true };
  },
  async getDeck(): Promise<Character[]> {
    await delay(0);
    return characters;
  },
  async getAllCharacters(): Promise<Character[]> {
    await delay(0);
    return characters;
  },
  async getCharacter(id: string): Promise<Character> {
    await delay(0);
    const character = getCharacter(id);
    if (!character) throw new Error(`Unknown character: ${id}`);
    return character;
  },
  async recordMatch(_id: string): Promise<{ ok: true }> {
    await delay(0);
    return { ok: true };
  },
  async recordSkip(_id: string): Promise<{ ok: true }> {
    await delay(0);
    return { ok: true };
  },
  async getMatchedSlugs(): Promise<string[]> {
    // Mock has no backend; the local Zustand `matches` array IS the
    // truth in this mode. Returning [] would falsely wipe it on sync,
    // so callers that respect the real/mock split must skip the
    // reconciliation entirely when in mock mode.
    return [];
  },
  async getProgress(): Promise<SyncedProgress> {
    await delay(0);
    return { completed: {}, levelResults: {}, skipped: [] };
  },
  async saveProgress(progress: SyncedProgress): Promise<SyncedProgress> {
    await delay(0);
    return progress;
  },
  async getChallenge(id: string): Promise<ChallengeQuestion[]> {
    await delay(0);
    const character = getCharacter(id);
    if (!character) throw new Error(`Unknown character: ${id}`);
    return character.challenge;
  },
  async submitChallenge(
    id: string,
    answers: number[],
  ): Promise<ChallengeResult> {
    await delay(0);
    const character = getCharacter(id);
    if (!character) throw new Error(`Unknown character: ${id}`);
    return scoreChallenge(character, answers);
  },
  async gradeOpenEndedAnswer(
    input: OpenEndedGradeRequest,
  ): Promise<OpenEndedGradeResult> {
    await delay(0);
    const hasAnswer = input.answer.trim().length > 0;
    return {
      score: hasAnswer ? 1 : 0,
      passed: hasAnswer,
      feedback: hasAnswer
        ? "Mock mode: câu trả lời có nội dung, được tính đạt."
        : "Mock mode: câu trả lời còn trống.",
      matchedCriteria: hasAnswer ? ["Có trả lời theo rubric."] : [],
      missingCriteria: hasAnswer ? [] : ["Cần trả lời theo rubric."],
      confidence: 1,
      retrievalMode: "mock",
    };
  },
  async getLeaderboard(): Promise<LeaderboardEntry[]> {
    await delay(0);
    return demoLeaders;
  },
  async getChatHistory(_characterId: string) {
    await delay(0);
    return [];
  },
  streamChat(input: ChatRequest) {
    return mockStreamChat(input);
  },
};
