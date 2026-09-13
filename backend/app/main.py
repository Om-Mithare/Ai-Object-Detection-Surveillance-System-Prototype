from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base
from app.api.endpoints import router as api_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intelligent Surveillance System API",
    description="API for object detection, event tracking, and incident flagging",
    version="1.0.0"
)

# CORS configuration to allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Must be False if allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Surveillance API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
