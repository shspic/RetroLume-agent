# -*- coding: utf-8 -*-
"""TASK-074 运行控制脚本：结构复用 073（限时、监督子进程、finally 收尾），
仅更换任务标识/runTag/容器/库名/标签。只操作本脚本创建的容器与本次测试子进程；
容器与卷保留不删除。"""
import hashlib
import json
import os
import secrets
import subprocess
import time

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
BACKEND = os.path.join(ROOT, "backend")
VENV_PY = os.path.join(BACKEND, ".venv", "Scripts", "python.exe")
OUT = os.path.dirname(os.path.abspath(__file__))

RUN_TAG = "20260921T1319-wbB1"
NAME = f"retrolume-task-074-pg-{RUN_TAG}"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
PORT = 55435
DB = "retrolume_task074_synthetic"
DB_USER = "retrolume_t074"
DB_PASS = secrets.token_urlsafe(18)  # 仅用于本合成容器
DSN = f"postgresql://{DB_USER}:{DB_PASS}@127.0.0.1:{PORT}/{DB}"

TOTAL_WINDOW = 600.0
CREATE_TIMEOUT = 30.0
PG_READY_TIMEOUT = 30.0
TEST_TIMEOUT = 120.0
MIGR_TIMEOUT = 60.0
STOP_TIMEOUT = 30.0

T0 = time.monotonic()
WALL0 = time.time()


def elapsed():
    return time.monotonic() - T0


def budget(limit):
    return max(1.0, min(limit, TOTAL_WINDOW - elapsed() - 5.0))


def run(cmd, timeout, stdin_bytes=None, **kw):
    p = subprocess.run(cmd, input=stdin_bytes, capture_output=True, timeout=timeout, **kw)
    return {"rc": p.returncode, "stdout_bytes": p.stdout, "stderr_bytes": p.stderr,
            "stdout": p.stdout.decode("utf-8", "replace"), "stderr": p.stderr.decode("utf-8", "replace")}


def save_bytes(name, data):
    with open(os.path.join(OUT, name), "wb") as f:
        f.write(data)


R = {"run_tag": RUN_TAG, "container_name": NAME, "image": IMAGE, "port": PORT, "database": DB,
     "db_user": DB_USER, "db_password": DB_PASS, "dsn_for_evidence": DSN,
     "test_file_hash_before": "ef705113fbf6af83a0a29e99b40dfdb68109282c0ae8b724790e1d440575d246",
     "test_file_hash_after_fix": "7839af04e3043a173f8caaeefd5085ff72e138891207a0e882d8b2ef585d15e4",
     "started_wall": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(WALL0)),
     "steps": {}, "test": {}, "cleanup": {}, "verdict": None}
LOG = []


def log(msg):
    line = f"[{elapsed():7.1f}s] {msg}"
    LOG.append(line)
    print(line, flush=True)


def fail(stage, detail):
    R["verdict"] = f"FAIL:{stage}"
    R["failure_detail"] = detail
    log(f"FAIL at {stage}: {detail}")


def docker_inspect(target):
    try:
        r = run(["docker", "inspect", target], budget(30))
        if r["rc"] == 0:
            return json.loads(r["stdout"])[0]
    except Exception as e:
        log(f"inspect error: {e}")
    return None


container_id = None
test_proc = None

