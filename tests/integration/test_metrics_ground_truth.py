import json
from pathlib import Path
from securecode.models.gh001 import GH001Evidence
from securecode.engine.evaluator import evaluate_gh001, EvaluationStatus
from benchmark.metrics import calculate_metrics

def test_metrics_against_ground_truth():
    """
    Load the Ground Truth JSON, evaluate evidence via GH001 evaluator,
    and calculate overall metrics, confirming that the current logic
    achieves a perfect score across the 6 cases.
    """
    test_dir = Path(__file__).resolve().parent
    repo_root = test_dir.parent.parent
    gt_path = repo_root / "data" / "ground_truth" / "gh001_ground_truth.json"
    
    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)
        
    cases_pairs = []
    
    for case in gt_data.get("cases", []):
        expected_status = EvaluationStatus(case["expected_status"])
        
        evidence = GH001Evidence(
            required_review_approvals=case["expected_approvals"],
            dismiss_stale_reviews=case["expected_dismiss_stale"]
        )
        
        actual_status = evaluate_gh001(evidence)
        cases_pairs.append((expected_status, actual_status))
        
    result = calculate_metrics(cases_pairs)
    
    # 1 PASS, 3 FAIL, 2 UNKNOWN expected from the Ground Truth
    assert result.true_positive == 3
    assert result.true_negative == 1
    assert result.false_positive == 0
    assert result.false_negative == 0
    assert result.unknown_correct == 2
    
    assert result.accuracy == 1.0
    assert result.precision == 1.0
    assert result.recall == 1.0
    assert result.f1 == 1.0
    assert result.unknown_accuracy == 1.0
