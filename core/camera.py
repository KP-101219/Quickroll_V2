"""
Camera Module with DroidCam/External Camera Support

Supports:
- Laptop webcam (index 0)
- DroidCam phone camera (usually index 1 or 2)
- IP cameras via RTSP URL
- Auto-detection of best quality camera
"""
import cv2
import threading
import time
import os


# Configuration - Force Camera 0 (PC Camera)
DEFAULT_CAMERA_INDEX = 0  # PC built-in camera


def find_best_camera():
    """
    Auto-detect the best quality camera available.
    Returns the camera index with highest resolution.
    """
    best_idx = 0
    best_resolution = 0
    
    for i in range(4):  # Check indices 0-3
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                resolution = w * h
                print(f"[INFO] Found camera {i}: {w}x{h}")
                
                if resolution > best_resolution:
                    best_resolution = resolution
                    best_idx = i
        cap.release()
    
    if best_resolution > 0:
        print(f"[INFO] Best camera: index {best_idx}")
    
    return best_idx


class Camera:
    def __init__(self, source=None, auto_detect=False, mirror=True):
        """
        Initialize the camera with a separate thread for reading frames.
        
        Args:
            source: Camera index (int), 'auto' for auto-detection, or RTSP URL (string)
            auto_detect: If True, automatically find best quality camera
            mirror: If True, flip frame horizontally for selfie-style view
        """
        # Determine source
        if source == 'auto' or auto_detect:
            self.source = find_best_camera()
            print(f"[INFO] Auto-detected camera: {self.source}")
        elif source is None:
            self.source = DEFAULT_CAMERA_INDEX
        else:
            self.source = source
        
        self.mirror = mirror
        self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera source: {self.source}. Check if DroidCam is running!")
        
        # Set resolution to HD if possible
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Read actual resolution
        actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        self.ret, self.frame = self.cap.read()
        self.running = True
        self.lock = threading.Lock()
        
        # Start the capture thread
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        
        print(f"[INFO] Camera started: source={self.source}, resolution={actual_w}x{actual_h}, fps={actual_fps:.0f}")

    def _update(self):
        """Continuously read frames from the camera."""
        reconnect_attempts = 0
        max_reconnect = 5
        
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                
                if ret:
                    reconnect_attempts = 0
                    with self.lock:
                        self.ret = ret
                        self.frame = frame
                else:
                    # Connection lost - try to reconnect
                    reconnect_attempts += 1
                    if reconnect_attempts <= max_reconnect:
                        print(f"[WARN] Camera frame lost, reconnecting... ({reconnect_attempts}/{max_reconnect})")
                        time.sleep(0.5)
                        self.cap.release()
                        self.cap = cv2.VideoCapture(self.source)
                    else:
                        print("[ERROR] Camera connection lost!")
                        self.running = False
            else:
                self.running = False
            
            time.sleep(0.01)  # Prevent CPU hogging

    def read(self):
        """Return the latest frame."""
        with self.lock:
            if self.frame is not None:
                if self.mirror:
                    return self.ret, cv2.flip(self.frame, 1)
                return self.ret, self.frame.copy()
            return self.ret, None

    def get_resolution(self):
        """Get current camera resolution."""
        return (
            int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )

    def stop(self):
        """Stop the camera thread and release resources."""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=2.0)
        self.cap.release()
        print("[INFO] Camera stopped")


# Quick test
if __name__ == "__main__":
    print("Testing camera with auto-detection...")
    cam = Camera(source='auto')
    
    print("Press 'q' to quit")
    while True:
        ret, frame = cam.read()
        if ret and frame is not None:
            w, h = cam.get_resolution()
            cv2.putText(frame, f"Resolution: {w}x{h}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("Camera Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cam.stop()
    cv2.destroyAllWindows()

