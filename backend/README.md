# Smile Detection Backend

A lightweight FastAPI backend service that captures images from a webcam, detects smiles using OpenCV, and returns an image with a smile bounding box. Detection events are logged to a local SQLite database.

---

## Features

- RESTful API built with FastAPI
- Smile detection using OpenCV Haar cascades
- Returns JPEG image with bounding box overlay
- Centralized logging to console and `app.log`
- SQLite persistence for detection coordinates
- Unit tests using Pytest

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- A device with a webcam

### Installation

```bash
cd backend
poetry install
```

### ▶️ Run Locally

```bash
poetry run uvicorn app.main:app --reload
```

---

## API Endpoints

- **Health Check**: `GET /`
  Returns service status

- **Smile Detection**: `GET /detect`
  Captures webcam frame, detects smile, returns image
  Returns `204` if no smile is detected, `500` on error

- **Docs**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

---

## How It Works

1. `/detect` captures a webcam image.
2. Uses Haar cascades to detect face and smiles.
3. If a smile is found:

   - Rectangle is drawn
   - Image returned as `image/jpeg`
   - Coordinates logged to `smiles.db`

4. Logs are saved in real-time to `app.log` and terminal.

---

## 🧪 Run Tests

```bash
poetry run pytest
```

**Tests cover:**

- Health check (`GET /`)
- Smile detection with no result (mocked)
- Internal error (mocked exception)

---

## Tech Stack

- **Framework**: FastAPI, Python 3.10
- **CV**: OpenCV, Pillow
- **Data**: SQLite
- **Logging**: Python `logging`
- **Testing**: Pytest, FastAPI TestClient

---

## Notes for Reviewers

- Haar cascade files are bundled with OpenCV (no extra setup needed).
- Smile detection may return `204` if no smile is visible.
- All logs are stored in `backend/app.log`.

---

## Smile Detection Limitations & Known Issues

### Why Haar Cascade Smile Detection Is Inaccurate

This project uses OpenCV’s classic [Haar cascade](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html) for smile detection, which is fast and requires no training. However, it is well-known in the vision community for the following limitations:

- **Sensitive to Lighting and Angle:** Webcam overexposure, shadows, and head tilt can confuse the detector.
- **Easily Fooled by Non-Smile Patterns:** Glasses, mustaches, and even nostrils can be misidentified as smiles.
- **Bounding Box Misplacement:** The detected region may drift above or below the lips, especially in complex lighting or with accessories.
- **False Positives and Negatives:** Not all smiles are detected; some neutral mouths or unrelated areas may trigger “smile” boxes.

**References:**

- [OpenCV docs: Cascade Classifier](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html)
- [StackOverflow: Haarcascade smile detection accuracy](https://stackoverflow.com/questions/49966201/haarcascade-smile-detection-accuracy)

---

### Filtering and Post-Processing Strategies Used

To improve detection accuracy, I applied several post-processing filters:

- **Aspect Ratio Filter:** Only consider boxes where `width/height > 1.8`
- **Location Filter:** Only accept boxes with center below 60% of the face height (`center_y > y + 0.6*h`)
- **Largest Box Only:** When multiple “smiles” are found, only the largest region is considered

```python
aspect_ratio = sw / float(sh)
smile_center_y = y + sy + sh // 2
face_lower_threshold = y + int(0.6 * h)
if aspect_ratio > 1.8 and smile_center_y > face_lower_threshold:
    # Accept this smile box
```

---

### Example Images: **Correct vs. Incorrect Detections**

A sample set of test outputs is included in [`/backend/example_images`](./example_images/), showing:

- **Correct detections:** Smile bounding box matches mouth
- **Incorrect detections:** Box is off-center, or triggered by glasses/nose

---

### Recommended Modern Alternatives

For production-grade, real-world smile detection, consider:

- **MediaPipe Face Landmarker** ([Google, Official Docs](https://developers.google.com/mediapipe/solutions/vision/face_landmarker)): Accurate mouth landmarks for robust smile classification
- **Dlib’s facial landmarks** ([Dlib documentation](http://dlib.net/face_landmark_detection.py.html)): Widely used in Python for facial analysis
- **Deep Learning Models:** Custom CNNs or solutions trained for emotion/smile recognition

---

## Author

**Manushi**
[GitHub](https://github.com/manushig) | [LinkedIn](https://linkedin.com/in/manushi-g)

```

```
