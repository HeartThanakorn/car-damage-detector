# Implementation Plan: Car Damage Detection API

This implementation plan breaks down the Car Damage Detection API into discrete, actionable coding tasks. Each task builds incrementally on previous work and references specific requirements from the requirements document.

## Tasks

- [ ] 1. Set up backend project structure and core FastAPI application

  - Create directory structure: `backend/app/`, `backend/tests/`, `backend/app/services/`
  - Initialize FastAPI application in `app/main.py` with basic configuration
  - Configure CORS middleware with development and production origins (localhost:3000, localhost:5173, production URL)
  - Create `app/config.py` for centralized configuration management (S3 bucket name, model path, file size limits)
  - Set up `requirements.txt` with FastAPI, Pydantic, boto3, Pillow, and ultralytics dependencies
  - Create Dockerfile for containerizing the FastAPI application
  - _Requirements: 5.1, 5.2, 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 2. Implement Pydantic data models and validation

  - Create `app/models.py` with Detection, DetectionResponse, and ErrorResponse models
  - Define Detection model with bounding_box tuple, label string, and confidence_score float (0.0-1.0)
  - Define DetectionResponse model with detections list, image_id string, and processing_time_ms float
  - Add field validation and descriptions using Pydantic Field
  - _Requirements: 3.4, 3.5, 3.6, 3.7_

- [ ] 3. Implement S3 storage service

  - Create `app/services/storage.py` with StorageService class
  - Implement `generate_image_id()` method using UUID for unique identifiers
  - Implement `upload_image()` method to upload image bytes to S3 with proper content type
  - Configure boto3 S3 client with bucket name from environment variables
  - Add error handling for S3 upload failures
  - _Requirements: 2.5, 6.3_

- [ ] 4. Implement AI damage detection service

  - Create `app/services/detection.py` with DamageDetectionService class
  - Implement `load_model()` method to load pre-trained YOLO model (singleton pattern for Lambda efficiency)
  - Implement `detect_damages()` method that accepts image bytes and returns List[Detection]
  - Add image preprocessing logic to convert bytes to format expected by YOLO
  - Parse YOLO model output and convert to Detection objects with bounding boxes, labels, and confidence scores
  - Set confidence threshold to 0.25 for filtering low-confidence detections
  - _Requirements: 2.2, 2.3, 2.4_

- [ ] 5. Implement POST /detect endpoint

  - Create `/detect` endpoint in `app/main.py` that accepts multipart/form-data
  - Validate uploaded file is an image type (JPEG, PNG, WebP)
  - Validate file size does not exceed 10MB limit
  - Generate unique image ID using StorageService
  - Upload image to S3 using StorageService
  - Process image using DamageDetectionService to get detections
  - Calculate processing time and return DetectionResponse with detections, image_id, and processing_time_ms
  - _Requirements: 2.1, 2.2, 2.5, 3.1, 3.2, 3.3, 3.4_

- [ ] 6. Implement error handling and health check endpoint

  - Add FastAPI exception handlers for validation errors (400), file size errors (413), and internal errors (500)
  - Create `/health` endpoint that returns status and timestamp
  - Implement error response formatting using ErrorResponse model
  - Add logging for errors to facilitate debugging
  - _Requirements: 4.1, 4.3_

- [ ] 7. Write backend unit and integration tests

  - Create `tests/conftest.py` with pytest fixtures for test client and sample images
  - Write unit tests in `tests/test_detection.py` for DamageDetectionService (mock YOLO model)
  - Write unit tests in `tests/test_storage.py` for StorageService (mock S3 with moto)
  - Write integration tests in `tests/test_api.py` for `/detect` endpoint with valid and invalid inputs
  - Write tests for `/health` endpoint
  - Verify test coverage meets 80% minimum requirement
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 8. Set up AWS CDK infrastructure project

  - Create `infrastructure/` directory with CDK Python project structure
  - Initialize CDK app in `infrastructure/app.py`
  - Create `infrastructure/stacks/car_damage_stack.py` with CarDamageDetectionStack class
  - Set up `infrastructure/requirements.txt` with aws-cdk-lib dependencies
  - Create `cdk.json` configuration file
  - _Requirements: 6.1, 6.5_

