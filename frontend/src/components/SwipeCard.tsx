import { useEffect, useRef, useState } from "react";
import {
  motion,
  useMotionValue,
  useTransform,
  animate,
  useReducedMotion,
  type PanInfo,
} from "framer-motion";
import CharacterCard from "@/components/CharacterCard";
import type { Character } from "@/types";

export type SwipeDirection = "left" | "right";

// Commit thresholds. A swipe commits when the card is either dragged past
// COMMIT_DISTANCE, or flicked: a non-trivial offset plus enough projected
// power. The MIN_FLICK_OFFSET gate stops a near-zero-offset trackpad flick from
// firing an accidental swipe.
const COMMIT_DISTANCE = 110;
const MIN_FLICK_OFFSET = 40;
const COMMIT_POWER = 120;
const VELOCITY_WEIGHT = 0.2;
const FLY_DURATION = 0.28;

interface Props {
  character: Character;
  /** A match/skip mutation is in flight. */
  busy: boolean;
  onSwipe: (direction: SwipeDirection) => void;
}

/**
 * One draggable Tinder-style card built on framer-motion. The parent mounts it
 * with `key={character.id}`, so each card gets fresh motion values starting at
 * x=0 — no manual reset between cards.
 */
export default function SwipeCard({ character, busy, onSwipe }: Props) {
  const prefersReducedMotion = useReducedMotion();
  const x = useMotionValue(0);
  // Rotate the card as it travels, and fade the "skip"/"match" stamps in.
  const rotate = useTransform(x, [-240, 0, 240], [-14, 0, 14]);
  const skipStampOpacity = useTransform(x, [-110, -30], [1, 0]);
  const matchStampOpacity = useTransform(x, [30, 110], [0, 1]);

  // A committed card is flying off-screen; lock drag + buttons until it either
  // unmounts (mutation succeeded → deck advanced) or recovers (mutation failed).
  const [exiting, setExiting] = useState(false);
  const committed = useRef(false);
  const sawBusy = useRef(false);

  const flyOff = (direction: SwipeDirection) => {
    if (committed.current || busy || exiting) return;
    committed.current = true;
    setExiting(true);
    const commit = () => onSwipe(direction);
    if (prefersReducedMotion) {
      commit();
      return;
    }
    const offscreen =
      (direction === "right" ? 1 : -1) *
      (typeof window !== "undefined" ? window.innerWidth : 1000);
    // Commit once the card has flown off — and also on cancellation, so a swipe
    // is never silently dropped if the animation is interrupted.
    animate(x, offscreen, {
      type: "tween",
      ease: "easeOut",
      duration: FLY_DURATION,
    }).then(commit, commit);
  };

  // Recover from a failed mutation. The deck only advances (unmounting this
  // card) when recordMatch/recordSkip succeeds. If our swipe's mutation settles
  // while this same card is still mounted, it failed — reset so the user can
  // retry instead of being left with a dead, off-screen card.
  useEffect(() => {
    if (sawBusy.current && !busy && committed.current) {
      committed.current = false;
      setExiting(false);
      animate(x, 0, { type: "spring", stiffness: 320, damping: 32 });
    }
    sawBusy.current = busy;
  }, [busy, x]);

  const handleDragEnd = (_: PointerEvent, info: PanInfo) => {
    const { offset, velocity } = info;
    const power = offset.x + velocity.x * VELOCITY_WEIGHT;
    const draggedFar = Math.abs(offset.x) > COMMIT_DISTANCE;
    const flicked =
      Math.abs(offset.x) > MIN_FLICK_OFFSET && Math.abs(power) > COMMIT_POWER;
    if (draggedFar || flicked) {
      flyOff(power > 0 ? "right" : "left");
    } else {
      // Didn't reach the threshold — ease back to centre.
      animate(x, 0, { type: "spring", stiffness: 320, damping: 32 });
    }
  };

  const locked = busy || exiting;

  return (
    <motion.div
      className="deck-tinder"
      style={{ x, rotate, transformOrigin: "50% 92%" }}
      drag={locked ? false : "x"}
      dragSnapToOrigin={false}
      dragMomentum={false}
      onDragEnd={handleDragEnd}
    >
      <CharacterCard
        character={character}
        busy={locked}
        skipStampOpacity={skipStampOpacity}
        matchStampOpacity={matchStampOpacity}
        onSkip={() => flyOff("left")}
        onMatch={() => flyOff("right")}
      />
    </motion.div>
  );
}
