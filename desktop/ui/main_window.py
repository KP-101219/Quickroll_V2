import customtkinter as ctk
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.capture_view import CaptureView
from ui.attendance_view import AttendanceView
from ui.manage_view import ManageView
from ui.styles import COLORS, FONTS, DIMENSIONS

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Quickroll V2 - Face Recognition System")
        self.geometry("1280x800")
        
        # Set theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue") # Fallback, we override manually
        
        # Background
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create Sidebar
        self.create_sidebar()
        
        # Create Main Area (Frames)
        self.frames = {}
        self.container = ctk.CTkFrame(self, fg_color="transparent") # Transparent to show bg_dark
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Initialize Views
        self.current_view = None
        self.show_view("capture")

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(
            self, 
            width=250, 
            corner_radius=0, 
            fg_color=COLORS["bg_medium"]
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # Spacer
        
        # Logo / Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="QUICKROLL", 
            font=FONTS["header_xl"],
            text_color=COLORS["accent"]
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Attendance System", 
            font=FONTS["body_sm"],
            text_color=COLORS["text_dim"]
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 40))
        
        # Buttons
        self.btn_capture = self.create_nav_button("Register Student", "capture", 2)
        self.btn_attendance = self.create_nav_button("Attendance Mode", "attendance", 3)
        self.btn_manage = self.create_nav_button("Manage Records", "manage", 4)
        
        # Footer
        self.lbl_version = ctk.CTkLabel(
            self.sidebar_frame,
            text="v2.0 Beta",
            font=FONTS["body_sm"],
            text_color="#555555"
        )
        self.lbl_version.grid(row=6, column=0, pady=20)

    def create_nav_button(self, text, view_name, row):
        btn = ctk.CTkButton(
            self.sidebar_frame, 
            text=text,
            font=FONTS["body_md"],
            fg_color="transparent", 
            text_color=COLORS["text_main"],
            hover_color=COLORS["bg_light"],
            anchor="w",
            height=50,
            corner_radius=10,
            command=lambda: self.show_view(view_name)
        )
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        return btn

    def highlight_button(self, view_name):
        # Reset all
        for btn in [self.btn_capture, self.btn_attendance, self.btn_manage]:
            btn.configure(fg_color="transparent", text_color=COLORS["text_main"])
            
        # Highlight active
        target = None
        if view_name == "capture": target = self.btn_capture
        elif view_name == "attendance": target = self.btn_attendance
        elif view_name == "manage": target = self.btn_manage
        
        if target:
            target.configure(fg_color=COLORS["primary"], text_color="white")

    def show_view(self, view_name):
        # Highlight sidebar
        self.highlight_button(view_name)
        
        # Destroy current view if exists
        for widget in self.container.winfo_children():
            widget.destroy()
            
        if view_name == "capture":
            # Lazy load
            view = CaptureView(self.container)
            view.pack(fill="both", expand=True)
        elif view_name == "attendance":
            view = AttendanceView(self.container)
            view.pack(fill="both", expand=True)
        elif view_name == "manage":
            view = ManageView(self.container)
            view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
