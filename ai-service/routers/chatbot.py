from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import os
import json
import requests
import re
import asyncio
from typing import List, Dict, Optional
from schemas import ChatRequest, ChatResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Multimodel fallbacks to bypass free-tier rate limits
HF_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.2",
    "HuggingFaceH4/zephyr-7b-beta",
    "meta-llama/Meta-Llama-3-8B-Instruct"
]
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models"

# ─── MASSIVE KNOWLEDGE BASE (100% Accuracy & Sub-Second Response) ──────────────
FAQ_KNOWLEDGE_BASE = {
    r"\b(dsa|data structures|algorithms)\b": """
**Data Structures and Algorithms (DSA)** is the fundamental pillar of technical interviews at product-based companies. 

### Core Roadmap:
1. **Mathematics & Arrays**: Master Prefix Sums, Two Pointers, Sliding Window, and Kadane's Algorithm.
2. **Linked Lists & Stacks/Queues**: Practice Reversal, Cycle Detection (Floyd's), and Monotonic Stacks (Next Greater Element).
3. **Trees & Graphs**: Deeply understand BFS/DFS, Tree Traversals, Lowest Common Ancestor (LCA), and Dijkstra's Shortest Path.
4. **Dynamic Programming**: Start with Recursion + Memoization (Top-Down) and transition to Tabulation (Bottom-Up). Focus on LIS, LCS, and Knapsack patterns.

### Interview Advice:
*   **Time Complexity**: Always state the Big O complexity of your solution before coding.
*   **Edge Cases**: Mention Null checks, single-element arrays, and negative numbers.
*   **Dry Run**: Walk through your logic with a small test case like `[1, 2, 3]` before finalizing.
""",

    r"\b(fullstack|full stack|mern|mean)\b": """
**Fullstack Development** requires mastering both the client-side (Frontend) and server-side (Backend) of an application. 

### Modern Tech Stack:
*   **Frontend**: HTML5, CSS3 (Flexbox/Grid), Modern JavaScript (ES6+), and **React** (Hooks, Context, Redux for State Management).
*   **Backend**: **Node.js with Express** or **Java Spring Boot** (highly valued in enterprises). Focus on RESTful API design.
*   **Databases**: Use **PostgreSQL** or **MySQL** for structured data, and **MongoDB** for flexible schemas.
*   **DevOps**: Learn basic Docker containers and how to deploy using platforms like AWS (EC2/S3) or Vercel.

### Pro-Tip:
Build a **Real-World Project** like an E-commerce platform with Stripe integration or a Real-time Chat app using WebSockets. This demonstrates you can handle authentication, state, and persistent storage.
""",

    r"\b(software developer|sde|engineers|engineer)\b": """
An **SDE (Software Development Engineer)** role is not just about writing code; it's about solving complex problems efficiently at scale.

### Key Skills Required:
*   **Problem Solving**: Strong proficiency in DSA (LeetCode Medium-Hard level).
*   **CS Fundamentals**: Deep knowledge of **Operating Systems** (Process/Thread, Deadlocks), **DBMS** (Indexing, Transactions), and **Computer Networks** (TCP/UDP, DNS).
*   **Object-Oriented Design (OOD)**: Master the SOLID principles and Design Patterns (Singleton, Factory, Observer).
*   **System Design**: For SDE-2+ roles, you must understand Load Balancers, Caching (Redis), and Database Sharding.

### Career Tip:
Collaborate on **Open Source** or contribute to complex team projects. Companies value the ability to read and integrate with existing large codebases.
""",

    r"\b(tcs|nqt|infosys|wipro|mass recruiters)\b": """
**Service-Based Mass Recruiters** (TCS, Infosys, Wipro, Cognizant) follow a very specific hiring pattern focused on volume and reliability.

### Preparation Strategy:
1. **Aptitude & Logical Reasoning**: This is the biggest filter. Practice Numerical Ability, Syllogisms, and Data Interpretation.
2. **Verbal Ability**: Basic English grammar and reading comprehension are mandatory.
3. **Coding Round**: Expect 1-2 basic questions on String manipulation, Array filtering, or basic loops. Mastering 'Easy' level GeeksForGeeks problems is sufficient.
4. **Interview (TR+HR)**: Focus on your Final Year Project and basic OOP concepts (Abstraction, Encapsulation).

### Important Note:
Scoring high in **TCS NQT** can land you 'Ninja' or 'Digital' roles with significantly higher packages (up to ₹7LPA+).
""",

    r"\b(ats|resume|cv|parse)\b": """
An **ATS-Friendly Resume** is designed to pass through the Automated Tracking Systems that recruiters use to filter applications.

### Strict Rules:
*   **Single Column**: Never use double columns or complex tables; some parsers read left-to-right across columns.
*   **Plain Text**: Avoid images, progress bars, or icons (GitHub/LinkedIn icons are fine).
*   **Keyword Optimization**: Use the exact terminology from the Job Description (e.g., use 'React.js' if they ask for it, not just 'Frontend').
*   **Action Verbs**: Start bullets with strong verbs like 'Engineered', 'Optimized', or 'Scaled'.
*   **Metrics**: quantify your impact (e.g., 'Reduced API latency by 40%' instead of 'Worked on latency').

### Suggested Tools:
Use platforms like **Overleaf (LaTeX templates)** or simple Google Docs 'Resume' templates for the best parsing results.
""",

    r"\b(faang|maang|amazon|google|microsoft|facebook|meta|netflix)\b": """
**FAANG/MAANG** companies evaluate candidates on three distinct levels: Coding, System Design, and Cultural Fit.

### Success Checklist:
1. **DSA Mastery**: You must be able to solve LeetCode Medium/Hard problems in 20-30 minutes. Focus on Recursion, Trees, and Dynamic Programming.
2. **System Design (HLD/LLD)**: Understand how to design a distributed system (e.g., 'Design YouTube' or 'Design a Rate Limiter').
3. **Behavioral (Amazon Leadership Principles)**: For Amazon specifically, use the **STAR method** (Situation, Task, Action, Result) to answer behavioral questions.
4. **Communication**: Explain your thought process *while* you code. The interviewer wants to see *how* you think about constraints.
""",

    r"\b(java)\b": """
**Java** is the backbone of enterprise-grade backend systems and Android development.

### Roadmap for Placement:
*   **Core Java**: Master the 4 Pillars of OOP, Strings (Immutable), Exception Handling, and the **Collections Framework** (ArrayList vs HashMap vs TreeMap).
*   **JVM Internals**: Understand JIT compilation, Garbage Collection (G1GC), and Heap/Stack memory.
*   **Multithreading**: Learn about Synchronized blocks, Volatile variable, and the ExecutorService framework.
*   **Modern Java**: Get comfortable with Java 8+ features like **Streams** and **Lambdas**.
*   **Frameworks**: If aiming for backend, **Spring Boot** is mandatory. Master Dependency Injection (DI) and Inversion of Control (IoC).
""",

    r"\b(python)\b": """
**Python** is the primary choice for Data Science, AI, and rapid prototyping.

### Key Concepts for Interviews:
*   **List Comprehensions**: The most 'Pythonic' way to map/filter data.
*   **Memory Management**: Understand Python's reference counting and garbage collection.
*   **Decorators & Generators**: Vital for writing efficient, reusable code.
*   **GIL (Global Interpreter Lock)**: Know why Python isn't truly parallel for CPU-bound tasks.
*   **Libraries**: For web, learn **FastAPI** (Async) or **Django**. For AI/ML, focus on **Pandas, NumPy, and Scikit-Learn**.
""",

    r"\b(databases?|sql|dbms|mysql|postgresql|mongodb)\b": """
**Database Management Systems (DBMS)** are critical for almost every software role.

### Interview Hot-Topics:
1. **SQL vs NoSQL**: When to use ACID (Relational) vs CAP (Non-Relational).
2. **Normalization**: Master 1NF, 2NF, and 3NF. Be ready to explain why we sometimes 'de-normalize' for performance.
3. **Joins**: Understand Inner, Left, Right, and Full Outer joins with Venn diagrams.
4. **Indexing**: B-Trees vs Hash Indexes. Explain how indexing speeds up SELECT queries but slows down INSERTs.
5. **ACID Properties**: Atomicity, Consistency, Isolation, and Durability—the core principles of robust transactions.
""",
    r"\b(arrays?|strings?)\b": """
**Arrays and Strings** are the most common starting points for coding interviews.

### Must-Know Patterns:
*   **Two Pointers**: Used for sorted arrays, reversing strings, or finding pairs.
*   **Sliding Window**: Essential for 'Longest Substring' or 'Smallest Subarray' problems.
*   **Hash Maps**: Use them to count frequencies or store complements (like in 'Two Sum').
*   **String Manipulation**: Be comfortable with reversing, trimming, and checking palindromes without using built-in library shortcuts if asked.

### Pro-Tip:
Always ask about **Constraints** (e.g., 'Is the array sorted?', 'Does the string contain only lowercase letters?') before you start solving.
""",
    r"\b(recursion|backtracking)\b": """
**Recursion** is a method where the solution to a problem depends on solutions to smaller instances of the same problem.

### Key Framework:
1. **Base Case**: The condition where the recursion stops.
2. **Recursive Step**: Moving toward the base case.
3. **Stack Space**: Remember that each recursive call adds to the system stack, which can lead to 'StackOverflow' for deep recursion.

### Common Problems:
*   **Backtracking**: N-Queens, Sudoku Solver, and generating Permutations/Subsets.
*   **Divide & Conquer**: Merge Sort and Quick Sort.
""",
    r"\b(operating systems?|os)\b": """
**Operating Systems (OS)** interviews focus on how software interacts with hardware.

### Core Concepts:
*   **Processes vs. Threads**: A process is an independent execution unit; threads are paths of execution within a process that share memory.
*   **Scheduling**: Understand FCFS, Round Robin, and Priority Scheduling.
*   **Memory Management**: Paging, Segmentation, and Virtual Memory.
*   **Deadlocks**: Know the 4 necessary conditions (Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait).
""",
    r"\b(computer networks?|networking)\b": """
**Computer Networking** is vital for understanding how data travels across the internet.

### Essential Topics:
*   **OSI Model**: Know all 7 layers (Physical to Application) and which protocols belong to each.
*   **TCP vs. UDP**: Connection-oriented reliable delivery (TCP) vs. Connectionless fast delivery (UDP).
*   **HTTP/HTTPS**: Understand status codes (200, 404, 500) and how SSL/TLS encryption works.
*   **IP Addressing**: IPv4 vs IPv6 and the concept of Subnetting.
""",
    r"\b(skill gap|gap analysis|missing skills)\b": """
**Skill Gap Analysis** is the process of identifying the delta between your current proficiency and industry expectations.

### How to Bridge the Gap:
1. **Identify**: Use our 'Analyze Resume' feature to see which keywords you are missing for your target role.
2. **Prioritize**: Focus on 'Core CS Fundamentals' first, then 'Frameworks' (React/Node), and finally 'Cloud/DevOps'.
3. **Practice**: Bridge coding gaps with 2-3 targeted LeetCode problems daily for your weakest data structures.
4. **Certify**: If a gap is in a specific tool (e.g., AWS, Docker), consider a hands-on project or a basic certification to prove your knowledge.
""",
    r"\b(roadmaps?|learning path|plan)\b": """
A **Placement Roadmap** should be structured, time-bound, and focused on high-ROI topics.

### 90-Day Winning Path:
*   **Month 1: Fundamentals**: Language deep-dive (Java/Python/C++) + basic DSA (Arrays, Strings, Recursion).
*   **Month 2: Core Engineering**: System Design basics + OS/DBMS/Networking + Advanced DSA (Trees, Graphs, DP).
*   **Month 3: Professional Polish**: Resume optimization + Mock Interviews + 2 Full-Stack Projects.

### Pro-Tip:
Don't get stuck in 'Tutorial Hell'. For every 1 hour of watching a tutorial, spend 2 hours actually coding or solving problems.
""",
    r"\b(two pointers?|sliding window|prefix sum|kadane)\b": """
**Two Pointers** and **Sliding Window** are highly efficient techniques to solve array and string problems with O(N) time complexity.

### Core Techniques:
*   **Two Pointers**: Used for searching pairs (Two Sum in sorted array), reversing pointers, or partitioning (Dutch National Flag).
*   **Sliding Window**: Ideal for finding sub-sequences or sub-arrays under a constraint (e.g., 'Longest Substring with K unique characters').
*   **Prefix Sum**: Used for range-sum queries in O(1) time after O(N) preprocessing.

### Why It Matters:
Companies like Amazon and Goldmann Sachs often ask these patterns to evaluate your ability to optimize from O(N²) to a linear O(N) solution.
""",
    r"\b(time complexity|space complexity|big o|omega|theta)\b": """
**Big O Notation** is used to describe the efficiency of an algorithm as a function of the input size (n).

### Common Complexities (Best to Worst):
1. **O(1) - Constant**: Accessing an index in an array.
2. **O(log N) - Logarithmic**: Binary Search.
3. **O(N) - Linear**: Iterating through a list once.
4. **O(N log N) - Linearithmic**: Efficient sorting (Merge Sort, Quick Sort).
5. **O(N²) - Quadratic**: Nested loops (Bubble Sort).
6. **O(2ⁿ) - Exponential**: Recursive Fibonacci without memoization.

### Interview Implementation:
Always start your explanation by stating the complexity. If your space complexity is O(N) due to a hash map, explicitly mention it and ask if you can optimize it further.
""",
    r"\b(greedy|bit manipulation|heaps)\b": """
**Greedy Algorithms** make the locally optimal choice at each step with the hope of finding a global optimum.

### Key Examples:
*   **Activity Selection**: Sorting by finish times.
*   **Huffman Coding**: Frequency-based compression.
*   **Dijkstra's Algorithm**: Also uses a greedy approach via a Priority Queue (Heap).

### Note on Bit Manipulation:
Master XOR properties (e.g., `x ^ x = 0`, `x ^ 0 = x`). It's commonly used in 'Find the single number' or 'Power of two' interview questions.
""",
    r"\b(hello|hi|hey|help)\b": "Hello! I am your **PlaceIQ AI Assistant**. I can provide deep industry roadmaps, help with **Resume ATS optimization**, evaluate your **Mock Interview** answers, or provide study paths for **Time Complexity, Two Pointers, Greedy logic, DSA, OS, Networking, and FAANG prep**. What can I help you with today?"
}

