"""Module for collecting static analysis reports into the database."""

import sqlite3
from pathlib import Path


def initialize_database(db_path="code_review.db"):
    """Create database schema for AI Code Review Assistant."""
    db_file = Path(db_path)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table for raw static analysis results
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        tool TEXT NOT NULL,
        line INTEGER,
        severity TEXT,
        message TEXT,
        rule_id TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    # Optional: logs for preprocessing
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS preprocessing_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        process_name TEXT,
        status TEXT,
        processed_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {db_path}")


if __name__ == "__main__":
    initialize_database()
