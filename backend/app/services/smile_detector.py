import cv2
import logging

# Load OpenCV pre-trained classifiers
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_smile_and_save():
    """
    Captures a single frame from the webcam, detects faces and smiles,
    draws bounding boxes on all detected smiles, and returns the image bytes
    and coordinates of the smiles (if more than one box detected).
    Returns:
        tuple: (image bytes, smile coordinates) if multiple smiles are detected
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
        smiles = smile_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.3,
            minNeighbors=12,
            minSize=(22, 22)
        )
        best_box = None
        for (sx, sy, sw, sh) in smiles:
            aspect_ratio = sw / float(sh)
            smile_center_y = y + sy + sh // 2
            face_lower_threshold = y + int(0.6 * h)
            if aspect_ratio > 1.8 and smile_center_y > face_lower_threshold:
                # If you want only the best (largest) box:
                if (best_box is None) or (sw * sh > best_box[2] * best_box[3]):
                    best_box = (sx, sy, sw, sh)
        if best_box:
            sx, sy, sw, sh = best_box
            cv2.rectangle(frame, (x+sx, y+sy), (x+sx+sw, y+sy+sh), (0, 255, 0), 2)
            coords.append({
                "x": int(x+sx),
                "y": int(y+sy),
                "w": int(sw),
                "h": int(sh)
            })

   
    # Save a copy for inspection
    cv2.imwrite("last_frame.jpg", frame)

    if coords:
        # Save image with detected smiles
        cv2.imwrite("detected_smile.jpg", frame)
        # Show popup for manual inspection (optional)
        #cv2.imshow("Captured Frame", frame)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        # Return encoded image and coords
        _, img_encoded = cv2.imencode('.jpg', frame)
        return img_encoded.tobytes(), coords

    return None


