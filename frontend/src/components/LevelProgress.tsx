import { Check, Lock } from "lucide-react";
import {
  getActiveChallengeLevel,
  getLevelResult,
  type LevelResults,
} from "@/lib/characterLevels";
import type { Character } from "@/types";

const LEVELS = [1, 2, 3] as const;

type StepState = "done" | "active" | "locked";

/**
 * Presentation-only stepper that renders a character's three phase levels as
 * done / active / locked. Reads level state through the existing
 * `characterLevels` helpers — it never mutates progression or scoring.
 *
 * - `compact` renders numbered dots only (for tight surfaces like the
 *   Collection card); phase titles move into the dot `title`/`aria-label`.
 * - default renders dots with their phase titles (Challenge header, Profile).
 */
export default function LevelProgress({
  character,
  levelResults,
  compact = false,
  className,
}: {
  character: Character;
  levelResults: LevelResults;
  compact?: boolean;
  className?: string;
}) {
  const challenges = character.levelChallenges;
  if (!challenges?.length) return null;

  const active = getActiveChallengeLevel(character, levelResults);

  return (
    <ol
      className={`level-progress${compact ? " compact" : ""}${
        className ? ` ${className}` : ""
      }`}
      aria-label="Tiến trình ba giai đoạn"
    >
      {LEVELS.map((level) => {
        const challenge = challenges.find((item) => item.level === level);
        if (!challenge) return null;

        const passed = Boolean(
          getLevelResult(levelResults, character.id, level)?.passed,
        );
        const state: StepState = passed
          ? "done"
          : level === active
            ? "active"
            : "locked";
        const phaseTitle =
          character.levels?.find((item) => item.level === level)?.title ??
          challenge.phaseTitle;
        const stateLabel =
          state === "done"
            ? "đã hoàn thành"
            : state === "active"
              ? "đang thực hiện"
              : "chưa mở khóa";

        return (
          <li
            key={level}
            className={`level-step ${state}`}
            aria-current={state === "active" ? "step" : undefined}
            title={`Giai đoạn ${level}: ${phaseTitle} (${stateLabel})`}
          >
            <span className="level-step-dot" aria-hidden="true">
              {state === "done" ? (
                <Check size={compact ? 13 : 15} strokeWidth={2.5} />
              ) : state === "locked" ? (
                <Lock size={compact ? 11 : 13} strokeWidth={2.2} />
              ) : (
                level
              )}
            </span>
            {!compact && (
              <span className="level-step-body">
                <span className="level-step-kicker">Giai đoạn {level}</span>
                <span className="level-step-title">{phaseTitle}</span>
              </span>
            )}
            <span className="sr-only">
              Giai đoạn {level}: {phaseTitle} — {stateLabel}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
