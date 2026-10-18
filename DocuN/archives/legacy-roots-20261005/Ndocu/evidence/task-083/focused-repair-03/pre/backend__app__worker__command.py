"""Fixed internal worker invocation. No executable or argv is caller supplied."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path



_BACKEND = Path(__file__).resolve().parents[2]
_INTERPRETER = _BACKEND / ".venv" / "Scripts" / "python.exe"


@dataclass(frozen=True)
class WorkerCommand:
    """Only the benign internal task is wired; product gateway injection is separate."""

    task: str = "idle"

    def __post_init__(self) -> None:
        if type(self.task) is not str or self.task not in ("idle", "one_call"):
            raise ValueError("unsupported internal worker task")

    @property
    def cwd(self) -> str:
        return str(_BACKEND)

    def argv(self) -> list[str]:
        return [str(_INTERPRETER), "-B", "-m", "app.worker.worker_main", self.task]


