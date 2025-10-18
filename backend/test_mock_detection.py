#!/usr/bin/env python3
"""
Quick test script for mock detection mode
"""

import os
import sys

# Set mock mode
os.environ['USE_MOCK_MODEL'] = 'true'

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.detection import DamageDetectionService
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (640, 480), color='blue')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

def main():
    print("🧪 Testing Mock Detection Mode")
    print("=" * 50)
    
    # Initialize service
    print("\n1. Initializing Detection Service...")
    service = DamageDetectionService()
    print(f"   ✅ Mock mode enabled: {service.use_mock}")
    
    # Create test image
    print("\n2. Creating test image...")
    image_bytes = create_test_image()
    print(f"   ✅ Test image created ({len(image_bytes)} bytes)")
    
    # Run detection
    print("\n3. Running detection...")
    detections = service.detect_damages(image_bytes)
    print(f"   ✅ Found {len(detections)} detections")
    
    # Display results
    print("\n4. Detection Results:")
    print("-" * 50)
    for i, detection in enumerate(detections, 1):
        print(f"\n   Detection {i}:")
        print(f"   - Label: {detection.label}")
        print(f"   - Confidence: {detection.confidence_score:.2f}")
        print(f"   - Bounding Box: {detection.bounding_box}")
    
    print("\n" + "=" * 50)
    print("✅ Mock Detection Test PASSED!")
    print("\n💡 Next step: Start the server with:")
    print("   uvicorn app.main:app --reload --port 8000")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
