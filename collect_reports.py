"""
collect_reports.py

Collects raw linting and static analysis reports
(pylint, flake8, bandit, mypy),
saves them into JSON, and stores normalized issues in SQLite.
"""

import json
import sqlite3
import subprocess  # nosec B404
from datetime import datetime
from pathlib import Path

RAW_REPORTS_DIR = Path("raw_reports")
RAW_REPORTS_DIR.mkdir(exist_ok=True)


def run_tool(name: str, cmd: list[str], output_file: str) -> None:
    """
    Run a linting tool as a subprocess and save its output.

    Args:
        name: Tool name (e.g., pylint).
        cmd: Command list to execute.
        output_file: Path to save the output.
    """
    try:
        result = subprocess.run(  # nosec B603
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write(result.stdout)

        print(f"[{name}] output saved to {output_file}")

    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error running {name}: {exc}")


def normalize_pylint(file_path: str) -> list[dict]:
    """
    Normalize pylint JSON output into issue dicts.
    """
    with open(file_path, "r", encoding="utf-8") as f_in:
        try:
            data = json.load(f_in)
        except json.JSONDecodeError:
            return []

    issues = []
    for item in data:
        issues.append({
            "file": item.get("path"),
            "tool": "pylint",
            "message": item.get("message"),
            "type": item.get("type"),
            "line": item.get("line"),
            "column": item.get("column"),
            "code": item.get("symbol"),
            "severity": (
                "warning" if item.get("type") == "convention" else "error"
            ),
            "timestamp": datetime.utcnow().isoformat(),
        })
    return issues


def save_to_db(issues: list[dict], db_file: str = "reports.db") -> None:
    """
    Save normalized issues into SQLite.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lint_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            tool TEXT,
            message TEXT,
            type TEXT,
            line INTEGER,
            column INTEGER,
            code TEXT,
            severity TEXT,
            timestamp TEXT
        )
        """
    )

    for issue in issues:
        cursor.execute(
            """
            INSERT INTO lint_issues
            (file, tool, message, type, line, column,
             code, severity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                issue["file"],
                issue["tool"],
                issue["message"],
                issue["type"],
                issue["line"],
                issue["column"],
                issue["code"],
                issue["severity"],
                issue["timestamp"],
            ),
        )

    conn.commit()
    conn.close()
    print(f"Saved {len(issues)} issues to {db_file}")


def main() -> None:
    """
    Entry point: run tools, normalize output, and save to DB.
    """
    # Example: run pylint (others like flake8, bandit can be added similarly)
    run_tool(
        "pylint",
        ["pylint", "src", "tests", "--output-format=json"],
        "raw_reports/pylint.json"
    )

    pylint_issues = normalize_pylint("raw_reports/pylint.json")
    save_to_db(pylint_issues)


if __name__ == "__main__":
    main()
