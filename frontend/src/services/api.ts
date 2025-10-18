import type { DetectionResponse, ErrorResponse } from "../types/detection";

/**
 * API service for communicating with the Car Damage Detection backend
 */
export class DamageDetectionAPI {
  private baseUrl: string;

  /**
   * Initialize the API service
   * @param baseUrl - Base URL of the API (defaults to environment variable or localhost)
   */
  constructor(baseUrl?: string) {
    // Use provided URL, environment variable, or default to localhost
    this.baseUrl =
      baseUrl || import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
  }

  /**
   * Send an image to the damage detection API
   * @param imageFile - The image file to analyze
   * @returns Promise resolving to detection results
   * @throws Error if the request fails or returns a non-OK response
   */
  async detectDamage(imageFile: File): Promise<DetectionResponse> {
    try {
      // Create FormData with the image file
      const formData = new FormData();
      formData.append("file", imageFile);

      // Send POST request to /detect endpoint
      const response = await fetch(`${this.baseUrl}/detect`, {
        method: "POST",
        body: formData,
      });

      // Handle non-OK responses
      if (!response.ok) {
        let errorMessage = `API Error: ${response.status} ${response.statusText}`;

        try {
          // Try to parse error response body
          const errorData: ErrorResponse = await response.json();
          errorMessage = errorData.detail || errorData.error || errorMessage;
        } catch {
          // If parsing fails, use the default error message
        }

        throw new Error(errorMessage);
      }

      // Parse and return successful response
      const data: DetectionResponse = await response.json();
      return data;
    } catch (error) {
      // Handle network failures and other errors
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("An unexpected error occurred while detecting damage");
    }
  }
}

// Export a default instance for convenience
export const damageDetectionAPI = new DamageDetectionAPI();
