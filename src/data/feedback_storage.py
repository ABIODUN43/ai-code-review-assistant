import json
from datetime import datetime
from pathlib import Path

storage_dir = Path("data/feedback_results")
storage_dir.mkdir(parents=True, exist_ok=True)


def save_feedback(code_id: str, model_name: str, feedback_data: dict):
    """Save model feedback with timestamp and model info."""
    feedback_record = {
        "code_id": code_id,
        "model_name": model_name,
        "timestamp": datetime.now().isoformat(),
        "feedback": feedback_data,
    }
    output_path = storage_dir / f"{code_id}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feedback_record, f, indent=2)
    print(f"✅ Feedback saved to {output_path}")


def load_feedback(code_id: str):
    """Load saved feedback for a specific code snippet."""
    file_path = storage_dir / f"{code_id}.json"
    if not file_path.exists():
        print(f"❌ No feedback found for {code_id}")
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
