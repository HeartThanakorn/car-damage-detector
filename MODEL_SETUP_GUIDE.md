# 🎯 Car Damage Detection - Model Setup Guide

คู่มือการติดตั้งและเลือก AI Model สำหรับ Car Damage Detection API

---

## 📊 Model Options Comparison

| Option                 | Difficulty    | Setup Time | Accuracy | Use Case              |
| ---------------------- | ------------- | ---------- | -------- | --------------------- |
| **Mock Model**         | ⭐ Easy       | 1 min      | N/A      | Testing, Frontend Dev |
| **Pre-trained YOLOv8** | ⭐⭐ Easy     | 5 min      | Medium   | MVP, Demo             |
| **Custom Car Damage**  | ⭐⭐⭐ Medium | 30+ min    | High     | Production            |

---

## 🚀 Option 1: Mock Model (แนะนำสำหรับเริ่มต้น)

**ข้อดี:**

- ✅ ไม่ต้อง download AI model
- ✅ รันได้ทันที
- ✅ เหมาะสำหรับ test API และ Frontend
- ✅ ไม่กิน RAM/CPU มาก

**ข้อเสีย:**

- ❌ ไม่ได้ detect จริง (return ข้อมูลปลอม)

### Setup Steps:

```bash
cd backend

# 1. ติดตั้ง dependencies
pip install -r requirements.txt

# 2. ตรวจสอบ .env (Mock mode enabled by default)
cat .env | grep USE_MOCK_MODEL
# ควรเห็น: USE_MOCK_MODEL=true

# 3. รัน server
uvicorn app.main:app --reload --port 8000

# 4. ทดสอบ
curl -X POST http://localhost:8000/detect \
  -F "file=@/path/to/any-image.jpg"
```

**ผลลัพธ์ที่ได้:**

```json
{
  "detections": [
    {
      "bounding_box": [96, 48, 288, 168],
      "label": "scratch",
      "confidence_score": 0.87
    },
    {
      "bounding_box": [352, 192, 480, 312],
      "label": "dent",
      "confidence_score": 0.92
    },
    {
      "bounding_box": [128, 288, 256, 408],
      "label": "paint_damage",
      "confidence_score": 0.78
    }
  ],
  "image_id": "...",
  "processing_time_ms": 12.34
}
```

---

## 🤖 Option 2: Pre-trained YOLOv8 (แนะนำสำหรับ MVP)

**ข้อดี:**

- ✅ Download อัตโนมัติ
- ✅ ใช้งานได้จริง
- ✅ รวดเร็ว (YOLOv8n ~6MB)

**ข้อเสีย:**

- ⚠️ ไม่ได้ train เฉพาะ car damage
- ⚠️ Detect objects ทั่วไป (car, person, etc.)
- ⚠️ อาจไม่เจอ scratch/dent

### Setup Steps:

```bash
cd backend

# 1. ติดตั้ง dependencies (รวม ultralytics)
pip install -r requirements.txt

# 2. แก้ไข .env
nano .env
# เปลี่ยน: USE_MOCK_MODEL=false

# 3. รัน server (model จะ download อัตโนมัติครั้งแรก)
uvicorn app.main:app --reload --port 8000
```

**Model จะ download ไปที่:**

- `~/.cache/ultralytics/yolov8n.pt` (~6MB)

**Model Sizes:**

```bash
# Nano (fastest, smallest)
MODEL_PATH=yolov8n.pt  # 6MB

# Small (balanced)
MODEL_PATH=yolov8s.pt  # 22MB

# Medium (more accurate)
MODEL_PATH=yolov8m.pt  # 52MB
```

**Classes ที่ detect ได้:**

- 80 COCO classes: person, car, truck, bus, bicycle, etc.
- **ไม่มี**: scratch, dent, damage classes

---

## 🎯 Option 3: Custom Car Damage Model (แนะนำสำหรับ Production)

**ข้อดี:**

- ✅ Train เฉพาะ car damage
- ✅ Detect: scratch, dent, crack, rust, etc.
- ✅ Accuracy สูง

**ข้อเสีย:**

- ⚠️ ต้องหา/train model เอง
- ⚠️ ใช้เวลานานกว่า

### 3.1 หา Pre-trained Model จาก Roboflow

**ขั้นตอน:**

1. **ไปที่ Roboflow Universe:**

   ```
   https://universe.roboflow.com/
   ```

2. **ค้นหา "car damage detection"**

3. **เลือก Dataset ที่มี:**

   - ✅ YOLOv8 export support
   - ✅ Good accuracy metrics
   - ✅ Sufficient training images

4. **Popular Datasets:**

   - "Car Damage Detection" by various authors
   - "Vehicle Damage Assessment"
   - "Auto Insurance Damage Detection"

5. **Export Model:**

   - เลือก Format: YOLOv8
   - Download model weights (.pt file)

