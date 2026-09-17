# Benchmark Migration Specification

## 1. Scope

This specification defines the formal migration of all benchmark and Ground Truth assets currently hosted inside `Medalcode/SecureCode` to their dedicated repository `Medalcode/securecode-ground-truth`.

The objective is to establish an unambiguous architectural boundary between:
1. **The Product (`SecureCode`)**: The core security compliance evaluation engine.
2. **The Benchmark (`securecode-ground-truth`)**: The empirical reference dataset, validation evidence, classification metrics, and test bench runner.

This document serves as the implementation blueprint. Following this specification, any engineer or agent can execute the migration deterministically without architectural ambiguity.

---

## 2. Current Architecture

### 2.1 State in `Medalcode/SecureCode`
- **Engine & Models**:
  - `src/models/gh001.py`: Defines `GH001Evidence` (immutable dataclass).
  - `src/engine/evaluator.py`: Defines `EvaluationStatus` enum and pure function `evaluate_gh001()`.
  - `src/models/__init__.py`, `src/engine/__init__.py`.
  - Note: `src/__init__.py` does **not** exist.
- **Benchmark assets improperly located in product**:
  - `data/ground_truth/gh001_ground_truth.json`: 6 curated cases for control GH-001.
  - `docs/evidence/ground_truth/`: Raw HTTP responses from GitHub API (duplicate of ground truth repo).
  - `docs/specs/METRICS.md`: Specification for confusion matrix and classification metrics.
  - `src/metrics.py`: Implementation of `calculate_metrics()` and `MetricsResult`.
  - `tests/unit/test_metrics.py`: 8 unit tests for metrics edge cases.
  - `tests/integration/test_ground_truth.py`: Validates engine against `gh001_ground_truth.json`.
  - `tests/integration/test_metrics_ground_truth.py`: Runs full pipeline and asserts 100% metrics.
- **Product Tests**:
  - `tests/unit/test_gh001_evaluator.py`: 12 self-contained unit tests for GH-001 evaluator logic.

### 2.2 State in `Medalcode/securecode-ground-truth`
- **Synthetic Testbed**:
  - 6 dedicated GitHub branches representing synthetic compliance scenarios (`branch-case-1-pass` to `branch-case-6-status-checks-only`).
- **Raw Evidence**:
  - `docs/evidence/ground_truth/GT-GH001-0{1..6}/api_response.json`: Authoritative raw GitHub REST API responses (HTTP 200/404).
- **Missing Elements**:
  - No formal dataset under `data/ground_truth/`.
  - No execution code, metrics module, or test runner.

---

## 3. Target Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Medalcode/SecureCode                             │
│                                  (PRODUCT)                                  │
│                                                                             │
│  src/                                                                       │
│  └── securecode/                                                            │
│      ├── __init__.py                                                        │
│      ├── models/                                                            │
│      │   ├── __init__.py                                                    │
│      │   └── gh001.py          (GH001Evidence)                              │
│      └── engine/                                                            │
│          ├── __init__.py                                                    │
│          └── evaluator.py      (EvaluationStatus, evaluate_gh001)           │
│                                                                             │
│  tests/                                                                     │
│  └── unit/                                                                  │
│      └── test_gh001_evaluator.py  (12 self-contained unit tests)            │
│                                                                             │
│  pyproject.toml                (PEP 621 package definition: "securecode")   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       │ installed as dependency
                                       │ (pip install -e ../SecureCode)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Medalcode/securecode-ground-truth                      │
│                                 (BENCHMARK)                                 │
│                                                                             │
│  data/                                                                      │
│  └── ground_truth/                                                          │
│      └── gh001_ground_truth.json (Authoritative curated dataset)            │
│                                                                             │
│  docs/                                                                      │
│  ├── evidence/ground_truth/      (Authoritative raw GitHub API responses)   │
│  └── specs/                                                                 │
│      ├── MIGRATION.md            (This specification)                       │
│      └── METRICS.md              (Benchmark metrics specification)          │
│                                                                             │
│  benchmark/                                                                 │
│  ├── __init__.py                                                            │
│  └── metrics.py                  (calculate_metrics, MetricsResult)         │
│                                                                             │
│  tests/                                                                     │
│  ├── unit/                                                                  │
│  │   └── test_metrics.py         (8 metrics unit tests)                     │
│  └── integration/                                                           │
│      ├── test_ground_truth.py    (Evaluates engine against dataset)         │
│      └── test_metrics_ground_truth.py (Pipeline validation)                 │
│                                                                             │
│  pyproject.toml / requirements.txt (Benchmark dependencies: pytest, etc.)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Repository Responsibilities

