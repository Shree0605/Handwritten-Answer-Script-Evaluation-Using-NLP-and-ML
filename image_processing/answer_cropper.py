import cv2
import numpy as np
import os
from config import CROPPED_DIR

class AnswerCropper:
    def __init__(self):
        self.cropped_images = []
    
    def crop_answers(self, image_path, output_dir=CROPPED_DIR):
        """Crop answer boxes from answer script"""
        print("📷 Cropping answer boxes...")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"❌ Could not load image: {image_path}")
        
        # Store original for report
        self.original_image = img.copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 30, 150)
        
        # Dilate to close small gaps
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=3)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by Y position (top to bottom)
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
        
        cropped_paths = []
        i = 0
        
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            
            # Filter by size (adjust these values based on your answer sheets)
            if 200 < w < 1000 and 80 < h < 300:
                i += 1
                # Draw bounding box on original image
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Add question number
                cv2.putText(img, f"Q{i}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 
                          0.7, (0, 255, 0), 2)
                
                # Crop and save
                crop = self.original_image[y:y+h, x:x+w]
                crop_path = os.path.join(output_dir, f"answer_{i}.jpg")
                cv2.imwrite(crop_path, crop)
                cropped_paths.append(crop_path)
                
                print(f"  ✅ Cropped Q{i}: {w}x{h} pixels")
        
        # Save image with bounding boxes
        self.annotated_image = img
        annotated_path = os.path.join(output_dir, "annotated_answers.jpg")
        cv2.imwrite(annotated_path, img)
        
        print(f"🎯 Total questions detected: {len(cropped_paths)}")
        return cropped_paths

def test_cropper():
    cropper = AnswerCropper()
    image_path = os.path.join("input", "op.jpg")
    
    if os.path.exists(image_path):
        cropped_paths = cropper.crop_answers(image_path)
        return cropped_paths
    else:
        print(f"❌ Input image not found: {image_path}")
        return []

if __name__ == "__main__":
    test_cropper()

