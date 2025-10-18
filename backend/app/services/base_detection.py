"""
Base Detection Service

Shared functionality for all detection services.
"""

import io
from typing import List
from PIL import Image

from app.models import Detection


class BaseDetectionService:
    """Base class for detection services with shared functionality"""
    
    @staticmethod
    def preprocess_image(image_bytes: bytes) -> Image.Image:
        """
        Preprocess image bytes into PIL Image format.
        
        Args:
            image_bytes: Raw image bytes from uploaded file
            
        Returns:
            PIL Image object ready for model inference
            
        Raises:
            ValueError: If image bytes cannot be decoded
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            raise ValueError(f"Failed to preprocess image: {str(e)}")
    
    @staticmethod
    def _generate_mock_detections(image_bytes: bytes) -> List[Detection]:
        """
        Generate mock detections for testing purposes.
        
        Args:
            image_bytes: Raw bytes of the uploaded image
            
        Returns:
            List of mock Detection objects
        """
        try:
            image = BaseDetectionService.preprocess_image(image_bytes)
            width, height = image.size
        except:
            width, height = 640, 480
        
        # Generate realistic mock detections
        mock_detections = [
            Detection(
                bounding_box=(
                    int(width * 0.15),
                    int(height * 0.10),
                    int(width * 0.45),
                    int(height * 0.35)
                ),
                label="scratch",
                confidence_score=0.87
            ),
            Detection(
                bounding_box=(
                    int(width * 0.55),
                    int(height * 0.40),
                    int(width * 0.75),
                    int(height * 0.65)
                ),
                label="dent",
                confidence_score=0.92
            ),
            Detection(
                bounding_box=(
                    int(width * 0.20),
                    int(height * 0.60),
                    int(width * 0.40),
                    int(height * 0.85)
                ),
                label="paint_damage",
                confidence_score=0.78
            )
        ]
        
        return mock_detections
