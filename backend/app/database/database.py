import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# We default to SQLite for the MVP to ensure easy hackathon setup.
# This URL can be changed to postgresql://user:password@localhost/dbname later
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hackathon_surveillance.db")

# connect_args={"check_same_thread": False} is only needed for SQLite
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
