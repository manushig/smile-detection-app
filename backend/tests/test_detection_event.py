"""
Unit tests for detection event logging and image saving.
Covers table creation, error handling, and file persistence.
"""

import sqlite3
import os
import pytest
from app.models.detection_event import log_detection_event, save_detection_image

def test_log_detection_event_creates_table_and_inserts(tmp_path):
    """
    Ensures log_detection_event creates table and inserts detection data in a temp SQLite DB.
    """
    db_path = tmp_path / "test_smiles.db"
    coords = [{"x": 1, "y": 2, "w": 3, "h": 4}]
    log_detection_event(coords, db_path=str(db_path))

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detections")
    rows = cursor.fetchall()
    assert len(rows) == 1
    # Check coords column matches what we inserted
    assert coords == eval(rows[0][2]) or coords == __import__('json').loads(rows[0][2])
    conn.close()

def test_log_detection_event_empty_coords(tmp_path):
    """
    Ensures log_detection_event handles empty coords gracefully (still inserts row).
    """
    db_path = tmp_path / "empty_smiles.db"
    log_detection_event([], db_path=str(db_path))
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detections")
    rows = cursor.fetchall()
    assert len(rows) == 1
    conn.close()

def test_log_detection_event_db_error(monkeypatch, tmp_path):
    """
    Ensures log_detection_event handles DB connection errors gracefully.
    """
    def fail_connect(*args, **kwargs):
        raise sqlite3.OperationalError("test error")
    monkeypatch.setattr(sqlite3, "connect", fail_connect)
    # Should not raise, but log the error
    log_detection_event([{"x": 1}], db_path=str(tmp_path / "bad.db"))

def test_save_detection_image_creates_file(tmp_path):
    """
    Ensures save_detection_image writes image bytes to a file and returns file path.
    """
    # Patch the target directory
    test_dir = tmp_path / "detected_smiles"
    os.makedirs(test_dir, exist_ok=True)
    image_bytes = b"\x00\x01\x02\x03"
    # Patch os.path.join to write to the test directory
    from app.models import detection_event
    old_join = detection_event.os.path.join
    detection_event.os.path.join = lambda a, b: str(test_dir / b)
    try:
        result = save_detection_image(image_bytes)
        assert os.path.exists(result)
        with open(result, "rb") as f:
            assert f.read() == image_bytes
    finally:
        detection_event.os.path.join = old_join

def test_save_detection_image_handles_failure(monkeypatch):
    """
    Ensures save_detection_image returns None if file cannot be written (simulates OSError).
    """
    # Patch open to raise an OSError
    monkeypatch.setattr("builtins.open", lambda *a, **kw: (_ for _ in ()).throw(OSError("fail")))
    path = save_detection_image(b"abc")
    assert path is None
