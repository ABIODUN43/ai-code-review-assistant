import logging
from typing import List, Dict, Any

from src.ai.analyzer import analyze_code_with_ai
from src.ai.static_tools import run_static_tools
from src.db.session import save_analysis_result


class HybridReviewer:
    """
    Combines static rule-based tools (flake8, pylint, bandit)
    with AI-powered code review feedback.
    """

    def __init__(self):
        self.tools = ["flake8", "pylint", "bandit"]
        logging.info("Hybrid Reviewer initialized with tools: %s", self.tools)

    def review(self, code: str) -> Dict[str, Any]:
        """
        Runs static tools + AI reasoning.
        Returns structured review report.
        """

        # 1. Static-analysis output: List[Dict]
        base_issues: List[Dict[str, Any]] = run_static_tools(code)

        # 2. AI returns a dict — so annotate correctly
        ai_feedback: Dict[str, Any] = analyze_code_with_ai(code, base_issues)

        # 3. Merge both into final dict
        final_report: Dict[str, Any] = merge_results(base_issues, ai_feedback)

        # 4. Save to DB
        save_analysis_result(code, final_report)

        return final_report


def merge_results(
    base_issues: List[Dict[str, Any]],
    ai_feedback: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Combine static tool issues with AI insights.
    """
    return {
        "static_analysis": base_issues,
        "ai_analysis": ai_feedback,
        "total_issues": len(base_issues)
    }
