"""098单例真实应用/SUP/worker注入，仅增加记录、屏障和合成transport。"""
from dataclasses import asdict
import asyncio
import ctypes
import hashlib
import importlib.machinery
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time

from probe_support import HERE, ROOT, RUN, event, load, publish, install_network

sys.path.insert(0, str(ROOT / "backend"))


def install_imports():
    original = importlib.machinery.SourceFileLoader.get_code

    def get_code(self, fullname):
        path = Path(self.path).resolve()
        if path.is_relative_to(ROOT / "backend/app") or path.is_relative_to(HERE):
            raw = self.get_data(self.path)
            event("import", {"pid": os.getpid(), "module": fullname, "path": path.relative_to(ROOT).as_posix(),
                             "sha256": hashlib.sha256(raw).hexdigest()})
            return self.source_to_code(raw, self.path)
        return original(self, fullname)

    importlib.machinery.SourceFileLoader.get_code = get_code
    event("boot", {"mode": sys.argv[1] if len(sys.argv) > 1 else "case-runner", "pid": os.getpid(), "at": time.time(),
                   "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


SUP_LOCK = threading.Lock()


def create_supervisor(cls, mapping_name):
    from app.worker import launcher
    if os.environ.get("RETROLUME_TASK098_PERMIT") != "g7-audit-01":
        raise RuntimeError("098_exact_permit_required")
    with SUP_LOCK:
        total = len(list(RUN.glob("sup-attempt-*.json")))
        if total >= 2:
            raise RuntimeError("098_sup_limit")
        number = total + 1
        publish(f"sup-attempt-{number:02d}.json", {"at": time.time(), "caller_pid": os.getpid(),
                "created": False, "number": number, "permit": "g7-audit-01",
                "mapping_sha256": hashlib.sha256(mapping_name.encode()).hexdigest()})
    api = launcher._api()
    exe = str(sys._base_executable)
    argv = [exe, "-B", str(HERE / "probe_bootstrap.py"), "sup", mapping_name]
    command = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
    environment = launcher._environment_block()
    startup = launcher._STARTUPINFOW()
    startup.cb = ctypes.sizeof(startup)
    info = launcher._PROCESS_INFORMATION()
    created = api.CreateProcessW(exe, command, None, None, False,
                                launcher.CREATE_SUSPENDED | launcher.CREATE_NO_WINDOW | launcher.CREATE_UNICODE_ENVIRONMENT,
                                ctypes.cast(environment, ctypes.c_void_p), str(launcher._BACKEND),
                                ctypes.byref(startup), ctypes.byref(info))
    instance = cls(api, info) if info.hProcess or info.hThread else None
    if not created or not info.hProcess or not info.hThread:
        raise launcher.ProcessCreationError(ctypes.get_last_error(), instance)
    try:
        # CreateProcess后的所有观察均受partial保护，包括GetProcessTimes。
        created_time = instance.creation_time_100ns()
        publish(f"sup-created-{number:02d}.json", {"number": number, "pid": instance.pid,
                "created_100ns": created_time, "created": True, "at": time.time(),
                "attempt_file": f"sup-attempt-{number:02d}.json"})
    except BaseException as exc:
        raise launcher.ProcessCreationError(ctypes.get_last_error(), instance) from exc
    return instance


def install_launcher():
    from app.worker import launcher, one_call
    launcher._SuspendedSupervisor.create = classmethod(create_supervisor)
    original_resume = launcher._SuspendedSupervisor.resume

    def resume(self):
        original_resume(self)
        event("sup-resumed", {"pid": self.pid, "created_100ns": self.creation_time_100ns(), "at": time.time()})

    launcher._SuspendedSupervisor.resume = resume
    original = one_call.run_one_call
    gate = threading.Barrier(2)
    case = load(RUN / "case-spec.json")

    def observed(*args, **kwargs):
        ledger, config, activity_id, executor_id, operation_id, request, service = args
        profile = request.learning_profile
        if activity_id != case["activity_id"] or profile is None or profile.goal not in case["goals"]:
            raise ValueError("098_unexpected_candidate")
        event("candidate-prepared", {"at": time.time(), "monotonic_ns": time.monotonic_ns(),
              "activity_id": activity_id, "goal": profile.goal, "request_sha256": profile.request_sha256,
              "operation_id": operation_id, "scope_revision": profile.scope_revision,
              "sources": [s.model_dump() for s in profile.sources], "output_tokens": request.max_output_tokens,
              "request_validated_by_application": True, "run_tag": kwargs["run_tag"]})
        gate.wait(timeout=10)
        event("candidate-barrier-released", {"at": time.time(), "goal": profile.goal, "run_tag": kwargs["run_tag"]})
        result = original(*args, **kwargs)
        publish("session-" + result.run_tag + ".json", asdict(result))
        return result

    one_call.run_one_call = observed


def sup():
    from app.worker.windows_job import NamedJob
    original_close = NamedJob.close
    original_terminate = NamedJob.terminate

    def close(self):
        count, error = None, None
        try:
            count = self.active_processes() if self.handle else None
        except BaseException as exc:
            error = type(exc).__name__
        name = self.name
        result = original_close(self)
        event("job-closed", {"job_name": name, "active_processes_before_close": count,
                            "pid": os.getpid(), "at": time.time(), "close_returned": True,
                            "observation_error": error})
        return result

    def terminate(self):
        count, error = None, None
        try:
            count = self.active_processes()
        except BaseException as exc:
            error = type(exc).__name__
        result = original_terminate(self)
        event("job-terminated", {"job_name": self.name, "active_processes_before_terminate": count,
                                "pid": os.getpid(), "at": time.time(), "observation_error": error})
        return result

    NamedJob.close, NamedJob.terminate = close, terminate
    from app.worker.command import WorkerCommand
    original = WorkerCommand.argv

    def argv(self, mapping_name=None):
        validated = original(self, mapping_name)
        if self.task == "one_call":
            return [validated[0], "-B", str(HERE / "probe_bootstrap.py"), "worker", mapping_name]
        return validated

    WorkerCommand.argv = argv
    from app.worker.supervisor_main import main
    sys.argv = ["supervisor_main", sys.argv[2]]
    return main()


def worker():
    from app.worker.gate import ClosingCallGate
    original_close = ClosingCallGate.close

    async def close(self, **kwargs):
        result = await original_close(self, **kwargs)
        event("gate-closed", {"closed": self.closed, "active_calls": self.active_calls, "pid": os.getpid()})
        return result

    ClosingCallGate.close = close
    from app.capabilities.transport import HttpxModelTransport, TransportResponse
    sent = False

    async def send(self, **kwargs):
        nonlocal sent
        if sent:
            raise RuntimeError("098_repeat_send_forbidden")
        sent = True
        payload = kwargs["payload"]
        data = json.loads(payload["messages"][-1]["content"])
        evidence = data["evidence"][0]
        event("transport", {"pid": os.getpid(), "at": time.time(), "payload": payload,
                            "transport_only_synthetic": True, "dns_socket_calls": 0, "send_number": 1})
        await asyncio.sleep(0.4)
        value = {"kind": "answer", "message": "098合成竞争取证，引用身份可回查。",
                 "segments": [{"text": evidence["text"], "citations": [evidence["id"]]}], "questions": []}
        raw = json.dumps({"model": payload["model"], "choices": [{"finish_reason": "stop",
              "message": {"role": "assistant", "content": json.dumps(value, ensure_ascii=False)}}],
              "usage": {"prompt_tokens": 10, "completion_tokens": 32, "total_tokens": 42}}, ensure_ascii=False).encode()
        event("response", {"model_output": value, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        return TransportResponse(200, raw, len(raw))

    HttpxModelTransport.send = send
    from app.worker.worker_main import main
    sys.argv = ["worker_main", "one_call", sys.argv[2]]
    return main()


def app():
    install_launcher()
    from app.main import create_app
    from app.runtime import psycopg_compatible_loop_factory
    import uvicorn
    application = create_app()
    server = uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=18098,
                                          access_log=False, log_level="critical"))
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
        runner.run(server.serve())
    return 0


if __name__ == "__main__":
    install_imports()
    install_network()
    try:
        code = {"app": app, "sup": sup, "worker": worker}[sys.argv[1]]()
    except BaseException as exc:
        event("bootstrap-failure", {"pid": os.getpid(), "type": type(exc).__name__, "at": time.time()})
        code = 1
    raise SystemExit(code)
