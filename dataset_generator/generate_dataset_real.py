"""
Comprehensive dataset generator:
- Produces TXT + PDF resumes and JDs
- Adds synonym / paraphrase noise
- Produces duplicate resume variants
- Produces badly formatted resumes and some with missing SKILLS section
- Keeps metadata and labeled/unlabeled match CSVs for training
- Configurable via top constants

"""

import os
import random
import json
import re
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
from faker import Faker

# PDF libraries (try reportlab first, then fpdf)
PDF_ENGINE = None
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter
    PDF_ENGINE = 'reportlab'
except Exception:
    try:
        from fpdf import FPDF
        PDF_ENGINE = 'fpdf'
    except Exception:
        PDF_ENGINE = None

# ---------------- CONFIGURATION ----------------
NUM_RESUMES = 200
NUM_JDS = 500
DATASET_ROOT = 'dataset_real'
SEED = 42

GENERATE_PDF = True   # We've chosen A (both TXT + PDF)
DUPLICATE_VARIANTS_PER_RESUME = (0, 2)  # inclusive random range of duplicates
BAD_FORMAT_PROB = 0.18  # probability each resume will be badly formatted
MISSING_SKILLS_PROB = 0.08  # probability to omit SKILLS section entirely
SYNONYM_INJECTION_PROB = 0.35  # chance of injecting synonym/paraphrase noise in sentences
PARAPHRASE_RATIO = 0.15  # percent of resume sentences to paraphrase
INCLUDE_TXT_COPY = True

random.seed(SEED)
Faker.seed(SEED)
fake = Faker()

# ---------------- BASE SKILLS & TEMPLATES ----------------
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

# ---------------- SYNONYMS / PARAPHRASE DICTIONARY ----------------
# small handcrafted mapping for synonyms & paraphrases
SYNONYMS = {
    "Developed": ["Built", "Created", "Engineered"],
    "Designed": ["Architected", "Outlined", "Specified"],
    "Implemented": ["Executed", "Built and deployed", "Realized"],
    "Optimized": ["Improved", "Tuned", "Refined"],
    "Led": ["Managed", "Spearheaded", "Coordinated"],
    "Automated": ["Scripted", "Streamlined", "Programmed automation for"],
    "Improved": ["Enhanced", "Increased", "Boosted"],
    "Integrated": ["Combined", "Linked", "Merged"],
    "Tested": ["Validated", "Verified"],
    "Debugged": ["Troubleshot", "Resolved issues in"]
}

PARAPHRASE_PATTERNS = [
    # simple paraphrase patterns using format placeholders: {verb}, {tech}, {what}
    "{verb} solutions using {tech} in production environments.",
    "Worked on {tech} to {verb_lower} critical systems and services.",
    "Responsible for {verb_lower} and maintaining systems built with {tech}.",
    "Worked closely with stakeholders to {verb_lower} {tech}-based solutions."
]

