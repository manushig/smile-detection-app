import sqlite3
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def manual_test_detection_and_db(endpoint: str, backend_label: str):
    """
    Manual integration test for a given smile detection endpoint.
    Args:
        endpoint (str): The API route to call (e.g. '/detect/opencv').
        backend_label (str): Human-readable backend name for logs.
    """
    print(f"\n🔍 Testing endpoint: {endpoint} ({backend_label})")
    response = client.get(endpoint)
    print(f"📡 Response status code: {response.status_code}")

    if response.status_code == 200:
        print("Smile detected and image returned.")
        # Check DB entry
        try:
            conn = sqlite3.connect("smiles.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM detections")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"📦 DB entries found: {count}")
            assert count > 0
        except Exception as e:
            print("Error accessing DB:", e)

    elif response.status_code == 204:
        print("No smile detected. Try smiling visibly!")
        print("API returned:", response.json())

    else:
        print("Unexpected error:")
        print("Response:", response.text)

if __name__ == "__main__":
    # Test both OpenCV and Dlib endpoints
    endpoints = [
        ("/detect/opencv", "OpenCV"),
        ("/detect/dlib", "Dlib")
    ]
    for endpoint, label in endpoints:
        manual_test_detection_and_db(endpoint, label)
