import cv2
import dlib
import numpy as np
import logging

# Load DLib models
MODEL_PATH = 'models/shape_predictor_68_face_landmarks.dat'
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(MODEL_PATH)

# Mouth landmark indices (68-point model)
MOUTH_IDX = list(range(48, 68))

def mouth_aspect_ratio(coords):
    A = np.linalg.norm(coords[51] - coords[57])
    B = np.linalg.norm(coords[48] - coords[54])
    return A / B if B != 0 else 0

def mouth_lip_height(coords):
    return np.linalg.norm(coords[62] - coords[66])

def mouth_arc(coords):
    left_corner = coords[48]
    right_corner = coords[54]
    center = coords[51]
    return ((left_corner[1] + right_corner[1]) / 2) - center[1]

def detect_smile_and_save():
    """
    Captures a single frame from the webcam, detects faces and smiles,
    draws bounding boxes on detected smiles, and returns the image bytes
    and coordinates. Returns None if no smile is detected or on error.
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
    faces = detector(gray)
    coords = []

    for rect in faces:
        shape = predictor(gray, rect)
        points = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])
        mouth = points[MOUTH_IDX]

        mar = mouth_aspect_ratio(points)
        lip_height = mouth_lip_height(points)
        arc = mouth_arc(points)

        # Heuristic smile score, tweak as needed!
        score = 0
        if mar > 0.36: score += 1
        if lip_height > 6: score += 1
        if arc > 0: score += 1

        if score >= 2:
            x, y, w, h = cv2.boundingRect(mouth)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            coords.append({
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h)
            })
        # Optional: draw landmarks for visual debugging
        for (mx, my) in mouth:
            cv2.circle(frame, (mx, my), 1, (0, 0, 255), -1)

    cv2.imwrite("last_frame.jpg", frame)  # Always save for manual check

    if coords:
        # Save and encode image with bounding box
        cv2.imwrite("detected_smile.jpg", frame)
        # Uncomment to pop up the image window for visual confirmation
        # cv2.imshow("Captured Frame", frame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        _, img_encoded = cv2.imencode('.jpg', frame)
        return img_encoded.tobytes(), coords

    return None
