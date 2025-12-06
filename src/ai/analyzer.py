# src/ai/analyzer.py
"""
Week 5: Basic AI Analyzer
Combines static (rule-based) and AI feedback into categorized suggestions.
"""

import json
import logging
from typing import List, Dict, Any
from src.ai_feedback.generate_feedback import generate_feedback


logger = logging.getLogger("ai_analyzer")
logging.basicConfig(level=logging.INFO)


def categorize_suggestion(issue: dict | str) -> str:
    """
    Simple keyword-based categorization of suggestions.
    Later can be replaced with an ML classifier.
    """
    if isinstance(issue, dict):
        text = issue.get("text", "")
    else:
        text = str(issue)
    text_lower = text.lower()
    if any(
        k in text_lower
        for k in [
            "readability", "naming",
            "comment",  "docstring",
            "format", "pep8",
        ]
    ):
        return "readability"
    if any(
        k in text_lower
        for k in [
            "optimize",
            "performance",
            "efficiency",
            "speed",
            "memory",
        ]
    ):
        return "performance"
    if any(
        k in text_lower
        for k in [
            "security",
            "vulnerability",
            "injection",
            "auth",
            "encrypt"
        ]
    ):
        return "security"
    if any(
        k in text_lower
        for k in [
            "pattern",
            "architecture",
            "design",
            "structure"
        ]
    ):
        return "design_pattern_violations"
    return "general"


def analyze_code_with_ai(
        code: str,
        issues: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Combines AI feedback with rule-based issues.
    Returns categorized results.
    """
    logger.info("Running AI analyzer...")

    # Convert issues to dict format if user/tool passed simple strings
    normalized_issues = []
    for issue in issues:
        if isinstance(issue, dict):
            normalized_issues.append({
                "text": issue.get("text", ""),
                "severity": issue.get("severity", "medium"),
                "tool": issue.get("tool", "static")
            })
        else:
            normalized_issues.append(
                {"text": str(issue), "severity": "medium"}
            )

    # Step 1: Get AI feedback
    ai_feedback = generate_feedback(code, normalized_issues)

    # Step 2: Merge rule-based + AI findings
    all_suggestions = []

    # From rule-based
    for issue in normalized_issues:
        all_suggestions.append({
            "source": issue.get("tool", "rule_based"),
            "text": issue.get("text", ""),
            "category": categorize_suggestion(issue),
            "severity": issue.get("severity", "medium")
        })

    # From AI feedback
    if "suggestions" in ai_feedback:
        for s in ai_feedback["suggestions"]:
            all_suggestions.append({
                "source": "ai",
                "text": s.get("explanation", ""),
                "fix": s.get("fix", ""),
                "severity": s.get("severity", "low"),
                "category": categorize_suggestion(s.get("explanation", "")),
            })
    else:
        all_suggestions.append({
            "source": "ai",
            "text": ai_feedback.get("feedback", ""),
            "category": categorize_suggestion(ai_feedback.get("feedback", "")),
            "severity": "low",
        })

    # Step 3: Group by category
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for s in all_suggestions:
        cat = s["category"]
        grouped.setdefault(cat, []).append(s)

    result = {
        "summary": f"Analyzed {len(issues)} rule-based issues + AI feedback.",
        "grouped_suggestions": grouped
    }

    logger.info("AI analysis complete.")
    return result


if __name__ == "__main__":
    # --- Example test run ---
    sample_code = """
    def process_data(data):
        result = []
        for i in range(len(data)):
            if data[i] != None:
                result.append(data[i]*2)
        return result
    """

    sample_issues = [
        {"text": "Code does not follow PEP8 naming conventions.",
            "severity": "medium"},
        {"text": "Inefficient iteration using range(len(data)).",
            "severity": "medium"},
        {"text": "Possible bug if data contains non-numeric types.",
            "severity": "medium"},
        {"text": "Missing type hints for parameters and return value.",
            "severity": "medium"}
    ]

    analysis = analyze_code_with_ai(sample_code, sample_issues)
    print(json.dumps(analysis, indent=2))
