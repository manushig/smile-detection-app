"""
Unit tests for detect_smile_on_frame in smile_detector service.
Mocks OpenCV cascades and imencode to test smile detection logic.
"""

import numpy as np
from unittest.mock import MagicMock
from app.services.smile_detector import detect_smile_on_frame

def test_no_frame_returns_none():
    """
    Ensures detect_smile_on_frame returns None if frame is None.
    """
    assert detect_smile_on_frame(None) is None

def test_blank_image_no_face():
    """
    Ensures detect_smile_on_frame returns None for a blank image with no faces.
    """
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    assert detect_smile_on_frame(frame) is None

def test_no_faces_with_injected_cascade():
    """
    Ensures detect_smile_on_frame returns None if no faces are detected (mocked cascade).
    """
    fake_face_cascade = MagicMock()
    fake_face_cascade.detectMultiScale.return_value = []
    fake_smile_cascade = MagicMock()
    fake_smile_cascade.detectMultiScale.return_value = []

    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = detect_smile_on_frame(frame, face_cascade=fake_face_cascade, smile_cascade=fake_smile_cascade)
    assert result is None

def test_face_no_smile_with_injected_cascade():
    """
    Ensures detect_smile_on_frame returns None if a face is detected but no smiles are found.
    """
    fake_face_cascade = MagicMock()
    fake_face_cascade.detectMultiScale.return_value = [(10, 10, 80, 80)]
    fake_smile_cascade = MagicMock()
    fake_smile_cascade.detectMultiScale.return_value = []

    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = detect_smile_on_frame(frame, face_cascade=fake_face_cascade, smile_cascade=fake_smile_cascade)
    assert result is None

def test_smile_detected_best_box_and_encoding_success(monkeypatch):
    """
    Ensures detect_smile_on_frame returns encoded image bytes and coords for best smile box.
    """
    fake_face_cascade = MagicMock()
    fake_face_cascade.detectMultiScale.return_value = [(10, 10, 80, 80)]
    fake_smile_cascade = MagicMock()
    # Two smile candidates; one is best by area
    fake_smile_cascade.detectMultiScale.return_value = [(20, 60, 50, 20), (30, 50, 40, 22)]
    def fake_imencode(fmt, img):
        return True, np.array([1, 2, 3])

    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = detect_smile_on_frame(
        frame,
        face_cascade=fake_face_cascade,
        smile_cascade=fake_smile_cascade,
        imencode_func=fake_imencode
    )
    assert result is not None
    img_bytes, coords = result
    assert isinstance(img_bytes, (bytes, np.ndarray))
    assert isinstance(coords, list)
    assert "x" in coords[0]

def test_smile_detected_encoding_failure(monkeypatch):
    """
    Ensures detect_smile_on_frame returns None if image encoding fails.
    """
    fake_face_cascade = MagicMock()
    fake_face_cascade.detectMultiScale.return_value = [(10, 10, 80, 80)]
    fake_smile_cascade = MagicMock()
    fake_smile_cascade.detectMultiScale.return_value = [(20, 60, 50, 20)]
    def fake_imencode(fmt, img):
        return False, None  # Simulate encoding failure

    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = detect_smile_on_frame(
        frame,
        face_cascade=fake_face_cascade,
        smile_cascade=fake_smile_cascade,
        imencode_func=fake_imencode
    )
    assert result is None

def test_smile_filtered_by_aspect_and_center(monkeypatch):
    """
    Ensures detect_smile_on_frame ignores smiles not meeting aspect ratio and center conditions.
    """
    fake_face_cascade = MagicMock()
    fake_face_cascade.detectMultiScale.return_value = [(10, 10, 80, 80)]
    fake_smile_cascade = MagicMock()
    # Smile candidate fails aspect ratio and center threshold
    fake_smile_cascade.detectMultiScale.return_value = [(10, 10, 20, 30)]  # aspect_ratio = 0.66
    def fake_imencode(fmt, img):
        return True, np.array([1, 2, 3])
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = detect_smile_on_frame(
        frame,
        face_cascade=fake_face_cascade,
        smile_cascade=fake_smile_cascade,
        imencode_func=fake_imencode
    )
    assert result is None
