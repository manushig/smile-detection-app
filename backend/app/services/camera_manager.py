"""
Camera Manager Singleton.
Handles background webcam access, frame capture, and clean resource release.
Intended for real-time smile detection endpoints.
"""

import cv2
import threading
import logging
import time

class CameraManager:
    """
    Singleton class to manage webcam access and frame capture.
    Maintains the latest frame in memory and provides thread-safe access.
    """

    def __init__(self):
        self._cap = None
        self._lock = threading.Lock()
        self._running = False
        self._frame = None
        self._thread = None

    def start(self):
        """
        Starts the camera and begins background frame capture.
        """
        with self._lock:
            if self._running:
                logging.warning("Camera already started.")
                return False
            self._cap = cv2.VideoCapture(0)
            if not self._cap.isOpened():
                logging.error("Failed to open webcam.")
                self._cap = None
                return False
            self._running = True
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()
            logging.info("Camera started.")
            return True

    def stop(self):
        """
        Stops the camera and releases resources.
        """
        with self._lock:
            if not self._running:
                logging.info("Camera already stopped.")
                return False
            self._running = False
            if self._cap:
                self._cap.release()
                self._cap = None
            self._frame = None
            logging.info("Camera stopped and resources released.")
            return True

    def _capture_loop(self):
        """
        Background thread loop to read frames continuously.
        """
        while self._running and self._cap:
            ret, frame = self._cap.read()
            if ret:
                self._frame = frame
            else:
                logging.warning("Failed to read frame from webcam.")
                self._frame = None
            time.sleep(0.03)  # ~30 FPS

    def get_frame(self):
        """
        Returns the latest captured frame.
        Returns:
            np.ndarray or None: The latest frame, or None if not available.
        """
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def is_running(self):
        """
        Returns whether the camera is running.
        Returns:
            bool: True if camera is running, False otherwise.
        """
        with self._lock:
            return self._running

# Singleton instance
camera_manager = CameraManager()
