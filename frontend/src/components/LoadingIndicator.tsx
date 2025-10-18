import React from "react";
import { Spinner } from "react-bootstrap";

interface LoadingIndicatorProps {
  isVisible: boolean;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ isVisible }) => {
  if (!isVisible) {
    return null;
  }

  return (
    <div className="loading-indicator text-center my-4">
      <Spinner animation="border" role="status" variant="primary">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
      <p className="mt-3 text-muted">Analyzing image...</p>
    </div>
  );
};

export default LoadingIndicator;
