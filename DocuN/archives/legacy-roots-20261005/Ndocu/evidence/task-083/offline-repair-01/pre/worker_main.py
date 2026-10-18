"""供未来业务worker入口注入任务函数的内部单窗运行骨架。

本卡没有产品任务/供应商接线；唯一可交给任务函数的是受门控的gateway包装器。
任务正常返回后先排空，才允许进程以成功码退出；异常或排空超时向外失败。
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from .gate import ClosingCallGate


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
