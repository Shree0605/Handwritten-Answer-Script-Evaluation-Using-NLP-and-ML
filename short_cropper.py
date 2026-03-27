import cv2
import numpy as np
import os

# =========================
# 🔧 CHANGE THIS PATH ONLY
# =========================
IMAGE_PATH = "/workspaces/Handwritten-Answer-Script-Evaluation-Using-NLP-and-ML/input/short.jpeg"   # <-- your image path here
OUTPUT_DIR = "/workspaces/Handwritten-Answer-Script-Evaluation-Using-NLP-and-ML/output/short_answers"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def crop_short_answers(image_path, output_dir):
    print("📷 Loading image...")
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError(f"❌ Could not load image: {image_path}")

    original = img.copy()

    print("🔍 Preprocessing...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(gray, 50, 150)

    kernel = np.ones((7, 7), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=3)

    print("📦 Finding contours...")
    contours, _ = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    count = 0
    cropped_paths = []

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        aspect_ratio = w / float(h)

        # 🔑 SHORT ANSWER FILTERS
        if (
            area > 30000 and
            w > 600 and
            h > 120 and
            aspect_ratio > 2.5
        ):
            count += 1

            print(f"✅ Detected Answer {count} | w={w}, h={h}")

            cv2.rectangle(
                img, (x, y), (x + w, y + h), (0, 255, 0), 2
            )
            cv2.putText(
                img, f"Ans {count}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            crop = original[y:y + h, x:x + w]
            crop_path = os.path.join(output_dir, f"short_answer_{count}.jpg")
            cv2.imwrite(crop_path, crop)
            cropped_paths.append(crop_path)

    annotated_path = os.path.join(output_dir, "annotated_short_answers.jpg")
    cv2.imwrite(annotated_path, img)

    print("====================================")
    print(f"🎯 Total short answers detected: {count}")
    print(f"📁 Crops saved in: {output_dir}")
    print(f"🖼 Annotated image: {annotated_path}")
    print("====================================")

    return cropped_paths


# =========================
# ▶ RUN
# =========================
if __name__ == "__main__":
    crop_short_answers(IMAGE_PATH, OUTPUT_DIR)
