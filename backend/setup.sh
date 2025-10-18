#!/bin/bash

# Car Damage Detection API - Setup Script
# This script sets up the backend environment and prepares for testing

set -e  # Exit on error

echo "🚗 Car Damage Detection API - Setup"
echo "===================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo ""
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Dependencies installed successfully!"

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p models
mkdir -p uploads
mkdir -p logs
echo "   ✅ Directories created"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found, creating from .env.example..."
    cp .env.example .env
    echo "   ✅ .env file created"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Display configuration
echo ""
echo "📝 Current Configuration:"
echo "========================"
grep -E "^USE_MOCK_MODEL|^MODEL_PATH|^USE_LOCAL_STORAGE" .env | sed 's/^/   /'

echo ""
echo "===================================="
echo "✅ Setup Complete!"
echo "===================================="
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Start the server:"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "2. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "3. View API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "💡 Tips:"
echo "   - Mock mode is enabled by default (no AI model needed)"
echo "   - To use real AI model, edit .env and set USE_MOCK_MODEL=false"
echo "   - Run tests with: pytest tests/ -v"
echo ""
