# TASK-083 pg-run-08 有限超时 runner（单容器、单unittest进程、finally收尾）
# 口令随机生成，仅注入本次 docker run 与子进程环境；所有写出文本经口令过滤。
# 不改生产/夹具；容器/库/schema/失败数据保留；不 DROP schema/database、不删容器/卷。
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

import psycopg
from psycopg import errors as pg_errors

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
EVID = ROOT / "Ndocu/evidence/task-083/pg-run-08"
VENV_PY = ROOT / "backend/.venv/Scripts/python.exe"
TESTS_DIR = ROOT / "backend/tests"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"

RUN_TAG = "20260925-1515"
CONTAINER = f"retrolume-task-083-pg08-{RUN_TAG}"
DB_NAME = "retrolume_task083_pg08"
DB_USER = "task083_pg08"
DB_PORT = 55437
PW = secrets.token_urlsafe(24)
DSN = f"postgresql://{DB_USER}:{PW}@127.0.0.1:{DB_PORT}/{DB_NAME}"

# 卡面总窗自创建起 <=10分钟(600s)；runner 内取 560s 以保留工具层余量，
# 各阶段预算均截断为 remaining()-65，保证 finally 收尾预算 >=65s。
TOTAL_WINDOW = 560.0
T0 = time.monotonic()

log_lines = []
def log(msg):
    line = f"[{time.monotonic() - T0:7.2f}s] {msg}"
    print(line, flush=True)
    log_lines.append(line)

def remaining():
    return TOTAL_WINDOW - (time.monotonic() - T0)

def scrub(text):
    if text is None:
        return ""
    return text.replace(PW, "***") if PW in text else text

state = {"run_tag": RUN_TAG, "container_name": CONTAINER, "db_name": DB_NAME,
         "db_user": DB_USER, "port": DB_PORT, "image": IMAGE,
         "verdict": None, "unittest": None, "ready": None}
container_id = None
created = False

def run_docker(args, timeout, label):
    if remaining() < 70:
        log(f"SKIP docker {label}: 剩余预算不足 ({remaining():.1f}s)")
        return None
    t = min(timeout, max(5.0, remaining() - 65))
    log(f"CMD docker {label} (budget {t:.1f}s)")
    try:
        r = subprocess.run(["docker"] + args, capture_output=True, text=True, timeout=t)
    except subprocess.TimeoutExpired:
        state.setdefault("docker", {})[label] = {"exit": "TIMEOUT"}
        log(f"  {label} TIMEOUT")
        return None
    except FileNotFoundError as e:
        state.setdefault("docker", {})[label] = {"exit": "CLI_NOT_FOUND", "stderr": str(e)}
        log(f"  {label} docker CLI not found")
        return None
    state.setdefault("docker", {})[label] = {
        "exit": r.returncode, "stdout": scrub(r.stdout), "stderr": scrub(r.stderr)}
    tail = (r.stdout.strip().splitlines() or [""])[-1][:120] if r.stdout.strip() else scrub(r.stderr.strip())[:200]
    log(f"  {label} exit={r.returncode} {tail}")
    return r

INSPECT_TPL = ('{"id":{{json .Id}},"name":{{json .Name}},"labels":{{json .Config.Labels}},'
               '"image":{{json .Image}},"nano_cpus":{{json .HostConfig.NanoCpus}},'
               '"memory":{{json .HostConfig.Memory}},"pids_limit":{{json .HostConfig.PidsLimit}},'
               '"restart_policy":{{json .HostConfig.RestartPolicy.Name}},'
               '"port_bindings":{{json .HostConfig.PortBindings}},"binds":{{json .HostConfig.Binds}},'
               '"mounts":{{json .Mounts}},"network_mode":{{json .HostConfig.NetworkMode}},'
               '"running":{{json .State.Running}},"created":{{json .Created}}}')

