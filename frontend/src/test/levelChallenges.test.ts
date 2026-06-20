import { describe, expect, it } from "vitest";
import { getCharacter } from "@/data/characters";
import { levelChallengeMap } from "@/data/levelChallenges";
import { getLevelProgressPercent, type LevelResults } from "@/lib/characterLevels";
import { scoreLevelChallenge } from "@/lib/scoring";
import type { ChallengeResult } from "@/types";

const coveredCharacters = [
  "chi-pheo",
  "mi",
  "xuan-toc-do",
  "luc-van-tien",
  "thuy-kieu",
  "lao-hac",
  "chi-dau",
  "ong-sau",
  "ong-hai",
  "vu-nuong",
] as const;

describe("level challenge data", () => {
  it("loads three five-question phases for the workbook-backed characters", () => {
    for (const characterId of coveredCharacters) {
      const character = getCharacter(characterId);
      expect(character?.levelChallenges).toHaveLength(3);
      expect(levelChallengeMap[characterId]).toHaveLength(3);

      for (const challenge of character?.levelChallenges ?? []) {
        expect(challenge.questions).toHaveLength(5);
        expect(
          challenge.questions.filter((q) => q.type === "multiple_choice"),
        ).toHaveLength(4);
        expect(
          challenge.questions.filter((q) => q.type === "open_ended"),
        ).toHaveLength(1);
      }
    }
  });

  it("scores MCQs and non-empty rubric answers for one level", () => {
    const challenge = levelChallengeMap["chi-pheo"][0];
    const result = scoreLevelChallenge(challenge, [
      challenge.questions[0].answer,
      challenge.questions[1].answer,
      challenge.questions[2].answer,
      challenge.questions[3].answer,
      "Quá khứ lương thiện làm bi kịch nặng hơn vì Chí từng có khả năng sống như một người bình thường.",
    ]);

    expect(result).toMatchObject({
      level: 1,
      score: 5,
      total: 5,
      passed: true,
      perfect: true,
      nextLevelUnlocked: 2,
    });
  });

  it("uses explicit open-ended grader results when they are provided", () => {
    const challenge = levelChallengeMap["chi-pheo"][0];
    const openQuestion = challenge.questions.find(
      (question) => question.type === "open_ended",
    );
    expect(openQuestion).toBeDefined();

    const result = scoreLevelChallenge(
      challenge,
      [
        challenge.questions[0].answer,
        challenge.questions[1].answer,
        challenge.questions[2].answer,
        challenge.questions[3].answer,
        "Một câu trả lời dài nhưng chưa đạt rubric.",
      ],
      {
        [openQuestion!.id]: {
          score: 0,
          passed: false,
          feedback: "Thiếu tiêu chí cốt lõi.",
          matchedCriteria: [],
          missingCriteria: ["Cần nêu tha hóa không phải bản chất bẩm sinh."],
          confidence: 0.92,
          retrievalMode: "vector",
        },
      },
    );

    expect(result.score).toBe(4);
    expect(result.perfect).toBe(false);
    expect(result.openGrades?.[openQuestion!.id]?.passed).toBe(false);
  });

  it("counts completed levels for collection exploration progress", () => {
    const character = getCharacter("chi-pheo");
    expect(character).toBeDefined();

    const passedResult: ChallengeResult = {
      score: 5,
      total: 5,
      passed: true,
      perfect: true,
      awarded: 115,
      answers: [],
    };
    const failedResult: ChallengeResult = {
      score: 3,
      total: 5,
      passed: false,
      perfect: false,
      awarded: 50,
      answers: [],
    };

    const noLevels: LevelResults = {};
    const onePassed: LevelResults = {
      "chi-pheo": { 1: passedResult },
    };
    const twoPassed: LevelResults = {
      "chi-pheo": { 1: passedResult, 2: passedResult },
    };
    const allPassed: LevelResults = {
      "chi-pheo": {
        1: passedResult,
        2: passedResult,
        3: passedResult,
      },
    };
    const failedOnly: LevelResults = {
      "chi-pheo": { 1: failedResult },
    };

    expect(getLevelProgressPercent(character!, noLevels)).toBe(0);
    expect(getLevelProgressPercent(character!, failedOnly)).toBe(0);
    expect(getLevelProgressPercent(character!, onePassed)).toBe(33);
    expect(getLevelProgressPercent(character!, twoPassed)).toBe(67);
    expect(getLevelProgressPercent(character!, allPassed)).toBe(100);
  });
});