6. **ติดตั้ง:**

   ```bash
   cd backend

   # วาง model file ในโฟลเดอร์ models
   mv ~/Downloads/best.pt models/car-damage-yolov8.pt

   # แก้ไข .env
   USE_MOCK_MODEL=false
   MODEL_PATH=models/car-damage-yolov8.pt

   # รัน server
   uvicorn app.main:app --reload --port 8000
   ```

### 3.2 หา Model จาก Hugging Face

**ขั้นตอน:**

1. **ไปที่ Hugging Face:**

   ```
   https://huggingface.co/models
   ```

2. **ค้นหา:**

   - "car damage detection yolo"
   - "vehicle damage yolov8"

3. **Download:**
   ```bash
   # ตัวอย่าง (URL จะแตกต่างกันไปตาม model)
   wget https://huggingface.co/[username]/[model]/resolve/main/best.pt \
     -O backend/models/car-damage-yolov8.pt
   ```

### 3.3 Train Model เอง (Advanced)

**ถ้าต้องการ accuracy สูงสุด:**

1. **เตรียม Dataset:**

   - รวบรวมรูปรถที่มี damage
   - Annotate bounding boxes (ใช้ Roboflow, LabelImg)
   - Classes: scratch, dent, crack, rust, etc.

2. **Train ด้วย Ultralytics:**

   ```python
   from ultralytics import YOLO

   # Load pre-trained model
   model = YOLO('yolov8n.pt')

   # Train on custom dataset
   model.train(
       data='car-damage.yaml',
       epochs=100,
       imgsz=640
   )
   ```

3. **Export Model:**
   ```bash
   # Model จะอยู่ที่ runs/detect/train/weights/best.pt
   cp runs/detect/train/weights/best.pt backend/models/car-damage-yolov8.pt
   ```

---

## 🧪 Testing Your Model

### Test Model Loading

```bash
cd backend

python -c "
from app.services.detection import DamageDetectionService
service = DamageDetectionService()
model = service.load_model()
print('✅ Model loaded successfully!')
print(f'Model classes: {model.names}')
"
```

### Test Detection

```bash
# Upload test image
curl -X POST http://localhost:8000/detect \
  -F "file=@test-images/car-with-damage.jpg" \
  | jq .
```

### Run Unit Tests

```bash
pytest tests/ -v --cov=app
```

---

## 📝 Configuration Summary

### Mock Mode (Testing)

```bash
# .env
USE_MOCK_MODEL=true
MODEL_PATH=yolov8n.pt  # ไม่ได้ใช้
```

### Pre-trained YOLOv8

```bash
# .env
USE_MOCK_MODEL=false
MODEL_PATH=yolov8n.pt  # auto-download
```

### Custom Model

```bash
# .env
USE_MOCK_MODEL=false
MODEL_PATH=models/car-damage-yolov8.pt
```

---

## 🎬 Recommended Workflow

### Phase 1: Development (Week 1)

```bash
USE_MOCK_MODEL=true
```

- ✅ Develop Frontend
- ✅ Test API integration
- ✅ Build UI components

### Phase 2: MVP Testing (Week 2)

```bash
USE_MOCK_MODEL=false
MODEL_PATH=yolov8n.pt
```

- ✅ Test with real AI
- ✅ Demo to stakeholders
- ✅ Gather feedback

### Phase 3: Production (Week 3+)

```bash
USE_MOCK_MODEL=false
MODEL_PATH=models/car-damage-yolov8.pt
```

- ✅ Use custom trained model
- ✅ High accuracy detection
- ✅ Deploy to AWS

---

## 🆘 Troubleshooting

### Model ไม่ download

```bash
# Download manually
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Out of Memory

```bash
# ใช้ model เล็กกว่า
MODEL_PATH=yolov8n.pt  # แทน yolov8m.pt
```

### Detection ไม่แม่นยำ

```bash
# ลด confidence threshold
CONFIDENCE_THRESHOLD=0.15  # แทน 0.25
```

### Model ไม่เจอ car damage

```bash
# ต้องใช้ custom model ที่ train เฉพาะ car damage
# Pre-trained YOLOv8 ไม่มี scratch/dent classes
```

---

## 📚 Resources

- **Ultralytics Docs**: https://docs.ultralytics.com/
- **Roboflow Universe**: https://universe.roboflow.com/
- **Hugging Face Models**: https://huggingface.co/models
- **YOLO Training Guide**: https://docs.ultralytics.com/modes/train/

---

## ✅ Quick Start Checklist

- [ ] ติดตั้ง dependencies: `pip install -r requirements.txt`
- [ ] เลือก model option (Mock/Pre-trained/Custom)
- [ ] แก้ไข `.env` file
- [ ] รัน server: `uvicorn app.main:app --reload`
- [ ] ทดสอบ: `curl http://localhost:8000/health`
- [ ] Test detection: Upload รูปผ่าน `/docs`
- [ ] รัน tests: `pytest tests/ -v`

---

**ตอนนี้พร้อมแล้ว! 🚀**

เริ่มต้นด้วย Mock Mode แล้วค่อยๆ upgrade ไปเป็น Custom Model ตามความพร้อม
