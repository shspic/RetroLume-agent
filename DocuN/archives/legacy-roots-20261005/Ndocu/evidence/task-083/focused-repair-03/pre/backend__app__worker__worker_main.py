"""Fixed internal worker entry. Product supplier routing remains unwired."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import sys
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


async def run_internal_task(gateway: Any, task: str) -> None:
    """The injected gateway is only handed to work through ClosingCallGate."""
    if task not in ("idle", "one_call"):
        raise ValueError("unsupported internal worker task")

    async def idle(_gate: ClosingCallGate) -> None:
        return None

    async def one_call(gate: ClosingCallGate) -> None:
        await gate.call(None, None)

    await run_controlled_worker(gateway, one_call if task == "one_call" else idle, drain_timeout_seconds=1.0)


class _UnwiredGateway:
    async def call(self, _context: Any, _request: Any) -> None:
        raise RuntimeError("product gateway is not connected")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ("idle", "one_call"):
        return 2
    asyncio.run(run_internal_task(_UnwiredGateway(), sys.argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

