"""
schemas.py — Pydantic request/response models for PlaceIQ AI endpoints.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


# ─── RESUME ──────────────────────────────────────────────────────────────────

class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    student_id: str
    target_role: Optional[str] = "SDE"
    target_companies: Optional[List[str]] = []


class ResumeAnalysisResponse(BaseModel):
    placement_probability: float
    readiness_score: float
    resume_score: int
    ats_score: int
    company_probabilities: Dict[str, float]
    extracted_skills: List[str]
    missing_skills: List[str]
    summary: str
    recommendations: List[str]
    improvement_tips: List[str]


# ─── PLACEMENT PREDICTION ─────────────────────────────────────────────────────

class PlacementPredictionRequest(BaseModel):
    student_id: str
    cgpa: float
    skills: List[str]
    internship_count: Optional[int] = 0
    project_count: Optional[int] = 0
    certification_count: Optional[int] = 0
    backlogs: Optional[int] = 0
    target_role: Optional[str] = "SDE"
    target_companies: Optional[List[str]] = []


class PlacementPredictionResponse(BaseModel):
    placement_probability: float
    readiness_score: float
    company_probabilities: Dict[str, float]
    recommendations: List[str]


# ─── SKILL GAP ────────────────────────────────────────────────────────────────

class SkillGapRequest(BaseModel):
    student_id: str
    current_skills: List[str]
    target_role: str
    cgpa: Optional[float] = None


class SkillEntry(BaseModel):
    skill_name: str
    current_level: int      # 0-100
    required_level: int     # 0-100
    priority: str           # CRITICAL | HIGH | MEDIUM | LOW


class CourseRecommendation(BaseModel):
    skill_name: str
    course_name: str
    platform: str
    url: str
    duration: str
    priority: str


class SkillGapResponse(BaseModel):
    missing_skills: List[str]
    critical_skills: List[str]
    skill_entries: List[SkillEntry]
    recommended_courses: List[CourseRecommendation]
    gap_score: float
    estimated_weeks: int


# ─── INTERVIEW QUESTIONS ──────────────────────────────────────────────────────

class InterviewQuestion(BaseModel):
    question_id: str
    question: str
    difficulty: str
    topic: Optional[str] = "General"
    hint: Optional[str] = ""
    sample_answer: Optional[str] = ""
    expected_time: Optional[int] = 5
    evaluation_criteria: Optional[str] = ""
    domain: Optional[str] = ""

class InterviewRound(BaseModel):
    round_name: str
    round_id: str
    questions: List[InterviewQuestion]

class InterviewQuestionsRequest(BaseModel):
    target_role: str
    company: Optional[str] = "General"
    difficulty: Optional[str] = "Medium"
    count: Optional[int] = 7
    student_id: Optional[str] = None
    skills: Optional[List[str]] = []
    cgpa: Optional[float] = None
    projects: Optional[List[str]] = []
    previous_questions: Optional[List[str]] = []

class InterviewQuestionsResponse(BaseModel):
    domain: str
    rounds: List[InterviewRound]


# ─── ROADMAP ──────────────────────────────────────────────────────────────────

class RoadmapRequest(BaseModel):
    target_role: str
    current_skills: List[str]
    student_id: Optional[str] = None

class RoadmapStep(BaseModel):
    month: str
    focus: str
    topics: List[str]
    tasks: List[str] = []
    video_url: Optional[str] = None
    resource: str

class RoadmapResponse(BaseModel):
    role_name: str
    roadmap: List[RoadmapStep]
    recommendations: List[str]


# ─── CHATBOT ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    student_id: str
    name: Optional[str] = "Student"
    cgpa: Optional[float] = None
    skills: Optional[List[str]] = []
    weak_areas: Optional[List[str]] = []
    target_role: Optional[str] = "SDE"
    target_companies: Optional[List[str]] = []
    past_performance: Optional[Dict[str, Any]] = {}
    mode: Optional[str] = "chat"           # chat | evaluate | resume | skill_gap
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    mode: str
    suggestions: Optional[List[str]] = []
