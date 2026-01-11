import sys
import os
import cv2
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.camera import Camera
from core.detector import FaceDetector

def test_foundation():
    print("=== Testing Quickroll V2 Foundation ===")
    
    # 1. Test Camera
    print("\n[1] Initializing Camera...")
    try:
        cam = Camera(0)
        time.sleep(2) # Warmup
        ret, frame = cam.read()
        if ret and frame is not None:
            print(f"[PASS] Camera working. Frame size: {frame.shape}")
        else:
            print("[FAIL] Camera failed to read frame.")
            return
    except Exception as e:
        print(f"[FAIL] Camera exception: {e}")
        return

    # 2. Test Detector
    print("\n[2] Initializing YuNet Detector...")
    try:
        detector = FaceDetector()
        if detector.detector is None:
            print("[FAIL] Detector failed to load model.")
            return
        print("[PASS] Detector initialized.")
    except Exception as e:
        print(f"[FAIL] Detector exception: {e}")
        return

    # 3. Integration Test
    print("\n[3] Running Detection Loop (50 frames)...")
    start_time = time.time()
    frames_processed = 0
    
    try:
        for i in range(50):
            ret, frame = cam.read()
            if not ret: continue
            
            faces = detector.detect(frame)
            frames_processed += 1
            
            # Optional: Visualize (don't show window in automated test)
            # vis = detector.visualize(frame, faces)
            
            if i % 10 == 0:
                print(f"Frame {i}: Found {len(faces)} faces")
                
    except Exception as e:
        print(f"[FAIL] Detection loop error: {e}")
    
    end_time = time.time()
    fps = frames_processed / (end_time - start_time)
    print(f"\n[PASS] Processed {frames_processed} frames at {fps:.2f} FPS")
    
    # Cleanup
    cam.stop()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_foundation()
