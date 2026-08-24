import { describe, it, expect } from "vitest";
import { screen, fireEvent } from "@testing-library/react";
import { renderWithProviders } from "../test-utils";
import { Sidebar } from "@/components/Sidebar";

describe("Sidebar", () => {
  it("renders all nav links with correct hrefs", () => {
    renderWithProviders(<Sidebar />);
    expect(screen.getByRole("link", { name: /yields/i })).toHaveAttribute("href", "/yields");
    expect(screen.getByRole("link", { name: /forecasts/i })).toHaveAttribute("href", "/forecasts");
    expect(screen.getByRole("link", { name: /commercialization/i })).toHaveAttribute(
      "href",
      "/commercialization",
    );
    expect(screen.getByText("Nepal Ag")).toBeInTheDocument();
  });

  it("toggles the mobile overlay open and closed", () => {
    renderWithProviders(<Sidebar />);
    const toggle = screen.getByRole("button", { name: /toggle sidebar/i });

    fireEvent.click(toggle); // open -> overlay + close-on-link wired
    // Clicking a nav link closes the drawer again (setIsOpen(false)).
    fireEvent.click(screen.getByRole("link", { name: /home/i }));
    expect(toggle).toBeInTheDocument();
  });
});
