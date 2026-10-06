"""Dataset schema validation, coverage analysis, and redundancy checks."""

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VALID_CONTROLS = {"GH-001", "GH-002"}
VALID_STATUSES = {"PASS", "FAIL", "UNKNOWN"}
VALID_CASE_TYPES = {"synthetic", "empirical"}


def compute_file_sha256(path: Path) -> str:
    """Calculate raw SHA-256 digest of a file on disk."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def compute_canonical_sha256(data: Any) -> str:
    """Calculate deterministic canonical JSON SHA-256 digest."""
    canonical_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()


def load_dataset(path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Load dataset, accommodating both top-level list and top-level dict schemas."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, list):
        return {"cases": raw}, raw
    return raw, raw.get("cases", [])


def validate_case(case: Dict[str, Any], default_control: Optional[str] = None) -> List[str]:
    """Validate an individual test case against the Ground Truth specification."""
    errors = []

    case_id = case.get("case_id")
    if not case_id or not isinstance(case_id, str):
        errors.append("Missing or invalid 'case_id'")

    control = case.get("control_id") or case.get("control") or default_control
    if not control or control not in VALID_CONTROLS:
        errors.append(f"Invalid or missing control identifier: '{control}'")

    status = case.get("expected_status") or case.get("status")
    if not status or status not in VALID_STATUSES:
        errors.append(f"Invalid or missing expected status: '{status}'")

    evidence = case.get("evidence")
    if control == "GH-001":
        if evidence is None and "expected_approvals" in case:
            # Empirical baseline format
            pass
        elif not isinstance(evidence, dict):
            errors.append("Evidence must be a dictionary")
        else:
            if "required_review_approvals" not in evidence:
                errors.append("Missing 'required_review_approvals' in GH-001 evidence")
            if "dismiss_stale_reviews" not in evidence:
                errors.append("Missing 'dismiss_stale_reviews' in GH-001 evidence")
    elif control == "GH-002":
        if not isinstance(evidence, dict):
            errors.append("Evidence must be a dictionary")
        else:
            if "default_branch" not in evidence:
                errors.append("Missing 'default_branch' in GH-002 evidence")
            if "protection_enabled" not in evidence:
                errors.append("Missing 'protection_enabled' in GH-002 evidence")

    return errors


def validate_dataset_file(path: Path) -> List[str]:
    """Validate all cases in a dataset file and verify uniqueness."""
    errors = []
    if not path.exists():
        return [f"File not found: {path}"]

    meta, cases = load_dataset(path)
    default_control = meta.get("control_id") or meta.get("control")

    if not cases:
        errors.append(f"{path.name}: dataset contains zero cases")
        return errors

    seen_ids = set()
    for idx, case in enumerate(cases):
        case_errors = validate_case(case, default_control=default_control)
        for err in case_errors:
            errors.append(f"{path.name}[{idx}]: {err}")

        cid = case.get("case_id")
        if cid:
            if cid in seen_ids:
                errors.append(f"{path.name}[{idx}]: Duplicate case_id '{cid}'")
            seen_ids.add(cid)

    return errors


def analyze_coverage_gh001(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute semantic partition coverage for GH-001 benchmark."""
    status_counts = Counter()
    approval_partitions = Counter()
    dismiss_partitions = Counter()
    scenario_families = Counter()

    for c in cases:
        status = c.get("expected_status") or c.get("status")
        status_counts[status] += 1

        fam = c.get("scenario_family", "empirical_or_unclassified")
        scenario_families[fam] += 1

        ev = c.get("evidence")
        if ev:
            app = ev.get("required_review_approvals")
            ds = ev.get("dismiss_stale_reviews")
        else:
            app = c.get("expected_approvals")
            ds = c.get("expected_dismiss_stale")

        if app is None:
            approval_partitions["missing (None)"] += 1
        elif app < 2:
            approval_partitions["below threshold (<2)"] += 1
        elif app == 2:
            approval_partitions["at threshold (=2)"] += 1
        else:
            approval_partitions["above threshold (>2)"] += 1

        if ds is None:
            dismiss_partitions["missing (None)"] += 1
        elif ds is True:
            dismiss_partitions["true"] += 1
        else:
            dismiss_partitions["false"] += 1

    return {
        "total_cases": len(cases),
        "status_distribution": dict(status_counts),
        "approval_partitions": dict(approval_partitions),
        "dismiss_partitions": dict(dismiss_partitions),
        "scenario_families": dict(scenario_families),
    }


def analyze_coverage_gh002(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute semantic partition coverage for GH-002 benchmark."""
    status_counts = Counter()
    protection_partitions = Counter()

    for c in cases:
        status = c.get("expected_status") or c.get("status")
        status_counts[status] += 1

        pe = c["evidence"].get("protection_enabled")
        if pe is None:
            protection_partitions["missing / unknown (None)"] += 1
        elif pe is True:
            protection_partitions["protected (True)"] += 1
        else:
            protection_partitions["unprotected (False)"] += 1

    return {
        "total_cases": len(cases),
        "status_distribution": dict(status_counts),
        "protection_partitions": dict(protection_partitions),
    }


def analyze_duplicates(cases: List[Dict[str, Any]], control: str) -> Dict[str, Any]:
    """Analyze identical evidence permutations across cases."""
    evidence_tuples = []
    for c in cases:
        ev = c.get("evidence")
        if control == "GH-001":
            if ev:
                evidence_tuples.append((ev.get("required_review_approvals"), ev.get("dismiss_stale_reviews")))
            else:
                evidence_tuples.append((c.get("expected_approvals"), c.get("expected_dismiss_stale")))
        elif control == "GH-002":
            evidence_tuples.append((ev.get("default_branch"), ev.get("protection_enabled")))

    counts = Counter(evidence_tuples)
    unique_configs = len(counts)
    duplicate_count = len(cases) - unique_configs

    return {
        "total_cases": len(cases),
        "unique_evidence_configurations": unique_configs,
        "duplicate_evidence_cases": duplicate_count,
        "configuration_frequencies": {str(k): v for k, v in counts.items()},
    }
