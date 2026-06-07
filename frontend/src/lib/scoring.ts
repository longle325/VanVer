import type {
  Character,
  CharacterLevelChallenge,
  ChallengeResult,
  OpenEndedGradeResult,
} from "@/types";

export const PASS_THRESHOLD = 4;
export const POINTS_PER_MATCH = 10;
export const POINTS_PER_COMPLETION = 50;
export const POINTS_PASS_BONUS = 40;
export const POINTS_PER_LEVEL_COMPLETION = 30;
export const POINTS_LEVEL_PASS_BONUS = 20;

export function scoreChallenge(
  character: Character,
  answers: number[],
): ChallengeResult {
  const score = character.challenge.reduce(
    (total, question, index) =>
      total + (answers[index] === question.answer ? 1 : 0),
    0,
  );
  const passed = score >= PASS_THRESHOLD;
  const perfect = score === character.challenge.length;
  const awarded =
    POINTS_PER_COMPLETION + (passed ? POINTS_PASS_BONUS : 0);
  return {
    score,
    total: character.challenge.length,
    passed,
    perfect,
    awarded,
    answers: [...answers],
    correctAnswers: character.challenge.map((q) => q.answer),
  };
}

export function scoreLevelChallenge(
  challenge: CharacterLevelChallenge,
  answers: Array<number | string>,
  openGrades?: Record<string, OpenEndedGradeResult>,
): ChallengeResult {
  const correctAnswers: number[] = [];
  const openResponses: Record<string, string> = {};
  const resolvedOpenGrades: Record<string, OpenEndedGradeResult> = {};
  let score = 0;

  challenge.questions.forEach((question, index) => {
    const answer = answers[index];
    if (question.type === "open_ended") {
      const response = typeof answer === "string" ? answer.trim() : "";
      const grade = openGrades?.[question.id];
      if (grade) {
        if (grade.score === 1) score += 1;
        resolvedOpenGrades[question.id] = grade;
      } else if (openGrades === undefined && response) {
        score += 1;
      }
      openResponses[question.id] = response;
      correctAnswers[index] = -1;
      return;
    }

    correctAnswers[index] = question.answer;
    if (answer === question.answer) {
      score += 1;
    }
  });

  const total = challenge.questions.length;
  const passed = score >= PASS_THRESHOLD;
  const perfect = score === total;
  const nextLevelUnlocked =
    passed && challenge.level < 3
      ? ((challenge.level + 1) as 2 | 3)
      : undefined;

  return {
    level: challenge.level,
    phaseTitle: challenge.phaseTitle,
    score,
    total,
    passed,
    perfect,
    awarded:
      POINTS_PER_LEVEL_COMPLETION + (passed ? POINTS_LEVEL_PASS_BONUS : 0),
    answers: [...answers],
    correctAnswers,
    openResponses,
    openGrades: resolvedOpenGrades,
    nextLevelUnlocked,
  };
}
