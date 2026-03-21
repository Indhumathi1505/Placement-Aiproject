import requests
import json

url = "http://localhost:8001/analyze/skill-gap"
payload = {
    "student_id": "test_student",
    "current_skills": ["java", "python"],
    "target_role": "SDE",
    "cgpa": 8.5
}

try:
    print(f"Calling {url}...")
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
