import re
import os
import logging
import requests
import json
from typing import List, Dict, Optional
from fastapi import APIRouter
from schemas import ResumeAnalysisRequest, ResumeAnalysisResponse
from prediction import (
    compute_placement_probability,
    compute_company_probabilities,
    compute_readiness_score,
    ROLE_SKILLS,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
HF_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.2",
    "HuggingFaceH4/zephyr-7b-beta",
    "meta-llama/Meta-Llama-3-8B-Instruct"
]
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models"

# ─── SKILL KEYWORD BANKS (Improved Regex Ready) ──────────────────────────────
# We use keys that are specific enough for word-boundary matching
ALL_KNOWN_SKILLS = [
    # Languages
    "java", "python", "javascript", "typescript", "c\\+\\+", "c#", "go", "rust", "kotlin", "ruby", "php", "swift", "scala", "dart", "r", "julia", "lua",
    # Frameworks & Libraries
    "spring boot", "spring", "django", "fastapi", "flask", "express", "node\\.js", "nestjs", "laravel", "ruby on rails", "asp\\.net",
    "react", "angular", "vue", "next\\.js", "svelte", "html", "css", "tailwind", "bootstrap", "sass", "less", "redux", "jquery",
    "tensorflow", "pytorch", "scikit-learn", "keras", "pandas", "numpy", "matplotlib", "seaborn", "opencv", "nltk", "spacy",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "oracle", "firebase", "sqlite", "mariadb", "neo4j",
    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ansible", "cloud native", "serverless", "lambda", "ec2", "s3",
    "git", "github", "gitlab", "ci/cd", "jenkins", "github actions", "circleci", "travis ci", "bitbucket",
    # Mobile & Game Dev
    "flutter", "react native", "android", "ios", "unity", "unreal engine",
    # Core CS & Tools
    "dsa", "data structures", "algorithms", "system design", "rest api", "graphql", "grpc", "soap",
    "machine learning", "deep learning", "nlp", "computer vision", "reinforcement learning",
    "sql", "nosql", "junit", "mockito", "selenium", "pytest", "jest", "mocha", "chai",
    "maven", "gradle", "linux", "bash", "shell scripting", "unix", "powershell",
    "microservices", "kafka", "rabbitmq", "activemq", "mqtt",
    "jwt", "oauth", "oops", "object oriented programming", "design patterns", "agile", "scrum", "kanban",
    "snowflake", "apache spark", "hadoop", "bi", "data engineering", "cypress", "playwright", "postman",
]

ATS_KEYWORDS = [
    "experience", "skills", "education", "projects", "certifications",
    "internship", "objective", "summary", "achievements", "references",
]

