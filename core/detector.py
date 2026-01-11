import cv2
import numpy as np
import os

class FaceDetector:
    def __init__(self, model_path=None, conf_threshold=0.8, nms_threshold=0.3, top_k=5000):
        """
        Initialize YuNet Face Detector.
        """
        if model_path is None:
            # Default to the models directory relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "face_detection_yunet_2023mar.onnx")
            
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self.top_k = top_k
        
        # Initialize YuNet
        try:
            self.detector = cv2.FaceDetectorYN.create(
                model=self.model_path,
                config="",
                input_size=(320, 320),
                score_threshold=self.conf_threshold,
                nms_threshold=self.nms_threshold,
                top_k=self.top_k
            )
            print(f"[INFO] YuNet Face Detector loaded from {self.model_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load YuNet: {e}")
            self.detector = None

    def set_input_size(self, width, height):
        """
        Update the input size for the detector. 
        Must be called before detection if frame size changes.
        """
        if self.detector:
            self.detector.setInputSize((width, height))

    def detect(self, frame):
        """
        Detect faces in the frame.
        Returns: list of faces, where each face is [x, y, w, h, x1, y1, x2, y2, ... confidence]
        """
        if self.detector is None:
            return []
            
        # Ensure input size matches frame size
        h, w = frame.shape[:2]
        self.set_input_size(w, h)
        
        faces = self.detector.detect(frame)
        
        # faces[1] contains the actual detections
        return faces[1] if faces[1] is not None else []

    def visualize(self, frame, faces):
        """
        Draw bounding boxes and landmarks on the frame.
        """
        output = frame.copy()
        for face in faces:
            # Bounding box
            box = face[0:4].astype(np.int32)
            cv2.rectangle(output, (box[0], box[1]), (box[0]+box[2], box[1]+box[3]), (0, 255, 0), 2)
            
            # Landmarks (5 points)
            landmarks = face[4:14].astype(np.int32).reshape((5, 2))
            for idx, landmark in enumerate(landmarks):
                color = (0, 0, 255) if idx < 2 else (0, 255, 255) # Eyes red, others yellow
                cv2.circle(output, (landmark[0], landmark[1]), 2, color, -1)
                
            # Confidence
            conf = face[14]
            cv2.putText(output, f"{conf:.2f}", (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
        return output
