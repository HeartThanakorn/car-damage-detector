import React, { useEffect, useRef } from "react";
import type { Detection } from "../types/detection";

interface ResultsDisplayProps {
  imageUrl: string;
  detections: Detection[];
}

// Color mapping for different damage types
const DAMAGE_COLORS: Record<string, string> = {
  scratch: "#FF6B6B",
  dent: "#4ECDC4",
  crack: "#FFE66D",
  "broken part": "#95E1D3",
  default: "#A8DADC",
};

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  imageUrl,
  detections,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Load the image
    const img = new Image();
    img.onload = () => {
      imageRef.current = img;

      // Set canvas dimensions to match image
      canvas.width = img.width;
      canvas.height = img.height;

      // Draw the image
      ctx.drawImage(img, 0, 0);

      // Draw bounding boxes and labels
      detections.forEach((detection) => {
        drawDetection(ctx, detection);
      });
    };

    img.src = imageUrl;
  }, [imageUrl, detections]);

  const drawDetection = (
    ctx: CanvasRenderingContext2D,
    detection: Detection
  ) => {
    const [x1, y1, x2, y2] = detection.bounding_box;

    // Get color for this damage type
    const color =
      DAMAGE_COLORS[detection.label.toLowerCase()] || DAMAGE_COLORS.default;

    // Draw bounding box
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

    // Prepare label text
    const confidencePercent = (detection.confidence_score * 100).toFixed(1);
    const labelText = `${detection.label} (${confidencePercent}%)`;

    // Configure text style
    ctx.font = "16px Arial";
    ctx.fillStyle = color;

    // Measure text to create background
    const textMetrics = ctx.measureText(labelText);
    const textWidth = textMetrics.width;
    const textHeight = 20;
    const padding = 4;

    // Position label above bounding box, or below if too close to top
    let labelX = x1;
    let labelY = y1 - textHeight - padding;

    if (labelY < 0) {
      labelY = y1 + textHeight + padding;
    }

    // Draw background rectangle for label
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(
      labelX,
      labelY - textHeight,
      textWidth + padding * 2,
      textHeight + padding
    );

    // Draw label text
    ctx.fillStyle = color;
    ctx.fillText(labelText, labelX + padding, labelY - padding);
  };

  return (
    <div className="results-display-container">
      <h5>Detection Results</h5>
      <div
        style={{
          maxWidth: "100%",
          overflow: "auto",
          border: "1px solid #dee2e6",
          borderRadius: "4px",
        }}
      >
        <canvas
          ref={canvasRef}
          style={{
            maxWidth: "100%",
            height: "auto",
            display: "block",
          }}
        />
      </div>
      <div className="mt-3">
        <p className="text-muted">
          Found {detections.length} damage{detections.length !== 1 ? "s" : ""}
        </p>
      </div>
    </div>
  );
};

export default ResultsDisplay;
