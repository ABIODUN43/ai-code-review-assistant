# src/ai_feedback/generate_feedback.py
"""
Generate AI feedback for code + tool findings using OpenAI API.
Saves a local cache (SQLite) and logs all feedback to feedback_log.jsonl.
"""
from __future__ import annotations
import json
import os
import logging
import sqlite3
import hashlib
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt
from tenacity import wait_exponential, retry_if_exception_type
from dotenv import load_dotenv
from src.data.feedback_storage import save_feedback

# --- Environment Setup ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "1"))

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env file.")

# --- OpenAI client ---
try:
    from openai import OpenAI
except Exception as e:
    raise RuntimeError("Failed to import OpenAI client.") from e

client = OpenAI(api_key=OPENAI_API_KEY)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_feedback")

# --- SQLite Cache ---
DB_PATH = os.path.join(os.getcwd(), "code_review.db")


def ensure_feedback_table() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_feedback_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_hash TEXT UNIQUE,
            code TEXT,
            tool_findings TEXT,
            feedback TEXT,
            model TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def compute_simple_hash(code: str, tool_findings: List[Dict[str, Any]]) -> str:
    key = json.dumps(
        {"code": code, "tool_findings": tool_findings}, sort_keys=True
        )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def get_cached_feedback(code_hash: str) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT feedback FROM ai_feedback_cache WHERE code_hash = ?",
        (code_hash,),
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def save_feedback_to_cache(
        code_hash: str,
        code: str,
        tool_findings: List[Dict[str, Any]],
        feedback: str,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO ai_feedback_cache
        (code_hash, code, tool_findings, feedback, model)
        VALUES (?, ?, ?, ?, ?)
        """,
        (code_hash, code, json.dumps(tool_findings), feedback, MODEL),
    )
    conn.commit()
    conn.close()


def log_feedback_to_file(entry: Dict[str, Any]) -> None:
    """Append each generated feedback to feedback_log.jsonl"""
    with open("feedback_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def build_prompt(code: str, tool_findings: List[Dict[str, Any]]) -> str:
    """
    Strong prompt that produces clear, useful feedback.
    """
    findings_text = "\n".join([f"- {f}" for f in tool_findings])
    return f"""
You are a senior Python code reviewer.
Analyze the code below and the findings provided.

Your job:
1. Combine the tool findings and your own analysis.
2. Return concise, prioritized feedback the developer can act on.
3. If no major issue exists, give a short positive remark.

Provide your output in this JSON format:
{{
  "feedback": "<overall summary>",
  "suggestions": [
    {{
      "explanation": "<what’s wrong or can be improved>",
      "fix": "<corrected or improved code snippet or advice>",
      "severity": "low|medium|high"
    }}
  ]
}}

Code:
{code}

Findings:
{findings_text}
"""


# --- Retry & Model Call ---
@retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
)
def call_model(prompt: str) -> str:
    logger.info("Calling model %s", MODEL)

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system",
                    "content": "You are an expert Python code reviewer."},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=512,
        )
        content = resp.choices[0].message.content
        return content.strip() if content else "No feedback returned."
    except Exception as e:
        logger.error("Model call failed: %s", e)
        raise


def generate_feedback(
        code: str,
        tool_findings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    ensure_feedback_table()
    code_hash = compute_simple_hash(code, tool_findings)

    cached = get_cached_feedback(code_hash)
    if cached:
        logger.info("Using cached feedback")
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            return {"feedback": cached}

    prompt = build_prompt(code, tool_findings)
    raw = call_model(prompt)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"feedback": raw}

    save_feedback_to_cache(code_hash, code, tool_findings, json.dumps(parsed))
    log_feedback_to_file({
        "code": code,
        "findings": tool_findings,
        "response": parsed
    })
    return parsed


if __name__ == "__main__":
    sample_code = """
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] != None:
            result.append(data[i]*2)
    return result
"""

    sample_findings = [
        "Code does not follow PEP8 naming conventions.",
        "Inefficient iteration using range(len(data)).",
        "Possible bug if data contains non-numeric types.",
        "Missing type hints for parameters and return value."
    ]

    structured_sample_findings = [{"message": msg} for msg in sample_findings]
    out = generate_feedback(sample_code, structured_sample_findings)
    print(json.dumps(out, indent=2))
    # Example unique ID (could be file name or hash of the code snippet)
    code_id = "sample_code_01"
    save_feedback(code_id, MODEL, out)
