import time
import datetime
import os
import csv

class AttendanceManager:
    """
    Manages attendance logic:
    - Cooldowns (Don't mark same person twice in X mins)
    - Logging (Save to CSV/DB)
    - Status tracking
    - Decision engine for confidence-based marking
    """
    
    # Confidence thresholds (should match Recognizer thresholds)
    HIGH_CONFIDENCE = 0.75
    LOW_CONFIDENCE = 0.50
    
    def __init__(self, cooldown_seconds=900): # 15 mins default
        self.cooldown_seconds = cooldown_seconds
        self.last_marked = {} # {student_id: timestamp}
        self.today_log = [] # List of dicts
        
        try:
            from data.database import Database
            self.db = Database()
            
            # Load today's history from DB to populate cache
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            history = self.db.get_attendance_history(date=today_str)
            
            # Populate cache and last_marked
            self.today_log = history
            
            for rec in history:
                # Approximate timestamp from time string
                t_str = rec['time']
                full_dt_str = f"{today_str} {t_str}"
                try:
                    dt = datetime.datetime.strptime(full_dt_str, "%Y-%m-%d %H:%M:%S")
                    self.last_marked[rec['id']] = dt.timestamp()
                except:
                    pass
        except ImportError:
            print("[ERROR] Could not import Database module.")
            self.db = None

    def should_mark_attendance(self, confidence, student_id=None):
        """
        Decision engine for attendance marking based on confidence.
        
        This implements the SmartPencs-style decision logic:
        - HIGH confidence: Auto-mark attendance
        - LOW confidence: Show as 'MAYBE' - may need verification
        - UNKNOWN: Not recognized
        
        Args:
            confidence: Float recognition confidence (0.0-1.0)
            student_id: Optional student ID for cooldown check
            
        Returns: dict with keys:
            - action: 'AUTO_MARK', 'MAYBE', 'UNKNOWN'
            - status: Human-readable status
            - requires_verification: bool
            - message: Display message
            - can_mark: bool (False if in cooldown)
        """
        result = {
            'action': 'UNKNOWN',
            'status': 'NOT_RECOGNIZED',
            'requires_verification': True,
            'message': 'Unknown person',
            'can_mark': True
        }
        
        # Check cooldown if student_id provided
        if student_id:
            now = time.time()
            last_time = self.last_marked.get(student_id, 0)
            if now - last_time < self.cooldown_seconds:
                time_left = int(self.cooldown_seconds - (now - last_time))
                result['can_mark'] = False
                result['message'] = f"Already marked (wait {time_left}s)"
                result['action'] = 'COOLDOWN'
                return result
        
        # Decision based on confidence
        if confidence >= self.HIGH_CONFIDENCE:
            result['action'] = 'AUTO_MARK'
            result['status'] = 'RECOGNIZED'
            result['requires_verification'] = False
            result['message'] = 'High confidence - auto marking'
        elif confidence >= self.LOW_CONFIDENCE:
            result['action'] = 'MAYBE'
            result['status'] = 'MAYBE'
            result['requires_verification'] = True
            result['message'] = f'Medium confidence ({confidence:.0%}) - verification optional'
        else:
            result['action'] = 'UNKNOWN'
            result['status'] = 'NOT_RECOGNIZED'
            result['requires_verification'] = True
            result['message'] = 'Unknown person'
        
        return result

    def mark_attendance(self, student_id, name, confidence, marked_by="face_recognition"):
        """
        Attempt to mark attendance. 
        """
        now = time.time()
        
        # Check cooldown
        last_time = self.last_marked.get(student_id, 0)
        if now - last_time < self.cooldown_seconds:
            time_left = int(self.cooldown_seconds - (now - last_time))
            return False, f"Already Marked (Wait {time_left}s)"
            
        # Time strings
        timestamp_str = datetime.datetime.now().strftime("%H:%M:%S")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # DB Write
        if self.db:
            success = self.db.mark_attendance(student_id, date_str, timestamp_str, confidence, marked_by)
            if not success:
                return False, "Database Error"
        
        # Update Cache
        record = {
            "id": student_id,
            "name": name,
            "time": timestamp_str,
            "status": "Present",
            "confidence": f"{confidence:.2f}",
            "marked_by": marked_by
        }
        
        self.today_log.append(record)
        self.last_marked[student_id] = now
        
        print(f"[ATTENDANCE] Marked {name} ({student_id}) at {timestamp_str}")
        return True, "Marked Present"

    def get_todays_count(self):
        return len(self.today_log)
    
    def get_todays_records(self):
        """Get all attendance records for today."""
        return self.today_log.copy()
    
    def get_confidence_stats(self):
        """
        Get statistics about confidence scores for today's attendance.
        Useful for monitoring system accuracy.
        
        Returns: dict with 'high_confidence_count', 'low_confidence_count', 'avg_confidence'
        """
        if not self.today_log:
            return {'high_confidence_count': 0, 'low_confidence_count': 0, 'avg_confidence': 0.0}
        
        confidences = [float(r['confidence']) for r in self.today_log]
        high_count = sum(1 for c in confidences if c >= self.HIGH_CONFIDENCE)
        low_count = sum(1 for c in confidences if c < self.LOW_CONFIDENCE)
        
        return {
            'high_confidence_count': high_count,
            'low_confidence_count': low_count,
            'avg_confidence': sum(confidences) / len(confidences)
        }