# ---------------- HELPERS ----------------
def ensure_dirs():
    dirs = [
        os.path.join(DATASET_ROOT, 'resumes'),
        os.path.join(DATASET_ROOT, 'jds'),
        os.path.join(DATASET_ROOT, 'metadata'),
        os.path.join(DATASET_ROOT, 'parsed')
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def noisy(text, intensity=0.25):
    """Add realistic noise: typos, casing, spacing, random punctuation."""
    t = text
    # minor random char flips / substitutions
    if random.random() < intensity * 0.4:
        t = t.replace("e", "3", 1)
    if random.random() < intensity * 0.2:
        t = t.replace("a", "@", 1)
    # punctuation
    if random.random() < intensity * 0.25:
        t += random.choice([".", "..", "...", ""])
    # random case
    r = random.random()
    if r < intensity * 0.1:
        t = t.upper()
    elif r < intensity * 0.15:
        t = t.lower()
    # stray spaces
    if random.random() < intensity * 0.08:
        t = "  " + t
    return t

def inject_synonyms(text):
    """Replace verbs or short phrases with synonyms randomly."""
    # word-by-word naive substitution for keys in SYNONYMS
    for k, v in SYNONYMS.items():
        if k in text and random.random() < SYNONYM_INJECTION_PROB:
            repl = random.choice(v)
            text = text.replace(k, repl, 1)
    return text

def paraphrase_sentence(sentence, skills):
    """Return a paraphrased sentence using patterns and random verbs/skills."""
    if random.random() > PARAPHRASE_RATIO:
        return sentence
    verb = random.choice(ACTION_VERBS)
    verb_lower = verb.lower()
    tech_sample = ', '.join(random.sample(skills, k=min(2, len(skills))))
    pattern = random.choice(PARAPHRASE_PATTERNS)
    return pattern.format(verb=verb, verb_lower=verb_lower, tech=tech_sample)

def badly_format_text(text):
    """Introduce line-break noise, random bullet symbols, missing headers, etc."""
    lines = text.splitlines()
    out_lines = []
    for line in lines:
        # randomly break lines
        if random.random() < 0.18 and len(line) > 20:
            # split at a random space
            idx = random.randint(10, len(line)-10)
            # find nearest space
            sp = line.find(' ', idx)
            if sp != -1:
                out_lines.append(line[:sp])
                out_lines.append("   " + line[sp+1:])
                continue
        # random bullet replacement
        if line.strip().startswith(('-', '*')) and random.random() < 0.25:
            line = line.replace('-', random.choice(['--', '->', '•', '♦']), 1)
        # random uppercase
        if random.random() < 0.06:
            line = line.upper()
        # drop some punctuation
        if random.random() < 0.05:
            line = re.sub(r'[.,;:]', '', line)
        out_lines.append(line)
    # sometimes remove headers
    if random.random() < 0.25:
        out = "\n".join(out_lines)
        out = re.sub(r'^(SUMMARY:|SKILLS:|PROJECTS:|EXPERIENCE:|EDUCATION:)\n', '', out, flags=re.MULTILINE)
        return out
    return "\n".join(out_lines)

def write_pdf_from_text(filepath_pdf, text):
    """Write PDF using available engine. If none installed, print message."""
    if not GENERATE_PDF:
        return False
    if PDF_ENGINE == 'reportlab':
        try:
            styles = getSampleStyleSheet()
            doc = SimpleDocTemplate(filepath_pdf, pagesize=letter)
            story = []
            for para in text.split('\n\n'):
                p = Paragraph(re.sub(r'\n', '<br/>', para), styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 6))
            doc.build(story)
            return True
        except Exception as e:
            print("reportlab PDF write error:", e)
            return False
    elif PDF_ENGINE == 'fpdf':
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=12)
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            for line in text.splitlines():
                # ensure we wrap if line too long
                pdf.multi_cell(0, 6, txt=line)
            pdf.output(filepath_pdf)
            return True
        except Exception as e:
            print("fpdf PDF write error:", e)
            return False
    else:
        print("No PDF engine available (install reportlab or fpdf). PDFs skipped.")
        return False

# ---------------- GENERATORS ----------------
all_resumes = []
all_jds = []
generated_files = []

def get_jd_primary_skills(job_title):
    for category, skills in JOB_CATEGORIES.items():
        if job_title.startswith(category):
            return skills
    # fallback
    return random.sample(TECH_SKILLS, k=random.randint(5, 8))

def generate_skills(primary_category_skills):
    tech_primary = random.sample(primary_category_skills, k=random.randint(3, 5))
    other_tech = [s for s in TECH_SKILLS if s not in tech_primary]
    tech_other = random.sample(other_tech, k=random.randint(2, 4))
    soft = random.sample(COMMON_SKILLS, k=random.randint(3, 4))
    return tech_primary + tech_other, soft

def sentence_with_skills(skills):
    verb = random.choice(ACTION_VERBS)
    used = random.sample(skills, k=min(2, len(skills)))
    return f"{verb} solutions using {', '.join(used)} in production environments."

def generate_resume_bullets(category_skills, n_bullets=None):
    bullets = []
    n = n_bullets if n_bullets is not None else random.randint(4, 7)
    for _ in range(n):
        verb = random.choice(ACTION_VERBS)
        tech = random.sample(category_skills, k=min(2, len(category_skills)))
        metric = random.choice(METRICS)
        value = random.randint(10, 60)
        bullet = f"{verb} systems using {', '.join(tech)}, improving {metric} by {value}%."
        # possibly inject synonyms
        bullet = inject_synonyms(bullet) if random.random() < SYNONYM_INJECTION_PROB else bullet
        bullets.append(noisy(bullet))
    return bullets

def generate_projects(category_skills, n_projects=None):
    projects = []
    n = n_projects if n_projects is not None else random.randint(2, 4)
    for _ in range(n):
        tech1, tech2 = random.sample(category_skills, 2) if len(category_skills) >= 2 else random.sample(TECH_SKILLS, 2)
        project_type = random.choice(PROJECT_TYPES)
        cloud = random.choice(["AWS", "Azure", "GCP"])
        metric = random.choice(METRICS)
        value = random.randint(10, 70)
        component = random.choice(["pipeline", "API", "model"])
        text = random.choice(PROJECT_TEMPLATES).format(
            tech1=tech1, tech2=tech2, project_type=project_type,
            cloud=cloud, metric=metric, value=value, component=component
        )
        # paraphrase sometimes
        text = inject_synonyms(text) if random.random() < SYNONYM_INJECTION_PROB else text
        projects.append(noisy(text))
    return projects

