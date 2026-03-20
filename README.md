# 🎓 PlaceIQ — AI-Powered Student Placement Prediction System

> A full-stack web application that uses AI to predict placement outcomes, detect skill gaps, analyze resumes, generate learning roadmaps, and conduct mock interviews.

---

## 📁 Project Structure

```
placeiq/
├── frontend/                  # Static HTML/CSS/JS — no build step needed
│   ├── index.html             # Landing page with particle animation
│   ├── login.html             # Auth page (Student / Admin / Coordinator)
│   ├── register.html          # Multi-step student registration
│   ├── dashboard.html         # Student dashboard with charts & predictions
│   ├── resume.html            # AI Resume Analyzer
│   ├── skill-gap.html         # Skill Gap Analysis
│   ├── roadmap.html           # AI Learning Roadmap Generator
│   ├── interview.html         # Mock Interview + Skill Gap tabs
│   └── admin.html             # Admin / Coordinator Dashboard
│
├── backend/                   # Java 17 + Spring Boot 3.2
│   ├── pom.xml
│   └── src/main/java/com/placeiq/
│       ├── PlaceIQApplication.java
│       ├── config/
│       │   ├── SecurityConfig.java
│       │   └── WebClientConfig.java
│       ├── controller/
│       │   ├── AuthController.java
│       │   ├── StudentController.java
│       │   └── InterviewController.java
│       ├── dto/
│       │   └── AuthDTO.java
│       ├── model/
│       │   ├── Student.java
│       │   ├── Prediction.java
│       │   └── SkillGap.java
│       ├── repository/
│       │   ├── StudentRepository.java
│       │   ├── PredictionRepository.java
│       │   └── SkillGapRepository.java
│       ├── security/
│       │   ├── JwtUtil.java
│       │   └── JwtAuthFilter.java
│       └── service/
│           ├── AuthService.java
│           ├── StudentService.java
│           └── AIService.java
│
└── ai-service/                # Python 3.11 + FastAPI
    ├── main.py                # FastAPI app entry point
    ├── model_loader.py        # HuggingFace model initialization
    ├── prediction.py          # Core ML heuristic engine
    ├── schemas.py             # Pydantic request/response models
    ├── requirements.txt
    ├── .env.example
    └── routers/
        ├── resume.py          # POST /analyze/resume
        ├── prediction.py      # POST /predict/placement
        ├── skill_gap.py       # POST /analyze/skill-gap
        └── interview.py       # POST /generate/interview-questions
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JS, Chart.js 4 |
| Backend | Java 17, Spring Boot 3.2, Spring Security, Spring Data MongoDB |
| AI Service | Python 3.11, FastAPI, Mistral-7B (HuggingFace), sentence-transformers |
| Database | MongoDB 7 |
| Auth | JWT (HS256) |
| PDF Parsing | Apache PDFBox (Java), pypdf (Python) |
| Fonts | Syne + DM Sans (Google Fonts) |

---

## 🚀 Running the Project

### Prerequisites

- Java 17+
- Maven 3.9+
- Python 3.11+
- MongoDB 7 (running locally on port 27017)
- Node.js (optional, only if serving frontend via dev server)

---

### 1️⃣ Start MongoDB

```bash
# macOS (Homebrew)
brew services start mongodb-community

# Ubuntu
sudo systemctl start mongod

# Docker (quickest)
docker run -d -p 27017:27017 --name mongo mongo:7
```

---

### 2️⃣ Start the Python AI Microservice

```bash
cd ai-service

# Install dependencies
pip install -r requirements.txt

# Copy and fill in your HuggingFace token
cp .env.example .env
# Edit .env → set HF_API_TOKEN=hf_your_token_here

# Run the service
python main.py
# → Running on http://localhost:8000
```

**API Docs** available at: `http://localhost:8000/docs`

---

### 3️⃣ Start the Spring Boot Backend

```bash
cd backend

# Build and run
mvn spring-boot:run
# → Running on http://localhost:8080
```

---

### 4️⃣ Open the Frontend

Simply open any HTML file in your browser:

```bash
open frontend/index.html        # macOS
xdg-open frontend/index.html   # Linux
# or serve via VS Code Live Server extension
```

