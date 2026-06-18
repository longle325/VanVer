import { describe, expect, it } from "vitest";
import {
  countAttemptedChallenges,
  countPassedChallenges,
} from "@/lib/progressStats";
import type { ChallengeResult, LevelResultsState } from "@/types";

const result = (passed: boolean): ChallengeResult => ({
  score: passed ? 4 : 3,
  total: 5,
  passed,
  perfect: false,
  awarded: passed ? 50 : 30,
  answers: [],
});

describe("progressStats", () => {
  it("counts level challenge attempts", () => {
    const completed: Record<string, ChallengeResult> = {};
    const levelResults: LevelResultsState = {
      "xuan-toc-do": {
        1: result(false),
        2: result(true),
      },
      "chi-pheo": {
        1: result(true),
      },
    };

    expect(countAttemptedChallenges(completed, levelResults)).toBe(3);
  });

  it("does not double count aggregate completed entries", () => {
    const completed = {
      "xuan-toc-do": result(true),
      "legacy-character": result(true),
    };
    const levelResults: LevelResultsState = {
      "xuan-toc-do": {
        1: result(true),
        2: result(false),
      },
    };

    expect(countAttemptedChallenges(completed, levelResults)).toBe(3);
    expect(countPassedChallenges(completed, levelResults)).toBe(2);
  });
});
