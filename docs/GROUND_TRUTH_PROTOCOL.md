# Ground Truth Oracle & Benchmark Protocol

**Document Version:** 1.0  
**Authority:** Medalcode / securecode-ground-truth  
**Scope:** Compliance Evaluation Oracles (GH-001, GH-002)

---

## 1. Purpose & Core Objective

The primary objective of `securecode-ground-truth` is to serve as the **independent, authoritative, and reproducible oracle** for validating the correctness of the **SecureCode** compliance evaluation engine.

It answers the foundational validation question:
> *"Given a normalized evidence scenario, what SHOULD the expected security evaluation be, completely independent of SECURECODE's internal implementation?"*

To maintain academic and industrial rigor:
- Ground Truth is an **audit artifact** and test harness, not a second copy of the product.
- Ground Truth must never define its expectations by executing or reproducing product code.
- Validation must be falsifiable and sensitive to engine defects.

---

## 2. Independence Requirements & Non-Circularity Rule

### The Non-Circularity Law
$$\text{Expected Status} \neq f_{\text{SecureCode}}(\text{Evidence})$$

Under no circumstances may a Ground Truth dataset or benchmark harness derive `expected_status` by calling `securecode.engine.evaluator` or duplicating the internal rule structures of the product.

### Explicit Independence Constraints
1. **No Product Import for Oracles**: Dataset generation scripts, benchmark reference files, and test oracles MUST NOT import SecureCode evaluators to compute labels.
2. **Pre-Existing Reference Datasets**: Ground Truth reference datasets must exist and be cryptographically frozen *before* SecureCode is invoked.
3. **External Validation Boundary**: When measuring SecureCode against Ground Truth, SecureCode is treated as a black box (or gray box through public typed APIs `evaluate_gh001` and `evaluate_gh002`). The predicted status from the product is compared against the pre-recorded `expected_status`.

---

## 3. Classification States & Mathematical Semantics

The oracle recognizes three mutually exclusive deterministic outcomes:

| Classification Status | Oracle Definition | Operational Meaning |
|---|---|---|
| **`PASS`** | The evidence satisfies all mandated security requirements of the control. | Compliant posture. |
| **`FAIL`** | The evidence is complete, but violates at least one mandated security requirement. | Non-compliant posture (security violation detected). |
| **`UNKNOWN`** | The evidence is missing, partial, corrupted, or inaccessible. | Unobservable state; cannot assert compliance or violation. |

### Treatment of `UNKNOWN`
- `UNKNOWN` is a **first-class status**, not an implicit failure or passing state.
- In security contexts, assuming `FAIL` on missing evidence creates false positives that erode operator trust; assuming `PASS` creates dangerous false negatives.
- `UNKNOWN` is excluded from binary confusion counters ($TP, TN, FP, FN$) and evaluated separately through **UNKNOWN Accuracy**:
  $$\text{UNKNOWN Accuracy} = \frac{\text{Correctly Classified UNKNOWN}}{\text{Total Expected UNKNOWN}}$$

### Positive Class Definition
In accordance with academic security benchmarking standards (e.g., ISO/IEC 25010, ES1/ES2 specifications):
- **Positive Class = `FAIL`**: The primary detection objective is identifying security vulnerabilities and control failures.
- **Negative Class = `PASS`**: Conforming states represent the negative baseline.

---

## 4. Evidence Categorization: Synthetic vs. Empirical

The Ground Truth repository strictly segregates evidence into two orthogonal categories:

```text
┌────────────────────────────────────────────────────────┐
│                   Ground Truth Evidence                │
├───────────────────────────┬────────────────────────────┤
│    Synthetic Benchmark    │    Empirical API Pilot     │
│  - Controlled permutations│  - Real GitHub REST calls  │
│  - Full boundary coverage │  - Live audit evidence     │
│  - Offline & deterministic│  - Requires API token/auth │
│  - Scale: n=100+          │  - Pilot scale: n=6        │
└───────────────────────────┴────────────────────────────┘
```

