"""
API route tests for camera endpoints.
Mocks CameraManager and dependencies to isolate API logic.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

# ----------- Start Camera Tests ------------

def test_start_camera_success():
    """
    Ensures /start_camera returns 200 OK when the camera starts successfully.
    """
    with patch("app.routes.camera.camera_manager.start", return_value=True):
        response = client.post("/start_camera")
        assert response.status_code == 200
        assert "Camera started" in response.json()["status"]

def test_start_camera_already_running():
    """
    Ensures /start_camera returns 409 when camera is already running.
    """
    with patch("app.routes.camera.camera_manager.start", return_value=False), \
         patch("app.routes.camera.camera_manager.is_running", return_value=True):
        response = client.post("/start_camera")
        assert response.status_code == 409

def test_start_camera_failure():
    """
    Ensures /start_camera returns 500 if camera fails to start.
    """
    with patch("app.routes.camera.camera_manager.start", return_value=False), \
         patch("app.routes.camera.camera_manager.is_running", return_value=False):
        response = client.post("/start_camera")
        assert response.status_code == 500

def test_start_camera_exception():
    """
    Ensures /start_camera returns 500 if an exception is raised.
    """
    with patch("app.routes.camera.camera_manager.start", side_effect=Exception("fail")):
        response = client.post("/start_camera")
        assert response.status_code == 500

# ----------- Stop Camera Tests ------------

def test_stop_camera_success():
    """
    Ensures /stop_camera returns 200 OK when the camera stops successfully.
    """
    with patch("app.routes.camera.camera_manager.stop", return_value=True):
        response = client.post("/stop_camera")
        assert response.status_code == 200
        assert "Camera stopped" in response.json()["status"]

def test_stop_camera_already_stopped():
    """
    Ensures /stop_camera returns 409 when camera is already stopped.
    """
    with patch("app.routes.camera.camera_manager.stop", return_value=False):
        response = client.post("/stop_camera")
        assert response.status_code == 409

def test_stop_camera_exception():
    """
    Ensures /stop_camera returns 500 if an exception is raised.
    """
    with patch("app.routes.camera.camera_manager.stop", side_effect=Exception("fail")):
        response = client.post("/stop_camera")
        assert response.status_code == 500

# ----------- Detect Smile Tests ------------

def test_detect_smile_camera_not_started():
    """
    Ensures /detect_smile returns 409 if camera is not running.
    """
    with patch("app.routes.camera.camera_manager.is_running", return_value=False):
        response = client.get("/detect_smile")
        assert response.status_code == 409

def test_detect_smile_no_frame():
    """
    Ensures /detect_smile returns 204 if no frame is available from the camera.
    """
    with patch("app.routes.camera.camera_manager.is_running", return_value=True), \
         patch("app.routes.camera.camera_manager.get_frame", return_value=None):
        response = client.get("/detect_smile")
        assert response.status_code == 204

def test_detect_smile_no_smile_detected():
    """
    Ensures /detect_smile returns 204 if no smile is detected in the frame.
    """
    with patch("app.routes.camera.camera_manager.is_running", return_value=True), \
         patch("app.routes.camera.camera_manager.get_frame", return_value="frame"), \
         patch("app.routes.camera.detect_smile_on_frame", return_value=None):
        response = client.get("/detect_smile")
        assert response.status_code == 204

def test_detect_smile_success():
    """
    Ensures /detect_smile returns 200 OK and correct headers when a smile is detected.
    """
    fake_img_bytes = b"\xff\xd8\xff"
    fake_coords = [{"x": 1, "y": 2, "w": 3, "h": 4}]
    with patch("app.routes.camera.camera_manager.is_running", return_value=True), \
         patch("app.routes.camera.camera_manager.get_frame", return_value="frame"), \
         patch("app.routes.camera.detect_smile_on_frame", return_value=(fake_img_bytes, fake_coords)):
        response = client.get("/detect_smile")
        assert response.status_code == 200
        assert response.content == fake_img_bytes
        assert response.headers.get("x-smile-coords") is not None

def test_detect_smile_exception():
    """
    Ensures /detect_smile returns 500 if an exception is raised during detection.
    """
    with patch("app.routes.camera.camera_manager.is_running", return_value=True), \
         patch("app.routes.camera.camera_manager.get_frame", side_effect=Exception("fail")):
        response = client.get("/detect_smile")
        assert response.status_code == 500

def test_detect_smile_success_logs_and_saves(monkeypatch):
    """
    Ensures /detect_smile calls log_detection_event and save_detection_image when smile is detected.
    """
    fake_img_bytes = b"\xff\xd8\xff"
    fake_coords = [{"x": 1, "y": 2, "w": 3, "h": 4}]
    called = {"log": False, "save": False}

    def fake_log(coords):
        called["log"] = True
        assert coords == fake_coords

    def fake_save(img):
        called["save"] = True
        assert img == fake_img_bytes
        return "/tmp/fake.jpg"

    with patch("app.routes.camera.camera_manager.is_running", return_value=True), \
         patch("app.routes.camera.camera_manager.get_frame", return_value="frame"), \
         patch("app.routes.camera.detect_smile_on_frame", return_value=(fake_img_bytes, fake_coords)), \
         patch("app.routes.camera.log_detection_event", fake_log), \
         patch("app.routes.camera.save_detection_image", fake_save):
        response = client.get("/detect_smile")
        assert response.status_code == 200
        assert response.content == fake_img_bytes
        assert response.headers.get("x-smile-coords") is not None
        assert called["log"] is True
        assert called["save"] is True
