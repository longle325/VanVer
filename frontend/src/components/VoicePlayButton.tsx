import { useEffect, useRef, useState } from "react";
import { PlayCircle, StopCircle } from "lucide-react";

interface Props {
  characterId: string;
  label?: string;
  size?: "sm" | "md";
}

export default function VoicePlayButton({
  characterId,
  label = "Nghe nhân vật",
  size = "md",
}: Props) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const [available, setAvailable] = useState(true);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onEnd = () => setPlaying(false);
    const onErr = () => {
      setPlaying(false);
      setAvailable(false);
    };
    audio.addEventListener("ended", onEnd);
    audio.addEventListener("error", onErr);
    return () => {
      audio.removeEventListener("ended", onEnd);
      audio.removeEventListener("error", onErr);
      audio.pause();
    };
  }, []);

  const toggle = () => {
    const audio = audioRef.current;
    if (!audio || !available) return;
    if (playing) {
      audio.pause();
      audio.currentTime = 0;
      setPlaying(false);
      return;
    }
    audio.currentTime = 0;
    audio
      .play()
      .then(() => setPlaying(true))
      .catch(() => {
        setPlaying(false);
        setAvailable(false);
      });
  };

  if (!available) return null;

  return (
    <>
      <button
        type="button"
        className={`voice-play-button ${size} ${playing ? "playing" : ""}`}
        onClick={toggle}
        aria-label={playing ? "Tạm dừng" : label}
        title={playing ? "Tạm dừng" : label}
      >
        {playing ? <StopCircle size={size === "sm" ? 18 : 22} /> : <PlayCircle size={size === "sm" ? 18 : 22} />}
      </button>
      <audio
        ref={audioRef}
        src={`/voices/${characterId}.wav`}
        preload="none"
      />
    </>
  );
}