try:
    proc = None  # 修正02：finally 引用前先定义，避免异常早期路径 NameError
    log(f"start runTag={RUN_TAG} container={CONTAINER} db={DB_NAME} user={DB_USER} port={DB_PORT}")
    # 1) 创建容器（<=30s）
    run_args = [
        "run", "-d", "--name", CONTAINER,
        "--label", "retrolume-task=083", "--label", "retrolume-phase=pg08",
        "--label", f"retrolume-run={RUN_TAG}",
        "--cpus", "1", "--memory", "512m", "--pids-limit", "128",
        "--restart", "no",
        "-p", f"127.0.0.1:{DB_PORT}:5432",
        "-e", f"POSTGRES_USER={DB_USER}", "-e", f"POSTGRES_PASSWORD={PW}",
        "-e", f"POSTGRES_DB={DB_NAME}",
        IMAGE,
    ]
    r = run_docker(run_args, 30, "run-create")
    if r is None or r.returncode != 0:
        state["verdict"] = "BLOCKED_CONTAINER_CREATE_FAILED"
        log("容器创建失败（不重试、不换端口），终止")
        raise SystemExit(0)
    container_id = r.stdout.strip()
    created = True
    state["container_id"] = container_id
    log(f"容器已创建 id={container_id[:12]}")

    # 2) 创建后脱敏 inspect + 标签核对（<=15s）
    r = run_docker(["inspect", "--format", INSPECT_TPL, container_id], 15, "inspect-created")
    if r is not None and r.returncode == 0:
        (EVID / "container-inspect-created.json").write_text(scrub(r.stdout), encoding="utf-8")
        try:
            info = json.loads(r.stdout)
            labels = info.get("labels") or {}
            ok = (labels.get("retrolume-task") == "083"
                  and labels.get("retrolume-phase") == "pg08"
                  and labels.get("retrolume-run") == RUN_TAG)
            log(f"标签核对 {'OK' if ok else 'MISMATCH ' + json.dumps(labels)}")
            pb = (info.get("port_bindings") or {}).get("5432/tcp") or []
            pb_ok = any(str(b.get("HostPort")) == "55437" and b.get("HostIp") == "127.0.0.1" for b in pb)
            log(f"宿主端口绑定核对 {'OK (127.0.0.1:55437->5432)' if pb_ok else 'MISMATCH ' + json.dumps(pb)}")
            if not ok or not pb_ok:
                state["verdict"] = "BLOCKED_LABEL_MISMATCH"
                raise SystemExit(0)
            state["created_inspect"] = info
        except json.JSONDecodeError:
            log("inspect 输出非 JSON（不阻断，继续就绪检查）")

    # 3) 就绪等待（自创建起 <=30s）+ 连接身份核对（current_database/current_user/server_port）
    #    修正01：current_user 是 PG 裸关键字，不能写 current_user()（20260925-1455 批就绪
    #    超时根因即此 SQL 语法缺陷——连接与认证实际一直成功）。
    pg_version = None
    mismatch = None
    fatal_sql_error = None
    ready_deadline = time.monotonic() + max(0.0, min(30.0, remaining() - 200))
    while time.monotonic() < ready_deadline:
        try:
            with psycopg.connect(DSN, connect_timeout=3) as c:
                # 修正03（批次三）：inet_server_port() 返回 PG 在容器内监听的端口（5432），
                # 非宿主映射端口；宿主 55437 归属已由上方 port_bindings 核对证实。
                row = c.execute("SELECT current_database(), current_user, inet_server_port()").fetchone()
                if tuple(row) != (DB_NAME, DB_USER, 5432):
                    mismatch = (f"identity mismatch db={row[0]} user={row[1]} port={row[2]}"
                                f" (expect {DB_NAME}/{DB_USER}/container-internal 5432)")
                    break
                pg_version = c.execute("SELECT version()").fetchone()[0]
                break
        except pg_errors.SyntaxError as e:
            fatal_sql_error = f"SYNTAX_ERROR_IN_CHECK_SQL: {scrub(str(e))[:200]}"
            break  # 检查脚本自身缺陷，重试无意义
        except pg_errors.ProgrammingError as e:
            fatal_sql_error = f"PROGRAMMING_ERROR_IN_CHECK_SQL: {scrub(str(e))[:200]}"
            break
        except Exception as e:
            mismatch = None
            state["ready_last_error"] = f"{type(e).__name__}: {scrub(str(e))[:160]}"
            time.sleep(1.0)
    if fatal_sql_error:
        state["ready"] = {"ok": False, "mismatch": None, "pg_version": None,
                          "fatal_sql_error": fatal_sql_error}
        state["verdict"] = "BLOCKED_CHECK_SQL_DEFECT"
        log(f"就绪检查 SQL 自身缺陷: {fatal_sql_error}")
        raise SystemExit(0)
    if pg_version is None:
        state["ready"] = {"ok": False, "mismatch": mismatch, "pg_version": None}
        state["verdict"] = "BLOCKED_IDENTITY_MISMATCH" if mismatch else "BLOCKED_READY_TIMEOUT"
        log(f"就绪/身份失败: {mismatch or 'timeout(30s)'}")
        raise SystemExit(0)
    state["ready"] = {"ok": True, "pg_version": pg_version}
    log(f"PG 就绪且身份核对一致: {pg_version[:90]}")

    # 4) unittest（单进程 failfast 六方法，硬超时120s；unittest 前预算检查保 finally>=60s+15s缓冲）
    if remaining() < 120 + 60 + 15:
        state["verdict"] = "BLOCKED_BUDGET_EXHAUSTED_BEFORE_TESTS"
        log("unittest 前剩余预算不足，停批")
        raise SystemExit(0)

    test_ids = [
        "fixtures.task083.pg_migration.PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column",
        "fixtures.task083.pg_migration.PGMigrationTests.test_pg_migration_02_nonempty_table_rolls_back_whole_005",
        "fixtures.task083.pg_close.PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window",
        "fixtures.task083.pg_close.PGCloseTests.test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes",
        "fixtures.task083.pg_close.PGCloseTests.test_pg03_close_commits_before_concurrent_admit_and_mark",
        "fixtures.task083.pg_close.PGCloseTests.test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges",
    ]
    cmd = [str(VENV_PY), "-B", "-m", "unittest", "-v", "-f"] + test_ids
    env = {
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "COMSPEC": os.environ.get("COMSPEC", r"C:\Windows\system32\cmd.exe"),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
        "RETROLUME_TASK_083_DATABASE_URL": DSN,
    }
    log("启动 unittest（单进程 failfast，6方法，cwd=backend/tests，硬超时120s）")
    u_t0 = time.monotonic()
    killed = False
    try:
        proc = subprocess.Popen(cmd, cwd=str(TESTS_DIR), env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        state["unittest"] = {"spawn_error": f"{type(e).__name__}: {scrub(str(e))[:200]}"}
        state["verdict"] = "BLOCKED_UNITTEST_SPAWN_FAILED"
        raise SystemExit(0)
    try:
        out_b, err_b = proc.communicate(timeout=min(120.0, remaining() - 70))
        u_exit = proc.returncode
    except subprocess.TimeoutExpired:
        killed = True
        log("unittest 超时 → 按精确PID树杀（taskkill /T /F，仅本次进程后代）")
        try:
            tk = subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                capture_output=True, text=True, timeout=15)
            state["unittest_kill"] = {"exit": tk.returncode,
                                      "stdout": scrub(tk.stdout), "stderr": scrub(tk.stderr)}
        except Exception as e:
            state["unittest_kill"] = {"error": f"{type(e).__name__}: {e}"}
        try:
            out_b, err_b = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            out_b, err_b = b"", b"(communicate still hung after tree kill)"
        u_exit = proc.returncode
    u_elapsed = time.monotonic() - u_t0
    out_text = scrub(out_b.decode("utf-8", errors="replace"))
    err_text = scrub(err_b.decode("utf-8", errors="replace"))
    (EVID / "unittest-stdout.txt").write_text(out_text, encoding="utf-8")
    (EVID / "unittest-stderr.txt").write_text(err_text, encoding="utf-8")
    state["unittest"] = {"exit": u_exit, "elapsed_s": round(u_elapsed, 3),
                         "killed_by_timeout": killed}
    log(f"unittest exit={u_exit} elapsed={u_elapsed:.2f}s killed_by_timeout={killed}")
    (EVID / "unittest-meta.txt").write_text(
        "command(脱敏): " + " ".join(cmd) + "\n"
        "cwd: " + str(TESTS_DIR) + "\n"
        "env keys: PATH,SYSTEMROOT,COMSPEC,TEMP,TMP,RETROLUME_TASK_083_DATABASE_URL(值脱敏)\n"
        f"exit={u_exit} elapsed_s={u_elapsed:.3f} killed_by_timeout={killed}\n",
        encoding="utf-8")

    # 修正04（批次三后）：unittest 摘要行（Ran/OK/FAIL）写在 stderr 而非 stdout，
    # 解析须合并两路；批次三 verdict 因只查 stdout 被误标 TESTS_FAILED，
    # 实际结果以 unittest-stderr.txt（Ran 6 tests / OK）+ exit=0 为准 = PASS。
    ran_lines = [l for l in (out_text + "\n" + err_text).splitlines() if l.startswith("Ran ")]
    ok_lines = [l for l in (out_text + "\n" + err_text).splitlines() if l.strip() == "OK"]
    schemas = sorted({l.split("schema=")[1].split()[0]
                      for l in out_text.splitlines() if "schema=" in l})
    (EVID / "schemas.txt").write_text("\n".join(schemas) + "\n", encoding="utf-8")
    state["unittest"]["ran"] = ran_lines
    state["unittest"]["ok"] = bool(ok_lines)
    state["unittest"]["schema_count"] = len(schemas)
    log(f"Ran行={ran_lines} OK行={len(ok_lines)} schema数={len(schemas)}")

    if u_exit == 0 and not killed and any("Ran 6 tests" in l for l in ran_lines) and ok_lines:
        state["verdict"] = "PASS"
    elif killed:
        state["verdict"] = "TESTS_TIMEOUT_KILLED"
    else:
        state["verdict"] = "TESTS_FAILED"

