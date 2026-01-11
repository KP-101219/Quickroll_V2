import sys
import os
import cv2
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.camera import Camera
from core.detector import FaceDetector
from data.storage import StorageManager
from core.capture_manager import CaptureManager

def test_interactive_capture():
    print("=== Interactive Capture Test ===")
    print("This test will open a window.")
    print("1. Look Front")
    print("2. Turn Left")
    print("3. Turn Right")
    print("Press 'q' to quit.")
    
    # Initialize components
    cam = Camera(0)
    time.sleep(1)
    
    detector = FaceDetector()
    storage = StorageManager()
    manager = CaptureManager(detector, storage)
    
    # Start a test session
    student_id = "test_student_001"
    print(f"\nStarting capture for {student_id}...")
    manager.start_session(student_id)
    
    while True:
        ret, frame = cam.read()
        if not ret: break
        
        # Process frame through manager
        vis_frame, status = manager.process_frame(frame)
        
        # Add overlay text from status
        msg = status['message']
        progress = status['progress']
        
        # Draw status bar
        h, w = vis_frame.shape[:2]
        cv2.rectangle(vis_frame, (0, h-50), (w, h), (0, 0, 0), -1)
        cv2.putText(vis_frame, f"{msg} ({progress*100:.1f}%)", (20, h-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        cv2.imshow("Smart Capture Test", vis_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        if manager.state.name == 'COMPLETED':
            print("\n[SUCCESS] Capture Sequence Completed!")
            print(f"Files saved in data/students/{student_id}/")
            time.sleep(2)
            break
            
    cam.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_interactive_capture()
