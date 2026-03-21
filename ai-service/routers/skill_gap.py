"""
routers/skill_gap.py
POST /analyze/skill-gap
Compares student's current skills against role requirements,
returns gap breakdown with curated course recommendations.
"""

import logging
from fastapi import APIRouter
from schemas import SkillGapRequest, SkillGapResponse, SkillEntry, CourseRecommendation
from prediction import ROLE_SKILLS

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── COURSE LIBRARY ──────────────────────────────────────────────────────────
COURSE_LIBRARY = {
    "system design": CourseRecommendation(
        skill_name="System Design",
        course_name="Grokking the System Design Interview",
        platform="Educative.io",
        url="https://educative.io/courses/grokking-the-system-design-interview",
        duration="3 weeks",
        priority="CRITICAL",
    ),
    "aws": CourseRecommendation(
        skill_name="AWS / Cloud",
        course_name="AWS Certified Solutions Architect – Associate",
        platform="AWS Training",
        url="https://aws.amazon.com/training/",
        duration="2 weeks",
        priority="CRITICAL",
    ),
    "kubernetes": CourseRecommendation(
        skill_name="Kubernetes",
        course_name="Kubernetes for Beginners",
        platform="YouTube (TechWorld with Nana)",
        url="https://youtube.com/watch?v=X48VuDVv0do",
        duration="2 weeks",
        priority="HIGH",
    ),
    "docker": CourseRecommendation(
        skill_name="Docker",
        course_name="Docker & Kubernetes: The Practical Guide",
        platform="Udemy",
        url="https://udemy.com/course/docker-kubernetes-the-practical-guide",
        duration="1 week",
        priority="MEDIUM",
    ),
    "machine learning": CourseRecommendation(
        skill_name="Machine Learning",
        course_name="Machine Learning Specialization",
        platform="Coursera (Andrew Ng)",
        url="https://coursera.org/specializations/machine-learning-introduction",
        duration="4 weeks",
        priority="HIGH",
    ),
    "deep learning": CourseRecommendation(
        skill_name="Deep Learning",
        course_name="Deep Learning Specialization",
        platform="Coursera",
        url="https://coursera.org/specializations/deep-learning",
        duration="5 weeks",
        priority="HIGH",
    ),
    "sql": CourseRecommendation(
        skill_name="Advanced SQL",
        course_name="SQL for Data Analysis",
        platform="Mode Analytics",
        url="https://mode.com/sql-tutorial",
        duration="1 week",
        priority="HIGH",
    ),
    "dsa": CourseRecommendation(
        skill_name="Data Structures & Algorithms",
        course_name="DSA Master Course",
        platform="LeetCode + Striver's Sheet",
        url="https://takeuforward.org/strivers-a2z-dsa-course",
        duration="6 weeks",
        priority="CRITICAL",
    ),
    "react": CourseRecommendation(
        skill_name="React",
        course_name="React – The Complete Guide",
        platform="Udemy",
        url="https://udemy.com/course/react-the-complete-guide-incl-redux",
        duration="2 weeks",
        priority="MEDIUM",
    ),
    "spring boot": CourseRecommendation(
        skill_name="Spring Boot",
        course_name="Spring Boot Microservices",
        platform="YouTube (Java Brains)",
        url="https://youtube.com/c/JavaBrainsChannel",
        duration="2 weeks",
        priority="HIGH",
    ),
    "python": CourseRecommendation(
        skill_name="Python",
        course_name="Python Bootcamp",
        platform="Udemy",
        url="https://udemy.com/course/complete-python-bootcamp",
        duration="2 weeks",
        priority="MEDIUM",
    ),
    "ci/cd": CourseRecommendation(
        skill_name="CI/CD Pipelines",
        course_name="GitHub Actions – The Complete Guide",
        platform="Udemy",
        url="https://udemy.com/course/github-actions-the-complete-guide",
        duration="1 week",
        priority="HIGH",
    ),
}

# Skill level requirements per role (0–100)
ROLE_LEVEL_REQUIREMENTS = {
    "SDE": {
        "java": 80, "dsa": 90, "system design": 85, "spring boot": 75,
        "sql": 80, "react": 65, "git": 70, "aws": 70, "docker": 60,
        "kubernetes": 55, "ci/cd": 55,
    },
    "Data Scientist": {
        "python": 90, "machine learning": 85, "deep learning": 75,
        "sql": 85, "pandas": 80, "statistics": 80, "tensorflow": 70,
    },
    "DevOps": {
        "docker": 90, "kubernetes": 85, "aws": 85, "ci/cd": 90,
        "linux": 80, "python": 70, "ansible": 65, "terraform": 65,
    },
}


def estimate_current_level(skill: str, student_skills: list[str]) -> int:
    """Rough estimate of current proficiency level based on skill presence."""
    skill_lower = skill.lower()
    student_lower = [s.lower() for s in student_skills]
    if skill_lower in student_lower:
        return 65  # assume intermediate if listed
    for s in student_lower:
        if skill_lower in s or s in skill_lower:
            return 40  # partial match = beginner
    return 5  # not in resume


@router.post("/skill-gap", response_model=SkillGapResponse)
def analyze_skill_gap(req: SkillGapRequest):
    logger.info(f"Analyzing skill gap for student {req.student_id}, target role: {req.target_role}")
    target_role = req.target_role or "SDE"
    required_skills = ROLE_SKILLS.get(target_role, ROLE_SKILLS["SDE"])
    level_reqs = ROLE_LEVEL_REQUIREMENTS.get(target_role, {})

    student_lower = [s.lower() for s in req.current_skills]

    missing_skills = []
    critical_skills = []
    skill_entries = []
    recommended_courses = []

    for skill in required_skills:
        current_level = estimate_current_level(skill, req.current_skills)
        required_level = level_reqs.get(skill, 70)

        gap = required_level - current_level

        if gap > 50:
            priority = "CRITICAL"
        elif gap > 30:
            priority = "HIGH"
        elif gap > 15:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        skill_entries.append(SkillEntry(
            skill_name=skill.title(),
            current_level=current_level,
            required_level=required_level,
            priority=priority,
        ))

        if current_level < 30:
            missing_skills.append(skill.title())
            if priority == "CRITICAL":
                critical_skills.append(skill.title())

            # Add course recommendation if available
            course = COURSE_LIBRARY.get(skill.lower())
            if course and skill.title() not in [c.skill_name for c in recommended_courses]:
                recommended_courses.append(course)

    # Calculate gap score (0 = no gap, 1 = completely missing)
    total_gap = sum(
        max(0, level_reqs.get(s, 70) - estimate_current_level(s, req.current_skills))
        for s in required_skills
    )
    max_possible_gap = len(required_skills) * 95
    gap_score = round(total_gap / max(max_possible_gap, 1), 3)

    # Rough time estimate: 1 week per 10 gap points per skill
    estimated_weeks = min(int(gap_score * 20) + 2, 26)

    res = SkillGapResponse(
        missing_skills=missing_skills,
        critical_skills=critical_skills,
        skill_entries=skill_entries,
        recommended_courses=recommended_courses[:6],  # top 6
        gap_score=gap_score,
        estimated_weeks=estimated_weeks,
    )
    logger.info(f"Skill gap analysis complete. Found {len(skill_entries)} entries.")
    return res
