from securecode.engine.evaluator import EvaluationStatus
from benchmark.metrics import calculate_metrics, MetricsResult

def test_metrics_case_a_ground_truth_distribution():
    """Caso A: 1 PASS, 3 FAIL, 2 UNKNOWN perfect prediction"""
    cases = [
        (EvaluationStatus.PASS, EvaluationStatus.PASS),
        (EvaluationStatus.FAIL, EvaluationStatus.FAIL),
        (EvaluationStatus.FAIL, EvaluationStatus.FAIL),
        (EvaluationStatus.FAIL, EvaluationStatus.FAIL),
        (EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN),
        (EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN),
    ]
    
    result = calculate_metrics(cases)
    
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


def test_metrics_case_b_incorrect_classification():
    """Caso B: FP and FN simultaneous presence"""
    cases = [
        (EvaluationStatus.FAIL, EvaluationStatus.FAIL),  # TP
        (EvaluationStatus.PASS, EvaluationStatus.PASS),  # TN
        (EvaluationStatus.PASS, EvaluationStatus.FAIL),  # FP
        (EvaluationStatus.FAIL, EvaluationStatus.PASS),  # FN
    ]
    
    result = calculate_metrics(cases)
    
    assert result.true_positive == 1
    assert result.true_negative == 1
    assert result.false_positive == 1
    assert result.false_negative == 1
    
    assert result.accuracy == 0.5   # 2 correct / 4 total
    assert result.precision == 0.5  # 1 TP / 2 predicted FAIL
    assert result.recall == 0.5     # 1 TP / 2 expected FAIL
    assert result.f1 == 0.5


def test_metrics_case_c_unknown_partially_correct():
    """Caso C: UNKNOWN expected mixed predictions"""
    cases = [
        (EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN), # correct
        (EvaluationStatus.UNKNOWN, EvaluationStatus.PASS),    # incorrect
        (EvaluationStatus.UNKNOWN, EvaluationStatus.FAIL),    # incorrect
    ]
    
    result = calculate_metrics(cases)
    
    # Binary metrics remain zero/None
    assert result.true_positive == 0
    assert result.true_negative == 0
    assert result.false_positive == 0
    assert result.false_negative == 0
    
    assert result.unknown_correct == 1
    assert result.unknown_accuracy == 1 / 3


def test_metrics_case_d_empty_dataset():
    """Caso D: Empty dataset -> everything 0 or None"""
    cases = []
    
    result = calculate_metrics(cases)
    
    assert result.true_positive == 0
    assert result.true_negative == 0
    assert result.false_positive == 0
    assert result.false_negative == 0
    assert result.unknown_correct == 0
    
    assert result.accuracy is None
    assert result.precision is None
    assert result.recall is None
    assert result.f1 is None
    assert result.unknown_accuracy is None


def test_metrics_case_e_only_unknown():
    """Caso E: Only UNKNOWN"""
    cases = [
        (EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN),
    ]
    
    result = calculate_metrics(cases)
    
    assert result.accuracy is None
    assert result.precision is None
    assert result.recall is None
    assert result.f1 is None
    assert result.unknown_accuracy == 1.0


def test_metrics_case_f_zero_denominators():
    """Caso F: Explicitly ensure None policy for individual zero-denominators"""
    # Precision denom zero (TP+FP=0) -> expected PASS, predicted PASS
    cases_no_pred_pos = [
        (EvaluationStatus.PASS, EvaluationStatus.PASS),
    ]
    result_no_pred_pos = calculate_metrics(cases_no_pred_pos)
    assert result_no_pred_pos.precision is None
    assert result_no_pred_pos.recall is None
    assert result_no_pred_pos.f1 is None
    
    # Recall denom zero (TP+FN=0) -> expected PASS, predicted FAIL
    cases_no_act_pos = [
        (EvaluationStatus.PASS, EvaluationStatus.FAIL), # FP=1
    ]
    result_no_act_pos = calculate_metrics(cases_no_act_pos)
    assert result_no_act_pos.precision == 0.0 # TP(0) / FP(1) = 0.0
    assert result_no_act_pos.recall is None   # TP(0) / TP(0)+FN(0) = None
    assert result_no_act_pos.f1 is None

    # F1 denom zero (Precision+Recall=0)
    cases_zero_f1_denom = [
        (EvaluationStatus.FAIL, EvaluationStatus.PASS), # FN=1 (recall = 0)
        (EvaluationStatus.PASS, EvaluationStatus.FAIL), # FP=1 (precision = 0)
    ]
    result_zero_f1 = calculate_metrics(cases_zero_f1_denom)
    assert result_zero_f1.precision == 0.0
    assert result_zero_f1.recall == 0.0
    assert result_zero_f1.f1 is None
