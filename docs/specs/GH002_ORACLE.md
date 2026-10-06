# GH-002 Oracle Specification — Default Branch Protection Enabled

**Control ID:** GH-002  
**Category:** Source Code Management / Branch Protection  
**Document Version:** 1.0  
**Authority:** Medalcode / securecode-ground-truth  

---

## 1. Control Objective

To deterministically evaluate whether a repository enforces branch protection on its default branch (e.g., `main` or `master`), preventing unreviewed or direct pushes into production branches.

---

## 2. Required Normalized Evidence Model

Evidence presented to the oracle consists of two parameters:

| Evidence Field | Type | Description |
|---|---|---|
| `default_branch` | `str` | Name of the repository's primary branch (e.g., `"main"`). |
| `protection_enabled` | `Optional[bool]` | Whether branch protection is active on `default_branch`. `None` if unobservable or indeterminable. |

---

## 3. Independent Decision Rules & Boundaries

### 3.1 PASS Condition
The control evaluates to **`PASS`** if and only if:
1. `protection_enabled` is strictly `True`.

### 3.2 FAIL Condition
The control evaluates to **`FAIL`** if and only if:
1. `protection_enabled` is strictly `False`.

### 3.3 UNKNOWN Condition
The control evaluates to **`UNKNOWN`** if:
1. `protection_enabled` is `None`, OR
2. Evidence object is `None`, OR
3. API authentication/scoping errors prevent trustworthy observation.

---

## 4. Truth & Boundary Decision Table

| `default_branch` | `protection_enabled` | Boundary Class | Oracle Status | Rationale |
|:---:|:---:|---|:---:|---|
| Valid string (`"main"`) | `True` | Protected Default | **`PASS`** | Branch protection is actively configured on default branch. |
| Valid string (`"main"`) | `False` | Unprotected Default | **`FAIL`** | Default branch is confirmed to exist but has no protection rules. |
| Valid string (`"main"`) | `None` | Indeterminate | **`UNKNOWN`** | Protection state cannot be confirmed (missing token, API error). |
| Empty / None | Any | Invalid Evidence | **`UNKNOWN`** | Unspecified default branch. |

---

## 5. Formal Mathematical Specification

$$\text{Oracle}_{\text{GH-002}}(B, P) = \begin{cases}
\text{UNKNOWN} & \text{if } B = \text{null} \lor B = \text{""} \lor P = \text{null} \\
\text{PASS} & \text{if } P = \text{true} \\
\text{FAIL} & \text{if } P = \text{false}
\end{cases}$$

---

## 6. Real-World GitHub API Evidence Acquisition Semantics

GitHub's REST API requires sequential verification to eliminate ambiguity regarding HTTP status codes (specifically `404 Not Found`):

```text
Step 1: Discover Default Branch
GET /repos/{owner}/{repo}
  ├── 200 OK      ──► Capture default_branch name (proceed to Step 2)
  └── 404/403/401 ──► UNKNOWN (Repository inaccessible, missing, or rate-limited)

Step 2: Verify Branch Existence
GET /repos/{owner}/{repo}/branches/{default_branch}
  ├── 200 OK      ──► Branch verified (proceed to Step 3)
  └── 404/403/401 ──► UNKNOWN (Branch missing or inaccessible)

Step 3: Check Protection Rules
GET /repos/{owner}/{repo}/branches/{default_branch}/protection
  ├── 200 OK        ──► protection_enabled = True  (PASS)
  ├── 404 Not Found ──► protection_enabled = False (FAIL) 
  │                     [Confirmed branch exists in Step 2; 404 means unprotected]
  └── 401/403       ──► protection_enabled = None  (UNKNOWN)
                        [Requires authentication; unobservable without token]
```

### Empirical Operational Note
The endpoint `/branches/{default_branch}/protection` strictly requires an authenticated GitHub token even for public repositories. Consequently, empirical execution without `GITHUB_TOKEN` yields HTTP 401/403, correctly triggering an **`UNKNOWN`** classification rather than a false violation (`FAIL`).
