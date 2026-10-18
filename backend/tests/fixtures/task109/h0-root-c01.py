"""C01唯一H0-R03：本地OCI导出/构建、真实最小诊断和精确收尾。"""
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

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "backend/app/preview"))
sys.path.insert(0, str(ROOT / "deploy/preview"))
from oci_local import normalize_archive
from contracts import read_observation
from supervisor import PERMIT, atomic_json, clean_env, docker_call, inspect_owned, process_birth

AREA = ROOT / "DocuN/evidence/TASK-109/execution/continuation-01"
BASE = "sha256:c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac"


def main():
    session_path = AREA / "session.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    if len(session["roots"]) >= 1:
        raise RuntimeError("本C01只一次根，不重置原R01/R02")
    root_index = len(session["roots"])
    t0 = time.monotonic_ns()
    root_deadline = min(t0 + 1200000000000, session["deadline_ns"])
    run = AREA / "root-03"
    run.mkdir(exist_ok=False)
    descriptor = {"id": "H0-R03", "start_ns": t0, "deadline_ns": root_deadline, "state": "started", "pid": os.getpid(), "birth": process_birth(os.getpid()), "prechecks_counted": True, "old_global_roots": 72, "global_ordinal": 73, "action_permit": "TASK-109-G11-C01-20261009"}
    session["roots"].append(descriptor)
    session["image_builds"] = []
    session["preview_creates"] = []
    session["preview_starts"] = []
    session["controllers"] = []
    session["stage"] = "H0_real_root"
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
    terminal = None
    failure = None
    name = "retrolume-task-109-g11-preview-01"
    cleanup_deadline = None
    def call(args, timeout=8):
        if time.monotonic_ns() >= min(cleanup_deadline or root_deadline, session["original_deadline_ns"]):
            raise RuntimeError("真实根硬截止")
        result = docker_call(docker, args, timeout)
        calls.append(result)
        atomic_json(run / "docker-calls.json", calls)
        return result
    def read_output():
        sequence = 1
        chunks = {}
        packets = []
        try:
            while True:
                row = read_observation(attach.stdout, sequence)
                if row is None:
                    return
                sequence += 1
                packets.append(row)
                atomic_json(run / "protocol-packets.json", packets)
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
                if row["kind"] == "terminal":
                    messages.put(row)
        except Exception as error:
            messages.put({"kind": "parser_error", "data": str(error)[:2000]})
    def capture(stream, target, limit):
        with target.open("wb") as output:
            remaining = limit
            while True:
                chunk = stream.read(1024)
                if not chunk:
                    return
                if remaining:
                    piece = chunk[:remaining]
                    output.write(piece)
                    output.flush()
                    remaining -= len(piece)
    try:
        names = call(["ps", "-a", "--filter", "name=^retrolume-task-109-g11-preview-01$", "--format", "{{.Names}}"], 8)
        if names["code"] or name in names["stdout"].splitlines():
            raise RuntimeError("本卡专用容器名冲突")
        base = call(["image", "inspect", "--format", '{"id":{{json .Id}},"descriptor":{{json .Descriptor}},"rootfs":{{json .RootFS}},"os":{{json .Os}},"architecture":{{json .Architecture}}}', BASE], 8)
        if base["code"]:
            raise RuntimeError("精确基础镜像读取失败")
        base_metadata = json.loads(base["stdout"])
        if base_metadata["id"] != BASE:
            raise RuntimeError("精确基础镜像身份不符")
        atomic_json(run / "base-metadata.json", base_metadata)
        cache = ROOT / "deploy/preview/task109-c01-cache"
        cache.mkdir(exist_ok=False)
        archive = cache / "base-image.tar"
        session["image_save"] = 1
        atomic_json(session_path, session)
        exported = call(["image", "save", "--output", str(archive), BASE], min(300, (root_deadline - time.monotonic_ns()) / 1000000000))
        if exported["code"]:
            raise RuntimeError("本地image save失败，不pull或再导出")
        oci = normalize_archive(archive, cache / "oci", base_metadata, root_deadline)
        atomic_json(run / "OCI-identity.json", oci)
        context = ROOT / "deploy/preview/task109-h0-context"
        for rel, expected_hash in json.loads((context / "input-manifest.json").read_text(encoding="utf-8"))["source_files"].items():
            if hashlib.sha256((context / rel).read_bytes()).hexdigest() != expected_hash:
                raise RuntimeError("COPY白名单字节漂移")
        session["imagebuild"] = 1
        session["image_builds"].append({"index": 2, "before_ns": time.monotonic_ns(), "deadline_ns": min(time.monotonic_ns() + 600000000000, root_deadline)})
        atomic_json(session_path, session)
        image_file = run / "image-id.txt"
        build_args = ["buildx", "build", "--builder", "desktop-linux", "--build-context", "task109_cached_base=" + oci["uri"], "--network=none", "--pull=false", "--provenance=false", "--sbom=false", "--load", "--tag", "retrolume-task-109-g11-h0:c01", "--iidfile", str(image_file), "--metadata-file", str(run / "build-metadata.json"), "--progress=plain", "--label", "retrolume.task=TASK-109", "--label", "retrolume.permit=" + PERMIT, "--label", "retrolume.action-permit=TASK-109-G11-C01-20261009", str(context)]
        atomic_json(run / "build-command.json", {"args": build_args, "source":"本地OCI，不允许其他基础来源"})
        build_start = time.monotonic_ns()
        with (run / "build-stdout.log").open("wb") as out, (run / "build-stderr.log").open("wb") as err:
            build = subprocess.run([docker] + build_args, stdout=out, stderr=err, timeout=min(600, (root_deadline - time.monotonic_ns()) / 1000000000), env=clean_env(), creationflags=subprocess.CREATE_NO_WINDOW)
        descriptor["build_elapsed_seconds"] = (time.monotonic_ns() - build_start) / 1000000000
        descriptor["build_exit"] = build.returncode
        if build.returncode or not image_file.is_file():
            raise RuntimeError("派生镜像构建失败")
        iid = image_file.read_text(encoding="utf-8").strip()
        loaded = call(["image", "inspect", "--format", '{"id":{{json .Id}},"descriptor":{{json .Descriptor}},"user":{{json .Config.User}},"entrypoint":{{json .Config.Entrypoint}},"os":{{json .Os}},"architecture":{{json .Architecture}}}', "retrolume-task-109-g11-h0:c01"], 8)
        if loaded["code"]:
            raise RuntimeError("构建完成但image未load，不创建容器")
        metadata = json.loads(loaded["stdout"])
        image = metadata["id"]
        if not image.startswith("sha256:") or len(image) != 71 or metadata["user"] != "10001:10001" or metadata["entrypoint"] != ["node", "/opt/preview/h0-counter.cjs"]:
            raise RuntimeError("实际派生image身份或配置不符")
        atomic_json(run / "loaded-image.json", {"iidfile": iid, "loaded": metadata, "not_assumed_equal": True})
        build_log = (run / "build-stderr.log").read_text(encoding="utf-8", errors="replace")
        if any(word in build_log for word in ["auth.docker.io", "https://mcr.microsoft.com", "docker.io/library/task109_cached_base", "docker-image://"]):
            raise RuntimeError("本地OCI构建仍出现任务registry解析，停止")
        registry = run / "reaper-registry.json"
        reaper_registry = {"parent_pid": os.getpid(), "parent_birth": process_birth(os.getpid()), "docker": docker, "nonce": nonce, "controller_deadline_ns": min(time.monotonic_ns() + 1200000000000, root_deadline), "cid": None, "complete": False}
        atomic_json(registry, reaper_registry)
        session["controllers"].append({"start_ns": time.monotonic_ns(), "deadline_ns": reaper_registry["controller_deadline_ns"], "registry": str(registry)})
        atomic_json(session_path, session)
        reaper = subprocess.Popen([sys.executable, "-B", "-u", str(ROOT / "backend/app/preview/reaper.py"), str(registry)], stdout=subprocess.DEVNULL, stderr=(run / "reaper-stderr.log").open("wb"), env=clean_env(), creationflags=subprocess.CREATE_NO_WINDOW)
        process_rows = {"controller": {"pid": os.getpid(), "birth": process_birth(os.getpid())}, "reaper": {"pid": reaper.pid, "birth": process_birth(reaper.pid)}, "attach": None, "events": None}
        atomic_json(run / "owned-processes.json", process_rows)
        ready_deadline = time.monotonic_ns() + 3000000000
        while not (run / "reaper-ready.json").is_file():
            if reaper.poll() is not None or time.monotonic_ns() >= ready_deadline:
                raise RuntimeError("独立救援器未就绪")
            time.sleep(0.05)
        runtime_start = time.monotonic_ns()
        runtime_deadline = min(runtime_start + 60000000000, root_deadline)
        create_args = ["create", "--name", name, "--label", "retrolume.task=TASK-109", "--label", "retrolume.permit=" + PERMIT, "--label", "retrolume.synthetic=true", "--label", "retrolume.phase=H0-C01", "--label", "retrolume.action-permit=TASK-109-G11-C01-20261009", "--label", "retrolume.nonce=" + nonce, "--network=none", "--user=10001:10001", "--cap-drop=ALL", "--security-opt", "no-new-privileges", "--security-opt", "seccomp=" + str(ROOT / "deploy/preview/seccomp.json"), "--read-only", "--restart=no", "--init", "--cpus=1", "--memory=768m", "--memory-swap=768m", "--pids-limit=128", "--ipc=private", "--shm-size=64m", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=128m", "--tmpfs", "/home/preview:rw,nosuid,nodev,noexec,size=32m", image]
        session["preview_create"] = 1
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
        reaper_registry.update({"cid": cid, "image": image, "runtime_deadline_ns": runtime_deadline})
        atomic_json(registry, reaper_registry)
        bound_deadline = min(time.monotonic_ns() + 3000000000, runtime_deadline)
        while not (run / "reaper-bound.json").is_file():
            if reaper.poll() is not None or time.monotonic_ns() >= bound_deadline:
                raise RuntimeError("CID未被独立救援器接管，不start")
            time.sleep(0.05)
        events_file = (run / "docker-events.log").open("wb")
        event_process = subprocess.Popen([docker, "events", "--filter", "container=" + cid, "--format", "{{json .}}"], stdout=events_file, stderr=subprocess.DEVNULL, env=clean_env(), creationflags=subprocess.CREATE_NO_WINDOW)
        session["preview_start"] = 1
        session["preview_starts"].append({"before_ns": time.monotonic_ns(), "cid": cid, "deadline_ns": runtime_deadline})
        atomic_json(session_path, session)
        attach = subprocess.Popen([docker, "start", "-a", "-i", cid], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=clean_env(), creationflags=subprocess.CREATE_NO_WINDOW)
        process_rows["attach"] = {"pid": attach.pid, "birth": process_birth(attach.pid)}
        process_rows["events"] = {"pid": event_process.pid, "birth": process_birth(event_process.pid)}
        atomic_json(run / "owned-processes.json", process_rows)
        messages = queue.Queue()
        reader = threading.Thread(target=read_output, daemon=True); reader.start()
        stderr_reader = threading.Thread(target=capture, args=(attach.stderr, run / "container-stderr.log", 65536), daemon=True); stderr_reader.start()
        while time.monotonic_ns() < runtime_deadline - 5000000000:
            try:
                terminal = messages.get(timeout=0.2)
                break
            except queue.Empty:
                if attach.poll() is not None:
                    failure = "真实容器已退出但未交付完整观测"
                    break
        if terminal is None and failure is None:
            failure = "固定预览截止前没有完整观测"
        descriptor["runtime_start_ns"] = runtime_start
        descriptor["runtime_observed_until_ns"] = time.monotonic_ns()
    except Exception as error:
        failure = str(error)[:2000]
    finally:
        cleanup_start = time.monotonic_ns()
        cleanup_deadline = min(cleanup_start + 300000000000, session["original_deadline_ns"])
        cleanup = {"cid": cid, "image": image, "nonce": nonce, "physical_tree": "unconfirmed"}
        if cid and image:
            try:
                before = inspect_owned(docker, cid, image, nonce)
                cleanup["before"] = before["state"]
                if before["state"]["Running"]:
                    cleanup["kill"] = call(["kill", cid], 3)
                cleanup["wait"] = call(["wait", cid], 3)
                cleanup["after"] = inspect_owned(docker, cid, image, nonce)
                if attach:
                    cleanup["attach_exit"] = attach.wait(timeout=3)
                    reader.join(timeout=1); stderr_reader.join(timeout=1)
                    cleanup["protocol_thread_closed"] = not reader.is_alive()
                    cleanup["stderr_thread_closed"] = not stderr_reader.is_alive()
                state = cleanup["after"]["state"]
                cleanup["docker_stopped"] = not state["Running"] and not state["Restarting"] and state["Pid"] == 0
                cleanup["physical_tree"] = "namespace_termination_inference_pending_review" if cleanup["docker_stopped"] and cleanup.get("protocol_thread_closed") else "unconfirmed"
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
        descriptor.update({"state": "ERROR" if failure or terminal is None else terminal.get("data", {}).get("verdict", "ERROR"), "failure": failure, "terminal": terminal, "end_ns": time.monotonic_ns(), "elapsed_seconds": (time.monotonic_ns() - t0) / 1000000000, "cleanup_seconds": cleanup["elapsed_seconds"], "business_phase_entered": False})
        atomic_json(run / "root-result.json", descriptor)
        session["roots"][root_index] = descriptor
        session["stage"] = "H0_stopped_before_business"
        session["cleanup_seconds"] = cleanup["elapsed_seconds"]
        if "runtime_start_ns" in descriptor:
            session["runtime_seconds"] = (descriptor["runtime_observed_until_ns"] - descriptor["runtime_start_ns"]) / 1000000000
        atomic_json(session_path, session)
        print(json.dumps({"root": descriptor["id"], "state": descriptor["state"], "failure": failure, "terminal": terminal, "cid": cid, "image": image, "docker_stopped": cleanup.get("docker_stopped"), "physical_tree": cleanup["physical_tree"], "business_phase_entered": False}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