- [ ] 9. Implement CDK stack for AWS resources

  - Define S3 bucket resource in CDK stack for image storage with appropriate CORS configuration
  - Define ECR repository resource for storing Docker images
  - Define Lambda function resource using DockerImageFunction with 3GB memory and 30-second timeout
  - Configure Lambda environment variables (S3_BUCKET_NAME)
  - Grant Lambda function read/write permissions to S3 bucket
  - Define API Gateway REST API resource with Lambda proxy integration
  - Configure API Gateway CORS settings
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 10. Set up frontend React project structure

  - Initialize React project with TypeScript using Vite
  - Install dependencies: React, TypeScript, Bootstrap, React Bootstrap
  - Create directory structure: `frontend/src/components/`, `frontend/src/services/`, `frontend/src/types/`
  - Configure TypeScript with strict mode in `tsconfig.json`
  - Set up Bootstrap CSS imports in main entry point
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 11. Implement TypeScript types and API service

  - Create `src/types/detection.ts` with Detection, DetectionResponse, and ErrorResponse interfaces
  - Create `src/services/api.ts` with DamageDetectionAPI class
  - Implement `detectDamage()` method that sends multipart/form-data POST request to `/detect` endpoint
  - Add error handling for network failures and non-OK responses
  - Configure API base URL from environment variable
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 12. Implement ImageUpload component

  - Create `src/components/ImageUpload.tsx` with file input and preview
  - Implement file type validation (JPEG, PNG, WebP only)
  - Implement file size validation (10MB maximum)
  - Display error messages for invalid files using Bootstrap alert components
  - Show image preview after successful selection
  - Disable upload button when processing is in progress
  - _Requirements: 1.1, 1.2, 1.3, 1.5, 8.4_

- [ ] 13. Implement LoadingIndicator component

  - Create `src/components/LoadingIndicator.tsx` with Bootstrap spinner
  - Display "Analyzing image..." message during processing
  - Control visibility based on isVisible prop
  - _Requirements: 1.4_

- [ ] 14. Implement ResultsDisplay component

  - Create `src/components/ResultsDisplay.tsx` with HTML canvas for rendering
  - Implement canvas drawing logic to render uploaded image
  - Draw bounding boxes at coordinates from Detection objects
  - Display damage labels and confidence scores near each bounding box
  - Use different colors for different damage types (scratches, dents, etc.)
  - Scale coordinates appropriately if image is resized for display
  - _Requirements: 3.5, 3.8_

- [ ] 15. Implement JsonViewer component

  - Create `src/components/JsonViewer.tsx` for displaying raw API response
  - Format JSON with proper indentation and syntax highlighting
  - Use monospace font and code block styling
  - Display error responses when API calls fail
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 16. Implement main App component and integrate all features

  - Create `src/App.tsx` as root component
  - Implement state management for uploadedImage, isLoading, detectionResults, and error
  - Integrate ImageUpload component with onImageSelect handler
  - Integrate LoadingIndicator component with isLoading state
  - Integrate ResultsDisplay component with detection results
  - Integrate JsonViewer component with API response
  - Implement API call flow: image selection → loading state → API request → display results
  - Handle errors and display error messages using Bootstrap alert
  - Organize UI into sections using Bootstrap grid and card components
  - _Requirements: 1.3, 1.4, 3.8, 4.3, 8.3, 8.4_

- [ ] 17. Write frontend unit tests

  - Install Jest and React Testing Library as dev dependencies
  - Configure Jest for TypeScript and React
  - Write unit tests for ImageUpload component (file validation, error display)
  - Write unit tests for ResultsDisplay component (canvas rendering with mock data)
  - Write unit tests for API service (mock fetch calls)
  - Verify test coverage meets 70% minimum requirement for components
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 18. Create deployment documentation and scripts
  - Create README.md with project overview and setup instructions
  - Document backend local development setup (virtual environment, dependencies, running locally)
  - Document frontend local development setup (npm install, environment variables, running dev server)
  - Create script for building and pushing Docker image to ECR
  - Document CDK deployment process (bootstrap, deploy, destroy)
  - Add environment variable configuration examples (.env.example files)
  - Document API endpoint usage with example curl commands
  - _Requirements: 6.1, 6.5_
