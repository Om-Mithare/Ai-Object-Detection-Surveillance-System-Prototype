from app.database.database import SessionLocal
from app.models.models import Event
from datetime import datetime, timedelta
import random

db = SessionLocal()

object_types = ['person', 'vehicle', 'bicycle', 'motorcycle']
event_types = ['DETECTION', 'INCIDENT_LOITERING', 'INCIDENT_SPEEDING']
plates = ['ABC-1234', 'XYZ-9999', 'HACK-2026', None, None, None]

# Generate 20 realistic events over the last 10 minutes
now = datetime.utcnow()
for i in range(20):
    event = Event(
        timestamp=now - timedelta(seconds=random.randint(1, 600)),
        object_type=random.choice(object_types),
        confidence=random.uniform(0.65, 0.99),
        event_type=random.choice(event_types) if random.random() > 0.7 else 'DETECTION',
        plate_number=random.choice(plates) if random.random() > 0.8 else None,
        source_id="demo_video.mp4"
    )
    db.add(event)

db.commit()
db.close()
print("Seeded database with demo data!")
