import json
import random

def generate_gh002_ground_truth():
    cases = []
    statuses = ["PASS", "FAIL", "UNKNOWN"]
    for i in range(1, 101):
        repo_name = f"owner/repo_{i}"
        status = random.choice(statuses)
        
        # Match evidence model logic
        if status == "PASS":
            protected = True
        elif status == "FAIL":
            protected = False
        else:
            protected = None
            
        case = {
            "repository": repo_name,
            "status": status,
            "evidence": {
                "default_branch": "main",
                "protection_enabled": protected
            }
        }
        cases.append(case)
        
    return cases

if __name__ == "__main__":
    import os
    os.makedirs("data/ground_truth", exist_ok=True)
    with open("data/ground_truth/gh002_ground_truth.json", "w") as f:
        json.dump(generate_gh002_ground_truth(), f, indent=2)
