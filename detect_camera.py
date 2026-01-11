"""
Camera Detection Script
Run this to find DroidCam or other camera devices.
"""
import cv2
import time

def detect_cameras():
    """Detect all available cameras and their resolutions."""
    print("=" * 50)
    print("QUICKROLL Camera Detection")
    print("=" * 50)
    print("\nScanning for cameras...\n")
    
    cameras_found = []
    
    for i in range(5):  # Check indices 0-4
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                
                # Determine camera type based on quality
                if w >= 1280:
                    quality = "HD (1280x720+)"
                    icon = "🎥"
                elif w >= 640:
                    quality = "SD (640x480)"
                    icon = "📷"
                else:
                    quality = "Low"
                    icon = "📹"
                
                camera_info = {
                    'index': i,
                    'width': w,
                    'height': h,
                    'quality': quality
                }
                cameras_found.append(camera_info)
                
                print(f"{icon} Camera {i}: {w}x{h} - {quality}")
                
                # If high quality, likely DroidCam
                if w >= 720:
                    print(f"   ✅ HIGH QUALITY - Likely DroidCam/External camera!")
                
        cap.release()
    
    if not cameras_found:
        print("❌ No cameras found!")
        return None
    
    print("\n" + "=" * 50)
    
    # Find best camera (highest resolution)
    best_camera = max(cameras_found, key=lambda x: x['width'] * x['height'])
    print(f"\n🏆 RECOMMENDED: Camera {best_camera['index']} ({best_camera['width']}x{best_camera['height']})")
    print(f"\nTo use this camera in QUICKROLL:")
    print(f"   Set QUICKROLL_CAMERA_INDEX={best_camera['index']} in environment")
    print(f"   Or modify Camera(0) to Camera({best_camera['index']}) in code")
    
    return best_camera['index']


def test_camera(index, duration=5):
    """Test a specific camera for a few seconds."""
    print(f"\nTesting camera {index} for {duration} seconds...")
    print("Press 'q' to quit early.\n")
    
    cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print(f"❌ Failed to open camera {index}")
        return
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            print("❌ Lost frame!")
            continue
        
        frame_count += 1
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        # Display info on frame
        h, w = frame.shape[:2]
        cv2.putText(frame, f"Camera {index} | {w}x{h} | FPS: {fps:.1f}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow(f"Camera {index} Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"✅ Test complete! Average FPS: {frame_count / duration:.1f}")


if __name__ == "__main__":
    best_idx = detect_cameras()
    
    if best_idx is not None:
        response = input(f"\nTest camera {best_idx}? (y/n): ").strip().lower()
        if response == 'y':
            test_camera(best_idx)
