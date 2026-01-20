import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import time

from core.camera import Camera
from core.detector import FaceDetector
from core.recognizer import Recognizer
from core.attendance_manager import AttendanceManager
from core.frame_tracker import FrameTracker, FPSCounter
from ui.styles import COLORS, FONTS, DIMENSIONS

def detect_available_cameras():
    """Force return only PC camera (Index 0)."""
    return [(0, "PC Camera (Force Index 0)", 640, 480)]


class AttendanceView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        # Detect available cameras first
        self.available_cameras = detect_available_cameras()
        self.current_camera_idx = 0 # Force 0
        
        # Initialize Core Modules
        self.camera = Camera(source=0) # FORCE PC CAMERA
        self.detector = FaceDetector()
        self.recognizer = Recognizer()
        self.recognizer.load_database()
        self.attendance = AttendanceManager()
        
        # Phase 2: Frame Tracker for optimized performance
        self.frame_tracker = FrameTracker(
            self.detector, 
            self.recognizer,
            detection_interval=5,
            recognition_interval=15
        )
        self.fps_counter = FPSCounter()
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main Container (Card)
        self.view_container = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg_medium"], 
            corner_radius=DIMENSIONS["corner_radius"]
        )
        self.view_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

        # Camera Feed
        self.lbl_video = ctk.CTkLabel(self.view_container, text="")
        self.lbl_video.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Overlay Stats Frame (top-left) - Styled as a HUD
        self.stats_frame = ctk.CTkFrame(
            self.view_container, 
            fg_color=COLORS["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.stats_frame.grid(row=0, column=0, sticky="nw", padx=30, pady=30)
        
        self.lbl_count = ctk.CTkLabel(
            self.stats_frame, 
            text="Today: 0", 
            font=FONTS["header_md"],
            text_color=COLORS["success"]
        )
        self.lbl_count.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.lbl_fps = ctk.CTkLabel(
            self.stats_frame, 
            text="FPS: --", 
            font=FONTS["body_sm"],
            text_color=COLORS["text_dim"]
        )
        self.lbl_fps.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.lbl_confidence = ctk.CTkLabel(
            self.stats_frame, 
            text="Avg Confidence: --", 
            font=FONTS["body_sm"],
            text_color=COLORS["text_dim"]
        )
        self.lbl_confidence.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Camera Switcher Frame (top-right)
        self.camera_frame = ctk.CTkFrame(
            self.view_container, 
            fg_color=COLORS["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.camera_frame.grid(row=0, column=0, sticky="ne", padx=30, pady=30)
        
        self.lbl_camera = ctk.CTkLabel(
            self.camera_frame, 
            text="DEVICE SETUP", 
            font=FONTS["body_sm"],
            text_color=COLORS["accent"]
        )
        self.lbl_camera.pack(side="left", padx=(15, 10), pady=10)
        
        # Camera dropdown
        camera_options = [cam[1] for cam in self.available_cameras]
        if not camera_options:
            camera_options = ["No cameras found"]
        
        self.camera_var = ctk.StringVar(value=camera_options[0])
        self.camera_dropdown = ctk.CTkOptionMenu(
            self.camera_frame,
            values=camera_options,
            variable=self.camera_var,
            command=self.on_camera_change,
            width=180,
            fg_color=COLORS["bg_light"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"]
        )
        self.camera_dropdown.pack(side="left", padx=(0, 10), pady=10)
        
        # Mirror Switch
        self.mirror_var = ctk.BooleanVar(value=True)
        self.mirror_switch = ctk.CTkSwitch(
            self.camera_frame, 
            text="Mirror",
            text_color=COLORS["text_main"],
            variable=self.mirror_var,
            command=self.on_mirror_change,
            onvalue=True,
            offvalue=False,
            width=80,
            progress_color=COLORS["primary"]
        )
        self.mirror_switch.pack(side="left", padx=(0, 15), pady=10)
        
        # Start Loop
        self.running = True
        self.update_loop()
    
    def on_mirror_change(self):
        """Handle mirror toggle."""
        self.camera.mirror = self.mirror_var.get()
        # Reset tracking because coordinates flip
        self.frame_tracker.reset()
    
    def on_camera_change(self, selection):
        """Handle camera switch - Forced to keep Camera 0."""
        print(f"[INFO] Selection changed to {selection}, but FORCING Camera 0")
        
        # Stop current camera
        self.camera.stop()
        
        # Reset frame tracker
        self.frame_tracker.reset()
        
        # Start new camera (Force 0)
        self.current_camera_idx = 0
        try:
            self.camera = Camera(source=0)
        except Exception as e:
            print(f"[ERROR] Failed to switch camera: {e}")
            self.camera = Camera(source=0)

    def update_loop(self):
        if not self.running: return
        
        ret, frame = self.camera.read()
        if ret:
            # Use FrameTracker for optimized processing
            face_results = self.frame_tracker.process_frame(frame)
            fps = self.fps_counter.update()
            
            # Visualize results
            vis_frame = frame.copy()
            
            for result in face_results:
                x, y, w, h = result['bbox']
                status = result['status']
                confidence = result['confidence']
                name = result['name']
                student_id = result['student_id']
                is_tracked = result.get('is_tracked', False)
                
                # Color based on status
                if status == "RECOGNIZED":
                    success, msg = self.attendance.mark_attendance(student_id, name, confidence)
                    
                    if success:
                        color = (0, 255, 0)
                        status_text = f"{name} - PRESENT ({confidence:.0%})"
                    elif "Already" in msg:
                        color = (0, 255, 255)
                        status_text = f"{name} - RECORDED ({confidence:.0%})"
                    else:
                        color = (0, 255, 0)
                        status_text = f"{name} ({confidence:.0%})"
                        
                elif status == "MAYBE":
                    color = (0, 165, 255)
                    status_text = f"Maybe: {name}? ({confidence:.0%})"
                    
                else:
                    color = (0, 0, 255)
                    status_text = f"{name} ({confidence:.0%})" if confidence > 0 else name
                
                # Draw bounding box
                if is_tracked:
                    cv2.rectangle(vis_frame, (x, y), (x+w, y+h), color, 1)
                else:
                    cv2.rectangle(vis_frame, (x, y), (x+w, y+h), color, 2)
                
                # Draw status text with background
                text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(vis_frame, (x, y-25), (x + text_size[0] + 5, y-5), (0, 0, 0), -1)
                cv2.putText(vis_frame, status_text, (x+2, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Draw confidence bar
                if confidence > 0:
                    bar_width = int(w * confidence)
                    cv2.rectangle(vis_frame, (x, y+h+5), (x+bar_width, y+h+10), color, -1)
                    cv2.rectangle(vis_frame, (x, y+h+5), (x+w, y+h+10), (100, 100, 100), 1)
            
            # Draw FPS on frame
            cv2.putText(vis_frame, f"FPS: {fps:.1f}", (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Update UI labels
            self.lbl_count.configure(text=f"Today: {self.attendance.get_todays_count()}")
            self.lbl_fps.configure(text=f"FPS: {fps:.1f}")
            
            stats = self.attendance.get_confidence_stats()
            if stats['avg_confidence'] > 0:
                self.lbl_confidence.configure(
                    text=f"Avg: {stats['avg_confidence']:.0%} | High: {stats['high_confidence_count']}"
                )
            
            # Display frame
            img = cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            
            display_w = self.lbl_video.winfo_width()
            display_h = self.lbl_video.winfo_height()
            
            if display_w < 10 or display_h < 10:
                display_w, display_h = 640, 480
                 
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(display_w, display_h))
            self.lbl_video.configure(image=ctk_img)
            self.lbl_video.image = ctk_img
            
        self.after(15, self.update_loop)

    def destroy(self):
        self.running = False
        self.camera.stop()
        super().destroy()



