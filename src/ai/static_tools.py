import subprocess  # nosec B404
import logging  # nosec B404
from typing import List, Dict, Any  # nosec B404


logger = logging.getLogger("static_tools")


def run_tool(cmd: List[str]) -> str:
    """Run a CLI tool and return raw stdout text."""
    try:
        result = subprocess.run(  # nosec B603
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout
    except (subprocess.CalledProcessError, OSError) as e:
        logger.error(f"Static analysis failed: {e}")
        return ""


def parse_output(raw: str, tool_name: str) -> List[Dict[str, Any]]:
    """Normalize raw output into issue dicts."""
    if not raw.strip():
        return []

    return [
        {"tool": tool_name, "text": line.strip(), "severity": "medium"}
        for line in raw.splitlines()
        if line.strip()
    ]


def run_static_tools(code: str) -> List[Dict[str, Any]]:
    """Run flake8, pylint, bandit and return normalized issues."""
    tmp_file = "tmp_review.py"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(code)

    tools = {
        "flake8": ["flake8", tmp_file],
        "pylint": ["pylint", tmp_file, "--output-format=text"],
        "bandit": ["bandit", "-r", tmp_file, "-f", "txt"],
    }

    all_issues = []

    for tool_name, cmd in tools.items():
        raw = run_tool(cmd)
        parsed = parse_output(raw, tool_name)
        all_issues.extend(parsed)

    return all_issues
