"""Comprehensive benchmark classification metrics and 3x3 confusion matrix calculation."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
from securecode.engine.evaluator import EvaluationStatus


@dataclass(frozen=True)
class MetricsResult:
    """Immutable representation of GH-001/GH-002 binary evaluation metrics (FAIL as positive)."""

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "true_positive": self.true_positive,
            "true_negative": self.true_negative,
            "false_positive": self.false_positive,
            "false_negative": self.false_negative,
            "unknown_correct": self.unknown_correct,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "unknown_accuracy": self.unknown_accuracy,
        }


@dataclass(frozen=True)
class ClassMetrics:
    """Per-class classification metrics."""

    support: int
    correct: int
    incorrect: int
    precision: Optional[float]
    recall: Optional[float]
    f1: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "support": self.support,
            "correct": self.correct,
            "incorrect": self.incorrect,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
        }


@dataclass(frozen=True)
class ComprehensiveMetricsResult:
    """Complete evaluation report including 3x3 matrix, multiclass and binary metrics."""

    total_cases: int
    matched_cases: int
    mismatched_cases: int
    overall_accuracy: Optional[float]
    confusion_matrix_3x3: Dict[str, Dict[str, int]]
    per_class_metrics: Dict[str, ClassMetrics]
    binary_metrics: MetricsResult
    unknown_accuracy: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_cases": self.total_cases,
            "matched_cases": self.matched_cases,
            "mismatched_cases": self.mismatched_cases,
            "overall_accuracy": self.overall_accuracy,
            "confusion_matrix_3x3": self.confusion_matrix_3x3,
            "per_class_metrics": {k: v.to_dict() for k, v in self.per_class_metrics.items()},
            "binary_metrics": self.binary_metrics.to_dict(),
            "unknown_accuracy": self.unknown_accuracy,
        }


def _coerce_status_str(status: Union[EvaluationStatus, str]) -> str:
    if isinstance(status, EvaluationStatus):
        return status.value
    return str(status).upper()


def calculate_3x3_confusion_matrix(
    cases: List[Tuple[Union[EvaluationStatus, str], Union[EvaluationStatus, str]]]
) -> Dict[str, Dict[str, int]]:
    """
    Generate 3x3 confusion matrix indexed by [Expected][Actual].
    Rows: Expected Status (PASS, FAIL, UNKNOWN)
    Columns: Actual Status (PASS, FAIL, UNKNOWN)
    """
    matrix: Dict[str, Dict[str, int]] = {
        "PASS": {"PASS": 0, "FAIL": 0, "UNKNOWN": 0},
        "FAIL": {"PASS": 0, "FAIL": 0, "UNKNOWN": 0},
        "UNKNOWN": {"PASS": 0, "FAIL": 0, "UNKNOWN": 0},
    }

    for expected, predicted in cases:
        exp_str = _coerce_status_str(expected)
        act_str = _coerce_status_str(predicted)
        if exp_str in matrix and act_str in matrix[exp_str]:
            matrix[exp_str][act_str] += 1

    return matrix


def calculate_metrics(
    cases: List[Tuple[Union[EvaluationStatus, str], Union[EvaluationStatus, str]]]
) -> MetricsResult:
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
        exp_status = (
            expected if isinstance(expected, EvaluationStatus) else EvaluationStatus(str(expected).upper())
        )
        act_status = (
            predicted if isinstance(predicted, EvaluationStatus) else EvaluationStatus(str(predicted).upper())
        )

        if exp_status == EvaluationStatus.UNKNOWN:
            total_expected_unknown += 1
            if act_status == EvaluationStatus.UNKNOWN:
                unknown_correct += 1
        elif exp_status == EvaluationStatus.FAIL:
            if act_status == EvaluationStatus.FAIL:
                tp += 1
            elif act_status == EvaluationStatus.PASS:
                fn += 1
        elif exp_status == EvaluationStatus.PASS:
            if act_status == EvaluationStatus.PASS:
                tn += 1
            elif act_status == EvaluationStatus.FAIL:
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
        unknown_accuracy=unknown_accuracy,
    )


def calculate_comprehensive_metrics(
    cases: List[Tuple[Union[EvaluationStatus, str], Union[EvaluationStatus, str]]]
) -> ComprehensiveMetricsResult:
    """
    Compute complete benchmark report including 3x3 matrix, per-class metrics,
    binary security metrics, and overall accuracy.
    """
    total = len(cases)
    matched = 0
    mismatched = 0

    cm = calculate_3x3_confusion_matrix(cases)

    for exp, act in cases:
        if _coerce_status_str(exp) == _coerce_status_str(act):
            matched += 1
        else:
            mismatched += 1

    overall_accuracy = (matched / total) if total > 0 else None

    # Per-class calculation
    per_class = {}
    for cls in ("PASS", "FAIL", "UNKNOWN"):
        support = sum(cm[cls].values())
        correct = cm[cls][cls]
        incorrect = support - correct

        pred_total = sum(cm[row][cls] for row in ("PASS", "FAIL", "UNKNOWN"))
        prec = (correct / pred_total) if pred_total > 0 else None
        rec = (correct / support) if support > 0 else None
        f1 = (2 * prec * rec / (prec + rec)) if (prec is not None and rec is not None and (prec + rec) > 0) else None

        per_class[cls] = ClassMetrics(
            support=support,
            correct=correct,
            incorrect=incorrect,
            precision=prec,
            recall=rec,
            f1=f1,
        )

    binary_metrics = calculate_metrics(cases)

    return ComprehensiveMetricsResult(
        total_cases=total,
        matched_cases=matched,
        mismatched_cases=mismatched,
        overall_accuracy=overall_accuracy,
        confusion_matrix_3x3=cm,
        per_class_metrics=per_class,
        binary_metrics=binary_metrics,
        unknown_accuracy=binary_metrics.unknown_accuracy,
    )
