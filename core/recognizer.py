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

    def _generate_embedding(self, image, face_data=None):
        """
        Generate 128D embedding from an image.
        
        Args:
            image: Full image or cropped face.
            face_data: (Optional) Detection result [x, y, w, h, x_re, y_re, ...]. 
                       Required for alignCrop.
        
        Returns:
            128D numpy array or None
        """
        if self.recognizer is None:
            return None
            
        try:
            # Method 1: Alignment (Preferred)
            # Requires full frame + face detection data (with landmarks)
            if face_data is not None:
                # alignCrop crops and aligns the face to 112x112
                aligned_face = self.recognizer.alignCrop(image, face_data)
                return self.recognizer.feature(aligned_face)
            
            # Method 2: Naive Resize (Legacy/Fallback)
            # Used if we only have a pre-cropped face without landmarks
            else:
                target = cv2.resize(image, (112, 112))
                return self.recognizer.feature(target)
                
        except Exception as e:
            print(f"[ERROR] Embedding Generation Failed: {e}")
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

    def recognize(self, image, face_data=None):
        """
        Match a face against the database.
        Returns: student_id, confidence, info_dict
        """
        if self.recognizer is None: return None, 0.0, {}
        
        target_emb = self._generate_embedding(image, face_data)
        if target_emb is None: return None, 0.0, {}
        
        # Reuse existing logic via _compute_all_scores or manual loop
        # For consistency, let's just use match_face_with_confidence logic
        best_id, status, conf, info = self.match_face_with_confidence(image, face_data)
        return best_id, conf, info

    def match_face_with_confidence(self, image, face_data=None):
        """
        Match face and return recognition status with confidence level.
        
        Args:
            image: Full frame or crop (if face_data is None)
            face_data: Detection result (for alignment)
        
        Returns: (student_id, status, confidence, info_dict)
        """
        if self.recognizer is None:
            return None, "UNKNOWN", 0.0, {}
        
        target_emb = self._generate_embedding(image, face_data)
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

    def get_top_matches(self, image, face_data=None, top_n=3):
        """
        Get top N candidate matches with confidence scores.
        Useful for displaying multiple possible matches to the user.
        
        Args:
            image: Full frame or crop (if face_data is None)
            face_data: Detection result (for alignment)
        
        Returns: List of (student_id, confidence, info_dict) tuples
                 List will be empty if no embeddings exist or face is invalid.
        """
        if self.recognizer is None:
            return []
        
        target_emb = self._generate_embedding(image, face_data)
        if target_emb is None:
            return []
        
        all_scores = self._compute_all_scores(target_emb)
        
        # Return top N matches (only those above MIN_CONFIDENCE)
        top_matches = []
        for s_id, score, info in all_scores[:top_n]:
            if score >= self.MIN_CONFIDENCE:
                top_matches.append((s_id, score, info))
        
        return top_matches

