"""
Camera API Endpoints
Handles camera detection and streaming.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()

class CameraInfo(BaseModel):
    index: int
    name: str
    available: bool

@router.get("/list")
async def list_cameras():
    """
    List available cameras.
    Tests camera indices 0-4 to find working cameras.
    """
    try:
        import cv2
        cameras = []
        
        for idx in range(5):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                cameras.append({
                    "index": idx,
                    "name": f"Camera {idx}",
                    "available": True
                })
                cap.release()
        
        return {"cameras": cameras, "count": len(cameras)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/{camera_index}")
async def test_camera(camera_index: int):
    """Test if a specific camera is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return {
                    "camera_index": camera_index,
                    "available": True,
                    "message": "Camera is working"
                }
        
        return {
            "camera_index": camera_index,
            "available": False,
            "message": "Camera not accessible"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
