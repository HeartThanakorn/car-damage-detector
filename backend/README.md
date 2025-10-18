# Car Damage Detection API - Backend

FastAPI backend service for detecting vehicle damage using AI.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   └── services/            # Service layer (detection, storage)
│       └── __init__.py
├── tests/                   # Test suite
│   └── __init__.py
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container image definition
└── pytest.ini              # Pytest configuration
```

## Setup

### Local Development

1. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

4. Access the API:

- API: http://localhost:8080
- Interactive docs: http://localhost:8080/docs
- Health check: http://localhost:8080/health

## Configuration

Configuration is managed through environment variables in `app/config.py`:

- `S3_BUCKET_NAME`: S3 bucket for image storage (default: "car-damage-detection-bucket")
- `MODEL_PATH`: Path to YOLO model weights (default: "models/yolov8n.pt")
- `CONFIDENCE_THRESHOLD`: Detection confidence threshold (default: 0.25)
- `MAX_FILE_SIZE_MB`: Maximum upload file size in MB (default: 10)

## Docker

Build the Docker image:

```bash
docker build -t car-damage-detection:latest .
```

Run the container:

```bash
docker run -p 8080:8080 \
  -e S3_BUCKET_NAME=your-bucket-name \
  car-damage-detection:latest
```

## Testing

Run tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

## API Endpoints

### GET /health

Health check endpoint

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T12:34:56Z"
}
```

### POST /detect

(To be implemented in subsequent tasks)
