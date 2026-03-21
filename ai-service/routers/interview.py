import re
import json
import random
import logging
import requests
import asyncio
from typing import List, Dict, Optional
from fastapi import APIRouter
from schemas import InterviewQuestionsRequest, InterviewQuestionsResponse, InterviewRound, InterviewQuestion
from model_loader import get_hf_token, HF_API_URL, MODEL_ID

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── DOMAIN LOGIC DEFINITIONS ────────────────────────────────────────────────
DOMAIN_LOGIC = {
    "Software Developer": "DSA (arrays, trees, graphs), DBMS, OS, CN, Coding problems, OOP concepts.",
    "Fullstack Developer": "Frontend + Backend + APIs, Database + system flow, React / Node / REST APIs.",
    "Frontend Developer": "HTML, CSS, JavaScript, React / Angular, DOM, performance, accessibility.",
    "Backend Developer": "APIs, DBMS, authentication, System design basics, Java / Spring Boot / Node.",
    "UI/UX Designer": "Design principles, Wireframing, User research, Case study questions.",
    "Cloud Engineer": "AWS / Azure / GCP, Deployment, scaling, Docker, Kubernetes.",
    "Data Analyst": "SQL, Excel, Data interpretation, Visualization, Case-based questions.",
    "AI Engineer": "ML algorithms, Python, NLP / DL basics, Model evaluation."
}

def get_system_prompt(domain: str, company: str, skills: List[str], diff: str):
    logic = DOMAIN_LOGIC.get(domain, "Core technical concepts and problem-solving.")
    skills_str = ", ".join(skills) if skills else "General technical skills"
    
    return f"""You are an AI Mock Interview Generator.
Generate HIGH-QUALITY, NON-REPEATING interview questions based on the selected DOMAIN.

---
## 🎯 CONTEXT:
* Domain: {domain}
* Target Companies: {company}
* Candidate Skills: {skills_str}
* Difficulty Level: {diff}

---
## 🚫 STRICT RULES:
1. DO NOT repeat any question.
2. DO NOT generate similar/rephrased questions.
3. Always generate NEW and UNIQUE questions.
4. Avoid common generic questions.
5. If previous_questions are provided, COMPLETELY avoid them.

---
🧠 DOMAIN-BASED LOGIC: {logic}

---
## 📚 QUALITY RULES:
* Questions must feel like real interviews.
* Mix conceptual + coding + scenario-based.
* Avoid textbook-only questions.
* Keep answers/hints concise and useful.
"""

def call_mistral_for_round(round_name: str, domain: str, company: str, 
                           skills: List[str], diff: str, token: str, 
                           prev_q: List[str]) -> Optional[InterviewRound]:
    """Generates a single round for better parallelism and less timeout risk."""
    if not token: return None
    
    sys_prompt = get_system_prompt(domain, company, skills, diff)
    prev_str = ", ".join(prev_q) if prev_q else "None"

    user_prompt = f"""Generate exactly 6-8 questions for the '{round_name}' round.

Previous questions to COMPLETELY AVOID: [{prev_str}]

STRICT OUTPUT FORMAT (JSON ONLY):
{{
  "round_name": "{round_name}",
  "round_id": "{round_name[:2].upper()}",
  "questions": [
    {{
      "question_id": "ID-1",
      "question": "The question text...",
      "difficulty": "{diff}",
      "topic": "Specific Topic",
      "hint": "Helpful hint here...",
      "sample_answer": "A good sample answer...",
      "expected_time": 5,
      "evaluation_criteria": "What to look for...",
      "domain": "{domain}"
    }}
  ]
}}

Return ONLY valid JSON."""

    try:
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.7
        }
        resp = requests.post(HF_API_URL, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=90)
        resp.raise_for_status()
        
        text = resp.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        # Extract JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return InterviewRound(**data)
    except Exception as e:
        logger.error(f"Failed to generate round {round_name}: {e}")
    return None

# PREDEFINED HIGH-QUALITY CURATED QUESTION BANK FOR INSTANT RESPONSE (2-3 seconds requirement)
CURATED_BANK = {
    "Aptitude": [
        "A train running at the speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train?",
        "If a person walks at 14 km/hr instead of 10 km/hr, he would have walked 20 km more. The actual distance travelled by him is?",
        "The ratio of the ages of a man and his wife is 4:3. After 4 years, this ratio will be 9:7. What is the age of the man?",
        "Look at this series: 2, 1, (1/2), (1/4), ... What number should come next?",
        "If A is the brother of B; B is the sister of C; and C is the father of D, how D is related to A?",
        "A bag contains 2 red, 3 green and 2 blue balls. Two balls are drawn at random. What is the probability that none of the balls drawn is blue?",
        "In a certain code language, '134' means 'good and tasty'; '478' means 'see good pictures' and '729' means 'pictures are faint'. Which of the following digits stands for 'see'?"
    ],
    "HR": [
        "Tell me about a time you handled a difficult situation with a coworker.",
        "Where do you see yourself in 5 years?",
        "Why do you want to work for our company?",
        "Describe a time you failed and how you handled it.",
        "What are your greatest strengths and weaknesses?",
        "How do you prioritize your work when you have multiple deadlines?",
        "Tell me about a time you had to learn a new technology quickly."
    ],
    "Communication": [
        "Explain a complex technical concept to someone without a technical background.",
        "How would you communicate a project delay to a stakeholder?",
        "Describe a situation where written communication was better than verbal.",
        "How do you adapt your communication style when talking to different audiences?",
        "Tell me about a time you had to persuade someone to see your point of view.",
        "How do you ensure you have completely understood a client's requirements?",
        "Describe a time when poor communication caused an issue on your team."
    ],
    "Group Discussion": [
        "Is Artificial Intelligence a threat to human jobs or an enabler?",
        "Remote work vs Office work: Which yields better productivity?",
        "Should social media platforms be regulated by the government?",
        "Impact of electric vehicles on the global economy.",
        "Is college education still necessary in the era of online learning?",
        "The role of ethics in corporate governance.",
        "How has technology changed human interactions?"
    ]
}

