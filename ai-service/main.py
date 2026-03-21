"""
PlaceIQ — Python AI Microservice
FastAPI application exposing AI endpoints for the Spring Boot backend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from routers import resume, prediction, skill_gap, interview, roadmap, chatbot
from model_loader import load_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load AI models on startup, release on shutdown."""
    logger.info("🚀 Loading AI models...")
    load_models()
    logger.info("✅ Models loaded. PlaceIQ AI service ready.")
    yield
    logger.info("👋 Shutting down PlaceIQ AI service.")


app = FastAPI(
    title="PlaceIQ AI Microservice",
    description="AI endpoints for placement prediction, resume analysis, and skill gap detection",
    version="1.0.0",
    lifespan=lifespan,
)

import os
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8080,http://localhost:5173,http://localhost:5174").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(resume.router,     prefix="/analyze",  tags=["Resume"])
app.include_router(prediction.router, prefix="/predict",  tags=["Prediction"])
app.include_router(skill_gap.router,  prefix="/analyze",  tags=["Skill Gap"])
app.include_router(interview.router,  prefix="/generate", tags=["Interview"])
app.include_router(chatbot.router,    prefix="/chat",     tags=["Chatbot"])
app.include_router(roadmap.router,    prefix="/generate/roadmap", tags=["Roadmap"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "PlaceIQ AI"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
