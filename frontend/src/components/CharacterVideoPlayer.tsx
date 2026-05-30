import { useCallback, useEffect, useRef, useState } from "react";
import { Play, Pause, Maximize, Minimize } from "lucide-react";
import type { CharacterVideo } from "@/types";

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs.toString().padStart(2, "0")}`;
}

/**
 * Auto-hide for video controls: while `active` (i.e. playing) the controls
 * fade out after `delayMs` of no pointer activity, and any call to `wake`
 * (wired to mouse movement) reveals them and restarts the timer. Paused
 * videos always keep their controls visible.
 */
export function useIdleControls(active: boolean, delayMs = 3000) {
  const [hidden, setHidden] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clear = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  const wake = useCallback(() => {
    setHidden(false);
    clear();
    if (active) {
      timerRef.current = setTimeout(() => setHidden(true), delayMs);
    }
  }, [active, delayMs]);

  useEffect(() => {
    if (active) {
      wake();
    } else {
      clear();
      setHidden(false);
    }
    return clear;
  }, [active, wake]);

  return { hidden, wake };
}

/**
 * Custom video player with a centered play/pause button (showing the live
 * playback state), a seek bar, and a centered time readout. Used both in the
 * Discover gallery and at the bottom of the character profile.
 *
 * `isActive` lets the gallery pause the video when its slide scrolls out of
 * view. When `controlsHidden`/`onPlayingChange` are supplied the parent owns
 * the auto-hide (so it can fade the gallery arrows in sync); otherwise the
 * player auto-hides its own button.
 */
export default function CharacterVideoPlayer({
  video,
  isActive = true,
  controlsHidden,
  onPlayingChange,
}: {
  video: CharacterVideo;
  isActive?: boolean;
  controlsHidden?: boolean;
  onPlayingChange?: (playing: boolean) => void;
}) {
  const ref = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    const onChange = () => setIsFullscreen(Boolean(document.fullscreenElement));
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);

  const toggleFullscreen = () => {
    if (document.fullscreenElement) {
      void document.exitFullscreen();
    } else {
      void containerRef.current?.requestFullscreen();
    }
  };

  const controlled = controlsHidden !== undefined;
  const internal = useIdleControls(controlled ? false : playing);
  const hidden = controlled ? controlsHidden : internal.hidden;

  useEffect(() => {
    const el = ref.current;
    if (!isActive && el && !el.paused) {
      el.pause();
    }
  }, [isActive]);

  const setPlayState = (next: boolean) => {
    setPlaying(next);
    onPlayingChange?.(next);
  };

  const toggle = () => {
    const el = ref.current;
    if (!el) return;
    if (el.paused) {
      void el.play();
    } else {
      el.pause();
    }
  };

  const seek = (event: React.ChangeEvent<HTMLInputElement>) => {
    const el = ref.current;
    if (!el || !duration) return;
    el.currentTime = (Number(event.target.value) / 100) * duration;
  };

  const progress = duration ? (current / duration) * 100 : 0;

  // Stop the deck's swipe handler from hijacking video / control interaction.
  const stopSwipe = (event: React.PointerEvent) => event.stopPropagation();

  return (
    <div
      ref={containerRef}
      className="video-player"
      onPointerDown={stopSwipe}
      onMouseMove={controlled ? undefined : internal.wake}
    >
      <video
        ref={ref}
        playsInline
        preload="metadata"
        poster={video.poster}
        aria-label={video.title}
        onClick={toggle}
        onPlay={() => setPlayState(true)}
        onPause={() => setPlayState(false)}
        onTimeUpdate={(event) => setCurrent(event.currentTarget.currentTime)}
        onLoadedMetadata={(event) => setDuration(event.currentTarget.duration)}
      >
        <source src={video.src} type="video/mp4" />
        {video.captions && (
          <track
            kind="subtitles"
            src={video.captions}
            srcLang="vi"
            label="Tiếng Việt"
            default
          />
        )}
      </video>

      <button
        type="button"
        className={`video-toggle${playing ? " is-playing" : ""}${hidden ? " is-hidden" : ""}`}
        aria-label={playing ? "Tạm dừng video" : "Phát video"}
        aria-hidden={hidden}
        tabIndex={hidden ? -1 : 0}
        onClick={toggle}
      >
        {playing ? <Pause size={26} /> : <Play size={26} />}
      </button>

      <div className="video-bar">
        <input
          type="range"
          className="video-seek"
          min={0}
          max={100}
          step={0.1}
          value={progress}
          onChange={seek}
          aria-label="Thanh thời gian video"
        />
        <span className="video-time">
          {formatTime(current)} / {formatTime(duration)}
        </span>
        <button
          type="button"
          className="video-fullscreen"
          aria-label={isFullscreen ? "Thoát toàn màn hình" : "Xem toàn màn hình"}
          onClick={toggleFullscreen}
        >
          {isFullscreen ? <Minimize size={18} /> : <Maximize size={18} />}
        </button>
      </div>
    </div>
  );
}
