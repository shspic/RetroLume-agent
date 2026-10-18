"""单窗内部 worker 的纯数据命令；SUP 不接受任意构造回调。"""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class WorkerCommand:
    executable: str
    arguments: tuple[str, ...]
    cwd: str

    def __post_init__(self) -> None:
        if type(self.executable) is not str or self.executable.startswith("\\") or not os.path.isabs(self.executable) or not os.path.isfile(self.executable):
            raise ValueError("worker须为既有绝对可执行文件")
        if type(self.cwd) is not str or self.cwd.startswith("\\") or not os.path.isabs(self.cwd) or not os.path.isdir(self.cwd):
            raise ValueError("worker工作目录须为既有绝对目录")
        if type(self.arguments) is not tuple or len(self.arguments) > 64:
            raise ValueError("worker参数须为有界不可变数据")
        if any(type(arg) is not str or "\x00" in arg or len(arg) > 4096 for arg in self.arguments):
            raise ValueError("worker参数非法")
        if sum(len(arg) for arg in self.arguments) + len(self.executable) > 16_384:
            raise ValueError("worker命令过长")

    def argv(self) -> list[str]:
        return [self.executable, *self.arguments]