| Responsibility Area | Authority | Description |
|---|---|---|
| **Evidence Collection** | `securecode-ground-truth` | Manages synthetic GitHub branches and records raw API responses. |
| **Ground Truth Dataset** | `securecode-ground-truth` | Authoritative definition of reference cases, expected statuses, and rationales. |
| **Evidence Models** | `SecureCode` | Immutable schemas (`GH001Evidence`) representing normalized inputs. |
| **Evaluation Engine** | `SecureCode` | Pure deterministic evaluation functions (`evaluate_gh001`) and statuses (`EvaluationStatus`). |
| **Product Unit Testing** | `SecureCode` | Validates internal evaluator logic against synthetic fixtures (no GT dependency). |
| **Metrics Calculation** | `securecode-ground-truth` | Implements classification statistics (TP, FP, FN, TN, Accuracy, Precision, Recall, F1). |
| **Benchmark Execution** | `securecode-ground-truth` | Runs test harness feeding GT evidence into SecureCode and scoring outputs. |
| **Benchmark Reporting** | `securecode-ground-truth` | Produces structured benchmark execution reports (`reports/`). |

---

## 5. Python Packaging

### 5.1 Analysis of Packaging Options for `SecureCode`

#### Option A: Flat `src` package
- Leave `src/engine/` and `src/models/` directly under `src/`.
- **Problem**: When installed, the top-level packages would be `engine` and `models`, or if packaged as `src`, imports would be `from src.engine import ...`. This pollutes global namespace, conflicts with any other project using `src`, and violates PEP 8 / PEP 517 packaging standards.

#### Option B: Canonical `src-layout` with namespace (`src/securecode/`)
- Relocate:
  - `src/models/` → `src/securecode/models/`
  - `src/engine/` → `src/securecode/engine/`
- Add `src/securecode/__init__.py`.
- Define standard `pyproject.toml` using `setuptools` build backend.
- Package name: `securecode`.
- Import path: `from securecode.engine.evaluator import evaluate_gh001, EvaluationStatus`.
- **Advantages**:
  - Industry standard Python packaging (PEP 517/518/621).
  - Eliminates namespace collisions.
  - Enables clean editable installation (`pip install -e .`).
  - Clear import paths (`securecode.*`) in benchmark and external consumers.
- **Required Changes**:
  - Internal imports in `SecureCode/tests/unit/test_gh001_evaluator.py` updated from `from src.engine...` to `from securecode.engine...`.

#### Option C: Root package (`securecode/` without `src/`)
- Places `securecode/` directly at repository root.
- **Drawback**: Lacks the protection of `src-layout` against accidental imports from local working directory during test execution.

### 5.2 Decision: Option B (Canonical `src-layout`)
`SecureCode` will adopt the standard `src/securecode/` structure and configure a minimal `pyproject.toml`.

#### Target `SecureCode/pyproject.toml` Specification:
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "securecode"
version = "0.1.0"
description = "Deterministic security control evaluation engine"
readme = "README.md"
requires-python = ">=3.11"
authors = [
    { name = "Medalcode" }
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0"
]

