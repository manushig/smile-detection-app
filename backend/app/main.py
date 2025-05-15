# File: backend/app/main.py

from fastapi import FastAPI
from app.routes import detect
from app.logger import setup_logger

# Initialize logging once on app startup
setup_logger()

# Initialize the FastAPI app
app = FastAPI(
    title="Smile Detection API",
    description="Captures an image, detects a smile, and returns the image with bounding box and smile coordinates.",
    version="1.0.0"
)

# Root health check endpoint
@app.get("/", tags=["Health"])
def root():
    return {"message": "Smile Detection API is running."}

# Include the detection route
app.include_router(detect.router)