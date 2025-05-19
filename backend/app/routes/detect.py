from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from app.services.smile_detector import detect_smile_and_save as opencv_detect
from app.services.dlib_smile_detector import detect_smile_and_save as dlib_detect
from app.models.detection_event import log_detection_event
import logging
import json

router = APIRouter()

def handle_detection(detect_fn, method_name="OpenCV"):
    """
    Helper function to handle smile detection workflow.
    Args:
        detect_fn (callable): The backend smile detection function.
        method_name (str): Label for logging and error messages.
    Returns:
        FastAPI Response: JPEG image and coordinates if smile detected,
                         204 No Content if not detected,
                         500 Internal Server Error on failure.
    """
    try:
        # Run the selected detection algorithm
        result = detect_fn()

        # Guard clause: no smile detected or capture failed
        if result is None:
            logging.info(f"[{method_name}] No smile detected or capture failed. Returning 204.")
            # Return *empty* 204 No Content response
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        image_bytes, coords = result

        logging.info(f"[{method_name}] Smile detected: {coords}")
        
        # Log the smile coordinates to the database
        log_detection_event(coords)

        # Return image with smile detection and coordinates as response header
        return Response(
            content=image_bytes,
            media_type="image/jpeg",            
            headers={"X-Smile-Coords": json.dumps(coords)}
        )
    except Exception:
        logging.exception(f"[{method_name}] Error during smile detection")
        # Only for error (not 204!) send JSON error body
        return JSONResponse(
            content={"error": f"{method_name} smile detection failed."},
            status_code=500
        )

@router.get(
    "/detect/opencv",
    tags=["Detection"],
    summary="Smile Detection (OpenCV Haar Cascade)",
    description="""
Detects smiles in a webcam image using OpenCV's Haar cascade classifier.

**Returns:**
- JPEG image with detected smile bounding box (200 OK)
- 204 No Content if no smile detected
- 500 Internal Server Error on failure

**Response headers:**
- `X-Smile-Coords`: JSON string of bounding box coordinates for detected smiles.
""",
    responses={
        200: {"description": "Smile detected. JPEG image returned with bounding box."},
        204: {"description": "No smile detected or camera not available."},
        500: {"description": "Internal server error."},
    }
)
def detect_smile_opencv():
    """
    Endpoint for smile detection using OpenCV Haar cascades.
    """
    logging.info("[OpenCV] /detect/opencv endpoint called.")
    return handle_detection(opencv_detect, "OpenCV")

@router.get(
    "/detect/dlib",
    tags=["Detection"],
    summary="Smile Detection (Dlib Landmarks)",
    description="""
Detects smiles using Dlib's 68-point facial landmarks.

**Returns:**
- JPEG image with detected mouth bounding box (200 OK)
- 204 No Content if no smile detected
- 500 Internal Server Error on failure

**Response headers:**
- `X-Smile-Coords`: JSON string of mouth region coordinates if a smile is detected.
""",
    responses={
        200: {"description": "Smile detected. JPEG image returned with bounding box."},
        204: {"description": "No smile detected or camera not available."},
        500: {"description": "Internal server error."},
    }
)
def detect_smile_dlib():
    """
    Endpoint for smile detection using Dlib facial landmarks.
    """
    logging.info("[Dlib] /detect/dlib endpoint called.")
    return handle_detection(dlib_detect, "Dlib")
