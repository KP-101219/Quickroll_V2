"""
Attendance Management API Endpoints
Handles attendance marking and history retrieval.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import cv2
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import Database
from core.recognizer import Recognizer
from core.detector import FaceDetector

router = APIRouter()

# Initialize components
db = Database()
recognizer = Recognizer()
recognizer.load_database()
detector = FaceDetector()

class AttendanceRecord(BaseModel):
    student_id: str
    name: str
    time: str
    status: str
    confidence: float
    marked_by: str

@router.post("/mark")
async def mark_attendance(image: UploadFile = File(...)):
    """
    Mark attendance by recognizing face from image.
    Only marks if confidence is HIGH (>= 0.75).
    """
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Detect face
        faces = detector.detect(img)
        if not faces or len(faces) == 0:
            return {
                "success": False,
                "message": "No face detected",
                "status": "NO_FACE"
            }
        
        # Get the largest face  
        face = faces[0]
        x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])
        face_crop = img[y:y+h, x:x+w]
        
        # Recognize
        student_id, status, confidence, info = recognizer.match_face_with_confidence(face_crop)
        
        if status == "RECOGNIZED":
            # Mark attendance
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M:%S")
            
            db.mark_attendance(
                student_id=student_id,
                date=current_date,
                time=current_time,
                confidence=confidence,
                marked_by="face_recognition"
            )
            
            return {
                "success": True,
                "message": f"Attendance marked for {info.get('name', student_id)}",
                "student_id": student_id,
                "name": info.get("name"),
                "status": status,
                "confidence": float(confidence),
                "time": current_time
            }
        elif status == "MAYBE":
            return {
                "success": False,
                "message": "Low confidence - verification required",
                "student_id": student_id,
                "name": info.get("name") if info else None,
                "status": status,
                "confidence": float(confidence)
            }
        else:
            return {
                "success": False,
                "message": "Person not recognized",
                "status": "UNKNOWN",
                "confidence": float(confidence)
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_attendance_history(date: Optional[str] = None):
    """
    Get attendance history, optionally filtered by date (YYYY-MM-DD).
    If no date provided, returns all records.
    """
    try:
        history = db.get_attendance_history(date)
        return {"records": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today")
async def get_today_attendance():
    """Get today's attendance records"""
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        history = db.get_attendance_history(current_date)
        return {"date": current_date, "records": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