def generate_resumes():
    print(f"Generating {NUM_RESUMES} Realistic Resumes...")
    resume_categories = list(JOB_CATEGORIES.keys())

    for i in range(1, NUM_RESUMES + 1):
        resume_id_base = f"resume_{i:03d}"
        resume_id_txt = resume_id_base + ".txt"

        category_key = random.choice(resume_categories)
        category_skills = JOB_CATEGORIES[category_key]

        tech_skills, soft_skills = generate_skills(category_skills)
        all_skills = tech_skills + soft_skills

        # summary
        summary = noisy(fake.paragraph(nb_sentences=3))
        # bullets & projects
        bullets = generate_resume_bullets(category_skills)
        projects = generate_projects(category_skills)

        # experience
        experience_section = ""
        for _ in range(random.randint(2, 4)):
            job_title = fake.job()
            company = fake.company()
            start_year = random.randint(2014, 2021)
            end_year = start_year + random.randint(1, 4)
            end_year = end_year if end_year <= datetime.now().year else "Present"

            exp_bullets = "\n".join(
                f"{random.choice(['-', '*', '•', '->'])} {sentence_with_skills(all_skills)}"
                for __ in range(random.randint(2, 4))
            )

            block = f"""{job_title} at {company} ({start_year} - {end_year})
{exp_bullets}

"""
            experience_section += noisy(block)

        education = (
            f"{fake.random_element(['B.Tech', 'M.Tech', 'M.S.', 'B.S.'])} in "
            f"{fake.random_element(['Computer Science', 'Data Science', 'Software Engineering'])}, "
            f"{random.randint(2016, 2024)}"
        )

        # Construct core resume text
        resume_blocks = {
            "SUMMARY:": summary,
            "SKILLS:": ", ".join(all_skills),
            "PROJECTS:": "\n".join(['* ' + p for p in projects]),
            "EXPERIENCE:": experience_section.strip(),
            "EDUCATION:": education
        }

        # Possibly remove SKILLS header to create missing-skills resumes
        skills_missing = random.random() < MISSING_SKILLS_PROB

        # Compose text with optional paraphrase injection per-sentence
        composed_sections = []
        for header, body in resume_blocks.items():
            if header == "SKILLS:" and skills_missing:
                continue
            # paraphrase some sentences in summary / projects
            if header in ("SUMMARY:", "PROJECTS:", "EXPERIENCE:"):
                # paraphrase at sentence granularity
                sentences = re.split(r'(?<=[.!?])\s+', body)
                for sidx, s in enumerate(sentences):
                    if s.strip() == "":
                        continue
                    # paraphrase some sentences
                    if random.random() < PARAPHRASE_RATIO:
                        s_new = paraphrase_sentence(s, all_skills)
                        sentences[sidx] = s_new
                    else:
                        sentences[sidx] = inject_synonyms(s) if random.random() < SYNONYM_INJECTION_PROB else s
                body = " ".join(sentences)
            composed_sections.append(header)
            composed_sections.append(body)

        resume_text = "\n\n".join(composed_sections).strip()

        # Bad formatting noise
        is_bad = random.random() < BAD_FORMAT_PROB
        if is_bad:
            resume_text = badly_format_text(resume_text)

        # Save txt
        file_txt_path = os.path.join(DATASET_ROOT, 'resumes', resume_id_txt)
        with open(file_txt_path, 'w', encoding='utf-8') as f:
            f.write(resume_text)
        generated_files.append(file_txt_path)

        # Save parsed copy (same as txt for now) to parsed/
        parsed_path = os.path.join(DATASET_ROOT, 'parsed', resume_id_txt)
        with open(parsed_path, 'w', encoding='utf-8') as f:
            f.write(resume_text)
        generated_files.append(parsed_path)

        # Save PDF
        file_pdf_path = os.path.join(DATASET_ROOT, 'resumes', resume_id_base + ".pdf")
        wrote_pdf = False
        if GENERATE_PDF:
            wrote_pdf = write_pdf_from_text(file_pdf_path, resume_text)
            if wrote_pdf:
                generated_files.append(file_pdf_path)

        # Save metadata entry
        all_resumes.append({
            "id": resume_id_txt,
            "skills": all_skills,
            "category": category_key,
            "badly_formatted": bool(is_bad),
            "missing_skills": bool(skills_missing),
            "pdf": wrote_pdf
        })

        # Create duplicate variants (if any)
        n_dupes = random.randint(*DUPLICATE_VARIANTS_PER_RESUME)
        for d in range(n_dupes):
            variant_suffix = f"_v{d+1}"
            variant_id_txt = resume_id_base + variant_suffix + ".txt"
            # Make a small variation: swap two skills, alter a project, or alter company name
            variant_text = resume_text
            # small tweak: swap two skills in skills list (if present)
            if "," in resume_blocks.get("SKILLS:", ""):
                # quick shuffle in the skills string occurrence
                variant_text = re.sub(r'([A-Za-z0-9\.\+#\-\s]+,\s*)([A-Za-z0-9\.\+#\-\s]+)', lambda m: m.group(2) + ", " + m.group(1).strip(), variant_text, count=1)
            # minor additional noise
            variant_text = noisy(variant_text, intensity=0.18)
            # randomly more bad formatting
            if random.random() < 0.45:
                variant_text = badly_format_text(variant_text)
            # write variant txt and PDF
            vtxt_path = os.path.join(DATASET_ROOT, 'resumes', variant_id_txt)
            with open(vtxt_path, 'w', encoding='utf-8') as f:
                f.write(variant_text)
            generated_files.append(vtxt_path)
            vpdf_path = os.path.join(DATASET_ROOT, 'resumes', resume_id_base + variant_suffix + ".pdf")
            if GENERATE_PDF:
                if write_pdf_from_text(vpdf_path, variant_text):
                    generated_files.append(vpdf_path)
            # Append metadata
            all_resumes.append({
                "id": variant_id_txt,
                "skills": all_skills,
                "category": category_key,
                "badly_formatted": True,
                "missing_skills": False,
                "pdf": GENERATE_PDF
            })

    print(f"Generated {len([r for r in all_resumes if r['id'].endswith('.txt')])} resume TXT records (plus duplicates).")

