"""
Smile Detection Service.
Improved: More accurate smile detection using OpenCV.
"""

import cv2
import logging

# Use the alternative smile cascade (sometimes more accurate)
smile_cascade_global = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_smile.xml'
)
face_cascade_global = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

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
    
    fc = face_cascade if face_cascade is not None else face_cascade_global
    sc = smile_cascade if smile_cascade is not None else smile_cascade_global
    imencode = imencode_func if imencode_func is not None else cv2.imencode

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)  # Improve contrast for detection

    faces = fc.detectMultiScale(gray, 1.3, 5)
    coords = []

    for (x, y, w, h) in faces:
        # Focus only on the lower 50% of the face where smiles are likely
        lower_face_start = int(h * 0.5)
        roi_gray = gray[y + lower_face_start:y + h, x:x + w]

        # Improved detection parameters
        smiles = sc.detectMultiScale(
            roi_gray,
            scaleFactor=1.3,     # More thorough scan
            minNeighbors=25,     # Require more neighbor rectangles to reduce false positives
            minSize=(25, 25),    # Ignore tiny "smiles" (less likely to be real)
            maxSize=(200, 200),  # Ignore huge "smiles"
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        #print(f"Faces found: {len(faces)} | Smile regions: {len(smiles)} | Valid smiles: {len([s for s in smiles if (s[2]/s[3]) > 2.0])}")

        best_box = None
        for (sx, sy, sw, sh) in smiles:
            aspect_ratio = sw / float(sh)
            # Smiles are typically wide, so require a high aspect ratio
            if aspect_ratio > 2.0:
                # Keep the largest smile (if multiple detected)
                if (best_box is None) or (sw * sh > best_box[2] * best_box[3]):
                    best_box = (sx, sy, sw, sh)

        if best_box and len(smiles) >= 1:  # Require at least 1 valid smile
            sx, sy, sw, sh = best_box
            # Adjust sy for the lower face ROI offset
            sy_adjusted = sy + lower_face_start
            cv2.rectangle(frame, (x + sx, y + sy_adjusted), (x + sx + sw, y + sy_adjusted + sh), (0, 255, 0), 2)
            coords.append({
                "x": int(x + sx),
                "y": int(y + sy_adjusted),
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
