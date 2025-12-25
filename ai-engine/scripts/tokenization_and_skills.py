"""
tokenization_and_skills.py

- Loads cleaned resumes and JDs from processed folder
- Tokenizes text into sentences
- Extracts technical and common skills
- Saves tokenized text and metadata for embeddings

Dependencies:
    pip install nltk pandas
"""

from pathlib import Path
import re
import pandas as pd
import json
import nltk
from nltk.tokenize import sent_tokenize

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# ---------------- Paths ----------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_DIR = BASE_DIR / "dataset"

DATASET_RESUME_DIR = DATASET_DIR / "processed/resumes"
DATASET_JD_DIR = DATASET_DIR / "processed/jds"

SAVE_DIR = DATASET_DIR / "tokenized"
RESUME_SAVE = SAVE_DIR / "resumes"
JD_SAVE = SAVE_DIR / "jds"

RESUME_SAVE.mkdir(parents=True, exist_ok=True)
JD_SAVE.mkdir(parents=True, exist_ok=True)

# ---------------- Load skill lists ----------------
SKILLS_TECH_PATH = DATASET_DIR / "raw/dataset_noisy_pdfs/metadata/skills_tech.json"
SKILLS_COMMON_PATH = DATASET_DIR / "raw/dataset_noisy_pdfs/metadata/skills_common.json"

try:
    with open(SKILLS_TECH_PATH, 'r', encoding='utf-8') as f:
        TECH_SKILLS = json.load(f)
except FileNotFoundError:
    print(f"Warning: Tech skills file not found at {SKILLS_TECH_PATH}")
    TECH_SKILLS = []

try:
    with open(SKILLS_COMMON_PATH, 'r', encoding='utf-8') as f:
        COMMON_SKILLS = json.load(f)
except FileNotFoundError:
    print(f"Warning: Common skills file not found at {SKILLS_COMMON_PATH}")
    COMMON_SKILLS = []

ALL_SKILLS = TECH_SKILLS + COMMON_SKILLS
ALL_SKILLS_LOWER = [s.lower() for s in ALL_SKILLS]

# ---------------- Helper functions ----------------
def clean_whitespace(text):
    """Remove extra spaces, tabs, newlines."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_skills(text, skills_list=ALL_SKILLS_LOWER):
    """Return list of skills found in text (case-insensitive)."""
    text_lower = text.lower()
    found = [s for s in skills_list if s in text_lower]
    return list(set(found))  # remove duplicates

# ---------------- Process Resumes ----------------
resume_data = []

# Check if directory exists before globbing
if DATASET_RESUME_DIR.exists():
    for txt_file in DATASET_RESUME_DIR.glob("*.txt"):
        text = txt_file.read_text(encoding="utf-8")
        text_clean = clean_whitespace(text)
        sentences = sent_tokenize(text_clean)
        skills = extract_skills(text_clean)

        # Save tokenized text
        tokenized_path = RESUME_SAVE / f"{txt_file.stem}_tokenized.txt"
        tokenized_path.write_text("\n".join(sentences), encoding="utf-8")

        # Store metadata
        resume_data.append({
            "file": txt_file.name,
            "sentences": sentences,
            "skills": skills
        })
else:
    print(f"Warning: Resume directory not found at {DATASET_RESUME_DIR}")

print(f"Processed {len(resume_data)} resumes.")

# ---------------- Process JDs ----------------
jd_data = []

if DATASET_JD_DIR.exists():
    for txt_file in DATASET_JD_DIR.glob("*.txt"):
        text = txt_file.read_text(encoding="utf-8")
        text_clean = clean_whitespace(text)
        sentences = sent_tokenize(text_clean)
        skills = extract_skills(text_clean)

        # Save tokenized text
        tokenized_path = JD_SAVE / f"{txt_file.stem}_tokenized.txt"
        tokenized_path.write_text("\n".join(sentences), encoding="utf-8")

        # Store metadata
        jd_data.append({
            "file": txt_file.name,
            "sentences": sentences,
            "skills": skills
        })
else:
    print(f"Warning: JD directory not found at {DATASET_JD_DIR}")

print(f"Processed {len(jd_data)} job descriptions.")

# ---------------- Save metadata for embeddings ----------------
if resume_data:
    pd.DataFrame(resume_data).to_pickle(SAVE_DIR / "resumes_metadata.pkl")
if jd_data:
    pd.DataFrame(jd_data).to_pickle(SAVE_DIR / "jds_metadata.pkl")

print("✅ Tokenization and skill extraction complete.")