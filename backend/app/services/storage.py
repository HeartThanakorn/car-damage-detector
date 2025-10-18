import uuid
import logging
from typing import BinaryIO
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from app.config import settings


logger = logging.getLogger(__name__)


class StorageService:
    """Service for handling S3 storage operations"""
    
    def __init__(self):
        """Initialize the S3 client with configuration from environment"""
        self.s3_client = boto3.client('s3')
        self.bucket_name = settings.S3_BUCKET_NAME
        logger.info(f"StorageService initialized with bucket: {self.bucket_name}")
    
    def generate_image_id(self) -> str:
        """
        Generate a unique identifier for an image using UUID.
        
        Returns:
            str: A unique UUID string
        """
        return str(uuid.uuid4())
    
    def upload_image(self, image_bytes: bytes, image_id: str, content_type: str = "image/jpeg") -> str:
        """
        Upload image bytes to S3 with proper content type.
        
        Args:
            image_bytes: The image data as bytes
            image_id: Unique identifier for the image
            content_type: MIME type of the image (default: image/jpeg)
        
        Returns:
            str: The S3 object key where the image was stored
        
        Raises:
            Exception: If the S3 upload fails after error handling
        """
        # Construct the S3 key with uploads prefix
        key = f"uploads/{image_id}.jpg"
        
        try:
            logger.info(f"Uploading image to S3: bucket={self.bucket_name}, key={key}")
            
            # Upload the image to S3
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
