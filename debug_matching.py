import cv2
import numpy as np
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.getcwd())

from core.detector import FaceDetector
from core.recognizer import Recognizer
from data.database import Database

def debug_recognition():
    print("=============================================")
    print("   QUICKROLL FACE DEBUGGER")
    print("=============================================")
    print("1. Shows the 'Raw' Camera Feed")
    print("2. Shows the 'Aligned' Face (What the AI sees)")
    print("3. Shows the Match Score in real-time")
    print("=============================================")
    
    detector = FaceDetector()
    recognizer = Recognizer()
    recognizer.load_database()
    
    if not recognizer.embeddings:
        print("[WARNING] DATABASE IS EMPTY! Please register a student first.")
        print("Scores will be 0.0")
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # 1. Detect
        faces = detector.detect(frame)
        
        debug_frame = frame.copy()
        aligned_display = np.zeros((112, 112, 3), dtype=np.uint8)
        
        if len(faces) > 0:
            face = faces[0]
            
            # Draw Box & Landmarks
            box = face[0:4].astype(int)
            cv2.rectangle(debug_frame, (box[0], box[1]), (box[0]+box[2], box[1]+box[3]), (0, 255, 0), 2)
            
            landmarks = face[4:14].reshape((5, 2)).astype(int)
            for p in landmarks:
                cv2.circle(debug_frame, tuple(p), 2, (0, 0, 255), -1)
            
            # 2. Align (The new logic)
            try:
                # Direct call to OpenCV's alignCrop to visualize it
                aligned_face = recognizer.recognizer.alignCrop(frame, face)
                aligned_display = aligned_face
                
                # 3. Match Score
                student_id, status, confidence, info = recognizer.match_face_with_confidence(frame, face)
                
                # Display Score
                color = (0, 255, 0) if status == "RECOGNIZED" else (0, 0, 255)
                text = f"{info.get('name', 'Unknown')} ({confidence:.2f})"
                cv2.putText(debug_frame, text, (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                # Console log for history
                # print(f"Match: {text} | Status: {status}")
                
            except Exception as e:
                print(f"Alignment Error: {e}")
        
        # UI - Show side by side
        # Resize aligned to be bigger for visibility
        aligned_big = cv2.resize(aligned_display, (224, 224))
        
        cv2.imshow("Main Feed", debug_frame)
        cv2.imshow("What AI Sees (Aligned)", aligned_big)
        
        if cv2.waitKey(1) & ord('q') == 0xFF:
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    debug_recognition()
