"""固定worker入口；一次模型调用，正文与 received 终态在 record_outcome 同事务提交。

G3 协议3：回执仅身份/状态/hash（text/json_object 恒 None），正文从持久层读取；
business_commit 三值 committed/unconfirmed/not_committed。
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import sys
import time
from typing import Any

from .gate import ClosingCallGate
from .one_call import decode_worker_request, receipt
from .supervisor_ipc import NamedMapping
from app.activities import PostgresAdmissionLedger
from app.capabilities.gateway import ControlledModelGateway
from app.runtime import psycopg_compatible_loop_factory


async def run_controlled_worker(
    gateway: Any,
    work: Callable[[ClosingCallGate], Awaitable[None]],
    *,
    drain_timeout_seconds: float,
) -> None:
    gate = ClosingCallGate(gateway)
    await gate.arm()
    try:
        await work(gate)
    finally:
        await gate.close(timeout_seconds=drain_timeout_seconds)


async def run_internal_task(gateway: Any, task: str, context=None, request=None, *, call_seconds=1.0):
    """The injected gateway is only handed to work through ClosingCallGate."""
    if task not in ("idle", "one_call"):
        raise ValueError("unsupported internal worker task")

    async def idle(_gate: ClosingCallGate) -> None:
        return None

    async def one_call(gate: ClosingCallGate) -> None:
        nonlocal result
        if context is None or request is None:
            raise ValueError("one_call requires context and request")
        async with asyncio.timeout(call_seconds):
            result = await gate.call(context, request)

    result = None
    await run_controlled_worker(gateway, one_call if task == "one_call" else idle, drain_timeout_seconds=1.0)
    return result


async def execute_one_call(value):
    call, context = decode_worker_request(value)
    ledger = PostgresAdmissionLedger(**value["ledger"])
    gateway = ControlledModelGateway(call.service, ledger=ledger)
    # 单调截止由SUP固定；整体超时包括准入/发送/记账，不靠网络timeout扩窗。
    seconds = min(value["call_seconds"], (value["stop_ns"] - time.monotonic_ns()) / 1e9 - 0.25)
    if seconds <= 0:
        raise ValueError("call window expired")
    result = await run_internal_task(gateway, "one_call", context, call.request, call_seconds=seconds)
    return receipt(result, context, value["run_tag"])


def main() -> int:
    mapping = None
    try:
        if sys.argv[1:] == ["idle"]:
            return 0
        if len(sys.argv) != 3 or sys.argv[1] != "one_call":
            return 2
        mapping = NamedMapping.open_existing(sys.argv[2])
        value = mapping.read_request()
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            result = runner.run(execute_one_call(value))
        mapping.write_result(result)
        return 0
    except BaseException:
        # 包括模型验证异常都不输出消息/traceback/正文。
        return 1
    finally:
        if mapping is not None:
            try:
                mapping.close()
            except BaseException:
                return 1


if __name__ == "__main__":
    raise SystemExit(main())

