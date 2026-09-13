from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    source_id: str
    event_type: str
    object_type: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int
    image_path: str
    plate_number: Optional[str] = None
    person_id: Optional[str] = None

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class Stats(BaseModel):
    total_events: int
    total_persons: int
    total_vehicles: int
    total_incidents: int
