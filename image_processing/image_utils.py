import cv2
import numpy as np
from PIL import Image
import os

class ImageUtils:
    @staticmethod
    def resize_image(image, max_width=800):
        """Resize image while maintaining aspect ratio"""
        if isinstance(image, str):
            image = cv2.imread(image)
        
        height, width = image.shape[:2]
        
        if width > max_width:
            ratio = max_width / width
            new_width = max_width
            new_height = int(height * ratio)
            image = cv2.resize(image, (new_width, new_height))
        
        return image
    
    @staticmethod
    def enhance_image(image):
        """Enhance image for better OCR"""
        if isinstance(image, str):
            image = cv2.imread(image)
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Denoising
        denoised = cv2.fastNlMeansDenoising(enhanced)
        
        return denoised
    
    @staticmethod
    def preprocess_for_ocr(image_path):
        """Complete preprocessing pipeline for OCR"""
        image = cv2.imread(image_path)
        
        # Resize if too large
        image = ImageUtils.resize_image(image)
        
        # Enhance
        enhanced = ImageUtils.enhance_image(image)
        
        return enhanced
    
    @staticmethod
    def save_image(image, output_path):
        """Save image to file"""
        if isinstance(image, np.ndarray):
            cv2.imwrite(output_path, image)
        elif isinstance(image, Image.Image):
            image.save(output_path)
        else:
            raise ValueError("Unsupported image type")
    
    @staticmethod
    def display_image(image, title="Image"):
        """Display image (for debugging)"""
        if isinstance(image, str):
            image = cv2.imread(image)
        
        cv2.imshow(title, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def test_image_utils():
    utils = ImageUtils()
    
    # Test with a sample image
    sample_image = "test_image.jpg"
    if os.path.exists(sample_image):
        enhanced = utils.preprocess_for_ocr(sample_image)
        utils.save_image(enhanced, "enhanced_test.jpg")
        print("✅ Image preprocessing test completed")
    else:
        print("⚠️  No test image found")

if __name__ == "__main__":
    test_image_utils()
