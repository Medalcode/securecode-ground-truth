import json
from pathlib import Path
from securecode.models.gh001 import GH001Evidence
from securecode.engine.evaluator import evaluate_gh001, EvaluationStatus

def test_gh001_ground_truth_cases():
    """
    Integration test that loads the empirical Ground Truth JSON,
    constructs the GH001Evidence objects, and validates that the 
    core evaluator logic strictly produces the expected status.
    """
    # Robust path resolution independent of CWD
    test_dir = Path(__file__).resolve().parent
    repo_root = test_dir.parent.parent
    gt_path = repo_root / "data" / "ground_truth" / "gh001_ground_truth.json"
    
    assert gt_path.exists(), f"Ground Truth file not found at {gt_path}"
    
    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)
        
    cases = gt_data.get("cases", [])
    assert len(cases) == 6, f"Expected 6 cases, found {len(cases)}"
    
    for case in cases:
        case_id = case["case_id"]
        expected_approvals = case["expected_approvals"]
        expected_dismiss_stale = case["expected_dismiss_stale"]
        expected_status_str = case["expected_status"]
        
        # Convert expected status string to Enum
        expected_status = EvaluationStatus(expected_status_str)
        
        # Construct the immutable evidence model
        evidence = GH001Evidence(
            required_review_approvals=expected_approvals,
            dismiss_stale_reviews=expected_dismiss_stale
        )
        
        # Evaluate
        actual_status = evaluate_gh001(evidence)
        
        # Assert actual vs expected
        assert actual_status == expected_status, (
            f"Case {case_id} failed: "
            f"Expected {expected_status}, got {actual_status} "
            f"(approvals={expected_approvals}, dismiss={expected_dismiss_stale})"
        )
