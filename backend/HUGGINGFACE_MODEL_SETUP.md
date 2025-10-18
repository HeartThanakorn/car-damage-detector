# Hugging Face Car Damage Detection Model Setup

## Model Information

**Model**: `beingamit99/car_damage_detection`  
**Type**: Image Classification  
**Framework**: Hugging Face Transformers

## What Changed

### 1. Dependencies Added

- `transformers==4.35.2` - Hugging Face transformers library
- `torch==2.2.2` - PyTorch for model inference
- `numpy<2` - NumPy 1.x for compatibility

### 2. New Service Created

- `backend/app/services/huggingface_detection.py` - Hugging Face detection service

### 3. Configuration Updates

- Added `MODEL_TYPE` setting (yolo/huggingface)
- Added `HUGGINGFACE_MODEL` setting for model name
- Updated `.env` and `.env.example`

### 4. Detection Service Updated

- Added factory function `get_detection_service()` to switch between YOLO and Hugging Face
- Updated `main.py` to use the factory function

## Model Classes

The model can detect the following damage types:

- **Scratch** - Surface scratches on car body
- **Dent** - Dents and deformations
- **Glass Shatter** - Broken glass
- **Crack** - Cracks in body or glass
- **Tire Flat** - Flat or damaged tires

## How It Works

1. Image is uploaded via API
2. Image is preprocessed (converted to RGB if needed)
3. Hugging Face pipeline runs classification
4. Top prediction is returned with confidence score
5. Detection covers the whole image (classification, not object detection)

## Performance

- **First request**: ~3-4 seconds (model loading + inference)
- **Subsequent requests**: ~200-300ms (inference only)
- **Model size**: 343MB (auto-downloaded on first use)

## Testing

Test the API:

```bash
curl -X POST http://localhost:8000/detect \
  -F "file=@path/to/image.jpg"
```

Expected response:

```json
{
  "detections": [
    {
      "bounding_box": [0, 0, width, height],
      "label": "Scratch",
      "confidence_score": 0.559
    }
  ],
  "image_id": "uuid",
  "processing_time_ms": 248.73
}
```

## Switching Between Models

Edit `backend/.env`:

```bash
# Use Hugging Face model (current)
MODEL_TYPE=huggingface

# Use YOLO model
MODEL_TYPE=yolo
```

Restart the backend server after changing.
