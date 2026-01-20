import cv2
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.getcwd())

from core.detector import FaceDetector
from core.recognizer import Recognizer

def verify_alignment():
    print("[INFO] Initializing modules...")
    detector = FaceDetector()
    recognizer = Recognizer()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open camera")
        return

    print("[INFO] Camera opened. Show your face...")
    
    verified = False
    frames_processed = 0
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frames_processed += 1
        
        # Detect
        faces = detector.detect(frame)
        
        vis_frame = frame.copy()
        
        if len(faces) > 0:
            face = faces[0] # First face
            
            # Draw box
            box = face[0:4].astype(int)
            cv2.rectangle(vis_frame, (box[0], box[1]), (box[0]+box[2], box[1]+box[3]), (0, 255, 0), 2)
            
            # VERIFY: Generate embedding with alignment
            try:
                # This call uses the new signature (frame, face_data)
                # resulting in alignCrop being called internally
                emb = recognizer._generate_embedding(frame, face)
                
                if emb is not None and emb.shape == (128,):
                    cv2.putText(vis_frame, "Alignment: OK (128D)", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    verified = True
                else:
                    cv2.putText(vis_frame, "Alignment: FAILED", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            except Exception as e:
                print(f"[ERROR] Logic failed: {e}")
                cv2.putText(vis_frame, f"Error: {str(e)}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        else:
            cv2.putText(vis_frame, "No Face", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

        cv2.imshow("Verification - Press 'q' to quit", vis_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        if verified and frames_processed > 30:
            print("[SUCCESS] alignment logic verified working!")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    verify_alignment()
