import { X, Heart, Scale } from "lucide-react";
import { motion, type MotionValue } from "framer-motion";
import type { Character } from "@/types";
import CharacterArt from "./CharacterArt";
import VoicePlayButton from "./VoicePlayButton";

interface Props {
  character: Character;
  onSkip: () => void;
  onMatch: () => void;
  /** When true (mutation in flight) the action buttons are disabled to
   *  prevent fast double-taps on trackpads from firing the swipe twice. */
  busy?: boolean;
  /** Drag-driven opacity for the "skip"/"match" stamps. Supplied by SwipeCard
   *  so the stamps fade in as the card is dragged; omitted when the card is
   *  rendered statically. */
  skipStampOpacity?: MotionValue<number>;
  matchStampOpacity?: MotionValue<number>;
}

export default function CharacterCard({
  character,
  onSkip,
  onMatch,
  busy = false,
  skipStampOpacity,
  matchStampOpacity,
}: Props) {
  const traits = character.personality
    .split(",")
    .slice(0, 3)
    .map((trait) => trait.trim());
  return (
    <article className="card deck-card">
      <motion.div
        className="swipe-stamp swipe-stamp-left"
        style={skipStampOpacity ? { opacity: skipStampOpacity } : undefined}
        aria-hidden="true"
      >
        Bỏ qua
      </motion.div>
      <motion.div
        className="swipe-stamp swipe-stamp-right"
        style={matchStampOpacity ? { opacity: matchStampOpacity } : undefined}
        aria-hidden="true"
      >
        Chọn
      </motion.div>
      <CharacterArt character={character} />
      <div className="deck-body">
        <div className="deck-title">
          <h1 className="headline-lg">{character.name}</h1>
          <p>
            {character.work} · {character.author}
          </p>
        </div>
        <div className="quote-row">
          <blockquote className="quote">"{character.quote}"</blockquote>
          <VoicePlayButton characterId={character.id} size="sm" />
        </div>
        <p className="deck-bio">{character.bio}</p>
        <div className="conflict-tile">
          <span>Xung đột</span>
          <strong>
            <Scale size={16} style={{ display: "inline", verticalAlign: "middle", marginRight: 4 }} />
            {character.conflict.split(";")[0]}
          </strong>
        </div>
        <div className="trait-row">
          {traits.map((trait) => (
            <span key={trait}>{trait}</span>
          ))}
        </div>
      </div>
      <div className="swipe-actions">
        <button
          className="btn circle ghost"
          aria-label="Bỏ qua"
          onClick={onSkip}
          disabled={busy}
        >
          <X size={24} />
        </button>
        <button
          className="btn circle primary"
          aria-label="Chọn nhân vật"
          onClick={onMatch}
          disabled={busy}
        >
          <Heart size={24} />
        </button>
      </div>
    </article>
  );
}
