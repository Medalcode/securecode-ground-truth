"""Unit tests verifying that the benchmark detects faulty/mutated evaluator logic."""

from pathlib import Path
from benchmark.dataset_validator import load_dataset
from benchmark.runner import run_mutation_suite

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_mutation_sensitivity_detects_all_mutants():
    """All intentional test-only mutants must be caught by the benchmark suite."""
    p_gh1 = REPO_ROOT / "data" / "ground_truth" / "gh001_benchmark_105.json"
    p_gh2 = REPO_ROOT / "data" / "ground_truth" / "gh002_ground_truth.json"

    _, cases_gh1 = load_dataset(p_gh1)
    _, cases_gh2 = load_dataset(p_gh2)

    results = run_mutation_suite(cases_gh1, cases_gh2)

    assert results["mutants_evaluated"] == 4
    assert results["mutants_detected"] == 4
    assert results["mutation_score"] == 1.0, "Mutation score must be 100% (all mutants detected)"

    for detail in results["details"]:
        assert detail["detected"] is True, f"Mutant {detail['mutation']} was not detected!"
        assert detail["mismatches_detected"] > 0
        assert detail["detection_rate"] > 0.0