DOMAIN_TECHNICAL_BANK = {
    "Software Developer": [
        "Explain the difference between an Abstract Class and an Interface.",
        "What are the four pillars of Object-Oriented Programming?",
        "How does garbage collection work in Java/Python?",
        "Explain the concept of threading vs multiprocessing.",
        "What is a memory leak and how can you avoid it?",
        "How do you resolve merge conflicts in Git?",
        "What is Dependency Injection and why is it useful?"
    ],
    "Fullstack Developer": [
        "Explain the lifecycle of a React component.",
        "How do you handle state management in a large frontend application?",
        "What is CORS and how do you configure it?",
        "Explain the difference between SQL and NoSQL databases. When would you use each?",
        "What are JWT tokens and how do they work?",
        "How do you optimize a web application for performance?",
        "Explain the MVC (Model-View-Controller) architecture."
    ],
    "Frontend Developer": [
        "What is the Virtual DOM and how does React use it?",
        "Explain CSS Specificity and the cascading algorithm.",
        "What are closures in JavaScript? Provide an example.",
        "How do you ensure your web application is accessible (a11y)?",
        "Explain the difference between `var`, `let`, and `const`.",
        "What are promises in JavaScript and how do they differ from callbacks?",
        "Explain CSS Grid vs Flexbox."
    ],
    "Backend Developer": [
        "Explain the CAP Theorem and its implications.",
        "What is the difference between REST and GraphQL?",
        "How do you handle database migrations in a production environment?",
        "Explain how indexing works in a relational database.",
        "What is rate limiting and how would you implement it?",
        "How do you handle authentication securely in a REST API?",
        "What is a message queue and when would you use one (e.g., RabbitMQ, Kafka)?"
    ],
    "UI/UX Designer": [
        "What is the difference between UI and UX?",
        "Explain your design process from concept to delivery.",
        "How do you conduct user research and usability testing?",
        "What are wireframes, mockups, and prototypes?",
        "How do you balance user needs with business goals?",
        "Explain the principles of Gestalt psychology in design.",
        "How do you design for accessibility and inclusivity?"
    ],
    "Cloud Engineer": [
        "What are the differences between IaaS, PaaS, and SaaS?",
        "Explain the concept of Auto Scaling. How do you configure it in AWS?",
        "What is Infrastructure as Code (IaC)? Mention some tools.",
        "How do you secure an S3 bucket or equivalent blob storage?",
        "Explain the architecture of a serverless application.",
        "What is Docker and how does it differ from a Virtual Machine?",
        "Explain how Kubernetes handles container orchestration."
    ],
    "Data Analyst": [
        "What is the difference between supervised and unsupervised learning?",
        "How do you handle missing values in a dataset?",
        "Explain the concept of p-value and statistical significance.",
        "What is the difference between a join and a union in SQL?",
        "How do you optimize a slow-performing SQL query?",
        "Explain the central limit theorem.",
        "What metrics would you use to evaluate a classification model?"
    ],
    "AI Engineer": [
        "Explain the concept of backpropagation in neural networks.",
        "What is the difference between a CNN and an RNN?",
        "How do you prevent overfitting in a machine learning model?",
        "Explain the self-attention mechanism in the Transformer architecture.",
        "What is transfer learning and when is it useful?",
        "How do you evaluate the performance of an NLP model?",
        "Explain the difference between L1 and L2 regularization."
    ]
}

