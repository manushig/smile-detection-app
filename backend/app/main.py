"""
Smile Detection API - FastAPI entry point.
Integrates camera/session-based smile detection endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import camera  # Use new camera-based routes
from app.logger import setup_logger
from app.services.camera_manager import camera_manager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize logging once on app startup
setup_logger()

# Initialize the FastAPI app
app = FastAPI(
    title="Smile Detection API",
    description="RESTful API for real-time smile detection using webcam images. Supports OpenCV-based detection with session camera.",
    version="1.0.0"
)

# CORS settings - allow React frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-smile-coords"],
)

# Health check endpoint
@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint for Smile Detection API.
    Returns:
        dict: Status message confirming the API is online.
    """
    return {"message": "Smile Detection API is running."}

# Attach new camera-based detection endpoints
app.include_router(camera.router)

# Ensure camera is stopped on server shutdown
@app.on_event("shutdown")
def shutdown_event():
    camera_manager.stop()
