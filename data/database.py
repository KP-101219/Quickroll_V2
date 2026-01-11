import sqlite3
import os
import io
import numpy as np
import datetime

class Database:
    """
    SQLite database manager for QUICKROLL.
    Handles storage of students, embeddings, and attendance logs.
    """
    
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, "data", "quickroll.db")
        else:
            self.db_path = db_path
            
        self.init_db()

    def get_connection(self):
        """Get a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize the database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Students Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Embeddings Table
        # Store numpy array as BLOB
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            embedding BLOB NOT NULL,
            pose TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        ''')
        
        # Attendance Logs Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            date TEXT,
            time TEXT,
            confidence REAL,
            marked_by TEXT,
            status TEXT DEFAULT 'Present',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        ''')
        
        conn.commit()
        conn.close()

    def add_student(self, student_id, name):
        """Add a new student."""
        conn = self.get_connection()
        try:
            conn.execute('INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)', 
                         (student_id, name))
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB ERROR] Add Student: {e}")
            return False
        finally:
            conn.close()

    def add_embedding(self, student_id, embedding, pose):
        """Add a face embedding."""
        if isinstance(embedding, np.ndarray):
            # Serialize numpy array to bytes
            emb_blob = embedding.tobytes()
        else:
            emb_blob = embedding

        conn = self.get_connection()
        try:
            conn.execute('INSERT INTO embeddings (student_id, embedding, pose) VALUES (?, ?, ?)',
                         (student_id, emb_blob, pose))
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB ERROR] Add Embedding: {e}")
            return False
        finally:
            conn.close()

    def mark_attendance(self, student_id, date, time, confidence, marked_by="face_recognition"):
        """Log attendance."""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO attendance_logs (student_id, date, time, confidence, marked_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, date, time, float(confidence), marked_by))
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB ERROR] Mark Attendance: {e}")
            return False
        finally:
            conn.close()

    def delete_student(self, student_id):
        """Delete student and all associated data."""
        conn = self.get_connection()
        try:
            conn.execute('DELETE FROM embeddings WHERE student_id = ?', (student_id,))
            conn.execute('DELETE FROM attendance_logs WHERE student_id = ?', (student_id,))
            conn.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB ERROR] Delete Student: {e}")
            return False
        finally:
            conn.close()

    def get_all_embeddings(self):
        """
        Fetch all embeddings.
        Returns: {student_id: [emb_array1, emb_array2, ...]}
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT student_id, embedding FROM embeddings')
        rows = cursor.fetchall()
        
        embeddings = {}
        for s_id, blob in rows:
            # Reconstruct numpy array (128 floats)
            emb_arr = np.frombuffer(blob, dtype=np.float32)
            # Ensure shape matches SFace output (1, 128)
            emb_arr = emb_arr.reshape(1, 128)
            
            if s_id not in embeddings:
                embeddings[s_id] = []
            embeddings[s_id].append(emb_arr)
            
        conn.close()
        return embeddings

    def get_student_map(self):
        """
        Get mapping of student_id -> info.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT student_id, name FROM students')
        
        student_map = {}
        for s_id, name in cursor.fetchall():
            student_map[s_id] = {"name": name, "id": s_id}
            
        conn.close()
        return student_map

    def get_attendance_history(self, date=None):
        """Get attendance logs, optionally filtered by date (YYYY-MM-DD)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT a.student_id, s.name, a.time, a.status, a.confidence, a.marked_by
            FROM attendance_logs a
            LEFT JOIN students s ON a.student_id = s.student_id
        '''
        params = []
        if date:
            query += ' WHERE a.date = ?'
            params.append(date)
            
        query += ' ORDER BY a.time DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        history = []
        for r in rows:
            history.append({
                "id": r[0],
                "name": r[1],
                "time": r[2],
                "status": r[3],
                "confidence": r[4],
                "marked_by": r[5]
            })
        return history
