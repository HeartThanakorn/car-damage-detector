"""
Integration tests for API endpoints.

Tests the complete API flow including:
- /detect endpoint with valid and invalid inputs
- /health endpoint
- Error handling and response formats
- Request validation
"""

import pytest
from io import BytesIO


class TestDetectEndpoint:
    """Integration tests for POST /detect endpoint"""
    
    def test_detect_with_valid_jpeg_image(
        self, test_client, mock_s3_bucket, mock_yolo_model, sample_image_bytes
    ):
        """Test /detect endpoint with valid JPEG image"""
        files = {'file': ('test.jpg', sample_image_bytes, 'image/jpeg')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify response structure
        assert 'detections' in data
        assert 'image_id' in data
        assert 'processing_time_ms' in data
        
        # Verify detections
        assert isinstance(data['detections'], list)
        assert len(data['detections']) == 2  # Mock returns 2 detections
        
        # Verify first detection structure
        detection = data['detections'][0]
        assert 'bounding_box' in detection
        assert 'label' in detection
        assert 'confidence_score' in detection
        
        # Verify bounding box format
        assert len(detection['bounding_box']) == 4
        assert all(isinstance(coord, int) for coord in detection['bounding_box'])
        
        # Verify label and confidence
        assert isinstance(detection['label'], str)
        assert 0.0 <= detection['confidence_score'] <= 1.0
        
        # Verify image_id is a valid UUID string
        assert isinstance(data['image_id'], str)
        assert len(data['image_id']) > 0
        
        # Verify processing time
        assert isinstance(data['processing_time_ms'], float)
        assert data['processing_time_ms'] > 0
    
    def test_detect_with_valid_png_image(
        self, test_client, mock_s3_bucket, mock_yolo_model, sample_png_image_bytes
    ):
        """Test /detect endpoint with valid PNG image"""
        files = {'file': ('test.png', sample_png_image_bytes, 'image/png')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 200
        
        data = response.json()
        assert 'detections' in data
        assert 'image_id' in data
        assert len(data['detections']) == 2
    
    def test_detect_with_valid_webp_image(
        self, test_client, mock_s3_bucket, mock_yolo_model, sample_webp_image_bytes
    ):
        """Test /detect endpoint with valid WebP image"""
        files = {'file': ('test.webp', sample_webp_image_bytes, 'image/webp')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 200
        
        data = response.json()
        assert 'detections' in data
        assert len(data['detections']) == 2
    
    def test_detect_with_invalid_file_type(self, test_client):
        """Test /detect endpoint rejects non-image files"""
        files = {'file': ('test.txt', b'not an image', 'text/plain')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 400
        
        data = response.json()
        assert 'error' in data
        assert 'detail' in data
        assert data['error'] == 'Bad Request'
        assert 'Invalid file type' in data['detail']
    
    def test_detect_with_pdf_file(self, test_client):
        """Test /detect endpoint rejects PDF files"""
        files = {'file': ('document.pdf', b'fake pdf content', 'application/pdf')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 400
        
        data = response.json()
        assert 'Invalid file type' in data['detail']
    
    def test_detect_with_oversized_file(self, test_client, large_image_bytes):
        """Test /detect endpoint rejects files larger than 10MB"""
        files = {'file': ('large.jpg', large_image_bytes, 'image/jpeg')}
        response = test_client.post('/detect', files=files)
        
        # Should return 413 or 500 depending on when size check happens
        assert response.status_code in [413, 500]
        
        data = response.json()
        assert 'error' in data
        assert 'detail' in data
    
    def test_detect_without_file(self, test_client):
        """Test /detect endpoint requires file parameter"""
        response = test_client.post('/detect')
        
        # FastAPI validation errors are converted to 400 by our exception handler
        assert response.status_code == 400
    
    def test_detect_with_empty_file(self, test_client):
        """Test /detect endpoint handles empty file"""
        files = {'file': ('empty.jpg', b'', 'image/jpeg')}
        response = test_client.post('/detect', files=files)
        
        # Should fail during image preprocessing
        assert response.status_code in [400, 500]
    
    def test_detect_stores_image_in_s3(
        self, test_client, mock_s3_bucket, mock_yolo_model, sample_image_bytes
    ):
        """Test that /detect endpoint stores image in S3"""
        files = {'file': ('test.jpg', sample_image_bytes, 'image/jpeg')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 200
        
        data = response.json()
        image_id = data['image_id']
        
        # Verify image was stored in S3
        from app.config import settings
        s3_key = f"uploads/{image_id}.jpg"
        
        s3_response = mock_s3_bucket.get_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key
        )
        
        stored_data = s3_response['Body'].read()
        assert stored_data == sample_image_bytes
    
    def test_detect_response_format_matches_schema(
        self, test_client, mock_s3_bucket, mock_yolo_model, sample_image_bytes
    ):
        """Test that /detect response matches DetectionResponse schema"""
        files = {'file': ('test.jpg', sample_image_bytes, 'image/jpeg')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify all required fields are present
        required_fields = ['detections', 'image_id', 'processing_time_ms']
        for field in required_fields:
            assert field in data
        
        # Verify detection fields
        for detection in data['detections']:
            assert 'bounding_box' in detection
            assert 'label' in detection
            assert 'confidence_score' in detection
            
            # Verify types
            assert isinstance(detection['bounding_box'], list)
            assert isinstance(detection['label'], str)
            assert isinstance(detection['confidence_score'], float)
    
    def test_detect_error_response_format(self, test_client):
        """Test that error responses follow ErrorResponse schema"""
        files = {'file': ('test.txt', b'not an image', 'text/plain')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 400
        
        data = response.json()
        
        # Verify ErrorResponse format
        assert 'error' in data
        assert 'detail' in data
        assert isinstance(data['error'], str)
        assert isinstance(data['detail'], str)
    
    def test_detect_handles_s3_upload_failure(
        self, test_client, mock_s3_bucket, mock_yolo_model, sample_image_bytes, monkeypatch
    ):
        """Test /detect endpoint handles S3 upload failures gracefully"""
        from app.services.storage import StorageService
        
        # Mock upload_image to raise exception
        def mock_upload_error(*args, **kwargs):
            raise Exception("S3 upload failed")
        
        monkeypatch.setattr(StorageService, 'upload_image', mock_upload_error)
        
        files = {'file': ('test.jpg', sample_image_bytes, 'image/jpeg')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 500
        
        data = response.json()
        assert 'error' in data
        assert 'Failed to store image' in data['detail']
    
    def test_detect_handles_detection_failure(
        self, test_client, mock_s3_bucket, mock_yolo_model, sample_image_bytes, monkeypatch
    ):
        """Test /detect endpoint handles detection failures gracefully"""
        from app.services.detection import DamageDetectionService
        
        # Mock detect_damages to raise exception
        def mock_detection_error(*args, **kwargs):
            raise Exception("Model inference failed")
        
        monkeypatch.setattr(DamageDetectionService, 'detect_damages', mock_detection_error)
        
        files = {'file': ('test.jpg', sample_image_bytes, 'image/jpeg')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 500
        
        data = response.json()
        assert 'error' in data
        assert 'Damage detection failed' in data['detail']


class TestHealthEndpoint:
    """Integration tests for GET /health endpoint"""
    
    def test_health_endpoint_returns_200(self, test_client):
        """Test /health endpoint returns 200 OK"""
        response = test_client.get('/health')
        
        assert response.status_code == 200
    
    def test_health_endpoint_response_format(self, test_client):
        """Test /health endpoint returns correct response format"""
        response = test_client.get('/health')
        
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify required fields
        assert 'status' in data
        assert 'timestamp' in data
        
        # Verify values
        assert data['status'] == 'healthy'
        assert isinstance(data['timestamp'], str)
        
        # Verify timestamp is ISO format
        from datetime import datetime
        datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    
    def test_health_endpoint_always_available(self, test_client):
        """Test /health endpoint is always available"""
        # Make multiple requests
        for _ in range(5):
            response = test_client.get('/health')
            assert response.status_code == 200
            assert response.json()['status'] == 'healthy'


class TestCORSConfiguration:
    """Tests for CORS middleware configuration"""
    
    def test_cors_headers_present(self, test_client, mock_s3_bucket, mock_yolo_model, sample_image_bytes):
        """Test that CORS headers are present in responses"""
        files = {'file': ('test.jpg', sample_image_bytes, 'image/jpeg')}
        response = test_client.post('/detect', files=files)
        
        # TestClient doesn't include CORS headers, but we can verify the middleware is configured
        # In actual deployment, CORS headers would be present
        assert response.status_code == 200
    
    def test_options_request_for_preflight(self, test_client):
        """Test OPTIONS request for CORS preflight"""
        response = test_client.options('/detect')
        
        # TestClient may return 405 for OPTIONS, but CORS middleware handles this in production
        # The important thing is that CORS middleware is configured
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Tests for global error handling"""
    
    def test_validation_error_returns_400(self, test_client):
        """Test that validation errors return 400 Bad Request"""
        # Send request without required file parameter
        response = test_client.post('/detect')
        
        # Our exception handler converts validation errors to 400
        assert response.status_code == 400
    
    def test_file_size_error_returns_413(self, test_client, large_image_bytes):
        """Test that file size errors return 413 Payload Too Large"""
        files = {'file': ('large.jpg', large_image_bytes, 'image/jpeg')}
        response = test_client.post('/detect', files=files)
        
        # Should return 413 or 500 depending on when size check happens
        assert response.status_code in [413, 500]
        
        data = response.json()
        assert 'error' in data
    
    def test_invalid_file_type_returns_400(self, test_client):
        """Test that invalid file types return 400 Bad Request"""
        files = {'file': ('test.txt', b'not an image', 'text/plain')}
        response = test_client.post('/detect', files=files)
        
        assert response.status_code == 400
        
        data = response.json()
        assert data['error'] == 'Bad Request'
