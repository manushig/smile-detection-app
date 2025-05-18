/**
 * Main Application Component for Smile Detection UI.
 *
 * - Handles polling of backend API for smile detection images and coordinates.
 * - Manages state for selected model, polling, result image, and feedback messages.
 * - Renders model selection, start/stop controls, live status, and result viewers.
 * - Integrates SmileViewer and SmileDetails child components for modularity.
 */

import React, { useState, useEffect, useRef } from "react";
import SmileViewer from "./components/SmileViewer";
import SmileDetails from "./components/SmileDetails";
import { fetchSmileDetection } from "./api/SmileApi";
import "./index.css";

/**
 * Main React component for the Smile Detection App.
 * @returns {JSX.Element}
 */
function App() {
  // User-selected model ("opencv" or "dlib")
  const [model, setModel] = useState("opencv");
  // Indicates if smile detection polling is running
  const [detectionRunning, setDetectionRunning] = useState(false);
  // Status message shown in the UI
  const [statusMessage, setStatusMessage] = useState("Click 'Start' to begin.");
  // Latest result image and smile coordinates
  const [imageSrc, setImageSrc] = useState(null);
  const [smileCoords, setSmileCoords] = useState(null);
  // Stores last detected smile info for fallback display
  const [lastSmile, setLastSmile] = useState({ coords: null, image: null });

  // Polling interval and in-flight request tracking
  const intervalRef = useRef(null);
  const inFlight = useRef(false);

  /**
   * Side effect: Poll for smile detection when started.
   * Polls every second as long as detectionRunning is true.
   */
  useEffect(() => {
    if (detectionRunning) {
      intervalRef.current = setInterval(() => {
        if (!inFlight.current) {
          handleSmileDetection();
        }
      }, 1000);
    }
    // Cleanup on stop
    return () => clearInterval(intervalRef.current);
  }, [detectionRunning, model]);

  /**
   * Calls the backend API to fetch smile detection results.
   * Updates UI state based on HTTP status and data.
   * - 200: Parse coordinates, update image, update last smile.
   * - 204: No smile found, clears smileCoords but keeps lastSmile.
   * - 500/other: Shows error.
   */
  const handleSmileDetection = async () => {
    inFlight.current = true;
    try {
      const response = await fetchSmileDetection(model);
      if (!detectionRunning) return;
      if (response.status === 200) {
        // Parse coordinates from header (supports both JSON and single-quoted fallback)
        const coordsHeader = response.headers["x-smile-coords"];
        let coords = null;
        if (coordsHeader) {
          try {
            coords = JSON.parse(coordsHeader);
          } catch (e) {
            try {
              coords = JSON.parse(coordsHeader.replace(/'/g, '"'));
            } catch {
              coords = coordsHeader;
            }
          }
        }
        // Generate object URL for new image blob
        const newImage = URL.createObjectURL(response.data);
        setImageSrc(newImage);
        setSmileCoords(coords);
        setLastSmile({ coords, image: newImage });
      } else if (response.status === 204) {
        if (detectionRunning) {
          setSmileCoords(null);
        }
      } else {
        setStatusMessage("Error occurred.");
      }
    } catch (error) {
      setStatusMessage("Error: Could not connect to backend.");
    } finally {
      inFlight.current = false;
    }
  };

  /**
   * Handles model selection change (dropdown).
   * @param {React.ChangeEvent<HTMLSelectElement>} e
   */
  const handleModelChange = (e) => {
    setModel(e.target.value);
  };

  /**
   * Start smile detection polling and reset UI results.
   * Called when user clicks 'Start'.
   */
  const startDetection = () => {
    if (!detectionRunning) {
      setImageSrc(null);
      setSmileCoords(null);
      setLastSmile({ coords: null, image: null });
      setStatusMessage("Keep smiling!");
    }
    setDetectionRunning(true);
  };

  /**
   * Stop smile detection polling and update status message.
   * Called when user clicks 'Stop'.
   */
  const stopDetection = () => {
    setDetectionRunning(false);
    setStatusMessage("Click 'Start' to begin.");
    clearInterval(intervalRef.current);
  };

  // Select which image/coordinates to display: prefer most recent, else fallback to lastSmile
  const displayImage = smileCoords ? imageSrc : lastSmile.image;
  const displayCoords = smileCoords ? smileCoords : lastSmile.coords;
  const smileDetected = !!displayCoords;

  return (
    <div className="main-app-card">
      <h1>Smile Detection App</h1>
      <div className="controls-row" style={{ justifyContent: "space-between" }}>
        {/* Model selection dropdown */}
        <div>
          <label htmlFor="modelSelect">
            <b>Model:</b>{" "}
          </label>
          <select
            id="modelSelect"
            value={model}
            onChange={handleModelChange}
            disabled={detectionRunning}
          >
            <option value="opencv">OpenCV (Haar Cascade)</option>
            <option value="dlib">Dlib (HOG)</option>
          </select>
        </div>
        {/* Start/Stop buttons */}
        <div>
          <button onClick={startDetection} disabled={detectionRunning}>
            Start
          </button>
          <button onClick={stopDetection} disabled={!detectionRunning}>
            Stop
          </button>
        </div>
        {/* Status message */}
        <div className="status-label" style={{ marginLeft: 16 }}>
          <span>{statusMessage}</span>
        </div>
      </div>
      <div className="content-section-wider">
        {/* Image viewer and details */}
        <SmileViewer imageSrc={displayImage} />
        <SmileDetails coords={displayCoords} smileDetected={smileDetected} />
      </div>
    </div>
  );
}

export default App;
