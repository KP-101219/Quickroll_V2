# Quickroll V2 API Documentation

Base URL: `http://localhost:8000`

## Table of Contents

- [Authentication](#authentication)
- [Students API](#students-api)
- [Recognition API](#recognition-api)
- [Attendance API](#attendance-api)
- [Camera API](#camera-api)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)

## Authentication

Currently, the API does not require authentication. For production deployment, implement JWT or API key authentication.

## Students API

### Register Student

Register a new student with face embeddings.

**Endpoint:** `POST /api/students/register`

**Content-Type:** `multip art/form-data`

**Parameters:**
- `student_id` (form): Unique student identifier
- `name` (form): Student's full name
- `face_images` (files): 1-3 face images (JPEG/PNG)

**Example Request (curl):**
```bash
curl -X POST http://localhost:8000/api/students/register \
  -F "student_id=STU001" \
  -F "name=John Doe" \
  -F "face_images=@face1.jpg" \
  -F "face_images=@face2.jpg" \
  -F "face_images=@face3.jpg"
```

**Response:**
```json
{
  "message": "Student registered successfully",
  "student_id": "STU001",
  "name": "John Doe",
  "embeddings_count": 3
}
```

---

### List Students

Get all registered students.

**Endpoint:** `GET /api/students/list`

**Example Request:**
```bash
curl http://localhost:8000/api/students/list
```

**Response:**
```json
{
  "students": [
    {"student_id": "STU001", "name": "John Doe"},
    {"student_id": "STU002", "name": "Jane Smith"}
  ],
  "count": 2
}
```

---

### Get Student

Get details of a specific student.

**Endpoint:** `GET /api/students/{student_id}`

**Example Request:**
```bash
curl http://localhost:8000/api/students/STU001
```

**Response:**
```json
{
  "student_id": "STU001",
  "name": "John Doe"
}
```

---

### Delete Student

Delete a student and all associated data.

**Endpoint:** `DELETE /api/students/{student_id}`

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/students/STU001
```

**Response:**
```json
{
  "message": "Student deleted successfully",
  "student_id": "STU001"
}
```

---

## Recognition API

### Recognize Face

Recognize a face from an uploaded image.

**Endpoint:** `POST /api/recognition/recognize`

**Content-Type:** `multipart/form-data`

**Parameters:**
- `image` (file): Face image (JPEG/PNG)

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/recognition/recognize \
  -F "image=@face.jpg"
```

**Response:**
```json
{
  "student_id": "STU001",
  "name": "John Doe",
  "status": "RECOGNIZED",
  "confidence": 0.89
}
```

**Status Values:**
- `RECOGNIZED`: High confidence (≥0.75) - Auto-mark attendance
- `MAYBE`: Medium confidence (0.50-0.75) - Requires verification
- `UNKNOWN`: Low confidence (<0.50) - Not in database
- `NO_FACE`: No face detected in image

---

### Get Top Matches

Get top N candidate matches for a face.

**Endpoint:** `POST /api/recognition/top-matches`

**Parameters:**
- `image` (file): Face image
- `top_n` (query, optional): Number of matches to return (default: 3)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/recognition/top-matches?top_n=3" \
  -F "image=@face.jpg"
```

**Response:**
```json
{
  "matches": [
    {"student_id": "STU001", "name": "John Doe", "confidence": 0.89},
    {"student_id": "STU005", "name": "Alice Brown", "confidence": 0.62},
    {"student_id": "STU003", "name": "Bob Wilson", "confidence": 0.51}
  ]
}
```

---

### Reload Database

Reload the face recognition database (call after adding/deleting students).

**Endpoint:** `POST /api/recognition/reload-database`

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/recognition/reload-database
```

**Response:**
```json
{
  "message": "Database reloaded successfully"
}
```

---

## Attendance API

### Mark Attendance

Mark attendance by recognizing face from image. Only marks if confidence ≥ 0.75.

**Endpoint:** `POST /api/attendance/mark`

**Parameters:**
- `image` (file): Face image

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/attendance/mark \
  -F "image=@face.jpg"
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Attendance marked for John Doe",
  "student_id": "STU001",
  "name": "John Doe",
  "status": "RECOGNIZED",
  "confidence": 0.89,
  "time": "14:32:15"
}
```

**Response (Low Confidence):**
```json
{
  "success": false,
  "message": "Low confidence - verification required",
  "student_id": "STU002",
  "name": "Jane Smith",
  "status": "MAYBE",
  "confidence": 0.62
}
```

---

### Get Attendance History

Get attendance records, optionally filtered by date.

**Endpoint:** `GET /api/attendance/history`

**Parameters:**
- `date` (query, optional): Filter by date (YYYY-MM-DD format)

**Example Request (All records):**
```bash
curl http://localhost:8000/api/attendance/history
```

**Example Request (Specific date):**
```bash
curl "http://localhost:8000/api/attendance/history?date=2026-01-11"
```

**Response:**
```json
{
  "records": [
    {
      "id": "STU001",
      "name": "John Doe",
      "time": "14:32:15",
      "status": "Present",
      "confidence": 0.89,
      "marked_by": "face_recognition"
    },
    {
      "id": "STU002",
      "name": "Jane Smith",
      "time": "14:35:22",
      "status": "Present",
      "confidence": 0.92,
      "marked_by": "face_recognition"
    }
  ],
  "count": 2
}
```

---

### Get Today's Attendance

Get attendance records for today.

**Endpoint:** `GET /api/attendance/today`

**Example Request:**
```bash
curl http://localhost:8000/api/attendance/today
```

**Response:**
```json
{
  "date": "2026-01-11",
  "records": [
    {
      "id": "STU001",
      "name": "John Doe",
      "time": "14:32:15",
      "status": "Present",
      "confidence": 0.89,
      "marked_by": "face_recognition"
    }
  ],
  "count": 1
}
```

---

## Camera API

### List Cameras

Get list of available cameras.

**Endpoint:** `GET /api/camera/list`

**Example Request:**
```bash
curl http://localhost:8000/api/camera/list
```

**Response:**
```json
{
  "cameras": [
    {"index": 0, "name": "Camera 0", "available": true},
    {"index": 1, "name": "Camera 1", "available": true}
  ],
  "count": 2
}
```

---

### Test Camera

Test if a specific camera is accessible.

**Endpoint:** `GET /api/camera/test/{camera_index}`

**Example Request:**
```bash
curl http://localhost:8000/api/camera/test/0
```

**Response:**
```json
{
  "camera_index": 0,
  "available": true,
  "message": "Camera is working"
}
```

---

## Response Formats

### Success Response
```json
{
  "message": "Operation successful",
  "data": {...}
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters or malformed request
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Errors

**Student Already Exists:**
```json
{
  "detail": "Student already exists or database error"
}
```

**No Face Detected:**
```json
{
  "detail": "No valid faces detected in images"
}
```

**Student Not Found:**
```json
{
  "detail": "Student not found"
}
```

**Invalid Image:**
```json
{
  "detail": "Invalid image"
}
```

---

## Interactive API Documentation

FastAPI provides auto-generated interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these for testing API endpoints directly in your browser.

---

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Implement rate limiting per IP
- Add authentication tokens
- Monitor suspicious activity

---

## Best Practices

1. **Image Quality**: Send clear, well-lit face images
2. **Image Size**: Resize images to 640x480 before upload
3. **Error Handling**: Always check response status codes
4. **Confidence Thresholds**: 
   - ≥0.75: Auto-accept
   - 0.50-0.75: Manual verification
   - <0.50: Reject
5. **Database Reload**: Call `/api/recognition/reload-database` after bulk student operations

---

## Example Client (Python)

```python
import requests

API_BASE = "http://localhost:8000"

# Register student
with open("face1.jpg", "rb") as f1:
    files = [("face_images", f1)]
    data = {"student_id": "STU001", "name": "John Doe"}
    response = requests.post(f"{API_BASE}/api/students/register", data=data, files=files)
    print(response.json())

# Recognize face
with open("face.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post(f"{API_BASE}/api/recognition/recognize", files=files)
    result = response.json()
    print(f"Recognized: {result['name']} (Confidence: {result['confidence']})")

# Mark attendance
with open("face.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post(f"{API_BASE}/api/attendance/mark", files=files)
    result = response.json()
    if result["success"]:
        print(f"✓ Attendance marked for {result['name']}")
```

---

For more information, see the [main README](../README.md) or explore the interactive docs at http://localhost:8000/docs