Or use Python's built-in server:

```bash
cd frontend
python -m http.server 3000
# → http://localhost:3000
```

---

## 🔑 API Endpoints

### Auth (Public)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new student |
| POST | `/api/auth/login` | Login and get JWT token |

### Students (Authenticated)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students/me` | Get current student profile |
| PUT | `/api/students/{id}` | Update profile |
| POST | `/api/students/{id}/resume` | Upload PDF resume → triggers AI analysis |
| GET | `/api/students/{id}/prediction` | Get latest placement prediction |
| POST | `/api/students/{id}/prediction/refresh` | Force new AI prediction |
| GET | `/api/students/{id}/skill-gap` | Get skill gap report |
| GET | `/api/students/{id}/skill-gap?role=DevOps` | Analyze gap for specific role |

### Interview
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/interview/questions?role=SDE&company=Amazon&difficulty=Hard` | Generate interview questions |

### Admin (ADMIN / COORDINATOR role)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students` | List all students |
| GET | `/api/students/stats` | Get placement statistics |

---

### Python AI Service Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze/resume` | Full resume analysis |
| POST | `/predict/placement` | Profile-based placement prediction |
| POST | `/analyze/skill-gap` | Skill gap breakdown with courses |
| POST | `/generate/interview-questions` | AI-generated interview questions |
| GET | `/health` | Health check |

---

## 🧠 AI Features

### Placement Probability Engine
- Weighted heuristic model using: CGPA (25%), Skill Match (35%), Internships (15%), Projects (12%), Certifications (8%), Backlog Penalty
- Per-company probability scores based on company-specific skill alignment
- Pluggable design — replace the heuristic with an XGBoost/sklearn model by swapping `prediction.py`

### Resume Analyzer
- Apache PDFBox extracts text from uploaded PDF
- Keyword scan identifies 50+ technical skills
- ATS score based on section headings, keyword density, and length
- Mistral-7B (HuggingFace Inference API) generates deep analysis, recommendations, and improvement tips
- Graceful fallback if LLM is unavailable

### Skill Gap Detector
- Role-specific required skill banks for SDE, Data Scientist, DevOps, Full Stack, ML Engineer
- Current level estimation based on resume/profile skills
- Priority classification: CRITICAL / HIGH / MEDIUM / LOW
- Curated course recommendations with platform + URL + duration

### Mock Interview AI
- Company-specific question banks (TCS, Infosys, Amazon, Google, etc.)
- Mistral-7B generates fresh questions when HF token is available
- Fallback to curated question bank (Technical, Coding, HR) per role

---

## 🗄️ MongoDB Collections

| Collection | Description |
|-----------|-------------|
| `students` | Student profiles, skills, targets, resume path |
| `predictions` | AI prediction history per student |
| `skill_gaps` | Skill gap analysis history per student |

---

## 🔒 Security

- Passwords hashed with BCrypt (strength 10)
- JWT tokens signed with HS256, expire in 24 hours
- Role-based access control: `STUDENT`, `ADMIN`, `COORDINATOR`
- CORS configured for frontend origins only
- Stateless session (no server-side sessions)

---

## 📈 Extending the Project

### Replace heuristic model with ML model
```python
# prediction.py — swap compute_placement_probability with:
import joblib
model = joblib.load("placement_model.pkl")

def compute_placement_probability(cgpa, skills, ...):
    features = build_feature_vector(cgpa, skills, ...)
    return float(model.predict_proba([features])[0][1])
```

### Add email notifications
Add `spring-boot-starter-mail` to `pom.xml` and create a `NotificationService` that sends placement updates via SMTP.

### Add analytics dashboard
Use MongoDB Aggregation Pipeline to compute department-wise placement trends and expose via `/api/admin/analytics`.

---

## 👨‍💻 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Student | `student@college.edu` | `student123` |
| Admin | `admin@placeiq.com` | `admin123` |
| Coordinator | `coord@placeiq.com` | `coord123` |

> ⚠️ These are UI-only demo credentials for the static frontend. The Spring Boot backend requires real registration via `/api/auth/register`.

---

## 📄 License

MIT License — free to use for academic and portfolio projects.
