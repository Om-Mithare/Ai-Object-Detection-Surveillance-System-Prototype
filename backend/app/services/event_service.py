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
        
        for det in detections:
            # 1. Determine base event type
            event_type = f"{det['object_type'].upper()}_DETECTED"
            
            # 2. Basic Incident Rule Check (Hackathon MVP logic)
            # Rule: If we see a person with a face, we can flag it for review
            # Rule: If confidence is very low but it's a person, flag it as INCIDENT
            if det['object_type'] == "person" and det['confidence'] < 0.3:
                event_type = "INCIDENT_LOW_CONFIDENCE_PERSON"
            
            if det.get("plate_number"):
                event_type = "PLATE_RECOGNIZED"
                
            if det['object_type'] == "person_with_face":
                event_type = "FACE_DETECTED"

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
