"""
routers/roadmap.py
POST /generate/roadmap
Generates a personalized month-by-month learning plan based on domain and skills.
"""

import logging
from fastapi import APIRouter
from schemas import RoadmapRequest, RoadmapResponse, RoadmapStep

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── ROADMAP DATA ────────────────────────────────────────────────────────────
ROLE_ROADMAPS = {
    "SDE": [
        {"month": "Month 1", "focus": "DSA Fundamentals", "topics": ["Arrays", "Strings", "Recursion", "Complexity Analysis"], "tasks": ["Solve 50 easy LeetCode problems", "Implement Merge Sort and Quick Sort from scratch", "Watch Time Complexity Analysis video"], "video_url": "https://www.youtube.com/watch?v=RBSGKlAvoiM", "resource": "Striver's A2Z DSA Sheet"},
        {"month": "Month 2", "focus": "Core CS & Java/C++", "topics": ["OOPS", "Memory Management", "Multithreading", "STL/Collections"], "tasks": ["Build a small console application using OOP", "Learn Java Garbage Collection", "Practice Collections API in Java"], "video_url": "https://www.youtube.com/watch?v=U86G6MvS-I8", "resource": "GeeksforGeeks Core CS Section"},
        {"month": "Month 3", "focus": "Backend Core", "topics": ["Spring Boot", "REST APIs", "JWT Auth", "Spring Data MongoDB"], "tasks": ["Create a REST API with Spring Boot", "Implement JWT Authentication", "Connect Spring Boot with MongoDB"], "video_url": "https://www.youtube.com/watch?v=9SGDpanrc8U", "resource": "Amigoscode Spring Boot Course"},
        {"month": "Month 4", "focus": "System Design & Databases", "topics": ["HLD/LLD", "Indexing", "Caching (Redis)", "SQL vs NoSQL"], "tasks": ["Learn Database Indexing", "Design a simple Rate Limiter", "Understand Consistent Hashing"], "video_url": "https://www.youtube.com/watch?v=i53Gi_Kkv4w", "resource": "Grokking System Design"},
        {"month": "Month 5", "focus": "DevOps & Cloud", "topics": ["Docker", "Kubernetes basics", "AWS (S3, EC2)", "CI/CD"], "tasks": ["Dockerize your Spring Boot app", "Deploy a container to AWS EC2", "Setup a GitHub Action for CI/CD"], "video_url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "resource": "TechWorld with Nana Docker Guide"},
        {"month": "Month 6", "focus": "Interview Mastery", "topics": ["Mock Interviews", "Puzzles", "HR Prep", "Aptitude"], "tasks": ["Conduct 5 peer mock interviews", "Solve 50 GFG Aptitude questions", "Prepare HR answers using STAR method"], "video_url": "https://www.youtube.com/watch?v=uT-G_8Dsd-A", "resource": "PlaceIQ Mock Interview Simulator"},
    ],
    "Frontend Developer": [
        {"month": "Month 1", "focus": "HTML/CSS Mastery", "topics": ["Flexbox", "Grid", "Semantic HTML", "Responsive Design"], "tasks": ["Build a responsive portfolio page", "Create a complex layout with CSS Grid", "Learn SASS/SCSS"], "video_url": "https://www.youtube.com/watch?v=OXGznpKZ_sA", "resource": "MDN Web Docs"},
        {"month": "Month 2", "focus": "Modern JavaScript", "topics": ["ES6+", "Promises", "Async/Await", "Closures", "DOM Manipulation"], "tasks": ["Implement a Debounce function", "Build a weather app using Fetch API", "Understand Event Loop"], "video_url": "https://www.youtube.com/watch?v=8aGhZQkoFbQ", "resource": "JavaScript.info"},
        {"month": "Month 3", "focus": "React Fundamentals", "topics": ["JSX", "Hooks", "State Management (Context/Redux)", "Routing"], "tasks": ["Build a Todo list with React Hooks", "Implement Client-side Routing", "Learn Context API"], "video_url": "https://www.youtube.com/watch?v=Ke90Tje7VS0", "resource": "React.dev Beta Docs"},
        {"month": "Month 4", "focus": "Advanced React & UI", "topics": ["Performance Optimization", "Custom Hooks", "Tailwind/Sass", "Framer Motion"], "tasks": ["Build a dashboard with Tailwind CSS", "Create a custom useFetch Hook", "Add animations with Framer Motion"], "video_url": "https://www.youtube.com/watch?v=f4s1h2stEgs", "resource": "Josh Comeau's React Guide"},
        {"month": "Month 5", "focus": "Testing & Build Tools", "topics": ["Jest", "React Testing Library", "Vite/Webpack", "CI/CD"], "tasks": ["Write unit tests for React components", "Optimize Vite build", "Setup CI/CD with Vercel"], "video_url": "https://www.youtube.com/watch?v=8Xgi_vaJcXk", "resource": "Testing JavaScript course"},
        {"month": "Month 6", "focus": "Portfolio & Interviews", "topics": ["Project Deployment", "Performance", "Mock Interviews"], "tasks": ["Launch 3 polished projects", "Optimize Web Vitals", "Practice React coding challenges"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Frontend Masters"},
    ],
    "Backend Developer": [
        {"month": "Month 1", "focus": "Language Mastery (Java/Python/Go)", "topics": ["Advanced Syntax", "Concurrency", "Error Handling"], "tasks": ["Implement a multi-threaded server", "Master async/await in your language", "Write a CLI tool"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Official Language Docs"},
        {"month": "Month 2", "focus": "Web Frameworks", "topics": ["Spring Boot/FastAPI/Express", "Middlewares", "Auth"], "tasks": ["Build a secure CRUD API", "Implement OAuth2 flow", "Write comprehensive unit tests"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Framework Guides"},
        {"month": "Month 3", "focus": "Databases (SQL & NoSQL)", "topics": ["Query Optimization", "Indexing", "Transactions"], "tasks": ["Write complex SQL joins", "Optimize slow queries", "Design a normalized schema"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Database Internals Book"},
        {"month": "Month 4", "focus": "System Design (LLD/HLD)", "topics": ["Caching", "Load Balancing", "Microservices"], "tasks": ["Design a URL Shortener", "Implement Redis caching", "Study distributed systems patterns"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "ByteByteGo"},
        {"month": "Month 5", "focus": "Cloud & Infrastructure", "topics": ["Docker", "Kubernetes", "AWS/GCP"], "tasks": ["Containerize your backend", "Setup a K8s cluster", "Deploy to the cloud"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Cloud Practitioner Exams"},
        {"month": "Month 6", "focus": "Interview Mastery", "topics": ["Mock Interviews", "Scalability Puzzles"], "tasks": ["Practice 20 HLD scenarios", "Optimize API performance", "Final Mock Interviews"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "System Design Primer"},
    ],
    "AI Engineer": [
        {"month": "Month 1", "focus": "Math & Python for AI", "topics": ["Linear Algebra", "Calculus", "NumPy", "Pandas"], "tasks": ["Implement Gradient Descent from scratch", "Analyze a dataset with Pandas", "Perform matrix ops with NumPy"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Khan Academy Math for AI"},
        {"month": "Month 2", "focus": "Machine Learning Fundamentals", "topics": ["Regression", "SVM", "Trees", "Scikit-Learn"], "tasks": ["Build a house price predictor", "Compare different classifiers", "Feature engineering with a real dataset"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Andrew Ng's ML Course"},
        {"month": "Month 3", "focus": "Deep Learning (CNN/RNN)", "topics": ["Neural Networks", "PyTorch/TensorFlow", "Backprop"], "tasks": ["Build a digit classifier (MNIST)", "Create a simple CNN for images", "Understand layer architecture"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Fast.ai Part 1"},
        {"month": "Month 4", "focus": "NLP & Transformers", "topics": ["Attention", "BERT", "GPT", "Tokenization"], "tasks": ["Fine-tune a BERT model", "Generate text with GPT-2", "Text classification with Hugging Face"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Hugging Face Course"},
        {"month": "Month 5", "focus": "Computer Vision / MLOps", "topics": ["Object Detection", "MLflow", "Deployment"], "tasks": ["Train a YOLOv8 model", "Setup an ML pipeline", "Deploy a model as an API (FastAPI)"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "PyImageSearch"},
        {"month": "Month 6", "focus": "Advanced Projects & Interviews", "topics": ["LLM Apps", "Edge AI", "Mock Interviews"], "tasks": ["Build a RAG application", "Optimize model with ONNX", "Practice AI system design"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Mistral/OpenAI Docs"},
    ],
    "Data Scientist": [
        {"month": "Month 1", "focus": "Statistics & Probability", "topics": ["Distributions", "Hypothesis Testing", "Correlation"], "tasks": ["Perform A/B testing analysis", "Calculate confidence intervals", "Visualize data distributions"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "StatQuest with Josh Starmer"},
        {"month": "Month 2", "focus": "Data Wrangling & SQL", "topics": ["Advanced SQL", "Pandas", "Cleaning"], "tasks": ["Clean a messy Kaggle dataset", "Write advanced SQL queries", "Merge multiple data sources"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "SQL for Data Science"},
        {"month": "Month 3", "focus": "Statistical Modeling (ML)", "topics": ["Regression", "Time Series", "Clustering"], "tasks": ["Predict stock prices (Time Series)", "Customer segmentation with K-means", "Build a predictive model"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "ISLP (James et al.)"},
        {"month": "Month 4", "focus": "Data Visualization", "topics": ["Tableau", "Power BI", "Matplotlib/Seaborn"], "tasks": ["Build a Tableau Dashboard", "Create interactive plots in Python", "Storytelling with data"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Storytelling with Data"},
        {"month": "Month 5", "focus": "Big Data & Python (Spark)", "topics": ["PySpark", "Cloud Data Warehouses", "Pipeline"], "tasks": ["Analyze large dataset with Spark", "Use Snowflake or BigQuery", "Setup a data pipeline"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Spark Official Docs"},
        {"month": "Month 6", "focus": "Portfolio Projects & Interviews", "topics": ["End-to-end Project", "Communication", "Interviews"], "tasks": ["Finish three Kaggle projects", "Present results to a friend", "Practice data science cases"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "DataCamp"},
    ],
    "DevOps Engineer": [
        {"month": "Month 1", "focus": "Linux & Scripting", "topics": ["Bash", "File Systems", "Permissions", "Users"], "tasks": ["Automate a task with Bash", "Configure a Linux server", "Learn Cron jobs"], "video_url": "https://www.youtube.com/watch?v=wX75Z-4ME0w", "resource": "Linux Journey"},
        {"month": "Month 2", "focus": "Networking & Security", "topics": ["DNS", "SSH", "Firewalls", "SSL/TLS"], "tasks": ["Configure an Nginx proxy", "Setup SSH keys", "Manage SSL certificates"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Network+ Guide"},
        {"month": "Month 3", "focus": "CI/CD & Source Control", "topics": ["Git Flow", "Jenkins", "GitHub Actions", "GitLab CI"], "tasks": ["Setup a Jenkins pipeline", "Implement Git branching strategy", "Automate builds and tests"], "video_url": "https://www.youtube.com/watch?v=R8_veQiYBjI", "resource": "CI/CD Guide"},
        {"month": "Month 4", "focus": "Containerization & Orchestration", "topics": ["Docker", "Kubernetes", "Helm"], "tasks": ["Deploy a 3-tier app to K8s", "Write a Helm chart", "Setup K8s Dashboard"], "video_url": "https://www.youtube.com/watch?v=X48VuDVv0do", "resource": "Nana K8s Course"},
        {"month": "Month 5", "focus": "Monitoring & SRE", "topics": ["Prometheus", "Grafana", "Alertmanager", "Logging (ELK)"], "tasks": ["Setup Grafana Dashboards", "Configure K8s Alerts", "Centralize logs with Fluentd"], "video_url": "https://www.youtube.com/watch?v=8Xgi_vaJcXk", "resource": "Google SRE Book"},
        {"month": "Month 6", "focus": "Cloud Mastery & Projects", "topics": ["AWS/Azure/GCP", "Secrets Management", "Interview Prep"], "tasks": ["Implement Hashicorp Vault", "Cost optimization on Cloud", "Practice DevOps Scenarios"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Cloud Certified Professional"},
    ],
    "Mobile Developer": [
        {"month": "Month 1", "focus": "Swift/Kotlin Basics", "topics": ["Variables", "Functions", "Optionals/Null Safety", "UI Basics"], "tasks": ["Build a calculator app", "Understand Swift/Kotlin Lifecycle", "Handle User Input"], "video_url": "https://www.youtube.com/watch?v=comQ1-x2a1Q", "resource": "Android/iOS Docs"},
        {"month": "Month 2", "focus": "Platform Advanced UI", "topics": ["SwiftUI/Jetpack Compose", "Navigation", "Lists/Grids"], "tasks": ["Build a news reader UI", "Implement complex navigation", "Custom view components"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Design Guidelines"},
        {"month": "Month 3", "focus": "Networking & Local DB", "topics": ["Retrofit/Alamofire", "Room/Realm", "JSON Parsing"], "tasks": ["Fetch data from a public API", "Store data locally with SQLite", "Handle offline mode"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Ray Wenderlich"},
        {"month": "Month 4", "focus": "State Management & Arch", "topics": ["MVVM", "MVI", "Combine/Coroutines"], "tasks": ["Refactor app to MVVM", "Use reactive streams", "Unit test ViewModels"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Architecture Components"},
        {"month": "Month 5", "focus": "Flutter/React Native", "topics": ["Cross-platform basics", "Bridging", "Design Systems"], "tasks": ["Build a cross-platform app", "Understand Native modules", "Use shared components"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Official Tutorials"},
        {"month": "Month 6", "focus": "App Store & Interviews", "topics": ["Publishing", "Performance tuning", "Mock Interviews"], "tasks": ["Prepare an app for Store submission", "Fix memory leaks", "Practice Mobile system design"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "App Store Review Guidelines"},
    ],
    "Cybersecurity Analyst": [
        {"month": "Month 1", "focus": "Networking & Fundamentals", "topics": ["OSI Model", "TCP/IP", "Wireshark", "Network Security"], "tasks": ["Capture packets with Wireshark", "Configure a basic Firewall", "Understand Port Scanning"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "CompTIA Security+"},
        {"month": "Month 2", "focus": "Linux for Security", "topics": ["Permissions", "Shell Scripting", "KALI Linux", "Metasploit"], "tasks": ["Explore Kali Linux tools", "Practice basic Bash scripting", "Understand Privilege Escalation"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "TryHackMe"},
        {"month": "Month 3", "focus": "Web App Security", "topics": ["OWASP Top 10", "SQL Injection", "XSS", "Burp Suite"], "tasks": ["Find an XSS vulnerability (Labs)", "Practice SQLi on DVWA", "Use Burp Proxy"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "HackTheBox"},
        {"month": "Month 4", "focus": "Cryptography & Identity", "topics": ["Hashing", "Symmetric/Asymmetric", "IAM", "SSL/TLS"], "tasks": ["Encrypt a message with RSA", "Understand OAuth workflows", "Manage IAM roles"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Cybrary"},
        {"month": "Month 5", "focus": "Incident Response & Blue Team", "topics": ["SIEM", "Splunk", "Forensics", "Threathunting"], "tasks": ["Analyze logs in Splunk", "Perform memory forensics", "Identify an IOC"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "SANS Institute"},
        {"month": "Month 6", "focus": "Compliance & Interviews", "topics": ["GDPR/SOC2", "Risk Management", "Ethics", "Mock Interviews"], "tasks": ["Conduct a mock security audit", "Understand GRC basics", "Practice Security Scenarios"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "CISM Guide"},
    ],
    "Cloud Architect": [
        {"month": "Month 1", "focus": "Cloud Foundations (AWS/Azure)", "topics": ["IAM", "VPC", "EC2", "S3"], "tasks": ["Setup a multi-tier VPC", "Host a static site on S3", "IAM user management"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "AWS Cloud Practitioner"},
        {"month": "Month 2", "focus": "Cloud Databases", "topics": ["RDS", "DynamoDB", "Aurora", "Caching"], "tasks": ["Scale an RDS instance", "Write to DynamoDB with Lambda", "Multi-region Replication"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "AWS Associate Architect"},
        {"month": "Month 3", "focus": "Serverless & Messaging", "topics": ["Lambda", "SQS/SNS", "EventBridge", "APIGateway"], "tasks": ["Build an event-driven app", "Implement async messaging", "Secure API with Cognito"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Serverless Framework"},
        {"month": "Month 4", "focus": "High Availability & DR", "topics": ["Auto Scaling", "Load Balancers", "RTO/RPO", "Route53"], "tasks": ["Setup a global Load Balancer", "Simulate a region failure", "Latency-based routing"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Architecting for Scale"},
        {"month": "Month 5", "focus": "Advanced Networking & Sec", "topics": ["Direct Connect", "Transit Gateway", "WAF", "Shield"], "tasks": ["Setup a Transit Gateway", "Configure WAF rules", "Monitor with CloudWatch"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Cloud Security Alliance"},
        {"month": "Month 6", "focus": "Cost & Governance", "topics": ["Billing", "Organizations", "Well-Architected Framework"], "tasks": ["Analyze cloud spend", "Conduct a WAF review", "Mock Architecture Interviews"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "AWS Pro Architect"},
    ],
    "Full Stack Developer": [
        {"month": "Month 1", "focus": "Frontend Basics", "topics": ["HTML", "CSS", "JS", "React Basics"], "tasks": ["Create a responsive website", "Learn JS arrays and objects", "Build a React landing page"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "The Odin Project"},
        {"month": "Month 2", "focus": "Backend Basics (Node/Python)", "topics": ["Express", "MongoDB", "Auth", "REST"], "tasks": ["Build a simple backend", "Understand NoSQL", "Implement User Login"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "App Academy Open"},
        {"month": "Month 3", "focus": "Connecting Frontend & Backend", "topics": ["Axios", "CORS", "API Design", "State sharing"], "tasks": ["Integrate React with Node.js", "Handle form data securely", "Global State Management"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "FullStackOpen"},
        {"month": "Month 4", "focus": "Deployment & Tools", "topics": ["Git", "Docker", "Heroku/Vercel", "Postman"], "tasks": ["Containerize the full app", "Deploy to production", "Setup GitHub workflows"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Modern Full Stack Book"},
        {"month": "Month 5", "focus": "Advanced Stack (Next.js/TS)", "topics": ["Next.js", "TypeScript", "Tailwind", "Postgres"], "tasks": ["Build a Next.js app with SQL", "Add type safety with TS", "Responsive UI with Tailwind"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "CodeWithMosh"},
        {"month": "Month 6", "focus": "Final Project & Interviews", "topics": ["E-commerce App", "Performance", "Mock Interviews"], "tasks": ["Launch a full-scale project", "Optimize for SEO", "Practice System Design"], "video_url": "https://www.youtube.com/watch?v=r_hYR53r61M", "resource": "Zero To Mastery"},
    ],
}


@router.post("/generate", response_model=RoadmapResponse)
def generate_roadmap(req: RoadmapRequest):
    role = req.target_role or "SDE"
    
    # In a more advanced version, we'd use Mistral to tailor this
    base_roadmap = ROLE_ROADMAPS.get(role, ROLE_ROADMAPS["SDE"])
    steps = [RoadmapStep(**step) for step in base_roadmap]
    
    recos = [
        f"Focus on {steps[0].focus} as your first priority since it's the foundation for {role}.",
        f"By month 3, you should be building projects in {steps[2].focus}.",
        f"Use the {steps[3].resource} for in-depth understanding of architecture."
    ]

    return RoadmapResponse(
        role_name=role,
        roadmap=steps,
        recommendations=recos
    )
