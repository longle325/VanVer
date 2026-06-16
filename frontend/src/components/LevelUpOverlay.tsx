import { useEffect } from "react";
import { Sparkles, Star } from "lucide-react";
import type { Character } from "@/types";

const TOTAL_LEVELS = 3;

/**
 * Full-screen card-game-style "level up" reveal. Presentation-only: it reads
 * the character's per-level portraits and animates the completed-level image
 * brightening and crossfading into the next level's image while the star meter
 * gains one star. Dismissed by the continue button, which advances the flow.
 */
export default function LevelUpOverlay({
  character,
  completedLevel,
  unlockedLevel,
  onContinue,
}: {
  character: Character;
  completedLevel: 1 | 2 | 3;
  unlockedLevel: 2 | 3;
  onContinue: () => void;
}) {
  const levels = character.levels ?? [];
  const imageFor = (level: number): string =>
    levels.find((item) => item.level === level)?.image ||
    character.images?.[0] ||
    character.image ||
    "";

  const fromImage = imageFor(completedLevel);
  const toImage = imageFor(unlockedLevel) || fromImage;
  const nextTitle =
    levels.find((item) => item.level === unlockedLevel)?.title ??
    "Giai đoạn mới";

  // Play the level-up chime once when the reveal opens. This mounts directly
  // from the "Tiếp tục" click (a user gesture), so autoplay is permitted; if a
  // browser still blocks it, the reveal just plays silently.
  useEffect(() => {
    const audio = new Audio("/sounds/level-up.mp3");
    audio.volume = 0.55;
    void audio.play().catch(() => {});
    return () => {
      audio.pause();
      audio.currentTime = 0;
    };
  }, []);

  return (
    <div
      className="levelup-overlay"
      role="dialog"
      aria-modal="true"
      aria-label={`Lên cấp ${unlockedLevel}: ${nextTitle}`}
    >
      <div className="levelup-backdrop" />
      <div className="levelup-panel">
        <p className="levelup-kicker">
          <Sparkles size={16} />
          Lên cấp
          <Sparkles size={16} />
        </p>

        <div className="levelup-portrait">
          {fromImage && (
            <img className="levelup-img from" src={fromImage} alt="" aria-hidden />
          )}
          <img
            className="levelup-img to"
            src={toImage}
            alt={`${character.name} — Level ${unlockedLevel}`}
          />
          <span className="levelup-flare" aria-hidden />
        </div>

        <div
          className="levelup-stars"
          role="img"
          aria-label={`${unlockedLevel} trên ${TOTAL_LEVELS} sao`}
        >
          {Array.from({ length: TOTAL_LEVELS }, (_, i) => {
            const level = i + 1;
            const filled = level <= unlockedLevel;
            const gained = level === unlockedLevel;
            return (
              <span
                key={level}
                className={`levelup-star${filled ? " filled" : ""}${
                  gained ? " gained" : ""
                }`}
                aria-hidden
              >
                <Star
                  size={30}
                  strokeWidth={1.8}
                  fill={filled ? "currentColor" : "none"}
                />
              </span>
            );
          })}
        </div>

        <h2 className="levelup-title">
          Level {unlockedLevel}: {nextTitle}
        </h2>
        <p className="levelup-sub">
          Ảnh nhân vật của bạn đã chuyển sang giai đoạn mới.
        </p>

        <button
          type="button"
          className="btn primary levelup-continue"
          onClick={onContinue}
          autoFocus
        >
          Tiếp tục Level {unlockedLevel}
        </button>
      </div>
    </div>
  );
}
