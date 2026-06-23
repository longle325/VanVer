import { afterEach, describe, expect, it, vi } from "vitest";
import { getOAuthLoginUrl } from "./realClient";

describe("getOAuthLoginUrl", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("keeps local OAuth redirects on localhost when the app is opened on 127.0.0.1", () => {
    vi.stubGlobal("window", {
      location: {
        origin: "http://127.0.0.1:5173",
        pathname: "/",
      },
    });

    const loginUrl = new URL(getOAuthLoginUrl("google", "/discover"));

    expect(loginUrl.origin).toBe("http://localhost:8081");
    expect(loginUrl.searchParams.get("next")).toBe(
      "http://localhost:5173/#/discover",
    );
  });
});
