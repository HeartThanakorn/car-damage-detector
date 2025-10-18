from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timezone
import time
import logging

from app.models import DetectionResponse, ErrorResponse
from app.services.detection import DamageDetectionService
from app.services.storage import StorageService
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Car Damage Detection API",
    description="API for detecting vehicle damage using AI",
    version="1.0.0"
)

# CORS Configuration
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


# Exception Handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors (422) and return as 400 Bad Request.
    
    This handler catches validation errors from request parsing and formats them
    using the ErrorResponse model for consistency.
    """
    error_details = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    logger.warning(f"Validation error on {request.url.path}: {error_details}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "detail": f"Request validation failed: {error_details}"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions and format them using ErrorResponse model.
    
    This handler ensures all HTTP exceptions return a consistent error format
    and logs appropriate messages based on the status code.
    """
    # Determine error category based on status code
    if exc.status_code == 400:
        error_type = "Bad Request"
        logger.warning(f"Bad request on {request.url.path}: {exc.detail}")
    elif exc.status_code == 413:
        error_type = "Payload Too Large"
        logger.warning(f"File size exceeded on {request.url.path}: {exc.detail}")
    elif exc.status_code >= 500:
        error_type = "Internal Server Error"
        logger.error(f"Server error on {request.url.path}: {exc.detail}")
    else:
        error_type = "Error"
        logger.info(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_type,
            "detail": exc.detail
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected exceptions.
    
    This handler catches any unhandled exceptions, logs them with full traceback,
    and returns a generic 500 error to avoid exposing internal details.
    """
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred while processing your request"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/detect", response_model=DetectionResponse, responses={
    400: {"model": ErrorResponse, "description": "Invalid file type or format"},
    413: {"model": ErrorResponse, "description": "File size exceeds limit"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def detect_damage(file: UploadFile = File(...)):
    """
    Detect vehicle damages in an uploaded image.
    
    This endpoint accepts an image file, processes it using a pre-trained YOLO model,
    stores it in S3, and returns detected damages with bounding boxes and confidence scores.
    
    Args:
        file: Uploaded image file (JPEG, PNG, or WebP format, max 10MB)
    
    Returns:
        DetectionResponse containing:
        - detections: List of detected damages with bounding boxes, labels, and confidence scores
        - image_id: Unique identifier for the uploaded image
        - processing_time_ms: Total processing time in milliseconds
    
    Raises:
        HTTPException 400: If file is not an image or has invalid format
        HTTPException 413: If file size exceeds 10MB limit
        HTTPException 500: If processing fails due to internal error
    """
    start_time = time.time()
    
    try:
        # Validate file type (JPEG, PNG, WebP)
        if not file.content_type or file.content_type not in settings.ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file type uploaded: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Please upload a JPEG, PNG, or WebP image. Received: {file.content_type}"
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate file size (10MB limit)
        file_size = len(image_bytes)
        if file_size > settings.MAX_FILE_SIZE_BYTES:
            logger.warning(f"File size exceeds limit: {file_size} bytes (max: {settings.MAX_FILE_SIZE_BYTES})")
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit. Uploaded file is {file_size / (1024 * 1024):.2f}MB"
            )
        
        logger.info(f"Processing image: {file.filename}, size: {file_size} bytes, type: {file.content_type}")
        
        # Generate unique image ID using StorageService
        storage_service = StorageService()
        image_id = storage_service.generate_image_id()
        logger.info(f"Generated image ID: {image_id}")
        
        # Upload image to S3 using StorageService
        try:
            s3_key = storage_service.upload_image(
                image_bytes=image_bytes,
                image_id=image_id,
                content_type=file.content_type
            )
            logger.info(f"Image uploaded to S3: {s3_key}")
        except Exception as e:
            logger.error(f"Failed to upload image to S3: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store image: {str(e)}"
            )
        
        # Process image using DamageDetectionService to get detections
        try:
            detection_service = DamageDetectionService()
            detections = detection_service.detect_damages(image_bytes)
            logger.info(f"Detection complete: found {len(detections)} damages")
        except ValueError as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image format: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Detection failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Damage detection failed: {str(e)}"
            )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        logger.info(f"Total processing time: {processing_time_ms:.2f}ms")
        
        # Return DetectionResponse with detections, image_id, and processing_time_ms
        return DetectionResponse(
            detections=detections,
            image_id=image_id,
            processing_time_ms=processing_time_ms
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in /detect endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
