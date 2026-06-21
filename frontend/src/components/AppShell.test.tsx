import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";
import { useAppStore } from "@/stores/useAppStore";
import AppShell from "./AppShell";

function renderShell() {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter
        initialEntries={["/discover"]}
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/discover" element={<p>Khám phá</p>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("AppShell", () => {
  beforeEach(() => {
    useAppStore.getState().resetAll();
    useAppStore.getState().setProfile("An", 10, "user-1", 120);
  });

  it("shows a shell-level logout action", () => {
    renderShell();

    expect(
      screen.getByRole("button", { name: "Đăng xuất" }),
    ).toBeInTheDocument();
  });
});
