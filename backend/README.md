# Smile Detection Backend

A lightweight FastAPI backend service that captures images from a webcam, detects smiles using OpenCV, and returns an image with a smile bounding box. Detection events are logged to a local SQLite database.

---

## 🚀 Features

- RESTful API built with FastAPI
- Smile detection using OpenCV Haar cascades
- Returns JPEG image with bounding box overlay
- Centralized logging to console and `app.log`
- SQLite persistence for detection coordinates
- Unit tests using Pytest

---

## 📦 Setup Instructions

### ✅ Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- A device with a webcam

### 📁 Installation

```bash
cd backend
poetry install
```

### ▶️ Run Locally

```bash
# Start the FastAPI server using Poetry
poetry run uvicorn app.main:app --reload
```

---

## 🌐 API Endpoints

- **Health Check**: `GET /`
  → Returns service status

- **Smile Detection**: `GET /detect`
  → Captures webcam frame, detects smile, returns image
  → `204` if no smile is detected
  → `500` on error

- **Docs**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

---

## 📸 How It Works

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

## ⚙️ Tech Stack

- **Framework**: FastAPI, Python 3.10
- **CV**: OpenCV, Pillow
- **Data**: SQLite
- **Logging**: Python `logging`
- **Testing**: Pytest, FastAPI TestClient

---

## 🧾 Notes for Reviewers

- Haar cascade files are bundled with OpenCV (no extra setup needed).
- Smile detection may return `204` if no smile is visible.
- All logs are stored in `backend/app.log`.

---

## 👩‍💻 Author

**Manushi**
[GitHub](https://github.com/manushig) | [LinkedIn](https://linkedin.com/in/manushi-g)
