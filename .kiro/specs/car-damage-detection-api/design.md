# Design Document: Car Damage Detection API

## Overview

This design document outlines the technical architecture and implementation approach for the Car Damage Detection API. The system is built as a full-stack application with a React frontend, FastAPI backend, and AWS serverless infrastructure. The core functionality leverages a pre-trained YOLO model to detect vehicle damages from uploaded images and return structured results with bounding box coordinates.

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              React Frontend Application                    │  │
│  │  - Image Upload Component                                  │  │
│  │  - Results Visualization                                   │  │
│  │  - JSON Response Viewer                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS POST /detect
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS Cloud Infrastructure                    │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Amazon API Gateway (REST API)                 │  │
│  │  - CORS Configuration                                      │  │
│  │  - Request/Response Transformation                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              │ Lambda Proxy Integration          │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         AWS Lambda (Container Image)                       │  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │           FastAPI Application                        │  │  │
│  │  │  - /detect endpoint                                  │  │  │
│  │  │  - Request validation (Pydantic)                     │  │  │
│  │  │  - CORS middleware                                   │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                      │                                     │  │
│  │                      ▼                                     │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │         Detection Service                            │  │  │
│  │  │  - Image preprocessing                               │  │  │
│  │  │  - YOLO model inference                              │  │  │
│  │  │  - Post-processing                                   │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                      │                                     │  │
│  │                      ▼                                     │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │         Storage Service                              │  │  │
│  │  │  - S3 client wrapper                                 │  │  │
│  │  │  - Image upload logic                                │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              │ boto3 SDK                         │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Amazon S3 Bucket                              │  │
│  │  - Uploaded vehicle images                                 │  │
│  │  - Organized by unique identifiers                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         Amazon ECR (Container Registry)                    │  │
│  │  - Docker image for Lambda function                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Architecture

The infrastructure is provisioned using AWS CDK (Python), which defines:

- Lambda function with container image from ECR
- API Gateway REST API with Lambda proxy integration
- S3 bucket with appropriate IAM permissions
- IAM roles and policies for Lambda execution

## Components and Interfaces

### Frontend Components

#### 1. App Component (`App.tsx`)

- **Purpose**: Root component that orchestrates the application flow
- **State Management**:
  - `uploadedImage`: File | null - The selected image file
  - `isLoading`: boolean - Processing state indicator
  - `detectionResults`: DetectionResponse | null - API response data
  - `error`: string | null - Error message if request fails
- **Responsibilities**:
  - Coordinate child components
  - Manage application-level state
  - Handle API communication via the API service

#### 2. ImageUpload Component (`ImageUpload.tsx`)

- **Props**:
  - `onImageSelect: (file: File) => void` - Callback when image is selected
  - `disabled: boolean` - Disable upload during processing
- **Responsibilities**:
  - Render file input with accept attribute for images
  - Validate file type and size (max 10MB)
  - Display preview of selected image
  - Show validation error messages

#### 3. LoadingIndicator Component (`LoadingIndicator.tsx`)

- **Props**:
  - `isVisible: boolean` - Control visibility
- **Responsibilities**:
  - Display Bootstrap spinner during API calls
  - Show "Analyzing image..." message

#### 4. ResultsDisplay Component (`ResultsDisplay.tsx`)

- **Props**:
  - `imageUrl: string` - URL or data URL of uploaded image
  - `detections: Detection[]` - Array of detection objects
- **Responsibilities**:
  - Render image on HTML canvas
  - Draw bounding boxes with labels and confidence scores
  - Use different colors for different damage types
  - Scale coordinates appropriately for display

#### 5. JsonViewer Component (`JsonViewer.tsx`)

- **Props**:
  - `data: DetectionResponse` - Raw API response
- **Responsibilities**:
  - Display formatted JSON with syntax highlighting
  - Provide collapsible sections for readability
  - Use monospace font for code display

### Frontend Services

#### API Service (`services/api.ts`)

```typescript
interface Detection {
  bounding_box: [number, number, number, number];
  label: string;
  confidence_score: number;
}

interface DetectionResponse {
  detections: Detection[];
  image_id: string;
  processing_time_ms: number;
}

class DamageDetectionAPI {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async detectDamage(imageFile: File): Promise<DetectionResponse> {
    const formData = new FormData();
    formData.append("file", imageFile);

    const response = await fetch(`${this.baseUrl}/detect`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }
}
```

### Backend Components

#### 1. Main Application (`app/main.py`)

