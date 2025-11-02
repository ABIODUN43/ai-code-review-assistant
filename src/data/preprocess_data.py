"""preprocess and clean analysis results."""

import sqlite3
import datetime


def normalize_severity_levels():
    """Normalize severity level (low,medium,high)."""

    conn = sqlite3.connect("code_review.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    UPDATE issues
    SET severity = CASE
        WHEN severity IN ('error', 'high', 'critical') THEN 'high'
        WHEN severity IN ('warning', 'medium') THEN 'medium'
        ELSE 'low'
    END
    """
    )
    conn.commit()
    conn.close()


def deduplicate_issues():
    """duplicate issues"""
    conn = sqlite3.connect("code_review.db")
    cursor = conn.cursor()

    cursor.execute(
        """
    DELETE FROM issues
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM issues
        GROUP BY file, tool, line, column, code, message
    )
    """
    )
    conn.commit()
    conn.close()


def log_step(step, status):
    """log function"""
    conn = sqlite3.connect("code_review.db")
    cursor = conn.cursor()
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    cursor.execute(
        """INSERT INTO preprocessing_log(step, status, timestamp)
        VALUES(?, ?, ?)""",
        (step, status, timestamp),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    normalize_severity_levels()
    log_step("normalize_severity", "done")

    deduplicate_issues()
    log_step("deduplicate", "done")

    print("Data preprocessing complete!")
