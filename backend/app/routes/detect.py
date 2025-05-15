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
    returns the image with smile bounding boxes (as JPEG bytes),
    logs the coordinates of detected smiles, and handles errors gracefully.

    Returns:
        - 200 OK: Image with smile bounding box and header with coordinates
        - 204 No Content: If no smile is detected
        - 500 Internal Server Error: If any unexpected error occurs
    """
    try:
        # Run smile detection service
        result = detect_smile_and_save()

        # Guard clause: no smile detected or capture failed
        if result is None:
            return JSONResponse(content={"smile_detected": False}, status_code=status.HTTP_204_NO_CONTENT)

        image_bytes, coords = result

        # Log detection event to the database
        log_detection_event(coords)

        # Return image with smile detection and metadata in header
        return Response(
            content=image_bytes,
            media_type="image/jpeg",
            headers={"X-Smile-Coords": str(coords)}
        )

    except Exception as e:
        # Log the error to app.log and console
        logging.exception("Error during smile detection")
        return JSONResponse(content={"error": "Smile detection failed."}, status_code=500)