- **Purpose**: FastAPI application entry point
- **Responsibilities**:
  - Initialize FastAPI app with CORS middleware
  - Configure CORS origins for development and production
  - Define health check endpoint
  - Register API routes
  - Configure exception handlers

**CORS Configuration**:

```python
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://my-damage-detector-app.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)
```

#### 2. API Models (`app/models.py`)

- **Purpose**: Pydantic models for request/response validation
- **Models**:

```python
from pydantic import BaseModel, Field
from typing import List, Tuple

class Detection(BaseModel):
    bounding_box: Tuple[int, int, int, int] = Field(
        description="Bounding box coordinates [x1, y1, x2, y2]"
    )
    label: str = Field(description="Damage type label")
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence score between 0 and 1"
    )

class DetectionResponse(BaseModel):
    detections: List[Detection]
    image_id: str = Field(description="Unique identifier for uploaded image")
    processing_time_ms: float = Field(description="Processing time in milliseconds")

class ErrorResponse(BaseModel):
    error: str
    detail: str
```

#### 3. Detection Service (`app/services/detection.py`)

- **Purpose**: Encapsulate AI model inference logic
- **Key Methods**:
  - `load_model()`: Load pre-trained YOLO model (singleton pattern)
  - `preprocess_image(image_bytes: bytes) -> np.ndarray`: Prepare image for model
  - `detect_damages(image: np.ndarray) -> List[Detection]`: Run inference
  - `postprocess_results(raw_results) -> List[Detection]`: Convert model output to API format

**Model Loading Strategy**:

- Load model once during Lambda cold start
- Cache model in global variable for warm starts
- Use YOLOv8 or YOLOv5 from Ultralytics
- Model weights bundled in Docker image

**Detection Logic**:

```python
class DamageDetectionService:
    def __init__(self):
        self.model = None
        self.confidence_threshold = 0.25

    def load_model(self):
        if self.model is None:
            # Load YOLO model (cached globally)
            from ultralytics import YOLO
            self.model = YOLO('path/to/weights.pt')

    def detect_damages(self, image_bytes: bytes) -> List[Detection]:
        self.load_model()

        # Convert bytes to image
        image = Image.open(io.BytesIO(image_bytes))

        # Run inference
        results = self.model(image, conf=self.confidence_threshold)

        # Parse results
        detections = []
        for result in results[0].boxes.data:
            x1, y1, x2, y2, conf, cls = result
            detections.append(Detection(
                bounding_box=(int(x1), int(y1), int(x2), int(y2)),
                label=self.model.names[int(cls)],
                confidence_score=float(conf)
            ))

        return detections
```

#### 4. Storage Service (`app/services/storage.py`)

- **Purpose**: Handle S3 operations
- **Key Methods**:
  - `upload_image(image_bytes: bytes, image_id: str) -> str`: Upload to S3
  - `generate_image_id() -> str`: Create unique identifier (UUID)
  - `get_bucket_name() -> str`: Retrieve bucket name from environment

```python
import boto3
import uuid
from typing import BinaryIO

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    def generate_image_id(self) -> str:
        return str(uuid.uuid4())

    def upload_image(self, image_bytes: bytes, image_id: str) -> str:
        key = f"uploads/{image_id}.jpg"
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=image_bytes,
            ContentType='image/jpeg'
        )
        return key
```

#### 5. Configuration (`app/config.py`)

- **Purpose**: Centralize configuration management
- **Settings**:
  - S3 bucket name (from environment)
  - Model path
  - Confidence threshold
  - Max file size
  - Allowed file extensions

### Backend API Endpoints

#### POST /detect

- **Purpose**: Process uploaded image and return damage detections
- **Request**:
  - Content-Type: multipart/form-data
  - Body: `file` field containing image file
- **Response** (200 OK):

```json
{
  "detections": [
    {
      "bounding_box": [120, 45, 280, 190],
      "label": "scratch",
      "confidence_score": 0.87
    },
    {
      "bounding_box": [350, 200, 480, 310],
      "label": "dent",
      "confidence_score": 0.92
    }
  ],
  "image_id": "a3f2c8d1-4b5e-6789-0abc-def123456789",
  "processing_time_ms": 1245.67
}
```

- **Error Responses**:
  - 400: Invalid file type or size
  - 413: File too large
  - 500: Internal server error

**Implementation**:

