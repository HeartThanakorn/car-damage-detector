# 🚀 Quick Start Guide - Car Damage Detection API

เริ่มต้นใช้งาน Backend API ภายใน 5 นาที!

## 📋 Prerequisites

- Python 3.11+
- pip หรือ pip3

## ⚡ Quick Start (Mock Mode - ไม่ต้อง AI Model)

วิธีนี้เหมาะสำหรับ:

- ทดสอบ API endpoints
- พัฒนา Frontend
- ทดสอบ Integration

```bash
# 1. เข้าไปที่โฟลเดอร์ backend
cd backend

# 2. สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# หรือ venv\Scripts\activate  # Windows

# 3. ติดตั้ง dependencies
pip install -r requirements.txt

# 4. ใช้ไฟล์ .env ที่มีอยู่แล้ว (Mock mode enabled)
# ไฟล์ .env ถูกสร้างไว้แล้วพร้อม USE_MOCK_MODEL=true

# 5. รัน server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ เสร็จแล้ว! API พร้อมใช้งานที่ http://localhost:8000

### ทดสอบ API

```bash
# Test health check
curl http://localhost:8000/health

# Test detect endpoint (ใช้รูปใดก็ได้)
curl -X POST http://localhost:8000/detect \
  -F "file=@/path/to/any-image.jpg"
```

หรือเปิด Swagger UI: http://localhost:8000/docs

## 🤖 Real AI Model Setup

เมื่อพร้อมใช้ AI model จริง:

### Option 1: Pre-trained YOLOv8 (ง่ายที่สุด)

```bash
# 1. ติดตั้ง ultralytics
pip install ultralytics

# 2. แก้ไข .env
# เปลี่ยน USE_MOCK_MODEL=true เป็น USE_MOCK_MODEL=false

# 3. รัน server (model จะ download อัตโนมัติครั้งแรก ~6MB)
uvicorn app.main:app --reload --port 8000
```

⚠️ **หมายเหตุ**: YOLOv8 pre-trained เป็น general-purpose model

- รู้จัก objects ทั่วไป (car, person, etc.)
- **ไม่ได้ train เฉพาะ car damage** (scratch, dent)
- เหมาะสำหรับ MVP/testing

### Option 2: Custom Car Damage Model (แนะนำสำหรับ Production)

```bash
# 1. หา custom car damage model จาก:
#    - Roboflow Universe: https://universe.roboflow.com/
#    - Hugging Face: https://huggingface.co/
#    - Train เอง

# 2. Download model weights (.pt file)
# ตัวอย่าง:
wget https://example.com/car-damage-model.pt -O models/car-damage-yolov8.pt

# 3. แก้ไข .env
USE_MOCK_MODEL=false
MODEL_PATH=models/car-damage-yolov8.pt

# 4. รัน server
uvicorn app.main:app --reload --port 8000
```

## 🔍 Roboflow Car Damage Datasets

ค้นหา pre-trained models ที่:

1. ไปที่ https://universe.roboflow.com/
2. ค้นหา "car damage detection"
3. เลือก dataset ที่มี YOLOv8 export
4. Download model weights
5. วางไฟล์ใน `backend/models/`

**Popular datasets:**

- Car Damage Detection
- Vehicle Damage Assessment
- Auto Insurance Damage Detection

## 🧪 Running Tests

```bash
# รัน tests ทั้งหมด
pytest tests/ -v

# รัน tests พร้อม coverage report
pytest tests/ -v --cov=app --cov-report=html

# ดู coverage report
open htmlcov/index.html  # macOS
# หรือ xdg-open htmlcov/index.html  # Linux
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── config.py            # Configuration
│   └── services/
│       ├── detection.py     # AI detection service
│       └── storage.py       # S3/local storage
├── tests/                   # Test files
├── models/                  # AI model weights
├── .env                     # Configuration (created)
├── .env.example            # Configuration template
└── requirements.txt        # Python dependencies
```

## 🐛 Troubleshooting

### ปัญหา: Module not found

```bash
# ติดตั้ง dependencies ใหม่
pip install -r requirements.txt
```

### ปัญหา: Port 8000 ถูกใช้งานแล้ว

```bash
# ใช้ port อื่น
uvicorn app.main:app --reload --port 8001
```

### ปัญหา: CORS error จาก Frontend

```bash
# ตรวจสอบว่า Frontend URL อยู่ใน CORS_ORIGINS
# แก้ไขใน app/config.py หรือ .env
```

### ปัญหา: Model download ช้า

```bash
# Download model ล่วงหน้า
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

## 🎯 Next Steps

1. ✅ รัน Backend ใน Mock mode
2. ✅ ทดสอบ API endpoints
3. ✅ รัน Frontend และเชื่อมต่อ Backend
4. ⏭️ เปลี่ยนเป็น Real AI model
5. ⏭️ หา/train Custom car damage model
6. ⏭️ Deploy to AWS

## 📚 API Documentation

เมื่อ server รันอยู่:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 💡 Tips

- ใช้ Mock mode ขณะพัฒนา Frontend (เร็วกว่า)
- ใช้ Pre-trained YOLOv8 สำหรับ MVP
- ใช้ Custom model สำหรับ Production
- เก็บ model weights ใน `.gitignore` (ไฟล์ใหญ่)

---

มีคำถามหรือปัญหา? เปิด issue หรือดูที่ README.md
