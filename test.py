from ocr.ensemble_ocr import OCREnsemble

ocr = OCREnsemble()

pred, all_preds = ocr.ensemble_predict("output/cropped_answers/answer_1.jpg")

print("FINAL:", pred)
print("ALL:", all_preds)