[tool.setuptools.packages.find]
where = ["src"]
```

---

## 6. Dependency Model

### 6.1 Directionality
The dependency is strictly **unidirectional**:
$$\text{securecode-ground-truth} \longrightarrow \text{SecureCode}$$

- `SecureCode` has **zero** dependencies on `securecode-ground-truth`.
- `securecode-ground-truth` depends on `SecureCode` solely as the **System Under Test (SUT)**.

### 6.2 Installation Mechanism
- **Local Development / Execution**:
  ```bash
  pip install -e ../SecureCode
  ```
  This editable installation ensures that code updates in `SecureCode` are immediately evaluated without re-packaging.
- **Reproducible / CI Audits**:
  ```bash
  pip install git+https://github.com/Medalcode/SecureCode.git@<COMMIT_SHA>
  ```
  Guarantees deterministic benchmarking against an immutable Git commit hash.

---

## 7. Dataset Migration

### 7.1 Action
Move `SecureCode/data/ground_truth/gh001_ground_truth.json` to `securecode-ground-truth/data/ground_truth/gh001_ground_truth.json`.

### 7.2 Schema & Invariants
- **Schema Version**: `"1.0"`
- **Control**: `"GH-001"`
- **Total Cases**: 6
- **Case Distribution**:
  - `GT-GH001-01`: Expected `PASS` (approvals=2, dismiss_stale=true)
  - `GT-GH001-02`: Expected `FAIL` (approvals=1, dismiss_stale=true)
  - `GT-GH001-03`: Expected `FAIL` (approvals=2, dismiss_stale=false)
  - `GT-GH001-04`: Expected `FAIL` (approvals=1, dismiss_stale=false)
  - `GT-GH001-05`: Expected `UNKNOWN` (approvals=null, dismiss_stale=null, 404)
  - `GT-GH001-06`: Expected `UNKNOWN` (approvals=null, dismiss_stale=null, 200 no reviews)
- **SHA-256 Checksum Baseline**:
  `7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832B`
  *(Must match identically after transfer)*.

---

## 8. Metrics Migration

### 8.1 Action
1. Move `SecureCode/src/metrics.py` to `securecode-ground-truth/benchmark/metrics.py`.
2. Move `SecureCode/docs/specs/METRICS.md` to `securecode-ground-truth/docs/specs/METRICS.md`.

### 8.2 Architectural Rationale
Placing the metrics in `benchmark/metrics.py` (rather than a generic `src/metrics.py`) explicitly scopes the package to benchmark analytics.

### 8.3 Import Adjustments in `benchmark/metrics.py`
Change:
```python
# Before (in SecureCode)
from src.engine.evaluator import EvaluationStatus
```
To:
```python
# After (in securecode-ground-truth)
from securecode.engine.evaluator import EvaluationStatus
```

---

## 9. Test Migration

### 9.1 Files to Migrate
1. **`SecureCode/tests/unit/test_metrics.py`** → `securecode-ground-truth/tests/unit/test_metrics.py`
   - Imports changed:
     ```python
     from securecode.engine.evaluator import EvaluationStatus
     from benchmark.metrics import calculate_metrics, MetricsResult
     ```
2. **`SecureCode/tests/integration/test_ground_truth.py`** → `securecode-ground-truth/tests/integration/test_ground_truth.py`
   - Imports changed:
     ```python
     from securecode.models.gh001 import GH001Evidence
     from securecode.engine.evaluator import evaluate_gh001, EvaluationStatus
     ```
   - Path resolution: Resolves `data/ground_truth/gh001_ground_truth.json` relative to `securecode-ground-truth` repository root.
3. **`SecureCode/tests/integration/test_metrics_ground_truth.py`** → `securecode-ground-truth/tests/integration/test_metrics_ground_truth.py`
   - Imports changed:
     ```python
     from securecode.models.gh001 import GH001Evidence
     from securecode.engine.evaluator import evaluate_gh001, EvaluationStatus
     from benchmark.metrics import calculate_metrics
     ```

### 9.2 Tests Remaining in `SecureCode`
- `tests/unit/test_gh001_evaluator.py`: 12 unit tests covering all deterministic permutations.
  - Imports updated to:
    ```python
    from securecode.engine.evaluator import evaluate_gh001, EvaluationStatus
    from securecode.models.gh001 import GH001Evidence
    ```

---

## 10. Evidence Migration

### 10.1 Authoritative Location
`securecode-ground-truth/docs/evidence/ground_truth/` is the sole authoritative store for raw HTTP evidence.

### 10.2 SHA-256 Hashes of Evidence Baseline:
- `GT-GH001-01/api_response.json`: `FFBA1D4EDF71C6DD6D75BA650B561EE4E1C9C00E157CDB186E7C887B6290A95A`
- `GT-GH001-02/api_response.json`: `3F23708AB2A72A2F0316E3D03F596754C81EB3F2AD95E9674B345C190A55B3C3`
- `GT-GH001-03/api_response.json`: `F70EA6C4C6E1242BC34B15E840EBB10AA2B398950FF3EF31402A3D9CF23D5740`
- `GT-GH001-04/api_response.json`: `18BB54000EF614FDB2B24A0B3317099AECC68F68EA59E92E1498D1BD1B254FC8`
- `GT-GH001-05/api_response.json`: `D6020EE3B0852C3DEB66C66D159CC80CAABEAA66EE301778307A2A18D486450D`
- `GT-GH001-06/api_response.json`: `2F9300292C97099F98EBBB8111B529AE71A3F4A6A3E3333DBDD63A31FA2001CA`

### 10.3 Cleanup in `SecureCode`
The duplicate directory `SecureCode/docs/evidence/` will be safely removed from `SecureCode` after migration confirmation.

---

## 11. Benchmark Integration Contract

The interface between the Benchmark and the System Under Test (SUT) is formalized as:

```text
┌────────────────────────────────────────────────────────┐
│                   Integration Model                    │
├────────────────────────────────────────────────────────┤
│ Input:                                                 │
│   evidence: GH001Evidence                              │
│     - required_review_approvals: Optional[int]         │
│     - dismiss_stale_reviews: Optional[bool]            │
│                                                        │
│ Function Call:                                         │
│   predicted: EvaluationStatus = evaluate_gh001(ev)     │
│                                                        │
│ Output:                                                │
│   EvaluationStatus ∈ {PASS, FAIL, UNKNOWN}             │
└────────────────────────────────────────────────────────┘
```

The benchmark extracts `expected_approvals` and `expected_dismiss_stale` from each Ground Truth case, instantiates `GH001Evidence`, passes it to `evaluate_gh001()`, and compares the resulting `EvaluationStatus` with `case["expected_status"]`.

---

## 12. Versioning

A benchmark run must record the following metadata tuple to guarantee scientific reproducibility:

```json
{
  "product_version": "0.1.0",
  "product_commit": "45195af...",
  "benchmark_version": "0.1.0",
  "ground_truth_version": "1.0",
  "control": "GH-001",
  "execution_timestamp": "2026-09-15T22:45:00Z"
}
```

- **`product_version`**: From `securecode.__version__` or `pyproject.toml`.
- **`product_commit`**: Git commit hash of the installed `SecureCode`.
- **`benchmark_version`**: Version tag of `securecode-ground-truth`.
- **`ground_truth_version`**: Extracted from `gh001_ground_truth.json` (`schema_version`).
- **`control`**: Control identifier (`"GH-001"`).
- **`execution_timestamp`**: UTC timestamp at benchmark initiation.

---

## 13. Reproducibility

### 13.1 Requirements for Benchmark Execution
- Python `>= 3.11` (tested on Python 3.14).
- `securecode-ground-truth/pyproject.toml` or `requirements.txt`:
  ```text
  pytest>=8.0.0
  ```
- Active virtual environment with `securecode` installed (`pip install -e ../SecureCode`).

### 13.2 Execution Command
```bash
python -m pytest tests/ -q
```
Expected output: `8 passed` (8 benchmark tests passing in `securecode-ground-truth`).

---

## 14. Benchmark Reports

The benchmark runner will output a persistent artifact under `reports/`:
File pattern: `reports/benchmark_GH001_{timestamp}.json`

### Report Contract Schema:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "metadata": {
    "product_version": "0.1.0",
    "product_commit": "string",
    "benchmark_version": "0.1.0",
    "ground_truth_version": "1.0",
    "control": "GH-001",
    "timestamp": "ISO8601-UTC"
  },
  "summary": {
    "total_cases": 6,
    "evaluated_cases": 6,
    "pass_count": 1,
    "fail_count": 3,
    "unknown_count": 2
  },
  "metrics": {
    "true_positive": 3,
    "true_negative": 1,
    "false_positive": 0,
    "false_negative": 0,
    "unknown_correct": 2,
    "accuracy": 1.0,
    "precision": 1.0,
    "recall": 1.0,
    "f1": 1.0,
    "unknown_accuracy": 1.0
  },
  "cases": [
    {
      "case_id": "GT-GH001-01",
      "expected_status": "PASS",
      "predicted_status": "PASS",
      "match": true
    }
  ]
}
```

