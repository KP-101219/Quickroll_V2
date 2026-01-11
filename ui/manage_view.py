import customtkinter as ctk
import os
import shutil
import glob
import json
from ui.styles import COLORS, FONTS, DIMENSIONS

class ManageView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        # Data path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.students_dir = os.path.join(base_dir, "data", "students")
        
        try:
            from data.database import Database
            self.db = Database()
        except:
            print("DB Init Error")
            self.db = None
            
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(
            self, 
            height=60, 
            fg_color=COLORS["bg_medium"],
            corner_radius=DIMENSIONS["corner_radius"]
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.lbl_title = ctk.CTkLabel(
            self.header_frame, 
            text="Manage Registered Students", 
            font=FONTS["header_md"],
            text_color=COLORS["text_main"]
        )
        self.lbl_title.pack(side="left", padx=20, pady=15)
        
        self.btn_refresh = ctk.CTkButton(
            self.header_frame, 
            text="Refresh List", 
            width=120,
            command=self.load_students,
            fg_color=COLORS["bg_light"],
            hover_color=COLORS["primary"],
            text_color=COLORS["text_main"]
        )
        self.btn_refresh.pack(side="right", padx=20)
        
        # Scrollable List
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_medium"],
            corner_radius=DIMENSIONS["corner_radius"]
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Footer
        self.lbl_hint = ctk.CTkLabel(
            self, 
            text="Changes are applied immediately.", 
            text_color=COLORS["text_dim"], 
            font=FONTS["body_sm"]
        )
        self.lbl_hint.grid(row=2, column=0, pady=5)
        
        self.load_students()
        
    def load_students(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        if self.db is None:
            return

        # Load from DB
        student_map = self.db.get_student_map()
        
        idx = 0
        sorted_students = sorted(student_map.items(), key=lambda x: x[0]) # Sort by ID
        
        for s_id, info in sorted_students:
            name = info.get("name", "Unknown")
            self.create_student_row(idx, s_id, name)
            idx += 1
            
        if idx == 0:
            ctk.CTkLabel(self.scroll_frame, text="No students registered yet.", text_color="gray").pack(pady=20)

    def create_student_row(self, idx, student_id, name):
        row = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["bg_dark"])
        row.pack(fill="x", padx=10, pady=5)
        
        # ID Badge
        id_badge = ctk.CTkLabel(
            row, 
            text=f"ID: {student_id}", 
            width=80, 
            font=FONTS["body_sm"],
            fg_color=COLORS["bg_light"],
            corner_radius=5
        )
        id_badge.pack(side="left", padx=10, pady=10)
        
        # Name
        ctk.CTkLabel(
            row, 
            text=f"{name}", 
            font=FONTS["body_md"],
            text_color="white"
        ).pack(side="left", padx=10)
        
        # Delete Button
        btn_del = ctk.CTkButton(
            row, 
            text="Delete", 
            width=80, 
            fg_color=COLORS["error"], 
            hover_color="#D50000",
            height=30,
            command=lambda s=student_id: self.delete_student(s)
        )
        btn_del.pack(side="right", padx=10, pady=10)

    def delete_student(self, student_id):
        # Delete from DB
        if self.db:
            success = self.db.delete_student(student_id)
            if success:
                print(f"[MANAGE] Deleted {student_id} from DB")
            else:
                print(f"[ERROR] Failed to delete {student_id} from DB")

        # Delete from File System
        target = os.path.join(self.students_dir, student_id)
        if os.path.exists(target):
            try:
                shutil.rmtree(target)
                print(f"[MANAGE] Deleted {target}")
            except Exception as e:
                print(f"[ERROR] Delete file failed: {e}")
        
        self.load_students()
