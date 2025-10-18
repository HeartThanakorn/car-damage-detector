# 🧪 Testing Guide - Car Damage Detection API

## ✅ Option 1: Mock Mode Testing (ที่เราทำตอนนี้)

### Step 1: ทดสอบ Detection Service

```bash
cd backend
python test_mock_detection.py
```

**ผลลัพธ์ที่คาดหวัง:**

```
✅ Mock mode enabled: True
✅ Test image created
✅ Found 3 detections
```

### Step 2: รัน Backend Server

**เปิด Terminal ใหม่** และรันคำสั่ง:

```bash
cd backend
source venv/bin/activate  # ถ้ายังไม่ได้ activate
uvicorn app.main:app --reload --port 8000
```

**ผลลัพธ์ที่คาดหวัง:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

⚠️ **ปล่อย terminal นี้ไว้ - server ต้องรันอยู่ตลอด**

### Step 3: ทดสอบ API (เปิด Terminal ใหม่อีกอัน)

**Option A: ใช้ Test Script (แนะนำ)**

```bash
cd backend
./test_api_manual.sh
```

**Option B: ใช้ curl โดยตรง**

```bash
# Test health check
curl http://localhost:8000/health

# Test detect endpoint
curl -X POST http://localhost:8000/detect \
  -F "file=@/path/to/any-image.jpg"
```

**Option C: ใช้ Swagger UI (ง่ายที่สุด)**

1. เปิด browser: http://localhost:8000/docs
2. คลิก "POST /detect"
3. คลิก "Try it out"
4. Upload รูปใดก็ได้
5. คลิก "Execute"

### Step 4: ดูผลลัพธ์

**ตัวอย่าง Response:**

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
  "image_id": "a3f2c8d1-4b5e-6789-0abc-def123456789",
  "processing_time_ms": 12.34
}
```

---

## 🧪 Running Unit Tests

```bash
cd backend

# รัน tests ทั้งหมด
pytest tests/ -v

# รัน tests พร้อม coverage
pytest tests/ -v --cov=app --cov-report=html

# รัน test เฉพาะ detection service
pytest tests/test_detection.py -v

# รัน test เฉพาะ API endpoints
pytest tests/test_api.py -v
```

**ดู Coverage Report:**

```bash
open htmlcov/index.html  # macOS
```

---

## 🔍 Troubleshooting

### ปัญหา: Server ไม่ start

```bash
# ตรวจสอบว่า port 8000 ว่างไหม
lsof -i :8000

# ถ้ามีโปรแกรมใช้อยู่ ให้ใช้ port อื่น
uvicorn app.main:app --reload --port 8001
```

### ปัญหา: Module not found

```bash
# ติดตั้ง dependencies ใหม่
pip install -r requirements.txt
```

### ปัญหา: Mock mode ไม่ทำงาน

```bash
# ตรวจสอบ .env file
cat .env | grep USE_MOCK_MODEL

# ควรเห็น: USE_MOCK_MODEL=true
```

### ปัญหา: curl command ไม่ทำงาน

```bash
# ตรวจสอบว่า server รันอยู่
curl http://localhost:8000/health

# ถ้าไม่ได้ ให้ start server ก่อน
```

---

## 📊 Test Checklist

### Backend Tests

- [x] Mock detection service ทำงาน
- [ ] Server start สำเร็จ
- [ ] Health check endpoint ตอบกลับ 200
- [ ] /detect endpoint รับ upload ได้
- [ ] Response มี detections array
- [ ] Response มี image_id
- [ ] Response มี processing_time_ms
- [ ] Unit tests ผ่านทั้งหมด
- [ ] Test coverage >= 80%

### Integration Tests

- [ ] Upload รูป → ได้ response กลับมา
- [ ] Mock detections มี 3 items
- [ ] Bounding boxes มีค่าถูกต้อง
- [ ] Labels ถูกต้อง (scratch, dent, paint_damage)
- [ ] Confidence scores อยู่ระหว่าง 0-1

---

## 🚀 Next Steps

หลังจาก Mock Mode ทำงานได้แล้ว:

1. ✅ ทดสอบ Frontend integration
2. ⏭️ เปลี่ยนเป็น Real AI model (YOLOv8)
3. ⏭️ Deploy to AWS

---

## 💡 Quick Commands Reference

```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Test detection service
python test_mock_detection.py

# Test API
./test_api_manual.sh

# Run unit tests
pytest tests/ -v

# View API docs
open http://localhost:8000/docs
```

---

**ตอนนี้พร้อมทดสอบแล้ว! 🎉**

เริ่มจาก Step 2: รัน Backend Server ใน terminal แยก
