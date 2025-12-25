import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(r"d:\College\Extra\Practice\Projects\Resume and Job Description Matcher\python_backend\.env")
load_dotenv(env_path)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("No API key found")
    exit(1)

genai.configure(api_key=api_key)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
