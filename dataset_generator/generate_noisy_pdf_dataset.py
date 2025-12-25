"""
Generates a dataset of UNIQUE noisy PDFs (resumes + JDs) suitable for ATS-like pipelines:
- ONLY PDFs (no TXT/PDF duplicates)
- Each file intentionally noisy (typos, weird bullets, missing SKILLS, broken lines, unicode)
- Metadata saved (resumes_metadata.json, jds_metadata.json)
- Labeled + unlabeled match CSVs generated (using the internal skill lists used to generate PDFs)
- Configurable constants at top

"""

import os
import random
import json
import re
from datetime import datetime
from pathlib import Path
from faker import Faker
import pandas as pd
import sys

# Attempt PDF engines
PDF_ENGINE = None
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    PDF_ENGINE = 'reportlab'
except Exception:
    try:
        from fpdf import FPDF
        PDF_ENGINE = 'fpdf'
    except Exception:
        PDF_ENGINE = None

# ---------------- CONFIG ----------------
NUM_RESUMES = 200         # change to smaller value for quick tests
NUM_JDS = 500
DATASET_ROOT = "dataset_noisy_pdfs"
SEED = 42

# Behavior toggles
REQUIRED_PDF_ENGINE = True   # require PDF engine to run; script exits if missing
RANDOM_SEED = SEED

# Noise probabilities
BAD_FORMAT_PROB = 0.20
MISSING_SKILLS_PROB = 0.10
TYPO_PROB = 0.06
UNICODE_GARBAGE_PROB = 0.07
HEADER_VARIATION_PROB = 0.25
BULLET_VARIATION_PROB = 0.35

random.seed(RANDOM_SEED)
Faker = Faker
fake = Faker()
Faker.seed(RANDOM_SEED)

# ---------------- SKILLS / TEMPLATES ----------------
TECH_SKILLS = [
    "Python", "JavaScript", "Java", "C++", "Go", "TypeScript", "SQL", "NoSQL",
    "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Ansible",
    "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Spark",
    "CI/CD", "Git", "Jira", "Linux", "Shell Scripting", "Data Modeling",
    "REST API", "Microservices", "System Design", "HTML5", "CSS3", "PHP",
    "R", "Tableau", "Power BI", "Kafka", "RabbitMQ", "GraphQL", "Jenkins"
]

COMMON_SKILLS = [
    "Communication", "Leadership", "Teamwork", "Problem-Solving", "Adaptability",
    "Time Management", "Critical Thinking", "Creativity", "Attention to Detail",
    "Interpersonal Skills", "Project Management", "Mentorship"
]

JOB_CATEGORIES = {
    "Software Engineer": ["Python", "Java", "C++", "React", "Node.js", "Microservices", "System Design", "Docker", "AWS", "SQL"],
    "Data Scientist": ["Python", "R", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "SQL", "Data Modeling", "Tableau"],
    "Web Developer (Frontend)": ["JavaScript", "HTML5", "CSS3", "React", "Angular", "Vue.js", "TypeScript", "REST API", "Git"],
    "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Ansible", "CI/CD", "Linux", "Shell Scripting", "Jenkins"],
    "AI/ML Specialist": ["Python", "TensorFlow", "PyTorch", "Spark", "MLOps", "Deep Learning", "NLP", "Computer Vision", "AWS", "Go"]
}

ACTION_VERBS = [
    "Developed", "Built", "Designed", "Optimized", "Led", "Implemented",
    "Architected", "Deployed", "Refactored", "Automated", "Enhanced",
    "Improved", "Integrated", "Debugged", "Tested", "Analyzed"
]

PROJECT_TEMPLATES = [
    "Developed a {tech1}-based {project_type} improving {metric} by {value}%.",
    "Implemented an end-to-end {project_type} using {tech1}, {tech2}, deployed on {cloud}.",
    "Optimized {component} using {tech1}, reducing {metric} by {value}%.",
    "Built a scalable {project_type} leveraging {tech1} and {tech2}."
]

PROJECT_TYPES = [
    "ML model", "web application", "microservice", "analytics pipeline",
    "recommendation engine", "REST API", "dashboard", "automation tool"
]

