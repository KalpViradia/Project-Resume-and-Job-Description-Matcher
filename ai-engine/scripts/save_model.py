"""
save_model.py

- Downloads the Sentence-BERT model
- Saves it to backend/models/sentence-bert
"""

from pathlib import Path
from sentence_transformers import SentenceTransformer

# ---------------- Paths ----------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
MODELS_DIR = BACKEND_DIR / "models"
MODEL_SAVE_PATH = MODELS_DIR / "sentence-bert"

MODELS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- Model Setup ----------------
MODEL_NAME = 'all-mpnet-base-v2'

def save_model():
    print(f"Downloading model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"Saving model to {MODEL_SAVE_PATH}...")
    model.save(str(MODEL_SAVE_PATH))
    print("✅ Model saved successfully.")

if __name__ == "__main__":
    save_model()
