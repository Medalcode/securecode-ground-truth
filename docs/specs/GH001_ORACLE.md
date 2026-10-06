# GH-001 Oracle Specification — Branch Protection Review Policy

**Control ID:** GH-001  
**Category:** Source Code Management / Branch Protection  
**Document Version:** 1.0  
**Authority:** Medalcode / securecode-ground-truth  

---

## 1. Control Objective

To deterministically evaluate whether a repository's protected branch policy enforces mandatory peer code reviews and automatically dismisses stale approvals upon new commits.

---

## 2. Required Normalized Evidence Model

Evidence presented to the oracle consists of two parameters:

| Evidence Field | Type | Description |
|---|---|---|
| `required_review_approvals` | `Optional[int]` | Minimum number of required approving pull request reviews. `None` if absent/unconfigured. |
| `dismiss_stale_reviews` | `Optional[bool]` | Whether existing approvals are dismissed when new commits are pushed. `None` if absent/unconfigured. |

---

## 3. Independent Decision Rules & Boundaries

### 3.1 PASS Condition
The control evaluates to **`PASS`** if and only if **both** of the following criteria are satisfied:
1. `required_review_approvals` is an integer $\ge 2$.
2. `dismiss_stale_reviews` is strictly `True`.

### 3.2 FAIL Condition
The control evaluates to **`FAIL`** if the evidence is complete (neither field is `None`), but at least one requirement is violated:
1. `required_review_approvals < 2` (e.g., 0 or 1), OR
2. `dismiss_stale_reviews == False`.

### 3.3 UNKNOWN Condition
The control evaluates to **`UNKNOWN`** if either evidence field is absent or indeterminate:
1. `required_review_approvals is None`, OR
2. `dismiss_stale_reviews is None`, OR
3. Evidence object itself is `None`.

---

## 4. Truth & Boundary Decision Table

| Approvals ($A$) | Dismiss Stale ($D$) | Boundary Class | Oracle Status | Rationale |
|:---:|:---:|---|:---:|---|
| $\ge 2$ (e.g., 2, 3, 4) | `True` | Baseline / Compliant | **`PASS`** | Meets threshold ($\ge 2$) and enforces fresh reviews. |
| 1 | `True` | Below Threshold | **`FAIL`** | Insufficient peer reviews (only 1 approval required). |
| 0 | `True` | Zero Threshold | **`FAIL`** | No mandatory approvals required. |
| $\ge 2$ | `False` | Stale Permitted | **`FAIL`** | Stale approvals remain valid after new code is pushed. |
| $< 2$ | `False` | Dual Violation | **`FAIL`** | Neither review count nor stale dismissal satisfied. |
| `None` | `True` | Missing Review Count | **`UNKNOWN`** | Cannot assess review count threshold. |
| `None` | `False` | Missing Review Count | **`UNKNOWN`** | Incomplete evidence; cannot determine compliance. |
| $\ge 0$ | `None` | Missing Stale Flag | **`UNKNOWN`** | Cannot determine if stale approvals are dismissed. |
| `None` | `None` | Total Omission | **`UNKNOWN`** | No branch protection policy data available. |

---

## 5. Formal Mathematical Specification

$$\text{Oracle}_{\text{GH-001}}(A, D) = \begin{cases}
\text{UNKNOWN} & \text{if } A = \text{null} \lor D = \text{null} \\
\text{PASS} & \text{if } A \ge 2 \land D = \text{true} \\
\text{FAIL} & \text{otherwise}
\end{cases}$$

This formal specification is completely independent of programming language or product implementation.
