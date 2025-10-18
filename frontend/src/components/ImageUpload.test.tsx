import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ImageUpload from "./ImageUpload";

describe("ImageUpload", () => {
  it("renders file input with correct attributes", () => {
    const mockOnImageSelect = vi.fn();
    render(<ImageUpload onImageSelect={mockOnImageSelect} disabled={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveAttribute("type", "file");
    expect(fileInput).toHaveAttribute(
      "accept",
      ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
    );
  });

  it("displays error for invalid file type", () => {
    const mockOnImageSelect = vi.fn();
    render(<ImageUpload onImageSelect={mockOnImageSelect} disabled={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;

    // Create a text file (invalid type)
    const invalidFile = new File(["test content"], "test.txt", {
      type: "text/plain",
    });

    fireEvent.change(fileInput, { target: { files: [invalidFile] } });

    expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
    expect(mockOnImageSelect).not.toHaveBeenCalled();
  });

  it("displays error for file exceeding size limit", () => {
    const mockOnImageSelect = vi.fn();
    render(<ImageUpload onImageSelect={mockOnImageSelect} disabled={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;

    // Create a file larger than 10MB
    const largeContent = "x".repeat(11 * 1024 * 1024);
    const largeFile = new File([largeContent], "large.jpg", {
      type: "image/jpeg",
    });

    fireEvent.change(fileInput, { target: { files: [largeFile] } });

    expect(screen.getByText(/file size exceeds 10mb/i)).toBeInTheDocument();
    expect(mockOnImageSelect).not.toHaveBeenCalled();
  });

  it("accepts valid image file and shows preview", () => {
    const mockOnImageSelect = vi.fn();
    render(<ImageUpload onImageSelect={mockOnImageSelect} disabled={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;

    // Create a valid JPEG file
    const validFile = new File(["image content"], "test.jpg", {
      type: "image/jpeg",
    });
    Object.defineProperty(validFile, "size", { value: 1024 * 1024 }); // 1MB

    fireEvent.change(fileInput, { target: { files: [validFile] } });

    // Should not show error
    expect(screen.queryByText(/invalid file type/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/file size exceeds/i)).not.toBeInTheDocument();
  });

  it("disables file input when disabled prop is true", () => {
    const mockOnImageSelect = vi.fn();
    render(<ImageUpload onImageSelect={mockOnImageSelect} disabled={true} />);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    expect(fileInput).toBeDisabled();
  });

  it("calls onImageSelect when analyze button is clicked", async () => {
    const mockOnImageSelect = vi.fn();
    render(<ImageUpload onImageSelect={mockOnImageSelect} disabled={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;

    // Create and select a valid file
    const validFile = new File(["image content"], "test.jpg", {
      type: "image/jpeg",
    });
    Object.defineProperty(validFile, "size", { value: 1024 * 1024 });

    fireEvent.change(fileInput, { target: { files: [validFile] } });

    // Wait for preview to render
    await screen.findByText(/image preview/i);

    const analyzeButton = screen.getByRole("button", {
      name: /analyze image/i,
    });
    fireEvent.click(analyzeButton);

    expect(mockOnImageSelect).toHaveBeenCalledWith(validFile);
  });

  it("clears selection when clear button is clicked", async () => {
    const mockOnImageSelect = vi.fn();
    render(<ImageUpload onImageSelect={mockOnImageSelect} disabled={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;

    // Select a valid file
    const validFile = new File(["image content"], "test.jpg", {
      type: "image/jpeg",
    });
    Object.defineProperty(validFile, "size", { value: 1024 * 1024 });

    fireEvent.change(fileInput, { target: { files: [validFile] } });

    // Wait for preview
    await screen.findByText(/image preview/i);

    const clearButton = screen.getByRole("button", { name: /clear/i });
    fireEvent.click(clearButton);

    // Preview should be removed
    expect(screen.queryByText(/image preview/i)).not.toBeInTheDocument();
  });

  it("dismisses error alert when close button is clicked", () => {
    const mockOnImageSelect = vi.fn();
    render(<ImageUpload onImageSelect={mockOnImageSelect} disabled={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;

    // Trigger an error
    const invalidFile = new File(["test"], "test.txt", { type: "text/plain" });
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });

    expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();

    // Find and click the dismiss button
    const alert = screen.getByRole("alert");
    const dismissButton = alert.querySelector("button");
    if (dismissButton) {
      fireEvent.click(dismissButton);
    }

    expect(screen.queryByText(/invalid file type/i)).not.toBeInTheDocument();
  });
});
