import json
from src.ai.hybrid_reviewer import HybridReviewer

sample_code = """
def add(a,b):
  return a+  b
"""

reviewer = HybridReviewer()
out = reviewer.review(sample_code)

print(json.dumps(out, indent=2))
