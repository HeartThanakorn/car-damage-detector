"""
Pytest configuration and fixtures for backend tests.

This module provides reusable test fixtures including:
- Test client for API testing
- Sample images for upload testing
- Mock S3 setup for storage testing
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image
from moto import mock_s3
import boto3
import os

from app.main import app
from app.config import settings


@pytest.fixture
def test_client():
    """
    Fixture providing a FastAPI TestClient for API integration tests.
    
    Returns:
        TestClient: Configured test client for making API requests
    """
    return TestClient(app)


@pytest.fixture
def sample_image_bytes():
    """
    Fixture providing a small valid JPEG image as bytes.
    
    Creates a 100x100 red RGB image suitable for testing.
    
    Returns:
        bytes: JPEG image data
    """
    img = Image.new('RGB', (100, 100), color='red')
    buf = BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def sample_png_image_bytes():
    """
    Fixture providing a small valid PNG image as bytes.
    
    Creates a 100x100 blue RGB image in PNG format.
    
    Returns:
        bytes: PNG image data
    """
    img = Image.new('RGB', (100, 100), color='blue')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def sample_webp_image_bytes():
    """
    Fixture providing a small valid WebP image as bytes.
    
    Creates a 100x100 green RGB image in WebP format.
    
    Returns:
        bytes: WebP image data
    """
    img = Image.new('RGB', (100, 100), color='green')
    buf = BytesIO()
    img.save(buf, format='WEBP')
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def large_image_bytes():
    """
    Fixture providing an image that exceeds the 10MB size limit.
    
    Returns:
        bytes: Large image data (>10MB)
    """
    # Create a large image that exceeds 10MB
    img = Image.new('RGB', (5000, 5000), color='white')
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=100)
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def mock_s3_bucket():
    """
    Fixture providing a mocked S3 environment using moto.
    
    Creates a mock S3 bucket for testing storage operations without
    actually connecting to AWS.
    
    Yields:
        boto3.client: Mocked S3 client
    """
    with mock_s3():
        # Create mock S3 client
        s3_client = boto3.client('s3', region_name='us-east-1')
        
        # Create the test bucket
        bucket_name = settings.S3_BUCKET_NAME
        s3_client.create_bucket(Bucket=bucket_name)
        
        yield s3_client


@pytest.fixture
def mock_yolo_model(monkeypatch):
    """
    Fixture providing a mocked YOLO model for detection testing.
    
    Mocks the ultralytics YOLO model to avoid loading actual model weights
    and provides predictable test results.
    
    Args:
        monkeypatch: Pytest monkeypatch fixture
    """
    class MockBox:
        """Mock YOLO box result"""
        def __init__(self):
            # Mock detection: [x1, y1, x2, y2, confidence, class_id]
            # Create mock tensors with .item() method
            self.data = [
                MockTensor([10.0, 20.0, 100.0, 150.0, 0.85, 0.0]),
                MockTensor([200.0, 50.0, 350.0, 200.0, 0.92, 1.0])
            ]
        
        def __len__(self):
            return len(self.data)
    
    class MockTensor:
        """Mock tensor with item() method"""
        def __init__(self, values):
            self.values = values
        
        def __getitem__(self, idx):
            return MockTensorValue(self.values[idx])
        
        def __iter__(self):
            return iter([MockTensorValue(v) for v in self.values])
    
    class MockTensorValue:
        """Mock tensor value with item() method"""
        def __init__(self, value):
            self.value = value
        
        def item(self):
            return self.value
        
        def __float__(self):
            return float(self.value)
        
        def __int__(self):
            return int(self.value)
    
    class MockResult:
        """Mock YOLO result"""
        def __init__(self):
            self.boxes = MockBox()
            self.names = {0: 'scratch', 1: 'dent'}
    
    class MockYOLO:
        """Mock YOLO model"""
        def __init__(self, model_path):
            self.model_path = model_path
        
        def __call__(self, image, conf=0.25, verbose=True):
            """Mock inference call"""
            return [MockResult()]
    
    # Mock the ultralytics module
    import sys
    from unittest.mock import MagicMock
    
    # Create mock ultralytics module if it doesn't exist
    if 'ultralytics' not in sys.modules:
        sys.modules['ultralytics'] = MagicMock()
    
    # Patch YOLO in ultralytics
    sys.modules['ultralytics'].YOLO = MockYOLO
    
    # Reset the class-level model cache to ensure fresh mock
    import app.services.detection
    app.services.detection.DamageDetectionService._model = None
    
    yield MockYOLO
    
    # Clean up: reset model cache after test
    app.services.detection.DamageDetectionService._model = None
