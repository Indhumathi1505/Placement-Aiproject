import json
import re
import random

def test_parsing():
    analysis_text = """
{
  "company": "TCS",
  "role": "Software Engineer",
  "rounds": [
    {
      "round_name": "Technical",
      "round_id": "R1",
      "questions": [
        {
          "question_id": "TCS-R1-Q1",
          "question": "What is a deadlock?",
          "difficulty": "Medium",
          "domain": "OS",
          "hint": "Think about mutual exclusion.",
          "sample_answer": "A situation where...",
          "expected_time_to_answer": 5,
          "evaluation_criteria": "Understanding of OS concepts"
        }
      ]
    },
    {
      "round_name": "HR",
      "round_id": "R2",
      "questions": [
        {
          "question_id": "TCS-R2-Q1",
          "question": "Why TCS?",
          "difficulty": "Easy",
          "domain": "HR",
          "hint": "Research company values.",
          "sample_answer": "TCS is a global leader...",
          "expected_time_to_answer": 3,
          "evaluation_criteria": "Cultural fit"
        }
      ]
    }
  ]
}
"""

    match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
    assert match is not None
    
    data = json.loads(match.group())
    flat_questions = []
    if "rounds" in data:
        for round_data in data["rounds"]:
            round_name = round_data.get("round_name", "General")
            for q in round_data.get("questions", []):
                q["round"] = round_name
                q["type"] = round_name # Map for frontend compatibility
                q["id"] = q.get("question_id", f"Q{random.randint(100,999)}")
                flat_questions.append(q)

    print(f"Flattened Questions Count: {len(flat_questions)}")
    for q in flat_questions:
        print(f"ID: {q['id']}, Round: {q['round']}, Type: {q['type']}, Question: {q['question'][:30]}...")
        assert "round" in q
        assert "type" in q
        assert "sample_answer" in q

    assert len(flat_questions) == 2
    assert flat_questions[0]["round"] == "Technical"
    assert flat_questions[1]["round"] == "HR"
    assert flat_questions[0]["domain"] == "OS"
    
    print("\nInterview parsing test passed!")

if __name__ == "__main__":
    test_parsing()
