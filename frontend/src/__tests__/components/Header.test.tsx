import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Header } from "@/components/Header";
import * as api from "@/lib/api";

vi.mock("@/lib/api");

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function renderHeader() {
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <Header />
      </QueryClientProvider>
    </MemoryRouter>,
  );
}

describe("Header component", () => {
  it("renders brand name", () => {
    renderHeader();
    expect(screen.getByText("Intelligence")).toBeInTheDocument();
  });

  it("renders About link", () => {
    renderHeader();
    expect(screen.getByRole("link", { name: /about/i })).toBeInTheDocument();
  });

  it("renders GitHub link", () => {
    renderHeader();
    expect(screen.getByRole("link", { name: /github/i })).toBeInTheDocument();
  });

  it("renders search input", () => {
    // Mock districts so the useQuery doesn't hang
    vi.mocked(api.getDistricts).mockResolvedValue({ districts: [] });
    renderHeader();
    expect(screen.getByPlaceholderText(/search district/i)).toBeInTheDocument();
  });

  it("returns at most ten district results when typing a non-empty query", async () => {
    vi.mocked(api.getDistricts).mockResolvedValue({
      districts: Array.from({ length: 15 }, (_, i) => ({
        id: i,
        name: `District ${i}`,
      })),
    });
    renderHeader();
    const input = screen.getByPlaceholderText(/search district/i);
    fireEvent.change(input, { target: { value: "District" } });
    await waitFor(() => {
      const items = screen.queryAllByRole("listitem");
      expect(items.length).toBeGreaterThan(0);
      expect(items.length).toBeLessThanOrEqual(10);
    });
  });
});
