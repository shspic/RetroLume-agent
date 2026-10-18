"""无重试的受限 HTTP transport。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

import httpx


class RequestNotSent(RuntimeError):
    """能够确定请求未到达远端连接的失败。"""


class DeliveryUnknown(RuntimeError):
    """开始发送后无法确认远端是否处理的失败。"""


@dataclass(frozen=True)
class TransportResponse:
    status_code: int
    body: bytes
    response_bytes: int
    remote_request_id: str | None = None
    body_too_large: bool = False


class ModelTransport(Protocol):
    async def send(
        self,
        *,
        endpoint: str,
        api_key: str,
        payload: Mapping[str, Any],
        timeout_seconds: float,
        max_response_bytes: int,
    ) -> TransportResponse: ...


class HttpxModelTransport:
    """单次 POST；禁代理、禁重定向、禁 SDK/transport 自动重试。"""
    # 默认真实传输，只有获准合成夹具的最低传输替身可另标False。
    is_external = True

    async def send(
        self,
        *,
        endpoint: str,
        api_key: str,
        payload: Mapping[str, Any],
        timeout_seconds: float,
        max_response_bytes: int,
    ) -> TransportResponse:
        timeout = httpx.Timeout(timeout_seconds)
        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=False,
                trust_env=False,
            ) as client:
                request = client.build_request(
                    "POST",
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response = await client.send(request, stream=True)
                chunks: list[bytes] = []
                size = 0
                async for chunk in response.aiter_bytes():
                    size += len(chunk)
                    if size > max_response_bytes:
                        await response.aclose()
                        return TransportResponse(
                            status_code=response.status_code,
                            body=b"",
                            response_bytes=size,
                            remote_request_id=response.headers.get("x-request-id"),
                            body_too_large=True,
                        )
                    chunks.append(chunk)
                return TransportResponse(
                    status_code=response.status_code,
                    body=b"".join(chunks),
                    response_bytes=size,
                    remote_request_id=response.headers.get("x-request-id"),
                )
        except (httpx.PoolTimeout, httpx.ConnectTimeout, httpx.ConnectError) as exc:
            raise RequestNotSent("连接建立前失败") from exc
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
            raise DeliveryUnknown("请求处理状态不明") from exc

