import cv2

def test_camera(index):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Camera {index} NOT available")
        return
    
    print(f"Testing Camera {index}... Press 'q' to close this camera window.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to read from Camera {index}")
            break
            
        cv2.putText(frame, f"CAMERA {index}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow(f"TESTING CAMERA {index}", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

print("We will test Camera 0 first. Look at the popup window.")
print("If it's DroidCam, close it (press 'q') and we will try Camera 1.")
test_camera(0)

print("\nNow testing Camera 1...")
test_camera(1)

print("\nNow testing Camera 2...")
test_camera(2)
