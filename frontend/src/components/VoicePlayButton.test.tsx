import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { characters } from "@/data/characters";
import VoicePlayButton from "./VoicePlayButton";

const newlyRecordedCharacterIds = [
  "lao-hac",
  "chi-dau",
  "ong-sau",
  "ong-hai",
  "vu-nuong",
] as const;

describe("VoicePlayButton", () => {
  it("uses each newly recorded character's own voice file", () => {
    vi.spyOn(window.HTMLMediaElement.prototype, "pause").mockImplementation(
      () => undefined,
    );

    for (const characterId of newlyRecordedCharacterIds) {
      const { container, unmount } = render(
        <VoicePlayButton characterId={characterId} />,
      );

      expect(container.querySelector("audio")?.getAttribute("src")).toBe(
        `/voices/${characterId}.wav`,
      );

      unmount();
    }
  });

  it("has a public voice file for every character id", () => {
    const missingVoiceFiles = characters
      .map((character) => {
        const voiceFile = resolve(
          process.cwd(),
          "public",
          "voices",
          `${character.id}.wav`,
        );

        return { characterId: character.id, path: voiceFile };
      })
      .filter(({ path }) => !existsSync(path));

    expect(missingVoiceFiles).toEqual([]);
  });
});
