# SecureCode Ground Truth & Benchmark

Authoritative reference datasets, independent oracle specifications, cryptographic integrity manifests, classification metrics, and reproducible test bench harness for the **SecureCode** deterministic compliance evaluation engine.

---

## 1. Overview & Architectural Separation

This repository serves as the **independent, falsifiable validation authority** for [Medalcode/SecureCode](https://github.com/Medalcode/SecureCode).

### Separation of Responsibilities

```text
┌─────────────────────────────────────────────────────────┐
│               securecode-ground-truth                   │
│  Authoritative Reference Datasets (Expected Status)     │
│  Independent Oracle Specifications (GH-001, GH-002)     │
│  Cryptographic Manifest & Schema Validation             │
└────────────┬────────────────────────────────────────────┘
             │ normalized evidence
             ▼
┌─────────────────────────────────────────────────────────┐
│                      SecureCode                         │
│  evaluate_gh001(evidence) / evaluate_gh002(evidence)    │
│  Pure Deterministic Rule Engine                         │
└────────────┬────────────────────────────────────────────┘
             │ predicted_status (PASS / FAIL / UNKNOWN)
             ▼
┌─────────────────────────────────────────────────────────┐
│               securecode-ground-truth                   │
│  Expected vs. Actual Outcome Comparison                 │
│  3x3 Confusion Matrix & Binary Metrics (Positive = FAIL)│
│  Mutation Sensitivity Verification                      │
└─────────────────────────────────────────────────────────┘
```

- **`SecureCode` (Product Under Test)**: Owns the runtime evidence normalization adapters, PostgreSQL persistence layer, and the deterministic rule evaluation engine (`evaluate_gh001`, `evaluate_gh002`).
- **`securecode-ground-truth` (Independent Oracle)**: Owns the expected evaluation labels (`expected_status`), the formal mathematical oracle specifications, the empirical GitHub API response records, and the evaluation harness. Ground Truth **never** imports or reproduces product logic to derive labels (non-circularity guarantee).

---

## 2. Controls & Dataset Taxonomy

Datasets are strictly bifurcated into **Synthetic Benchmark** and **Empirical API Pilot** suites:

### Control GH-001: Branch Protection Review Policy
- **Synthetic Benchmark ($n=105$)**: Exercises all permutations of review approval thresholds ($<2, =2, >2, \text{None}$) and stale review dismissal flags ($\text{True}, \text{False}, \text{None}$) across 9 scenario families.
  - Distribution: **35 PASS**, **35 FAIL**, **35 UNKNOWN** (balanced 1:1:1).
  - Path: `data/ground_truth/gh001_benchmark_105.json`
- **Empirical Pilot ($n=6$)**: Live HTTP responses from GitHub's REST API (`GET /repos/Medalcode/securecode-ground-truth/branches/{branch}/protection`) against controlled synthetic branches.
  - Status: **`REAL-GITHUB VALIDATED PILOT`** (6 cases, 100% agreement).
  - Path: `data/ground_truth/gh001_ground_truth.json`
  - Evidence: `docs/evidence/ground_truth/GT-GH001-01` through `06`.

### Control GH-002: Default Branch Protection Enabled
- **Synthetic Benchmark ($n=100$)**: Exercises default branch protection states ($\text{True}, \text{False}, \text{None}$) across 100 simulated repository environments.
  - Distribution: **34 PASS**, **33 FAIL**, **33 UNKNOWN**.
  - Path: `data/ground_truth/gh002_ground_truth.json`
- **Empirical Pilot ($n=0$)**:
  - Status: **`REAL-GITHUB PILOT BLOCKED`**
  - Reason: The GitHub API endpoint `/branches/{default_branch}/protection` strictly mandates authentication token scopes even for public repositories. In the absence of an empirical `VALIDATION_GITHUB_TOKEN`, live adapter calls fall back safely to `UNKNOWN`.

---

## 3. Cryptographic Integrity & Manifest

Canonical dataset files are cryptographically frozen. Hashes are recorded in `benchmark/manifest.json`:

| Control | Dataset Type | Path | Cases | File SHA-256 | Canonical JSON SHA-256 |
|---|---|---|:---:|---|---|
| **GH-001** | Synthetic Benchmark | `data/ground_truth/gh001_benchmark_105.json` | 105 | `8319425d25a1b251f680282495e22a11043093397cf36afcd88a77a1529d7947` | `9fda9475134c53244c9af0d6ccdfeb9b6cafa6caa98728750b28803085338464` |
| **GH-001** | Empirical Pilot | `data/ground_truth/gh001_ground_truth.json` | 6 | `7418f0da8b8f55da1123068756650434b0ec03e20d575fba1c01e6663656832b` | `d560a93cfe2e4c31f0177853f99b044d2f81190e52b6521c5ef07357e671c045` |
| **GH-002** | Synthetic Benchmark | `data/ground_truth/gh002_ground_truth.json` | 100 | `c285dc542d0f97de0507f71aa601484055a80e6b34d060fb2529c5d4dfbaca13` | `8f0bd5554014f37c0206acdc1b92e53aa5bcac601265ab3dc6e92428910c6a99` |

**Total Synthetic Cases:** 205 | **Total Empirical Cases:** 6 | **Combined Fleet:** 211

---

## 4. Evaluation Metrics & 3x3 Confusion Matrix

Per `docs/specs/METRICS.md`:
- **Positive Class = `FAIL`**: Detecting security non-compliance is the primary objective ($TP, TN, FP, FN$).
- **`UNKNOWN` Semantics**: First-class, distinct outcome indicating unobservable or partial evidence. Excluded from binary counters; evaluated via $\text{UNKNOWN Accuracy} = \frac{\text{Correct UNKNOWN}}{\text{Total Expected UNKNOWN}}$.
- **Zero-Denominator Behavior**: Denominators evaluating to zero yield `None` (undefined).

### 3x3 Confusion Matrix (Combined Benchmark, n=205)

```text
               ┌────────────────────────────────────────────────────────┐
               │                     ACTUAL PREDICTION                  │
               ├────────────────┬───────────────┬──────────────────────┤
               │      PASS      │     FAIL      │       UNKNOWN        │
┌──────────────┼────────────────┼───────────────┼──────────────────────┤
│ EXPECTED PASS│      69        │ 0             │ 0                    │
├──────────────┼────────────────┼───────────────┼──────────────────────┤
│ EXPECTED FAIL│      0         │ 68            │ 0                    │
├──────────────┼────────────────┼───────────────┼──────────────────────┤
│ EXPECTED UNK │      0         │ 0             │ 68                   │
└──────────────┴────────────────┴───────────────┴──────────────────────┘
```

### Academic KPI Summary (Correctitud)

| Metric | GH-001 Synthetic ($n=105$) | GH-002 Synthetic ($n=100$) | Combined Synthetic ($n=205$) | GH-001 Empirical ($n=6$) |
|---|:---:|:---:|:---:|:---:|
| **Matched / Mismatched** | 105 / 0 | 100 / 0 | 205 / 0 | 6 / 0 |
| **Overall 3-Class Accuracy** | **100.0%** | **100.0%** | **100.0%** | **100.0%** |
| **Binary Accuracy** | 100.0% | 100.0% | 100.0% | 100.0% |
| **Precision** | 100.0% | 100.0% | 100.0% | 100.0% |
| **Recall** | 100.0% | 100.0% | 100.0% | 100.0% |
| **F1-Score** | 100.0% | 100.0% | 100.0% | 100.0% |
| **UNKNOWN Accuracy** | 100.0% | 100.0% | 100.0% | 100.0% |

---

## 5. Mutation Sensitivity & Falsifiability

A scientific benchmark must actively fail when exposed to a flawed engine. Four test-only mutants were evaluated:

| Mutation Description | Target | Cases | Mismatches Detected | Mutation Kill Rate | Status |
|---|---|:---:|:---:|:---:|:---:|
| GH-001 Threshold Raised ($2 \to 3$) | GH-001 | 105 | 15 | 14.3% | **DETECTED** |
| GH-001 Ignore Stale Review Dismissal | GH-001 | 105 | 25 | 23.8% | **DETECTED** |
| GH-002 Inverted Boolean Logic | GH-002 | 100 | 67 | 67.0% | **DETECTED** |
| GH-002 Treat UNKNOWN as PASS | GH-002 | 100 | 33 | 33.0% | **DETECTED** |

**Benchmark Mutation Score:** **100.0%** (4/4 mutants successfully caught and killed).

---

## 6. Repository Layout

```text
securecode-ground-truth/
├── .github/
│   └── workflows/
│       └── ci.yml                      # Automated CI workflow
├── artifacts/
│   ├── ground_truth_validation.json    # Machine-readable evaluation report
│   └── ground_truth_validation.md      # Human-readable evaluation report
├── benchmark/
│   ├── __init__.py
│   ├── dataset_validator.py            # Schema validation, coverage & duplicate analysis
│   ├── manifest.json                   # Cryptographic benchmark manifest
│   ├── metadata.py                     # Result metadata models & package version resolver
│   ├── metrics.py                      # 3x3 confusion matrix & academic metrics engine
│   ├── run_benchmark.py                # CLI runner entrypoint
│   └── runner.py                       # Unified cross-repository benchmark harness
├── data/
│   └── ground_truth/
│       ├── gh001_benchmark_105.json    # Frozen synthetic dataset for GH-001 (105 cases)
│       ├── gh001_ground_truth.json     # Frozen empirical baseline for GH-001 (6 cases)
│       └── gh002_ground_truth.json     # Frozen synthetic dataset for GH-002 (100 cases)
├── docs/
│   ├── evidence/
│   │   └── ground_truth/               # Raw HTTP responses (GT-GH001-01..06)
│   ├── specs/
│   │   ├── GH001_ORACLE.md             # Independent GH-001 oracle specification & truth table
│   │   ├── GH002_ORACLE.md             # Independent GH-002 oracle specification & API flow
│   │   ├── METRICS.md                  # Mathematical metrics specification
│   │   └── MIGRATION.md                # Migration record from SecureCode
│   └── GROUND_TRUTH_PROTOCOL.md        # Oracle independence & governance protocol
├── gen_gh002.py                        # Deterministic generator reference for GH-002
├── scripts/
│   ├── generate_gh001_benchmark.py     # Independent generator for GH-001
│   └── generate_gh002_benchmark.py     # Independent generator for GH-002
├── tests/
│   ├── unit/
│   │   ├── test_dataset_validation.py  # 5 tests: schema integrity, uniqueness, coverage
│   │   ├── test_manifest.py            # 2 tests: cryptographic hash consistency
│   │   ├── test_metadata.py            # 9 tests: execution metadata model & validation
│   │   ├── test_metrics.py             # 6 tests: metric calculation edge cases (A..F)
│   │   └── test_mutation_sensitivity.py# 1 test: mutation kill rate verification
│   ├── integration/
│   │   ├── test_benchmark_runner.py    # 1 test: end-to-end benchmark execution
│   │   ├── test_ground_truth.py        # 1 test: empirical baseline evaluator agreement
│   │   └── test_metrics_ground_truth.py# 1 test: empirical metrics agreement
│   └── test_gh001_benchmark.py         # 5 tests: GH-001 105 synthetic dataset properties
├── .gitignore
└── README.md
```

---

## 7. Execution & Verification

### Prerequisites
- Python `>= 3.11`
- `pytest >= 8.0`
- `securecode` installed in editable mode:
  ```bash
  pip install -e ../SecureCode
  ```

### Running the Test Suite (31 Tests)
Execute all unit, integration, and mutation tests:
```bash
python -m pytest tests/ -v
```

### Running the Benchmark Harness
Generate fresh machine-readable and human-readable validation artifacts:
```bash
python benchmark/run_benchmark.py
```

Generated reports:
- `artifacts/ground_truth_validation.json`
- `artifacts/ground_truth_validation.md`

---

## 8. Academic Limitations

1. **Synthetic Sample Equivalence**: Controlled synthetic permutations validate rule engine boundaries, but cannot simulate external GitHub API schema changes or rate-limiting anomalies.
2. **Control Breadth**: Currently evaluates controls `GH-001` and `GH-002`. Controls `GH-003+` are future work.
3. **Empirical Sample Size**: The empirical pilot for GH-001 is small ($n=6$) and intended for adapter normalization validation, not statistical inference.
4. **Provider Scope**: GitHub is the sole supported platform. GitLab, Bitbucket, and Azure DevOps are unbenchmarked.