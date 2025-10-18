#!/usr/bin/env python3
"""
Script to download and setup car damage detection model.

This script provides multiple options for obtaining a car damage detection model:
1. Download from Roboflow Universe (if available)
2. Use pre-trained YOLOv8 as fallback
3. Train custom model (instructions provided)
"""

import os
import sys
import urllib.request
from pathlib import Path


def download_file(url: str, destination: str):
    """Download file with progress indicator"""
    print(f"Downloading from {url}...")
    print(f"Saving to {destination}...")
    
    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\rProgress: {percent}%")
        sys.stdout.flush()
    
    urllib.request.urlretrieve(url, destination, progress_hook)
    print("\n✅ Download complete!")


def setup_pretrained_yolo():
    """Setup pre-trained YOLOv8 model"""
    print("\n" + "="*60)
    print("Setting up Pre-trained YOLOv8 Model")
    print("="*60)
    
    try:
        from ultralytics import YOLO
        
        print("\n📦 Downloading YOLOv8n model...")
        model = YOLO('yolov8n.pt')
        
        print("\n✅ YOLOv8n model ready!")
        print(f"   Model classes: {len(model.names)} classes")
        print(f"   Sample classes: {list(model.names.values())[:10]}")
        print("\n⚠️  Note: This is a general-purpose model.")
        print("   It can detect cars but NOT specific car damages.")
        print("   For production, consider training a custom model.")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def setup_custom_model_from_roboflow():
    """Setup custom car damage model from Roboflow"""
    print("\n" + "="*60)
    print("Custom Car Damage Model from Roboflow")
    print("="*60)
    
    print("\n📋 To use a custom car damage model from Roboflow:")
    print("\n1. Visit: https://universe.roboflow.com/")
    print("2. Search for 'car damage detection' datasets")
    print("3. Popular datasets:")
    print("   - Car Damage Detection")
    print("   - Vehicle Damage Assessment")
    print("   - Auto Insurance Damage Detection")
    print("\n4. Export as YOLOv8 format")
    print("5. Download the model weights (.pt file)")
    print("6. Place in backend/models/car-damage-yolov8.pt")
    print("\n7. Update .env file:")
    print("   MODEL_PATH=models/car-damage-yolov8.pt")
    
    return False


def setup_mock_model():
    """Create a mock model configuration for testing"""
    print("\n" + "="*60)
    print("Setting up Mock Model for Testing")
    print("="*60)
    
    env_file = Path("backend/.env")
    
    env_content = """# Car Damage Detection API Configuration

# Use mock model for testing (no real AI inference)
USE_MOCK_MODEL=true

# Storage configuration
USE_LOCAL_STORAGE=true
S3_BUCKET_NAME=car-damage-detection-bucket

# Model configuration (not used when USE_MOCK_MODEL=true)
MODEL_PATH=yolov8n.pt
CONFIDENCE_THRESHOLD=0.25

# File upload limits
MAX_FILE_SIZE_MB=10
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Created {env_file}")
    print("\n📝 Mock model configuration:")
    print("   - Returns fake detections for testing")
    print("   - No AI model required")
    print("   - Perfect for frontend development")
    print("\n🚀 You can now run: uvicorn app.main:app --reload")
    
    return True


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("🚗 Car Damage Detection Model Setup")
    print("="*60)
    
    print("\nChoose an option:")
    print("\n1. Use Pre-trained YOLOv8 (Quick start, general purpose)")
    print("2. Setup Custom Car Damage Model from Roboflow (Recommended for production)")
    print("3. Use Mock Model for Testing (No AI required)")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        setup_pretrained_yolo()
    elif choice == "2":
        setup_custom_model_from_roboflow()
    elif choice == "3":
        setup_mock_model()
    elif choice == "4":
        print("\n👋 Goodbye!")
        sys.exit(0)
    else:
        print("\n❌ Invalid choice!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
