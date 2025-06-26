import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/svelte";
import Layout from "./+layout.svelte";

describe("Root Layout Component (+layout.svelte)", () => {
  it("should render without errors", () => {
    render(Layout);
    expect(screen.getByRole("main")).toBeInTheDocument();
  });

  it("should render Layout component with default title", () => {
    render(Layout);
    expect(screen.getByRole("heading", { level: 1, name: "IntelliPost AI" })).toBeInTheDocument();
  });

  it("should render header within main container", () => {
    render(Layout);
    const main = screen.getByRole("main");
    const header = screen.getByRole("banner");
    expect(main).toContainElement(header);
  });

  it("should have slot available for page content", () => {
    const { container } = render(Layout);
    const main = container.querySelector("main");
    expect(main).toBeInTheDocument();
    // Slot structure available after the header
    expect(main?.innerHTML).toContain("<header>");
  });

  it("should have proper semantic structure", () => {
    render(Layout);
    expect(screen.getByRole("main")).toBeInTheDocument();
    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
  });

  it("should contain Layout component structure", () => {
    render(Layout);
    // Should have the main container from Layout component
    expect(screen.getByRole("main")).toBeInTheDocument();
    // Should have the header from Layout component
    expect(screen.getByRole("banner")).toBeInTheDocument();
    // Should have the h1 from Layout component
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
  });

  it("should maintain Layout component accessibility features", () => {
    render(Layout);
    // Layout component provides semantic HTML structure
    const main = screen.getByRole("main");
    const header = screen.getByRole("banner");
    const heading = screen.getByRole("heading", { level: 1 });

    expect(main).toBeInTheDocument();
    expect(header).toBeInTheDocument();
    expect(heading).toBeInTheDocument();

    // Check that header is within main (as per Layout component structure)
    expect(main).toContainElement(header);
    expect(header).toContainElement(heading);
  });
});
