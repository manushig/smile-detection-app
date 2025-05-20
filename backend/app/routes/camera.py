"""
Camera API Endpoints.
Provides endpoints to start/stop camera and detect smiles in real-time video frames.
"""

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from app.services.camera_manager import camera_manager
from app.services.smile_detector import detect_smile_on_frame
from app.models.detection_event import log_detection_event, save_detection_image
import logging
import json

router = APIRouter()

@router.post("/start_camera", tags=["Camera"])
def start_camera():
    """
    Endpoint to start the webcam for smile detection.
    Returns:
        200 OK if started, 409 Conflict if already running, 500 on error.
    """
    try:
        result = camera_manager.start()
        if result:
            return {"status": "Camera started"}
        elif camera_manager.is_running():
            return JSONResponse(status_code=409, content={"error": "Camera already running"})
        else:
            return JSONResponse(status_code=500, content={"error": "Failed to start camera"})
    except Exception:
        logging.exception("[Camera] Exception in /start_camera")
        return JSONResponse(status_code=500, content={"error": "Unexpected error while starting camera"})

@router.post("/stop_camera", tags=["Camera"])
def stop_camera():
    """
    Endpoint to stop the webcam and release resources.
    Returns:
        200 OK if stopped, 409 Conflict if already stopped.
    """
    try:
        result = camera_manager.stop()
        if result:
            return {"status": "Camera stopped"}
        else:
            return JSONResponse(status_code=409, content={"error": "Camera already stopped"})
    except Exception:
        logging.exception("[Camera] Exception in /stop_camera")
        return JSONResponse(status_code=500, content={"error": "Unexpected error while stopping camera"})

@router.get("/detect_smile", tags=["Detection"])
def detect_smile():
    """
    Endpoint to detect smile in the current camera frame.
    Returns:
        - 200: JPEG image with smile coordinates in headers (if detected)
        - 204: No Content if no smile detected or no frame available
        - 409: Error if camera is not started
        - 500: Internal server error on failure
    """
    try:
        if not camera_manager.is_running():
            return JSONResponse(status_code=409, content={"error": "Camera not started"})
        frame = camera_manager.get_frame()
        if frame is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        result = detect_smile_on_frame(frame)
        if result is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        image_bytes, coords = result
        log_detection_event(coords)
        save_detection_image(image_bytes)
        return Response(
            content=image_bytes,
            media_type="image/jpeg",
            headers={"X-Smile-Coords": json.dumps(coords)}
        )
    except Exception:
        logging.exception("[Camera] Exception in /detect_smile")
        return JSONResponse(status_code=500, content={"error": "Unexpected error during detection"})
