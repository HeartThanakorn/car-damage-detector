from pydantic import BaseModel, Field
from typing import List, Tuple


class Detection(BaseModel):
    """
    Represents a single damage detection result.
    
    Contains the bounding box coordinates, damage type label, and confidence score
    for a detected damage area in the vehicle image.
    """
    bounding_box: Tuple[int, int, int, int] = Field(
        description="Bounding box coordinates in format [x1, y1, x2, y2] where (x1, y1) is top-left and (x2, y2) is bottom-right corner in pixels"
    )
    label: str = Field(
        description="Damage type label (e.g., 'scratch', 'dent', 'crack', 'broken_part')"
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 indicating model certainty"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "bounding_box": [120, 45, 280, 190],
                "label": "scratch",
                "confidence_score": 0.87
            }
        }


class DetectionResponse(BaseModel):
    """
    Response model for the damage detection endpoint.
    
    Contains the list of detected damages, unique image identifier,
    and processing time metrics.
    """
    detections: List[Detection] = Field(
        description="List of detected damages with bounding boxes and confidence scores"
    )
    image_id: str = Field(
        description="Unique identifier (UUID) for the uploaded image stored in S3"
    )
    processing_time_ms: float = Field(
        description="Total processing time in milliseconds from upload to response"
    )

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class ErrorResponse(BaseModel):
    """
    Standard error response model for API errors.
    
    Provides consistent error formatting across all endpoints.
    """
    error: str = Field(
        description="High-level error category or type"
    )
    detail: str = Field(
        description="Detailed error message explaining what went wrong"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "Invalid file type. Please upload a JPEG, PNG, or WebP image."
            }
        }
