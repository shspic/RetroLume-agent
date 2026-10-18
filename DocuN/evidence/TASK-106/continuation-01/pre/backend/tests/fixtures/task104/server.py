"""真实产品 factory/router/dist；本卡安全外壳只接受读取请求。"""
import argparse, asyncio, sys
from pathlib import Path
import uvicorn
from starlette.responses import JSONResponse
from app.main import create_app
from app.runtime import psycopg_compatible_loop_factory
from app.worker.session import SessionConfig
from .common import write, stamp

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    run_dir = Path(parser.parse_args().run_dir)
    attempts = []

    def audit_network(event, args):
        if event in ("socket.connect", "socket.getaddrinfo"):
            address = args[1] if event == "socket.connect" else args[0]
            host = address[0] if isinstance(address, tuple) else address
            if isinstance(host, str) and host not in ("127.0.0.1", "localhost", "::1"):
                attempts.append({"at": stamp(), "event": event, "host": host})
                write(run_dir / "network-denied.json", attempts)
                raise RuntimeError("本只读审计禁止真实外部连接")

    sys.addaudithook(audit_network)
    app = create_app()
    app.state.teaching_session_config = SessionConfig(
        window_seconds=20, request_timeout_seconds=2, stop_grace_seconds=2, startup_limit_seconds=5,
        manager_db_timeout_seconds=5, cleanup_seconds=5, mutex_wait_seconds=3, manager_overhead_seconds=30,
        single_host_single_session_recovery=False,
    )

    @app.middleware("http")
    async def readonly(request, next_handler):
        if request.method not in ("GET", "HEAD"):
            attempts.append({"at": stamp(), "method": request.method, "path": request.url.path})
            write(run_dir / "forbidden-http.json", attempts)
            return JSONResponse({"detail": {"code": "audit_read_only", "message": "本审计仅允许读取"}}, status_code=405)
        return await next_handler(request)

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=18103, loop="none", access_log=False, log_level="warning"))

    async def serve():
        async def stop_watch():
            while not server.should_exit:
                if (run_dir / "stop-api.json").exists():
                    server.should_exit = True
                await asyncio.sleep(0.1)
        watch = asyncio.create_task(stop_watch())
        try:
            await server.serve()
        finally:
            watch.cancel()

    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
        runner.run(serve())

if __name__ == "__main__":
    main()