finally:
    # 5) finally 收尾：确认测试子进程退出 → 核对ID/标签 → stop → inspect Running=false
    log("FINALLY 收尾开始")
    if state.get("verdict") is None:
        state["verdict"] = "RUNNER_ERROR"
    cleanup_ok = False
    final_running = None
    try:
        # 确认测试子进程退出（proc 可能不存在于异常早期路径）
        try:
            if proc is not None and proc.poll() is None:  # noqa: F821
                proc.kill()
                proc.wait(timeout=15)
                log("测试子进程仍在，已补杀并确认退出")
        except Exception as e:
            log(f"子进程确认异常: {type(e).__name__}: {e}")
        if created and container_id:
            r = run_docker(["inspect", "--format", INSPECT_TPL, container_id], 15, "inspect-before-stop")
            verified = False
            if r is not None and r.returncode == 0:
                try:
                    info = json.loads(r.stdout)
                    lbl = info.get("labels") or {}
                    verified = (str(info.get("id", "")).startswith(container_id[:12])
                                and lbl.get("retrolume-run") == RUN_TAG
                                and lbl.get("retrolume-task") == "083")
                except json.JSONDecodeError:
                    verified = False
            log(f"停止前容器身份核对 {'OK' if verified else 'FAIL'}")
            if verified:
                r = run_docker(["stop", "-t", "10", container_id], 30, "stop")
                if r is None or r.returncode != 0:
                    log("stop 失败 → 对同一核实ID一次 kill")
                    run_docker(["kill", container_id], 20, "kill")
                r = run_docker(["inspect", "--format", INSPECT_TPL, container_id], 15, "inspect-final")
                if r is not None and r.returncode == 0:
                    (EVID / "container-final-inspect.json").write_text(scrub(r.stdout), encoding="utf-8")
                    try:
                        final_running = json.loads(r.stdout).get("running")
                        cleanup_ok = (final_running is False)
                    except json.JSONDecodeError:
                        cleanup_ok = False
                log(f"最终 Running={final_running} cleanup_ok={cleanup_ok}")
            else:
                log("身份核对失败：不 stop 不 kill，记 cleanup_incomplete")
        else:
            log("容器未创建，无需停止")
            cleanup_ok = True
    finally:
        state["cleanup_ok"] = cleanup_ok
        state["final_running"] = final_running
        if state.get("verdict") == "PASS" and not cleanup_ok:
            state["verdict"] = "CLEANUP_INCOMPLETE"
        (EVID / "runner-log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        (EVID / "runner-state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"RUNNER_VERDICT = {state.get('verdict')}", flush=True)
