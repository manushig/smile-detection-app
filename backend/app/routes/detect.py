# File: backend/app/routes/detect.py

from fastapi import APIRouter, Response
from app.services.smile_detector import detect_smile_and_save
from app.models.detection_event import log_detection_event

router = APIRouter()

@router.get("/detect", tags=["Detection"])
def detect_smile():
    """
    Captures an image from the webcam, detects smiles using OpenCV,
    returns the image with smile bounding boxes, and logs coordinates.
    """
    result = detect_smile_and_save()
    if result is None:
        return {"smile_detected": False}

    image_bytes, coords = result
    log_detection_event(coords)
    return Response(content=image_bytes, media_type="image/jpeg", headers={"X-Smile-Coords": str(coords)})