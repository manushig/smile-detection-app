# File: backend/app/routes/detect.py

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from app.services.smile_detector import detect_smile_and_save
from app.models.detection_event import log_detection_event
import logging

router = APIRouter()

@router.get("/detect", tags=["Detection"])
def detect_smile():
    """
    Captures an image from the webcam, detects smiles using OpenCV,
    returns the image with smile bounding boxes, and logs coordinates.
    """
    try:
        result = detect_smile_and_save()
        if result is None:
            return JSONResponse(content={"smile_detected": False}, status_code=status.HTTP_204_NO_CONTENT)

        image_bytes, coords = result
        log_detection_event(coords)
        return Response(content=image_bytes, media_type="image/jpeg", headers={"X-Smile-Coords": str(coords)})
    except Exception as e:
        logging.exception("Error during smile detection")
        return JSONResponse(content={"error": "Smile detection failed."}, status_code=500)