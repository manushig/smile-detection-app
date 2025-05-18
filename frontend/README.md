# Smile Detection Frontend

A React-based user interface for real-time smile detection.  
Connects to a Python backend (REST API) for image analysis and shows results live.

---

## Features

- **Start/Stop Smile Detection**: Simple interface for initiating or stopping detection.
- **Model Selection**: Switch between multiple backend detection models (OpenCV, Dlib).
- **Live Image Display**: See the latest frame with bounding boxes for detected smiles.
- **Smile Coordinates**: View detailed coordinates of detected smile regions.
- **Robust Error Handling**: User-friendly messages for errors or connectivity issues.
- **Extensive Unit Tests**: >90% test coverage with Jest and React Testing Library.

---

## Setup Instructions

### 1. Prerequisites

- Node.js (v18+ recommended)
- npm (v9+ recommended)

### 2. Installation

```bash
cd frontend
npm install
```

### 3. Configure API Endpoint

Create a `.env` file in the `/frontend` directory to set the backend API URL:

```
REACT_APP_API_URL=http://localhost:8000
```

> By default, it falls back to `http://localhost:8000` if not set.

### 4. Run Locally

```bash
npm start
```

App runs at [http://localhost:3000](http://localhost:3000).

---

## Testing

### Run All Tests

```bash
npm test
```

### View Coverage Report

```bash
npx react-scripts test --coverage --watchAll=false
```

Coverage report is saved in `frontend/coverage/` (open `index.html` for a visual report).

---

## Tech Stack

- [React](https://reactjs.org/) (v18+)
- [Axios](https://axios-http.com/) for backend API calls
- [Jest](https://jestjs.io/) & [React Testing Library](https://testing-library.com/) for testing
- [CSS Modules](https://css-tricks.com/css-modules-part-1-need/) (or plain CSS)

---

## 👩‍💻 Author

**Manushi**
[GitHub](https://github.com/manushig) | [LinkedIn](https://linkedin.com/in/manushi-g)
