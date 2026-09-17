from dataclasses import dataclass
from typing import List, Tuple, Optional
from securecode.engine.evaluator import EvaluationStatus

@dataclass(frozen=True)
class MetricsResult:
    """Immutable representation of GH-001 evaluation metrics."""
    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int
    unknown_correct: int
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1: Optional[float]
    unknown_accuracy: Optional[float]


def calculate_metrics(cases: List[Tuple[EvaluationStatus, EvaluationStatus]]) -> MetricsResult:
    """
    Calculate classification metrics for evaluator outcomes against Ground Truth.
    
    FAIL is the positive class. PASS is the negative class.
    UNKNOWN is excluded from binary metrics and calculated separately.
    Zero denominators return None.
    """
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    unknown_correct = 0
    total_expected_unknown = 0
    
    for expected, predicted in cases:
        if expected == EvaluationStatus.UNKNOWN:
            total_expected_unknown += 1
            if predicted == EvaluationStatus.UNKNOWN:
                unknown_correct += 1
        elif expected == EvaluationStatus.FAIL:
            if predicted == EvaluationStatus.FAIL:
                tp += 1
            elif predicted == EvaluationStatus.PASS:
                fn += 1
        elif expected == EvaluationStatus.PASS:
            if predicted == EvaluationStatus.PASS:
                tn += 1
            elif predicted == EvaluationStatus.FAIL:
                fp += 1
                
    total_binary = tp + tn + fp + fn
    accuracy = (tp + tn) / total_binary if total_binary > 0 else None
    
    precision_denom = tp + fp
    precision = tp / precision_denom if precision_denom > 0 else None
    
    recall_denom = tp + fn
    recall = tp / recall_denom if recall_denom > 0 else None
    
    f1 = None
    if precision is not None and recall is not None:
        f1_denom = precision + recall
        if f1_denom > 0:
            f1 = 2 * precision * recall / f1_denom
            
    unknown_accuracy = unknown_correct / total_expected_unknown if total_expected_unknown > 0 else None
    
    return MetricsResult(
        true_positive=tp,
        true_negative=tn,
        false_positive=fp,
        false_negative=fn,
        unknown_correct=unknown_correct,
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1=f1,
        unknown_accuracy=unknown_accuracy
    )