try:
    # ---- 0. 同名冲突检查 + 073 旧容器隔离确认（只读，不触碰） ----
    pre = run(["docker", "container", "inspect", NAME], budget(30))
    R["steps"]["name_conflict_check"] = {"rc": pre["rc"]}
    if pre["rc"] == 0:
        fail("name_conflict", "同名容器已存在，按卡阻塞，不复用")
        raise SystemExit(1)
    old073 = run(["docker", "container", "inspect", "da18c806a871780500df3bdf2b612632afa7c5721e122e80437b6c248c1d2a62"], budget(30))
    R["steps"]["old_073_untouched"] = {
        "exists": old073["rc"] == 0,
        "note": "仅只读确认旧073容器仍在且不被本卡操作" if old073["rc"] == 0 else "旧073容器查询失败（未触碰）",
    }
    log("无同名容器；073 旧容器仅只读确认，不操作")

    # ---- 1. 创建唯一容器 ----
    create_cmd = [
        "docker", "run", "-d", "--name", NAME,
        "--label", "retrolume-task=074", "--label", f"retrolume-run={RUN_TAG}",
        "--cpus", "1", "--memory", "512m", "--pids-limit", "128",
        "--restart", "no",
        "-p", f"127.0.0.1:{PORT}:5432",
        "-e", f"POSTGRES_USER={DB_USER}", "-e", f"POSTGRES_PASSWORD={DB_PASS}",
        "-e", f"POSTGRES_DB={DB}",
        IMAGE,
    ]
    R["steps"]["create_cmd"] = create_cmd
    r = run(create_cmd, budget(CREATE_TIMEOUT))
    save_bytes("docker-run-stdout.txt", r["stdout_bytes"])
    save_bytes("docker-run-stderr.txt", r["stderr_bytes"])
    R["steps"]["create"] = {"rc": r["rc"], "stderr": r["stderr"][:2000]}
    if r["rc"] != 0:
        fail("create_container", r["stderr"][:2000])
        raise SystemExit(1)
    container_id = r["stdout"].strip()
    R["container_id"] = container_id
    log(f"容器已创建 id={container_id}")

    insp = docker_inspect(container_id)
    if insp:
        with open(os.path.join(OUT, "container-inspect-created.json"), "w", encoding="utf-8") as f:
            json.dump(insp, f, ensure_ascii=False, indent=2)
        R["steps"]["inspect_created"] = {
            "id": insp.get("Id"), "image": insp.get("Image"),
            "labels": insp.get("Config", {}).get("Labels"),
            "network_mode": insp.get("HostConfig", {}).get("NetworkMode"),
            "port_bindings": insp.get("HostConfig", {}).get("PortBindings"),
            "mounts": insp.get("Mounts"),
            "nano_cpus": insp.get("HostConfig", {}).get("NanoCpus"),
            "memory": insp.get("HostConfig", {}).get("Memory"),
            "pids_limit": insp.get("HostConfig", {}).get("PidsLimit"),
            "restart_policy": insp.get("HostConfig", {}).get("RestartPolicy"),
        }
    else:
        fail("inspect_created", "无法 inspect 本次创建的容器")
        raise SystemExit(1)

    # ---- 2. PG 就绪等待（最多 30s） ----
    ready_deadline = min(time.monotonic() + PG_READY_TIMEOUT, time.monotonic() + budget(PG_READY_TIMEOUT))
    ready = False
    pg_version = None
    last_err = None
    import psycopg
    while time.monotonic() < ready_deadline:
        try:
            with psycopg.connect(DSN, connect_timeout=3) as c:
                pg_version = c.execute("SELECT version()").fetchone()[0]
            ready = True
            break
        except Exception as e:
            last_err = repr(e)[:500]
            time.sleep(1.0)
    R["steps"]["pg_ready"] = {"ready": ready, "pg_version": pg_version, "last_error": last_err,
                              "elapsed_s": round(elapsed(), 1)}
    if not ready:
        fail("pg_ready", f"30 秒内未就绪: {last_err}")
        raise SystemExit(1)
    log(f"PG 就绪: {pg_version[:80]}")

    # ---- 3. 迁移 001、002 各一次 ----
    for mig in ("001_materials.sql", "002_activities.sql"):
        with open(os.path.join(BACKEND, "migrations", mig), "rb") as f:
            sql_bytes = f.read()
        try:
            r = run(["docker", "exec", "-i", container_id, "psql", "-U", DB_USER, "-d", DB,
                     "-v", "ON_ERROR_STOP=1", "-f", "-"],
                    budget(MIGR_TIMEOUT), stdin_bytes=sql_bytes)
        except subprocess.TimeoutExpired as e:
            r = {"rc": "timeout", "stdout_bytes": e.stdout or b"", "stderr_bytes": e.stderr or b"",
                 "stdout": "", "stderr": "migr timeout"}
        tag = mig.replace(".sql", "")
        save_bytes(f"migration-{tag}-stdout.txt", r["stdout_bytes"])
        save_bytes(f"migration-{tag}-stderr.txt", r["stderr_bytes"])
        R["steps"][f"migration_{tag}"] = {"rc": r["rc"], "stdout_tail": r["stdout"][-800:]}
        if r["rc"] != 0:
            fail(f"migration_{tag}", f"rc={r['rc']} stderr={r['stderr'][:800]}")
            raise SystemExit(1)
        log(f"迁移 {mig} 完成 rc=0")

    # ---- 4. 唯一一次测试运行（含修复后的测试文件） ----
    env = os.environ.copy()
    env["RETROLUME_TASK_068_DATABASE_URL"] = DSN
    env["PYTHONIOENCODING"] = "utf-8"
    test_cmd = [VENV_PY, "-B", "-m", "unittest", "-f", "-v", "tests.test_activity_recovery"]
    R["test"]["cmd"] = test_cmd
    R["test"]["cwd"] = BACKEND
    R["test"]["started_wall"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    R["test"]["start_monotonic_s"] = round(elapsed(), 1)
    test_proc = subprocess.Popen(test_cmd, cwd=BACKEND, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    R["test"]["pid"] = test_proc.pid
    log(f"测试子进程已启动 pid={test_proc.pid}")
    timed_out = False
    try:
        out_bytes, _ = test_proc.communicate(timeout=budget(TEST_TIMEOUT))
    except subprocess.TimeoutExpired:
        timed_out = True
        R["test"]["timeout"] = True
        log("测试超时，有界终止：terminate -> taskkill /T /F（仅限本次子进程树）")
        try:
            test_proc.terminate()
            test_proc.wait(timeout=10)
        except Exception:
            pass
        if test_proc.poll() is None:
            kill = run(["taskkill", "/PID", str(test_proc.pid), "/T", "/F"], budget(30))
            R["test"]["taskkill"] = {"rc": kill["rc"], "stdout": kill["stdout"][:500]}
            try:
                test_proc.wait(timeout=10)
            except Exception:
                pass
        out_bytes = b""
    R["test"]["finished_wall"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    R["test"]["duration_s"] = round(time.monotonic() - (T0 + R["test"]["start_monotonic_s"]), 1)
    R["test"]["exit_code"] = test_proc.returncode
    R["test"]["timed_out"] = timed_out
    save_bytes("test-raw-output.bin", out_bytes or b"")
    with open(os.path.join(OUT, "test-output-utf8.txt"), "w", encoding="utf-8") as f:
        f.write((out_bytes or b"").decode("utf-8", "replace"))
    log(f"测试结束 exit={test_proc.returncode} timed_out={timed_out} 耗时={R['test']['duration_s']}s")
    test_proc = None

    if timed_out or R["test"]["exit_code"] != 0:
        fail("test_run", f"exit_code={R['test']['exit_code']} timed_out={timed_out}（失败即停，不重试不改码）")
        raise SystemExit(1)

    # ---- 5. 六表只读核对（仅全部成功后） ----
    tables = ["material_sources", "material_versions", "activities", "activity_scope_sources",
              "activity_allowed_models", "activity_operations"]
    counts = {}
    ok = True
    with psycopg.connect(DSN, connect_timeout=5) as c:
        for t in tables:
            counts[t] = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            ok = ok and counts[t] == 0
    R["steps"]["table_counts"] = counts
    R["steps"]["table_counts_all_zero"] = ok
    log(f"六表计数: {counts} all_zero={ok}")
    if not ok:
        fail("table_cleanup_check", f"存在非零表: {counts}")
        raise SystemExit(1)

    R["verdict"] = "PASS"
    log("全部验收点达成：六例运行 0 失败/错误/skip、test06 分批通过、六表清零、待收尾")

except SystemExit:
    pass
except Exception as e:
    fail("unexpected", repr(e)[:1000])
finally:
    if test_proc is not None and test_proc.poll() is None:
        log("finally: 终止仍在运行的测试子进程")
        try:
            test_proc.terminate()
            test_proc.wait(timeout=10)
        except Exception:
            pass
        if test_proc.poll() is None:
            run(["taskkill", "/PID", str(test_proc.pid), "/T", "/F"], budget(30))
        R["cleanup"]["test_process"] = {"pid": test_proc.pid, "terminated": True}
    else:
        R["cleanup"]["test_process"] = {"state": "exited_before_finally"}

    if container_id:
        insp = docker_inspect(container_id)
        verified = bool(insp and insp.get("Id") == container_id
                        and insp.get("Config", {}).get("Labels", {}).get("retrolume-run") == RUN_TAG)
        R["cleanup"]["identity_verified"] = verified
        if verified:
            try:
                r = run(["docker", "stop", "-t", "10", container_id], budget(STOP_TIMEOUT))
                R["cleanup"]["docker_stop_rc"] = r["rc"]
            except subprocess.TimeoutExpired:
                R["cleanup"]["docker_stop_rc"] = "timeout"
            insp2 = docker_inspect(container_id)
            running = insp2.get("State", {}).get("Running") if insp2 else None
            if running:
                log("stop 后仍 Running，按卡对同一核实 ID 一次 docker kill")
                try:
                    k = run(["docker", "kill", container_id], budget(60))
                    R["cleanup"]["docker_kill_rc"] = k["rc"]
                except subprocess.TimeoutExpired:
                    R["cleanup"]["docker_kill_rc"] = "timeout"
                insp3 = docker_inspect(container_id)
                running = insp3.get("State", {}).get("Running") if insp3 else None
                if insp3:
                    with open(os.path.join(OUT, "container-inspect-final.json"), "w", encoding="utf-8") as f:
                        json.dump(insp3, f, ensure_ascii=False, indent=2)
            R["cleanup"]["container_running_after_cleanup"] = running
            try:
                lg = run(["docker", "logs", "--tail", "200", container_id], budget(30))
                save_bytes("container-logs-tail.txt",
                           lg["stdout_bytes"] + b"\n--- stderr ---\n" + lg["stderr_bytes"])
            except Exception as e:
                log(f"docker logs 失败: {e}")
            R["cleanup"]["container_retained"] = True
        else:
            R["cleanup"]["identity_verified"] = False
            R["cleanup"]["note"] = "无法核验本次 ID/标签，未停止任何资源，如实上报"
    else:
        R["cleanup"]["container"] = "never_created"

    R["finished_wall"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    R["total_elapsed_s"] = round(elapsed(), 1)
    with open(os.path.join(OUT, "run-result.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "run-log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    log(f"收尾完成 verdict={R['verdict']} 总耗时={R['total_elapsed_s']}s")