METRICS = ["latency", "accuracy", "memory usage", "processing speed", "throughput"]

# Bullets & weird chars
BULLETS = ["-", "*", "•", "->", "→", "▪", "◦", "·", "—"]
UNICODE_GARBAGE = ["�", "©", "®", "✓", "✗", "★", "✦"]

# ---------------- UTILITIES ----------------
def ensure_dirs():
    folders = [
        os.path.join(DATASET_ROOT, "resumes_pdf"),
        os.path.join(DATASET_ROOT, "jds_pdf"),
        os.path.join(DATASET_ROOT, "metadata")
    ]
    for p in folders:
        os.makedirs(p, exist_ok=True)

def random_phone():
    # mixture of formats to simulate messy phone fields
    patterns = [
        lambda: f"+91-{random.randint(6000000000, 9999999999)}",
        lambda: f"{random.randint(6000000000, 9999999999)}",
        lambda: f"({random.randint(60,99)}) {random.randint(10000000,99999999)}",
        lambda: f"+1 ({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"
    ]
    return random.choice(patterns)()

def maybe_typo(word):
    if random.random() > TYPO_PROB:
        return word
    # simple typo strategies
    ops = random.choice(["swap", "drop", "repeat", "replace"])
    if ops == "swap" and len(word) > 2:
        i = random.randint(0, len(word)-2)
        lst = list(word)
        lst[i], lst[i+1] = lst[i+1], lst[i]
        return "".join(lst)
    if ops == "drop" and len(word) > 3:
        i = random.randint(0, len(word)-1)
        return word[:i] + word[i+1:]
    if ops == "repeat":
        i = random.randint(0, len(word)-1)
        return word[:i] + word[i] + word[i:]
    if ops == "replace":
        return re.sub(r'[aeiou]', lambda m: random.choice('aeiou'), word, count=1)
    return word

def noisy_sentence(s):
    # inject typos into some words
    ws = s.split()
    ws = [maybe_typo(w) for w in ws]
    s2 = " ".join(ws)
    # add unicode garbage sometimes
    if random.random() < UNICODE_GARBAGE_PROB:
        s2 += " " + random.choice(UNICODE_GARBAGE)
    # random spacing issues
    if random.random() < 0.12:
        s2 = s2.replace(" ", "  ")
    return s2

def build_skills_line(skills):
    if not skills:
        return ""  # missing SKILLS scenario
    # shuffle and join with inconsistent separators to simulate variations
    sep = random.choice([", ", " | ", "; ", " / "])
    skills_shuffled = skills[:]
    random.shuffle(skills_shuffled)
    return sep.join(skills_shuffled)

def make_random_header(name, title=None):
    # header variants to simulate inconsistent headings
    parts = []
    if random.random() < 0.5:
        parts.append(name.upper() if random.random() < 0.3 else name)
    else:
        parts.append(name)
    if title:
        if random.random() < 0.6:
            parts.append("—")
            parts.append(title)
    header = " ".join([str(x) for x in parts])
    # sometimes drop 'SUMMARY' or capitalize weirdly
    if random.random() < HEADER_VARIATION_PROB:
        header = header.replace("SUMMARY", "Sumry").replace("SKILLS", "Skills")
    return header

# ---------------- PDF WRITERS ----------------
def write_pdf_reportlab(path, content_lines):
    # content_lines: list of strings (each string is a text line / block)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    # register a simple TTF if available to improve unicode rendering - optional
    try:
        # attempt a widely available font, fall back silently
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        c.setFont('DejaVuSans', 10)
    except Exception:
        c.setFont("Helvetica", 10)

    x = 40
    y = height - 40
    line_height = 12
    for block in content_lines:
        # if block contains explicit newlines, split further
        for line in str(block).splitlines():
            if y < 60:
                c.showPage()
                try:
                    c.setFont('DejaVuSans', 10)
                except Exception:
                    c.setFont("Helvetica", 10)
                y = height - 40
            # draw
            try:
                c.drawString(x, y, line.strip())
            except Exception:
                # fallback: basic ascii
                c.drawString(x, y, re.sub(r'[^\x00-\x7F]+','', line).strip())
            y -= line_height
    c.save()