1. **Synthetic Benchmark**:
   - Synthesized evidence records designed to exercise every boundary condition, combinatorial state, and edge case of the specification.
   - Run fully offline with zero external network dependencies or API token requirements.
   - Example: 105 cases for GH-001; 100 cases for GH-002.
2. **Empirical API Pilot**:
   - Raw HTTP responses captured from real GitHub repository/branch endpoints.
   - Validates that the product's external adapter correctly normalizes real-world API responses into the typed evidence model.
   - Must never be conflated with the synthetic benchmark in summary claims.
   - Example: 6 empirically validated branch configurations in `Medalcode/securecode-ground-truth` for GH-001.

---

## 5. Case Schema Specification

Every benchmark case in canonical datasets must adhere to the following schema:

```json
{
  "case_id": "GT-GH001-BENCH-001",
  "control": "GH-001",
  "control_id": "GH-001",
  "dataset_version": "1.0",
  "case_type": "synthetic",
  "provenance": "independent-oracle",
  "evidence": { ... },
  "expected_status": "PASS",
  "rationale": "Clear human-auditable justification of expected outcome."
}
```

### Mandatory Fields
- `case_id`: Globally unique identifier matching `GT-<CONTROL>-<TYPE>-<NUM>` format.
- `control_id` / `control`: Target security control identifier (`GH-001` or `GH-002`).
- `dataset_version`: Semantic version of the dataset (e.g., `1.0`).
- `case_type`: Either `"synthetic"` or `"empirical"`.
- `provenance`: Origin of the ground truth label (e.g., `"independent-oracle"`, `"empirical-github"`).
- `evidence`: Dictionary containing the normalized evidence fields.
- `expected_status`: One of `PASS`, `FAIL`, or `UNKNOWN`.
- `rationale`: Auditable rationale explaining why the oracle assigns this status.

---

## 6. Dataset Freezing & Cryptographic Integrity

1. **Immutable Storage**: Once validated, dataset files in `data/ground_truth/` are frozen and committed to version control.
2. **Deterministic Hashing**:
   - Each canonical dataset is identified by its SHA-256 digest.
   - Hashes are tracked in `benchmark/manifest.json`.
3. **No Dynamic Regeneration in CI**: Normal CI/CD pipeline runs MUST NOT re-run generation scripts to overwrite frozen datasets. CI validates the committed files against their recorded manifest hashes.

---

## 7. Versioning & Correction Procedure

1. **Dataset Versioning**: Datasets follow semantic versioning (`v1.0`, `v1.1`, `v2.0`).
2. **Defect Correction Protocol**:
   - If a discrepancy arises between SecureCode and Ground Truth, **the expected label MUST NOT be modified simply to force 100% agreement**.
   - A label correction requires verifiable proof that the oracle specification or manual label was erroneous.
   - Any approved label correction triggers a version bump, a changelog entry documenting the justification, and an update to `benchmark/manifest.json`.

---

## 8. Mutation Sensitivity & Falsifiability

A benchmark that cannot fail is scientifically useless. To prove the validity of the Ground Truth harness:
- The test suite must incorporate **mutation sensitivity tests**.
- Mutations intentionally alter the rule evaluation semantics (e.g., changing approval threshold from 2 to 3, inverting boolean logic).
- The benchmark harness MUST detect these mutations with a non-zero mutation detection rate, verifying that the benchmark actively polices engine accuracy.

---

## 9. Zero Secret Storage Policy

Under no circumstances may empirical evidence files or test fixtures contain:
- GitHub Personal Access Tokens (`ghp_*`, `github_pat_*`)
- Bearer tokens or `Authorization` HTTP headers
- Passwords or private keys

Evidence acquisition adapters must strip all authorization headers prior to serialization in `docs/evidence/`.
