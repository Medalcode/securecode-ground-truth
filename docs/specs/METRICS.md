# Metrics Specification

## 1. Purpose
This document specifies how to evaluate the accuracy of the deterministic engine when classifying security-control compliance states against the validated Ground Truth. It establishes the mathematical and semantic foundation for measuring performance, ensuring the engine correctly identifies control violations without distorting results due to missing evidence.

## 2. Classification States
The system strictly operates on three deterministic states. The evaluator semantics remain unchanged:
- **PASS**: The control satisfies the required conditions.
- **FAIL**: The control does not satisfy the required conditions.
- **UNKNOWN**: The evidence is insufficient (missing or incomplete) to determine compliance.

## 3. Positive Class
**FAIL is the positive class** for Precision, Recall, and F1 calculations.
In the context of SecureCode, the objective is the detection of control violations (security risks). Therefore, successfully detecting a violation (FAIL) is a True Positive. 
PASS is the negative class. It must not be inferred that PASS is the positive class.

## 4. Treatment of UNKNOWN
Based on the ES1 academic definition, UNKNOWN is a distinct, explicit state, not an implicit failure or success.
- Binary classification metrics (TP, TN, FP, FN) operate **only** on cases where both Expected and Actual statuses are either PASS or FAIL.
- Cases involving UNKNOWN (whether Expected or Actual) are **excluded** from TP/TN/FP/FN.
- UNKNOWN cases are evaluated separately through a specific metric: 
  `UNKNOWN Accuracy = correctly classified UNKNOWN cases / total expected UNKNOWN cases`.

Explicit treatment rules:
- **Expected FAIL + Actual UNKNOWN**
  → Excluded from binary TP/TN/FP/FN.
  → Not counted as a correctly detected violation.
  → Tracked separately as an UNKNOWN outcome.
- **Expected UNKNOWN + Actual FAIL/PASS**
  → Excluded from binary TP/TN/FP/FN.
  → Counted as an incorrect UNKNOWN classification (reduces UNKNOWN Accuracy).
- **Expected UNKNOWN + Actual UNKNOWN**
  → Excluded from binary TP/TN/FP/FN.
  → Counted as a correct UNKNOWN (`UNKNOWN_CORRECT`).
- **Expected PASS + Actual UNKNOWN**
  → Excluded from binary TP/TN/FP/FN.
  → Tracked as an UNKNOWN outcome rather than silently treating it as a binary negative.

## 5. Confusion Matrix
The binary counters are defined strictly over the eligible binary universe (Expected ∈ {PASS, FAIL} AND Actual ∈ {PASS, FAIL}):

- **TP (True Positive)**: Expected FAIL AND Actual FAIL
- **FP (False Positive)**: Expected PASS AND Actual FAIL
- **FN (False Negative)**: Expected FAIL AND Actual PASS
- **TN (True Negative)**: Expected PASS AND Actual PASS

*Note: Expected or Actual UNKNOWN does not increment any of these four counters.*

## 6. 3x3 Classification Matrix
The following table provides the unambiguous mapping for all 9 possible evaluation outcomes:

| | Actual PASS | Actual FAIL | Actual UNKNOWN |
|---|---|---|---|
| **Expected PASS** | TN | FP | excluded |
| **Expected FAIL** | FN | TP | excluded |
| **Expected UNKNOWN** | excluded | excluded | UNKNOWN_CORRECT |

## 7. Metrics
The formulas to be implemented are:

- **Accuracy** = (TP + TN) / (TP + TN + FP + FN)
- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **F1** = 2 * Precision * Recall / (Precision + Recall)
- **UNKNOWN Accuracy** = UNKNOWN_CORRECT / TOTAL_EXPECTED_UNKNOWN

**Zero-Denominator Behavior:**
Una métrica cuyo denominador matemático sea cero se considera **no definida para ese conjunto de datos**.
La implementación deberá representar ese estado mediante `None`.

| Métrica          | Denominador                         | Denominador = 0 |
| ---------------- | ----------------------------------- | --------------- |
| Accuracy         | TP + TN + FP + FN                   | `None`          |
| Precision        | TP + FP                             | `None`          |
| Recall           | TP + FN                             | `None`          |
| F1               | requiere Precision y Recall válidos | `None`          |
| UNKNOWN Accuracy | TOTAL_EXPECTED_UNKNOWN              | `None`          |

También se documenta que:
* `None` significa "métrica no definida para este conjunto de datos".
* `None` no significa `0%`.
* `None` no significa `100%`.
* `None` no debe interpretarse como PASS, FAIL o UNKNOWN.
* La presencia de `None` no constituye por sí misma un error del evaluador.

## 8. Scope
This specification applies initially to the **GH-001** vertical slice. It is not a generic metrics framework. The implementation must not introduce configurable classes, generic rule engines, expression languages, or abstract mathematical models beyond what is strictly specified here for GH-001.

## 9. Implementation Contract
The future metrics implementation must fulfill a strict contract. 

**Inputs (at minimum):**
- Expected status (Enum or String)
- Actual status (Enum or String)

**Outputs (at minimum):**
- `TP` (int)
- `TN` (int)
- `FP` (int)
- `FN` (int)
- `Accuracy` (float)
- `Precision` (float)
- `Recall` (float)
- `F1` (float)
- `UNKNOWN_CORRECT` (int)
- `TOTAL_EXPECTED_UNKNOWN` (int)
- `UNKNOWN Accuracy` (float)

*Note: Do not implement this contract yet.*

## 10. Example
This example is based on the 6 empirically validated GH-001 Ground Truth cases. Because the current integration test yields 100% agreement, the actual statuses match the expected statuses perfectly.

**Dataset Distribution:**
- GT-GH001-01: Expected PASS, Actual PASS
- GT-GH001-02: Expected FAIL, Actual FAIL
- GT-GH001-03: Expected FAIL, Actual FAIL
- GT-GH001-04: Expected FAIL, Actual FAIL
- GT-GH001-05: Expected UNKNOWN, Actual UNKNOWN
- GT-GH001-06: Expected UNKNOWN, Actual UNKNOWN

**Resulting Counters:**
- TP = 3 (Cases 02, 03, 04)
- FP = 0
- FN = 0
- TN = 1 (Case 01)
- UNKNOWN_CORRECT = 2 (Cases 05, 06)
- TOTAL_EXPECTED_UNKNOWN = 2

**Resulting Metrics:**
- Accuracy = (3 + 1) / (3 + 1 + 0 + 0) = 4 / 4 = 1.0
- Precision = 3 / (3 + 0) = 1.0
- Recall = 3 / (3 + 0) = 1.0
- F1 = 2 * 1.0 * 1.0 / (1.0 + 1.0) = 1.0
- UNKNOWN Accuracy = 2 / 2 = 1.0

*Note: This example demonstrates the specification logic and does not constitute a claim or baseline for future datasets.*

## 11. Traceability
- **ES1 Academic Definition**: `Informe_ES1_SECURECODE_INACAP.docx`
- **GH-001 Specification**: `docs/specs/GH-001.md`
- **Ground Truth**: `data/ground_truth/gh001_ground_truth.json`
- **Integration Test**: `tests/integration/test_ground_truth.py`
