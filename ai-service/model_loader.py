"""
model_loader.py
Loads and caches all AI models used by the PlaceIQ service.
Models are loaded once at startup and reused across requests.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Global model references ──────────────────────────────────────────────────
_sentence_model = None       # sentence-transformers for skill matching
_hf_api_token: Optional[str] = None

# Hugging Face Inference API endpoint for Mistral-7B
# Hugging Face Inference API endpoint (OpenAI-compatible router)
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_ID = "HuggingFaceH4/zephyr-7b-beta:featherless-ai"


def load_models():
    """
    Load models at service startup.
    sentence-transformers runs locally; Mistral-7B is called via HF Inference API.
    """
    global _sentence_model, _hf_api_token

    # 1. Load sentence-transformers for skill similarity matching
    try:
        from sentence_transformers import SentenceTransformer
        _sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("✅ Sentence transformer loaded: all-MiniLM-L6-v2")
    except Exception as e:
        logger.warning(f"⚠️  Could not load sentence transformer: {e}")
        _sentence_model = None

    # 2. Read HuggingFace API token from environment
    _hf_api_token = os.getenv("HF_API_TOKEN", "")
    if _hf_api_token:
        logger.info("✅ HuggingFace API token loaded.")
    else:
        logger.warning("⚠️  HF_API_TOKEN not set. LLM calls will be skipped.")


def get_sentence_model():
    return _sentence_model


def get_hf_token() -> str:
    return _hf_api_token or ""
