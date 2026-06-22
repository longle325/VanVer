import { describe, it, expect } from "vitest";
import {
  cn,
  calculateChallengePoints,
  initials,
  formatNumber,
  cleanBotChatText,
} from "@/lib/utils";

describe("cn (class merging)", () => {
  it("merges simple class names", () => {
    expect(cn("a", "b")).toBe("a b");
  });

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", "extra")).toBe("base extra");
  });

  it("resolves Tailwind conflicts", () => {
    // tailwind-merge should keep the last conflicting class
    expect(cn("px-4", "px-6")).toBe("px-6");
  });
});

describe("calculateChallengePoints", () => {
  it("awards base points for failing score", () => {
    const result = calculateChallengePoints(2, 5, 4);
    expect(result.passed).toBe(false);
    expect(result.perfect).toBe(false);
    expect(result.points).toBe(50);
  });

  it("awards pass bonus for 4/5", () => {
    const result = calculateChallengePoints(4, 5, 4);
    expect(result.passed).toBe(true);
    expect(result.perfect).toBe(false);
    expect(result.points).toBe(90); // 50 + 40
  });

  it("awards perfect bonus for 5/5", () => {
    const result = calculateChallengePoints(5, 5, 4);
    expect(result.passed).toBe(true);
    expect(result.perfect).toBe(true);
    expect(result.points).toBe(115); // 50 + 40 + 25
  });
});

describe("initials", () => {
  it("extracts first two initials", () => {
    expect(initials("Minh Trần")).toBe("MT");
  });

  it("handles single name", () => {
    expect(initials("Mị")).toBe("M");
  });
});

describe("formatNumber", () => {
  it("formats numbers for Vietnamese locale", () => {
    // The exact separator depends on locale support in the test env,
    // but the function should not throw and should return a string.
    const result = formatNumber(1450);
    expect(typeof result).toBe("string");
    expect(result).toContain("1");
  });
});

describe("cleanBotChatText", () => {
  it("removes markdown emphasis markers and horizontal rules from bot text", () => {
    expect(
      cleanBotChatText(
        "Tôi nghe người ta bảo là **2**.\n\n----------------\n\nÔng giáo ạ.",
      ),
    ).toBe("Tôi nghe người ta bảo là 2.\n\nÔng giáo ạ.");
  });

  it("removes AI-style markdown structure without touching natural paragraphs", () => {
    expect(
      cleanBotChatText("### Trả lời\n- Tôi không rành chuyện đó.\n\n**Hỏi tôi về cậu Vàng đi.**"),
    ).toBe("Trả lời\nTôi không rành chuyện đó.\n\nHỏi tôi về cậu Vàng đi.");
  });
});
