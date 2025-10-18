import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import ResultsDisplay from "./ResultsDisplay";
import type { Detection } from "../types/detection";

describe("ResultsDisplay", () => {
  const mockDetections: Detection[] = [
    {
      bounding_box: [100, 50, 200, 150],
      label: "scratch",
      confidence_score: 0.87,
    },
    {
      bounding_box: [300, 200, 450, 350],
      label: "dent",
      confidence_score: 0.92,
    },
  ];

  beforeEach(() => {
    // Mock HTMLCanvasElement methods
    HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
      drawImage: vi.fn(),
      strokeRect: vi.fn(),
      fillRect: vi.fn(),
      fillText: vi.fn(),
      measureText: vi.fn(() => ({ width: 100 })),
      strokeStyle: "",
      fillStyle: "",
      lineWidth: 0,
      font: "",
    })) as any;
  });

  it("renders canvas element", () => {
    render(
      <ResultsDisplay imageUrl="test-image.jpg" detections={mockDetections} />
    );

    const canvas = document.querySelector("canvas");
    expect(canvas).toBeInTheDocument();
  });

  it("displays correct detection count", () => {
    render(
      <ResultsDisplay imageUrl="test-image.jpg" detections={mockDetections} />
    );

    expect(screen.getByText(/found 2 damages/i)).toBeInTheDocument();
  });

  it("displays singular damage text for single detection", () => {
    const singleDetection: Detection[] = [
      {
        bounding_box: [100, 50, 200, 150],
        label: "scratch",
        confidence_score: 0.87,
      },
    ];

    render(
      <ResultsDisplay imageUrl="test-image.jpg" detections={singleDetection} />
    );

    expect(screen.getByText(/found 1 damage$/i)).toBeInTheDocument();
  });

  it("displays zero damages correctly", () => {
    render(<ResultsDisplay imageUrl="test-image.jpg" detections={[]} />);

    expect(screen.getByText(/found 0 damages/i)).toBeInTheDocument();
  });

  it("renders detection results heading", () => {
    render(
      <ResultsDisplay imageUrl="test-image.jpg" detections={mockDetections} />
    );

    expect(screen.getByText(/detection results/i)).toBeInTheDocument();
  });

  it("creates canvas with proper styling", () => {
    render(
      <ResultsDisplay imageUrl="test-image.jpg" detections={mockDetections} />
    );

    const canvas = document.querySelector("canvas");
    expect(canvas).toHaveStyle({
      maxWidth: "100%",
      height: "auto",
      display: "block",
    });
  });
});
