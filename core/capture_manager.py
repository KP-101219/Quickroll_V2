import time
import cv2
from enum import Enum
from core.face_validator import FaceValidator

class CaptureState(Enum):
    WAITING = 0
    CAPTURING = 1
    COMPLETED = 2

class CaptureManager:
    """
    Orchestrates the capture process:
    1. Detects face
    2. checks angle (Front -> Left -> Right)
    3. auto-captures when quality is good
    """
    
    def __init__(self, detector, storage):
        self.detector = detector
        self.storage = storage
        self.validator = FaceValidator()
        
        try:
            from data.database import Database
            from core.recognizer import Recognizer
            self.db = Database()
            self.recognizer = Recognizer()
        except:
            print("DB/Recognizer Init Error in CaptureManager")
            self.db = None
            self.recognizer = None
        
        self.reset()
        
    def reset(self):
        self.current_student_id = None
        self.required_angles = ['front', 'left', 'right']
        self.captured_angles = {} # Stores {'front': path, ...}
        self.current_idx = 0 # Index in required_angles
        self.last_capture_time = 0
        self.state = CaptureState.WAITING
        self.status_message = "Ready"

    def start_session(self, student_id):
        self.reset()
        self.current_student_id = student_id
        self.storage.create_student_dir(student_id)
        self.state = CaptureState.CAPTURING
        self.update_status()

    def get_current_target(self):
        if self.current_idx < len(self.required_angles):
            return self.required_angles[self.current_idx]
        return None

    def update_status(self):
        target = self.get_current_target()
        if target:
            if target == 'front':
                self.status_message = "Look Straight Ahead"
            elif target == 'left':
                self.status_message = "Turn Head LEFT (Show Right Profile)"
            elif target == 'right':
                self.status_message = "Turn Head RIGHT (Show Left Profile)"
        else:
            self.status_message = "All Captures Complete!"
            self.state = CaptureState.COMPLETED

    def process_frame(self, frame):
        """
        Main loop called by UI. Returns processed frame and status dict.
        """
        if self.state != CaptureState.CAPTURING:
            return frame, {"message": self.status_message, "progress": 1.0}

        faces = self.detector.detect(frame)
        
        # Default visualization
        vis_frame = self.detector.visualize(frame, faces)
        
        if len(faces) == 0:
            return vis_frame, {"message": "No Face Detected", "progress": self.current_idx / 3.0}
            
        # Select largest face
        face = max(faces, key=lambda f: f[2] * f[3])
        
        # 1. Quality Check
        is_good, issues = self.validator.check_quality(frame, face[0:4])
        if not is_good:
            return vis_frame, {"message": f"Quality: {', '.join(issues)}", "progress": self.current_idx / 3.0}
            
        # 2. Pose Check
        landmarks = face[4:14].reshape((5, 2))
        yaw = self.validator.calculate_pose(landmarks)
        
        target = self.get_current_target()
        passed_angle = False
        
        # Thresholds (Tunable)
        if target == 'front':
            if -0.2 < yaw < 0.2: passed_angle = True
            else: self.status_message = "Look Straight"
            
        elif target == 'left':
            # Looking Left -> Positive Yaw (showing Right cheek)
            # Actually, per my logic in validator:
            # +ve = Turn Left (Left Side dist < Right Side dist)
            if yaw > 0.4: passed_angle = True 
            else: self.status_message = "Turn MORE Left"
            
        elif target == 'right':
            # Looking Right -> Negative Yaw
            if yaw < -0.4: passed_angle = True
            else: self.status_message = "Turn MORE Right"
            
        # 3. Auto-Capture
        if passed_angle:
            current_time = time.time()
            if current_time - self.last_capture_time > 1.0: # 1 sec cooldown
                # Crop face with padding
                x, y, w, h = map(int, face[0:4])
                # Add 20% padding
                pad_x = int(w * 0.2)
                pad_y = int(h * 0.2)
                h_img, w_img = frame.shape[:2]
                
                x1 = max(0, x - pad_x)
                y1 = max(0, y - pad_y)
                x2 = min(w_img, x + w + pad_x)
                y2 = min(h_img, y + h + pad_y)
                
                face_img = frame[y1:y2, x1:x2]
                
                # Save
                success, path = self.storage.save_image(self.current_student_id, face_img, target)
                if success:
                    print(f"[CAPTURE] Saved {target} for {self.current_student_id}")
                    self.captured_angles[target] = path
                    
                  # Generate embedding and save to DB
                    if self.db and self.recognizer:
                        # Use full frame + face data for aligned embedding
                        # face is [x, y, w, h, x_re, y_re, ...] from detector
                        emb = self.recognizer._generate_embedding(frame, face)
                        if emb is not None:
                            self.db.add_embedding(self.current_student_id, emb, target)
                            print(f"[DB] Saved embedding for {target}")
                    
                    self.current_idx += 1
                    self.last_capture_time = current_time
                    self.update_status()
                    
                    # Draw FLASH effect
                    cv2.rectangle(vis_frame, (0,0), (w_img, h_img), (255, 255, 255), 10)
        
        return vis_frame, {"message": self.status_message, "progress": self.current_idx / 3.0}
