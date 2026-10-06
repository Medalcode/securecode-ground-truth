# SecureCode Ground Truth Benchmark Validation Report

**Report Generated:** 2026-10-06T03:28:41.788038+00:00  
**Benchmark Version:** 1.0.0  
**Validation Type:** `securecode_ground_truth_benchmark`  

---

## 1. Executive Summary & Traceability

| Artifact | Repository | Version | Commit Hash |
|---|---|---|---|
| **Product Under Test** | `Medalcode/SecureCode` | `0.1.0` | `bbc9c2747373ef31a3e9ba3589ae192842d2fd52` |
| **Independent Oracle** | `Medalcode/securecode-ground-truth` | `1.0.0` | `f006fb843f13fa09fa4ae39d6c2b0570385b7c1e` |

- **Synthetic Benchmark Cases:** 205 (GH-001: 105, GH-002: 100)
- **Empirical Pilot Cases:** 6 (GH-001: 6, GH-002: BLOCKED)
- **Synthetic Accuracy:** **100.0%** (205/205 matches, 0 mismatches)
- **Mutation Sensitivity Score:** **100.0%** (4/4 mutants detected)

---

## 2. 3x3 Multi-Class Confusion Matrix (Combined Benchmark, n=205)

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

---

## 3. Academic & Security Metrics (ES2 KPI: Correctitud)

### Binary Security Metrics (Positive Class = FAIL)

| Metric | GH-001 Synthetic | GH-002 Synthetic | Combined Synthetic |
|---|:---:|:---:|:---:|
| **Cases Evaluated** | 105 | 100 | 205 |
| **True Positives (TP)** | 35 | 33 | 68 |
| **True Negatives (TN)** | 35 | 34 | 69 |
| **False Positives (FP)** | 0 | 0 | 0 |
| **False Negatives (FN)** | 0 | 0 | 0 |
| **Accuracy (Binary)** | 100.0% | 100.0% | 100.0% |
| **Precision** | 100.0% | 100.0% | 100.0% |
| **Recall** | 100.0% | 100.0% | 100.0% |
| **F1-Score** | 100.0% | 100.0% | 100.0% |
| **UNKNOWN Accuracy** | 100.0% | 100.0% | 100.0% |
| **Overall 3-Class Accuracy**| 100.0% | 100.0% | 100.0% |

---

## 4. Mutation Sensitivity & Falsifiability Analysis

To guarantee that the benchmark is not trivially passing by circular construction, four isolated mutants were evaluated against the dataset:

| Mutation Scenario | Target Control | Evaluated Cases | Detected Mismatches | Mutation Detection Rate | Status |
|---|---|:---:|:---:|:---:|:---:|
| GH-001 Threshold Raised ($2 \to 3$) | GH-001 | 105 | 15 | 14.3% | **DETECTED** |
| GH-001 Ignore Dismiss Stale Reviews | GH-001 | 105 | 25 | 23.8% | **DETECTED** |
| GH-002 Inverted Protection Logic | GH-002 | 100 | 67 | 67.0% | **DETECTED** |
| GH-002 UNKNOWN Treated as PASS | GH-002 | 100 | 33 | 33.0% | **DETECTED** |

**Conclusion:** The benchmark harness actively falsifies flawed rule engines with a **100% mutant kill rate**.

---

## 5. Real-World GitHub Empirical Pilot Status

- **Control GH-001**:
  - Classification: **`REAL-GITHUB VALIDATED PILOT`** ($n=6$)
  - Results: 6 cases evaluated | 6 matches | 0 mismatches (**100% agreement**)
  - Evidence: Stored in `docs/evidence/ground_truth/GT-GH001-01` through `06`.
- **Control GH-002**:
  - Classification: **`REAL-GITHUB PILOT BLOCKED`**
  - Reason: GitHub REST API `/branches/{default_branch}/protection` strictly requires authentication even for public repositories. Without a configured `VALIDATION_GITHUB_TOKEN`, live pilot calls fall back safely to `UNKNOWN`.

---

## 6. Academic Limitations

1. **Synthetic Sample Equivalence**: Synthetic permutations validate deterministic logic boundaries across defined inputs, but cannot model unanticipated external API schema drift.
2. **Limited Control Scope**: Currently covers two controls (`GH-001` and `GH-002`). Additional controls (`GH-003+`) remain outside the current benchmark scope.
3. **Empirical Sample Size**: The empirical pilot for GH-001 is small ($n=6$) and intended for adapter protocol validation, not broad statistical inference.
4. **Provider Scope**: GitHub is currently the sole supported SCM provider.