def write_pdf_fpdf(path, content_lines):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for block in content_lines:
        for line in str(block).splitlines():
            pdf.multi_cell(0, 6, txt=line)
    pdf.output(path)

def write_pdf(path, content_lines):
    if PDF_ENGINE == 'reportlab':
        write_pdf_reportlab(path, content_lines)
    elif PDF_ENGINE == 'fpdf':
        write_pdf_fpdf(path, content_lines)
    else:
        raise RuntimeError("No PDF engine available. Install reportlab or fpdf.")

# ---------------- CONTENT GENERATORS ----------------
def create_resume_content(name, category_skills, all_skills):
    """
    Returns a list of strings (blocks/lines) representing the resume content.
    Designed to be messy and varied.
    """
    blocks = []

    # Header (name + random role)
    role = fake.job() if random.random() < 0.6 else category_skills[0]
    header = make_random_header(name, role)
    blocks.append(header)
    # contact line with formatting variations
    email = fake.email()
    phone = random_phone()
    contacts = f"Email: {email}  |  Phone: {phone}"
    if random.random() < 0.22:
        # show phone first sometimes
        contacts = f"Phone: {phone}   Email: {email}"
    blocks.append(contacts)

    # Random short summary (noisy)
    summary = fake.paragraph(nb_sentences=2)
    blocks.append("SUMMARY:")
    blocks.append(noisy_sentence(summary))

    # Projects / bullets - variable bullet char
    blocks.append("PROJECTS:")
    nproj = random.randint(1, 4)
    for _ in range(nproj):
        bullet = random.choice(BULLETS)
        tech1 = random.choice(all_skills) if all_skills else random.choice(TECH_SKILLS)
        tech2 = random.choice(all_skills) if all_skills else random.choice(TECH_SKILLS)
        proj = random.choice(PROJECT_TEMPLATES).format(
            tech1=tech1, tech2=tech2, project_type=random.choice(PROJECT_TYPES),
            cloud=random.choice(["AWS", "Azure", "GCP"]), metric=random.choice(METRICS),
            value=random.randint(10, 80), component=random.choice(["pipeline", "API", "model"])
        )
        blocks.append(f"{bullet} {noisy_sentence(proj)}")

    # Maybe missing skills
    if random.random() > MISSING_SKILLS_PROB:
        blocks.append("SKILLS:")
        skills_line = build_skills_line(all_skills)
        blocks.append(skills_line)

    # Experience - mix of random job lines, sometimes broken
    blocks.append("EXPERIENCE:")
    for _ in range(random.randint(1, 3)):
        job = fake.job()
        comp = fake.company()
        start = random.randint(2013, 2019)
        end = start + random.randint(1, 5)
        end = end if end <= datetime.now().year else "Present"
        header_line = f"{job} at {comp} ({start} - {end})"
        if random.random() < 0.25:
            # break header across lines
            header_line = header_line[:len(header_line)//2] + "\n" + header_line[len(header_line)//2:]
        blocks.append(header_line)
        # bullets
        for __ in range(random.randint(1, 3)):
            bullet = random.choice(BULLETS) if random.random() < BULLET_VARIATION_PROB else "-"
            sentence = f"{random.choice(ACTION_VERBS)} using {random.choice(all_skills) if all_skills else random.choice(TECH_SKILLS)} to improve {random.choice(METRICS)}."
            blocks.append(f"{bullet} {noisy_sentence(sentence)}")

    # Education (sometimes messy)
    edu = f"{random.choice(['B.Tech','M.Tech','B.S.','M.S.'])} in {random.choice(['Computer Science','Data Science','Software Engineering'])}, {random.randint(2013, 2022)}"
    if random.random() < 0.15:
        edu = edu.replace(",", "")
    blocks.append("EDUCATION:")
    blocks.append(edu)

    # Occasionally add stray unicode or random header/footer noise
    if random.random() < UNICODE_GARBAGE_PROB:
        blocks.insert(0, random.choice(UNICODE_GARBAGE) + " PROFILE ")

    # Final minor formatting corruption: extra spaces, missing punctuation
    blocks = [b.replace(".", "") if random.random() < 0.08 else b for b in blocks]

    return blocks

def create_jd_content(job_category, required_skills):
    blocks = []
    title = f"{job_category} ({random.choice(['Senior','Junior','Lead','Associate'])})"
    blocks.append(title)
    loc_line = f"Location: {random.choice(['Remote','Bangalore','Hyderabad','Pune','Gurgaon','Chennai','Delhi'])}"
    blocks.append(loc_line)

    blocks.append("RESPONSIBILITIES:")
    for _ in range(random.randint(3, 7)):
        verb = random.choice(ACTION_VERBS)
        sentence = fake.sentence(nb_words=10)
        # sometimes include required skills in responsibilities
        if random.random() < 0.5 and required_skills:
            sentence += " using " + random.choice(required_skills)
        blocks.append(f"{random.choice(BULLETS)} {noisy_sentence(sentence)}")

    # required skills (sometimes messy separators)
    if random.random() > 0.12:
        blocks.append("REQUIRED SKILLS:")
        blocks.append(build_skills_line(required_skills))
    else:
        # missing required skills occasionally
        pass

    # nice to have
    nice_to_have = random.sample(TECH_SKILLS, k=4)
    if random.random() < 0.85:
        blocks.append("NICE TO HAVE:")
        blocks.append(build_skills_line(nice_to_have))

    # random footer noise
    if random.random() < 0.12:
        blocks.append("Apply at: " + fake.url())

    # minor punctuation loss
    blocks = [b.replace(".", "") if random.random() < 0.06 else b for b in blocks]

    return blocks

# ---------------- GENERATION & METADATA ----------------
resumes_metadata = []
jds_metadata = []
resume_pdf_paths = []
jd_pdf_paths = []

def generate_resumes(num):
    for i in range(1, num + 1):
        resume_id = f"resume_{i:03d}.pdf"
        path = os.path.join(DATASET_ROOT, "resumes_pdf", resume_id)

        # choose category and skills
        category = random.choice(list(JOB_CATEGORIES.keys()))
        primary = JOB_CATEGORIES[category]
        tech_primary = random.sample(primary, k=min(len(primary), random.randint(2, 5)))
        other_tech = [s for s in TECH_SKILLS if s not in tech_primary]
        tech_other = random.sample(other_tech, k=random.randint(0, 3))
        soft = random.sample(COMMON_SKILLS, k=random.randint(1, 3))
        skills_used = tech_primary + tech_other + soft

        name = fake.name()
        content_blocks = create_resume_content(name, primary, skills_used)

        # apply overall bad-format mutation sometimes
        if random.random() < BAD_FORMAT_PROB:
            # insert random line breaks or remove section headers
            if random.random() < 0.5:
                # remove SKILLS heading if present
                content_blocks = [b for b in content_blocks if not b.strip().upper().startswith("SKILLS")]
            # add a broken line
            content_blocks.insert(random.randint(1, len(content_blocks)-1), " ".join([fake.word() for _ in range(6)]))

        # write PDF
        write_pdf(path, content_blocks)

        # metadata
        meta = {
            "id": resume_id,
            "path": path,
            "name": name,
            "category": category,
            "skills_generated": skills_used,
            "badly_formatted": random.random() < BAD_FORMAT_PROB,
            "missing_skills_prob": random.random() < MISSING_SKILLS_PROB
        }
        resumes_metadata.append(meta)
        resume_pdf_paths.append(path)

def generate_jds(num):
    for i in range(1, num + 1):
        jd_id = f"jd_{i:03d}.pdf"
        path = os.path.join(DATASET_ROOT, "jds_pdf", jd_id)

        category = random.choice(list(JOB_CATEGORIES.keys()))
        primary = JOB_CATEGORIES[category]
        required_skills = random.sample(primary, k=random.randint(3, min(6, len(primary))))

        content_blocks = create_jd_content(category, required_skills)
        # occasionally mess up JD layout
        if random.random() < 0.12:
            content_blocks.insert(0, "NOTE: " + fake.sentence(nb_words=6))
        write_pdf(path, content_blocks)

        meta = {
            "id": jd_id,
            "path": path,
            "category": category,
            "required_skills": required_skills
        }
        jds_metadata.append(meta)
        jd_pdf_paths.append(path)

# Label generation (use internal skill lists, not PDF text)
def calculate_match_score(resume_skills, jd_required, jd_nice):
    resume_set = set(s.lower() for s in resume_skills)
    req_set = set(s.lower() for s in jd_required)
    nice_set = set(s.lower() for s in jd_nice)

    req_overlap = len(resume_set.intersection(req_set))
    req_ratio = req_overlap / len(req_set) if req_set else 0

    if req_ratio >= 0.7:
        return 1
    if req_ratio >= 0.5 and random.random() < 0.6:
        return 1
    # occasional positive due to many nice overlaps
    nice_overlap = len(resume_set.intersection(nice_set))
    if nice_overlap >= 3 and random.random() < 0.15:
        return 1
    return 0

def generate_match_csvs():
    labeled = []
    unlabeled = []
    for r in resumes_metadata:
        resume_id = r["id"]
        resume_skills = r.get("skills_generated", [])
        for j in jds_metadata:
            jd_id = j["id"]
            primary_skills = j.get("required_skills", [])
            # create random required sampling to simulate variability
            required_skills = random.sample(primary_skills, k=min(len(primary_skills), random.randint(2, max(2, len(primary_skills)))))
            nice_to_have = random.sample(TECH_SKILLS, 4)
            label = calculate_match_score(resume_skills, required_skills, nice_to_have)
            labeled.append({"resume_id": resume_id, "jd_id": jd_id, "label": label})
            unlabeled.append({"resume_id": resume_id, "jd_id": jd_id})
    df_l = pd.DataFrame(labeled)
    df_u = pd.DataFrame(unlabeled)
    df_l.to_csv(os.path.join(DATASET_ROOT, "metadata", "match_pairs_labeled.csv"), index=False)
    df_u.to_csv(os.path.join(DATASET_ROOT, "metadata", "match_pairs_unlabeled.csv"), index=False)
    print(f"Saved labeled pairs: {len(df_l)}")

# ---------------- MAIN ----------------
def main():
    print("Starting noisy PDF-only dataset generation...")
    if REQUIRED_PDF_ENGINE and PDF_ENGINE is None:
        print("ERROR: No PDF engine found. Please install one of:")
        print("    pip install reportlab")
        print("or  pip install fpdf")
        sys.exit(1)

    ensure_dirs()
    print(f"Using PDF engine: {PDF_ENGINE}")

    # Generate
    print("Generating resumes ...")
    generate_resumes(NUM_RESUMES)
    print("Generating JDs ...")
    generate_jds(NUM_JDS)

    # Save skill lists
    with open(os.path.join(DATASET_ROOT, "metadata", "skills_tech.json"), "w", encoding="utf-8") as f:
        json.dump(TECH_SKILLS, f, indent=2)
    with open(os.path.join(DATASET_ROOT, "metadata", "skills_common.json"), "w", encoding="utf-8") as f:
        json.dump(COMMON_SKILLS, f, indent=2)

    # Save metadata JSON files
    with open(os.path.join(DATASET_ROOT, "metadata", "resumes_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(resumes_metadata, f, indent=2)
    with open(os.path.join(DATASET_ROOT, "metadata", "jds_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(jds_metadata, f, indent=2)

    # Generate labeled/unlabeled CSVs
    print("Generating match CSVs ...")
    generate_match_csvs()

    # summary
    total_files = len(resume_pdf_paths) + len(jd_pdf_paths)
    print("\n✅ Done.")
    print(f"Dataset root: {os.path.abspath(DATASET_ROOT)}")
    print(f"Resumes (PDF): {len(resume_pdf_paths)}")
    print(f"JDs (PDF): {len(jd_pdf_paths)}")
    print(f"Metadata saved to: {os.path.join(DATASET_ROOT, 'metadata')}")
    print("Next: run PDF extraction (pdfminer / PyPDF2 / tika) -> cleaning -> unified parsed corpus for EDA / model training.")

if __name__ == "__main__":
    main()
