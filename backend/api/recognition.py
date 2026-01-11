"""
Face Recognition API Endpoints
Handles face recognition and matching operations.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import cv2
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.recognizer import Recognizer
from core.detector import FaceDetector

router = APIRouter()

# Initialize components
recognizer = Recognizer()
recognizer.load_database()
detector = FaceDetector()

class RecognitionResponse(BaseModel):
    student_id: Optional[str]
    name: Optional[str]
    status: str  # RECOGNIZED, MAYBE, UNKNOWN
    confidence: float

class TopMatch(BaseModel):
    student_id: str
    name: str
    confidence: float

@router.post("/recognize")
async def recognize_face(image: UploadFile = File(...)):
    """
    Recognize a face from an uploaded image.
    Returns student_id, name, status, and confidence.
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
                "student_id": None,
                "name": None,
                "status": "NO_FACE",
                "confidence": 0.0
            }
        
        # Get the largest face
        face = faces[0]
        x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])
        face_crop = img[y:y+h, x:x+w]
        
        # Recognize
        student_id, status, confidence, info = recognizer.match_face_with_confidence(face_crop)
        
        return {
            "student_id": student_id,
            "name": info.get("name") if info else None,
            "status": status,
            "confidence": float(confidence)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/top-matches")
async def get_top_matches(image: UploadFile = File(...), top_n: int = 3):
    """
    Get top N candidate matches for a face.
    Useful for verification workflows.
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
            return {"matches": []}
        
        # Get the largest face
        face = faces[0]
        x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])
        face_crop = img[y:y+h, x:x+w]
        
        # Get top matches
        matches = recognizer.get_top_matches(face_crop, top_n)
        
        result = []
        for student_id, confidence, info in matches:
            result.append({
                "student_id": student_id,
                "name": info.get("name", "Unknown"),
                "confidence": float(confidence)
            })
        
        return {"matches": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload-database")
async def reload_database():
    """Reload the face recognition database (after adding/removing students)"""
    try:
        recognizer.load_database()
        return {"message": "Database reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
