import uuid
import logging
import os
from pathlib import Path
from typing import BinaryIO
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from app.config import settings


logger = logging.getLogger(__name__)


class StorageService:
    """Service for handling S3 storage operations with local mode support"""
    
    def __init__(self):
        """Initialize the storage service with S3 or local filesystem"""
        self.use_local = os.getenv('USE_LOCAL_STORAGE', 'true').lower() == 'true'
        
        if self.use_local:
            # Use local filesystem storage
            self.local_path = Path('uploads')
            self.local_path.mkdir(exist_ok=True)
            logger.info(f"StorageService initialized in LOCAL mode: {self.local_path}")
        else:
            # Use S3 storage
            self.s3_client = boto3.client('s3')
            self.bucket_name = settings.S3_BUCKET_NAME
            logger.info(f"StorageService initialized in S3 mode: bucket={self.bucket_name}")
    
    def generate_image_id(self) -> str:
        """
        Generate a unique identifier for an image using UUID.
        
        Returns:
            str: A unique UUID string
        """
        return str(uuid.uuid4())
    
    def upload_image(self, image_bytes: bytes, image_id: str, content_type: str = "image/jpeg") -> str:
        """
        Upload image bytes to S3 or local filesystem.
        
        Args:
            image_bytes: The image data as bytes
            image_id: Unique identifier for the image
            content_type: MIME type of the image (default: image/jpeg)
        
        Returns:
            str: The storage key/path where the image was stored
        
        Raises:
            Exception: If the upload fails
        """
        if self.use_local:
            return self._upload_local(image_bytes, image_id)
        else:
            return self._upload_s3(image_bytes, image_id, content_type)
    
    def _upload_local(self, image_bytes: bytes, image_id: str) -> str:
        """Upload image to local filesystem"""
        try:
            file_path = self.local_path / f"{image_id}.jpg"
            logger.info(f"Saving image locally: {file_path}")
            
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            logger.info(f"Successfully saved image: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save image locally: {str(e)}")
            raise Exception(f"Failed to save image locally: {str(e)}") from e
    
    def _upload_s3(self, image_bytes: bytes, image_id: str, content_type: str) -> str:
        """Upload image to S3"""
        key = f"uploads/{image_id}.jpg"
        
        try:
            logger.info(f"Uploading image to S3: bucket={self.bucket_name}, key={key}")
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_bytes,
                ContentType=content_type
            )
            
            logger.info(f"Successfully uploaded image: {key}")
            return key
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', 'Unknown error')
            logger.error(f"S3 ClientError during upload: {error_code} - {error_message}")
            raise Exception(f"Failed to upload image to S3: {error_code} - {error_message}") from e
            
        except BotoCoreError as e:
            logger.error(f"BotoCoreError during S3 upload: {str(e)}")
            raise Exception(f"Failed to upload image to S3: {str(e)}") from e
            
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            raise Exception(f"Failed to upload image to S3: {str(e)}") from e
