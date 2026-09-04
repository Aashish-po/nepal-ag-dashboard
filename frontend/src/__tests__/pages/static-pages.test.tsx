import { describe, it, expect } from "vitest";
import { screen, fireEvent, within } from "@testing-library/react";
import { renderWithProviders } from "../test-utils";
import { About } from "@/pages/About";
import { Home } from "@/pages/Home";
import { Map } from "@/pages/Map";

// Static pages: no API, no store — render + (for Map) interaction only.

describe("About page", () => {
  it("renders heading and data sources", () => {
    renderWithProviders(<About />);
    expect(screen.getByText("About & Methodology")).toBeInTheDocument();
    expect(screen.getByText("FAOSTAT")).toBeInTheDocument();
    expect(screen.getByText("NASA POWER")).toBeInTheDocument();
    expect(screen.getByText("CHIRPS")).toBeInTheDocument();
  });
});

describe("Home page", () => {
  it("renders hero and feature links", () => {
    renderWithProviders(<Home />);
    expect(
      screen.getByText(/Analyze agricultural productivity across Nepal/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /explore yields/i }),
    ).toHaveAttribute("href", "/yields");
    expect(screen.getByText("Yield Analysis")).toBeInTheDocument();
    expect(screen.getByText("77")).toBeInTheDocument();
  });
});

describe("Map page", () => {
  it("opens and closes the district detail panel on click", () => {
    renderWithProviders(<Map />);
    expect(screen.getByText("District Map")).toBeInTheDocument();

    // No panel until a district is picked.
    expect(screen.queryByText(/Population/)).not.toBeInTheDocument();

    // ponytail: click the SVG group whose <title> labels the district
    const kathmanduGroup = screen.getByText("Kathmandu").parentElement!;
    fireEvent.click(kathmanduGroup);

    // ponytail: map container is no longer a Card — only the detail panel has .card; scope to it
    const panel = document.querySelector(".card") as HTMLElement;
    expect(panel).toBeTruthy();
    expect(within(panel).getByText("Kathmandu")).toBeInTheDocument();
    expect(within(panel).getByText(/Population/)).toBeInTheDocument();
    expect(within(panel).getByText(/Area/)).toBeInTheDocument();

    // Close by clicking the same district again (toggle behavior).
    fireEvent.click(kathmanduGroup);
    expect(screen.queryByText(/Population/)).not.toBeInTheDocument();
  });
});
