import { describe, expect, it } from "vitest";
import { getCharacter } from "@/data/characters";
import { levelChallengeMap } from "@/data/levelChallenges";
import { scoreLevelChallenge } from "@/lib/scoring";

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
});
