import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/api/client";
import { useAppStore } from "@/stores/useAppStore";
import { useLogout } from "./useLogout";

function LogoutHarness() {
  const { isLoggingOut, logout } = useLogout();

  return (
    <button type="button" onClick={logout} disabled={isLoggingOut}>
      {isLoggingOut ? "Đang đăng xuất" : "Đăng xuất"}
    </button>
  );
}

function renderLogoutHarness(queryClient = new QueryClient()) {
  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        initialEntries={["/profile"]}
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <Routes>
          <Route path="/profile" element={<LogoutHarness />} />
          <Route path="/onboarding" element={<p>Màn đăng nhập</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("useLogout", () => {
  beforeEach(() => {
    useAppStore.getState().resetAll();
    useAppStore.getState().setProfile("An", 10, "user-1", 120);
    useAppStore.getState().matchCharacter("chi-pheo");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("logs out, clears persisted app state, clears query cache, and redirects", async () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData(["leaderboard"], [{ name: "An" }]);
    vi.spyOn(api, "logout").mockResolvedValue({ ok: true });

    renderLogoutHarness(queryClient);

    fireEvent.click(screen.getByRole("button", { name: "Đăng xuất" }));

    expect(await screen.findByText("Màn đăng nhập")).toBeInTheDocument();
    expect(api.logout).toHaveBeenCalledOnce();
    expect(useAppStore.getState().profile).toBeNull();
    expect(useAppStore.getState().matches).toEqual([]);
    expect(queryClient.getQueryData(["leaderboard"])).toBeUndefined();
  });

  it("still clears local session when backend logout fails", async () => {
    vi.spyOn(api, "logout").mockRejectedValue(new Error("offline"));
    vi.spyOn(console, "warn").mockImplementation(() => {});

    renderLogoutHarness();

    fireEvent.click(screen.getByRole("button", { name: "Đăng xuất" }));

    await waitFor(() => {
      expect(screen.getByText("Màn đăng nhập")).toBeInTheDocument();
    });
    expect(console.warn).toHaveBeenCalledWith(
      "Logout request failed; clearing local session anyway.",
      expect.any(Error),
    );
    expect(useAppStore.getState().profile).toBeNull();
  });
});
