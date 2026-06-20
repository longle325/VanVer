import { describe, expect, it } from "vitest";
import { characters } from "@/data/characters";

describe("character symbol labels", () => {
  it("uses readable labels for Mi's important symbols", () => {
    const mi = characters.find((character) => character.id === "mi");

    expect(mi?.symbols).toEqual([
      "Căn buồng",
      "Tiếng sáo",
      "Dòng nước mắt A Phủ",
    ]);
    expect(mi?.symbols).not.toEqual(["Căn", "Tiếng", "Dòng"]);
  });
});
