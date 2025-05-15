# Smile Detection App

A full-stack application with:

- **Frontend**: React (live webcam + smile detection)
- **Backend**: FastAPI + OpenCV (detects smiles)
- **Database**: SQLite for detection logs
- **Docker**: Dockerized backend and frontend

## Setup Instructions

### Local Development

```bash
# Terminal 1 - Backend
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm start
```
