"""
routers/prediction.py
POST /predict/placement
Profile-based placement prediction (no resume required).
"""

import logging
from fastapi import APIRouter
from schemas import PlacementPredictionRequest, PlacementPredictionResponse
from prediction import (
    compute_placement_probability,
    compute_company_probabilities,
    compute_readiness_score,
    compute_skill_match,
    ROLE_SKILLS,
)

logger = logging.getLogger(__name__)
router = APIRouter()

ROLE_RECOMMENDATIONS = {
    "SDE": [
        "Practise 2–3 LeetCode problems daily (focus: Arrays, Trees, DP).",
        "Build a full-stack project and host it on GitHub.",
        "Study High-Level Design concepts: Load Balancers, Caching, Databases.",
    ],
    "Data Scientist": [
        "Complete an end-to-end ML project and publish it on Kaggle.",
        "Strengthen your SQL skills with window functions and CTEs.",
        "Contribute to an open-source data science repository.",
    ],
    "DevOps": [
        "Get AWS/GCP Cloud Practitioner certified.",
        "Build a CI/CD pipeline for a personal project using GitHub Actions.",
        "Set up a local Kubernetes cluster with Minikube.",
    ],
}


@router.post("/placement", response_model=PlacementPredictionResponse)
def predict_placement(req: PlacementPredictionRequest):
    target_role = req.target_role or "SDE"

    probability = compute_placement_probability(
        cgpa=req.cgpa,
        skills=req.skills,
        internship_count=req.internship_count,
        project_count=req.project_count,
        certification_count=req.certification_count,
        backlogs=req.backlogs,
        target_role=target_role,
    )

    required = ROLE_SKILLS.get(target_role, ROLE_SKILLS["SDE"])
    skill_ratio = compute_skill_match(req.skills, required)
    readiness = compute_readiness_score(probability, skill_ratio, req.cgpa)
    company_probs = compute_company_probabilities(probability, req.skills, req.target_companies)

    recommendations = ROLE_RECOMMENDATIONS.get(target_role, ROLE_RECOMMENDATIONS["SDE"])

    return PlacementPredictionResponse(
        placement_probability=probability,
        readiness_score=readiness,
        company_probabilities=company_probs,
        recommendations=recommendations,
    )
