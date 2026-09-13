from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, index=True) # E.g., 'Camera-01' or 'Upload-video1.mp4'
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    event_type = Column(String, index=True) # e.g., OBJECT_DETECTED, INCIDENT
    object_type = Column(String, index=True) # e.g., person, car, motorcycle
    confidence = Column(Float)
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)
    image_path = Column(String) # Path to the saved frame/crop
    plate_number = Column(String, nullable=True, index=True) # For ALPR
    person_id = Column(String, nullable=True, index=True) # For face recognition
    created_at = Column(DateTime(timezone=True), server_default=func.now())