def extract_cgpa(text: str) -> float:
    """Extract CGPA from resume text using regex."""
    # Matches patterns like "CGPA: 8.23", "CGPA- 8.5", "8.23/10", "8.23 CGPA"
    patterns = [
        r"cgpa[:\-\s]+(\d\.\d{1,2})",
        r"(\d\.\d{1,2})\s*cgpa",
        r"(\d\.\d{1,2})\s*/\s*10"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                if 0 <= val <= 10:
                    return val
            except ValueError:
                continue
    return 7.5 # Default fallback

def extract_skills_from_text(text: str) -> List[str]:
    """Extracted skills using word boundaries for higher accuracy."""
    text_lower = text.lower()
    extracted = []
    for skill in ALL_KNOWN_SKILLS:
        # Handle start boundary
        has_symbol_start = re.search(r'^[^a-zA-Z0-9]', skill)
        start_boundary = r"(?<!\w)" if has_symbol_start else r"\b"
        
        # Handle end boundary
        has_symbol_end = re.search(r'[^a-zA-Z0-9]$', skill)
        end_boundary = r"(?!\w)" if has_symbol_end else r"\b"
        
        pattern = rf"(?i){start_boundary}{skill}{end_boundary}"
            
        if re.search(pattern, text_lower):
            # Clean up the display name (remove escape backslashes)
            display_name = skill.replace("\\", "")
            extracted.append(display_name)
    return list(set(extracted))

def score_ats(text: str, extracted_skills: List[str]) -> int:
    text_lower = text.lower()
    section_score = sum(10 for kw in ATS_KEYWORDS if re.search(rf"\b{kw}\b", text_lower))
    length_score = min(len(text) // 200, 20)
    keyword_density = min(len(extracted_skills) * 4, 30)
    return min(section_score + length_score + keyword_density, 100)

def score_resume(extracted_skills: List[str], target_role: str, text_length: int) -> int:
    required = ROLE_SKILLS.get(target_role, ROLE_SKILLS["SDE"])
    skill_match = len(set(s.lower() for s in extracted_skills) & 
                       set(s.lower() for s in required)) / max(len(required), 1)
    length_bonus = min(text_length // 300, 20)
    return min(int(skill_match * 65) + length_bonus + 15, 100)

def call_huggingface_model(model_id: str, prompt: str, token: str) -> Optional[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 1024, "temperature": 0.2, "return_full_text": False}
    }
    endpoint = f"{HF_INFERENCE_URL}/{model_id}"
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=45)
    resp.raise_for_status()
    output = resp.json()
    
    # Handle both list and dict response formats from HF Inference API
    if isinstance(output, list) and output:
        text = output[0].get('generated_text', '')
    else:
        text = output.get('generated_text', '')
        
    if not text:
        return None
        
    res = {
        "ats_score": 75, 
        "strengths": "", 
        "weaknesses": "", 
        "missing_keywords": "", 
        "suggestions": "", 
        "optimized_bullets": "",
        "extracted_skills": []
    }
    
    score_match = re.search(r"ATS Score:\s*(\d+)", text, re.IGNORECASE)
    if score_match:
        res["ats_score"] = int(score_match.group(1))

    def get_section(name, next_name=None):
        pattern = f"{name}:(.*?)(?:{next_name}:|$)" if next_name else f"{name}:(.*)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    res["strengths"] = get_section("Strengths", "Weaknesses")
    res["weaknesses"] = get_section("Weaknesses", "Missing Keywords")
    res["missing_keywords"] = get_section("Missing Keywords", "Extracted Skills")
    
    skills_text = get_section("Extracted Skills", "Improvement Suggestions")
    if skills_text:
        res["extracted_skills"] = [s.strip().strip("* -") for s in re.split(r'[,\n]', skills_text) if s.strip()]

    res["suggestions"] = get_section("Improvement Suggestions", "Optimized Example Bullet Points")
    res["optimized_bullets"] = get_section("Optimized Example Bullet Points")
    
    return res

@router.post("/resume", response_model=ResumeAnalysisResponse)
def analyze_resume(req: ResumeAnalysisRequest):
    text = req.resume_text
    target_role = req.target_role or "SDE"
    hf_token = os.getenv("HF_API_TOKEN", "")

    # 1. Extraction & Heuristics
    cgpa = extract_cgpa(text)
    extracted_skills = extract_skills_from_text(text)
    required_skills = ROLE_SKILLS.get(target_role, ROLE_SKILLS["SDE"])
    heuristic_missing = [s for s in required_skills if s not in [e.lower() for e in extracted_skills]]
    
    ats_score = score_ats(text, extracted_skills)
    resume_score = score_resume(extracted_skills, target_role, len(text))

    # 2. Placement Prediction
    prob = compute_placement_probability(
        cgpa=cgpa,
        skills=extracted_skills,
        internship_count=1 if "internship" in text.lower() else 0,
        project_count=max(1, text.lower().count("project")),
        certification_count=text.lower().count("certifi"),
        backlogs=0,
        target_role=target_role,
    )
    readiness = compute_readiness_score(prob, len(extracted_skills)/max(len(required_skills),1), cgpa)
    company_probs = compute_company_probabilities(prob, extracted_skills, req.target_companies)

    # 3. AI Analysis with Multi-Model Fallback
    ats_results = None
    if hf_token:
        prompt = f"""Evaluate this {target_role} resume with high precision. Context: CGPA {cgpa}.
        
        Analyze the provided resume text and provide a detailed evaluation. Focus on technical competence, project complexity, and role alignment.
        
        CRITICAL: For "Extracted Skills", ONLY list core technical skills (languages, frameworks, tools, databases) that are EXPLICITLY mentioned in the resume text. 
        - DO NOT hallucinate. 
        - DO NOT include soft skills.
        - DO NOT include skills that are "implied" but not stated.
        - Use standard professional naming (e.g., "React" instead of "ReactJS").
        
        Format your response EXACTLY like this:
        ATS Score: XX/100
        Strengths: (Briefly list 3-5 key technical strengths found in the resume)
        Weaknesses: (Briefly list 2-3 specific areas where the resume could be improved)
        Missing Keywords: (List 5-8 critical technical keywords for a {target_role} role missing from this resume, comma-separated)
        Extracted Skills: (List ALL technical skills actually found in the resume text, comma-separated)
        Improvement Suggestions: (Provide 3 actionable tips to improve this specific resume)
        Optimized Example Bullet Points: (Rewrite 1-2 existing points from the resume to be more impact-oriented)

        Resume Text:
        {text[:4000]}
        """
        for model in HF_MODELS:
            try:
                ats_results = call_huggingface_model(model, prompt, hf_token)
                if ats_results and ats_results.get("strengths"):
                    break # Success
            except Exception as e:
                logger.warning(f"Model {model} failed for resume: {e}")
                continue

    # 4. Dynamic Fallback on AI Failure
    if not ats_results:
        summary = f"Strong technical profile focusing on {', '.join(extracted_skills[:4])}."
        missing_str = ", ".join(heuristic_missing[:5])
        ats_results = {
            "ats_score": ats_score,
            "strengths": summary,
            "weaknesses": f"Could enhance profile by adding expertise in: {missing_str}",
            "missing_keywords": missing_str,
            "suggestions": f"Focus on mastering {missing_str} to improve ATS compatibility.",
            "optimized_bullets": "Example: Engineered a scalable backend using your top skills; improved efficiency by 20%."
        }

    # Final result assembly
    final_ats_score = ats_results.get("ats_score", ats_score)
    
    # Merge LLM-extracted skills with heuristics-extracted skills
    llm_skills = ats_results.get("extracted_skills", [])
    if llm_skills:
        # Use LLM skills as primary if available, but keep heuristics for safety
        all_skills = list(set(extracted_skills) | set(llm_skills))
        # Ensure we don't have empty strings or weird chars
        all_skills = [s.strip().title() for s in all_skills if len(s.strip()) > 1]
    else:
        all_skills = [s.title() for s in extracted_skills]

    final_missing = list(set(heuristic_missing) | set(re.split(r'[,\n]', ats_results.get("missing_keywords", ""))))
    final_missing = [m.strip("* -").strip().title() for m in final_missing if m.strip()]
    
    # Filter out skills already present in extracted skills from missing_skills
    final_missing = [m for m in final_missing if m.lower() not in [s.lower() for s in all_skills]]

    improvement_tips = []
    if ats_results.get("weaknesses"):
        improvement_tips.append(f"Area for improvement: {ats_results['weaknesses']}")
    if ats_results.get("optimized_bullets"):
        improvement_tips.append(f"Resume Tip: {ats_results['optimized_bullets']}")

    return ResumeAnalysisResponse(
        placement_probability=prob,
        readiness_score=readiness,
        resume_score=resume_score,
        ats_score=final_ats_score,
        company_probabilities=company_probs,
        extracted_skills=all_skills,
        missing_skills=final_missing,
        summary=ats_results.get("strengths", "Analysis complete."),
        recommendations=ats_results.get("suggestions", "").split("\n"),
        improvement_tips=improvement_tips,
    )
