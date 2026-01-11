import os
import cv2
import json
import datetime

class StorageManager:
    """
    Handles file system operations for saving student data.
    Structure:
    data/
      students/
        {student_id}/
          front.jpg
          left.jpg
          right.jpg
          metadata.json
    """
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            # Default to data/students relative to project root
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.base_dir = os.path.join(root_dir, "data", "students")
        else:
            self.base_dir = base_dir
            
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def create_student_dir(self, student_id):
        """
        Create a directory for the student if it doesn't exist.
        """
        student_path = os.path.join(self.base_dir, student_id)
        if not os.path.exists(student_path):
            os.makedirs(student_path)
            return True
        return False # Already exists

    def save_image(self, student_id, image, angle_name):
        """
        Save a face image.
        angle_name: 'front', 'left', 'right'
        """
        student_path = os.path.join(self.base_dir, student_id)
        filename = f"{angle_name}.jpg"
        filepath = os.path.join(student_path, filename)
        
        # Ensure directory exists
        if not os.path.exists(student_path):
            os.makedirs(student_path)
            
        try:
            cv2.imwrite(filepath, image)
            return True, filepath
        except Exception as e:
            print(f"[ERROR] Failed to save image: {e}")
            return False, str(e)

    def save_metadata(self, student_id, metadata):
        """
        Save metadata (name, ID, timestamp, etc.) to JSON.
        """
        student_path = os.path.join(self.base_dir, student_id)
        filepath = os.path.join(student_path, "metadata.json")
        
        # Add basic info
        metadata['last_updated'] = datetime.datetime.now().isoformat()
        
        try:
            with open(filepath, 'w') as f:
                json.dump(metadata, f, indent=4)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save metadata: {e}")
            return False
