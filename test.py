# # from ocr.ensemble_ocr import OCREnsemble

# # ocr = OCREnsemble()

# # pred, all_preds = ocr.ensemble_predict("output/cropped_answers/answer_1.jpg")

# # print("FINAL:", pred)
# # print("ALL:", all_preds)

# import os
# import torch
# from PIL import Image
# from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# class ShortAnswerOCR:
#     def __init__(self, model_name="microsoft/trocr-base-handwritten"):
#         print("🔧 Loading TrOCR model...")
#         self.processor = TrOCRProcessor.from_pretrained(model_name)
#         self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.model.to(self.device)
#         print(f"🚀 OCR running on: {self.device}")

#     def ocr_line(self, image_path):
#         image = Image.open(image_path).convert("RGB")

#         pixel_values = self.processor(image, return_tensors="pt").pixel_values
#         pixel_values = pixel_values.to(self.device)

#         with torch.no_grad():
#             generated_ids = self.model.generate(pixel_values)

#         text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
#         return text.strip()

#     def ocr_lines_and_merge(self, lines_dir):
#         print("🔍 Running OCR on segmented lines...")

#         line_files = sorted(
#             [f for f in os.listdir(lines_dir) if f.startswith("line_")],
#             key=lambda x: int(x.split("_")[1].split(".")[0])
#         )

#         final_text = []

#         for line_file in line_files:
#             line_path = os.path.join(lines_dir, line_file)
#             text = self.ocr_line(line_path)

#             print(f"  🧾 {line_file}: {text}")
#             if text:
#                 final_text.append(text)

#         merged_text = " ".join(final_text)

#         print("\n✅ FINAL SHORT ANSWER:")
#         print(merged_text)

#         return merged_text


# # ---------------- TEST ----------------
# if __name__ == "__main__":
#     lines_folder = "output/short_lines_seg"  # 👈 your segmented lines folder

#     ocr = ShortAnswerOCR()
#     ocr.ocr_lines_and_merge(lines_folder)

