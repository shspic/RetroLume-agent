"""TASK-095 Windows 链测试自举：SUP/worker 入口替换与传输替身注入。

布局（均由真实 launcher/SUP 以固定 CreateProcessW/句柄路径拉起）：
  [python,-B,bootstrap95.py, sup, <evidence>, <mapping>]
  [python,-B,bootstrap95.py, worker, <evidence>, <mapping>]

sup：仅把 WorkerCommand.argv 的 one_call 目标替换为本文件 worker 模式，
     随后调用真实 supervisor_main.main（真实 claim/Job/树零/关门/结算）。
worker：仅把 HttpxModelTransport.send 替换为受控合成响应（单次发送、禁重发，
     记录消息角色），并禁止工具执行；随后调用真实 worker_main.main。
本文件永不进入产品导入链；管道合法性仍由产品协议逐跳校验。
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]  # DocuN/evidence/TASK-095/win -> 项目根
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))


def run_sup(evidence: Path, mapping: str) -> int:
    from app.worker.command import WorkerCommand, _INTERPRETER

    original = WorkerCommand.argv

    def test_argv(self, mapping_name=None):
        if self.task == "one_call":
            return [str(_INTERPRETER), "-B", str(HERE / "bootstrap95.py"),
                    "worker", str(evidence), mapping_name]
        return original(self, mapping_name)

    WorkerCommand.argv = test_argv
    from app.worker.supervisor_main import main
    sys.argv = ["supervisor_main", mapping]
    return main()


def run_worker(evidence: Path, mapping: str) -> int:
    plan = json.loads((evidence / "transport-plan.json").read_text(encoding="utf-8"))
    counters = {"transport_sends": 0, "message_roles": None}
    from app.capabilities.transport import HttpxModelTransport, TransportResponse

    async def send(self, **kwargs):
        counters["transport_sends"] += 1
        if counters["transport_sends"] != 1:
            raise RuntimeError("test transport forbids resending")
        counters["message_roles"] = [item["role"] for item in kwargs["payload"]["messages"]]
        if plan.get("delay_seconds"):
            import asyncio
            await asyncio.sleep(float(plan["delay_seconds"]))
        raw = json.dumps({
            "model": plan["model"],
            "choices": [{"message": {"role": "assistant", "content": plan["content"]},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": plan["prompt_tokens"],
                      "completion_tokens": plan["completion_tokens"],
                      "total_tokens": plan["total_tokens"]},
        }).encode("utf-8")
        (evidence / f"transport-send-{os.getpid()}.json").write_text(
            json.dumps(counters, ensure_ascii=False), encoding="utf-8",
        )
        return TransportResponse(200, raw, len(raw))

    HttpxModelTransport.send = send
    from app.capabilities.tools import ToolRegistry

    def forbidden_execute(*args, **kwargs):
        raise RuntimeError("tool execution forbidden in one_call")

    ToolRegistry.execute = forbidden_execute
    from app.worker.worker_main import main
    sys.argv = ["worker_main", "one_call", mapping]
    return main()


def main() -> int:
    # argv: [bootstrap95.py, mode, evidence, mapping]
    mode = sys.argv[1]
    if mode == "sup":
        return run_sup(Path(sys.argv[2]).resolve(), sys.argv[3])
    if mode == "worker":
        return run_worker(Path(sys.argv[2]).resolve(), sys.argv[3])
    raise SystemExit(2)


if __name__ == "__main__":
    try:
        code = main()
    except BaseException:
        code = 1
    raise SystemExit(code)
