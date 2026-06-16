import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { useAppStore } from "@/stores/useAppStore";
import {
  CHALLENGE_MUSIC_TRACK,
  DEFAULT_TRACK_ID,
  MUSIC_LIBRARY,
} from "@/data/music";

export default function BackgroundMusic() {
  const { pathname } = useLocation();
  const enabled = useAppStore((s) => s.music.enabled);
  const trackId = useAppStore((s) => s.music.trackId);
  const volume = useAppStore((s) => s.music.volume);
  const isAuthRoute = pathname === "/onboarding" || pathname.startsWith("/auth/");
  const isChallengeRoute = pathname.includes("/challenge");

  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    audioRef.current = new Audio();
    audioRef.current.loop = true;
    audioRef.current.preload = "auto";
    return () => {
      audioRef.current?.pause();
      audioRef.current = null;
    };
  }, []);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.volume = volume;
  }, [volume]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isAuthRoute) {
      audio.pause();
      return;
    }

    const track = isChallengeRoute
      ? CHALLENGE_MUSIC_TRACK
      : (MUSIC_LIBRARY.find((t) => t.id === trackId) ??
        MUSIC_LIBRARY.find((t) => t.id === DEFAULT_TRACK_ID));
    if (!track) return;

    const expectedSrc = new URL(track.src, window.location.origin).toString();
    if (audio.src !== expectedSrc) {
      audio.src = track.src;
    }

    if (!enabled) {
      audio.pause();
      return;
    }

    audio.play().catch(() => {
      // Autoplay blocked — retry on first user gesture below.
    });

    const onUserGesture = () => {
      const a = audioRef.current;
      if (!a || !a.paused) return;
      a.play().catch(() => {});
    };
    window.addEventListener("pointerdown", onUserGesture);
    window.addEventListener("keydown", onUserGesture);
    return () => {
      window.removeEventListener("pointerdown", onUserGesture);
      window.removeEventListener("keydown", onUserGesture);
    };
  }, [enabled, isAuthRoute, isChallengeRoute, trackId]);

  return null;
}
