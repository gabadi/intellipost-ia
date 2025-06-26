import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/svelte";
import Page from "./+page.svelte";

describe("Root Page Component (+page.svelte)", () => {
  it("should render without errors", () => {
    render(Page);
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
  });

  it("should render Welcome component with default props", () => {
    render(Page);
    expect(screen.getByRole("heading", { level: 1, name: "IntelliPost AI" })).toBeInTheDocument();
    expect(screen.getByText("AI-Powered MercadoLibre Listing Assistant")).toBeInTheDocument();
  });

  it("should render Welcome component description", () => {
    render(Page);
    expect(
      screen.getByText(/Transform your product images into compelling MercadoLibre listings/)
    ).toBeInTheDocument();
  });

  it("should render all Welcome component features", () => {
    render(Page);
    const features = [
      "📸 Image upload and processing",
      "🤖 AI-generated titles and descriptions",
      "🛍️ Direct MercadoLibre integration",
      "📊 Performance analytics"
    ];

    features.forEach(feature => {
      expect(screen.getByText(feature)).toBeInTheDocument();
    });
  });

  it("should have features list with correct number of items", () => {
    render(Page);
    const listItems = screen.getAllByRole("listitem");
    expect(listItems).toHaveLength(4);
  });

  it("should maintain Welcome component structure", () => {
    render(Page);
    // Should have the heading from Welcome component
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
    // Should have the list from Welcome component
    expect(screen.getByRole("list")).toBeInTheDocument();
  });

  it("should render Welcome component with proper semantic structure", () => {
    render(Page);
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
    expect(screen.getByRole("list")).toBeInTheDocument();
    expect(screen.getAllByRole("listitem")).toHaveLength(4);
  });

  it("should contain Welcome component CSS classes", () => {
    const { container } = render(Page);
    expect(container.querySelector(".welcome")).toBeInTheDocument();
    expect(container.querySelector(".subtitle")).toBeInTheDocument();
    expect(container.querySelector(".description")).toBeInTheDocument();
    expect(container.querySelector(".features")).toBeInTheDocument();
  });

  it("should render subtitle with correct class and content", () => {
    const { container } = render(Page);
    const subtitleElement = container.querySelector(".subtitle");
    expect(subtitleElement).toBeInTheDocument();
    expect(subtitleElement).toHaveTextContent("AI-Powered MercadoLibre Listing Assistant");
  });

  it("should render description with correct class and content", () => {
    const { container } = render(Page);
    const descriptionElement = container.querySelector(".description");
    expect(descriptionElement).toBeInTheDocument();
    expect(descriptionElement).toHaveTextContent(/Transform your product images/);
  });
});
