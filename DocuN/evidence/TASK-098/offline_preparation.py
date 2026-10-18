"""唯一自身夹具准备：纯计算、假WinAPI和标准库self-pipe，不启业务。"""
import ast
import asyncio
from concurrent.futures import ThreadPoolExecutor
import ctypes
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
from unittest.mock import patch

from probe_support import HERE, ROOT, publish

sys.path.insert(0, str(ROOT / "backend"))


def main():
    started = time.monotonic()
    out = HERE / "offline-preparation"
    out.mkdir(exist_ok=False)
    checks = []
    for source in HERE.glob("*.py"):
        ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    checks.append("自己的全部Python源码AST无语法错误")
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda i: publish(f"publication-{i:02d}.json", {"n": i}, out), range(20)))
    assert [json.loads((out / f"publication-{i:02d}.json").read_text())["n"] for i in range(20)] == list(range(20))
    try:
        publish("publication-00.json", {"n": 99}, out)
    except FileExistsError:
        pass
    else:
        raise AssertionError("不可变发布被覆盖")
    assert json.loads((out / "publication-00.json").read_text())["n"] == 0
    checks.append("并发不可变发布及覆盖拒绝，无真实进程")

    import probe_bootstrap as bootstrap
    from app.worker import launcher

    class FakeApi:
        def CreateProcessW(self, *args):
            info = ctypes.cast(args[-1], ctypes.POINTER(launcher._PROCESS_INFORMATION)).contents
            info.hProcess, info.hThread, info.dwProcessId = 111, 222, 333
            return True

    class Partial:
        last = None
        pid = 333

        def __init__(self, api, info):
            type(self).last = self

        def creation_time_100ns(self):
            return 123

    for index, fault in enumerate(("identity", "publication")):
        target = out / fault
        target.mkdir()
        saved = publish

        def observed(name, value):
            if fault == "publication" and name.startswith("sup-created"):
                raise PermissionError("自己夹具的纯计算注入")
            return saved(name, value, target)

        with patch.dict(os.environ, {"RETROLUME_TASK098_PERMIT": "g7-audit-01"}), \
             patch.object(bootstrap, "RUN", target), patch.object(bootstrap, "publish", observed), \
             patch.object(launcher, "_api", return_value=FakeApi()):
            method = patch.object(Partial, "creation_time_100ns", side_effect=OSError("自己的身份读取故障")) if fault == "identity" else patch.object(Partial, "creation_time_100ns", return_value=123)
            with method:
                try:
                    bootstrap.create_supervisor(Partial, "fake_mapping_only")
                except launcher.ProcessCreationError as exc:
                    assert exc.partial is Partial.last
                else:
                    raise AssertionError("已创建实例未交回")
        assert len(list(target.glob("sup-attempt-*.json"))) == 1
    checks.append("创建后身份/发布故障均交回真实partial语义，仅假CreateProcess")

    import case_run
    cfg = out / "synthetic-config.json"
    cfg.write_text(json.dumps(case_run.config(), ensure_ascii=False), encoding="utf-8")
    from app.service_config import load_activity_config
    with patch.dict(os.environ, {"RETROLUME_TASK098_SYNTH_KEY": "synthetic-098-only"}):
        value = load_activity_config(cfg)
    assert value.create_layer.available and value.continue_layer.available and value.learning_layer.available
    checks.append("合成配置在现有合同纯内存校验可用，未建活动或连库")

    import probe_support as support
    old = (socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo, socket.socketpair)
    with patch.object(support, "event", lambda *args: None):
        try:
            support.install_network()
            async def no_business():
                await asyncio.sleep(0)
            from app.runtime import psycopg_compatible_loop_factory
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
                runner.run(no_business())
            try:
                socket.getaddrinfo("outside.invalid", 443)
            except OSError:
                pass
            else:
                raise AssertionError("外部DNS未早拒绝")
            with socket.socket() as probe:
                try:
                    probe.connect(("192.0.2.1", 443))
                except OSError:
                    pass
                else:
                    raise AssertionError("外网socket未早拒绝")
        finally:
            socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo, socket.socketpair = old
    checks.append("标准库self-pipe可用，外部DNS/socket提前拒绝，无外发")
    result = {"status": "PASS", "checks": checks, "elapsed_seconds": time.monotonic() - started,
              "entry": 0, "container_start": 0, "real_SUP": 0, "browser": 0, "driver": 0,
              "build": 0, "real_provider": 0,
              "own_sources": [{"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in HERE.glob("*.py")]}
    publish("preparation-result.json", result, out)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
