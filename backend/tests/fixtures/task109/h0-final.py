"""C04单根内本地增量构建、完整关口观测和精确收尾。"""
import hashlib
import base64
import json
from pathlib import Path
import queue
import secrets
import shutil
import subprocess
import sys
import threading
import time
import os
import argparse


sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "backend/app/preview"))
from contracts import read_observation
from supervisor import PERMIT, atomic_json, clean_env, docker_call, inspect_owned, process_birth

AREA = ROOT / "DocuN/evidence/TASK-109/execution/continuation-04"
IMAGE = None
CONFIG = None


class RecordedStream:
    """保全实际stdout封包，不改变协议读取结果。"""
    def __init__(self, stream, target):
        self.stream = stream
        self.output = target.open("wb")
        self.target = target
        self.total = 0
        self.saved = 0
        self.digest = hashlib.sha256()
        self.eof = False

    def read(self, count):
        data = self.stream.read(count)
        if not data:
            self.eof = True
        self.total += len(data)
        self.digest.update(data)
        piece = data[:max(0, 2097152-self.saved)]
        self.output.write(piece)
        self.output.flush()
        self.saved += len(piece)
        return data

    def close(self):
        self.output.close()
        atomic_json(self.target.with_name("stdout-capture.json"), {"total_bytes_seen": self.total, "saved_bytes": self.saved, "truncated": self.total > self.saved, "observed_sha256": self.digest.hexdigest(), "eof": self.eof})


