# Project: Car Damage Detection API

## Introduction

The Car Damage Detection API is a full-stack application that enables users to upload images of vehicles and receive automated damage detection analysis. The system leverages computer vision AI models to identify and locate damages such as scratches and dents, returning structured results with bounding box coordinates and confidence scores. The application consists of a React-based frontend, a FastAPI backend service, and AWS cloud infrastructure for scalable, serverless deployment.

## Glossary

- **Frontend Application**: The React-based web interface that allows users to upload images and view detection results
- **Backend API**: The FastAPI service that processes image uploads and executes damage detection
- **Detection Service**: The AI-powered component that analyzes images using a pre-trained YOLO model
- **API Gateway**: Amazon API Gateway service that exposes the Lambda function as a public REST endpoint
- **Lambda Function**: AWS Lambda compute service running the containerized FastAPI application
- **S3 Bucket**: Amazon S3 storage service for persisting uploaded vehicle images
- **ECR Repository**: Amazon Elastic Container Registry for storing Docker images
- **CDK Stack**: AWS Cloud Development Kit infrastructure code that provisions all cloud resources
- **Detection Object**: A JSON structure containing bounding box coordinates, damage label, and confidence score
- **Bounding Box**: A set of coordinates [x1, y1, x2, y2] defining the rectangular area of detected damage
- **Confidence Score**: A numerical value between 0 and 1 indicating the model's certainty of detection

## Requirements

### Requirement 1: Image Upload Capability

**User Story:** As a user, I want to upload an image of my car through a web interface, so that I can initiate damage detection analysis.

#### Acceptance Criteria

1. THE Frontend Application SHALL provide a file input component that accepts image files in JPEG, PNG, and WebP formats.
2. WHEN the user selects an image file, THE Frontend Application SHALL validate that the file size does not exceed 10 megabytes.
3. WHEN the user submits a valid image file, THE Frontend Application SHALL send the image to the Backend API using multipart/form-data encoding.
4. WHILE the Backend API processes the image, THE Frontend Application SHALL display a loading indicator to the user.
5. IF the user attempts to upload a file that is not an image, THEN THE Frontend Application SHALL display an error message stating "Invalid file type. Please upload a JPEG, PNG, or WebP image."

### Requirement 2: Damage Detection Processing

**User Story:** As a user, I want the system to automatically detect damages in my uploaded car image, so that I can identify areas requiring repair.

#### Acceptance Criteria

1. THE Backend API SHALL expose a POST endpoint at the path "/detect" that accepts multipart/form-data requests.
2. WHEN the Backend API receives an image file at the "/detect" endpoint, THE Detection Service SHALL process the image using a pre-trained YOLO computer vision model.
3. THE Detection Service SHALL identify damage types including scratches, dents, cracks, and broken parts within the uploaded image.
4. THE Detection Service SHALL generate Detection Objects for each identified damage, containing bounding box coordinates, damage label, and confidence score.
5. THE Backend API SHALL store the uploaded image in the S3 Bucket with a unique identifier as the object key.

### Requirement 3: Detection Results Delivery

**User Story:** As a user, I want to receive structured detection results with visual indicators, so that I can understand the location and type of damages found.

#### Acceptance Criteria

1. WHEN the Detection Service completes analysis, THE Backend API SHALL return a JSON response containing an array of Detection Objects.
2. THE Backend API SHALL include in each Detection Object a "bounding_box" field with coordinates in the format [x1, y1, x2, y2] where values are integers representing pixel positions.
3. THE Backend API SHALL include in each Detection Object a "label" field containing a string describing the damage type.
4. THE Backend API SHALL include in each Detection Object a "confidence_score" field containing a float value between 0.0 and 1.0.
5. THE Frontend Application SHALL render the original uploaded image with bounding boxes overlaid at the coordinates specified in each Detection Object.

### Requirement 4: API Response Transparency

**User Story:** As a developer or technical user, I want to view the raw API response data, so that I can debug issues and understand the detection results in detail.

#### Acceptance Criteria

1. THE Frontend Application SHALL display the complete JSON response received from the Backend API in a formatted text area or code block.
2. THE Frontend Application SHALL preserve the original structure and formatting of the JSON response for readability.
3. WHEN the Backend API returns an error response, THE Frontend Application SHALL display the error message and status code to the user.

### Requirement 5: Serverless Architecture Compliance

**User Story:** As a system administrator, I want the backend to operate in a stateless manner, so that it can scale efficiently on AWS Lambda infrastructure.

#### Acceptance Criteria

1. THE Backend API SHALL NOT maintain session state or user-specific data between requests.
2. THE Lambda Function SHALL process each request independently without relying on data from previous invocations.
3. THE Backend API SHALL complete image processing and return results within 30 seconds to comply with Lambda timeout constraints.
4. THE Lambda Function SHALL be packaged as a Docker container image stored in the ECR Repository.

### Requirement 6: Infrastructure as Code Management

**User Story:** As a DevOps engineer, I want all cloud resources defined in version-controlled code, so that infrastructure can be reliably reproduced and updated.

#### Acceptance Criteria

