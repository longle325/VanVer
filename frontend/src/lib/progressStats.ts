import type { ChallengeResult, LevelResultsState } from "@/types";

export function countAttemptedChallenges(
  completed: Record<string, ChallengeResult>,
  levelResults: LevelResultsState,
): number {
  const levelAttempts = Object.values(levelResults).reduce(
    (sum, results) => sum + Object.keys(results).length,
    0,
  );
  const legacyAttempts = Object.keys(completed).filter(
    (characterId) => !levelResults[characterId],
  ).length;

  return levelAttempts + legacyAttempts;
}

export function countPassedChallenges(
  completed: Record<string, ChallengeResult>,
  levelResults: LevelResultsState,
): number {
  const passedLevels = Object.values(levelResults).reduce(
    (sum, results) =>
      sum + Object.values(results).filter((result) => result?.passed).length,
    0,
  );
  const legacyPassed = Object.entries(completed).filter(
    ([characterId, result]) => !levelResults[characterId] && result.passed,
  ).length;

  return passedLevels + legacyPassed;
}
