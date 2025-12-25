# AI Resume & Job Matcher

A powerful full-stack application that leverages AI to match resumes with job descriptions, providing detailed analysis, skill matching, and an intelligent chat assistant to help candidates improve their profiles.

## 🚀 Features

- **Smart Matching**: Uses BERT embeddings and Cosine Similarity to calculate a precise match score between your resume and a job description.
- **AI Analysis**: Powered by Google's Gemini AI to provide qualitative feedback, missing skills analysis, and improvement tips.
- **General Chat Assistant**: A helpful AI assistant that answers general career and resume-related questions (Note: Does not have context of your specific match).
- **Match History**: Keeps track of all your past matches and scores.
- **Authentication**: Secure JWT-based signup and login system.
- **Modern UI**: Built with Next.js, Tailwind CSS, and Shadcn UI for a sleek, responsive dark-mode interface.
- **PDF Export**: Download detailed match reports as PDF.

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