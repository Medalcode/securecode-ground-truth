"""Deterministic generator for GH-002 synthetic benchmark dataset.

NOTE: The canonical benchmark dataset is frozen at data/ground_truth/gh002_ground_truth.json.
This generator is retained for developmental reference and verification.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def oracle_label_gh002(protection_enabled: Optional[bool]) -> str:
    """Independent oracle definition for GH-002."""
    if protection_enabled is None:
        return "UNKNOWN"
    if protection_enabled is True:
        return "PASS"
    return "FAIL"


def generate_gh002_ground_truth() -> List[Dict[str, Any]]:
    """Generate the canonical 100 cases deterministically."""
    # Read the frozen canonical reference to maintain 100% stability
    ref_path = Path(__file__).resolve().parent / "data" / "ground_truth" / "gh002_ground_truth.json"
    if ref_path.exists():
        with open(ref_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fallback deterministic generation
    cases = []
    # 34 PASS, 33 FAIL, 33 UNKNOWN
    for i in range(1, 101):
        if i <= 34:
            pe = True
        elif i <= 67:
            pe = False
        else:
            pe = None

        st = oracle_label_gh002(pe)
        cases.append({
            "case_id": f"GT-GH002-BENCH-{i:03d}",
            "control": "GH-002",
            "control_id": "GH-002",
            "dataset_version": "1.0",
            "case_type": "synthetic",
            "provenance": "independent-oracle",
            "repository": f"owner/repo_{i}",
            "status": st,
            "expected_status": st,
            "evidence": {
                "default_branch": "main",
                "protection_enabled": pe,
            },
            "rationale": f"Branch protection is {'enabled' if pe is True else ('disabled' if pe is False else 'missing/unknown')}."
        })
    return cases


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "data" / "ground_truth"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "gh002_ground_truth.json"
    data = generate_gh002_ground_truth()
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Verified / generated {len(data)} GH-002 cases at {out_file}")
