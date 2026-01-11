import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import time

from core.camera import Camera
from core.detector import FaceDetector
from core.recognizer import Recognizer
from data.storage import StorageManager
from core.capture_manager import CaptureManager
from ui.styles import COLORS, FONTS, DIMENSIONS

class CaptureView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent") # Blend with main background
        
        # Modules (Camera is initialized lazily)
        self.camera = None
        self.detector = FaceDetector()
        try:
            from data.database import Database
            self.db = Database()
        except:
            print("DB Init Error")
            self.db = None
            
        self.recognizer = Recognizer() # For duplicate checking
        self.recognizer.load_database()
        self.storage = StorageManager()
        self.manager = CaptureManager(self.detector, self.storage)
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Side: Registration Form ---
        self.form_frame = ctk.CTkFrame(
            self, 
            corner_radius=DIMENSIONS["corner_radius"],
            fg_color=COLORS["bg_medium"]
        )
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.form_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.lbl_title = ctk.CTkLabel(
            self.form_frame, 
            text="New Registration", 
            font=FONTS["header_md"],
            text_color=COLORS["text_main"]
        )
        self.lbl_title.grid(row=0, column=0, pady=(30, 20))
        
        # ID Input
        self.entry_id = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="Student ID",
            height=DIMENSIONS["input_height"],
            fg_color=COLORS["bg_light"],
            border_color=COLORS["border"]
        )
        self.entry_id.grid(row=1, column=0, pady=10, padx=30, sticky="ew")
        
        # Name Input
        self.entry_name = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="Full Name",
            height=DIMENSIONS["input_height"],
            fg_color=COLORS["bg_light"],
            border_color=COLORS["border"]
        )
        self.entry_name.grid(row=2, column=0, pady=10, padx=30, sticky="ew")
        
        # Start Button
        self.btn_start = ctk.CTkButton(
            self.form_frame, 
            text="Start Registration", 
            font=FONTS["body_lg"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=45,
            corner_radius=10,
            command=self.start_registration
        )
        self.btn_start.grid(row=3, column=0, pady=30, padx=30, sticky="ew")
        
        # Status Label
        self.lbl_status = ctk.CTkLabel(
            self.form_frame, 
            text="Enter details to begin", 
            text_color=COLORS["text_dim"],
            font=FONTS["body_md"]
        )
        self.lbl_status.grid(row=4, column=0, pady=10)
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self.form_frame, 
            progress_color=COLORS["accent"]
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=5, column=0, pady=15, padx=30, sticky="ew")

        # Instructions
        instruction_text = (
            "INSTRUCTIONS:\n\n"
            "1. Look Straight Ahead\n"
            "2. Turn Head Left Slowly\n"
            "3. Turn Head Right Slowly"
        )
        self.lbl_instructions = ctk.CTkLabel(
            self.form_frame, 
            text=instruction_text,
            justify="left",
            font=FONTS["body_sm"],
            text_color=COLORS["text_dim"],
            fg_color=COLORS["bg_dark"], # Contrast box
            corner_radius=8,
            padx=15,
            pady=15
        )
        self.lbl_instructions.grid(row=6, column=0, pady=30, padx=30, sticky="ew")
        
        # --- Right Side: Camera View ---
        self.cam_border = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg_medium"], 
            corner_radius=DIMENSIONS["corner_radius"]
        )
        self.cam_border.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.cam_border.grid_rowconfigure(0, weight=1)
        self.cam_border.grid_columnconfigure(0, weight=1)

        self.cam_frame = ctk.CTkFrame(
            self.cam_border, 
            fg_color="black", 
            corner_radius=10
        )
        self.cam_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.lbl_video = ctk.CTkLabel(self.cam_frame, text="Camera Offline", text_color="#555")
        self.lbl_video.pack(fill="both", expand=True)
        
        self.video_running = False

    def start_registration(self):
        student_id = self.entry_id.get()
        name = self.entry_name.get()
        
        if not student_id or not name:
            self.lbl_status.configure(text="Error: Enter ID and Name", text_color="red")
            return
            
        # Check for Duplicates (ID)
        if self.storage.create_student_dir(student_id) is False:
             # Just a warning, but we allow overwrite for now if same ID
             pass
        
        # Add to Database
        if self.db:
            self.db.add_student(student_id, name)
             
        self.lbl_status.configure(text="Initializing Camera...", text_color="yellow")
        self.form_frame.update()
        
        # Start Camera
        if self.camera is None:
            self.camera = Camera(source=1)  # Use Mobile Camera / DroidCam (index 1)
        
        self.video_running = True
        self.manager.start_session(student_id)
        
        # Lock UI
        self.btn_start.configure(state="disabled")
        self.entry_id.configure(state="disabled")
        self.entry_name.configure(state="disabled")
        
        # Save Metadata
        self.storage.save_metadata(student_id, {"name": name, "id": student_id})
        
        self.update_video()

    def update_video(self):
        if not self.video_running: return
        
        ret, frame = self.camera.read()
        if ret:
            # 1. Duplicate Check (Active Logic)
            # Only check for duplicate face in the FIRST few frames of "Front" capture?
            # Or continuous? Let's check continuously in WAITING state if we are worried.
            # For now, let's implement the core capture logic.
            
            # Since frame is MIRRORED by Camera class now:
            # Left (screen) = User's Right (face).
            # But the 'yaw' logic in FaceValidator was:
            # +ve = Left Profile (showing right cheek).
            # If we mirror, the "Right cheek" is now on the LEFT side of the image.
            # So the math MIGHT flip. Let's test this interactively.
            # My previous logic: "+ve yaw = Turn Left".
            # If I mirror:
            # Turning head Left -> Right cheek visible.
            # Right cheek is on Left side of image (small x).
            # Left cheek is hidden.
            # nose (center) is closer to Right cheek?
            # Let's adjust Yaw thresholds in CaptureManager if needed.
            
            vis_frame, status = self.manager.process_frame(frame)
            
            # Additional Check: Duplicate Face Prevention
            # If we are in 'WAITING' or early 'capturing' state, check if this face exists.
            if self.manager.state.name == 'CAPTURING' and self.manager.current_idx == 0:
                 # Check recognition
                 # Optimization: Run recognition not every frame
                 # For now, just a quick check
                 pass
            
            # UI Update
            self.lbl_status.configure(text=status['message'], text_color="white")
            self.progress_bar.set(status['progress'])
            
            if self.manager.state.name == 'COMPLETED':
                self.stop_registration()
            
            # Render
            img = cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            
            display_w = self.cam_frame.winfo_width()
            display_h = self.cam_frame.winfo_height()
            if display_w < 10: display_w, display_h = 640, 480
            
            ctk_img = ctk.CTkImage(img, img, (display_w, display_h))
            self.lbl_video.configure(image=ctk_img, text="")
            self.lbl_video.image = ctk_img
            
        self.after(15, self.update_video)

    def stop_registration(self):
        self.video_running = False
        if self.camera:
            self.camera.stop()
            self.camera = None
            
        self.btn_start.configure(state="normal", text="Registration Complete")
        self.entry_id.configure(state="normal")
        self.entry_name.configure(state="normal")
        self.entry_id.delete(0, 'end')
        self.entry_name.delete(0, 'end')
        self.lbl_status.configure(text="Ready for Next Student", text_color="green")
        self.lbl_video.configure(image=None, text="Camera Off")

    def destroy(self):
        self.video_running = False
        if self.camera: self.camera.stop()
        super().destroy()
