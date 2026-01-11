import customtkinter as ctk
try:
    # Set appearance mode before creating any widgets
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = ctk.CTk()
    
    print("Importing AttendanceView...")
    from ui.attendance_view import AttendanceView
    
    print("Initializing AttendanceView...")
    view = AttendanceView(app)
    print("AttendanceView created successfully.")
    
    # Test FrameTracker processing (simulating camera feed)
    print("Testing FrameTracker processing...")
    import numpy as np
    import cv2
    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Process a few frames to trigger detection and tracking logic
    for i in range(10):
        view.frame_tracker.process_frame(dummy_frame)
    print("FrameTracker processed 10 frames successfully.")
    
    # Cleanup
    view.destroy()
    app.destroy()
    print("SUCCESS: Test passed.")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"ERROR: {e}")
