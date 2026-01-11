import cv2
import numpy as np
import os
import glob
import json

class Recognizer:
    # Confidence thresholds for decision making
    # Tuned for high precision (avoid false positives)
    HIGH_CONFIDENCE = 0.75   # Auto-mark attendance (RECOGNIZED)
    LOW_CONFIDENCE = 0.50    # Require verification (MAYBE)
    MIN_CONFIDENCE = 0.40    # Below this = unknown
    
    def __init__(self, model_path=None, threshold=0.6):
        """
        Initialize SFace Recognizer.
        """
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "face_recognition_sface_2021dec.onnx")
            
        self.model_path = model_path
        self.threshold = threshold
        self.embeddings = {} # {student_id: [emb1, emb2, emb3]}
        self.student_map = {} # {student_id: {"name": "John"}}
        
        try:
            self.recognizer = cv2.FaceRecognizerSF.create(
                model=self.model_path,
                config=""
            )
            print(f"[INFO] SFace Recognizer loaded from {self.model_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load SFace: {e}")
            self.recognizer = None

    def load_database(self):
        """
        Load all student embeddings from SQLite Database.
        """
        if self.recognizer is None: return
        
        try:
            from data.database import Database
            db = Database()
            
            print("[INFO] Loading Face Database from SQLite...")
            self.embeddings = db.get_all_embeddings()
            
            # Load metadata
            self.student_map = db.get_student_map()
            
            count = len(self.embeddings)
            print(f"[INFO] Loaded {count} students into memory.")
            
        except ImportError:
            print("[ERROR] Could not import Database module.")
        except Exception as e:
            print(f"[ERROR] Database Load Failed: {e}")

    def _generate_embedding_from_file(self, image_path):
        image = cv2.imread(image_path)
        if image is None: return None
        return self._generate_embedding(image)

    def _generate_embedding(self, face_image):
        """
        Generate 128D embedding from a cropped face image.
        Note: SFace expects aligned 112x112 image. 
        For simplicity, we let SFace handle alignment if landmarks are provided, 
        but here we assume input IS the cropped face.
        """
        # Resize to 112x112 as required by SFace
        # Note: Ideally we should use alignCrop if we have landmarks, 
        # but since we saved cropped faces, we just resize.
        target = cv2.resize(face_image, (112, 112))
        
        # SFace expects float blob? No, the API handles it.
        # But alignCrop is better.
        # If we just pass the cropped image to feature(), it works.
        try:
            return self.recognizer.feature(target)
        except Exception as e:
            # print(f"Emb Error: {e}")
            return None

    def _compute_all_scores(self, target_emb):
        """
        Compute similarity scores against all enrolled students.
        Returns: List of (student_id, best_score, info_dict) sorted by score descending.
        """
        if target_emb is None:
            return []
        
        scores = []
        for s_id, emb_list in self.embeddings.items():
            best_score_for_student = 0.0
            for stored_emb in emb_list:
                score = self.recognizer.match(target_emb, stored_emb, 1)  # 1 = Cosine Similarity
                if score > best_score_for_student:
                    best_score_for_student = score
            
            scores.append((s_id, best_score_for_student, self.student_map.get(s_id, {})))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def recognize(self, face_image):
        """
        Match a face against the database.
        Returns: student_id, confidence, info_dict
                 OR None, 0.0, {} if no match
        """
        if self.recognizer is None: return None, 0.0, {}
        
        target_emb = self._generate_embedding(face_image)
        if target_emb is None: return None, 0.0, {}
        
        best_score = 0.0
        best_id = None
        
        # Compare against all students
        # Optimization: In Phase 5 we can use matrix multiplication.
        # For now (loop) is fine for distinct embeddings.
        for s_id, emp_list in self.embeddings.items():
            for stored_emb in emp_list:
                score = self.recognizer.match(target_emb, stored_emb, 1) # 1 = Cosine Similarity
                if score > best_score:
                    best_score = score
                    best_id = s_id
        
        if best_score > self.threshold:
            return best_id, best_score, self.student_map.get(best_id, {})
        
        return None, best_score, {}

    def match_face_with_confidence(self, face_image):
        """
        Match face and return recognition status with confidence level.
        
        This method implements the SmartPencs-style confidence scoring:
        - HIGH confidence (>=0.65): Auto-mark attendance
        - LOW confidence (0.45-0.65): May need verification
        - UNKNOWN (<0.45): Person not in database
        
        Returns: (student_id, status, confidence, info_dict)
            - student_id: Matched student ID or None
            - status: 'RECOGNIZED', 'MAYBE', or 'UNKNOWN'
            - confidence: Float score (0.0 - 1.0)
            - info_dict: Student metadata (name, etc.)
        """
        if self.recognizer is None:
            return None, "UNKNOWN", 0.0, {}
        
        target_emb = self._generate_embedding(face_image)
        if target_emb is None:
            return None, "UNKNOWN", 0.0, {}
        
        # Get all scores sorted by best match
        all_scores = self._compute_all_scores(target_emb)
        
        if not all_scores:
            return None, "UNKNOWN", 0.0, {}
        
        # Best match
        best_id, best_score, best_info = all_scores[0]
        
        # Determine status based on confidence thresholds
        if best_score >= self.HIGH_CONFIDENCE:
            status = "RECOGNIZED"
            return best_id, status, best_score, best_info
        elif best_score >= self.LOW_CONFIDENCE:
            status = "MAYBE"
            return best_id, status, best_score, best_info
        else:
            status = "UNKNOWN"
            return None, status, best_score, {}

    def get_top_matches(self, face_image, top_n=3):
        """
        Get top N candidate matches with confidence scores.
        Useful for displaying multiple possible matches to the user.
        
        Returns: List of (student_id, confidence, info_dict) tuples
                 List will be empty if no embeddings exist or face is invalid.
        """
        if self.recognizer is None:
            return []
        
        target_emb = self._generate_embedding(face_image)
        if target_emb is None:
            return []
        
        all_scores = self._compute_all_scores(target_emb)
        
        # Return top N matches (only those above MIN_CONFIDENCE)
        top_matches = []
        for s_id, score, info in all_scores[:top_n]:
            if score >= self.MIN_CONFIDENCE:
                top_matches.append((s_id, score, info))
        
        return top_matches

