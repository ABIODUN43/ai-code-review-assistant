An AI-powered code review assistant that automatically analyzes Python code for bugs, style issues, security vulnerabilities, and optimization opportunities.
It combines static analysis tools (PyLint, Flake8, Bandit) with AI/ML models to provide natural language explanations and fix suggestions.
This project is designed as part of my preparation for a Meta Software Engineering Internship, with a focus on showcasing skills in AI, software engineering, and systems integration

ROAD MAP OUTLINE

(1) Foundations
 Project Setup (repo, Docker, static tools, CI pipeline)
 Data Collection (GitHub PRs, CodeReviewDataset, CodeXGLUE)
 Data Preprocessing (AST parsing, cleaning, splitting dataset)
 (2) CORE ENGINE
 Static Rules Engine (wrap PyLint, Flake8, Bandit outputs)
 ML/LLM Integration (CodeBERT, StarCoder, or GPT API)
 Merge + Rank Layer (deduplication, severity ranking)
(3)APPLICATION LAYER
CLI Tool MVP (ai-review myscript.py)
API Backend (FastAPI service /review)
GitHub Action Integration (auto-review PRs with comments)
(4)Advanced & Showcase
Optimization & Security Checks
VS Code Extension (inline feedback)
Evaluation + Showcase (README, screenshots, demo repo)


SET UP INSTRUCTIONS
1. Clone the Repository
git clone https://github.com/ABIODUN43/ai-code-review-assistant.git
cd ai-code-review-assistant

2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Run Static Tools
Test on a file test.py:

pylint test.py
flake8 test.py
bandit test.py

5. Run Docker (optional)
docker build -t ai-code-review .
docker run -it ai-code-review
