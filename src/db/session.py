import sqlite3
import json
from datetime import datetime

DB_PATH = "analysis.db"


def save_analysis_result(code: str, report: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            report TEXT,
            created_at TEXT
        )
    """)

    cursor.execute(
        """INSERT INTO analysis_results (code, report, created_at)
        VALUES (?, ?, ?)""",
        (code, json.dumps(report), datetime.now().isoformat())
    )

    conn.commit()
    conn.close()
