import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import Onboarding from "./Onboarding";

describe("Onboarding", () => {
  it("shows only the Google OAuth login action", () => {
    render(
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
    expect(screen.queryByText(/khối lớp/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/lớp 10/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/tên hiển thị/i)).not.toBeInTheDocument();
  });
});
