import os
import random
import json
import pandas as pd
from faker import Faker

# --- 1. CONFIGURATION ---
NUM_RESUMES = 200
NUM_JDS = 500
DATASET_ROOT = 'dataset'
SEED = 42

random.seed(SEED)
Faker.seed(SEED)
fake = Faker()

# --- 2. SKILL DEFINITIONS ---
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

# --- 3. REALISTIC GENERATION HELPERS ---

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

METRICS = ["latency", "accuracy", "memory usage", "processing speed"]

def noisy(text):
    """Add realistic noise: typos, casing, spacing."""
    if random.random() < 0.25:
        text = text.replace("e", "3")
    if random.random() < 0.25:
        text += random.choice([".", "..", "..."])
    if random.random() < 0.2:
        text = text.upper()
    if random.random() < 0.1:
        text = text.lower()
    return text

def generate_skills(primary_category_skills):
    tech_primary = random.sample(primary_category_skills, k=random.randint(3, 5))
    other_tech = [s for s in TECH_SKILLS if s not in tech_primary]
    tech_other = random.sample(other_tech, k=random.randint(2, 4))
    soft = random.sample(COMMON_SKILLS, k=random.randint(3, 4))
    return tech_primary + tech_other, soft

def get_jd_primary_skills(job_title):
    for category, skills in JOB_CATEGORIES.items():
        if job_title.startswith(category):
            return skills
    return random.sample(TECH_SKILLS, k=random.randint(5, 8))

def sentence_with_skills(skills):
    verb = random.choice(ACTION_VERBS)
    used = random.sample(skills, k=min(2, len(skills)))
    return f"{verb} solutions using {', '.join(used)} in production environments."

def generate_resume_bullets(category_skills):
    bullets = []
    for _ in range(random.randint(4, 7)):
        verb = random.choice(ACTION_VERBS)
        tech = random.sample(category_skills, k=min(2, len(category_skills)))
        metric = random.choice(METRICS)
        value = random.randint(10, 60)
        bullet = f"{verb} systems using {', '.join(tech)}, improving {metric} by {value}%."
        bullets.append(noisy(bullet))
    return bullets

def generate_projects(category_skills):
    projects = []
    for _ in range(random.randint(2, 4)):
        tech1, tech2 = random.sample(category_skills, 2)
        project_type = random.choice(PROJECT_TYPES)
        cloud = random.choice(["AWS", "Azure", "GCP"])
        metric = random.choice(METRICS)
        value = random.randint(10, 70)
        component = random.choice(["pipeline", "API", "model"])
        text = random.choice(PROJECT_TEMPLATES).format(
            tech1=tech1, tech2=tech2, project_type=project_type,
            cloud=cloud, metric=metric, value=value, component=component
        )
        projects.append(noisy(text))
    return projects

# --- 4. DIRECTORY SETUP ---
def create_directory_structure():
    os.makedirs(os.path.join(DATASET_ROOT, 'resumes'), exist_ok=True)
    os.makedirs(os.path.join(DATASET_ROOT, 'jds'), exist_ok=True)
    os.makedirs(os.path.join(DATASET_ROOT, 'metadata'), exist_ok=True)
    print(f"Created directory structure in: {DATASET_ROOT}/")

# --- 5. DATA STORAGE ---
all_resumes = []
all_jds = []

