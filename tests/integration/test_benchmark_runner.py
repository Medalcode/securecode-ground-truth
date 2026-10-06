"""Integration test validating end-to-end benchmark execution against SecureCode."""

from pathlib import Path
from benchmark.runner import run_benchmark

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_full_benchmark_execution():
    """Execute complete cross-repository benchmark evaluation and assert contract adherence."""
    result = run_benchmark(REPO_ROOT)

    assert result["validation_type"] == "securecode_ground_truth_benchmark"
    assert result["benchmark_version"] == "1.0.0"

    # Product and ground truth identity
    assert result["product"]["name"] == "securecode"
    assert result["product"]["version"] == "0.1.0"
    assert result["ground_truth"]["version"] == "1.0.0"

    # Combined synthetic metrics
    comb = result["combined_synthetic"]
    assert comb["total_cases"] == 205
    assert comb["matched"] == 205
    assert comb["mismatched"] == 0
    assert comb["overall_accuracy"] == 1.0

    # 3x3 Confusion matrix
    cm = result["confusion_matrix_3x3"]
    assert cm["PASS"]["PASS"] == 69
    assert cm["FAIL"]["FAIL"] == 68
    assert cm["UNKNOWN"]["UNKNOWN"] == 68
    assert cm["PASS"]["FAIL"] == 0
    assert cm["FAIL"]["PASS"] == 0

    # GH-001 Synthetic
    gh1_syn = result["controls"]["GH-001"]["synthetic_benchmark"]
    assert gh1_syn["cases"] == 105
    assert gh1_syn["matched"] == 105
    assert gh1_syn["mismatched"] == 0

    # GH-001 Empirical Pilot
    gh1_pilot = result["controls"]["GH-001"]["empirical_pilot"]
    assert gh1_pilot["cases"] == 6
    assert gh1_pilot["matched"] == 6
    assert gh1_pilot["mismatched"] == 0
    assert gh1_pilot["classification"] == "REAL-GITHUB VALIDATED PILOT"

    # GH-002 Synthetic
    gh2_syn = result["controls"]["GH-002"]["synthetic_benchmark"]
    assert gh2_syn["cases"] == 100
    assert gh2_syn["matched"] == 100
    assert gh2_syn["mismatched"] == 0

    # GH-002 Empirical Pilot
    gh2_pilot = result["controls"]["GH-002"]["empirical_pilot"]
    assert gh2_pilot["status"] == "BLOCKED"
    assert gh2_pilot["cases"] == 0
    assert gh2_pilot["classification"] == "REAL-GITHUB PILOT BLOCKED"

    # Mutation Sensitivity
    mut = result["mutation_sensitivity"]
    assert mut["mutation_score"] == 1.0
    assert mut["mutants_detected"] == 4
