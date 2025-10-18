"""
Hugging Face Car Damage Detection Service

This module provides AI-powered damage detection using Hugging Face transformers model.
Model: beingamit99/car_damage_detection
"""

import os
from typing import List, Optional

from app.models import Detection
from app.config import settings
from app.services.base_detection import BaseDetectionService


class HuggingFaceDetectionService(BaseDetectionService):
    """
    Service for detecting vehicle damages using Hugging Face image classification model.
    
    Implements singleton pattern for model loading to optimize performance
    and reuse the model across multiple invocations.
    """
    
    _pipeline: Optional[object] = None
    
    def __init__(self):
        """Initialize the detection service."""
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.use_mock = os.getenv('USE_MOCK_MODEL', 'false').lower() == 'true'
        self.model_name = settings.HUGGINGFACE_MODEL
    
    @classmethod
    def load_model(cls):
        """
        Load the pre-trained Hugging Face model using pipeline.
        
        Uses singleton pattern to load the model only once and cache it
        at the class level for reuse across multiple invocations.
        """
        if cls._pipeline is None:
            from transformers import pipeline
            
            model_name = settings.HUGGINGFACE_MODEL
            print(f"Loading Hugging Face model: {model_name}")
            
            cls._pipeline = pipeline("image-classification", model=model_name)
            
            print(f"Model loaded successfully!")
        
        return cls._pipeline
    
    def postprocess_results(self, predictions, image_size) -> List[Detection]:
        """
        Convert model output to Detection objects.
        
        Since this is a classification model (not object detection),
        we create a single detection covering the whole image with the predicted class.
        
        Args:
            predictions: List of predictions from pipeline
            image_size: Tuple of (width, height) for bounding box
            
        Returns:
            List of Detection objects
        """
        detections = []
        
        # Get top prediction
        if predictions and len(predictions) > 0:
            top_prediction = predictions[0]
            label = top_prediction['label']
            score = top_prediction['score']
            
            # Filter by confidence threshold
            if score >= self.confidence_threshold:
                # Create detection covering the whole image
                width, height = image_size
                detection = Detection(
                    bounding_box=(0, 0, width, height),
                    label=label,
                    confidence_score=score
                )
                detections.append(detection)
        
        return detections
    
    def detect_damages(self, image_bytes: bytes) -> List[Detection]:
        """
        Detect damages in the provided image using Hugging Face model.
        
        Args:
            image_bytes: Raw bytes of the uploaded image
            
        Returns:
            List of Detection objects containing labels and confidence scores
            
        Raises:
            ValueError: If image preprocessing fails
            Exception: If model inference fails
        """
        # Mock mode for testing
        if self.use_mock:
            return self._generate_mock_detections(image_bytes)
        
        # Load pipeline
        pipe = self.load_model()
        
        # Preprocess image
        image = self.preprocess_image(image_bytes)
        image_size = image.size
        
        # Run inference using pipeline
        predictions = pipe(image)
        
        # Post-process and convert to Detection objects
        detections = self.postprocess_results(predictions, image_size)
        
        return detections
