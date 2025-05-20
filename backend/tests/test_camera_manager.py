"""
Unit tests for CameraManager singleton logic.
Mocks cv2.VideoCapture and threading as needed.
"""

import pytest
import threading
from app.services.camera_manager import CameraManager

def test_start_and_stop(monkeypatch):
    """
    Tests that starting the camera sets running to True, and stopping resets it.
    Mocks cv2.VideoCapture and simulates a normal start/stop cycle.
    """
    class DummyCap:
        def isOpened(self): return True
        def read(self): return (True, "dummy_frame")
        def release(self): pass

    cm = CameraManager()
    # Patch cv2.VideoCapture to use DummyCap
    monkeypatch.setattr("cv2.VideoCapture", lambda *_: DummyCap())
    assert cm.start() == True
    assert cm.is_running() is True
    assert cm.stop() == True
    assert cm.is_running() is False

def test_start_already_running(monkeypatch):
    """
    Tests that calling start() when already running returns False and does not restart the camera.
    """
    class DummyCap:
        def isOpened(self): return True
        def read(self): return (True, "frame")
        def release(self): pass
    cm = CameraManager()
    monkeypatch.setattr("cv2.VideoCapture", lambda *_: DummyCap())
    assert cm.start() == True
    assert cm.start() == False  # Should not allow start again

def test_stop_already_stopped():
    """
    Tests that calling stop() when camera is not running returns False.
    """
    cm = CameraManager()
    assert cm.stop() == False

def test_capture_loop_handles_failed_read(monkeypatch):
    """
    Tests that _capture_loop sets _frame to None and continues if frame read fails.
    """
    class DummyCap:
        def isOpened(self): return True
        def read(self): return (False, None)  # Simulate read failure
        def release(self): pass

    cm = CameraManager()
    cm._cap = DummyCap()
    cm._running = True

    # Patch time.sleep to avoid delays
    monkeypatch.setattr("time.sleep", lambda _: None)
    # Force only one loop iteration by toggling _running off in read()
    def fake_read():
        cm._running = False
        return (False, None)
    cm._cap.read = fake_read

    cm._capture_loop()
    assert cm._frame is None

def test_capture_loop_logs_failed_read(monkeypatch, caplog):
    """
    Tests that _capture_loop logs a warning when frame read fails.
    Ensures coverage for logging.warning call in _capture_loop.
    """
    class DummyCap:
        def isOpened(self): return True
        def read(self): return (False, None)
        def release(self): pass

    cm = CameraManager()
    cm._cap = DummyCap()
    cm._running = True

    monkeypatch.setattr("time.sleep", lambda _: None)
    def fake_read():
        cm._running = False
        return (False, None)
    cm._cap.read = fake_read

    with caplog.at_level("WARNING"):
        cm._capture_loop()
        assert any("Failed to read frame from webcam." in m for m in caplog.messages)
    assert cm._frame is None

def test_get_frame_returns_none_when_no_frame():
    """
    Tests that get_frame returns None when no frame is available.
    """
    cm = CameraManager()
    cm._frame = None
    assert cm.get_frame() is None

def test_is_running_returns_false():
    """
    Tests that is_running returns False when camera is not running.
    """
    cm = CameraManager()
    cm._running = False
    assert cm.is_running() is False

def test_get_frame_returns_copy_when_frame_exists():
    """
    Tests that get_frame returns a (shallow) copy of the frame if available.
    """
    cm = CameraManager()
    dummy_frame = [1, 2, 3]
    cm._frame = dummy_frame
    result = cm.get_frame()
    assert result == dummy_frame
    assert result is not dummy_frame  # Ensure a copy is returned
