"""
Student Management API Endpoints
Handles student registration, retrieval, and deletion.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import base64
import cv2
import numpy as np
from pydantic import BaseModel
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
detector = FaceDetector()

class StudentRegistration(BaseModel):
    student_id: str
    name: str

class StudentResponse(BaseModel):
    student_id: str
    name: str
    created_at: Optional[str] = None

@router.post("/register")
async def register_student(
    student_id: str = Form(...),
    name: str = Form(...),
    face_images: List[UploadFile] = File(...)
):
    """
    Register a new student with face embeddings.
    Expects: student_id, name, and 1-3 face images
    """
    try:
        # Add student to database
        success = db.add_student(student_id, name)
        if not success:
            raise HTTPException(status_code=400, detail="Student already exists or database error")
        
        # Process each face image and generate embeddings
        embeddings_added = 0
        poses = ["front", "left", "right"]
        
        for idx, face_file in enumerate(face_images):
            # Read image
            contents = await face_file.read()
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                continue
            
            # Detect face
            faces = detector.detect(image)
            if not faces or len(faces) == 0:
                continue
            
            # Get the largest face (first detection)
            face = faces[0]
            x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])
            face_crop = image[y:y+h, x:x+w]
            
            # Generate embedding
            embedding = recognizer._generate_embedding(face_crop)
            if embedding is not None:
                pose = poses[idx] if idx < len(poses) else f"pose_{idx}"
                db.add_embedding(student_id, embedding, pose)
                embeddings_added += 1
        
        if embeddings_added == 0:
            db.delete_student(student_id)
            raise HTTPException(status_code=400, detail="No valid faces detected in images")
        
        # Reload recognizer database
        recognizer.load_database()
        
        return {
            "message": "Student registered successfully",
            "student_id": student_id,
            "name": name,
            "embeddings_count": embeddings_added
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_students():
    """Get all registered students"""
    try:
        student_map = db.get_student_map()
        students = [
            {"student_id": sid, "name": info["name"]}
            for sid, info in student_map.items()
        ]
        return {"students": students, "count": len(students)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{student_id}")
async def delete_student(student_id: str):
    """Delete a student and all associated data"""
    try:
        success = db.delete_student(student_id)
        if not success:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Reload recognizer database
        recognizer.load_database()
        
        return {"message": "Student deleted successfully", "student_id": student_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{student_id}")
async def get_student(student_id: str):
    """Get student details by ID"""
    try:
        student_map = db.get_student_map()
        if student_id not in student_map:
            raise HTTPException(status_code=404, detail="Student not found")
        
        info = student_map[student_id]
        return {"student_id": student_id, "name": info["name"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