---

## 15. Migration Order

The migration must be executed in the following strict sequence to prevent any broken intermediate states:

```text
Step 1: Restructure SecureCode to src-layout
        ├── Create src/securecode/
        ├── Move src/models/ and src/engine/ under src/securecode/
        ├── Create src/securecode/__init__.py
        ├── Create pyproject.toml in SecureCode
        └── Update imports in tests/unit/test_gh001_evaluator.py

Step 2: Validate SecureCode in isolation
        ├── Execute: pip install -e . (inside SecureCode)
        └── Run: python -m pytest tests/unit/test_gh001_evaluator.py
        Gate: 12 passed.

Step 3: Transfer files to securecode-ground-truth
        ├── Create data/ground_truth/ and copy gh001_ground_truth.json
        ├── Create benchmark/ and copy src/metrics.py -> benchmark/metrics.py
        ├── Copy docs/specs/METRICS.md -> docs/specs/METRICS.md
        ├── Create tests/unit/ and copy tests/unit/test_metrics.py
        └── Create tests/integration/ and copy test_ground_truth.py, test_metrics_ground_truth.py

Step 4: Update imports in securecode-ground-truth
        ├── Update benchmark/metrics.py: import from securecode.engine.evaluator
        ├── Update tests/unit/test_metrics.py: import from benchmark.metrics and securecode
        └── Update tests/integration/*.py: import from securecode and benchmark

Step 5: Verify integrity of transferred assets
        ├── Verify SHA-256 of gh001_ground_truth.json
        └── Verify SHA-256 of docs/evidence/ground_truth/*

Step 6: Execute Benchmark suite in securecode-ground-truth
        ├── Install SecureCode dependency: pip install -e ../SecureCode
        └── Run: python -m pytest tests/ -q
        Gate: 8 passed.

Step 7: Clean up retired assets from SecureCode
        ├── Remove SecureCode/data/ground_truth/
        ├── Remove SecureCode/docs/evidence/
        ├── Remove SecureCode/docs/specs/METRICS.md
        ├── Remove SecureCode/src/metrics.py
        ├── Remove SecureCode/tests/unit/test_metrics.py
        └── Remove SecureCode/tests/integration/

Step 8: Final re-validation of both repositories
        ├── SecureCode: python -m pytest tests/ -q (12 passed)
        └── securecode-ground-truth: python -m pytest tests/ -q (8 passed)
        Total across both: 20 passed.
```

