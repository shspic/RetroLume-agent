"""TASK-083 fixture-completion-06 pre evidence: byte copies + SHA-256 drift check.

Drift policy per card: verify BEFORE copying; stop on any mismatch, never overwrite.
Scope: card-named three files only (no repo-wide rescan, per card).
"""
import hashlib
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
SRC = ROOT / "backend/tests/fixtures/task083"
EV = ROOT / "Ndocu/evidence/task-083/fixture-completion-06"
PRE = EV / "pre"
PRE.mkdir(parents=True, exist_ok=True)

EXPECT = {
    "focused_unit.py": "4a633aff536f833cdbf3a266be2d44de70b8e01105a204b68d7947995627a1ca",
    "job_control.py": "5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2",
    "offline_unit.py": "3029a709f615ab068d65004d1083568d0a96e577417380b26109defaf0a64c5c",
}

lines = ["# fixture-completion-06 pre hashes (managed Python 3.13.12 hashlib, read-only)",
         "# Scope: card-named three files; other freezes carried per stub-fix-05/final-hashes.txt and review-04 evidence."]
for name, expect in EXPECT.items():
    data = (SRC / name).read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expect:
        raise SystemExit(f"DRIFT STOP: {name} actual={actual} expect={expect}")
    (PRE / f"pre__{name}").write_bytes(data)
    lines.append(f"{actual}  backend/tests/fixtures/task083/{name}  == card freeze MATCH (pre copy pre__{name})")

(PRE / "pre-hashes.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print("pre copies saved:", PRE)
