import os
import random
import json
import pandas as pd
from faker import Faker

# --- 1. CONFIGURATION ---
NUM_RESUMES = 200
NUM_JDS = 500
DATASET_ROOT = 'dataset_clean'
SEED = 42 # For reproducibility
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

# --- 3. HELPER FUNCTIONS ---

def generate_skills(primary_category_skills):
    """Generates a mix of tech and soft skills, prioritizing the primary category."""
    
    # 3-5 primary tech skills
    tech_primary = random.sample(primary_category_skills, k=random.randint(3, 5))
    
    # 2-4 other tech skills
    other_tech = [s for s in TECH_SKILLS if s not in tech_primary]
    tech_other = random.sample(other_tech, k=random.randint(2, 4))
    
    # 3-4 soft skills
    soft = random.sample(COMMON_SKILLS, k=random.randint(3, 4))
    
    return tech_primary + tech_other, soft

def get_jd_primary_skills(job_title):
    """Maps a job title to its primary skill set."""
    for category, skills in JOB_CATEGORIES.items():
        if job_title.startswith(category):
            return skills
    return random.sample(TECH_SKILLS, k=random.randint(5, 8)) # Fallback

def create_directory_structure():
    """Creates the necessary folder structure, including the new 'metadata' folder."""
    os.makedirs(os.path.join(DATASET_ROOT, 'resumes'), exist_ok=True)
    os.makedirs(os.path.join(DATASET_ROOT, 'jds'), exist_ok=True)
    # --- UPDATED: Create metadata folder ---
    os.makedirs(os.path.join(DATASET_ROOT, 'metadata'), exist_ok=True) 
    print(f"Created directory structure in: {DATASET_ROOT}/")

# --- 4. DATA GENERATION LOGIC ---

# Storage for generated data to be used in CSVs
all_resumes = []
all_jds = []

def generate_resumes():
    """Generates and saves unique resume files."""
    print(f"Generating {NUM_RESUMES} Resumes...")
    resume_category_keys = list(JOB_CATEGORIES.keys())
    
    for i in range(1, NUM_RESUMES + 1):
        resume_id = f"resume_{i:03d}.txt"
        
        # Determine the resume's focus/category
        category_key = random.choice(resume_category_keys)
        category_skills = JOB_CATEGORIES[category_key]
        
        tech_skills, soft_skills = generate_skills(category_skills)
        all_skills = tech_skills + soft_skills

        # Generate unique content
        summary = fake.paragraph(nb_sentences=4, variable_nb_sentences=True)
        
        projects = []
        for _ in range(random.randint(2, 3)):
            project_title = fake.catch_phrase()
            project_desc = fake.sentence(nb_words=15)
            projects.append(f"{project_title}: {project_desc}")

        experience = []
        for _ in range(random.randint(2, 4)):
            job_title = fake.job()
            company = fake.company()
            start_year = random.randint(2015, 2022)
            end_year = start_year + random.randint(1, 3)
            if end_year > 2024: end_year = 'Present'
            desc = fake.sentence(nb_words=20)
            experience.append(f"{job_title} at {company} ({start_year} - {end_year})\n\t- {desc}")

        education = f"{fake.random_element(['M.S.', 'B.S.', 'Ph.D.'])}, {fake.random_element(['Computer Science', 'Data Science', 'Software Engineering', 'Electrical Engineering'])}, {random.randint(2018, 2024)}"

        # Assemble the resume text
        resume_content = f"""
SUMMARY: {summary}

SKILLS: {', '.join(all_skills)}

PROJECTS:
{'\n'.join([f'* {p}' for p in projects])}

EXPERIENCE:
{'\n'.join([f'* {e}' for e in experience])}

EDUCATION:
{education}
"""
        
        # Save file
        filepath = os.path.join(DATASET_ROOT, 'resumes', resume_id)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(resume_content.strip())
            
        # Store for labeling
        all_resumes.append({
            'id': resume_id,
            'skills': all_skills,
            'category': category_key
        })

def generate_jds():
    """Generates and saves unique job description files."""
    print(f"Generating {NUM_JDS} Job Descriptions...")
    job_titles = list(JOB_CATEGORIES.keys())

    for i in range(1, NUM_JDS + 1):
        jd_id = f"jd_{i:03d}.txt"
        
        # Determine job category and skills
        job_category = random.choice(job_titles)
        primary_skills = get_jd_primary_skills(job_category)
        
        required_tech = random.sample(primary_skills, k=random.randint(5, 7))
        nice_to_have_tech = [s for s in random.sample(TECH_SKILLS, k=4) if s not in required_tech]
        
        required_soft = random.sample(COMMON_SKILLS, k=random.randint(2, 3))
        nice_to_have_soft = [s for s in random.sample(COMMON_SKILLS, k=2) if s not in required_soft]

        all_required_skills = required_tech + required_soft
        all_nice_to_have = nice_to_have_tech + nice_to_have_soft
        
        # Generate unique content
        title = f"{job_category} ({fake.random_element(['Senior', 'Mid-Level', 'Junior'])})"
        experience = f"{random.randint(2, 10)}+ Years"
        location = fake.random_element(['Remote', 'On-site', 'Hybrid'])

        responsibilities = [fake.sentence(nb_words=12) for _ in range(random.randint(4, 6))]
        
        # Assemble the JD text
        jd_content = f"""
Title: {title}
Experience: {experience}
Location: {location}

Responsibilities:
{'\n'.join([f'* {r}' for r in responsibilities])}

Required Skills:
{'\n'.join([f'* {s}' for s in all_required_skills])}

Nice to Have:
{'\n'.join([f'* {s}' for s in all_nice_to_have])}
"""
        
        # Save file
        filepath = os.path.join(DATASET_ROOT, 'jds', jd_id)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(jd_content.strip())
            
        # Store for labeling
        all_jds.append({
            'id': jd_id,
            'required_skills': all_required_skills,
            'category': job_category
        })