def generate_jds():
    print(f"Generating {NUM_JDS} Realistic JDs...")
    job_titles = list(JOB_CATEGORIES.keys())

    for i in range(1, NUM_JDS + 1):
        jd_id_base = f"jd_{i:03d}"
        jd_id_txt = jd_id_base + ".txt"

        job_category = random.choice(job_titles)
        primary_skills = get_jd_primary_skills(job_category)

        required_tech = random.sample(primary_skills, k=random.randint(5, 7))
        required_soft = random.sample(COMMON_SKILLS, k=random.randint(2, 4))
        nice_to_have = random.sample(TECH_SKILLS, 4)

        responsibilities = []
        for _ in range(random.randint(5, 8)):
            verb = random.choice(ACTION_VERBS)
            tech = random.sample(primary_skills, k=min(2, len(primary_skills)))
            sentence = f"{verb} {fake.sentence(nb_words=8)} using {', '.join(tech)}."
            # inject synonyms sometimes
            sentence = inject_synonyms(sentence) if random.random() < SYNONYM_INJECTION_PROB else sentence
            responsibilities.append(noisy(sentence))

        jd_text = f"""
Title: {job_category} ({fake.random_element(['Senior', 'Junior', 'Lead', 'Associate'])})
Experience: {random.randint(1, 8)}+ years
Location: {fake.random_element(['Remote', 'Bangalore', 'Hyderabad', 'Pune', 'Gurgaon', 'Chennai', 'Delhi'])}

Responsibilities:
{chr(10).join(['- ' + r for r in responsibilities])}

Required Skills:
{chr(10).join(['* ' + s for s in required_tech + required_soft])}

Nice to Have:
{chr(10).join(['* ' + s for s in nice_to_have])}
""".strip()

        # Occasionally make JD slightly messy (to emulate real world)
        if random.random() < 0.12:
            jd_text = badly_format_text(jd_text)

        # Write txt
        path_txt = os.path.join(DATASET_ROOT, 'jds', jd_id_txt)
        with open(path_txt, 'w', encoding='utf-8') as f:
            f.write(jd_text)
        generated_files.append(path_txt)

        # PDF
        path_pdf = os.path.join(DATASET_ROOT, 'jds', jd_id_base + ".pdf")
        wrote_pdf = False
        if GENERATE_PDF:
            wrote_pdf = write_pdf_from_text(path_pdf, jd_text)
            if wrote_pdf:
                generated_files.append(path_pdf)

        all_jds.append({
            "id": jd_id_txt,
            "required_skills": required_tech + required_soft,
            "category": job_category,
            "pdf": wrote_pdf
        })

    print(f"Generated {len(all_jds)} JDs.")