# --- 6. RESUME GENERATOR (REALISTIC) ---
def generate_resumes():
    print(f"Generating {NUM_RESUMES} Realistic Resumes...")
    
    resume_categories = list(JOB_CATEGORIES.keys())
    
    for i in range(1, NUM_RESUMES + 1):
        resume_id = f"resume_{i:03d}.txt"
        category_key = random.choice(resume_categories)
        category_skills = JOB_CATEGORIES[category_key]

        tech_skills, soft_skills = generate_skills(category_skills)
        all_skills = tech_skills + soft_skills

        summary = noisy(fake.paragraph(nb_sentences=3))
        bullets = generate_resume_bullets(category_skills)
        projects = generate_projects(category_skills)

        experience_section = ""
        for _ in range(random.randint(2, 4)):
            job_title = fake.job()
            company = fake.company()
            start_year = random.randint(2014, 2021)
            end_year = start_year + random.randint(1, 4)
            end_year = end_year if end_year <= 2024 else "Present"

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

        resume_text = f"""
SUMMARY:
{summary}

SKILLS:
{', '.join(all_skills)}

PROJECTS:
{chr(10).join(['* ' + p for p in projects])}

EXPERIENCE:
{experience_section}

EDUCATION:
{education}
"""

        filepath = os.path.join(DATASET_ROOT, 'resumes', resume_id)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(resume_text.strip())

        all_resumes.append({
            "id": resume_id,
            "skills": all_skills,
            "category": category_key
        })

# --- 7. JOB DESCRIPTION GENERATOR ---
def generate_jds():
    print(f"Generating {NUM_JDS} Realistic JDs...")
    job_titles = list(JOB_CATEGORIES.keys())

    for i in range(1, NUM_JDS + 1):
        jd_id = f"jd_{i:03d}.txt"
        
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
"""

        filepath = os.path.join(DATASET_ROOT, 'jds', jd_id)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(jd_text.strip())

        all_jds.append({
            "id": jd_id,
            "required_skills": required_tech + required_soft,
            "category": job_category
        })

# --- 8. SKILL JSON EXPORT ---
def generate_skill_files():
    print("Generating skill JSONs...")
    with open(os.path.join(DATASET_ROOT, 'metadata', 'skills_tech.json'), 'w') as f:
        json.dump(TECH_SKILLS, f, indent=4)
    with open(os.path.join(DATASET_ROOT, 'metadata', 'skills_common.json'), 'w') as f:
        json.dump(COMMON_SKILLS, f, indent=4)

# --- 9. MATCH SCORE GENERATOR ---
def calculate_match_score(resume_skills, jd_required, jd_nice_to_have):
    resume_set = set(resume_skills)
    required_overlap = len(resume_set.intersection(jd_required))
    nice_overlap = len(resume_set.intersection(jd_nice_to_have))
    required_ratio = required_overlap / len(jd_required)
    
    if required_ratio >= 0.7:
        return 1
    if required_ratio >= 0.5 and random.random() < 0.6:
        return 1
    return 0

# --- 10. MATCH CSV EXPORT ---
def generate_match_csvs():
    print("Generating match CSV files...")
    
    labeled = []
    unlabeled = []

    for resume in all_resumes:
        for jd in all_jds:
            resume_id = resume['id']
            jd_id = jd['id']

            primary_skills = get_jd_primary_skills(jd['category'])
            required_skills = random.sample(primary_skills, k=random.randint(5, 7))
            nice_to_have = random.sample(TECH_SKILLS, 4)

            label = calculate_match_score(resume['skills'], required_skills, nice_to_have)

            labeled.append({
                "resume_id": resume_id,
                "jd_id": jd_id,
                "label": label
            })

            unlabeled.append({
                "resume_id": resume_id,
                "jd_id": jd_id
            })

    pd.DataFrame(labeled).to_csv(os.path.join(DATASET_ROOT, 'metadata', 'match_pairs_labeled.csv'), index=False)
    pd.DataFrame(unlabeled).to_csv(os.path.join(DATASET_ROOT, 'metadata', 'match_pairs_unlabeled.csv'), index=False)

    print(f"Generated {len(labeled)} labeled pairs.")

# --- 11. MAIN EXECUTION ---
def main():
    create_directory_structure()
    generate_resumes()
    generate_jds()
    generate_skill_files()
    generate_match_csvs()
    
    print("\n✅ Dataset generation complete.")
    print(f"Total files: {NUM_RESUMES + NUM_JDS + 4}")

if __name__ == '__main__':
    main()
