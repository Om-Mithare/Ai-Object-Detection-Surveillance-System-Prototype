import os
import cv2
import uuid
import re
from typing import List, Dict, Any
from ultralytics import YOLO
import easyocr
from dotenv import load_dotenv

load_dotenv()

class CVService:
    def __init__(self):
        # Read configurations
        self.model_path = os.getenv("YOLO_MODEL_PATH", "./models/yolov8n.pt")
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
        self.frame_skip = int(os.getenv("FRAME_SKIP", "5"))
        self.processed_dir = os.getenv("PROCESSED_DIR", "./processed")
        
        # Ensure directories exist
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # We initialize YOLO lazily or download if missing
        print(f"Loading YOLO model from {self.model_path}...")
        try:
            self.model = YOLO(self.model_path)
        except Exception as e:
            print(f"Failed to load YOLO model: {e}")
            self.model = YOLO("yolov8n.pt") 
            
        # Target classes we care about (COCO dataset IDs)
        # 0: person, 1: bicycle, 2: car, 3: motorcycle, 5: bus, 7: truck
        self.target_classes = [0, 1, 2, 3, 5, 7]
        
        # Initialize EasyOCR for ALPR (English only for speed/simplicity)
        print("Loading EasyOCR...")
        # Fallback to CPU if GPU isn't perfectly configured
        self.reader = easyocr.Reader(['en'], gpu=True) 
        
        # Load OpenCV Haar Cascade for Face Detection (Lightweight fallback)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def _map_class_id_to_name(self, class_id: int) -> str:
        mapping = {
            0: "person",
            1: "bicycle",
            2: "vehicle", 
            3: "motorcycle",
            5: "vehicle", 
            7: "vehicle"  
        }
        return mapping.get(class_id, "unknown")

    def _extract_license_plate(self, frame, x1, y1, x2, y2) -> str:
        """
        Attempts to read a license plate from a vehicle bounding box.
        """
        try:
            # Crop the vehicle
            vehicle_crop = frame[y1:y2, x1:x2]
            
            # Simple assumption for ALPR: Plates are usually in the lower half of the vehicle.
            # We crop the lower 50% to reduce OCR false positives on signs/logos.
            h, w = vehicle_crop.shape[:2]
            lower_half = vehicle_crop[int(h*0.5):h, 0:w]
            
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(lower_half, cv2.COLOR_BGR2GRAY)
            
            # Run EasyOCR
            results = self.reader.readtext(gray)
            
            for (bbox, text, prob) in results:
                if prob > 0.3: # Threshold for plate reading
                    # Clean text (remove non-alphanumeric)
                    clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
                    if len(clean_text) >= 4: # Typical plate length minimum
                        return clean_text
        except Exception as e:
            print(f"OCR Error: {e}")
            
        return None

    def _detect_faces_in_person(self, person_crop) -> bool:
        """
        Detects if a face is visible within a cropped person image.
        """
        try:
            gray = cv2.cvtColor(person_crop, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
            return len(faces) > 0
        except:
            return False

    def detect_frame(self, frame, source_id: str = "camera", timestamp_offset: float = 0.0) -> List[Dict[str, Any]]:
        results = self.model(frame, conf=self.confidence_threshold, classes=self.target_classes, verbose=False)
        detections = []
        
        if len(results) == 0:
            return detections
            
        result = results[0]
        boxes = result.boxes
        
        if len(boxes) > 0:
            annotated_frame = result.plot()
            frame_filename = f"{source_id}_{uuid.uuid4().hex[:8]}.jpg"
            frame_path = os.path.join(self.processed_dir, frame_filename)
            cv2.imwrite(frame_path, annotated_frame)
            
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                
                obj_type = self._map_class_id_to_name(cls_id)
                plate_number = None
                face_detected = False
                
                if obj_type == "vehicle":
                    plate_number = self._extract_license_plate(frame, x1, y1, x2, y2)
                    
                if obj_type == "person":
                    # Crop the person to look for faces
                    person_crop = frame[y1:y2, x1:x2]
                    face_detected = self._detect_faces_in_person(person_crop)
                    if face_detected:
                        # For the MVP, if we see a face, we might flag it differently or store it.
                        obj_type = "person_with_face"
                
                detections.append({
                    "source_id": source_id,
                    "object_type": obj_type,
                    "confidence": conf,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "image_path": frame_path,
                    "timestamp_offset": timestamp_offset,
                    "plate_number": plate_number
                })
                
        return detections

    def process_video(self, video_path: str, source_id: str) -> List[Dict[str, Any]]:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0 or fps != fps:
            fps = 30.0 
            
        frame_count = 0
        all_detections = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % self.frame_skip == 0:
                timestamp_offset = frame_count / fps
                detections = self.detect_frame(frame, source_id=source_id, timestamp_offset=timestamp_offset)
                all_detections.extend(detections)
                
            frame_count += 1
            
        cap.release()
        return all_detections

cv_service = CVService()