def get_hf_token():
    return os.getenv("HF_API_TOKEN")

def get_fast_faq_response(message: str, domain: Optional[str]) -> Optional[str]:
    msg_lower = message.lower()
    base_response = None
    for pattern, response in FAQ_KNOWLEDGE_BASE.items():
        if re.search(pattern, msg_lower):
            base_response = response.strip()
            break
            
    if base_response and domain:
        # Add domain-specific extension if applicable
        if "dsa" in msg_lower or "interview" in msg_lower:
            base_response += f"\n\n### 🌍 Domain Specific Advice ({domain}):\nAs someone targeting a **{domain}** role, prioritize how these concepts apply to production. For instance, in an interview, focus on how efficient algorithms directly impact server costs and user experience in {domain} systems."
            
    return base_response

def call_huggingface_model_stream(model_id: str, messages: List[Dict[str, str]], token: str):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Format for Zephyr/Mistral style
    prompt = ""
    for m in messages:
        if m["role"] == "system":
            prompt += f"<|system|>\n{m['content']}</s>\n"
        elif m["role"] == "user":
            prompt += f"<|user|>\n{m['content']}</s>\n"
        elif m["role"] == "assistant":
            prompt += f"<|assistant|>\n{m['content']}</s>\n"
    prompt += "<|assistant|>\n"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.5,
            "return_full_text": False
        },
        "stream": True
    }
    
    endpoint = f"{HF_INFERENCE_URL}/{model_id}"
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=90, stream=True)
    resp.raise_for_status()
    
    for line in resp.iter_lines():
        if not line:
            continue
            
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data_content = line_str[6:]
            try:
                data_json = json.loads(data_content)
                token_text = data_json.get('token', {}).get('text', '')
                if token_text:
                    yield token_text
            except (json.JSONDecodeError, KeyError):
                continue