---

## 16. Integrity Validation

During execution of the migration, the following checks must strictly pass:

1. **File Hash Equality**:
   - `gh001_ground_truth.json`: `7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832B`
   - All 6 `api_response.json` files match their recorded hashes.
2. **Case Cardinality**:
   - Exactly 6 cases in `gh001_ground_truth.json`.
3. **Deterministic Metric Scoring**:
   - Evaluator predictions against Ground Truth must score:
     - `Accuracy = 1.0`
     - `Precision = 1.0`
     - `Recall = 1.0`
     - `F1 = 1.0`
     - `UNKNOWN Accuracy = 1.0`
4. **Test Counts**:
   - `SecureCode`: 12 unit tests passing.
   - `securecode-ground-truth`: 8 tests passing (6 metrics unit tests, 1 GT integration, 1 metrics integration).

---

## 17. Open Decisions

The following items are deferred to future implementation iterations and do not block the file migration:
1. **Standalone CLI Runner**: Whether to build a dedicated CLI runner (`python -m benchmark.run`) or rely exclusively on `pytest` for benchmark triggers.
2. **CI/CD Workflow**: Configuration of automated GitHub Actions triggering benchmark execution on PRs across repositories.
3. **Multi-control Extension**: Schema adjustments when controls beyond GH-001 (e.g. GH-002) are introduced.

---

## 18. Acceptance Criteria

The migration will be considered complete when:
- [ ] `SecureCode` contains exclusively product code and `tests/unit/test_gh001_evaluator.py`.
- [ ] `SecureCode` is installable via `pip install -e .` with canonical namespace `securecode`.
- [ ] `securecode-ground-truth` contains the authoritative dataset, raw evidence, metrics module, and integration tests.
- [ ] No circular dependencies exist.
- [ ] `python -m pytest` in `SecureCode` passes 12/12 tests.
- [ ] `python -m pytest` in `securecode-ground-truth` passes 8/8 tests.
- [ ] Git working tree in both repositories is clean with no dangling untracked benchmark duplicates.
