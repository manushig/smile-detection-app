from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Smile Detection API is running."}

def test_detect_camera_unavailable(monkeypatch):
    from app.services import smile_detector

    def mock_video_capture_failure():
        return None

    monkeypatch.setattr(smile_detector, "detect_smile_and_save", mock_video_capture_failure)
    response = client.get("/detect")
    assert response.status_code == 204
    assert response.json() == {"smile_detected": False}

def test_detect_internal_error(monkeypatch):
    from app.services import smile_detector

    def raise_exception():
        raise RuntimeError("Mock error")

    monkeypatch.setattr(smile_detector, "detect_smile_and_save", raise_exception)
    response = client.get("/detect")
    assert response.status_code == 500
    assert response.json() == {"error": "Smile detection failed."}

