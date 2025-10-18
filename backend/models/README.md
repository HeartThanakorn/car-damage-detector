# Car Damage Detection Models

This directory contains the YOLO models for car damage detection.

## Available Models

### Option 1: Pre-trained YOLOv8 (General Purpose)

- **Model**: `yolov8n.pt`, `yolov8s.pt`, `yolov8m.pt`
- **Source**: Ultralytics official
- **Classes**: 80 COCO classes (car, person, etc.)
- **Use Case**: General object detection, good for MVP testing
- **Download**: Automatic on first run

### Option 2: Custom Car Damage Model (Recommended)

- **Model**: `car-damage-yolov8.pt`
- **Classes**: scratch, dent, crack, broken_part, etc.
- **Use Case**: Production car damage detection
- **Download**: See instructions below

## Installation Instructions

### Quick Start (Pre-trained YOLOv8)

The easiest way to get started:

```bash
# Install dependencies
pip install ultralytics

# Model will download automatically on first run
# No manual download needed!
```

### Custom Car Damage Model Setup

For production-ready car damage detection, we'll use a custom trained model:

```bash
# Download custom car damage model
# Option A: From Roboflow (if available)
curl -L "https://universe.roboflow.com/[workspace]/[project]/[version]/download/yolov8" -o car-damage-yolov8.pt

# Option B: From Hugging Face (if available)
wget https://huggingface.co/[model-path]/resolve/main/car-damage-yolov8.pt

# Option C: Use our provided model (see below)
```

## Model Configuration

Update your `.env` file:

```bash
# For pre-trained YOLOv8 (auto-download)
MODEL_PATH=yolov8n.pt

# For custom car damage model
MODEL_PATH=models/car-damage-yolov8.pt
```

## Model Classes

### Pre-trained YOLOv8 Classes

- 80 COCO classes including: person, car, truck, bus, etc.

### Custom Car Damage Classes (Expected)

- scratch
- dent
- crack
- broken_part
- rust
- paint_damage
- glass_damage

## Testing the Model

```bash
# Test model loading
python -c "
from app.services.detection import DamageDetectionService
service = DamageDetectionService()
model = service.load_model()
print('✅ Model loaded successfully!')
print(f'Model classes: {model.names}')
"
```

## Notes

- Models are cached in `~/.cache/ultralytics/` after first download
- Large models (>100MB) should not be committed to git
- Use `.gitignore` to exclude `*.pt` files
