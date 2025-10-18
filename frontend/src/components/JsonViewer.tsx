import React from "react";
import type { DetectionResponse, ErrorResponse } from "../types/detection";

interface JsonViewerProps {
  data: DetectionResponse | ErrorResponse | null;
  isError?: boolean;
}

/**
 * JsonViewer component displays raw API response data in a formatted JSON view
 * Supports both successful detection responses and error responses
 */
const JsonViewer: React.FC<JsonViewerProps> = ({ data, isError = false }) => {
  if (!data) {
    return null;
  }

  // Format JSON with proper indentation
  const formattedJson = JSON.stringify(data, null, 2);

  return (
    <div className="json-viewer-container">
      <h5>API Response</h5>
      <div
        className={`json-viewer ${isError ? "json-viewer-error" : ""}`}
        style={{
          backgroundColor: isError ? "#fff5f5" : "#f8f9fa",
          border: `1px solid ${isError ? "#f5c6cb" : "#dee2e6"}`,
          borderRadius: "4px",
          padding: "1rem",
          maxHeight: "400px",
          overflow: "auto",
        }}
      >
        <pre
          style={{
            margin: 0,
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: "14px",
            lineHeight: "1.5",
            color: isError ? "#721c24" : "#212529",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          <code>{formattedJson}</code>
        </pre>
      </div>
    </div>
  );
};

export default JsonViewer;
