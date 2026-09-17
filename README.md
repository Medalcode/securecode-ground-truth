# SecureCode Ground Truth & Benchmark

Official reference dataset, empirical validation evidence, classification metrics, and test bench harness for the **SecureCode** deterministic compliance evaluation engine.

---

## 1. Overview

This repository acts as the authoritative testbed for measuring and validating the classification accuracy of [Medalcode/SecureCode](https://github.com/Medalcode/SecureCode).

### Architectural Separation
- **`SecureCode` (Product)**: Implements evidence models, normalization adapters, and the pure deterministic rule evaluation engine (`evaluate_gh001`). It produces compliance predictions (`PASS`, `FAIL`, `UNKNOWN`).
- **`securecode-ground-truth` (Benchmark)**: Owns the empirical reference dataset (`expected_status`), raw API evidence from GitHub, the confusion matrix calculation engine (`benchmark.metrics`), and the verification test suites.

```text
┌─────────────────────────────────────────────────────────┐
│               securecode-ground-truth                   │
│  Reference Dataset (expected)                           │
└────────────┬────────────────────────────────────────────┘
             │ evidence
             ▼
┌─────────────────────────────────────────────────────────┐
│                      SecureCode                         │
│  evaluate_gh001(evidence)                               │
└────────────┬────────────────────────────────────────────┘
             │ predicted_status
             ▼
┌─────────────────────────────────────────────────────────┐
│               securecode-ground-truth                   │
│  expected vs. predicted → benchmark.metrics             │
│  Accuracy, Precision, Recall, F1, UNKNOWN Accuracy      │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Control GH-001 — Branch Protection Required

The current dataset contains **6 empirically validated test cases** for control **GH-001** (Branch Protection Review Policy), executed against dedicated synthetic branches in this repository:

| Case ID | Scenario | Branch Name | Required Approvals | Dismiss Stale | Expected Status |
|---|---|---|:---:|:---:|:---:|
| `GT-GH001-01` | PASS — Valid protection | `branch-case-1-pass` | 2 | `True` | **`PASS`** |
| `GT-GH001-02` | FAIL — Insufficient approvals | `branch-case-2-fail-low-approvals` | 1 | `True` | **`FAIL`** |
| `GT-GH001-03` | FAIL — Stale reviews not dismissed | `branch-case-3-fail-no-dismiss` | 2 | `False` | **`FAIL`** |
| `GT-GH001-04` | FAIL — Both conditions violated | `branch-case-4-fail-both` | 1 | `False` | **`FAIL`** |
| `GT-GH001-05` | UNKNOWN — Absence of protection (404) | `branch-case-5-unprotected` | *None* | *None* | **`UNKNOWN`** |
| `GT-GH001-06` | UNKNOWN — Incomplete evidence (no PR reviews) | `branch-case-6-status-checks-only` | *None* | *None* | **`UNKNOWN`** |

Raw HTTP responses directly captured from GitHub's REST API endpoint (`GET /repos/Medalcode/securecode-ground-truth/branches/{branch}/protection`) are stored in `docs/evidence/ground_truth/`.

---

## 3. Metrics Specification Summary

Per the academic definition established in `docs/specs/METRICS.md`:

- **Positive Class**: `FAIL` (identifying security non-compliance is the primary goal).
- **Negative Class**: `PASS`.
- **Treatment of UNKNOWN**:
  - `UNKNOWN` is an explicit, valid non-binary outcome representing insufficient or unobservable evidence.
  - Excluded from binary classification counters ($TP, TN, FP, FN$).
  - Measured independently via **UNKNOWN Accuracy**:
    $$\text{UNKNOWN Accuracy} = \frac{\text{Correctly Classified UNKNOWN}}{\text{Total Expected UNKNOWN}}$$
- **Zero-Denominator Policy**: When a metric denominator evaluates to zero, the metric produces `None` (undefined), distinguishing it from 0.0 or 1.0.

### Current Baseline Metrics on GH-001 Ground Truth
- **$TP = 3$** (Cases 02, 03, 04)
- **$TN = 1$** (Case 01)
- **$FP = 0$**
- **$FN = 0$**
- **$\text{UNKNOWN Correct} = 2$** (Cases 05, 06)
- **$\text{Accuracy} = 1.0$**
- **$\text{Precision} = 1.0$**
- **$\text{Recall} = 1.0$**
- **$\text{F1} = 1.0$**
- **$\text{UNKNOWN Accuracy} = 1.0$**

---

## 4. Repository Structure

```text
securecode-ground-truth/
├── benchmark/
│   ├── __init__.py
│   ├── metadata.py                 # Benchmark result metadata models & validation
│   └── metrics.py                  # calculate_metrics() implementation
├── data/
│   └── ground_truth/
│       └── gh001_ground_truth.json # Authoritative JSON reference dataset
├── docs/
│   ├── evidence/
│   │   └── ground_truth/           # Raw JSON responses from GitHub API (GT-GH001-01..06)
│   └── specs/
│       ├── METRICS.md              # Formal mathematical specification of metrics
│       └── MIGRATION.md            # Benchmark migration specification & audit history
├── tests/
│   ├── unit/
│   │   ├── test_metadata.py        # 9 unit tests covering metadata models & validation
│   │   └── test_metrics.py         # 6 unit tests covering metric edge cases (Cases A..F)
│   └── integration/
│       ├── test_ground_truth.py    # Direct evaluation of dataset against SecureCode engine
│       └── test_metrics_ground_truth.py # Full pipeline evaluation & 100% score verification
├── .gitignore
└── README.md
```

---

## 5. Execution & Verification

### Prerequisites
- Python `>= 3.11`
- `pytest >= 8.0.0`
- Editable installation of `SecureCode`:
  ```bash
  pip install -e ../SecureCode
  ```

### Running the Test Suite
To execute the complete benchmark verification harness (17 tests):
```bash
python -m pytest tests/ -v
```

Expected output:
```text
tests/unit/test_metadata.py::test_valid_metadata_creation PASSED
tests/unit/test_metadata.py::test_metadata_serialization_and_roundtrip PASSED
tests/unit/test_metadata.py::test_get_product_version_from_installed_package PASSED
tests/unit/test_metadata.py::test_required_fields_cannot_silently_disappear PASSED
tests/unit/test_metadata.py::test_nested_metadata_type_integrity PASSED
tests/unit/test_metadata.py::test_timestamp_validation PASSED
tests/unit/test_metadata.py::test_dataset_hash_validation PASSED
tests/unit/test_metadata.py::test_case_count_validation PASSED
tests/unit/test_metadata.py::test_commit_and_control_validation PASSED
tests/unit/test_metrics.py::test_metrics_case_a_ground_truth_distribution PASSED
tests/unit/test_metrics.py::test_metrics_case_b_incorrect_classification PASSED
tests/unit/test_metrics.py::test_metrics_case_c_unknown_partially_correct PASSED
tests/unit/test_metrics.py::test_metrics_case_d_empty_dataset PASSED
tests/unit/test_metrics.py::test_metrics_case_e_only_unknown PASSED
tests/unit/test_metrics.py::test_metrics_case_f_zero_denominators PASSED
tests/integration/test_ground_truth.py::test_gh001_ground_truth_cases PASSED
tests/integration/test_metrics_ground_truth.py::test_metrics_against_ground_truth PASSED

17 passed in 0.06s
```