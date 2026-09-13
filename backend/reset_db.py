from app.database.database import SessionLocal
from app.models.models import Event

db = SessionLocal()
db.query(Event).delete()
db.commit()
db.close()
print("Database cleared successfully!")
