"""应用运行时兼容入口。"""

from __future__ import annotations

import asyncio
import sys


def psycopg_compatible_loop_factory() -> asyncio.AbstractEventLoop:
    """创建 psycopg 异步连接兼容的事件循环。"""

    if sys.platform == "win32":
        return asyncio.SelectorEventLoop()
    return asyncio.new_event_loop()
