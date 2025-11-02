"""
Collect and save static analysis results (e.g., pylint, flake8)
into the local SQLite database.

This module runs static code analysis tools, parses their output,
and stores the results in the `analysis_results` table for later
AI-based analysis and preprocessing.
"""

from __future__ import annotations
import subprocess  # nosec B404
import datetime
import sqlite3
from pathlib import Path
import json
from typing import List, Dict, Any

DB_PATH = Path("code_review.db")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def ensure_db_schema() -> None:
    """Ensure the `analysis_results` table exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            tool TEXT,
            line INTEGER,
            severity TEXT,
            message TEXT,
            rule_id TEXT,
            timestamp TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def run_tool(command: list[str], tool_name: str) -> List[Dict[str, Any]]:
    """Run a static analysis tool safely and return parsed results."""
    try:
        result = subprocess.run(  # nosec B603
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout.strip()
        timestamp = datetime.datetime.now(datetime.UTC).isoformat()

        if not output:
            return []

        try:
            data = json.loads(output)
            if isinstance(data, dict):
                data = [data]
        except (ValueError, json.JSONDecodeError):
            data = [
                {"tool": tool_name, "message": line, "timestamp": timestamp}
                for line in output.splitlines()
            ]

        normalized = [
            {
                "filename": entry.get("path")
                or entry.get("filename")
                or "unknown_file",
                "line": entry.get("line", 0),
                "severity": entry.get("type") or entry.get("severity", "info"),
                "message": entry.get("message", "").strip(),
                "rule_id": entry.get("symbol") or entry.get("rule_id", ""),
                "timestamp": entry.get("timestamp", timestamp),
            }
            for entry in data
        ]

        return normalized

    except FileNotFoundError:
        print(f"⚠️ {tool_name} not installed or not found in PATH.")
        return []
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decode error in {tool_name}: {e}")
        return []
    except Exception as e:  # pylint: disable=broad-except
        print(f"⚠️ Unexpected error running {tool_name}: {e}")
        return []


def save_to_db(results: List[Dict[str, Any]], tool_name: str) -> None:
    """Insert collected results into the database."""
    if not results:
        print(f"No results to save for {tool_name}.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for entry in results:
        cursor.execute(
            """
            INSERT INTO analysis_results (
                filename, tool, line, severity, message, rule_id, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["filename"],
                tool_name,
                entry["line"],
                entry["severity"],
                entry["message"],
                entry["rule_id"],
                entry["timestamp"],
            ),
        )

    conn.commit()
    conn.close()
    print(f"✅ {len(results)} issues saved from {tool_name}.")


def collect_all_reports() -> None:
    """Run all supported tools and collect their results."""
    print("🔍 Running static analysis tools...")
    ensure_db_schema()

    tools = {
        "pylint": ["pylint", "src", "--output-format=json"],
        "flake8": ["flake8", "src", "--format=json"],
    }

    all_results: list[dict[str, Any]] = []

    for tool_name, command in tools.items():
        print(f"▶️ Running {tool_name}...")
        results = run_tool(command, tool_name)
        save_to_db(results, tool_name)
        all_results.extend(results)

    print(f"📊 Done — {len(all_results)} total issues recorded.")


if __name__ == "__main__":
    collect_all_reports()
