import cv2
import numpy as np
import os

class LineSegmenter:
    def __init__(self, min_line_height=20):
        self.min_line_height = min_line_height

    def segment_lines(self, image_path, output_dir="output/short_lines_seg"):
        print("📄 Segmenting text lines...")

        os.makedirs(output_dir, exist_ok=True)

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"❌ Cannot read image: {image_path}")

        original = image.copy()

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Adaptive threshold (important for handwriting)
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            15,
            10
        )

        # Remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Horizontal projection
        projection = np.sum(thresh, axis=1)

        # Normalize projection
        projection = projection / np.max(projection)

        lines = []
        start = None

        for i, value in enumerate(projection):
            if value > 0.05 and start is None:
                start = i
            elif value <= 0.05 and start is not None:
                end = i
                if end - start > self.min_line_height:
                    lines.append((start, end))
                start = None

        # Catch last line
        if start is not None:
            lines.append((start, len(projection)))

        print(f"✅ Detected {len(lines)} text lines")

        cropped_paths = []

        for idx, (y1, y2) in enumerate(lines, 1):
            line_crop = original[y1:y2, :]

            crop_path = os.path.join(output_dir, f"line_{idx}.jpg")
            cv2.imwrite(crop_path, line_crop)
            cropped_paths.append(crop_path)

            # Draw for debug
            cv2.rectangle(image, (0, y1), (image.shape[1], y2), (0, 255, 0), 2)

        # Save debug image
        debug_path = os.path.join(output_dir, "debug_lines.jpg")
        cv2.imwrite(debug_path, image)

        print(f"🖼 Saved line crops to: {output_dir}")
        print(f"🧪 Debug image saved as: debug_lines.jpg")

        return cropped_paths


# ---------------- TEST ----------------
if __name__ == "__main__":
    image_path = "/workspaces/Handwritten-Answer-Script-Evaluation-Using-NLP-and-ML/input/short.jpeg"  # 👈 change this
    segmenter = LineSegmenter()
    segmenter.segment_lines(image_path)
