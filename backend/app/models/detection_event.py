import sqlite3
import json
from datetime import datetime

def log_detection_event(coords):
    """
    Logs smile detection events with timestamp and coordinates
    into a local SQLite database.
    
    Args:
        coords (list): List of dictionaries containing smile coordinates.
    """
    try:
        # Connect to the local SQLite database
        conn = sqlite3.connect("smiles.db")
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
