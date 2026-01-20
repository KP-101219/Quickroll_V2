import cv2
import sys

print("=" * 50)
print("Camera Detection")
print("=" * 50)
print()

available_cameras = []

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            print(f"[OK] Camera {i}: {w}x{h} resolution")
            available_cameras.append(i)
        cap.release()
    else:
        print(f"[ ] Camera {i}: Not available")

print()
if available_cameras:
    print(f"Found {len(available_cameras)} camera(s): {available_cameras}")
    print()
    print(f"Camera 0 is typically your built-in PC camera")
    print(f"Higher indices (1, 2, etc.) are often DroidCam or USB cameras")
else:
    print("No cameras found!")
