"""
Damage Detection Service

This module provides AI-powered damage detection using either YOLO or Hugging Face models.
It handles model loading, image preprocessing, inference, and result post-processing.
"""

import os
from typing import List, Optional
import numpy as np

from app.models import Detection
from app.config import settings
from app.services.base_detection import BaseDetectionService


def get_detection_service():
    """
    Factory function to get the appropriate detection service based on configuration.
    
    Returns:
        DamageDetectionService or HuggingFaceDetectionService based on MODEL_TYPE setting
    """
    model_type = settings.MODEL_TYPE.lower()
    
    if model_type == "huggingface":
        from app.services.huggingface_detection import HuggingFaceDetectionService
        return HuggingFaceDetectionService()
    else:
        return DamageDetectionService()


class DamageDetectionService(BaseDetectionService):
    """
    Service for detecting vehicle damages using YOLO object detection model.
    
    Implements singleton pattern for model loading to optimize Lambda cold starts
    and reuse the model across warm invocations.
    """
    
    _model: Optional[object] = None  # Class-level model cache
    
    def __init__(self):
        """Initialize the detection service."""
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.use_mock = os.getenv('USE_MOCK_MODEL', 'false').lower() == 'true'
    
    @classmethod
    def load_model(cls):
        """
        Load the pre-trained YOLO model.
        
        Uses singleton pattern to load the model only once and cache it
        at the class level for reuse across multiple invocations.
        This is critical for Lambda efficiency to avoid reloading on warm starts.
        """
        if cls._model is None:
            from ultralytics import YOLO
            cls._model = YOLO(settings.MODEL_PATH)
        return cls._model
    
    def postprocess_results(self, raw_results) -> List[Detection]:
        """
        Convert YOLO model output to Detection objects.
        
        Args:
            raw_results: Raw results from YOLO model inference
            
        Returns:
            List of Detection objects with bounding boxes, labels, and confidence scores
        """
        detections = []
        
        # YOLO results structure: results[0].boxes contains detection data
        if len(raw_results) > 0 and hasattr(raw_results[0], 'boxes'):
            boxes = raw_results[0].boxes
            
            # Extract detection data
            if boxes is not None and len(boxes) > 0:
                # boxes.data contains [x1, y1, x2, y2, confidence, class_id]
                for box in boxes.data:
                    x1, y1, x2, y2, conf, cls = box
                    
                    # Filter by confidence threshold
                    if float(conf) >= self.confidence_threshold:
                        # Get class name from model
                        class_id = int(cls)
                        label = raw_results[0].names[class_id]
                        
                        detection = Detection(
                            bounding_box=(
                                int(x1.item()),
                                int(y1.item()),
                                int(x2.item()),
                                int(y2.item())
                            ),
                            label=label,
                            confidence_score=float(conf.item())
                        )
                        detections.append(detection)
        
        return detections
    
    def detect_damages(self, image_bytes: bytes) -> List[Detection]:
        """
        Detect damages in the provided image.
        
        This is the main entry point for damage detection. It handles:
        1. Loading the model (if not already loaded)
        2. Preprocessing the image
        3. Running inference
        4. Post-processing results
        
        Args:
            image_bytes: Raw bytes of the uploaded image
            
        Returns:
            List of Detection objects containing bounding boxes, labels, and confidence scores
            
        Raises:
            ValueError: If image preprocessing fails
            Exception: If model inference fails
        """
        # Mock mode for testing without AI model
        if self.use_mock:
            return self._generate_mock_detections(image_bytes)
        
        # Load model (singleton pattern ensures it's only loaded once)
        model = self.load_model()
        
        # Preprocess image
        image = self.preprocess_image(image_bytes)
        
        # Run inference with confidence threshold
        raw_results = model(image, conf=self.confidence_threshold, verbose=False)
        
        # Post-process and convert to Detection objects
        detections = self.postprocess_results(raw_results)
        
        return detections