DOMAIN_SYSTEM_DESIGN_BANK = {
    "Software Developer": [
        "Design a URL shortener like TinyURL.",
        "How would you design a ticketing system like BookMyShow?",
        "Design an autocomplete feature for a search engine.",
        "How would you implement a distributed cache?",
        "Design a rate limiter.",
        "Design a file storage service like Google Drive.",
        "How would you build a chat application like WhatsApp?"
    ],
    "Fullstack Developer": [
        "Design an E-commerce platform checkout flow.",
        "How would you build a real-time notification system?",
        "Design a collaborative document editor like Google Docs.",
        "Architecture a microservices-based social media feed.",
        "Design an API rate limiter for a SaaS product.",
        "How would you handle concurrent bookings in a hotel reservation system?",
        "Design a ride-sharing service like Uber."
    ],
    "Frontend Developer": [
        "Design the state management for a complex E-commerce SPA.",
        "Architecture a real-time chat web client.",
        "How would you build a design system for a large organization?",
        "Design an infinite scrolling image gallery.",
        "How would you optimize the loading time of a massive single-page application?",
        "Design the frontend architecture for a real-time collaborative tool.",
        "How would you implement off-line support for a web application?"
    ],
    "Backend Developer": [
        "Design a distributed key-value store.",
        "Architecture a scalable video streaming service like Netflix.",
        "How would you design a scalable pub/sub system?",
        "Design a ride-sharing application's backend architecture.",
        "How would you build a high-throughput logging system?",
        "Design an inventory management system for a global retailer.",
        "Architecture a highly available payment gateway."
    ],
    "UI/UX Designer": [
        "Design a dashboard for a cloud infrastructure monitoring tool.",
        "How would you redesign the checkout process of an E-commerce app?",
        "Design the user flow for a ride-sharing application.",
        "How would you design an intuitive navigation system for a complex enterprise software?",
        "Design a mobile app interface for tracking personal finances.",
        "How would you improve the accessibility of a government portal?",
        "Design a seamless onboarding experience for a new SaaS product."
    ],
    "Cloud Engineer": [
        "Design a highly available and fault-tolerant architecture on AWS.",
        "How would you migrate a monolithic application to a microservices architecture in the cloud?",
        "Architecture a disaster recovery strategy for a critical application.",
        "Design a secure multi-VPC architecture for an enterprise.",
        "How would you set up a scalable CI/CD pipeline?",
        "Design a serverless data processing pipeline.",
        "How would you architecture a global content delivery network (CDN) strategy?"
    ],
    "Data Analyst": [
        "Design a dashboard to monitor Key Performance Indicators (KPIs) for an E-commerce business.",
        "How would you structure a data warehouse for a retail company?",
        "Design a process for cleaning and validating incoming data streams.",
        "How would you setup A/B testing for a new product feature?",
        "Design a reporting system for real-time user behavior analytics.",
        "How would you track and analyze the success of a marketing campaign?",
        "Design a churn prediction model for a subscription service."
    ],
    "AI Engineer": [
        "Design a recommendation system for a video streaming platform.",
        "Architecture an edge computing system for real-time object detection.",
        "How would you build a scalable pipeline for training machine learning models?",
        "Design a conversational bot for customer service.",
        "How would you deploy and serve a large language model efficiently?",
        "Architecture a system for detecting fraudulent transactions in real-time.",
        "Design an automated data tagging system for computer vision."
    ]
}

def get_curated_round(round_name: str, domain: str, diff: str) -> InterviewRound:
    """Generates an instant round using pre-curated question banks."""
    questions = []
    
    if round_name == "Technical":
        q_list = DOMAIN_TECHNICAL_BANK.get(domain, DOMAIN_TECHNICAL_BANK["Software Developer"])
    elif round_name == "Problem Solving / System Design":
        q_list = DOMAIN_SYSTEM_DESIGN_BANK.get(domain, DOMAIN_SYSTEM_DESIGN_BANK["Software Developer"])
    else:
        q_list = CURATED_BANK.get(round_name, CURATED_BANK["HR"])
        
    random.shuffle(q_list)
    
    for i, q_text in enumerate(q_list[:7]):
        questions.append(
            InterviewQuestion(
                question_id=f"{round_name[:2].upper()}-{i}",
                question=q_text,
                difficulty=diff,
                topic=round_name,
                hint="Think critically about the core concepts.",
                sample_answer="Use STAR method or state core principles clearly.",
                expected_time=5,
                evaluation_criteria="Clarity, structure, and correctness.",
                domain=domain
            )
        )
        
    return InterviewRound(
        round_name=round_name,
        round_id=round_name[:2].upper(),
        questions=questions
    )

@router.post("/interview-questions", response_model=InterviewQuestionsResponse)
async def generate_questions(req: InterviewQuestionsRequest):
    domain = req.target_role or "Software Developer"
    rounds = ["Aptitude", "Technical", "HR", "Communication", "Group Discussion", "Problem Solving / System Design"]
    all_rounds = []
    
    try:
        # Instant generation using high-quality curated banks (takes < 0.1s)
        for r in rounds:
            all_rounds.append(get_curated_round(r, domain, req.difficulty))
            
    except Exception as e:
        logger.error(f"Curated mock interview generation failed: {e}")
        # Absolute fallback
        all_rounds = [
            InterviewRound(
                round_name="General Technical & HR", 
                round_id="G1", 
                questions=[
                    InterviewQuestion(
                        question_id="F1",
                        question=f"Could you explain your experience with {req.skills[0] if req.skills else 'software development'}?",
                        difficulty="Medium",
                        topic="Experience",
                        hint="Talk about a specific project.",
                        sample_answer="I have used it in...",
                        expected_time=5,
                        evaluation_criteria="Clarity and depth.",
                        domain=domain
                    )
                ]
            )
        ]

    return InterviewQuestionsResponse(domain=domain, rounds=all_rounds)
