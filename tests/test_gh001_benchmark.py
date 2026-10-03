import json
from pathlib import Path
import pytest

DATASET_PATH = Path(__file__).parent.parent / "data" / "ground_truth" / "gh001_benchmark_105.json"

@pytest.fixture
def dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_dataset_size(dataset):
    assert dataset["total_cases"] >= 100
    assert len(dataset["cases"]) == dataset["total_cases"]

def test_unique_case_ids(dataset):
    case_ids = [c["case_id"] for c in dataset["cases"]]
    assert len(case_ids) == len(set(case_ids)), "Case IDs must be unique"

def test_valid_expected_labels(dataset):
    labels = {c["expected_status"] for c in dataset["cases"]}
    assert labels.issubset({"PASS", "FAIL", "UNKNOWN"})

def test_scenario_families_represented(dataset):
    families = {c["scenario_family"] for c in dataset["cases"]}
    assert len(families) >= 5  # Ensure we have multiple families

def test_oracle_independence(dataset):
    # Verify expected labels map correctly to the independent spec rules
    for case in dataset["cases"]:
        app = case["evidence"]["required_review_approvals"]
        ds = case["evidence"]["dismiss_stale_reviews"]
        expected = case["expected_status"]
        
        if app is None or ds is None:
            assert expected == "UNKNOWN"
        elif app >= 2 and ds is True:
            assert expected == "PASS"
        else:
            assert expected == "FAIL"
