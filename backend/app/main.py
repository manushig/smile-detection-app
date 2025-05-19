from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import detect
from app.logger import setup_logger
# Initialize logging once on app startup
setup_logger()

# Initialize the FastAPI app
app = FastAPI(
    title="Smile Detection API",
    description="RESTful API for real-time smile detection using webcam images. Supports both OpenCV Haar cascades and Dlib facial landmarks.",
    version="1.0.0"
)

# CORS settings - allow React frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-smile-coords"], 
)

# Root health check endpoint
@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint for Smile Detection API.

    Returns:
        dict: Status message confirming the API is online.
    """
    return {"message": "Smile Detection API is running."}

# Attach detection endpoints (both OpenCV and Dlib) to the main app
app.include_router(detect.router)