@router.post("/chat")
async def chat_with_assistant(req: ChatRequest):
    token = get_hf_token()
    domain = req.target_role or "Software Developer"

    # --- 1. INSTANT KNOWLEDGE BASE ROUTING (High Quality & Multi-Paragraph) ---
    fast_response = get_fast_faq_response(req.message, domain)
    if fast_response:
        async def fast_stream_generator():
            # Breakdown into chunks to simulate high-speed terminal typing
            lines = fast_response.split('\n')
            for line in lines:
                words = line.split(' ')
                for i in range(0, len(words), 5):
                    chunk = " ".join(words[i:i+5]) + " "
                    yield chunk
                    await asyncio.sleep(0.01)
                yield "\n"
        return StreamingResponse(fast_stream_generator(), media_type="text/plain")

    # --- 2. AI FALLBACK WITH MULTI-MODEL FAILOVER ---
    if not token:
        return {"response": "Placement Assistant features are active, but AI model connection requires a token.", "mode": "error"}

    system_instructions = (
        f"You are 'PlaceIQ AI', a career mentor specialized in {domain}. "
        "Provide very detailed, accurate, and multi-paragraph answers. "
        "Use technical terms accurately and offer actionable advice based on 2024 hiring trends. "
        "Strictly avoid hallucination. If you don't know, suggest a roadmap to find out."
    )

    messages = [
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": f"USER PROFILE: CGPA: {req.cgpa}, Skills: {req.skills}\n\nUSER MESSAGE: {req.message}"}
    ]

    async def stream_generator_with_failover():
        # Try multiple models if one is busy
        for model in HF_MODELS:
            try:
                logger.info(f"Attempting chat generation with model: {model}")
                has_yielded = False
                for chunk in call_huggingface_model_stream(model, messages, token):
                    if chunk:
                        yield chunk
                        has_yielded = True
                if has_yielded:
                    return # Success!
            except Exception as e:
                logger.error(f"Model {model} failed: {e}")
                continue # Try next model
        
        # Absolute final fallback if all models fail
        yield f"\n\n### 🤖 Note: High Traffic\nOur AI models are currently processing a high volume of requests. While you wait, you can ask about **Resume ATS basics**, **FAANG prep**, or **DSA roadmaps**, which use our instant curated engine!"

    return StreamingResponse(stream_generator_with_failover(), media_type="text/plain")
