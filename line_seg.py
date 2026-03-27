import cv2
import numpy as np
import os

class LineSegmenter:
    def __init__(self, output_dir="line_outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def segment_lines(self, image_path):
        print("📄 Segmenting text lines...")

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"❌ Cannot load image: {image_path}")

        original = img.copy()

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Binary (invert: text = white)
        _, binary = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        # Horizontal projection
        horizontal_sum = np.sum(binary, axis=1)

        # Normalize
        horizontal_sum = horizontal_sum / np.max(horizontal_sum)

        # Detect text rows
        threshold = 0.15
        text_rows = horizontal_sum > threshold

        lines = []
        start = None

        for i, val in enumerate(text_rows):
            if val and start is None:
                start = i
            elif not val and start is not None:
                end = i
                if end - start > 15:  # minimum line height
                    lines.append((start, end))
                start = None

        # Handle last line
        if start is not None:
            lines.append((start, len(text_rows)))

        print(f"✅ Detected {len(lines)} text lines")

        line_images = []

        for idx, (y1, y2) in enumerate(lines, start=1):
            line_crop = original[y1:y2, :]
            line_path = os.path.join(self.output_dir, f"line_{idx}.jpg")
            cv2.imwrite(line_path, line_crop)
            line_images.append(line_path)

            # Draw debug box
            cv2.rectangle(
                original,
                (0, y1),
                (original.shape[1], y2),
                (0, 255, 0),
                2
            )
            cv2.putText(
                original,
                f"L{idx}",
                (10, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        debug_path = os.path.join(self.output_dir, "debug_lines.jpg")
        cv2.imwrite(debug_path, original)

        print(f"🖼 Saved line crops to: {self.output_dir}")
        print(f"🧪 Debug image saved as: debug_lines.jpg")

        return line_images


# ---------------- TEST ----------------
if __name__ == "__main__":
    image_path = "/workspaces/Handwritten-Answer-Script-Evaluation-Using-NLP-and-ML/input/short.jpeg"   # 👈 PUT YOUR IMAGE PATH HERE
    segmenter = LineSegmenter(output_dir="/workspaces/Handwritten-Answer-Script-Evaluation-Using-NLP-and-ML/output/short_lines_seg")
    segmenter.segment_lines(image_path)
