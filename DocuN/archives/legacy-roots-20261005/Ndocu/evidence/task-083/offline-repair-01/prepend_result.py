"""Prepend current repair result while retaining every byte of the 083 initial report."""

from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
result = ROOT / "Ndocu/results/TASK-083-result.md"
top = ROOT / "Ndocu/evidence/task-083/offline-repair-01/result-top.md"
backup = ROOT / "Ndocu/evidence/task-083/offline-repair-01/pre/TASK-083-result.before.md"
old = result.read_bytes()
assert sha256(old).hexdigest() == "f2149de31e4f706e3c06e1ccadaacb63e6276e4a561674078abac86646dbb0de"
assert not backup.exists()
backup.write_bytes(old)
prefix = top.read_bytes()
result.write_bytes(prefix + old)
assert result.read_bytes().endswith(old)
