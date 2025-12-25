"""
main.py

- FastAPI application for Resume & JD Matcher
- Loads the saved Sentence-BERT model
- Provides /match and /chat endpoints
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
import torch
import pypdf
import docx
import io
import os
from dotenv import load_dotenv

# ---------------- App Setup ----------------
app = FastAPI(title="Resume & JD Matcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Paths ----------------
BASE_DIR = Path(__file__).resolve().parent.parent  # python_backend/
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "sentence-bert"

# Load .env
load_dotenv(BASE_DIR / ".env")

# ---------------- Load Sentence-BERT Model ----------------
print(f"Loading Sentence-BERT model from {MODEL_PATH}...")
try:
    if MODEL_PATH.exists():
        model = SentenceTransformer(str(MODEL_PATH))
    else:
        print("Local model not found, downloading 'all-mpnet-base-v2'...")
        model = SentenceTransformer('all-mpnet-base-v2')
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    raise e

# ---------------- Skills DB ----------------
EXPANDED_SKILLS_DB = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "ruby",
    "react", "angular", "vue", "next.js", "node.js", "express", "django", "flask", "fastapi", "spring boot",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "git", "linux", "agile", "scrum", "communication", "leadership", "problem solving"
}

# ---------------- Helper Functions ----------------
def extract_text_from_file(file_content: bytes, filename: str) -> str:
    text = ""
    try:
        if filename.lower().endswith(".pdf"):
            reader = pypdf.PdfReader(io.BytesIO(file_content))
            for page in reader.pages:
                text += page.extract_text() or ""
        elif filename.lower().endswith(".docx"):
            doc = docx.Document(io.BytesIO(file_content))
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif filename.lower().endswith(".txt"):
            text = file_content.decode("utf-8")
        else:
            raise ValueError("Unsupported file format")
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
    return text.strip()

def extract_skills(text: str) -> set:
    import re
    found_skills = set()
    text_lower = text.lower()
    for skill in EXPANDED_SKILLS_DB:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    return found_skills

# ---------------- Gemini Setup ----------------
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured.")
    
   # List all models
    # print("\n🔍 Available Gemini Models:")
    # try:
    #     models = genai.list_models()
    #     for m in models:
    #         print(f" - {m.name}")
    # except Exception as e:
    #     print("❌ Error listing models:", e)

    # print("--------------------------------------------------\n")
else:
    print("⚠️ Warning: GEMINI_API_KEY not set. /chat endpoint will fail.")

# ---------------- Data Models ----------------
class MatchResponse(BaseModel):
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # [{"role": "user"|"assistant", "content": "text"}]
    context: str = ""          # Optional context

class ChatResponse(BaseModel):
    response: str

# ---------------- Endpoints ----------------
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Resume & JD Matcher API is running"}

# ---------------- Match Endpoint ----------------
@app.post("/match", response_model=MatchResponse)
async def match_resume_jd(
    resume: UploadFile = File(None),
    resume_text_input: str = Form(None),
    jd_text: str = Form(...)
):
    try:
        resume_text = ""
        if resume:
            contents = await resume.read()
            resume_text = extract_text_from_file(contents, resume.filename)
        elif resume_text_input:
            resume_text = resume_text_input
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Resume text is empty.")
        
        embeddings = model.encode([resume_text, jd_text], convert_to_tensor=True, normalize_embeddings=True)
        cosine_scores = util.cos_sim(embeddings[0], embeddings[1])
        score = cosine_scores.item() * 100

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        matched = list(resume_skills.intersection(jd_skills))
        missing = list(jd_skills - resume_skills)

        return MatchResponse(
            match_score=round(score, 2),
            matched_skills=matched,
            missing_skills=missing
        )
    except Exception as e:
        print(f"Error in /match: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Chat Endpoint ----------------
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured.")
    
    try:
        # Initialize model
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        
        # Convert history to Gemini format: list of {'role': 'user'|'model', 'parts': [...]}
        gemini_history = []
        
        if request.context:
            pass 

        # Map 'assistant' -> 'model' and ensure correct structure
        for msg in request.history:
            role = msg.get("role")
            content = msg.get("content")
            parts = msg.get("parts")

            if role == "assistant":
                role = "model"
            
            if role in ["user", "model"]:
                if parts:
                    gemini_history.append({"role": role, "parts": parts})
                elif content:
                    gemini_history.append({"role": role, "parts": [content]})
        
        # Initialize chat session
        chat = model.start_chat(history=gemini_history)
        
        # Constuct prompt with context if provided
        final_prompt = request.message
        if request.context:
            final_prompt = f"Context: {request.context}\n\nUser: {request.message}"

        # Send message
        response = chat.send_message(final_prompt)
        
        return ChatResponse(response=response.text)
    except Exception as e:
        print(f"Error in /chat: {e}")
        # Return a more descriptive error for debugging if needed, or keeping it generic
        raise HTTPException(status_code=500, detail=f"Gemini Error: {str(e)}")

# ---------------- Main ----------------
if __name__ == "__main__":
    import uvicorn
    # Use reload=False to avoid import errors with direct script execution
    uvicorn.run(app, host="0.0.0.0", port=8000)
