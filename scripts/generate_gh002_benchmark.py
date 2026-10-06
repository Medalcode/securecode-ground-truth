"""Generator script for GH-002 synthetic benchmark dataset."""

from pathlib import Path
import sys

# Ensure root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gen_gh002 import generate_gh002_ground_truth

if __name__ == "__main__":
    cases = generate_gh002_ground_truth()
    print(f"GH-002 Benchmark generator ready: {len(cases)} cases available.")
