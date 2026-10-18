"""Fixed internal worker invocation. No executable or argv is caller supplied."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path



_BACKEND = Path(__file__).resolve().parents[2]
_INTERPRETER = _BACKEND / ".venv" / "Scripts" / "python.exe"


@dataclass(frozen=True)
class WorkerCommand:
    """固定任务枚举；秘密和正文只能走映射。"""

    task: str = "idle"

    def __post_init__(self) -> None:
        if type(self.task) is not str or self.task not in ("idle", "one_call"):
            raise ValueError("unsupported internal worker task")

    @property
    def cwd(self) -> str:
        return str(_BACKEND)

    def argv(self, mapping_name: str | None = None) -> list[str]:
        result = [str(_INTERPRETER), "-B", "-m", "app.worker.worker_main", self.task]
        if self.task == "one_call":
            from .supervisor_ipc import validate_name
            result.append(validate_name(mapping_name))
        elif mapping_name is not None:
            raise ValueError("idle does not accept business data")
        return result


