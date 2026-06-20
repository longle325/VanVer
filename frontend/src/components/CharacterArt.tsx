import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { Character } from "@/types";

export default function CharacterArt({ character }: { character: Character }) {
  const images = character.images?.length
    ? character.images
    : character.image
      ? [character.image]
      : [];

  const [active, setActive] = useState(0);
  const hasGallery = images.length > 1;

  const showPrevious = () => {
    setActive((current) => (current === 0 ? images.length - 1 : current - 1));
  };

  const showNext = () => {
    setActive((current) => (current + 1) % images.length);
  };

  if (images.length) {
    return (
      <div className={`art image-art${hasGallery ? " profile-gallery" : ""}`}>
        <div
          className="gallery-track"
          style={
            {
              "--active-image": active,
            } as React.CSSProperties
          }
        >
          {images.map((src, index) => (
            <img
              key={`img-${src}`}
              src={src}
              loading={index === 0 ? "eager" : "lazy"}
              decoding="async"
              alt={
                images.length > 1
                  ? `${character.name} - ảnh ${index + 1}/${images.length}`
                  : character.name
              }
            />
          ))}
        </div>
        <span className="tag">{character.genre || "Kinh điển"}</span>
        {hasGallery && (
          <>
            <button
              type="button"
              className="gallery-zone gallery-zone-left"
              aria-label="Xem ảnh trước"
              onClick={showPrevious}
            />
            <button
              type="button"
              className="gallery-zone gallery-zone-right"
              aria-label="Xem ảnh tiếp theo"
              onClick={showNext}
            />
            <div className="gallery-controls" aria-label="Ảnh nhân vật">
              <button
                type="button"
                className="gallery-arrow"
                aria-label="Ảnh trước"
                onClick={showPrevious}
              >
                <ChevronLeft size={20} />
              </button>
              <div className="gallery-dots" role="tablist">
                {images.map((src, index) => (
                  <button
                    key={`dot-${src}`}
                    type="button"
                    className={index === active ? "active" : ""}
                    aria-label={`Xem ảnh ${index + 1}`}
                    aria-selected={index === active}
                    role="tab"
                    onClick={() => setActive(index)}
                  />
                ))}
              </div>
              <button
                type="button"
                className="gallery-arrow"
                aria-label="Ảnh tiếp theo"
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
