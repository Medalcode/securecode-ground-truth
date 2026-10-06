"""Unit tests for Ground Truth dataset schema validation and integrity."""

import json
from pathlib import Path
import pytest

from benchmark.dataset_validator import (
    analyze_coverage_gh001,
    analyze_coverage_gh002,
    analyze_duplicates,
    load_dataset,
    validate_case,
    validate_dataset_file,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_canonical_datasets_pass_validation():
    """All production datasets must pass validation without any schema errors."""
    datasets = [
        REPO_ROOT / "data" / "ground_truth" / "gh001_benchmark_105.json",
        REPO_ROOT / "data" / "ground_truth" / "gh002_ground_truth.json",
        REPO_ROOT / "data" / "ground_truth" / "gh001_ground_truth.json",
    ]
    for dpath in datasets:
        errors = validate_dataset_file(dpath)
        assert errors == [], f"Validation failed for {dpath.name}: {errors}"


def test_duplicate_case_ids_rejected(tmp_path):
    """Dataset with duplicate case IDs must fail validation."""
    dup_dataset = {
        "cases": [
            {
                "case_id": "GT-GH001-001",
                "control": "GH-001",
                "expected_status": "PASS",
                "evidence": {"required_review_approvals": 2, "dismiss_stale_reviews": True},
            },
            {
                "case_id": "GT-GH001-001",  # Duplicate!
                "control": "GH-001",
                "expected_status": "FAIL",
                "evidence": {"required_review_approvals": 1, "dismiss_stale_reviews": True},
            },
        ]
    }
    p = tmp_path / "dup.json"
    p.write_text(json.dumps(dup_dataset), encoding="utf-8")

    errors = validate_dataset_file(p)
    assert any("Duplicate case_id" in err for err in errors)


def test_invalid_status_rejected():
    """Invalid classification status strings must be rejected."""
    bad_case = {
        "case_id": "GT-GH001-999",
        "control": "GH-001",
        "expected_status": "MAYBE",  # Invalid!
        "evidence": {"required_review_approvals": 2, "dismiss_stale_reviews": True},
    }
    errors = validate_case(bad_case)
    assert any("Invalid or missing expected status" in err for err in errors)


def test_missing_evidence_fields_rejected():
    """Missing mandatory evidence fields must be rejected."""
    bad_case = {
        "case_id": "GT-GH001-999",
        "control": "GH-001",
        "expected_status": "PASS",
        "evidence": {"required_review_approvals": 2},  # Missing dismiss_stale_reviews!
    }
    errors = validate_case(bad_case)
    assert any("dismiss_stale_reviews" in err for err in errors)


def test_coverage_and_duplicate_analysis():
    """Coverage and duplicate analysis must produce consistent statistical breakdowns."""
    p_gh1 = REPO_ROOT / "data" / "ground_truth" / "gh001_benchmark_105.json"
    _, cases_gh1 = load_dataset(p_gh1)

    cov = analyze_coverage_gh001(cases_gh1)
    assert cov["total_cases"] == 105
    assert cov["status_distribution"]["PASS"] == 35
    assert cov["status_distribution"]["FAIL"] == 35
    assert cov["status_distribution"]["UNKNOWN"] == 35

    dup = analyze_duplicates(cases_gh1, "GH-001")
    assert dup["total_cases"] == 105
    assert dup["unique_evidence_configurations"] == 22
    assert dup["duplicate_evidence_cases"] == 83
