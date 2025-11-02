""" not sure of it usage yet"""

import sqlite3

conn = sqlite3.connect("reports.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM lint_issues;")
print("Total issues:", cursor.fetchone()[0])

cursor.execute("SELECT tool, COUNT(*) FROM lint_issues GROUP BY tool;")
print("Issues per tool:", cursor.fetchall())

cursor.execute("SELECT file, message FROM lint_issues LIMIT 5;")
print("Sample issues:", cursor.fetchall())