```python
@app.post("/detect", response_model=DetectionResponse)
async def detect_damage(file: UploadFile = File(...)):
    start_time = time.time()

    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read image bytes
    image_bytes = await file.read()

    # Validate file size (10MB)
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")

    # Generate unique ID
    storage_service = StorageService()
    image_id = storage_service.generate_image_id()

    # Upload to S3
    storage_service.upload_image(image_bytes, image_id)

    # Run detection
    detection_service = DamageDetectionService()
    detections = detection_service.detect_damages(image_bytes)

    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000

    return DetectionResponse(
        detections=detections,
        image_id=image_id,
        processing_time_ms=processing_time
    )
```

#### GET /health

- **Purpose**: Health check endpoint for monitoring
- **Response** (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T12:34:56Z"
}
```

## Data Models

### Frontend TypeScript Types

```typescript
// types/detection.ts
export interface Detection {
  bounding_box: [number, number, number, number];
  label: string;
  confidence_score: number;
}

export interface DetectionResponse {
  detections: Detection[];
  image_id: string;
  processing_time_ms: number;
}

export interface ErrorResponse {
  error: string;
  detail: string;
}
```

### Backend Pydantic Models

Defined in `app/models.py` (see Components section above)

### S3 Storage Structure

```
s3://car-damage-detection-bucket/
└── uploads/
    ├── a3f2c8d1-4b5e-6789-0abc-def123456789.jpg
    ├── b7e9d2f3-8c1a-4567-89ab-cdef01234567.jpg
    └── ...
```

## Error Handling

### Frontend Error Handling

1. **File Validation Errors**:

   - Display user-friendly message in ImageUpload component
   - Prevent API call if validation fails

2. **Network Errors**:

   - Catch fetch errors in API service
   - Display error message in App component
   - Provide retry option

3. **API Errors**:
   - Parse error response from backend
   - Display specific error message
   - Log errors to console for debugging

**Error Display Component**:

```typescript
interface ErrorDisplayProps {
  error: string;
  onDismiss: () => void;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onDismiss }) => (
  <div className="alert alert-danger alert-dismissible" role="alert">
    <strong>Error:</strong> {error}
    <button type="button" className="btn-close" onClick={onDismiss}></button>
  </div>
);
```

### Backend Error Handling

1. **Request Validation Errors**:

   - FastAPI automatically validates with Pydantic
   - Returns 422 with detailed validation errors

2. **File Processing Errors**:

   - Catch exceptions during image processing
   - Return 400 with descriptive message

3. **Model Inference Errors**:

   - Catch model errors
   - Log to CloudWatch
   - Return 500 with generic message (don't expose internals)

4. **S3 Upload Errors**:
   - Retry logic with exponential backoff
   - Return 500 if all retries fail

**Exception Handler**:

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )
```

## Infrastructure Design (AWS CDK)

### CDK Stack Structure

```python
# infrastructure/stacks/car_damage_stack.py
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_ecr as ecr,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)

class CarDamageDetectionStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # S3 Bucket for image storage
        image_bucket = s3.Bucket(
            self, "ImageBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT],
                allowed_origins=["*"],
                allowed_headers=["*"]
            )]
        )

        # ECR Repository for Docker image
        ecr_repo = ecr.Repository(
            self, "BackendRepository",
            removal_policy=RemovalPolicy.DESTROY
        )

        # Lambda Function from container image
        lambda_function = lambda_.DockerImageFunction(
            self, "DetectionFunction",
            code=lambda_.DockerImageCode.from_ecr(
                repository=ecr_repo,
                tag="latest"
            ),
            memory_size=3008,  # 3GB for model inference
            timeout=Duration.seconds(30),
            environment={
                "S3_BUCKET_NAME": image_bucket.bucket_name
            }
        )

        # Grant S3 permissions to Lambda
        image_bucket.grant_read_write(lambda_function)

        # API Gateway
        api = apigw.LambdaRestApi(
            self, "DetectionApi",
            handler=lambda_function,
            proxy=True,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )
```

### Resource Configuration

1. **Lambda Function**:

   - Memory: 3GB (required for YOLO model)
   - Timeout: 30 seconds
   - Container image from ECR
   - Environment variables: S3_BUCKET_NAME

2. **API Gateway**:

   - REST API with Lambda proxy integration
   - CORS enabled
   - Binary media types: image/jpeg, image/png

3. **S3 Bucket**:

   - Private bucket
   - Lifecycle policy: delete objects after 30 days (optional)
   - Encryption at rest

