import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { DamageDetectionAPI } from "./api";
import type { DetectionResponse, ErrorResponse } from "../types/detection";

describe("DamageDetectionAPI", () => {
  let api: DamageDetectionAPI;
  const mockBaseUrl = "http://test-api.com";

  beforeEach(() => {
    api = new DamageDetectionAPI(mockBaseUrl);
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("initializes with provided base URL", () => {
    const customApi = new DamageDetectionAPI("http://custom-url.com");
    expect(customApi["baseUrl"]).toBe("http://custom-url.com");
  });

  it("uses default base URL when none provided", () => {
    const defaultApi = new DamageDetectionAPI();
    expect(defaultApi["baseUrl"]).toBeTruthy();
  });

  it("sends POST request with FormData to /detect endpoint", async () => {
    const mockResponse: DetectionResponse = {
      detections: [
        {
          bounding_box: [100, 50, 200, 150],
          label: "scratch",
          confidence_score: 0.87,
        },
      ],
      image_id: "test-id-123",
      processing_time_ms: 1234.56,
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const testFile = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const result = await api.detectDamage(testFile);

    expect(global.fetch).toHaveBeenCalledWith(
      `${mockBaseUrl}/detect`,
      expect.objectContaining({
        method: "POST",
        body: expect.any(FormData),
      })
    );

    expect(result).toEqual(mockResponse);
  });

  it("includes file in FormData with correct field name", async () => {
    const mockResponse: DetectionResponse = {
      detections: [],
      image_id: "test-id",
      processing_time_ms: 100,
    };

    let capturedFormData: FormData | null = null;

    (global.fetch as any).mockImplementationOnce(
      (url: string, options: any) => {
        capturedFormData = options.body;
        return Promise.resolve({
          ok: true,
          json: async () => mockResponse,
        });
      }
    );

    const testFile = new File(["test"], "test.jpg", { type: "image/jpeg" });
    await api.detectDamage(testFile);

    expect(capturedFormData).toBeInstanceOf(FormData);
    expect(capturedFormData?.get("file")).toBe(testFile);
  });

  it("throws error when response is not ok", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: "Bad Request",
      json: async () => ({
        error: "Invalid file",
        detail: "File must be an image",
      }),
    });

    const testFile = new File(["test"], "test.txt", { type: "text/plain" });

    await expect(api.detectDamage(testFile)).rejects.toThrow(
      "File must be an image"
    );
  });

  it("handles error response with detail field", async () => {
    const errorResponse: ErrorResponse = {
      error: "Validation Error",
      detail: "File size exceeds limit",
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 413,
      statusText: "Payload Too Large",
      json: async () => errorResponse,
    });

    const testFile = new File(["x".repeat(11 * 1024 * 1024)], "large.jpg", {
      type: "image/jpeg",
    });

    await expect(api.detectDamage(testFile)).rejects.toThrow(
      "File size exceeds limit"
    );
  });

  it("handles error response with error field", async () => {
    const errorResponse: ErrorResponse = {
      error: "Internal Server Error",
      detail: "",
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: async () => errorResponse,
    });

    const testFile = new File(["test"], "test.jpg", { type: "image/jpeg" });

    await expect(api.detectDamage(testFile)).rejects.toThrow(
      "Internal Server Error"
    );
  });

  it("uses default error message when response body cannot be parsed", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: async () => {
        throw new Error("Invalid JSON");
      },
    });

    const testFile = new File(["test"], "test.jpg", { type: "image/jpeg" });

    await expect(api.detectDamage(testFile)).rejects.toThrow(
      "API Error: 500 Internal Server Error"
    );
  });

  it("handles network failures", async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error("Network error"));

    const testFile = new File(["test"], "test.jpg", { type: "image/jpeg" });

    await expect(api.detectDamage(testFile)).rejects.toThrow("Network error");
  });

  it("returns complete detection response with all fields", async () => {
    const mockResponse: DetectionResponse = {
      detections: [
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
      ],
      image_id: "abc-123-def",
      processing_time_ms: 2345.67,
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const testFile = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const result = await api.detectDamage(testFile);

    expect(result.detections).toHaveLength(2);
    expect(result.image_id).toBe("abc-123-def");
    expect(result.processing_time_ms).toBe(2345.67);
    expect(result.detections[0].label).toBe("scratch");
    expect(result.detections[1].label).toBe("dent");
  });
});
