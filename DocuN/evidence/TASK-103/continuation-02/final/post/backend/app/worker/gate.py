"""在worker进程内覆盖完整受控调用的不可重开本地发送门。"""

from __future__ import annotations

import asyncio
from typing import Any


class GateClosed(RuntimeError):
    pass


class ClosingCallGate:
    """只向业务回调暴露此包装器，不交出原始gateway。

    每个共享令牌从admit之前持续到gateway.call全部返回/抛出；关闭者先
    置closed再等待活跃数归零，后来的读者不能使关闭者饥饿。
    """

    def __init__(self, gateway: Any) -> None:
        self._gateway = gateway
        self._condition = asyncio.Condition()
        self._armed = False
        self._closed = False
        self._active = 0

    @property
    def active_calls(self) -> int:
        return self._active

    @property
    def closed(self) -> bool:
        return self._closed

    async def arm(self) -> None:
        async with self._condition:
            if self._armed or self._closed:
                raise GateClosed("发送门不能重新开启")
            self._armed = True

    async def call(self, context: Any, request: Any) -> Any:
        async with self._condition:
            if not self._armed or self._closed:
                raise GateClosed("发送门未开启或已永久关闭")
            self._active += 1
        try:
            return await self._gateway.call(context, request)
        finally:
            async with self._condition:
                self._active -= 1
                self._condition.notify_all()

    async def close(self, *, timeout_seconds: float) -> None:
        if timeout_seconds <= 0:
            raise ValueError("关闭等待必须为正数")
        async with self._condition:
            self._closed = True
            self._condition.notify_all()
            async with asyncio.timeout(timeout_seconds):
                await self._condition.wait_for(lambda: self._active == 0)