4. **IAM Roles**:
   - Lambda execution role with S3 read/write permissions
   - CloudWatch Logs permissions

## Testing Strategy

### Frontend Testing

**Unit Tests** (Jest + React Testing Library):

1. **ImageUpload Component**:

   - Test file selection triggers callback
   - Test file size validation
   - Test file type validation
   - Test error message display

2. **ResultsDisplay Component**:

   - Test canvas rendering with mock detections
   - Test bounding box drawing
   - Test label display

3. **API Service**:
   - Mock fetch calls
   - Test successful response parsing
   - Test error handling

**Example Test**:

```typescript
describe("ImageUpload", () => {
  it("should reject files larger than 10MB", () => {
    const { getByLabelText, getByText } = render(
      <ImageUpload onImageSelect={jest.fn()} disabled={false} />
    );

    const file = new File(["x".repeat(11 * 1024 * 1024)], "large.jpg", {
      type: "image/jpeg",
    });

    const input = getByLabelText(/upload/i);
    fireEvent.change(input, { target: { files: [file] } });

    expect(getByText(/exceeds 10 megabytes/i)).toBeInTheDocument();
  });
});
```

### Backend Testing

**Unit Tests** (pytest):

1. **Detection Service**:

   - Test model loading
   - Test image preprocessing
   - Test detection result formatting
   - Mock YOLO model for fast tests

2. **Storage Service**:

   - Test image ID generation
   - Test S3 upload (mocked with moto)
   - Test error handling

3. **API Models**:
   - Test Pydantic validation
   - Test field constraints

**Integration Tests** (pytest):

1. **API Endpoint Tests**:
   - Test /detect with valid image
   - Test /detect with invalid file type
   - Test /detect with oversized file
   - Test /health endpoint

**Example Test**:

```python
def test_detect_endpoint_success(test_client, sample_image):
    """Test successful damage detection"""
    files = {'file': ('test.jpg', sample_image, 'image/jpeg')}
    response = test_client.post('/detect', files=files)

    assert response.status_code == 200
    data = response.json()
    assert 'detections' in data
    assert 'image_id' in data
    assert isinstance(data['detections'], list)

def test_detect_endpoint_invalid_file_type(test_client):
    """Test rejection of non-image files"""
    files = {'file': ('test.txt', b'not an image', 'text/plain')}
    response = test_client.post('/detect', files=files)

    assert response.status_code == 400
    assert 'must be an image' in response.json()['detail']
```

**Test Fixtures** (`conftest.py`):

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def sample_image():
    # Return bytes of a small test image
    from PIL import Image
    import io
    img = Image.new('RGB', (100, 100), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()
```

### Infrastructure Testing

1. **CDK Snapshot Tests**:

   - Verify CloudFormation template generation
   - Ensure resources are created correctly

2. **Manual Deployment Tests**:
   - Deploy to test AWS account
   - Verify API Gateway endpoint
   - Test end-to-end flow

## Deployment Process

### 1. Build Docker Image

```bash
cd backend
docker build -t car-damage-detection:latest .
```

### 2. Push to ECR

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag car-damage-detection:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/car-damage-detection:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/car-damage-detection:latest
```

### 3. Deploy CDK Stack

```bash
cd infrastructure
cdk deploy
```

### 4. Build and Deploy Frontend

```bash
cd frontend
npm run build
# Deploy to hosting service (S3 + CloudFront, Vercel, Netlify, etc.)
```

## Performance Considerations

1. **Lambda Cold Starts**:

   - Container image size optimization
   - Model weights optimization
   - Consider provisioned concurrency for production

2. **Model Inference Time**:

   - Use optimized YOLO model (YOLOv8n for speed)
   - Consider GPU Lambda instances if available
   - Target < 5 seconds inference time

3. **Image Upload Size**:

   - 10MB limit balances quality and upload time
   - Consider image compression on frontend

4. **S3 Storage Costs**:
   - Implement lifecycle policy to delete old images
   - Consider S3 Intelligent-Tiering

## Security Considerations

1. **API Security**:

   - CORS properly configured
   - Input validation on all endpoints
   - Rate limiting (API Gateway throttling)

2. **S3 Security**:

   - Private bucket (no public access)
   - Signed URLs if images need to be retrieved
   - Encryption at rest

3. **Lambda Security**:

   - Least privilege IAM role
   - No hardcoded credentials
   - Environment variables for configuration

4. **Frontend Security**:
   - No sensitive data in client code
   - HTTPS only
   - Content Security Policy headers
