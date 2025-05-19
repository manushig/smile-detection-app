# File: scripts/dlib_smart_smile_batch.py

import os
import cv2
import dlib
import numpy as np

# --------- Configurable Paths ---------
MODEL_PATH = 'models/shape_predictor_68_face_landmarks.dat'
INPUT_DIR = 'input_images'
SMILE_DIR = 'output_images/dlib_smile_detected'
NO_SMILE_DIR = 'output_images/dlib_no_smile_detected'

# --------- Setup ---------
os.makedirs(SMILE_DIR, exist_ok=True)
os.makedirs(NO_SMILE_DIR, exist_ok=True)

# Mouth landmark indices (68-point model)
MOUTH_IDX = list(range(48, 68))

def mouth_aspect_ratio(coords):
    """Mouth Aspect Ratio (vertical / horizontal)"""
    A = np.linalg.norm(coords[51] - coords[57])
    B = np.linalg.norm(coords[48] - coords[54])
    return A / B if B != 0 else 0

def mouth_lip_height(coords):
    """Vertical distance between upper and lower inner lip"""
    return np.linalg.norm(coords[62] - coords[66])

def mouth_arc(coords):
    """How much corners are above mouth center (smile curve)"""
    left_corner = coords[48]
    right_corner = coords[54]
    center = coords[51]
    return ((left_corner[1] + right_corner[1]) / 2) - center[1]

# --------- Load Models ---------
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(MODEL_PATH)

# --------- Process Batch ---------
for img_file in os.listdir(INPUT_DIR):
    img_path = os.path.join(INPUT_DIR, img_file)
    image = cv2.imread(img_path)
    if image is None:
        print(f"Skipping {img_file} (cannot read)")
        continue

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    smile_found = False

    for rect in faces:
        shape = predictor(gray, rect)
        coords = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])
        mouth = coords[MOUTH_IDX]

        mar = mouth_aspect_ratio(coords)
        lip_height = mouth_lip_height(coords)
        arc = mouth_arc(coords)

        # Print all the values for manual tuning
        print(f"{img_file}: MAR={mar:.2f}, LipHeight={lip_height:.2f}, Arc={arc:.2f}")

        # Heuristic "smile score" (adjust as needed)
        score = 0
        if mar > 0.36: score += 1
        if lip_height > 6: score += 1
        if arc > 0: score += 1

        if score >= 2:
            smile_found = True
            x, y, w, h = cv2.boundingRect(mouth)
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # Draw landmarks for inspection
        for (mx, my) in mouth:
            cv2.circle(image, (mx, my), 1, (0, 0, 255), -1)

    # Save result
    out_path = os.path.join(SMILE_DIR if smile_found else NO_SMILE_DIR, img_file)
    cv2.imwrite(out_path, image)
    print(f"{img_file}: {'Smile' if smile_found else 'No Smile'}")

print("Batch processing complete!")
