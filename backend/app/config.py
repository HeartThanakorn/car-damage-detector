import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Centralized configuration management for the application"""
    
    # S3 Configuration
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "car-damage-detection-bucket")
    
    # Model Configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/yolov8n.pt")
    MODEL_TYPE: str = os.getenv("MODEL_TYPE", "huggingface")  # "yolo" or "huggingface"
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "beingamit99/car_damage_detection")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://my-damage-detector-app.com"
    ]


settings = Settings()
