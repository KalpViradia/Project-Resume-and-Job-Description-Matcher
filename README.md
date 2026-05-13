# AI Resume & Job Matcher

A powerful full-stack application that leverages AI to match resumes with job descriptions, providing detailed analysis, skill matching, and an intelligent chat assistant to help candidates improve their profiles.

## 🚀 Features

- **Smart Matching**: Uses Sentence-BERT (BERT) embeddings and Cosine Similarity for precise semantic matching between resumes and job descriptions.
- **AI Analysis**: Powered by Google's Gemini AI to provide qualitative feedback, missing skills analysis, and actionable improvement suggestions.
- **Resume Comparison**: Compare two different resumes against a single job description to find the best candidate for the role.
- **Contextual Chat Assistant**: An intelligent career assistant that remembers your match results to provide tailored interview prep and profile optimization advice.
- **Branding & UI**: Modern, responsive dark-mode interface with custom branding, logo, and a seamless user experience.
- **Match History**: Securely store and review past matches with full analysis reports.
- **Robust API**: Integrated exponential backoff and rate-limit handling for reliable Gemini AI interactions.
- **PDF Export**: Generate and download professional PDF match reports.

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16 (React 19)
- **Styling**: Tailwind CSS v4, Framer Motion
- **Components**: Shadcn UI (Radix Primitives)
- **Utilities**: `jspdf`, `canvas-confetti`, `react-markdown`

### Backend (Node.js)
- **Runtime**: Node.js & Express
- **Database**: PostgreSQL (via Neon)
- **ORM**: Prisma
- **Auth**: JWT & BCrypt

### AI Engine (Python)
- **API**: FastAPI & Uvicorn
- **LLM**: Google Generative AI (Gemini Pro)
- **Embeddings**: Sentence-Transformers (BERT)
- **Parsing**: `pypdf`, `python-docx`
- **NLP**: NLTK, Pandas, NumPy

## 📊 Performance & Scale

### AI / NLP Engine
| Metric | Value |
|--------|-------|
| Embedding Model | all-mpnet-base-v2 (109M params, 768-d vectors) |
| Embedding Vectors | 700 (200 resumes + 500 JDs) |
| Skill Taxonomy | 59 skills (47 technical + 12 soft) |
| Similarity Metric | Cosine similarity on L2-normalized embeddings |
| LLM Integration | Gemini 1.5 Flash + 2.0 Flash (2-model failover) |
| Skill Extraction | Hybrid (LLM-primary + regex fallback) |
| Rate-Limit Handling | Exponential backoff (2^n sec, 3 retries) |

### Data Pipeline
| Metric | Value |
|--------|-------|
| Total Dataset Files | 4,134 across 4 variants (clean, messy, real, noisy PDF) |
| Pipeline Stages | 5 (Extract → Clean → Tokenize → Skills → Embed) |
| Sentences Processed | 4,610+ (1,711 resume + 2,899 JD) |
| Cleaning Rules | 6 modular (unicode, whitespace, bullets, newlines, symbols, case) |
| Noise Types | 7 (typos, casing, spacing, unicode, missing sections, synonyms, bullets) |

### Architecture
| Metric | Value |
|--------|-------|
| API Endpoints | 8+ across FastAPI (AI) + Express (Auth/History) |
| Frontend Pages | 7 with 6 custom React components |
| Source Code | 5,700+ lines across 51 files |
| Database | PostgreSQL via Prisma ORM (2 models, UUID PKs) |
| Auth | JWT + BCrypt (salt rounds: 10) |

## 📂 Project Structure

```bash
├── resume-matcher-app/
│   ├── frontend/       # Next.js Application
│   └── backend/        # Node.js Auth & History API
├── ai-engine/     # FastAPI AI & Matching Engine
└── README.md
```

## ⚡ Getting Started

### Prerequisites
- Node.js & npm
- Python 3.9+
- PostgreSQL Database (Neon/Local)
- Google Gemini API Key

### 1. Setup Python AI Engine
```bash
cd ai-engine
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```
Create a `.env` file in `ai-engine/`:
```env
GEMINI_API_KEY=your_key_here
```
Run the server:
```bash
uvicorn main:app --reload --port 8000
```

### 2. Setup Node.js Backend
```bash
cd resume-matcher-app/backend
npm install
```
Create a `.env` file in `resume-matcher-app/backend/`:
```env
DATABASE_URL="postgresql://..."
JWT_SECRET="your_secret"
PORT=5000
```
Run the server:
```bash
npm run dev
```

### 3. Setup Frontend
```bash
cd resume-matcher-app/frontend
npm install
```
Run the client:
```bash
npm run dev
```

## 📝 Usage

1.  **Sign Up/Login**: Create an account to access the dashboard.
2.  **Dashboard**: Upload your Resume (PDF/DOCX) and paste the Job Description.
3.  **Analyze**: Click "Match" to get a score, missing skills list, and detailed report.
4.  **Chat**: Use the AI Assistant to ask specific questions about how to improve.
5.  **History**: View your past matches in the History tab.

## 📊 Dataset Generator

The project includes a robust synthetic dataset generation tool located in `dataset_generator/`. This tool creates realistic resume and job description data for training and testing the matching algorithms.

### Features
- **Multi-Format Output**: Generates both `.txt` and `.pdf` versions of resumes and JDs.
- **Realistic Content**: Uses `Faker` to generate full profiles including summaries, skills, projects, experience, and education.
- **Noise Injection**: Simulates real-world data issues by injecting typos, bad formatting, synonym variations, and missing sections.
- **Data Variants**: Creates duplicate versions of resumes with slight modifications to test robust matching.
- **Structured Metadata**: Automatically generates labeled and unlabeled match pair CSVs (`match_pairs_labeled.csv`) and JSON metadata for training.

### Usage
To generate a new dataset:
```bash
cd dataset_generator
# Install dependencies (if not already installed)
pip install faker pandas reportlab
# Run the generator
python generate_dataset_real.py
```
This will create a `dataset_real/` directory containing the generated resumes, JDs, and metadata.