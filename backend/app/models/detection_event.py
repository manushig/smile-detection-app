import os
from datetime import datetime
import logging
import sqlite3
import json

def log_detection_event(coords, db_path=None):
    """
    Logs smile detection events with timestamp and coordinates into a local SQLite database.

    Args:
        coords (list): List of dictionaries containing smile coordinates.
        db_path (str): Path to SQLite DB file (default "smiles.db").
    """
    db_path = db_path or os.environ.get("SMILE_DB_PATH", "smiles.db")
    try:
         # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create the detections table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                coords TEXT
            )
        """)

        # Insert the current timestamp and smile coordinates into the table
        cursor.execute(
            "INSERT INTO detections (timestamp, coords) VALUES (?, ?)",
            (datetime.now().isoformat(), json.dumps(coords))
        )

         # Commit the transaction
        conn.commit()
    except sqlite3.Error as e:
        # Log any database-related error
        logging.exception("Database error during detection logging")
    finally:
        # Ensure the connection is closed to avoid DB locks
        if 'conn' in locals():
            conn.close()

def save_detection_image(image_bytes, save_dir=None):
    """
    Saves the detected smile image as a JPEG file in detected_smiles/.
    Returns the file path on success, None on failure.
    """
    save_dir = save_dir or os.environ.get("DETECTION_IMAGE_DIR", "detected_smiles")
    try:        
        os.makedirs(save_dir, exist_ok=True)
        filename = f"smile_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        filepath = os.path.join(save_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        logging.info(f"[DetectionEvent] Saved detected smile image to {filepath}")
        return filepath
    except Exception as e:
        logging.error(f"[DetectionEvent] Failed to save detected smile image: {e}")
        return None