"""Unit tests for benchmark manifest integrity and cryptographic consistency."""

import json
from pathlib import Path

from benchmark.dataset_validator import compute_canonical_sha256, compute_file_sha256, load_dataset

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_manifest_file_exists_and_parses():
    """Manifest file must exist and be valid JSON."""
    manifest_path = REPO_ROOT / "benchmark" / "manifest.json"
    assert manifest_path.exists(), "benchmark/manifest.json does not exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert "benchmark_version" in manifest
    assert "controls" in manifest
    assert "summary" in manifest
    assert manifest["summary"]["total_synthetic_cases"] == 205


def test_manifest_hashes_match_actual_files():
    """SHA-256 hashes recorded in manifest must match actual file and canonical content digests."""
    manifest_path = REPO_ROOT / "benchmark" / "manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Check GH-001 Synthetic
    gh1_spec = manifest["controls"]["GH-001"]["synthetic_benchmark"]
    gh1_path = REPO_ROOT / gh1_spec["dataset_path"]
    assert compute_file_sha256(gh1_path) == gh1_spec["file_sha256"]
    meta_gh1, _ = load_dataset(gh1_path)
    assert compute_canonical_sha256(meta_gh1) == gh1_spec["canonical_sha256"]
    assert gh1_spec["case_count"] == 105

    # Check GH-001 Empirical
    gh1_emp_spec = manifest["controls"]["GH-001"]["empirical_pilot"]
    gh1_emp_path = REPO_ROOT / gh1_emp_spec["dataset_path"]
    assert compute_file_sha256(gh1_emp_path) == gh1_emp_spec["file_sha256"]
    assert gh1_emp_spec["case_count"] == 6

    # Check GH-002 Synthetic
    gh2_spec = manifest["controls"]["GH-002"]["synthetic_benchmark"]
    gh2_path = REPO_ROOT / gh2_spec["dataset_path"]
    assert compute_file_sha256(gh2_path) == gh2_spec["file_sha256"]
    _, cases_gh2 = load_dataset(gh2_path)
    assert compute_canonical_sha256(cases_gh2) == gh2_spec["canonical_sha256"]
    assert gh2_spec["case_count"] == 100
