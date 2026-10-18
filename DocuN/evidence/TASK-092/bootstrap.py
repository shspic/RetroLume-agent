"""TASK-092 Windows 链测试自举：加载hash捕获 + 场景替身注入。

布局：
  [python,-B,bootstrap.py, sup, <evidence>, <mapping>]
  [python,-B,bootstrap.py, worker, <子模式>, <evidence>, <mapping>]

sup 包装：捕获加载hash；按 TASK092_WORKER_MODE 把固定worker路由到本文件worker模式；
随后以真实 argv 调 product supervisor_main.main（保留真实解码/监督/序列化主体）。
worker 子模式（导入真实 worker_main.main 执行，仅注入场景替身）：
  one_tool       真实工具链（计数真实 ToolRegistry.execute；禁止 transport.send）
  one_tool_block 工具执行边界替换为不合作同步阻塞（停止机制反例）
  one_call       真实模型链，仅发送边界替换为合成响应（禁止工具执行）
  legacy_worker  旧版worker行为：对 one_tool 按旧 argv 规则退出2
本文件永不进入产品导入链。
"""
from __future__ import annotations

import hashlib
import importlib.machinery
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

loaded_bytes = {}
_original_get_code = importlib.machinery.SourceFileLoader.get_code


def _capture_code(self, fullname):
    if fullname == "app" or fullname.startswith("app."):
        path = Path(self.get_filename(fullname)).resolve()
        raw = self.get_data(str(path))
        loaded_bytes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
        return self.source_to_code(raw, str(path))
    return _original_get_code(self, fullname)


importlib.machinery.SourceFileLoader.get_code = _capture_code


def _write_capture(evidence: Path, mode: str, extra: dict) -> None:
    loaded = {}
    for name, module in tuple(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if filename and name.startswith("app."):
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT) and path.suffix == ".py":
                loaded[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    target = evidence / f"bootstrap-{mode}-{os.getpid()}.json"
    target.write_text(json.dumps({"mode": mode, "pid": os.getpid(),
                                  "loaded_modules": loaded, "loaded_source_bytes": loaded_bytes, **extra},
                                 indent=2), encoding="utf-8")


def run_sup(evidence: Path, mapping: str) -> int:
    worker_mode = os.environ.get("TASK092_WORKER_MODE", "one_tool")
    from app.worker.command import WorkerCommand, _INTERPRETER

    original = WorkerCommand.argv
    routing = {"one_tool": "one_tool", "one_tool_block": "one_tool_block",
               "one_call": "one_call", "legacy_worker": "legacy_worker"}

    def test_argv(self, mapping_name=None):
        if self.task == "one_call":
            return [str(_INTERPRETER), "-B", str(Path(__file__).resolve()),
                    "worker", "one_call", str(evidence), mapping_name]
        if self.task == "one_tool":
            return [str(_INTERPRETER), "-B", str(Path(__file__).resolve()),
                    "worker", routing[worker_mode], str(evidence), mapping_name]
        return original(self, mapping_name)

    WorkerCommand.argv = test_argv
    from app.worker.supervisor_main import main
    sys.argv = ["supervisor_main", mapping]
    try:
        code = main()
    finally:
        _write_capture(evidence, "sup", {"worker_mode": worker_mode})
    return code


def run_worker(submode: str, evidence: Path) -> int:
    if submode == "legacy_worker":
        from legacy_probe import legacy_worker_main
        try:
            code = legacy_worker_main()
        finally:
            _write_capture(evidence, "worker-legacy", {"worker_mode": submode})
        return code
    counters = {"tool_execute_calls": 0, "transport_sends": 0, "message_roles": None}
    if submode == "one_call":
        from app.capabilities.transport import HttpxModelTransport, TransportResponse

        async def send(self, **kwargs):
            counters["transport_sends"] += 1
            if counters["transport_sends"] != 1:
                raise RuntimeError("test transport forbids resending")
            counters["message_roles"] = [m["role"] for m in kwargs["payload"]["messages"]]
            content = os.environ.get("TASK092_MODEL_ANSWER", "synthetic-answer-092")
            raw = json.dumps({"model": "synthetic-model",
                              "choices": [{"message": {"role": "assistant", "content": content},
                                           "finish_reason": "stop"}],
                              "usage": {"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3}}).encode()
            return TransportResponse(200, raw, len(raw))

        HttpxModelTransport.send = send
        from app.capabilities.tools import ToolRegistry

        def forbidden_execute(*args, **kwargs):
            raise RuntimeError("tool execution forbidden in one_call")

        ToolRegistry.execute = forbidden_execute
    elif submode in ("one_tool", "one_tool_block"):
        from app.capabilities.tools import ToolRegistry

        if submode == "one_tool":
            real_execute = ToolRegistry.execute

            def counting_execute(self, plan):
                counters["tool_execute_calls"] += 1
                return real_execute(self, plan)

            ToolRegistry.execute = counting_execute
        else:
            def blocking_execute(self, plan):
                time.sleep(600)  # 不合作同步阻塞：执行边界挂死反例

            ToolRegistry.execute = blocking_execute
        from app.capabilities.transport import HttpxModelTransport

        def forbidden_send(*args, **kwargs):
            raise RuntimeError("model transport forbidden in one_tool")

        HttpxModelTransport.send = forbidden_send
    else:
        raise SystemExit(2)
    from app.worker.worker_main import main
    try:
        code = main()
    finally:
        _write_capture(evidence, f"worker-{submode}", {"worker_mode": submode, **counters})
    return code


def main() -> int:
    mode = sys.argv[1]
    if mode == "sup":
        return run_sup(Path(sys.argv[2]).resolve(), sys.argv[3])
    if mode == "worker":
        submode, mapping = sys.argv[2], sys.argv[4]
        evidence = Path(sys.argv[3]).resolve()
        task = "one_call" if submode == "one_call" else "one_tool"
        sys.argv = ["worker_main", task, mapping]
        return run_worker(submode, evidence)
    raise SystemExit(2)


if __name__ == "__main__":
    try:
        code = main()
    except BaseException:
        code = 1
    raise SystemExit(code)