def generate_skill_files():
    """Generates the JSON files for skills and saves them in the metadata folder."""
    print("Generating skill JSON files into metadata/...")
    
    # Tech Skills JSON
    # --- UPDATED PATH: Saves to dataset/metadata/ ---
    tech_path = os.path.join(DATASET_ROOT, 'metadata', 'skills_tech.json')
    with open(tech_path, 'w', encoding='utf-8') as f:
        json.dump(TECH_SKILLS, f, indent=4)
        
    # Common Skills JSON
    # --- UPDATED PATH: Saves to dataset/metadata/ ---
    common_path = os.path.join(DATASET_ROOT, 'metadata', 'skills_common.json')
    with open(common_path, 'w', encoding='utf-8') as f:
        json.dump(COMMON_SKILLS, f, indent=4)
        
def calculate_match_score(resume_skills, jd_required, jd_nice_to_have):
    """Calculates a simple score based on skill overlap for labeling."""
    
    # Set for faster lookup
    resume_skills_set = set(resume_skills)
    
    # Core Match: overlap with Required Skills (weighted higher)
    required_overlap = len(resume_skills_set.intersection(set(jd_required)))
    
    # Bonus Match: overlap with Nice to Have Skills (weighted lower)
    nice_to_have_overlap = len(resume_skills_set.intersection(set(jd_nice_to_have)))
    
    # Max possible required overlap (for normalization)
    max_required_skills = len(jd_required)
    
    # Heuristic: 
    # High Match (Label 1) if:
    # 1. Category matches AND > 50% of required skills are present.
    # OR 
    # 2. > 70% of required skills are present (cross-category high match).
    
    required_ratio = required_overlap / max_required_skills if max_required_skills > 0 else 0
    
    # A simple threshold for '1' or '0'
    if required_ratio >= 0.7:
        return 1 # Very strong match
    
    # A moderate match can also be labeled '1' with some probability
    if required_ratio >= 0.5 and random.random() < 0.6:
        return 1 # Moderate match with 60% chance of '1' label
    
    return 0 # Low or No match

def generate_match_csvs():
    """Generates the labeled and unlabeled match CSV files and saves them in the metadata folder."""
    print("Generating match_pairs CSV files into metadata/...")
    
    match_pairs_labeled = []
    match_pairs_unlabeled = []
    
    # Create all possible pairs (200 * 500 = 100,000 pairs)
    for resume in all_resumes:
        for jd in all_jds:
            resume_id = resume['id']
            jd_id = jd['id']
            
            # Re-generate the JD's skill set based on its category for consistent labeling logic
            jd_category = jd['category']
            primary_skills = get_jd_primary_skills(jd_category)
            required_skills_jd = random.sample(primary_skills, k=random.randint(5, 7))
            nice_to_have_jd = [s for s in random.sample(TECH_SKILLS, k=4) if s not in required_skills_jd]

            # Determine the label
            label = calculate_match_score(resume['skills'], required_skills_jd, nice_to_have_jd)
            
            # Add to lists
            match_pairs_labeled.append({
                'resume_id': resume_id,
                'jd_id': jd_id,
                'label': label
            })
            
            match_pairs_unlabeled.append({
                'resume_id': resume_id,
                'jd_id': jd_id
            })

    # Create DataFrames
    df_labeled = pd.DataFrame(match_pairs_labeled)
    df_unlabeled = pd.DataFrame(match_pairs_unlabeled)

    # Save CSVs
    # --- UPDATED PATH: Saves to dataset/metadata/ ---
    df_labeled.to_csv(os.path.join(DATASET_ROOT, 'metadata', 'match_pairs_labeled.csv'), index=False)
    # --- UPDATED PATH: Saves to dataset/metadata/ ---
    df_unlabeled.to_csv(os.path.join(DATASET_ROOT, 'metadata', 'match_pairs_unlabeled.csv'), index=False)
    print(f"Generated {len(df_labeled)} labeled pairs (Total pairs: {NUM_RESUMES * NUM_JDS}).")
    
# --- 5. EXECUTION ---

def main():
    create_directory_structure()
    generate_resumes()
    generate_jds()
    generate_skill_files()
    # CSV generation relies on the data stored during resume and JD creation
    generate_match_csvs()
    
    print("\n✅ Dataset generation complete!")
    print(f"Total files generated: {NUM_RESUMES + NUM_JDS + 4}")
    print(f"Find all files in the '{DATASET_ROOT}/' directory.")

if __name__ == '__main__':
    main()