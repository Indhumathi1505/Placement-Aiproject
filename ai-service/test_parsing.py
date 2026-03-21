import re

def test_parsing():
    analysis_text = """
ATS Score: 85/100

Strengths:
* Strong proficiency in Java and Spring Boot.
* Excellent project experience with microservices.

Weaknesses:
* Missing cloud deployment experience.
* Lack of unit testing in some projects.

Missing Keywords:
* Docker, Kubernetes, AWS, JUnit

Improvement Suggestions:
* Add a section for cloud certifications.
* Use more action verbs like 'Architected' or 'Orchestrated'.

Optimized Example Bullet Points:
* Before: Worked on a Java project.
* After: Architected and implemented a high-availability Java microservice using Spring Boot, reducing response time by 30%.
"""

    res = {
        "ats_score": 0,
        "strengths": "",
        "weaknesses": "",
        "missing_keywords": "",
        "suggestions": "",
        "optimized_bullets": "",
    }

    # Extract ATS Score
    score_match = re.search(r"ATS Score:\s*(\d+)/100", analysis_text, re.IGNORECASE)
    if score_match:
        res["ats_score"] = int(score_match.group(1))

    # Extract sections
    def get_section(name, next_name=None):
        pattern = f"{name}:(.*?)(?:{next_name}:|$)" if next_name else f"{name}:(.*)"
        match = re.search(pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    res["strengths"] = get_section("Strengths", "Weaknesses")
    res["weaknesses"] = get_section("Weaknesses", "Missing Keywords")
    res["missing_keywords"] = get_section("Missing Keywords", "Improvement Suggestions")
    res["suggestions"] = get_section("Improvement Suggestions", "Optimized Example Bullet Points")
    res["optimized_bullets"] = get_section("Optimized Example Bullet Points")

    print(f"Parsed Score: {res['ats_score']}")
    print(f"Strengths: {res['strengths'][:50]}...")
    print(f"Weaknesses: {res['weaknesses'][:50]}...")
    print(f"Missing Keywords: {res['missing_keywords']}")
    print(f"Suggestions: {res['suggestions'][:50]}...")
    print(f"Optimized Bullets: {res['optimized_bullets'][:50]}...")

    assert res["ats_score"] == 85
    assert "Strong proficiency" in res["strengths"]
    assert "Docker" in res["missing_keywords"]
    assert "Architected" in res["suggestions"]
    assert "Architected and implemented" in res["optimized_bullets"]
    
    print("\nParsing test passed!")

if __name__ == "__main__":
    test_parsing()
