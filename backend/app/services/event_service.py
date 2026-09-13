from sqlalchemy.orm import Session
from app.models.models import Event
from typing import List, Dict, Any
from datetime import datetime

class EventService:
    def process_detections(self, db: Session, detections: List[Dict[str, Any]]):
        """
        Takes raw detections from the CV pipeline, evaluates rules, 
        and stores them as events in the database.
        """
        events_to_create = []
        
        # Group detections by frame (timestamp_offset) for spatial/context rules
        frames = {}
        for det in detections:
            ts = det.get("timestamp_offset", 0.0)
            if ts not in frames:
                frames[ts] = []
            frames[ts].append(det)

        for ts, frame_dets in frames.items():
            # 1. Analyze the frame context for accidents
            has_fallen_person = False
            has_bike = False
            
            for det in frame_dets:
                w = det["x2"] - det["x1"]
                h = det["y2"] - det["y1"]
                
                # Make fall detection highly sensitive for CCTV angles
                if "person" in det["object_type"] and w > h * 0.7:
                    has_fallen_person = True
                if det["object_type"] in ["bicycle", "motorcycle"]:
                    has_bike = True

            # 2. Process each detection in the frame
            for det in frame_dets:
                event_type = f"{det['object_type'].upper()}_DETECTED"
                
                if det['object_type'] == "person" and det['confidence'] < 0.3:
                    event_type = "INCIDENT_LOW_CONFIDENCE_PERSON"
                
                if det.get("plate_number"):
                    event_type = "PLATE_RECOGNIZED"
                    
                if det['object_type'] == "person_with_face":
                    event_type = "FACE_DETECTED"
                
                # Inject Accident Heuristics
                if has_fallen_person and has_bike:
                    if "person" in det["object_type"] or det["object_type"] in ["bicycle", "motorcycle"]:
                        event_type = "INCIDENT_BIKE_ACCIDENT"
                elif has_fallen_person and "person" in det["object_type"]:
                    event_type = "INCIDENT_PERSON_FALL"

                # Create the DB model
                db_event = Event(
                    source_id=det["source_id"],
                    event_type=event_type,
                    object_type=det["object_type"],
                    confidence=det["confidence"],
                    x1=det["x1"],
                    y1=det["y1"],
                    x2=det["x2"],
                    y2=det["y2"],
                    image_path=det["image_path"],
                    plate_number=det.get("plate_number"),
                    person_id=None # Extensible for Face Recognition later
                )
                events_to_create.append(db_event)
                
        if events_to_create:
            db.add_all(events_to_create)
            db.commit()
            
        return len(events_to_create)

event_service = EventService()
