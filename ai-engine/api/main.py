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
import time

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured.")
else:
    print("⚠️ Warning: GEMINI_API_KEY not set. /chat endpoint will fail.")

# Configurable max retries
MAX_RETRIES = 3

def safe_gemini_call(action_func, *args, **kwargs):
    """Executes a Gemini SDK call with exponential backoff for rate limits."""
    for attempt in range(MAX_RETRIES):
        try:
            return action_func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg or "rate" in error_msg:
                if attempt < MAX_RETRIES - 1:
                    sleep_time = 2 ** attempt
                    print(f"⚠️ Rate limited. Gemini API backing off for {sleep_time} seconds (Attempt {attempt+1}/{MAX_RETRIES})...")
                    import time
                    time.sleep(sleep_time)
                    continue
            raise e

# ---------------- Data Models ----------------
class MatchResponse(BaseModel):
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    improvement_suggestions: list[str] = []

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

        # Smart skill extraction using Gemini 1.5 flash
        import json
        
        # Truncate text to save tokens
        safe_jd = jd_text[:3000]
        safe_resume = resume_text[:3000]
        
        prompt = f"""
        Analyze this Job Description and Resume. Extract ONLY: skills, tools, experience (years/roles), and keywords. Ignore long descriptions.
        Check if the resume possesses those skills. Group them into two arrays: "matched_skills" (present in resume) and "missing_skills" (absent from resume).
        Make sure the skills are concise phrase elements.
        Provide maximum 5 improvement suggestions (each < 10 words).
        
        Output ONLY a valid JSON object matching this schema exactly, and nothing else (no markdown ticks):
        {{
            "match_score": {round(score, 2)},
            "matched_skills": ["Skill 1", "Skill 2"],
            "missing_skills": ["Skill 3", "Skill 4"],
            "improvement_suggestions": ["Suggestion 1", "Suggestion 2"]
        }}

        JD: {safe_jd}
        
        RESUME: {safe_resume}
        """
        
        try:
            gemini_skills_model = genai.GenerativeModel("gemini-1.5-flash")
            response = safe_gemini_call(
                gemini_skills_model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
            parsed_skills = json.loads(response.text)
            
            # The AI might generate its own score, but we will fall back to sentence-bert score if missing
            ai_score = parsed_skills.get("match_score")
            final_score = float(ai_score) if ai_score is not None else round(score, 2)
            
            matched = parsed_skills.get("matched_skills", [])
            missing = parsed_skills.get("missing_skills", [])
            suggestions = parsed_skills.get("improvement_suggestions", [])
        except Exception as ai_err:
            print(f"Failed to use Gemini for skills extraction, falling back to basic regex: {ai_err}")
            final_score = round(score, 2)
            resume_skills = extract_skills(resume_text)
            jd_skills = extract_skills(jd_text)
            matched = list(resume_skills.intersection(jd_skills))
            missing = list(jd_skills - resume_skills)
            suggestions = []

        return MatchResponse(
            match_score=final_score,
            matched_skills=matched,
            missing_skills=missing,
            improvement_suggestions=suggestions
        )
    except Exception as e:
        print(f"Error in /match: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class CompareResponse(BaseModel):
    score_a: float
    score_b: float
    recommendation: str

# ---------------- Compare Endpoint ----------------
@app.post("/compare", response_model=CompareResponse)
async def compare_resumes(
    resume_a: UploadFile = File(None),
    resume_text_input_a: str = Form(None),
    resume_b: UploadFile = File(None),
    resume_text_input_b: str = Form(None),
    jd_text: str = Form(...)
):
    try:
        # Extract text for Resume A
        text_a = ""
        if resume_a:
            contents_a = await resume_a.read()
            text_a = extract_text_from_file(contents_a, resume_a.filename)
        elif resume_text_input_a:
            text_a = resume_text_input_a
            
        # Extract text for Resume B
        text_b = ""
        if resume_b:
            contents_b = await resume_b.read()
            text_b = extract_text_from_file(contents_b, resume_b.filename)
        elif resume_text_input_b:
            text_b = resume_text_input_b

        if not text_a or not text_b:
            raise HTTPException(status_code=400, detail="Both resumes must be provided.")
            
        # Calculate semantic similarity scores setup
        embeddings = model.encode([text_a, text_b, jd_text], convert_to_tensor=True, normalize_embeddings=True)
        score_a = round(util.cos_sim(embeddings[0], embeddings[2]).item() * 100, 2)
        score_b = round(util.cos_sim(embeddings[1], embeddings[2]).item() * 100, 2)
        
        # Truncate text to save tokens
        safe_jd = jd_text[:3000]
        safe_a = text_a[:3000]
        safe_b = text_b[:3000]
        
        # Use Gemini for recommendation
        prompt = f"""
        You are an expert technical recruiter evaluating two candidates for a role.
        Job Description:
        {safe_jd}
        
        Resume A (Score: {score_a}%):
        {safe_a}
        
        Resume B (Score: {score_b}%):
        {safe_b}
        
        Analyze both resumes against the job description. Which one is objectively better suited for the role and why?
        Be concise (1-2 paragraphs max). Highlight the decisive factor.
        """
        try:
            gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            response = safe_gemini_call(gemini_model.generate_content, prompt)
            recommendation = response.text
        except Exception as ai_err:
            print(f"Gemini error during compare: {ai_err}")
            recommendation = "AI recommendation temporarily unavailable due to API limits. Based purely on numerical matching, select the resume with the higher score."

        return CompareResponse(
            score_a=score_a,
            score_b=score_b,
            recommendation=recommendation
        )
    except Exception as e:
        print(f"Error in /compare: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Chat Endpoint ----------------
# Model fallback chain for free-tier rate limits
GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash"
]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured.")
    
    try:
        system_instruction = (
            "You are a highly optimized AI assistant designed to minimize token usage and avoid unnecessary verbosity.\n\n"
            "=====================\nGLOBAL RULES\n============\n"
            "* Be concise. No filler text.\n"
            "* Do NOT repeat user input.\n"
            "* Use bullet points or JSON when possible.\n"
            "* Only answer what is asked.\n\n"
            "=====================\nCONTEXT CONTROL (SMART)\n=======================\n"
            "* Resume and Job Description (JD) are OPTIONAL context.\n"
            "* Use them ONLY if:\n"
            "  1. They are provided in the current request, OR\n"
            "  2. The user explicitly asks about resume/job matching.\n"
            "* If the user asks general questions (e.g., \"how to improve resume\"):\n"
            "  → Answer normally WITHOUT requiring context.\n"
            "* If the user asks about match/analysis but NO resume/JD is provided:\n"
            "  → Respond: \"Please provide resume and job description for analysis.\"\n"
            "* NEVER assume or reuse old resume/JD automatically.\n\n"
            "=====================\nINPUT OPTIMIZATION\n==================\n"
            "If resume or JD is provided:\n"
            "* Extract ONLY: skills, tools, experience (years/roles), keywords\n"
            "* Ignore long descriptions.\n\n"
            "=====================\nOUTPUT RULES (MATCHING)\n=======================\n"
            "Return ONLY JSON:\n"
            "{\n\"match_score\": number,\n\"matched_skills\": [],\n\"missing_skills\": [],\n\"improvement_suggestions\": []\n}\n"
            "* Max 5 suggestions\n* Each suggestion < 10 words\n\n"
            "=====================\nCHAT MODE\n=========\n"
            "* Keep answers under 50 words\n* Give actionable advice only\n* No long explanations\n\n"
            "=====================\nFAIL-SAFE\n=========\n"
            "If input too large:\n\"INPUT_TOO_LARGE: Please summarize input.\""
        )
        
        # Convert history to Gemini format
        gemini_history = []
        
        # Inject resume/JD context as the first exchange if provided
        if request.context and len(request.history) == 0:
            gemini_history.append({
                "role": "user",
                "parts": [f"Here is my context for this conversation:\n\n{request.context}\n\nPlease keep this in mind for all my questions."]
            })
            gemini_history.append({
                "role": "model",
                "parts": ["Got it! I've reviewed your resume, the job description, and your match results. I'll tailor all my advice to your specific situation. How can I help you?"]
            })

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
        
        # Construct prompt
        final_prompt = request.message
        if request.context and len(request.history) > 0:
            final_prompt = f"Context (resume & job description):\n{request.context}\n\nUser question: {request.message}"

        # Try each model in the fallback chain
        last_error = None
        for model_name in GEMINI_MODELS:
            try:
                gemini_model = genai.GenerativeModel(
                    model_name,
                    system_instruction=system_instruction
                )
                chat = gemini_model.start_chat(history=gemini_history)
                response = safe_gemini_call(chat.send_message, final_prompt)
                return ChatResponse(response=response.text)
            except Exception as model_err:
                error_str = str(model_err)
                last_error = model_err
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    print(f"⚠️ Rate limited on {model_name}, trying next model...")
                    continue
                else:
                    # Non-rate-limit error, don't try other models
                    raise model_err
        
        # All models exhausted
        raise HTTPException(
            status_code=429, 
            detail="Free-tier API quota exceeded for all models. Please wait a minute and try again."
        )
    except HTTPException:
        # Re-raise already formatted HTTPExceptions (like the 429 above)
        raise
    except Exception as e:
        print(f"Error in /chat: {e}")
        # Return a more descriptive error for debugging if needed, or keeping it generic
        raise HTTPException(status_code=500, detail=f"Gemini Error: {str(e)}")

# ---------------- Main ----------------
if __name__ == "__main__":
    import uvicorn
    # Use reload=False to avoid import errors with direct script execution
    uvicorn.run(app, host="0.0.0.0", port=8000)
