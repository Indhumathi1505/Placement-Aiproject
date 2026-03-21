import requests
import os
from dotenv import load_dotenv

load_dotenv()

def debug_connection():
    # 1. Check local health
    try:
        health = requests.get("http://localhost:8001/health", timeout=5).json()
        print(f"Service Health: {health}")
    except Exception as e:
        print(f"Service Unreachable: {e}")

    # 2. Check Hugging Face directly
    token = os.getenv("HF_API_TOKEN")
    print(f"Token present: {bool(token)}")
    if token:
        print(f"Token prefix: {token[:10]}...")
        headers = {"Authorization": f"Bearer {token}"}
        # Try a tiny request
        try:
            resp = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                headers=headers,
                json={"inputs": "hi"},
                timeout=10
            )
            print(f"HF Status: {resp.status_code}")
            print(f"HF Response: {resp.text[:200]}")
        except Exception as e:
            print(f"HF Request Failed: {e}")

if __name__ == "__main__":
    debug_connection()
