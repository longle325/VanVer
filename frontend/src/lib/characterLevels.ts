import type { Character, ChallengeResult, CharacterLevel } from "@/types";

export type LevelResults = Record<string, Partial<Record<1 | 2 | 3, ChallengeResult>>>;

export function getLevelResult(
  levelResults: LevelResults,
  characterId: string,
  level: 1 | 2 | 3,
): ChallengeResult | undefined {
  return levelResults[characterId]?.[level];
}

export function getPassedLevelCount(
  character: Character,
  levelResults: LevelResults,
): number {
  if (!character.levelChallenges?.length) return 0;
  return character.levelChallenges.filter(
    (challenge) => getLevelResult(levelResults, character.id, challenge.level)?.passed,
  ).length;
}

export function getActiveChallengeLevel(
  character: Character,
  levelResults: LevelResults,
): 1 | 2 | 3 {
  const challenges = character.levelChallenges;
  if (!challenges?.length) return 1;

  const next = challenges.find(
    (challenge) => !getLevelResult(levelResults, character.id, challenge.level)?.passed,
  );
  return next?.level ?? 3;
}

export function getUnlockedCharacterLevel(
  character: Character,
  levelResults: LevelResults,
): 1 | 2 | 3 {
  if (!character.levelChallenges?.length) return 1;
  const passed = getPassedLevelCount(character, levelResults);
  return Math.min(3, passed + 1) as 1 | 2 | 3;
}

export function getCharacterLevel(
  character: Character,
  levelResults: LevelResults,
): CharacterLevel | undefined {
  const level = getUnlockedCharacterLevel(character, levelResults);
  return character.levels?.find((item) => item.level === level);
}

export function getLevelImages(
  character: Character,
  levelResults: LevelResults,
): string[] {
  const level = getCharacterLevel(character, levelResults);
  if (level?.images.length) return level.images;
  if (character.images?.length) return character.images;
  return character.image ? [character.image] : [];
}

export function getLevelProgressPercent(
  character: Character,
  levelResults: LevelResults,
  legacyResult?: ChallengeResult,
): number {
  const challenges = character.levelChallenges;
  if (!challenges?.length) {
    if (!legacyResult) return 0;
    return legacyResult.passed
      ? 100
      : Math.round((legacyResult.score / (legacyResult.total ?? 5)) * 100);
  }

  const passed = getPassedLevelCount(character, levelResults);
  return Math.min(100, Math.round((passed / challenges.length) * 100));
}
