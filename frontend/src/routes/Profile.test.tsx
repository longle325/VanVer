import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/api/client";
import { queryKeys } from "@/api/queries";
import { useAppStore } from "@/stores/useAppStore";
import Profile from "./Profile";

function renderProfile(queryClient = new QueryClient()) {
  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <Profile />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Profile", () => {
  beforeEach(() => {
    useAppStore.getState().resetAll();
    useAppStore.getState().setProfile("Student One", 10, "user-1", 120);
    vi.spyOn(window.HTMLMediaElement.prototype, "pause").mockImplementation(
      () => {},
    );
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("updates the display name and refreshes leaderboard data", async () => {
    const queryClient = new QueryClient();
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
    vi.spyOn(api, "updateDisplayName").mockResolvedValue({
      username: "Student Two",
      grade: 10,
      userId: "user-1",
      points: 120,
    });

    renderProfile(queryClient);

    fireEvent.change(screen.getByLabelText("Tên hiển thị"), {
      target: { value: "Student Two" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Lưu tên" }));

    await waitFor(() => {
      expect(api.updateDisplayName).toHaveBeenCalledWith({
        displayName: "Student Two",
      });
    });
    expect(useAppStore.getState().profile?.username).toBe("Student Two");
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: queryKeys.leaderboard,
    });
    expect(screen.getByText("Đã lưu tên hiển thị.")).toBeInTheDocument();
  });

  it("does not save an unchanged display name", () => {
    vi.spyOn(api, "updateDisplayName").mockResolvedValue({
      username: "Student One",
      grade: 10,
      userId: "user-1",
    });

    renderProfile();

    expect(screen.getByRole("button", { name: "Lưu tên" })).toBeDisabled();
  });
});