1. THE CDK Stack SHALL define the Lambda Function, API Gateway, S3 Bucket, and ECR Repository as code using AWS CDK with Python.
2. THE CDK Stack SHALL configure the API Gateway to route HTTP requests to the Lambda Function.
3. THE CDK Stack SHALL grant the Lambda Function permissions to read and write objects in the S3 Bucket.
4. THE CDK Stack SHALL configure the Lambda Function to use the Docker container image from the ECR Repository.
5. WHEN the CDK Stack is deployed, THE system SHALL provision all required AWS resources in the target account and region.

### Requirement 7: Backend Testing Coverage

**User Story:** As a software engineer, I want comprehensive automated tests for the backend, so that I can verify functionality and prevent regressions.

#### Acceptance Criteria

1. THE Backend API SHALL include unit tests written using pytest that validate request parsing and response formatting.
2. THE Backend API SHALL include integration tests that verify the "/detect" endpoint processes sample images and returns valid Detection Objects.
3. THE Backend API SHALL include tests that verify error handling for invalid file uploads and malformed requests.
4. WHEN all tests are executed, THE test suite SHALL achieve a minimum of 80 percent code coverage for the Backend API modules.

### Requirement 8: User Interface Design Standards

**User Story:** As a user, I want a clean and intuitive interface, so that I can easily upload images and view results without confusion.

#### Acceptance Criteria

1. THE Frontend Application SHALL use Bootstrap CSS framework for consistent styling and responsive layout.
2. THE Frontend Application SHALL implement TypeScript for type-safe component development.
3. THE Frontend Application SHALL organize the interface into distinct sections for image upload, loading state, results visualization, and raw JSON display.
4. THE Frontend Application SHALL provide clear labels and instructions for each interactive element.

### Requirement 9: API CORS Configuration

**User Story:** As a frontend developer, I need the Backend API to accept cross-origin requests, so that my React application running on a different domain can communicate with the API without being blocked by the browser.

#### Acceptance Criteria

1. THE Backend API SHALL implement CORSMiddleware to handle cross-origin resource sharing.
2. THE CORS configuration SHALL allow requests from the frontend development origin at http://localhost:3000 and http://localhost:5173.
3. THE CORS configuration SHALL allow requests from the production frontend URL placeholder https://my-damage-detector-app.com.
4. THE CORS configuration SHALL permit the HTTP methods GET, POST, and OPTIONS.
5. THE CORS configuration SHALL allow standard headers including Content-Type, Authorization, and Accept.

### Requirement 10: Frontend Testing Coverage

**User Story:** As a software engineer, I want automated tests for the frontend, so that I can verify component behavior, ensure type safety, and prevent UI regressions.

#### Acceptance Criteria

1. THE Frontend Application SHALL include unit tests for critical React components including ImageUpload.tsx and ResultsDisplay.tsx.
2. THE tests SHALL be written using Jest testing framework and React Testing Library.
3. THE tests SHALL verify that components render correctly when provided with different props and state values.
4. THE tests SHALL simulate user interactions including file selection and button clicks, and assert the expected outcomes.
5. WHEN all frontend tests are executed, THE test suite SHALL achieve a minimum of 70 percent code coverage for React components.

## Technology Stack

### Frontend

- **Framework**: React 18+
- **Language**: TypeScript 5+
- **Styling**: Bootstrap 5
- **Build Tool**: Vite or Create React App
- **Testing**: Jest and React Testing Library

### Backend

- **Framework**: FastAPI 0.100+
- **Language**: Python 3.11+
- **Validation**: Pydantic 2+
- **Testing**: pytest 7+
- **ASGI Server**: Uvicorn (for local development)

### AI/Machine Learning

- **Model**: Pre-trained YOLO (You Only Look Once) for object detection
- **Framework**: PyTorch or TensorFlow (depending on model implementation)
- **Computer Vision**: OpenCV or Pillow for image processing

### Cloud Infrastructure (AWS)

- **Compute**: AWS Lambda (container image support)
- **API Layer**: Amazon API Gateway (REST API)
- **Storage**: Amazon S3
- **Container Registry**: Amazon ECR
- **Infrastructure as Code**: AWS CDK (Python)

## High-Level System Architecture

```
User (Browser)
  ↓ [Upload Image]
React Frontend Application
  ↓ [HTTP POST /detect]
Amazon API Gateway
  ↓ [Invoke]
AWS Lambda Function (Docker Container)
  ↓ [Process Image]
Detection Service (YOLO Model)
  ↓ [Store Image]
Amazon S3 Bucket
  ↓ [Return Results]
React Frontend Application
  ↓ [Display Results]
User (Browser)
```

## Proposed Project Structure

```
car-damage-detection-api/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUpload.tsx
│   │   │   ├── LoadingIndicator.tsx
│   │   │   ├── ResultsDisplay.tsx
│   │   │   └── JsonViewer.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── detection.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── services/
│   │   │   ├── detection.py
│   │   │   └── storage.py
│   │   └── config.py
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_detection.py
│   │   └── conftest.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
│
├── infrastructure/
│   ├── app.py
│   ├── stacks/
│   │   └── car_damage_stack.py
│   ├── requirements.txt
│   └── cdk.json
│
├── .gitignore
└── README.md
```
