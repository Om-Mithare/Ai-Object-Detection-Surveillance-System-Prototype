from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import os
import shutil
import uuid

from app.database.database import get_db
from app.schemas.schemas import Event, Stats
from app.models.models import Event as EventModel
from app.services.cv_service import cv_service
from app.services.event_service import event_service

router = APIRouter()

def process_video_task(file_path: str, source_id: str, db: Session):
    """Background task to process video so the API doesn't block."""
    try:
        detections = cv_service.process_video(file_path, source_id)
        event_service.process_detections(db, detections)
    except Exception as e:
        print(f"Error processing video {source_id}: {e}")

@router.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads a video/image and starts CV processing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename to avoid overwrites
    ext = file.filename.split(".")[-1]
    safe_filename = f"{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Start processing in background (for hackathon demo, we could also do it synchronously for instant feedback)
    background_tasks.add_task(process_video_task, file_path, safe_filename, db)
    
    return {"message": "Upload successful, processing started.", "source_id": safe_filename}

@router.get("/events", response_model=List[Event])
def get_events(skip: int = 0, limit: int = 50, q: str = None, db: Session = Depends(get_db)):
    """Fetch recent events with optional search query."""
    query = db.query(EventModel)
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            (EventModel.object_type.ilike(search_term)) |
            (EventModel.event_type.ilike(search_term)) |
            (EventModel.plate_number.ilike(search_term)) |
            (EventModel.source_id.ilike(search_term))
        )
    events = query.order_by(EventModel.timestamp.desc()).offset(skip).limit(limit).all()
    return events

@router.get("/stats", response_model=Stats)
def get_stats(db: Session = Depends(get_db)):
    """Fetch dashboard statistics."""
    total = db.query(func.count(EventModel.id)).scalar() or 0
    persons = db.query(func.count(EventModel.id)).filter(EventModel.object_type.like('%person%')).scalar() or 0
    vehicles = db.query(func.count(EventModel.id)).filter(EventModel.object_type == 'vehicle').scalar() or 0
    incidents = db.query(func.count(EventModel.id)).filter(EventModel.event_type.like('INCIDENT%')).scalar() or 0
    
    return Stats(
        total_events=total,
        total_persons=persons,
        total_vehicles=vehicles,
        total_incidents=incidents
    )