def run_attempt(session, root_record, root_deadline, attempt_index):
    session_path = AREA / "session.json"
    t0 = time.monotonic_ns()
    run = AREA / ("root-" + str(attempt_index + 5).zfill(2)) / "preview"
    run.mkdir(parents=True, exist_ok=False)
    descriptor = {"attempt": attempt_index, "start_ns": t0, "state": "started", "root": root_record["id"], "action_permit": "TASK-109-G11-C04-20261009"}
    session.setdefault("attempts", []).append(descriptor)
    atomic_json(session_path, session)
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("Docker CLI不可用")
    calls = []
    observations = []
    cid = None
    image = None
    attach = None
    event_process = None
    reaper = None
    reaper_registry = None
    nonce = secrets.token_hex(16)
    events_since_epoch = int(time.time())
    observation_state = {}
    terminal = None
    failure = None
    name = "retrolume-task-109-g11-preview-" + str(attempt_index + 2).zfill(2)
    cleanup_deadline = None
    def call(args, timeout=8):
        deadline = min(cleanup_deadline or root_deadline, session["effective_deadline_ns"])
        remaining = (deadline-time.monotonic_ns()) / 1000000000
        if remaining <= 0:
            raise RuntimeError("真实根硬截止")
        result = docker_call(docker, args, min(timeout, remaining))
        calls.append(result)
        atomic_json(run / "docker-calls.json", calls)
        return result
    def read_output():
        sequence = 1
        chunks = {}
        packets = []
        packet_timings = []
        raw_stream = RecordedStream(attach.stdout, run / "container-stdout.bin")
        try:
            while True:
                row = read_observation(raw_stream, sequence)
                if row is None:
                    return
                sequence += 1
                if sequence > 256:
                    raise ValueError("观测包或队列超限")
                packets.append(row)
                packet_timings.append({"seq": sequence - 1, "received_ns": time.monotonic_ns(), "kind": row.get("kind")})
                atomic_json(run / "protocol-packets.json", packets)
                atomic_json(run / "packet-timings.json", packet_timings)
                if row["kind"] == "bounded_chunk":
                    part = row["data"]
                    if not 1 <= part["count"] <= 8 or not 4097 <= part["full_bytes"] <= 16384:
                        raise ValueError("累计观测超限")
                    group = chunks.setdefault(part["id"], [])
                    if part["index"] != len(group):
                        raise ValueError("分片观测乱序")
                    group.append(base64.b64decode(part["base64"], validate=True))
                    if len(group) < part["count"]:
                        continue
                    raw = b"".join(group)
                    if len(raw) != part["full_bytes"] or hashlib.sha256(raw).hexdigest() != part["full_sha256"]:
                        raise ValueError("完整观测摘要不符")
                    row = json.loads(raw)
                    del chunks[part["id"]]
                observations.append(row)
                atomic_json(run / "observations.json", observations)
                if row["kind"] == "diagnostic_begin":
                    if "diagnostic_start_ns" in observation_state or row["data"].get("limit_seconds") != 15 or row["data"].get("each_observation_ms") != 2000:
                        raise ValueError("真实诊断窗口或观察时间不符")
                    observation_state["diagnostic_start_ns"] = packet_timings[-1]["received_ns"]
                    observation_state["diagnostic_deadline_ns"] = observation_state["diagnostic_start_ns"] + 15000000000
                    atomic_json(run / "diagnostic-window.json", observation_state)
                if row["kind"] == "load_identity":
                    identity = row["data"]
                    frozen = json.loads((run.parent / "frozen-input.json").read_text("utf-8"))
                    if identity.get("node") != "v24.18.1" or identity.get("package") != "1.62.1" or identity.get("executable_sha256") != "0b20b130e7edd9dd51873be867761295fe0cfad490c2b9a64f95bd3cfc08fa71" or identity.get("input_manifest_sha256") != frozen["input_manifest_sha256"]:
                        raise ValueError("真实Node、包、binary或镜像输入清单身份不符")
                if row["kind"] == "terminal":
                    messages.put(row)
        except Exception as error:
            messages.put({"kind": "parser_error", "data": str(error)[:2000]})
            try:
                while raw_stream.read(1024):
                    pass
            except OSError:
                pass
        finally:
            raw_stream.close()
    def capture(stream, target, limit):
        tail = bytearray()
        total = 0
        with target.open("wb") as output:
            remaining = limit
            while True:
                chunk = stream.read(1024)
                if not chunk:
                    target.with_name("container-stderr-tail.log").write_bytes(bytes(tail))
                    atomic_json(target.with_name("stderr-capture.json"), {"total_bytes_seen": total, "saved_prefix_bytes": min(total, limit), "prefix_truncated": total > limit, "tail_bytes": len(tail), "tail_limit": 16384})
                    return
                total += len(chunk)
                tail.extend(chunk)
                if len(tail) > 16384:
                    del tail[:-16384]
                if remaining:
                    piece = chunk[:remaining]
                    output.write(piece)
                    output.flush()
                    remaining -= len(piece)
    try:
        names = call(["ps", "-a", "--filter", "name=^" + name + "$", "--format", "{{.Names}}"], 8)
        if names["code"] or name in names["stdout"].splitlines():
            raise RuntimeError("本卡专用容器名冲突")
        inspected = call(["image", "inspect", "--format", '{"id":{{json .Id}},"descriptor":{{json .Descriptor}},"user":{{json .Config.User}},"entrypoint":{{json .Config.Entrypoint}},"os":{{json .Os}},"architecture":{{json .Architecture}},"labels":{{json .Config.Labels}}}', IMAGE], 8)
        if inspected["code"]:
            raise RuntimeError("核证镜像缺失或不可读取，不拉取")
        metadata = json.loads(inspected["stdout"])
        image = metadata["id"]
        if image != IMAGE or metadata["descriptor"]["digest"] != IMAGE or metadata["descriptor"].get("annotations", {}).get("config.digest") != CONFIG or metadata["user"] != "10001:10001" or metadata["entrypoint"] != ["node", "/opt/preview/h0-counter.cjs"] or metadata["os"] != "linux" or metadata["architecture"] != "amd64" or metadata["labels"].get("retrolume.task") != "TASK-109" or metadata["labels"].get("retrolume.action-permit") != "TASK-109-G11-C04-20261009":
            raise RuntimeError("实际immutable image/config或构建出处不符")
        atomic_json(run / "loaded-image-reused.json", metadata)
        registry = run / "reaper-registry.json"
        reaper_registry = {"parent_pid": os.getpid(), "parent_birth": process_birth(os.getpid()), "docker": docker, "nonce": nonce, "controller_deadline_ns": min(time.monotonic_ns() + 900000000000, root_deadline), "cid": None, "complete": False}
        atomic_json(registry, reaper_registry)
        session["controllers"].append({"start_ns": time.monotonic_ns(), "deadline_ns": reaper_registry["controller_deadline_ns"], "registry": str(registry)})
        atomic_json(session_path, session)
        reaper = subprocess.Popen([sys.executable, "-B", "-u", str(ROOT / "backend/app/preview/reaper.py"), str(registry)], stdout=subprocess.DEVNULL, stderr=(run / "reaper-stderr.log").open("wb"), env=clean_env(), creationflags=subprocess.CREATE_NO_WINDOW)
        process_rows = {"controller": {"pid": os.getpid(), "birth": process_birth(os.getpid()), "argv": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]}, "reaper": {"pid": reaper.pid, "birth": process_birth(reaper.pid), "argv": [sys.executable, "-B", "-u", str(ROOT / "backend/app/preview/reaper.py"), str(registry)]}, "attach": None, "events": None}
        atomic_json(run / "owned-processes.json", process_rows)
        ready_deadline = time.monotonic_ns() + 3000000000
        while not (run / "reaper-ready.json").is_file():
            if reaper.poll() is not None or time.monotonic_ns() >= ready_deadline:
                raise RuntimeError("独立救援器未就绪")
            time.sleep(0.05)
        runtime_start = time.monotonic_ns()
        runtime_deadline = min(runtime_start + 60000000000, root_deadline)
        bootstrap = (ROOT / "deploy/preview/runtime-bootstrap.cjs").read_text(encoding="utf-8")
        atomic_json(run / "bootstrap-identity.json", {"path": str(ROOT / "deploy/preview/runtime-bootstrap.cjs"), "sha256": hashlib.sha256(bootstrap.encode("utf-8")).hexdigest(), "argv_source_is_frozen_trusted_only": True, "bytes": len(bootstrap.encode("utf-8"))})
        (run / "bootstrap-as-run.cjs").write_text(bootstrap, encoding="utf-8")
        create_args = ["create", "--pull=never", "--name", name, "--label", "retrolume.task=TASK-109", "--label", "retrolume.permit=" + PERMIT, "--label", "retrolume.synthetic=true", "--label", "retrolume.phase=H0-C04", "--label", "retrolume.action-permit=TASK-109-G11-C04-20261009", "--label", "retrolume.attempt=" + str(attempt_index), "--label", "retrolume.nonce=" + nonce, "--network=none", "--user=10001:10001", "--cap-drop=ALL", "--security-opt", "no-new-privileges", "--security-opt", "seccomp=" + str(ROOT / "deploy/preview/seccomp.json"), "--read-only", "--restart=no", "--init", "--cpus=1", "--memory=768m", "--memory-swap=768m", "--pids-limit=128", "--ipc=private", "--shm-size=64m", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=128m,uid=10001,gid=10001,mode=1777", "--tmpfs", "/home/preview:rw,nosuid,nodev,noexec,size=32m,uid=10001,gid=10001,mode=0700", "--env", "HOME=/home/preview", "--env", "XDG_CONFIG_HOME=/home/preview/.config", "--env", "XDG_CACHE_HOME=/home/preview/.cache", "--env", "XDG_RUNTIME_DIR=/home/preview/.runtime", "--env", "TMPDIR=/tmp/task109-private", "--env", "DEBUG=pw:browser", "--env", "DEBUG_COLORS=0", "--entrypoint", "node", image, "-e", bootstrap]
        create_args[1:1] = ["--label", "retrolume.root=" + root_record["id"]]
        session["preview_create"] = len(session["preview_creates"]) + 1
        session["preview_creates"].append({"before_ns": time.monotonic_ns(), "name": name, "runtime_deadline_ns": runtime_deadline})
        atomic_json(session_path, session)
        try:
            created = call(create_args, 15)
        except subprocess.TimeoutExpired:
            found = call(["inspect", "--format", "{{.Id}}", name], 8)
            if found["code"] == 0:
                candidate = found["stdout"].strip()
                inspect_owned(docker, candidate, image, nonce, timeout=8)
                cid = candidate
            raise RuntimeError("create超时；只找回本次CID用于收尾，不重复create/start")
        if created["code"]:
            raise RuntimeError("受限容器create失败")
        cid = created["stdout"].strip()
        if len(cid) != 64 or any(c not in "0123456789abcdef" for c in cid):
            raise RuntimeError("create返回CID未确认，不能继续start")
        owned = inspect_owned(docker, cid, image, nonce)
        host = owned["host"]
        if owned["user"] != "10001:10001" or host["NetworkMode"] != "none" or not host["ReadonlyRootfs"] or host["Privileged"] or host["Binds"] or owned["ports"] or any(m.get("Type") != "tmpfs" or m.get("Source") or m.get("Destination") not in {"/tmp", "/home/preview"} for m in owned["mounts"]) or set((host["Tmpfs"] or {}).keys()) != {"/tmp", "/home/preview"} or host["PidMode"] or host["IpcMode"] != "private" or host["CapAdd"] or host["CapDrop"] != ["ALL"] or host["NanoCpus"] != 1000000000 or host["Memory"] != 805306368 or host["MemorySwap"] != 805306368 or host["PidsLimit"] != 128 or not host["Init"] or host["ShmSize"] != 67108864:
            raise RuntimeError("实际受限配置或挂载身份不符")
        atomic_json(run / "container-created.json", owned)
        security = host["SecurityOpt"] or []
        previous_security = json.loads((ROOT / "DocuN/evidence/TASK-109/execution/continuation-03/resume-01/root-05/attempt-01/container-created.json").read_text("utf-8"))["host"]["SecurityOpt"]
        if security != previous_security or host["RestartPolicy"].get("Name") != "no" or "uid=10001,gid=10001,mode=1777" not in host["Tmpfs"]["/tmp"] or "uid=10001,gid=10001,mode=0700" not in host["Tmpfs"]["/home/preview"]:
            raise RuntimeError("原seccomp、NNP、固定目录归属或重启配置漂移")
        reaper_registry.update({"cid": cid, "image": image, "runtime_deadline_ns": runtime_deadline})
        atomic_json(registry, reaper_registry)
        bound_deadline = min(time.monotonic_ns() + 3000000000, runtime_deadline)
        while not (run / "reaper-bound.json").is_file():
            if reaper.poll() is not None or time.monotonic_ns() >= bound_deadline:
                raise RuntimeError("CID未被独立救援器接管，不start")
            time.sleep(0.05)
        events_file = (run / "docker-events.log").open("wb")
        event_args = [docker, "events", "--since", str(events_since_epoch), "--filter", "container=" + cid, "--format", "{{json .}}"]
        event_process = subprocess.Popen(event_args, stdout=events_file, stderr=subprocess.DEVNULL, env=clean_env(), creationflags=subprocess.CREATE_NO_WINDOW)
        session["preview_start"] = len(session["preview_starts"]) + 1
        session["preview_starts"].append({"before_ns": time.monotonic_ns(), "cid": cid, "deadline_ns": runtime_deadline})
        atomic_json(session_path, session)
        attach = subprocess.Popen([docker, "start", "-a", "-i", cid], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=clean_env(), creationflags=subprocess.CREATE_NO_WINDOW)
        process_rows["attach"] = {"pid": attach.pid, "birth": process_birth(attach.pid), "argv": [docker, "start", "-a", "-i", cid]}
        process_rows["events"] = {"pid": event_process.pid, "birth": process_birth(event_process.pid), "argv": event_args}
        atomic_json(run / "owned-processes.json", process_rows)
        messages = queue.Queue()
        reader = threading.Thread(target=read_output, daemon=True); reader.start()
        stderr_reader = threading.Thread(target=capture, args=(attach.stderr, run / "container-stderr.log", 65536), daemon=True); stderr_reader.start()
        while time.monotonic_ns() < min(runtime_deadline - 15000000000, observation_state.get("diagnostic_deadline_ns", runtime_deadline)):
            try:
                remaining = (min(runtime_deadline - 15000000000, observation_state.get("diagnostic_deadline_ns", runtime_deadline))-time.monotonic_ns()) / 1000000000
                terminal = messages.get(timeout=max(0.001, min(0.05, remaining)))
                break
            except queue.Empty:
                if attach.poll() is not None:
                    failure = "真实容器已退出但未交付完整观测"
                    break
        if terminal is None and failure is None:
            failure = "固定诊断15秒或预览截止前没有完整观测"
        if terminal and terminal.get("kind") == "parser_error":
            failure = terminal["data"]
        descriptor["runtime_start_ns"] = runtime_start
        descriptor["runtime_observed_until_ns"] = time.monotonic_ns()
        if "diagnostic_start_ns" in observation_state:
            descriptor["diagnostic_seconds"] = (descriptor["runtime_observed_until_ns"]-observation_state["diagnostic_start_ns"]) / 1000000000
    except Exception as error:
        failure = str(error)[:2000]
    finally:
        cleanup_start = time.monotonic_ns()
        cleanup_deadline = min(cleanup_start + int(max(0, 600-session["cleanup_seconds"]) * 1000000000), session["effective_deadline_ns"])
        cleanup = {"cid": cid, "image": image, "nonce": nonce, "physical_tree": "unconfirmed"}
        if cid and image:
            try:
                before = inspect_owned(docker, cid, image, nonce)
                cleanup["before"] = before["state"]
                if before["state"]["Running"]:
                    cleanup["kill"] = call(["kill", cid], 3)
                cleanup["wait"] = call(["wait", cid], 3) if before["state"].get("Status") != "created" else {"not_run": "未启动容器不等待退出"}
                cleanup["after"] = inspect_owned(docker, cid, image, nonce)
                cleanup["stopped_observed_ns"] = time.monotonic_ns()
                if attach:
                    cleanup["attach_exit"] = attach.wait(timeout=3)
                    reader.join(timeout=1); stderr_reader.join(timeout=1)
                    cleanup["protocol_thread_closed"] = not reader.is_alive()
                    cleanup["stderr_thread_closed"] = not stderr_reader.is_alive()
                state = cleanup["after"]["state"]
                cleanup["docker_stopped"] = not state["Running"] and not state["Restarting"] and state["Pid"] == 0
                cleanup["physical_tree"] = "namespace_termination_inference_pending_review" if cleanup["docker_stopped"] and cleanup.get("protocol_thread_closed") else "unconfirmed"
                if "runtime_start_ns" in descriptor:
                    cleanup["runtime_upper_seconds_until_stopped"] = (cleanup["stopped_observed_ns"]-descriptor["runtime_start_ns"]) / 1000000000
            except Exception as error:
                cleanup["error"] = str(error)[:2000]
        if reaper_registry is not None:
            if cleanup.get("docker_stopped"):
                reaper_registry["complete"] = True
                atomic_json(run / "reaper-registry.json", reaper_registry)
            if reaper:
                try:
                    cleanup["reaper_exit"] = reaper.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    reaper.kill(); cleanup["reaper_exit"] = reaper.wait(timeout=3)
                    cleanup["reaper_forced_after_owned_cleanup"] = True
        if event_process:
            time.sleep(0.2)
            event_process.terminate()
            cleanup["events_exit"] = event_process.wait(timeout=3)
        for process in [attach, reaper, event_process]:
            if process and process.poll() is None:
                process.kill(); process.wait(timeout=3)
        cleanup["elapsed_seconds"] = (time.monotonic_ns() - cleanup_start) / 1000000000
        atomic_json(run / "cleanup.json", cleanup)
        terminal_data = terminal.get("data") if terminal else None
        descriptor.update({"state": "ERROR" if failure or not isinstance(terminal_data, dict) else terminal_data.get("verdict", "ERROR"), "failure": failure, "terminal": terminal, "end_ns": time.monotonic_ns(), "elapsed_seconds": (time.monotonic_ns() - t0) / 1000000000, "cleanup_seconds": cleanup["elapsed_seconds"], "business_phase_entered": False})
        atomic_json(run / "root-result.json", descriptor)
        # 描述对象已直接附加到attempts，根序号不等于实际预览列表下标。
        session["stage"] = "C04_attempt_stopped_business_frozen"
        session["cleanup_seconds"] += cleanup["elapsed_seconds"]
        if "runtime_start_ns" in descriptor:
            session["new_runtime_seconds"] += cleanup.get("runtime_upper_seconds_until_stopped", (descriptor["runtime_observed_until_ns"] - descriptor["runtime_start_ns"]) / 1000000000)
        atomic_json(session_path, session)
        print(json.dumps({"root": root_record["id"], "state": descriptor["state"], "failure": failure, "terminal": terminal, "cid": cid, "image": image, "docker_stopped": cleanup.get("docker_stopped"), "physical_tree": cleanup["physical_tree"], "business_phase_entered": False}, ensure_ascii=False), flush=True)

        return descriptor, cleanup, observations


def frozen_input(run_index):
    source = AREA / "preparation" / ("frozen-run-" + str(run_index).zfill(2) + ".json")
    frozen = json.loads(source.read_text("utf-8"))
    for name, expected in frozen["project_files"].items():
        path = ROOT / name
        if not path.resolve().is_relative_to(ROOT.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError("本轮冻结源码或配置漂移: " + name)
    context = Path(frozen["context"])
    if not context.resolve().is_relative_to((ROOT / "deploy/preview/task109-c04-context").resolve()):
        raise RuntimeError("本地增量context路径越界")
    for name, expected in frozen["context_files"].items():
        if hashlib.sha256((context / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError("本轮冻结context漂移: " + name)
    return frozen


def build_image(session, record, run, frozen):
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("Docker CLI不可用")
    calls = []
    def call(args, timeout=8):
        remaining = (min(record["deadline_ns"], session["effective_deadline_ns"])-time.monotonic_ns()) / 1000000000
        if remaining <= 0:
            raise RuntimeError("构建根硬截止")
        value = docker_call(docker, args, min(timeout, remaining))
        calls.append(value)
        atomic_json(run / "build-docker-calls.json", calls)
        return value
    context = call(["context", "show"])
    if context["code"] or context["stdout"].strip() != "desktop-linux":
        raise RuntimeError("当前Docker context不是原desktop-linux")
    running = call(["ps", "--filter", "label=retrolume.task=TASK-109", "--format", "{{.ID}}"])
    if running["code"] or running["stdout"].strip():
        raise RuntimeError("已有本卡资源运行，不启动并行预览")
    tags = call(["image", "ls", "--filter", "reference=" + frozen["tag"], "--format", "{{.ID}}"])
    if tags["code"] or tags["stdout"].strip():
        raise RuntimeError("本轮新tag已经占用，不覆盖")
    template = json.loads((ROOT / "DocuN/evidence/TASK-109/execution/continuation-01/root-03/build-command.json").read_text("utf-8-sig"))
    args = list(template["args"])
    args[args.index("--tag") + 1] = frozen["tag"]
    args[args.index("--iidfile") + 1] = str(run / "image-id.txt")
    args[args.index("--metadata-file") + 1] = str(run / "build-metadata.json")
    args = ["retrolume.action-permit=TASK-109-G11-C04-20261009" if value == "retrolume.action-permit=TASK-109-G11-C01-20261009" else value for value in args]
    args[-1] = frozen["context"]
    args[-1:-1] = ["--label", "retrolume.root=" + record["id"]]
    required_context = "task109_cached_base=oci-layout://D:/shspic/project_NO3_RetroLume-agent/deploy/preview/task109-c01-cache/oci@sha256:c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac"
    if args[args.index("--build-context") + 1] != required_context or args[args.index("--builder") + 1] != "desktop-linux" or "--network=none" not in args or "--pull=false" not in args or "--load" not in args:
        raise RuntimeError("原本地OCI成功构建命令漂移")
    remaining = min(300, 600-session["new_build_seconds"], (record["deadline_ns"]-time.monotonic_ns()) / 1000000000-75)
    if remaining <= 0 or len(session["builds"]) >= 2:
        raise RuntimeError("本轮增量构建额度已到，禁止构建")
    atomic_json(run / "build-command.json", {"args": args, "source": "原C01本地OCI命令；仅新tag、输出、context和归属label映射", "timeout_seconds": remaining})
    started = time.monotonic_ns()
    build = {"root": record["id"], "tag": frozen["tag"], "counted_before_execution_ns": started, "state": "started"}
    session["builds"].append(build)
    atomic_json(AREA / "session.json", session)
    stdout = b""
    stderr = b""
    code = None
    error = None
    try:
        result = subprocess.run([docker] + args, capture_output=True, timeout=remaining, env=clean_env(), creationflags=subprocess.CREATE_NO_WINDOW)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as failure:
        stdout, stderr = failure.stdout or b"", failure.stderr or b""
        error = "本地增量构建触及固定截止，不重复同根构建"
    finally:
        elapsed = (time.monotonic_ns()-started) / 1000000000
        (run / "build-stdout.log").write_bytes(stdout[:1048576])
        (run / "build-stderr.log").write_bytes(stderr[:1048576])
        build.update({"code": code, "error": error, "elapsed_seconds": elapsed, "stdout_bytes": len(stdout), "stderr_bytes": len(stderr), "stdout_truncated": len(stdout) > 1048576, "stderr_truncated": len(stderr) > 1048576, "state": "BUILT" if code == 0 and not error else "ERROR"})
        session["new_build_seconds"] += elapsed
        atomic_json(run / "build-result.json", build)
        atomic_json(AREA / "session.json", session)
    if code != 0 or error:
        raise RuntimeError(error or "本地增量build/load失败，见完整有界构建日志")
    metadata = json.loads((run / "build-metadata.json").read_text("utf-8"))
    image = metadata["containerimage.digest"]
    iid = (run / "image-id.txt").read_text("utf-8").strip()
    if iid != image or image == "sha256:aa824fa25eb0aae09cee50c10372fb218a7d86ffb10124b46074a5c1e977cc66" or metadata["containerimage.descriptor"]["digest"] != image:
        raise RuntimeError("新构建manifest绑定不符，不能冒旧镜像")
    inspected = call(["image", "inspect", "--format", '{"id":{{json .Id}},"descriptor":{{json .Descriptor}},"user":{{json .Config.User}},"entrypoint":{{json .Config.Entrypoint}},"os":{{json .Os}},"architecture":{{json .Architecture}},"labels":{{json .Config.Labels}}}', frozen["tag"]])
    if inspected["code"]:
        raise RuntimeError("新镜像load后不能核证，不启动")
    actual = json.loads(inspected["stdout"])
    config = actual["descriptor"].get("annotations", {}).get("config.digest")
    if not isinstance(config, str) or not config.startswith("sha256:") or len(config) != 71 or config not in stderr.decode("utf-8", "replace"):
        raise RuntimeError("实际image descriptor与构建原始config记录不能绑定")
    if actual["id"] != image or actual["descriptor"]["digest"] != image or actual["descriptor"].get("annotations", {}).get("config.digest") != config or actual["user"] != "10001:10001" or actual["entrypoint"] != ["node", "/opt/preview/h0-counter.cjs"] or actual["labels"].get("retrolume.action-permit") != session["action_permit"] or actual["labels"].get("retrolume.root") != record["id"]:
        raise RuntimeError("新镜像manifest/config或实际tag归属不符")
    atomic_json(run / "loaded-image.json", {**actual, "config": config, "tag": frozen["tag"], "input_manifest_sha256": frozen["input_manifest_sha256"], "same_browser_binary_expected": "0b20b130e7edd9dd51873be867761295fe0cfad490c2b9a64f95bd3cfc08fa71"})
    return image, config


def main():
    global IMAGE, CONFIG
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-index", type=int, choices=[1, 2], required=True)
    args = parser.parse_args()
    session_path = AREA / "session.json"
    session = json.loads(session_path.read_text("utf-8"))
    if session.get("action_permit") != "TASK-109-G11-C04-20261009" or len(session["roots"]) != args.run_index - 1:
        raise RuntimeError("C04许可、真实根计数或执行序号不符，不重置")
    if args.run_index == 2:
        previous = AREA / "root-06/preview/cleanup.json"
        correction = json.loads((AREA / "correction-02.json").read_text("utf-8"))
        stopped = json.loads(previous.read_text("utf-8")).get("docker_stopped") if previous.is_file() else json.loads((AREA / "root-06/no-runtime-proof.json").read_text("utf-8")).get("no_preview_create_or_start")
        if session["roots"][0]["state"] != "ERROR" or not stopped or not correction.get("ordinary_diagnostic_only") or not correction.get("original_error_evidence") or not correction.get("source_diff"):
            raise RuntimeError("第二根没有明确普通修正依据或首CID停止确认")
        prior_frozen = json.loads((AREA / "root-06/frozen-input.json").read_text("utf-8"))
        next_frozen = json.loads((AREA / "preparation/frozen-run-02.json").read_text("utf-8"))
        if prior_frozen["project_files"] == next_frozen["project_files"] or prior_frozen["input_manifest_sha256"] == next_frozen["input_manifest_sha256"]:
            raise RuntimeError("第二根缺少实际新源码或context身份差异")
    now = time.monotonic_ns()
    record = {"id": "H0-R" + str(args.run_index + 5).zfill(2), "global_ordinal": 75 + args.run_index, "task_ordinal": 5 + args.run_index, "start_ns": now, "deadline_ns": min(now + 900000000000, session["effective_deadline_ns"]), "state": "started", "pid": os.getpid(), "birth": process_birth(os.getpid()), "prechecks_counted": True}
    session["roots"].append(record)
    session["status"] = "C04_real_root"
    atomic_json(session_path, session)
    run = AREA / ("root-" + str(args.run_index + 5).zfill(2))
    failure = None
    try:
        if now >= session["effective_deadline_ns"] - 380000000000 or session["new_real_seconds"] >= 1800 or session["new_runtime_seconds"] >= 120 or len(session["controllers"]) >= 2:
            raise RuntimeError("新有效时窗、收尾预留或独立子限不足，禁止启动")
        run.mkdir(parents=True, exist_ok=False)
        frozen = frozen_input(args.run_index)
        atomic_json(run / "frozen-input.json", frozen)
        (run / "controller-as-run.py").write_bytes(Path(__file__).read_bytes())
        IMAGE, CONFIG = build_image(session, record, run, frozen)
        descriptor, cleanup, observations = run_attempt(session, record, record["deadline_ns"], args.run_index)
        record.update({"state": descriptor["state"], "preview_result": str(run / "preview/root-result.json"), "image": IMAGE, "config": CONFIG, "docker_stopped": cleanup.get("docker_stopped"), "physical_tree": cleanup["physical_tree"], "observations": len(observations)})
    except Exception as error:
        failure = str(error)[:6000]
        record.update({"state": "ERROR", "failure": failure, "business_phase_entered": False})
    finally:
        record.update({"end_ns": time.monotonic_ns(), "elapsed_seconds": (time.monotonic_ns()-now) / 1000000000, "business_frozen": True})
        session["new_real_seconds"] += record["elapsed_seconds"]
        session["global_roots"] = 75 + len(session["roots"])
        session["task_roots"] = 5 + len(session["roots"])
        session["H0_roots"] = 5 + len(session["roots"])
        session["cumulative_imagebuilds"] = 2 + len(session["builds"])
        session["cumulative_controllers"] = 2 + len(session["controllers"])
        session["cumulative_preview_creates"] = 2 + len(session["preview_creates"])
        session["cumulative_preview_starts"] = 2 + len(session["preview_starts"])
        session["status"] = "C04_root_stopped_business_frozen"
        if run.is_dir():
            atomic_json(run / "root-result.json", record)
        atomic_json(session_path, session)
        print(json.dumps(record, ensure_ascii=False), flush=True)
    return 0 if not failure else 1


if __name__ == "__main__":
    raise SystemExit(main())
