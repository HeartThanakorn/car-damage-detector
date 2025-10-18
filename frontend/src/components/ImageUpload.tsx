import React, { useState, useRef } from "react";
import { Alert, Button, Form } from "react-bootstrap";

interface ImageUploadProps {
  onImageSelect: (file: File) => void;
  disabled: boolean;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onImageSelect,
  disabled,
}) => {
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Allowed file types
  const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes

  const validateFile = (file: File): string | null => {
    // Validate file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      return "Invalid file type. Please upload a JPEG, PNG, or WebP image.";
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds 10MB limit. Your file is ${(
        file.size /
        (1024 * 1024)
      ).toFixed(2)}MB.`;
    }

    return null;
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    // Clear previous state
    setError(null);
    setPreviewUrl(null);
    setSelectedFile(null);

    if (!file) {
      return;
    }

    // Validate the file
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      return;
    }

    // File is valid - create preview and store file
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleUpload = () => {
    if (selectedFile) {
      onImageSelect(selectedFile);
    }
  };

  const handleClear = () => {
    setError(null);
    setPreviewUrl(null);
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="image-upload-container">
      <Form.Group className="mb-3">
        <Form.Label>Upload Vehicle Image</Form.Label>
        <Form.Control
          ref={fileInputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
          onChange={handleFileChange}
          disabled={disabled}
        />
        <Form.Text className="text-muted">
          Accepted formats: JPEG, PNG, WebP (Max size: 10MB)
        </Form.Text>
      </Form.Group>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <strong>Error:</strong> {error}
        </Alert>
      )}

      {previewUrl && (
        <div className="preview-container mb-3">
          <h5>Image Preview</h5>
          <img
            src={previewUrl}
            alt="Preview"
            style={{
              maxWidth: "100%",
              maxHeight: "400px",
              border: "1px solid #dee2e6",
              borderRadius: "4px",
            }}
          />
          <div className="mt-3">
            <Button
              variant="primary"
              onClick={handleUpload}
              disabled={disabled || !selectedFile}
              className="me-2"
            >
              {disabled ? "Processing..." : "Analyze Image"}
            </Button>
            <Button
              variant="secondary"
              onClick={handleClear}
              disabled={disabled}
            >
              Clear
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
