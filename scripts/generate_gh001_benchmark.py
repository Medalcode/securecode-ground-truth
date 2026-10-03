import json
import random
from pathlib import Path

def oracle_label(approvals, dismiss_stale):
    if approvals is None or dismiss_stale is None:
        return "UNKNOWN"
    if approvals >= 2 and dismiss_stale is True:
        return "PASS"
    return "FAIL"

def generate_cases():
    cases = []
    case_id_counter = 1
    
    def add_case(family, app, ds):
        nonlocal case_id_counter
        cases.append({
            "case_id": f"GT-GH001-BENCH-{case_id_counter:03d}",
            "control": "GH-001",
            "scenario_family": family,
            "description": f"Synthetic benchmark case for {family}",
            "evidence": {
                "required_review_approvals": app,
                "dismiss_stale_reviews": ds
            },
            "expected_status": oracle_label(app, ds),
            "rationale": "Generated via independent Ground Truth oracle specification."
        })
        case_id_counter += 1

    # Generate 35 PASS cases
    # approvals >= 2, dismiss = True
    for _ in range(15):
        add_case("PASS - approvals=2, dismiss=true", 2, True)
    for _ in range(20):
        add_case("PASS - approvals>2, dismiss=true", random.randint(3, 6), True)
        
    # Generate 35 FAIL cases
    # approvals = 0, dismiss = True (10)
    for _ in range(10):
        add_case("FAIL - approvals=0, dismiss=true", 0, True)
    # approvals = 1, dismiss = True (10)
    for _ in range(10):
        add_case("FAIL - approvals=1, dismiss=true", 1, True)
    # approvals >= 2, dismiss = False (10)
    for _ in range(10):
        add_case("FAIL - approvals>=2, dismiss=false", random.randint(2, 6), False)
    # approvals < 2, dismiss = False (5)
    for _ in range(5):
        add_case("FAIL - multiple violations", random.randint(0, 1), False)
        
    # Generate 35 UNKNOWN cases
    # approvals = None, dismiss = True/False (15)
    for _ in range(15):
        add_case("UNKNOWN - missing approvals", None, random.choice([True, False]))
    # approvals >= 0, dismiss = None (15)
    for _ in range(15):
        add_case("UNKNOWN - missing dismiss_stale", random.randint(0, 6), None)
    # both None (5)
    for _ in range(5):
        add_case("UNKNOWN - missing both", None, None)
        
    return cases

def main():
    cases = generate_cases()
    
    # Shuffle for a realistic benchmark (fixed seed for reproducibility)
    random.seed(42)
    random.shuffle(cases)
    
    dataset = {
        "dataset_name": "GH-001 Synthetic Benchmark 100+",
        "control": "GH-001",
        "total_cases": len(cases),
        "cases": cases
    }
    
    out_dir = Path(__file__).parent.parent / "data" / "ground_truth"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "gh001_benchmark_105.json"
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"Generated {len(cases)} synthetic ground truth cases at {out_path}")

if __name__ == "__main__":
    main()
