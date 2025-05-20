""""
Smile Detection Service.
Provides utility to detect smiles in a given image frame using OpenCV.
"""

import cv2
import logging

# Always define cascades at the top so they exist for defaults
smile_cascade_global = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
face_cascade_global = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_smile_on_frame(
    frame,
    face_cascade=None,
    smile_cascade=None,
    imencode_func=None,
):
    """
    Detects faces and smiles in the given frame.
    Draws bounding boxes on detected smiles and returns encoded image and coordinates.

    Args:
        frame (np.ndarray): Image frame (BGR).
        face_cascade (CascadeClassifier, optional): Inject for testing or override default.
        smile_cascade (CascadeClassifier, optional): Inject for testing or override default.
        imencode_func (function, optional): Inject for testing/mocking cv2.imencode.
    Returns:
        tuple: (JPEG image bytes, [coords]) or None if no smile detected.
    """
    if frame is None:
        logging.warning("No frame received for smile detection.")
        return None

    # Use the injected cascades if provided, else fall back to module-level globals
    fc = face_cascade if face_cascade is not None else face_cascade_global
    sc = smile_cascade if smile_cascade is not None else smile_cascade_global
    imencode = imencode_func if imencode_func is not None else cv2.imencode

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = fc.detectMultiScale(gray, 1.3, 5)
    coords = []

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        smiles = sc.detectMultiScale(
            roi_gray,
            scaleFactor=1.5,
            minNeighbors=15,
            minSize=(22, 22)
        )
        best_box = None
        for (sx, sy, sw, sh) in smiles:
            aspect_ratio = sw / float(sh)
            smile_center_y = y + sy + sh // 2
            face_lower_threshold = y + int(0.6 * h)
            if aspect_ratio > 1.8 and smile_center_y > face_lower_threshold:
                if (best_box is None) or (sw * sh > best_box[2] * best_box[3]):
                    best_box = (sx, sy, sw, sh)
        if best_box:
            sx, sy, sw, sh = best_box
            cv2.rectangle(frame, (x + sx, y + sy), (x + sx + sw, y + sy + sh), (0, 255, 0), 2)
            coords.append({
                "x": int(x + sx),
                "y": int(y + sy),
                "w": int(sw),
                "h": int(sh)
            })

    if coords:
        success, img_encoded = imencode('.jpg', frame)
        if success:
            return img_encoded.tobytes(), coords
        else:
            logging.error("Failed to encode image to JPEG.")
            return None

    return None