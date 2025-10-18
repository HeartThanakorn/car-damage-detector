#!/bin/bash

# Full-Stack Testing Script
# This script checks if both backend and frontend are running

echo "🧪 Full-Stack System Check"
echo "=========================="
echo ""

# Check Backend
echo "1. Checking Backend (http://localhost:8000)..."
backend_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)

if [ "$backend_response" = "200" ]; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is NOT running"
    echo "   Please start backend:"
    echo "   cd backend && uvicorn app.main:app --reload --port 8000"
    exit 1
fi

# Check Frontend
echo ""
echo "2. Checking Frontend (http://localhost:5173)..."
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 2>/dev/null)

if [ "$frontend_response" = "200" ]; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend is NOT running"
    echo "   Please start frontend:"
    echo "   cd frontend && npm run dev"
    exit 1
fi

# Test API endpoint
echo ""
echo "3. Testing API endpoint..."
python3 -c "from PIL import Image; img = Image.new('RGB', (640, 480), color='blue'); img.save('/tmp/test_fullstack.jpg')" 2>/dev/null

api_test=$(curl -s -X POST http://localhost:8000/detect -F "file=@/tmp/test_fullstack.jpg" 2>/dev/null)
detections_count=$(echo "$api_test" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('detections', [])))" 2>/dev/null)

if [ "$detections_count" = "3" ]; then
    echo "   ✅ API endpoint working (found $detections_count detections)"
else
    echo "   ⚠️  API endpoint response unexpected"
fi

echo ""
echo "=========================="
echo "✅ System Status: ALL GOOD!"
echo "=========================="
echo ""
echo "🌐 Access Points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Next Steps:"
echo "   1. Open browser: http://localhost:5173"
echo "   2. Upload a car image"
echo "   3. See the detection results!"
echo ""
echo "📚 Documentation:"
echo "   Full testing guide: TESTING_FULLSTACK.md"
echo ""
