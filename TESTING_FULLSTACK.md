# 🎉 Full-Stack Testing Guide

## ✅ สถานะปัจจุบัน

### Backend ✅

- **Status**: Running
- **URL**: http://localhost:8000
- **Mode**: Mock Detection (ไม่ต้อง AI model)
- **API Docs**: http://localhost:8000/docs

### Frontend ✅

- **Status**: Running
- **URL**: http://localhost:5173
- **Framework**: React + TypeScript + Vite
- **Connected to**: http://localhost:8000

---

## 🧪 การทดสอบ Full-Stack

### Step 1: เปิด Frontend ใน Browser

```bash
# เปิด browser ไปที่:
http://localhost:5173
```

หรือใช้คำสั่ง:

```bash
open http://localhost:5173  # macOS
```

### Step 2: ทดสอบ Upload รูป

1. **คลิกปุ่ม "Choose File" หรือ "Upload Image"**
2. **เลือกรูปรถใดก็ได้** (หรือรูปอะไรก็ได้ในโหมด Mock)
3. **คลิก "Detect Damage" หรือ "Upload"**

### Step 3: ตรวจสอบผลลัพธ์

คุณควรเห็น:

✅ **Loading Indicator** - แสดงขณะ processing

✅ **รูปที่ upload พร้อม Bounding Boxes** - วาดกรอบสี่เหลี่ยมบนรูป

- กรอบสีแดง/เขียว/น้ำเงิน
- Label: "scratch", "dent", "paint_damage"
- Confidence score: 0.87, 0.92, 0.78

✅ **JSON Response** - แสดงข้อมูล raw API response

```json
{
  "detections": [
    {
      "bounding_box": [96, 48, 288, 168],
      "label": "scratch",
      "confidence_score": 0.87
    },
    ...
  ],
  "image_id": "...",
  "processing_time_ms": 18.0
}
```

---

## 🎨 UI Components ที่ควรเห็น

### 1. Image Upload Section

- File input button
- Image preview (หลังเลือกรูป)
- Upload/Detect button

### 2. Loading Section

- Spinner/Loading indicator
- "Analyzing image..." message

### 3. Results Section

- Canvas แสดงรูปพร้อม bounding boxes
- แต่ละ detection มี:
  - กรอบสี่เหลี่ยม
  - Label text
  - Confidence score

### 4. JSON Viewer Section

- Formatted JSON response
- Syntax highlighting (ถ้ามี)
- Collapsible sections

---

## 🧪 Test Cases

### Test Case 1: Upload รูปปกติ

- **Action**: Upload รูปรถ
- **Expected**: เห็น 3 detections (scratch, dent, paint_damage)
- **Status**: ✅ Should Pass

### Test Case 2: Upload รูปขนาดใหญ่

- **Action**: Upload รูป > 10MB
- **Expected**: Error message "File size exceeds 10MB limit"
- **Status**: ⚠️ ต้องทดสอบ

### Test Case 3: Upload ไฟล์ที่ไม่ใช่รูป

- **Action**: Upload .txt, .pdf file
- **Expected**: Error message "Invalid file type"
- **Status**: ⚠️ ต้องทดสอบ

### Test Case 4: Upload หลายรูปติดกัน

- **Action**: Upload → ดูผล → Upload อีกรูป
- **Expected**: Results update ทุกครั้ง
- **Status**: ⚠️ ต้องทดสอบ

---

## 🐛 Troubleshooting

### ปัญหา: Frontend ไม่เชื่อมต่อ Backend

**อาการ:**

- Error: "Network Error" หรือ "Failed to fetch"
- CORS error ใน console

**แก้ไข:**

```bash
# 1. ตรวจสอบว่า Backend รันอยู่
curl http://localhost:8000/health

# 2. ตรวจสอบ .env file
cat frontend/.env
# ควรเห็น: VITE_API_BASE_URL=http://localhost:8000

# 3. Restart Frontend
# กด Ctrl+C ใน terminal ที่รัน npm run dev
# แล้วรันใหม่: npm run dev
```

### ปัญหา: Bounding Boxes ไม่แสดง

**อาการ:**

- เห็นรูป แต่ไม่มีกรอบ
- JSON response มี detections แต่ไม่วาดบน canvas

**แก้ไข:**

- ตรวจสอบ browser console (F12)
- ดู error messages
- ตรวจสอบว่า canvas element render ถูกต้อง

### ปัญหา: Upload ช้า

**อาการ:**

- Loading นานเกิน 5 วินาที

**สาเหตุ:**

- รูปขนาดใหญ่เกินไป
- Network ช้า

**แก้ไข:**

- ใช้รูปขนาดเล็กกว่า (< 2MB)
- Compress รูปก่อน upload

---

## 📊 Performance Metrics

### Expected Response Times (Mock Mode)

- **Health Check**: < 50ms
- **Image Upload**: < 100ms
- **Detection Processing**: < 50ms (Mock mode)
- **Total Time**: < 200ms

### Expected Response Times (Real AI Model)

- **Detection Processing**: 1-5 seconds (depends on model size)
- **Total Time**: 1-5 seconds

---

## 🎯 Success Criteria

เมื่อทดสอบสำเร็จ คุณควรเห็น:

- [x] Frontend แสดงหน้าเว็บได้
- [x] Upload รูปได้
- [x] Loading indicator แสดง
- [x] Bounding boxes วาดบนรูป
- [x] Labels และ confidence scores แสดงถูกต้อง
- [x] JSON response แสดงครบถ้วน
- [x] ไม่มี error ใน console
- [x] Response time < 1 second (Mock mode)

---

## 🚀 Next Steps

หลังจากทดสอบ Full-Stack สำเร็จ:

### 1. ✅ เปลี่ยนเป็น Real AI Model

```bash
# แก้ไข backend/.env
USE_MOCK_MODEL=false
MODEL_PATH=yolov8n.pt

# Restart backend
# Model จะ download อัตโนมัติ
```

### 2. ✅ Run Unit Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

### 3. ✅ Improve UI/UX

- เพิ่ม animations
- ปรับปรุง error messages
- เพิ่ม loading states

### 4. ✅ Deploy to AWS

- Setup AWS CDK
- Deploy infrastructure
- Deploy application

---

## 📸 Screenshots (ควรเห็น)

### 1. Initial State

- Clean UI with upload button
- Instructions text

### 2. After Upload

- Image preview
- Detect button enabled

### 3. Loading State

- Spinner animation
- "Analyzing..." text

### 4. Results State

- Image with bounding boxes
- Detection labels
- JSON response

---

## 💡 Tips

1. **ใช้รูปรถจริง** - จะเห็นผลชัดเจนกว่า
2. **ทดสอบหลายรูป** - ดูว่า bounding boxes ปรับตามขนาดรูป
3. **เปิด DevTools** - ดู Network tab เพื่อดู API calls
4. **ทดสอบ Error Cases** - Upload ไฟล์ผิดประเภท, ขนาดใหญ่เกิน

---

**Happy Testing! 🎉**

ถ้ามีปัญหาหรือคำถาม ให้ตรวจสอบ:

1. Backend logs (terminal ที่รัน uvicorn)
2. Frontend console (F12 ใน browser)
3. Network tab (ดู API requests/responses)
