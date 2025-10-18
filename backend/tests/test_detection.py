"""
Unit tests for DamageDetectionService.

Tests the AI damage detection service including:
- Model loading (singleton pattern)
- Image preprocessing
- Detection result post-processing
- End-to-end detection flow
"""

import pytest
from PIL import Image
from io import BytesIO

from app.services.detection import DamageDetectionService
from app.models import Detection


class TestDamageDetectionService:
    """Test suite for DamageDetectionService"""
    
    def test_model_loading_singleton(self, mock_yolo_model):
        """Test that model is loaded only once using singleton pattern"""
        service1 = DamageDetectionService()
        service2 = DamageDetectionService()
        
        # Load model through both services
        model1 = service1.load_model()
        model2 = service2.load_model()
        
        # Both should reference the same model instance (singleton)
        assert model1 is model2
        assert DamageDetectionService._model is not None
    
    def test_preprocess_image_valid_jpeg(self, sample_image_bytes):
        """Test preprocessing of valid JPEG image"""
        service = DamageDetectionService()
        
        image = service.preprocess_image(sample_image_bytes)
        
        assert isinstance(image, Image.Image)
        assert image.mode == 'RGB'
        assert image.size == (100, 100)
    
    def test_preprocess_image_valid_png(self, sample_png_image_bytes):
        """Test preprocessing of valid PNG image"""
        service = DamageDetectionService()
        
        image = service.preprocess_image(sample_png_image_bytes)
        
        assert isinstance(image, Image.Image)
        assert image.mode == 'RGB'
        assert image.size == (100, 100)
    
    def test_preprocess_image_converts_rgba_to_rgb(self):
        """Test that RGBA images are converted to RGB"""
        service = DamageDetectionService()
        
        # Create RGBA image
        img = Image.new('RGBA', (50, 50), color=(255, 0, 0, 128))
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        rgba_bytes = buf.getvalue()
        
        image = service.preprocess_image(rgba_bytes)
        
        assert image.mode == 'RGB'
    
    def test_preprocess_image_invalid_data(self):
        """Test that invalid image data raises ValueError"""
        service = DamageDetectionService()
        
        invalid_bytes = b'not an image'
        
        with pytest.raises(ValueError, match="Failed to preprocess image"):
            service.preprocess_image(invalid_bytes)
    
    def test_postprocess_results_with_detections(self, mock_yolo_model):
        """Test post-processing of YOLO results with detections"""
        service = DamageDetectionService()
        service.load_model()
        
        # Create mock results (using the mock from fixture)
        from ultralytics import YOLO
        mock_model = YOLO('dummy_path')
        mock_results = mock_model(None)
        
        detections = service.postprocess_results(mock_results)
        
        # Should have 2 detections from mock
        assert len(detections) == 2
        
        # Verify first detection
        assert isinstance(detections[0], Detection)
        assert detections[0].bounding_box == (10, 20, 100, 150)
        assert detections[0].label == 'scratch'
        assert detections[0].confidence_score == 0.85
        
        # Verify second detection
        assert detections[1].bounding_box == (200, 50, 350, 200)
        assert detections[1].label == 'dent'
        assert detections[1].confidence_score == 0.92
    
    def test_postprocess_results_empty(self):
        """Test post-processing with no detections"""
        service = DamageDetectionService()
        
        # Create empty results
        class EmptyResult:
            boxes = None
        
        detections = service.postprocess_results([EmptyResult()])
        
        assert detections == []
    
    def test_postprocess_results_filters_low_confidence(self, mock_yolo_model, monkeypatch):
        """Test that detections below confidence threshold are filtered"""
        service = DamageDetectionService()
        service.confidence_threshold = 0.90  # Set high threshold
        service.load_model()
        
        # Create mock results with one detection below threshold
        from ultralytics import YOLO
        mock_model = YOLO('dummy_path')
        mock_results = mock_model(None)
        
        detections = service.postprocess_results(mock_results)
        
        # Only the detection with 0.92 confidence should pass
        assert len(detections) == 1
        assert detections[0].confidence_score == 0.92
    
    def test_detect_damages_end_to_end(self, mock_yolo_model, sample_image_bytes):
        """Test complete damage detection flow"""
        service = DamageDetectionService()
        
        detections = service.detect_damages(sample_image_bytes)
        
        # Should return list of Detection objects
        assert isinstance(detections, list)
        assert len(detections) == 2
        assert all(isinstance(d, Detection) for d in detections)
        
        # Verify detection structure
        detection = detections[0]
        assert len(detection.bounding_box) == 4
        assert isinstance(detection.label, str)
        assert 0.0 <= detection.confidence_score <= 1.0
    
    def test_detect_damages_with_invalid_image(self, mock_yolo_model):
        """Test detection with invalid image data"""
        service = DamageDetectionService()
        
        invalid_bytes = b'not an image'
        
        with pytest.raises(ValueError, match="Failed to preprocess image"):
            service.detect_damages(invalid_bytes)
    
    def test_confidence_threshold_from_settings(self):
        """Test that confidence threshold is loaded from settings"""
        service = DamageDetectionService()
        
        from app.config import settings
        assert service.confidence_threshold == settings.CONFIDENCE_THRESHOLD
