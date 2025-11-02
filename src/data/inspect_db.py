"""Module for collecting static analysis reports into the database."""

import sqlite3
from pathlib import Path
import pandas as pd


def inspect_database(db_path="code_review.db"):
    """
    Opens the SQLite database and
    prints sample rows from analysis_results table.
    """
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"Database file'{db_path}' not found")
        return

    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    try:
        # List all tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print("Tables in the database:", tables)

        # Read the analysis_results table
        if "analysis_results" in tables:
            d = pd.read_sql_query("SELECT*FROM analysis_results LIMIT 9", conn)
            print("\n Sample data from 'analysis_results':")
            print(d)
        else:
            print("No 'analysis_results' table found yet.")
    finally:
        conn.close()


if __name__ == "__main__":
    inspect_database()
