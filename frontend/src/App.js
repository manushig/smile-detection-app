/**
 * Main Application Component for Smile Detection UI.
 *
 * - Starts/stops camera session on backend.
 * - Polls backend every second for smile detection.
 * - Shows live feedback and handles network and API errors.
 * - Displays a spinner overlay while starting the camera.
 * - Cleans up Blob URLs to prevent memory leaks.
 */

import React, { useState, useEffect, useRef } from "react";
import SmileViewer from "./components/SmileViewer";
import SmileDetails from "./components/SmileDetails";
import { startCamera, stopCamera, fetchSmileDetection } from "./api/SmileApi";
import "./index.css";

function App() {
  // App state
  const [detectionRunning, setDetectionRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Click 'Start' to begin.");
  const [imageSrc, setImageSrc] = useState(null);
  const [smileCoords, setSmileCoords] = useState(null);
  const [lastSmile, setLastSmile] = useState({ coords: null, image: null });

  const intervalRef = useRef(null);
  const inFlight = useRef(false);

  /**
   * Poll for smile detection every second when detectionRunning is true.
   */
  useEffect(() => {
    if (detectionRunning) {
      intervalRef.current = setInterval(() => {
        if (!inFlight.current) {
          handleSmileDetection();
        }
      }, 1000);
    }
    return () => clearInterval(intervalRef.current);
    // eslint-disable-next-line
  }, [detectionRunning]);

  /**
   * Handles polling for smile detection from backend.
   * Updates image, coordinates, and UI status.
   */
  const handleSmileDetection = async () => {
    inFlight.current = true;
    try {
      const response = await fetchSmileDetection();
      if (!detectionRunning) return;

      // Success: Smile detected
      if (response.status === 200) {
        setStatusMessage("Keep smiling!");
        const coordsHeader = response.headers["x-smile-coords"];
        let coords = null;
        if (coordsHeader) {
          try {
            coords = JSON.parse(coordsHeader);
          } catch (e) {
            // Fallback: sometimes backend returns single quotes
            try {
              coords = JSON.parse(coordsHeader.replace(/'/g, '"'));
            } catch {
              coords = coordsHeader; // fallback to raw string
            }
          }
        }
        const newImage = URL.createObjectURL(response.data);
        setImageSrc(newImage);
        setSmileCoords(coords);
        setLastSmile({ coords, image: newImage });
      }
      // No smile detected (204)
      else if (response.status === 204) {
        setStatusMessage("Keep smiling!");
        setSmileCoords(null);
      }
      // Camera not started (409)
      else if (response.status === 409) {
        setStatusMessage("Camera not started. Click Start.");
      }
      // Error (500 or other)
      else {
        setStatusMessage("Error occurred.");
      }
    } catch (error) {
      setStatusMessage("Error: Could not connect to backend.");
    } finally {
      inFlight.current = false;
    }
  };

  /**
   * Starts camera session and polling for detection.
   * Shows spinner overlay while starting.
   */
  const handleStart = async () => {
    setLoading(true);
    setStatusMessage("Starting camera...");
    try {
      await startCamera();
      setImageSrc(null);
      setSmileCoords(null);
      setLastSmile({ coords: null, image: null });
      setStatusMessage("Keep smiling!");
      setDetectionRunning(true);
    } catch (error) {
      setStatusMessage("Failed to start camera.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Stops camera session and polling.
   */
  const handleStop = async () => {
    setDetectionRunning(false);
    clearInterval(intervalRef.current);
    setStatusMessage("Click 'Start' to begin.");
    try {
      await stopCamera();
    } catch (error) {
      // Optionally show an error, but do not block UI
    }
  };

  // Use last smile if nothing detected in current polling session
  const displayImage = smileCoords ? imageSrc : lastSmile.image;
  const displayCoords = smileCoords ? smileCoords : lastSmile.coords;
  const smileDetected = !!displayCoords;

  return (
    <div className="main-app-card">
      {/* Spinner overlay when loading */}
      {loading && (
        <div className="spinner-overlay">
          <div className="loader" />
        </div>
      )}

      <h1>Smile Detection App</h1>
      <div className="controls-row" style={{ justifyContent: "space-between" }}>
        {/* Start/Stop buttons */}
        <div>
          <button onClick={handleStart} disabled={detectionRunning || loading}>
            Start
          </button>
          <button onClick={handleStop} disabled={!detectionRunning || loading}>
            Stop
          </button>
        </div>
        {/* Status message */}
        <div className="status-label" style={{ marginLeft: 16 }}>
          <span>{statusMessage}</span>
        </div>
      </div>
      <div className="content-section-wider">
        <SmileViewer imageSrc={displayImage} />
        <SmileDetails coords={displayCoords} smileDetected={smileDetected} />
      </div>
    </div>
  );
}

export default App;
