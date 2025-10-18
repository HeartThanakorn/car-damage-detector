"""
Unit tests for StorageService.

Tests S3 storage operations including:
- Image ID generation
- Image upload to S3
- Error handling for S3 failures
"""

import pytest
import uuid
from botocore.exceptions import ClientError

from app.services.storage import StorageService
from app.config import settings


class TestStorageService:
    """Test suite for StorageService"""
    
    def test_generate_image_id_returns_uuid(self):
        """Test that generate_image_id returns a valid UUID string"""
        service = StorageService()
        
        image_id = service.generate_image_id()
        
        # Should be a string
        assert isinstance(image_id, str)
        
        # Should be a valid UUID
        uuid_obj = uuid.UUID(image_id)
        assert str(uuid_obj) == image_id
    
    def test_generate_image_id_unique(self):
        """Test that generate_image_id returns unique IDs"""
        service = StorageService()
        
        id1 = service.generate_image_id()
        id2 = service.generate_image_id()
        
        assert id1 != id2
    
    def test_upload_image_success(self, mock_s3_bucket, sample_image_bytes):
        """Test successful image upload to S3"""
        service = StorageService()
        image_id = "test-image-123"
        
        key = service.upload_image(sample_image_bytes, image_id)
        
        # Verify return value
        assert key == f"uploads/{image_id}.jpg"
        
        # Verify image was uploaded to S3
        s3_client = mock_s3_bucket
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key
        )
        
        # Verify content
        uploaded_data = response['Body'].read()
        assert uploaded_data == sample_image_bytes
        
        # Verify content type
        assert response['ContentType'] == 'image/jpeg'
    
    def test_upload_image_with_custom_content_type(self, mock_s3_bucket, sample_png_image_bytes):
        """Test image upload with custom content type"""
        service = StorageService()
        image_id = "test-png-456"
        
        key = service.upload_image(
            sample_png_image_bytes,
            image_id,
            content_type="image/png"
        )
        
        # Verify upload
        s3_client = mock_s3_bucket
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key
        )
        
        assert response['ContentType'] == 'image/png'
    
    def test_upload_image_constructs_correct_key(self, mock_s3_bucket, sample_image_bytes):
        """Test that upload_image constructs the correct S3 key"""
        service = StorageService()
        image_id = "abc-123-def"
        
        key = service.upload_image(sample_image_bytes, image_id)
        
        assert key == "uploads/abc-123-def.jpg"
    
    def test_upload_image_bucket_name_from_settings(self, mock_s3_bucket, sample_image_bytes):
        """Test that StorageService uses bucket name from settings"""
        service = StorageService()
        
        assert service.bucket_name == settings.S3_BUCKET_NAME
    
    def test_upload_image_handles_client_error(self, mock_s3_bucket, sample_image_bytes, monkeypatch):
        """Test error handling when S3 upload fails with ClientError"""
        service = StorageService()
        image_id = "test-error"
        
        # Mock put_object to raise ClientError
        def mock_put_object(*args, **kwargs):
            raise ClientError(
                {'Error': {'Code': 'NoSuchBucket', 'Message': 'Bucket does not exist'}},
                'PutObject'
            )
        
        monkeypatch.setattr(service.s3_client, 'put_object', mock_put_object)
        
        with pytest.raises(Exception, match="Failed to upload image to S3"):
            service.upload_image(sample_image_bytes, image_id)
    
    def test_upload_image_handles_generic_exception(self, mock_s3_bucket, sample_image_bytes, monkeypatch):
        """Test error handling for unexpected exceptions during upload"""
        service = StorageService()
        image_id = "test-generic-error"
        
        # Mock put_object to raise generic exception
        def mock_put_object(*args, **kwargs):
            raise RuntimeError("Unexpected error")
        
        monkeypatch.setattr(service.s3_client, 'put_object', mock_put_object)
        
        with pytest.raises(Exception, match="Failed to upload image to S3"):
            service.upload_image(sample_image_bytes, image_id)
    
    def test_storage_service_initialization(self):
        """Test StorageService initialization"""
        service = StorageService()
        
        assert service.s3_client is not None
        assert service.bucket_name == settings.S3_BUCKET_NAME
