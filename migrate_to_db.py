import os
import glob
import json
import csv
import cv2
from data.database import Database
from core.recognizer import Recognizer
import datetime

def migrate():
    print("starting Migration to SQLite...")
    
    # 1. Initialize Database
    db = Database()
    print("[INFO] Database initialized.")
    
    # 2. Initialize Recognizer for generating embeddings
    recognizer = Recognizer()
    if recognizer.recognizer is None:
        print("[ERROR] Recognizer validation failed. Cannot generate embeddings.")
        return
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data", "students")
    
    # 3. Migrate Students & Embeddings
    print("[INFO] Migrating Students and Embeddings...")
    student_dirs = glob.glob(os.path.join(data_dir, "*"))
    
    count_students = 0
    count_embeddings = 0
    
    for s_dir in student_dirs:
        if not os.path.isdir(s_dir): continue
        
        student_id = os.path.basename(s_dir)
        
        # Load Metadata
        name = "Unknown"
        meta_path = os.path.join(s_dir, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                data = json.load(f)
                name = data.get("name", "Unknown")
        
        # Insert Student
        db.add_student(student_id, name)
        count_students += 1
        
        # Load Images and Generate Embeddings
        for img_path in glob.glob(os.path.join(s_dir, "*.jpg")):
            # Determine pose from filename usually?
            # Filename format from CaptureManager: timestamp.jpg (doesn't contain pose?)
            # Wait, capture manager saves as timestamp.jpg. 
            # CaptureManager logic: self.storage.save_image ...
            # Actually we don't strictly need pose for recognition, but good for DB.
            # We'll just set pose='unknown'.
            
            # Use Recognizer to get embedding
            # We use _generate_embedding_from_file which reads the file
            emb = recognizer._generate_embedding_from_file(img_path)
            
            if emb is not None:
                db.add_embedding(student_id, emb, pose="unknown")
                count_embeddings += 1
                
    print(f"[SUCCESS] Migrated {count_students} students and {count_embeddings} embeddings.")
    
    # 4. Migrate Attendance Logs
    print("[INFO] Migrating Attendance Logs...")
    logs_dir = os.path.join(base_dir, "data", "logs")
    csv_files = glob.glob(os.path.join(logs_dir, "*.csv"))
    
    count_logs = 0
    
    for csv_file in csv_files:
        # Extract date from filename if possible: attendance_2023-12-01.csv
        filename = os.path.basename(csv_file)
        try:
            date_part = filename.replace("attendance_", "").replace(".csv", "")
            # Verify format
            datetime.datetime.strptime(date_part, "%Y-%m-%d")
        except:
            date_part = datetime.datetime.now().strftime("%Y-%m-%d")
            
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                s_id = row.get("id")
                time_str = row.get("time")
                conf = row.get("confidence", "0.0")
                marked_by = row.get("marked_by", "legacy") # Default for old logs
                
                if s_id:
                    db.mark_attendance(s_id, date_part, time_str, conf, marked_by)
                    count_logs += 1
                    
    print(f"[SUCCESS] Migrated {count_logs} attendance records.")
    print("Migration Complete!")

if __name__ == "__main__":
    migrate()
