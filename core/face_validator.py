import cv2
import numpy as np

class FaceValidator:
    """
    Validates face quality and estimates head pose using 5 landmarks.
    Landmarks order in YuNet: Right Eye, Left Eye, Nose, Right Mouth, Left Mouth
    (Note: YuNet output might vary, we assume standard 5 points: 
     0: right_eye, 1: left_eye, 2: nose, 3: right_mouth, 4: left_mouth)
    """
    
    @staticmethod
    def calculate_pose(landmarks):
        """
        Estimate Yaw (Left/Right turn) based on the symmetry of landmarks.
        Returns:
            yaw_ratio: Value between -1.0 (Left) and 1.0 (Right). 0 is Front.
            pitch_ratio: Value between -1.0 (Up) and 1.0 (Down).
        """
        # Extract points (x, y)
        re = landmarks[0] # Right Eye
        le = landmarks[1] # Left Eye
        n  = landmarks[2] # Nose
        rm = landmarks[3] # Right Mouth
        lm = landmarks[4] # Left Mouth
        
        # --- YAW CALCULATION (Horizontal) ---
        # Compare distance from nose to left eye vs nose to right eye
        # dist_n_re = np.linalg.norm(n - re)
        # dist_n_le = np.linalg.norm(n - le)
        
        # Simplified: Use X-coordinates
        # If looking straight: (re.x - n.x) should be similar to (n.x - le.x) 
        
        dist_left_side = abs(n[0] - re[0])   # Distance nose to right eye
        dist_right_side = abs(le[0] - n[0])  # Distance nose to left eye
        
        # Avoid division by zero
        total_span = dist_left_side + dist_right_side
        if total_span == 0: return 0.0
        
        # Yaw Ratio: 
        # Output range: ~ -1.0 to 1.0
        # 0.0 = Front
        # Positive = Turning Left (Left dist becomes small, Right dist becomes large)
        # Negative = Turning Right
        yaw_val = (dist_right_side - dist_left_side) / total_span
        
        # Note: If camera is mirrored, the SIGN might flip depending on landmark order.
        # But for consistency, we just rely on the magnitude/ratio.
        
        return yaw_val

    @staticmethod
    def check_quality(frame, face_box):
        """
        Check if the face image is clear and well-lit.
        frame: The full video frame.
        face_box: [x, y, w, h] of the face.
        Returns: strict_pass (bool), issues (list of strings)
        """
        issues = []
        x, y, w, h = map(int, face_box)
        
        # 1. Size Check
        if w < 60 or h < 60:
            issues.append(f"Too Small ({w}x{h})")
            
        # Extract face ROI with padding
        if x < 0: x = 0
        if y < 0: y = 0
        face_roi = frame[y:y+h, x:x+w]
        
        if face_roi.size == 0:
            return False, ["Invalid ROI"]
            
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # 2. Blur Check (Laplacian Variance)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 100: # Threshold
            issues.append("Blurry")
            
        # 3. Brightness Check
        mean_brightness = np.mean(gray)
        if mean_brightness < 40:
            issues.append("Too Dark")
        elif mean_brightness > 220:
            issues.append("Too Bright")
            
        return len(issues) == 0, issues
