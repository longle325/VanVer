import { useEffect, useRef } from "react";
import { useAppStore } from "@/stores/useAppStore";

const AUTH_MUSIC_SRC = "/audio/across-the-jade-valley.mp3";

export default function AuthBackgroundMusic() {
  const enabled = useAppStore((s) => s.music.enabled);
  const volume = useAppStore((s) => s.music.volume);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    audioRef.current = new Audio(AUTH_MUSIC_SRC);
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
  }, [enabled]);

  return null;
}
