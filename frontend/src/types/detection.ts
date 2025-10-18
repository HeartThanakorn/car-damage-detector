/**
 * Detection object representing a single damage detection result
 */
export interface Detection {
  /** Bounding box coordinates [x1, y1, x2, y2] */
  bounding_box: [number, number, number, number];
  /** Damage type label (e.g., "scratch", "dent", "crack") */
  label: string;
  /** Confidence score between 0 and 1 */
  confidence_score: number;
}

/**
 * Response from the damage detection API
 */
export interface DetectionResponse {
  /** Array of detected damages */
  detections: Detection[];
  /** Unique identifier for the uploaded image */
  image_id: string;
  /** Processing time in milliseconds */
  processing_time_ms: number;
}

/**
 * Error response from the API
 */
export interface ErrorResponse {
  /** Error type or message */
  error: string;
  /** Detailed error description */
  detail: string;
}
