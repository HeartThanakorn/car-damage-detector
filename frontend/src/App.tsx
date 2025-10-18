import { useState } from "react";
import { Container, Row, Col, Card, Alert } from "react-bootstrap";
import ImageUpload from "./components/ImageUpload";
import LoadingIndicator from "./components/LoadingIndicator";
import ResultsDisplay from "./components/ResultsDisplay";
import JsonViewer from "./components/JsonViewer";
import { damageDetectionAPI } from "./services/api";
import type { DetectionResponse } from "./types/detection";
import "./App.css";

function App() {
  // State management
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [detectionResults, setDetectionResults] =
    useState<DetectionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle image selection and initiate API call
   */
  const handleImageSelect = async (file: File) => {
    // Clear previous results and errors
    setError(null);
    setDetectionResults(null);

    // Create object URL for display
    const url = URL.createObjectURL(file);
    setImageUrl(url);

    // Set loading state
    setIsLoading(true);

    try {
      // Call the API
      const results = await damageDetectionAPI.detectDamage(file);

      // Store results
      setDetectionResults(results);
    } catch (err) {
      // Handle errors
      const errorMessage =
        err instanceof Error ? err.message : "An unexpected error occurred";
      setError(errorMessage);
    } finally {
      // Clear loading state
      setIsLoading(false);
    }
  };

  /**
   * Dismiss error alert
   */
  const handleDismissError = () => {
    setError(null);
  };

  return (
    <Container className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <h1 className="text-center">Car Damage Detection</h1>
          <p className="text-center text-muted">
            Upload an image of your vehicle to detect damages using AI
          </p>
        </Col>
      </Row>

      {/* Error Alert */}
      {error && (
        <Row className="mb-3">
          <Col>
            <Alert variant="danger" dismissible onClose={handleDismissError}>
              <Alert.Heading>Error</Alert.Heading>
              <p>{error}</p>
            </Alert>
          </Col>
        </Row>
      )}

      {/* Image Upload Section */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <Card.Title>Upload Image</Card.Title>
              <ImageUpload
                onImageSelect={handleImageSelect}
                disabled={isLoading}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Loading Indicator */}
      {isLoading && (
        <Row className="mb-4">
          <Col>
            <LoadingIndicator isVisible={isLoading} />
          </Col>
        </Row>
      )}

      {/* Results Section */}
      {detectionResults && imageUrl && !isLoading && (
        <>
          <Row className="mb-4">
            <Col lg={12}>
              <Card>
                <Card.Body>
                  <ResultsDisplay
                    imageUrl={imageUrl}
                    detections={detectionResults.detections}
                  />
                  <div className="mt-3 text-muted">
                    <small>
                      Image ID: {detectionResults.image_id} | Processing Time:{" "}
                      {detectionResults.processing_time_ms.toFixed(2)}ms
                    </small>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row className="mb-4">
            <Col lg={12}>
              <Card>
                <Card.Body>
                  <JsonViewer data={detectionResults} isError={false} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* Error Response Display */}
      {error && !isLoading && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Body>
                <JsonViewer
                  data={{ error: "Request Failed", detail: error }}
                  isError={true}
                />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
}

export default App;
