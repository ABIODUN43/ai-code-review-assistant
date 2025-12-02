import json
from pathlib import Path


reports_dir = Path("data/raw_reports")


def load_reports():
    """Load and merge all JSON lint reports"""
    data = []
    for file in reports_dir.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
                if isinstance(content, list):
                    data.extend(content)
            except json.JSONDecodeError:
                # Skip invalid JSON files safely
                pass
    return data


if __name__ == "__main__":
    all_reports = load_reports()
    print(f"Loaded {len(all_reports)} issues from linters.")
