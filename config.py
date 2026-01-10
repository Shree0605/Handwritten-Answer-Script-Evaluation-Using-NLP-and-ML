import os

# Path configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CROPPED_DIR = os.path.join(OUTPUT_DIR, "cropped_answers")
PREDICTIONS_DIR = os.path.join(OUTPUT_DIR, "predictions")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

# Model configurations
TROCR_MODEL_PATH = "Yuva-2106/trocr-handwriting-enhanced"
SIMILARITY_MODEL = 'paraphrase-MiniLM-L6-v2'

# Grading configurations
ML_THRESHOLD = 0.65
MARKS_PER_QUESTION = 1  # Default marks per question

# Create directories
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CROPPED_DIR, exist_ok=True)
os.makedirs(PREDICTIONS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