def generate_skill_files():
    print("Generating skill JSONs...")
    with open(os.path.join(DATASET_ROOT, 'metadata', 'skills_tech.json'), 'w', encoding='utf-8') as f:
        json.dump(TECH_SKILLS, f, indent=4)
    with open(os.path.join(DATASET_ROOT, 'metadata', 'skills_common.json'), 'w', encoding='utf-8') as f:
        json.dump(COMMON_SKILLS, f, indent=4)

def calculate_match_score(resume_skills, jd_required, jd_nice_to_have):
    resume_set = set([s.strip().lower() for s in resume_skills])
    required_set = set([s.strip().lower() for s in jd_required])
    nice_set = set([s.strip().lower() for s in jd_nice_to_have])

    required_overlap = len(resume_set.intersection(required_set))
    nice_overlap = len(resume_set.intersection(nice_set))
    required_ratio = required_overlap / len(required_set) if len(required_set) else 0

    # simple labeling heuristics: mimic earlier behaviour but a bit richer
    if required_ratio >= 0.7:
        return 1
    if required_ratio >= 0.5 and random.random() < 0.6:
        return 1
    # occasional positives due to many nice-to-have overlaps
    if nice_overlap >= 3 and random.random() < 0.15:
        return 1
    return 0

def extract_skills_from_resume_text(text):
    """Simple skill extraction by matching known TECH + COMMON keywords (case-insensitive)."""
    found = set()
    t = text.lower()
    for sk in TECH_SKILLS + COMMON_SKILLS:
        if sk.lower() in t:
            found.add(sk)
    return list(found)

def generate_match_csvs():
    print("Generating match CSV files...")
    labeled = []
    unlabeled = []

    # iterate resumes and jds
    for resume in all_resumes:
        # read actual resume text to get extracted skills
        resume_path = os.path.join(DATASET_ROOT, 'resumes', resume['id'])
        try:
            with open(resume_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            # might be a variant stored elsewhere; fallback to metadata skills
            text = ""
        resume_skills_extracted = extract_skills_from_resume_text(text) if text else resume.get('skills', [])

        for jd in all_jds:
            primary_skills = get_jd_primary_skills(jd['category'])
            required_skills = random.sample(primary_skills, k=random.randint(5, 7))
            nice_to_have = random.sample(TECH_SKILLS, 4)
            label = calculate_match_score(resume_skills_extracted, required_skills, nice_to_have)

            labeled.append({
                "resume_id": resume['id'],
                "jd_id": jd['id'],
                "label": label
            })

            unlabeled.append({
                "resume_id": resume['id'],
                "jd_id": jd['id']
            })

    # Save CSVs
    labeled_path = os.path.join(DATASET_ROOT, 'metadata', 'match_pairs_labeled.csv')
    unlabeled_path = os.path.join(DATASET_ROOT, 'metadata', 'match_pairs_unlabeled.csv')
    pd.DataFrame(labeled).to_csv(labeled_path, index=False)
    pd.DataFrame(unlabeled).to_csv(unlabeled_path, index=False)

    print(f"Generated {len(labeled)} labeled pairs.")

def save_metadata():
    # resumes metadata
    with open(os.path.join(DATASET_ROOT, 'metadata', 'resumes_metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(all_resumes, f, indent=2)
    # jds metadata
    with open(os.path.join(DATASET_ROOT, 'metadata', 'jds_metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(all_jds, f, indent=2)

# ---------------- MAIN ----------------
def main():
    print("Starting full dataset generation (TXT + PDF) with noise and variants...")
    ensure_dirs()
    # clean previous files if any (optional)
    # shutil.rmtree(DATASET_ROOT, ignore_errors=True); ensure_dirs()

    generate_resumes()
    generate_jds()
    generate_skill_files()
    generate_match_csvs()
    save_metadata()

    total_files = sum(len(files) for _, _, files in os.walk(DATASET_ROOT))
    print("\n✅ Dataset generation complete.")
    print(f"Dataset root: {os.path.abspath(DATASET_ROOT)}")
    print(f"Total metadata entries - resumes: {len([r for r in all_resumes if r['id'].endswith('.txt')])}, jds: {len(all_jds)}")
    print(f"Total files on disk (approx): {total_files}")
    if PDF_ENGINE is None and GENERATE_PDF:
        print("\n⚠️  PDF engine not found. Install `reportlab` or `fpdf` to enable PDF output:")
        print("    pip install reportlab")
        print("or: pip install fpdf")
    print("You can now start EDA on dataset/parsed/ and metadata CSVs.")

if __name__ == '__main__':
    main()
