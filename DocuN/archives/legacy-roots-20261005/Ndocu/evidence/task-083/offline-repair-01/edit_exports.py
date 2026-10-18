"""Exact-anchor public internal export update."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
path = ROOT / "backend/app/worker/__init__.py"
data = path.read_text(encoding="utf-8")
old = 'from .gate import ClosingCallGate, GateClosed\nfrom .session import SessionConfig, SessionOutcome, SingleWindowSupervisor\n\n__all__ = ["ClosingCallGate", "GateClosed", "SessionConfig", "SessionOutcome", "SingleWindowSupervisor"]\n'
new = 'from .command import WorkerCommand\nfrom .gate import ClosingCallGate, GateClosed\nfrom .launcher import run_supervised_window\nfrom .session import SessionConfig, SessionOutcome\nfrom .worker_main import run_controlled_worker\n\n__all__ = ["WorkerCommand", "ClosingCallGate", "GateClosed", "SessionConfig", "SessionOutcome", "run_controlled_worker", "run_supervised_window"]\n'
assert data.count(old) == 1
path.write_text(data.replace(old, new), encoding="utf-8", newline="")
