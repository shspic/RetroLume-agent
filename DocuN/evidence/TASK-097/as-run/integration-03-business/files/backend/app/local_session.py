"""本地会话与来源校验的共享依赖。

materials/pdf_review 原行为逐字保留；allow_own_origin 仅用于放行应用自身
来源，使同一页面在不同本地端口（如 18095 测试端口）下的同源写请求可用。
跨站请求、未知来源与非本应用来源的拒绝保持不变；localhost 本身不是授权。
"""
from __future__ import annotations

import secrets
from fastapi import HTTPException, Request

_FIXED_ORIGINS = frozenset({
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
})


def local_request(request: Request, *, allow_own_origin: bool = False) -> None:
    origin = request.headers.get("origin")
    if request.headers.get("sec-fetch-site") == "cross-site":
        raise HTTPException(403, "拒绝跨站访问")
    if origin and origin not in _FIXED_ORIGINS:
        own_origin = f"{request.url.scheme}://{request.url.netloc}"
        if not (allow_own_origin and origin == own_origin):
            raise HTTPException(403, "拒绝未知来源")


def local_session(request: Request, *, allow_own_origin: bool = False) -> None:
    local_request(request, allow_own_origin=allow_own_origin)
    if not secrets.compare_digest(
        request.headers.get("x-retrolume-session", "").encode("utf-8"),
        request.app.state.session_token.encode("utf-8"),
    ):
        raise HTTPException(403, "本地会话已失效，请刷新页面")
