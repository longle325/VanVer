import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";
import { useAppStore } from "@/stores/useAppStore";
import Onboarding from "./Onboarding";

describe("Onboarding", () => {
  beforeEach(() => {
    useAppStore.getState().resetAll();
  });

  it("shows only the Google OAuth login action", () => {
    const { container } = render(
      <MemoryRouter
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <Onboarding />
      </MemoryRouter>,
    );

    const loginLink = screen.getByRole("link", {
      name: /đăng nhập bằng google/i,
    });

    expect(loginLink).toHaveAttribute(
      "href",
      expect.stringContaining("/api/v1/auth/login/google"),
    );
    const next = new URL(loginLink.getAttribute("href") ?? "").searchParams.get(
      "next",
    );
    expect(next).toContain("#/discover");
    expect(loginLink.querySelector(".google-g-icon")).toBeInTheDocument();
    expect(container.querySelectorAll(".google-g-icon")).toHaveLength(1);
    expect(screen.queryByText(/khối lớp/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/lớp 10/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/tên hiển thị/i)).not.toBeInTheDocument();
  });

  it("shows a music toggle on the login screen", () => {
    render(
      <MemoryRouter
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <Onboarding />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("button", { name: "Bật nhạc nền" }),
    ).toBeInTheDocument();
  });

  it("toggles global background music from the login screen", () => {
    render(
      <MemoryRouter
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <Onboarding />
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Bật nhạc nền" }));

    expect(useAppStore.getState().music.enabled).toBe(true);
    expect(
      screen.getByRole("button", { name: "Tắt nhạc nền" }),
    ).toHaveAttribute("aria-pressed", "true");
  });
});
