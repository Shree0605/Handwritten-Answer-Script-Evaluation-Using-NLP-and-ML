import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import torch
# from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from transformers import AutoProcessor, AutoModelForVision2Seq
import Levenshtein
from collections import Counter
from tqdm import tqdm
from config import TROCR_MODEL_PATH

class OCREnsemble:
    def __init__(self, trocr_model_path=TROCR_MODEL_PATH):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 Using device: {self.device}")
        
        # Initialize models
        self._init_trocr(trocr_model_path)
        self._init_tesseract()
        self.easyocr_reader = None
    
    # def _init_trocr(self, model_path):
    #     """Initialize TrOCR model"""
    #     try:
    #         print("🔧 Loading TrOCR model...")
    #         self.trocr_processor = TrOCRProcessor.from_pretrained(model_path)
    #         self.trocr_model = VisionEncoderDecoderModel.from_pretrained(model_path)
    #         self.trocr_model.to(self.device)
    #         self.trocr_model.eval()
    #         print("✅ TrOCR model loaded successfully!")
    #     except Exception as e:
    #         print(f"❌ Failed to load TrOCR model: {e}")
    #         self.trocr_model = None
    
    def _init_trocr(self, model_path):
        try:
            print("🔧 Loading TrOCR (Vision2Seq) model...")
        
            self.trocr_processor = AutoProcessor.from_pretrained(model_path)
            self.trocr_model = AutoModelForVision2Seq.from_pretrained(model_path)
        
            self.trocr_model.to(self.device)
            self.trocr_model.eval()
        
            print("✅ TrOCR Vision2Seq model loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load TrOCR model: {e}")
            self.trocr_model = None

    
    def _init_tesseract(self):
        """Check Tesseract availability"""
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract OCR available!")
            self.tesseract_available = True
        except:
            print("❌ Tesseract not available")
            self.tesseract_available = False
    
    def _init_easyocr(self):
        """Initialize EasyOCR on demand"""
        if self.easyocr_reader is None:
            try:
                import easyocr
                self.easyocr_reader = easyocr.Reader(['en'])
                print("✅ EasyOCR initialized!")
            except Exception as e:
                print(f"❌ EasyOCR initialization failed: {e}")
    
    def preprocess_image(self, image):
        """Preprocess image for OCR"""
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        
        if isinstance(image, Image.Image):
            image_cv = np.array(image)
            if len(image_cv.shape) == 3:
                image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)
        else:
            image_cv = image.copy()
        
        # Convert to grayscale
        if len(image_cv.shape) == 3:
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_cv
        
        # Multiple preprocessing techniques
        processed_images = []
        processed_images.append(('original', gray))
        
        # Gaussian blur + threshold
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(('thresh_otsu', thresh1))
        
        return processed_images
    
    # def trocr_predict(self, image):
    #     """TrOCR prediction"""
    #     if self.trocr_model is None:
    #         return ""
        
    #     try:
    #         if isinstance(image, np.ndarray):
    #             image_pil = Image.fromarray(image).convert('RGB')
    #         else:
    #             image_pil = image
            
    #         pixel_values = self.trocr_processor(images=image_pil, return_tensors="pt").pixel_values.to(self.device)
            
    #         with torch.no_grad():
    #             generated_ids = self.trocr_model.generate(
    #                 pixel_values,
    #                 max_length=64,
    #                 num_beams=5,
    #                 early_stopping=True
    #             )
            
    #         prediction = self.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    #         return prediction.strip()
    #     except Exception as e:
    #         print(f"❌ TrOCR error: {e}")
    #         return ""

    def trocr_predict(self, image):
        if self.trocr_model is None:
            return ""

        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image).convert("RGB")

            inputs = self.trocr_processor(
                images=image,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                generated_ids = self.trocr_model.generate(
                    **inputs,
                    max_new_tokens=64
                )

            prediction = self.trocr_processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]

            return prediction.strip()

        except Exception as e:
            print(f"❌ TrOCR inference error: {e}")
            return ""

  
    def tesseract_predict(self, image):
        """Tesseract OCR prediction"""
        if not self.tesseract_available:
            return ""
        
        try:
            predictions = []
            psm_configs = {'psm_8': '8', 'psm_7': '7'}
            
            for config_name, psm in psm_configs.items():
                try:
                    config = f'--psm {psm}'
                    pred = pytesseract.image_to_string(image, config=config)
                    cleaned_pred = pred.strip()
                    if cleaned_pred:
                        predictions.append(cleaned_pred)
                except:
                    continue
            
            if predictions:
                counter = Counter(predictions)
                return counter.most_common(1)[0][0]
            return ""
        except Exception as e:
            print(f"❌ Tesseract error: {e}")
            return ""
    
    def easyocr_predict(self, image):
        """EasyOCR prediction"""
        self._init_easyocr()
        if self.easyocr_reader is None:
            return ""
        
        try:
            if isinstance(image, Image.Image):
                image_np = np.array(image)
            else:
                image_np = image
            
            if len(image_np.shape) == 3:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            
            results = self.easyocr_reader.readtext(image_np)
            texts = [result[1] for result in results]
            prediction = " ".join(texts).strip()
            return prediction
        except Exception as e:
            print(f"❌ EasyOCR error: {e}")
            return ""
    
    def normalize_text(self, text):
        return text.lower().strip()

    def similarity(self, a, b):
        if not a or not b:
            return 0.0
        return Levenshtein.ratio(
            self.normalize_text(a),
            self.normalize_text(b)
        )

    # def ensemble_predict(self, image_path):
    #     """Ensemble prediction for single image"""
    #     if not os.path.exists(image_path):
    #         return "", []
        
    #     original_image = Image.open(image_path).convert('RGB')
    #     processed_versions = self.preprocess_image(original_image)
        
    #     all_predictions = []
        
    #     for preprocess_name, processed_img in processed_versions:
    #         if preprocess_name == 'original':
    #             img_for_trocr = original_image
    #         else:
    #             img_for_trocr = Image.fromarray(processed_img).convert('RGB')
            
    #         # TrOCR
    #         trocr_pred = self.trocr_predict(img_for_trocr)
    #         if trocr_pred:
    #             all_predictions.append(('TrOCR', trocr_pred))
            
    #         # Tesseract
    #         tesseract_pred = self.tesseract_predict(processed_img)
    #         if tesseract_pred:
    #             all_predictions.append(('Tesseract', tesseract_pred))
            
    #         # EasyOCR
    #         easyocr_pred = self.easyocr_predict(processed_img)
    #         if easyocr_pred:
    #             all_predictions.append(('EasyOCR', easyocr_pred))
        
    #     if not all_predictions:
    #         return "", []
        
    #     # Voting ensemble
    #     texts = [pred[1] for pred in all_predictions]
    #     counter = Counter(texts)
    #     final_prediction = counter.most_common(1)[0][0]
        
    #     return final_prediction, all_predictions

    def ensemble_predict(self, image_path):
        if not os.path.exists(image_path):
            return "", []

        original_image = Image.open(image_path).convert("RGB")
        processed_versions = self.preprocess_image(original_image)

        trocr_predictions = []
        other_predictions = []

    # -----------------------------
    # Collect predictions
    # -----------------------------
        for preprocess_name, processed_img in processed_versions:
            img_for_trocr = (
                original_image if preprocess_name == "original"
                else Image.fromarray(processed_img).convert("RGB")
            )

            # TrOCR
            trocr_pred = self.trocr_predict(img_for_trocr)
            if trocr_pred:
                trocr_predictions.append(trocr_pred)

            # Tesseract
            tess_pred = self.tesseract_predict(processed_img)
            if tess_pred:
                other_predictions.append(tess_pred)

            # EasyOCR
            easy_pred = self.easyocr_predict(processed_img)
            if easy_pred:
                other_predictions.append(easy_pred)

    # -----------------------------
    # STEP 2: TrOCR-first logic
    # -----------------------------
        if not trocr_predictions:
            return "", []

        first_trocr = trocr_predictions[0]

    # Self-consistency check (TrOCR vs TrOCR)
        if len(trocr_predictions) > 1:
            sim = self.similarity(first_trocr, trocr_predictions[1])
            if sim >= 0.80:
                return first_trocr, [("TrOCR", p) for p in trocr_predictions]

    # Otherwise take second TrOCR (if exists)
        base_candidate = (
            trocr_predictions[1]
            if len(trocr_predictions) > 1
            else first_trocr
        )

    # -----------------------------
    # STEP 3: Fallback ensemble
    # -----------------------------
        ensemble_pool = [base_candidate] + other_predictions

        counter = Counter(ensemble_pool)
        majority_answer, _ = counter.most_common(1)[0]

    # Similarity validation
        sim = self.similarity(base_candidate, majority_answer)
        if sim >= 0.65:
            final_answer = majority_answer
        else:
            final_answer = base_candidate

        all_debug = (
            [("TrOCR", p) for p in trocr_predictions] +
            [("OtherOCR", p) for p in other_predictions]
        )

        return final_answer, all_debug

    
    def predict_batch(self, image_paths):
        """Predict for multiple images"""
        predictions = {}
        
        print("🔍 Running OCR on cropped answers...")
        for image_path in tqdm(image_paths, desc="OCR Processing"):
            filename = os.path.basename(image_path)
            final_pred, all_preds = self.ensemble_predict(image_path)
            predictions[filename] = {
                'final_prediction': final_pred,
                'all_predictions': all_preds
            }
            print(f"  {filename}: '{final_pred}'")
        
        return predictions
