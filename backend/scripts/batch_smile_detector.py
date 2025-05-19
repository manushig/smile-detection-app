import cv2
import os
import shutil

# Directories
INPUT_DIR = 'input_images'
SMILE_DIR = 'output_images/opencv_smile_detected'
NO_SMILE_DIR = 'output_images/opencv_no_smile_detected'

os.makedirs(SMILE_DIR, exist_ok=True)
os.makedirs(NO_SMILE_DIR, exist_ok=True)

# Load OpenCV pre-trained classifiers
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_smile_in_image(image_path):
    frame = cv2.imread(image_path)
    if frame is None:
        return False, None

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
    return bool(coords), frame

def main():
    total = 0
    smiles = 0
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(INPUT_DIR, filename)
            found_smile, output_img = detect_smile_in_image(path)
            if found_smile:
                output_path = os.path.join(SMILE_DIR, filename)
                cv2.imwrite(output_path, output_img)
                smiles += 1
            else:
                # If you want to copy, or save original image in no_smile_detected
                shutil.copy2(path, os.path.join(NO_SMILE_DIR, filename))
            total += 1
            print(f"{filename}: {'SMILE' if found_smile else 'NO SMILE'}")
    print(f"\nSummary: {smiles} of {total} images detected as smiles.")

if __name__ == "__main__":
    main()
