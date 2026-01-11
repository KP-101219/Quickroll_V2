"""
API Client for Desktop Application
Handles all HTTP communication with the backend API server.
"""

import requests
import io
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Optional, Tuple

class QuickrollAPIClient:
    """Client for communicating with Quickroll backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 30  # seconds
    
    def _check_connection(self) -> bool:
        """Check if backend server is reachable"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _image_to_bytes(self, image: np.ndarray) -> bytes:
        """Convert OpenCV image to bytes for upload"""
        is_success, buffer = cv2.imencode(".jpg", image)
        if not is_success:
            raise ValueError("Failed to encode image")
        return buffer.tobytes()
    
    # ==================== Student Management ====================
    
    def register_student(self, student_id: str, name: str, face_images: List[np.ndarray]) -> Dict:
        """
        Register a new student with face embeddings.
        
        Args:
            student_id: Unique student identifier
            name: Student's name
            face_images: List of face images (numpy arrays)
        
        Returns:
            Response dict with registration status
        """
        try:
            # Prepare multipart form data
            files = []
            for idx, img in enumerate(face_images):
                img_bytes = self._image_to_bytes(img)
                files.append(('face_images', (f'face_{idx}.jpg', img_bytes, 'image/jpeg')))
            
            data = {
                'student_id': student_id,
                'name': name
            }
            
            response = requests.post(
                f"{self.base_url}/api/students/register",
                data=data,
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to backend server. Please ensure it's running."}
        except Exception as e:
            return {"error": str(e)}
    
    def get_students(self) -> Dict:
        """Get list of all registered students"""
        try:
            response = requests.get(
                f"{self.base_url}/api/students/list",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "students": [], "count": 0}
    
    def delete_student(self, student_id: str) -> Dict:
        """Delete a student"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/students/{student_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== Face Recognition ====================
    
    def recognize_face(self, image: np.ndarray) -> Dict:
        """
        Recognize a face from an image.
        
        Args:
            image: Face image (numpy array)
        
        Returns:
            Dict with student_id, name, status, confidence
        """
        try:
            img_bytes = self._image_to_bytes(image)
            files = {'image': ('face.jpg', img_bytes, 'image/jpeg')}
            
            response = requests.post(
                f"{self.base_url}/api/recognition/recognize",
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "error": str(e),
                "student_id": None,
                "status": "ERROR",
                "confidence": 0.0
            }
    
    def get_top_matches(self, image: np.ndarray, top_n: int = 3) -> Dict:
        """Get top N matching candidates for a face"""
        try:
            img_bytes = self._image_to_bytes(image)
            files = {'image': ('face.jpg', img_bytes, 'image/jpeg')}
            params = {'top_n': top_n}
            
            response = requests.post(
                f"{self.base_url}/api/recognition/top-matches",
                files=files,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "matches": []}
    
    # ==================== Attendance ====================
    
    def mark_attendance(self, image: np.ndarray) -> Dict:
        """
        Mark attendance by recognizing face.
        
        Args:
            image: Face image (numpy array)
        
        Returns:
            Dict with success status and attendance details
        """
        try:
            img_bytes = self._image_to_bytes(image)
            files = {'image': ('face.jpg', img_bytes, 'image/jpeg')}
            
            response = requests.post(
                f"{self.base_url}/api/attendance/mark",
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to mark attendance"
            }
    
    def get_attendance_history(self, date: Optional[str] = None) -> Dict:
        """
        Get attendance history.
        
        Args:
            date: Optional date filter (YYYY-MM-DD)
        
        Returns:
            Dict with attendance records
        """
        try:
            params = {'date': date} if date else {}
            response = requests.get(
                f"{self.base_url}/api/attendance/history",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "records": [], "count": 0}
    
    def get_today_attendance(self) -> Dict:
        """Get today's attendance records"""
        try:
            response = requests.get(
                f"{self.base_url}/api/attendance/today",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "records": [], "count": 0}
    
    # ==================== Camera ====================
    
    def list_cameras(self) -> Dict:
        """Get list of available cameras"""
        try:
            response = requests.get(
                f"{self.base_url}/api/camera/list",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "cameras": [], "count": 0}


# Global API client instance
api_client = QuickrollAPIClient()
