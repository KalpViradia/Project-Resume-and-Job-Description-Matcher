"""
generate_embeddings.py

- Loads metadata (text/sentences) from tokenized folder
- Generates embeddings using Sentence-BERT
- Saves embeddings to dataset/embeddings/
"""

from pathlib import Path
import pandas as pd
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# ---------------- Paths ----------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_DIR = BASE_DIR / "dataset"
TOKENIZED_DIR = DATASET_DIR / "tokenized"
EMBEDDINGS_DIR = DATASET_DIR / "embeddings"

EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

RESUMES_PKL = TOKENIZED_DIR / "resumes_metadata.pkl"
JDS_PKL = TOKENIZED_DIR / "jds_metadata.pkl"

# ---------------- Model Setup ----------------
MODEL_NAME = 'all-mpnet-base-v2'
print(f"Loading model: {MODEL_NAME}...")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer(MODEL_NAME, device=device)

# ---------------- Helper Functions ----------------
def generate_and_save_embeddings(pkl_path, output_name):
    if not pkl_path.exists():
        print(f"Warning: Metadata file not found at {pkl_path}")
        return

    print(f"Loading data from {pkl_path}...")
    df = pd.read_pickle(pkl_path)
    
    if df.empty:
        print(f"Warning: DataFrame is empty for {pkl_path}")
        return

    # Join sentences to get full text for embedding
    # Alternatively, we could embed sentences and average, but full text is a good start
    texts = df['sentences'].apply(lambda s: " ".join(s)).tolist()
    
    print(f"Generating embeddings for {len(texts)} items...")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Save embeddings
    output_path = EMBEDDINGS_DIR / f"{output_name}.npy"
    np.save(output_path, embeddings)
    print(f"Saved embeddings to {output_path}")
    
    # Save mapping (file -> index)
    mapping_path = EMBEDDINGS_DIR / f"{output_name}_mapping.json"
    mapping = {file_name: i for i, file_name in enumerate(df['file'])}
    import json
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"Saved mapping to {mapping_path}")

# ---------------- Main Execution ----------------
if __name__ == "__main__":
    generate_and_save_embeddings(RESUMES_PKL, "resumes_embeddings")
    generate_and_save_embeddings(JDS_PKL, "jds_embeddings")
    print("✅ Embedding generation complete.")
