import { useMemo, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { Character, CharacterVideo } from "@/types";
import CharacterVideoPlayer, { useIdleControls } from "./CharacterVideoPlayer";

type CharacterMedia =
  | { type: "image"; src: string; alt: string }
  | { type: "video"; key: string; video: CharacterVideo };

export default function CharacterArt({ character }: { character: Character }) {
  const media = useMemo<CharacterMedia[]>(() => {
    const images = character.images?.length
      ? character.images
      : character.image
        ? [character.image]
        : [];
    const imageItems: CharacterMedia[] = images.map((src, index) => ({
      type: "image",
      src,
      alt:
        images.length > 1
          ? `${character.name} - ảnh ${index + 1}/${images.length}`
          : character.name,
    }));
    const videoItems: CharacterMedia[] = (character.videos ?? []).map(
      (video) => ({
        type: "video",
        key: video.id,
        video,
      }),
    );
    return [...imageItems, ...videoItems];
  }, [character.image, character.images, character.name, character.videos]);

  const [active, setActive] = useState(0);
  const hasGallery = media.length > 1;
  const activeMedia = media[active];
  const isVideoActive = activeMedia?.type === "video";

  // Auto-hide the slide arrows + play button while the video plays; mouse
  // movement anywhere over the card reveals them again.
  const [videoPlaying, setVideoPlaying] = useState(false);
  const { hidden: controlsHidden, wake } = useIdleControls(videoPlaying);

  const showPrevious = () => {
    setActive((current) => (current === 0 ? media.length - 1 : current - 1));
  };

  const showNext = () => {
    setActive((current) => (current + 1) % media.length);
  };

  if (media.length) {
    return (
      <div
        className={`art image-art${hasGallery ? " profile-gallery" : ""}`}
        onMouseMove={wake}
      >
        <div
          className="gallery-track"
          style={
            {
              "--active-image": active,
            } as React.CSSProperties
          }
        >
          {media.map((item, index) =>
            item.type === "image" ? (
              <img key={`img-${item.src}`} src={item.src} alt={item.alt} />
            ) : (
              <div key={`vid-${item.key}`} className="gallery-video">
                <CharacterVideoPlayer
                  video={item.video}
                  isActive={index === active}
                  controlsHidden={controlsHidden}
                  onPlayingChange={setVideoPlaying}
                />
              </div>
            ),
          )}
        </div>
        <span className="tag">{character.genre || "Kinh điển"}</span>
        {hasGallery && (
          <>
            {/* The wide invisible click zones would cover the native video
                controls, so only mount them while an image is showing. */}
            {!isVideoActive && (
              <>
                <button
                  type="button"
                  className="gallery-zone gallery-zone-left"
                  aria-label="Xem mục trước"
                  onClick={showPrevious}
                />
                <button
                  type="button"
                  className="gallery-zone gallery-zone-right"
                  aria-label="Xem mục tiếp theo"
                  onClick={showNext}
                />
              </>
            )}
            <div
              className={`gallery-controls${isVideoActive ? " gallery-controls-video" : ""}${isVideoActive && controlsHidden ? " controls-hidden" : ""}`}
              aria-label="Ảnh và video nhân vật"
            >
              <button
                type="button"
                className="gallery-arrow"
                aria-label="Mục trước"
                onClick={showPrevious}
              >
                <ChevronLeft size={20} />
              </button>
              <div className="gallery-dots" role="tablist">
                {media.map((item, index) => (
                  <button
                    key={`dot-${item.type}-${item.type === "image" ? item.src : item.key}`}
                    type="button"
                    className={index === active ? "active" : ""}
                    aria-label={
                      item.type === "video"
                        ? "Xem video"
                        : `Xem ảnh ${index + 1}`
                    }
                    aria-selected={index === active}
                    role="tab"
                    onClick={() => setActive(index)}
                  />
                ))}
              </div>
              <button
                type="button"
                className="gallery-arrow"
                aria-label="Mục tiếp theo"
                onClick={showNext}
              >
                <ChevronRight size={20} />
              </button>
            </div>
          </>
        )}
      </div>
    );
  }
  return (
    <div
      className="art"
      data-initial={character.initial}
      style={
        {
          "--art-a": character.artA,
          "--art-b": character.artB,
        } as React.CSSProperties
      }
    >
      <span className="tag">{character.genre || "Kinh điển"}</span>
      <div className="art-scene">
        <strong>{character.artTitle}</strong>
        <span>{character.imageBrief}</span>
      </div>
    </div>
  );
}
