import { describe, expect, it } from "vitest";
import { getCharacter } from "@/data/characters";
import { hasCharacterVideo } from "@/data/characterVideos";

describe("character video previews", () => {
  it("attaches conventional three-phase videos for characters in the manifest", () => {
    expect(getCharacter("mi")?.videos?.[0]).toMatchObject({
      id: "three-phase-demo",
      title: "Hành trình ba giai đoạn của Mị",
      src: "/character-videos/mi/mi-three-phase-demo.mp4",
    });

    expect(getCharacter("chi-dau")?.videos?.[0]).toMatchObject({
      src: "/character-videos/chi-dau/chi-dau-three-phase-demo.mp4",
      captions: "/character-videos/chi-dau/chi-dau-three-phase-demo.vtt",
    });

    expect(getCharacter("lao-hac")?.videos?.[0]).toMatchObject({
      src: "/character-videos/lao-hac/lao-hac-three-phase-demo.mp4",
      captions: "/character-videos/lao-hac/lao-hac-three-phase-demo.vtt",
    });
  });

  it("does not invent video previews for characters without generated assets", () => {
    expect(hasCharacterVideo("chi-pheo")).toBe(false);
    expect(getCharacter("chi-pheo")?.videos).toEqual([]);
  });
});
