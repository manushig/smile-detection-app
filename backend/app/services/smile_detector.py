import cv2
import logging
from PIL import Image

# Load OpenCV pre-trained classifiers
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_smile_and_save():
    """
    Captures a single frame from the webcam, detects faces and smiles,
    draws bounding boxes on detected smiles, and returns the image bytes
    and coordinates of the smiles. Saves the image if any smile is detected.
    
    Returns:
        tuple: (image bytes, smile coordinates) if smile is detected
        None: if no smile is detected or capture fails
    """
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logging.warning("Webcam could not be accessed.")
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret:
        logging.warning("Failed to read frame from webcam.")
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    coords = []

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
        for (sx, sy, sw, sh) in smiles:
            # Draw rectangle around detected smile
            cv2.rectangle(frame, (x+sx, y+sy), (x+sx+sw, y+sy+sh), (0, 255, 0), 2)
            coords.append({"x": x+sx, "y": y+sy, "w": sw, "h": sh})

    if coords:
        # Save and encode the image with detected smiles
        cv2.imwrite("detected_smile.jpg", frame)
        _, img_encoded = cv2.imencode('.jpg', frame)
        return img_encoded.tobytes(), coords

    return None
