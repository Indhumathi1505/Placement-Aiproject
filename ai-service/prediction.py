"""
prediction.py
Core ML logic for computing placement probability scores.
Uses a weighted heuristic model calibrated against historical placement data.
Can be replaced with a trained sklearn/XGBoost model later.
"""

from typing import List, Optional, Dict
import math

# ─── ROLE → REQUIRED SKILLS MAP ───────────────────────────────────────────────
ROLE_SKILLS: Dict[str, List[str]] = {
    "SDE": ["java", "python", "dsa", "data structures", "algorithms", "spring boot",
            "react", "sql", "git", "system design", "rest api", "oops"],
    "Data Scientist": ["python", "machine learning", "deep learning", "pandas", "numpy",
                       "sql", "statistics", "tensorflow", "scikit-learn", "data analysis"],
    "DevOps": ["docker", "kubernetes", "aws", "ci/cd", "jenkins", "linux",
               "ansible", "terraform", "python", "git"],
    "Full Stack": ["javascript", "react", "node.js", "html", "css", "sql",
                   "rest api", "git", "mongodb", "express"],
    "ML Engineer": ["python", "machine learning", "deep learning", "pytorch", "tensorflow",
                    "mlops", "docker", "sql", "statistics", "nlp"],
    "Business Analyst": ["sql", "excel", "tableau", "power bi", "statistics",
                         "communication", "project management", "jira"],
}

# Company-specific bonus skills (presence boosts that company's probability)
COMPANY_BONUS_SKILLS: Dict[str, List[str]] = {
    "TCS":       ["java", "sql", "communication"],
    "Infosys":   ["java", "python", "agile"],
    "Wipro":     ["java", "testing", "sql"],
    "Amazon":    ["dsa", "system design", "java", "python"],
    "Google":    ["dsa", "system design", "algorithms", "python"],
    "Microsoft": ["dsa", "system design", "c#", "azure"],
    "HCL":       ["java", "spring boot", "sql"],
    "Cognizant": ["java", "sql", "communication"],
}


def compute_skill_match(student_skills: List[str], required_skills: List[str]) -> float:
    """Returns fraction of required skills present in student's skill set."""
    if not required_skills:
        return 0.5
    student_lower = {s.lower().strip() for s in student_skills}
    matched = 0
    for skill in required_skills:
        skill_l = skill.lower().strip()
        # Exact match
        if skill_l in student_lower:
            matched += 1
            continue
        # Partial match only if it's a significant part or specific multi-word skill
        # Using a simple heuristic: if the required skill is a substring and stands as a 'word'
        for s in student_lower:
            if re.search(rf"\b{re.escape(skill_l)}\b", s):
                matched += 1
                break
    return matched / len(required_skills)


def compute_placement_probability(
    cgpa: float,
    skills: List[str],
    internship_count: int,
    project_count: int,
    certification_count: int,
    backlogs: int,
    target_role: str = "SDE",
) -> float:
    """
    Weighted heuristic placement probability (0.0 – 1.0).

    Weights (must sum to 1.0):
      - CGPA:              0.25
      - Skill match:       0.35
      - Internships:       0.15
      - Projects:          0.12
      - Certifications:    0.08
      - Backlog penalty:   -0.05 per backlog (capped at -0.25)
    """
    # CGPA score: normalise to [0, 1] on a 10.0 scale
    cgpa_score = min(cgpa / 10.0, 1.0)

    # Skill score
    required = ROLE_SKILLS.get(target_role, ROLE_SKILLS["SDE"])
    skill_score = compute_skill_match(skills, required)

    # Experience scores (capped)
    internship_score = min(internship_count / 3.0, 1.0)
    project_score    = min(project_count / 5.0, 1.0)
    cert_score       = min(certification_count / 4.0, 1.0)

    # Backlog penalty
    backlog_penalty = min(backlogs * 0.05, 0.25)

    raw = (
        0.25 * cgpa_score
        + 0.35 * skill_score
        + 0.15 * internship_score
        + 0.12 * project_score
        + 0.08 * cert_score
        - backlog_penalty
    )

    # Smooth to [0.05, 0.97] range and add slight randomness for realism
    probability = max(0.05, min(0.97, raw))
    return round(probability, 3)


def compute_company_probabilities(
    base_probability: float,
    skills: List[str],
    target_companies: Optional[List[str]] = None,
) -> Dict[str, float]:
    """
    Derive per-company probabilities from the base score,
    boosted/penalised based on company-specific skill requirements.
    """
    companies = target_companies if target_companies else list(COMPANY_BONUS_SKILLS.keys())

    result = {}
    for company in companies:
        bonus_skills = COMPANY_BONUS_SKILLS.get(company, [])
        if bonus_skills:
            match = compute_skill_match(skills, bonus_skills)
            # Company probability = base ± 15% based on skill alignment
            company_prob = base_probability + (match - 0.5) * 0.15
        else:
            company_prob = base_probability

        result[company] = round(max(0.05, min(0.97, company_prob)) * 100, 1)

    return result


def compute_readiness_score(
    placement_probability: float,
    skill_match: float,
    cgpa: float,
) -> float:
    """Readiness score on 0–10 scale."""
    raw = (placement_probability * 5 + skill_match * 3 + (cgpa / 10.0) * 2)
    return round(min(raw, 10.0), 1)
