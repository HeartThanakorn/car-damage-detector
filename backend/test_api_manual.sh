#!/bin/bash

# Manual API Testing Script
# Run this after starting the server with: uvicorn app.main:app --reload --port 8000

echo "🧪 Car Damage Detection API - Manual Test"
echo "=========================================="
echo ""

# Check if server is running
echo "1. Testing Health Check..."
response=$(curl -s -w "\n%{http_code}" http://localhost:8000/health 2>/dev/null)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "   ✅ Health check passed"
    echo "   Response: $body"
else
    echo "   ❌ Server not running or health check failed"
    echo "   Please start the server first:"
    echo "   uvicorn app.main:app --reload --port 8000"
    exit 1
fi

echo ""
echo "2. Creating test image..."
# Create a simple test image using Python
python3 << 'EOF'
from PIL import Image
img = Image.new('RGB', (640, 480), color='red')
img.save('/tmp/test_car.jpg')
print("   ✅ Test image created: /tmp/test_car.jpg")
EOF

echo ""
echo "3. Testing /detect endpoint..."
response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/detect \
  -F "file=@/tmp/test_car.jpg" 2>/dev/null)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "   ✅ Detection endpoint passed"
    echo ""
    echo "   Response:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
else
    echo "   ❌ Detection failed (HTTP $http_code)"
    echo "   Response: $body"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ All API Tests PASSED!"
echo ""
echo "📝 API Documentation:"
echo "   Swagger UI: http://localhost:8000/docs"
echo "   ReDoc: http://localhost:8000/redoc"
echo ""
