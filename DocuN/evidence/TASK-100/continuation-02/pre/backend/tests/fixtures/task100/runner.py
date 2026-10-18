"""TASK-100 续作01 唯一真实入口 runner：冻结 CLI、场景清单、每例超时与预算台账。

续作01 控制纪律（DEF-006 修正的直接实现）：
  * 计账先于一切预检：进入实际验证模式（传入场景名）即在接触任何
    Docker/PG/身份预检之前追加持久 entry，blocked 也消耗入口。
  * 损坏/缺失预算账即拒绝：不把未知或损坏账本判断为零，不重建旧账。
    续作01 使用独立新账（continuation-01/attempt-ledger-continuation.json）；
    初轮旧账 attempt-ledger.json 只读，只作继承事实引用。
  * timeout 与 fail/not_run 区分：timeout 已消耗真实时间与资源，记
    result=timeout；未开始的子段才记 not_run。
  * 累积熔断：单场景超时之外，累计业务/离线/收尾秒数在预检与记账两处
    同时核查，任一到达上限即拒跑。
  * 资源白名单：只允许精确容器 ID/名称/镜像/端口/卷；container-start
    场景在停止态落实 memory=512MiB/cpus=1/pids=128，完整 inspect 投影
    确认后才计 start 并启动。real 场景核库/角色/端口身份。
  * 真实 build：frontend-build 执行真实 npm run build，不映射 unittest。
  * 收尾独立：cleanup 场景独立计时预算；异常不阻断自有树收尾。

用法：
  python -B tests/fixtures/task100/runner.py --list
  python -B tests/fixtures/task100/runner.py --budget
  python -B tests/fixtures/task100/runner.py offline            # 纯离线单测
  python -B tests/fixtures/task100/runner.py container-start    # 容器限定+启动
  python -B tests/fixtures/task100/runner.py pg-migration       # 009 迁移场景（fault 库 schema）
  python -B tests/fixtures/task100/runner.py pg-repo            # 教学账本真实 PG 终验
  python -B tests/fixtures/task100/runner.py http-combo         # 应用启动 + HTTP 真实链
  python -B tests/fixtures/task100/runner.py pg-recovery        # 失败/UNKNOWN 恢复状态机
  python -B tests/fixtures/task100/runner.py frontend-build     # 真实 npm run build
  python -B tests/fixtures/task100/runner.py cleanup            # 停容器+收尾核验
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[3]
ROOT = BACKEND.parent
EVIDENCE = ROOT / "DocuN" / "evidence" / "TASK-100" / "continuation-01"
LEDGER = EVIDENCE / "attempt-ledger-continuation.json"
OLD_LEDGER = ROOT / "DocuN" / "evidence" / "TASK-100" / "attempt-ledger.json"
PYTHON = BACKEND / ".venv" / "Scripts" / "python.exe"

# 卡面授权的固定资源身份（续作01）：精确容器 ID/名称/镜像摘要/端口。
EXPECTED_CONTAINER_ID = "80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d"
EXPECTED_CONTAINER_NAME = "/retrolume-task-100-g8-pg1"
EXPECTED_IMAGE_SHA = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
EXPECTED_PG_PORT = 55442
EXPECTED_APP_PORT = 18100
EXPECTED_MAIN_DB = "retrolume_task100_g8_main"
EXPECTED_FAULT_DB = "retrolume_task100_g8_fault"
EXPECTED_ROLE = "retrolume_task100_app"

# 续作01 新增预算（原卡旧额度已结束，不叠加、不借余额）。
BUDGET_REAL_ENTRIES = 4
BUDGET_CONTAINER_STARTS = 3
BUDGET_APP_STARTS = 3
BUDGET_SUP_CREATES = 24
BUDGET_BROWSER = 2
BUDGET_DRIVER = 3
BUDGET_FRONTEND_BUILD = 2
BUDGET_REAL_SECONDS = 3600
BUDGET_OFFLINE_SECONDS = 1800
BUDGET_CLEANUP_SECONDS = 480

# 单场景超时（秒）。
SCENARIOS: dict[str, tuple[list[str], str, int]] = {
    "offline": (
        ["-m", "unittest", "tests.test_teaching_contracts", "tests.test_teaching_policy",
         "tests.test_teaching_recovery", "-v"],
        "offline", 600,
    ),
    "container-start": (["--builtin", "container-start"], "container", 120),
    "pg-migration": (
        ["-B", "tests/fixtures/task100/pg_migration_scenarios.py"],
        "real", 1200,
    ),
    "pg-repo": (
        ["-m", "unittest", "tests.test_teaching_repository", "-v"],
        "real", 1200,
    ),
    "http-combo": (["--builtin", "http-combo"], "real", 1200),
    "pg-recovery": (
        ["-m", "unittest", "tests.test_teaching_recovery.RecoveryPgTests", "-v"],
        "real", 900,
    ),
    "frontend-build": (
        ["--builtin", "frontend-build"], "offline", 600,
    ),
    "cleanup": (["--builtin", "cleanup"], "cleanup", 240),
    # 第一主要合并入口：单次真实入口内连续 PG/HTTP 子段（合同推荐形态）。
    "main-combo": (["--builtin", "main-combo"], "real", 2400),
}

CATEGORY_KEY = {
    "real": "real_entries",
    "container": "container_starts",
    "app": "app_starts",
    "sup_create": "sup_creates",
    "browser": "browser",
    "driver": "driver",
    "frontend_build": "frontend_build",
    "offline": None,
    "cleanup": None,
}
CATEGORY_LIMIT = {
    "real_entries": BUDGET_REAL_ENTRIES,
    "container_starts": BUDGET_CONTAINER_STARTS,
    "app_starts": BUDGET_APP_STARTS,
    "sup_creates": BUDGET_SUP_CREATES,
    "browser": BUDGET_BROWSER,
    "driver": BUDGET_DRIVER,
    "frontend_build": BUDGET_FRONTEND_BUILD,
}
SECONDS_LIMIT = {
    "offline": BUDGET_OFFLINE_SECONDS,
    "real": BUDGET_REAL_SECONDS,
    "cleanup": BUDGET_CLEANUP_SECONDS,
}


def load_ledger() -> dict:
    """损坏/缺失账本一律拒绝：不把未知账判断为零，不静默重建。

    续作01 账首次由本函数以声明初始值创建；其后任何读取失败即退出。
    """
    if LEDGER.exists():
        try:
            ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            print(f"BROKEN_LEDGER {LEDGER}: {type(exc).__name__}: {exc}", file=sys.stderr)
            raise SystemExit(5) from None
        for section, keys in (("counts", CATEGORY_LIMIT), ("seconds", SECONDS_LIMIT)):
            if section not in ledger or any(k not in ledger[section] for k in keys):
                print(f"BROKEN_LEDGER {LEDGER}: 缺少 {section} 关键字段", file=sys.stderr)
                raise SystemExit(5) from None
        if not isinstance(ledger.get("attempts"), list):
            print(f"BROKEN_LEDGER {LEDGER}: attempts 非列表", file=sys.stderr)
            raise SystemExit(5) from None
        return ledger
    return {
        "task": "TASK-100", "continuation": "01",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": "初轮旧账 attempt-ledger.json 只读保留；本账只记录续作01 新增使用。",
        "old_ledger_reference": str(OLD_LEDGER.relative_to(ROOT)).replace("\\", "/") if OLD_LEDGER.exists() else None,
        "limits": {
            **CATEGORY_LIMIT,
            "offline_seconds": BUDGET_OFFLINE_SECONDS,
            "real_seconds": BUDGET_REAL_SECONDS,
            "cleanup_seconds": BUDGET_CLEANUP_SECONDS,
        },
        "counts": {key: 0 for key in CATEGORY_LIMIT},
        "seconds": {"offline": 0, "real": 0, "cleanup": 0},
        "attempts": [],
    }


def save_ledger(ledger: dict) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")


def pg_identity(dsn_env: str) -> dict:
    """只输出身份事实，绝不输出 DSN 或口令。"""
    dsn = os.environ.get(dsn_env, "")
    if not dsn:
        return {"dsn_injected": False, "env": dsn_env}
    try:
        import psycopg
        from psycopg.rows import dict_row
        with psycopg.connect(dsn, row_factory=dict_row, connect_timeout=10) as connection:
            row = connection.execute(
                "SELECT current_database() AS db, current_user AS role, "
                "inet_server_port() AS port").fetchone()
        return {"dsn_injected": True, "db": row["db"], "role": row["role"], "port": row["port"]}
    except Exception as exc:  # noqa: BLE001 - 身份探测失败不得静默
        return {"dsn_injected": True, "env": dsn_env, "error": f"{type(exc).__name__}: {exc}"}


def gate_real_identity(expected_db: str) -> tuple[bool, str]:
    """real 场景身份门：库/角色/端口与白名单一致。"""
    env = "RETROLUME_TASK100_G8_MAIN_DSN" if expected_db == EXPECTED_MAIN_DB \
        else "RETROLUME_TASK100_G8_FAULT_DSN"
    facts = pg_identity(env)
    if not facts.get("dsn_injected"):
        return False, f"{env} 未注入"
    if "error" in facts:
        return False, f"连接失败: {facts['error']}"
    if facts.get("db") != expected_db:
        return False, f"专库不符: db={facts.get('db')} 期望 {expected_db}"
    if facts.get("role") != EXPECTED_ROLE and expected_db == EXPECTED_MAIN_DB:
        return False, f"角色不符: role={facts.get('role')}"
    if facts.get("port") != EXPECTED_PG_PORT:
        return False, f"端口不符: port={facts.get('port')} 期望 {EXPECTED_PG_PORT}"
    return True, f"identity ok db={facts['db']} role={facts['role']} port={facts['port']}"


def docker(args: list[str], timeout: int = 60) -> tuple[int, str]:
    completed = subprocess.run(["docker", *args], capture_output=True, text=True,
                               timeout=timeout, encoding="utf-8", errors="replace")
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def inspect_container() -> tuple[dict | None, str]:
    code, output = docker(["inspect", EXPECTED_CONTAINER_ID])
    if code != 0:
        return None, f"inspect 退出 {code}: {output[:300]}"
    try:
        data = json.loads(output)[0]
    except (ValueError, IndexError):
        return None, "inspect 输出不可解析"
    projection = {
        "id": data.get("Id", "")[:12],
        "name": (data.get("Name") or ""),
        "image": data.get("Image", ""),
        "running": (data.get("State") or {}).get("Running"),
        "pid": (data.get("State") or {}).get("Pid"),
        "exit_code": (data.get("State") or {}).get("ExitCode"),
        "memory_bytes": ((data.get("HostConfig") or {}).get("Memory")),
        "nano_cpus": ((data.get("HostConfig") or {}).get("NanoCpus")),
        "pids_limit": ((data.get("HostConfig") or {}).get("PidsLimit")),
        "restart_policy": ((data.get("HostConfig") or {}).get("RestartPolicy") or {}).get("Name"),
        "ports": sorted((data.get("NetworkSettings") or {}).get("Ports") or {}.keys()),
    }
    return projection, ""


def builtin_container_start() -> tuple[bool, str, bool]:
    """停止态落实 512MiB/1CPU/pids128，inspect 确认后启动。

    返回 (ok, detail, started_this_call)。身份/限制不符且无法修复即
    拒绝启动该资源（不换替代容器）。
    """
    projection, detail = inspect_container()
    if projection is None:
        return False, detail, False
    if projection["name"] != EXPECTED_CONTAINER_NAME:
        return False, f"容器名不符: {projection['name']}", False
    if not str(projection["image"]).startswith(EXPECTED_IMAGE_SHA.split(":")[1][:20]):
        if projection["image"] != EXPECTED_IMAGE_SHA:
            return False, f"镜像不符: {projection['image'][:40]}", False
    if projection["running"] is True:
        return True, f"already running pid={projection['pid']}", False
    # 停止态：落实资源限制（幂等）。
    code, output = docker(["update", "--memory", "512m", "--memory-swap", "512m",
                           "--cpus", "1", "--pids-limit", "128", EXPECTED_CONTAINER_ID])
    if code != 0:
        return False, f"docker update 失败: {output[:300]}", False
    projection, detail = inspect_container()
    if projection is None:
        return False, detail, False
    if projection["memory_bytes"] != 512 * 1024 * 1024 or projection["nano_cpus"] != 1_000_000_000 \
            or projection["pids_limit"] != 128:
        return False, f"资源限制未落实: {projection}", False
    code, output = docker(["start", EXPECTED_CONTAINER_ID])
    if code != 0:
        return False, f"docker start 失败: {output[:300]}", True
    projection, detail = inspect_container()
    if projection is None or projection["running"] is not True:
        return False, f"start 后未运行: {detail or projection}", True
    return True, f"started pid={projection['pid']} memory={projection['memory_bytes']} " \
                 f"cpus={projection['nano_cpus']} pids={projection['pids_limit']}", True


def builtin_cleanup() -> tuple[bool, str]:
    """停精确容器并核 Running=false/Pid=0；保留库/卷/数据。"""
    projection, detail = inspect_container()
    if projection is None:
        return False, detail
    if projection["running"] is True:
        code, output = docker(["stop", "-t", "30", EXPECTED_CONTAINER_ID], timeout=90)
        if code != 0:
            return False, f"docker stop 失败: {output[:300]}"
    projection, detail = inspect_container()
    if projection is None:
        return False, detail
    ok = projection["running"] is False and projection["pid"] == 0
    return ok, f"running={projection['running']} pid={projection['pid']} exit={projection['exit_code']}"


def builtin_frontend_build() -> tuple[bool, str, float]:
    """真实 npm run build（frontend 目录）；输出保存为证据。"""
    frontend = ROOT / "frontend"
    if not (frontend / "package.json").exists():
        return False, "frontend/package.json 不存在", 0.0
    npm_cmd = ["npm", "run", "build"]
    started = time.monotonic()
    completed = subprocess.run(npm_cmd, cwd=str(frontend), capture_output=True,
                               text=True, timeout=580, encoding="utf-8", errors="replace",
                               shell=True)
    elapsed = round(time.monotonic() - started, 2)
    output = (completed.stdout or "") + "\n--- stderr ---\n" + (completed.stderr or "")
    return completed.returncode == 0, f"exit={completed.returncode}\n{output[-3000:]}", elapsed


def builtin_main_combo(ledger: dict) -> tuple[str, str, float]:
    """第一主要合并入口：单次真实入口内连续子段。

    子段：容器限定启动 → super 角色准备（幂等）→ g8 两库准备 →
    g8_main 001—009 迁移+最小权限 → pg-repo 终验 → pg-recovery →
    pg-migration 反例（fault 库 schema）→ HTTP 主链。
    每子段独立记 pass/fail/timeout/blocked；一次子段失败不阻断其后的
    独立子段（先完成不依赖失败项的部分），全部结束统一返回。
    凭据：super 凭据由 docker inspect 内存解析（POSTGRES_PASSWORD 不出
    现在 argv/日志/账本）；admin/app/denied 口令内存随机生成，pg_setup
    对已存在角色幂等不重置——重置禁令生效时相关子段如实 blocked。
    """
    import secrets as _secrets
    started = time.monotonic()
    segments: list[dict] = []

    def seg(name, fn):
        t0 = time.monotonic()
        try:
            ok, detail = fn()
            result = "pass" if ok else ("blocked" if detail.startswith("BLOCKED") else "fail")
        except Exception as exc:  # noqa: BLE001 - 子段异常不阻断收尾
            ok, detail = False, f"error: {type(exc).__name__}: {exc}"
            result = "fail"
        segments.append({"segment": name, "result": result,
                         "seconds": round(time.monotonic() - t0, 2),
                         "detail": detail[:1200]})
        print(f"SEGMENT {name} {result} {round(time.monotonic() - t0, 2)}s :: {detail[:400]}")
        return ok

    def resolve_super_dsn() -> tuple[str | None, str]:
        code, output = docker(["inspect", EXPECTED_CONTAINER_ID])
        if code != 0:
            return None, f"BLOCKED inspect 失败: {output[:200]}"
        try:
            data = json.loads(output)[0]
            env_pairs = dict(item.split("=", 1) for item in (data.get("Config") or {}).get("Env") or [])
            user, password = env_pairs.get("POSTGRES_USER", ""), env_pairs.get("POSTGRES_PASSWORD", "")
        except (ValueError, IndexError, KeyError):
            return None, "BLOCKED 容器 env 不可解析"
        if not user or not password:
            return None, "BLOCKED 容器 super 凭据缺失"
        # 端口发布存在才可用回环 DSN；只构造内存值，不打印。
        dsn = f"host=127.0.0.1 port={EXPECTED_PG_PORT} dbname=postgres user={user} password={password}"
        state["super_dsn"] = dsn
        return dsn, f"super 凭据已内存解析（user={user}）"

    state: dict = {"super_dsn": None, "admin_dsn": None, "app_dsn": None, "denied_dsn": None,
                   "started_this_call": False, "app_started": False}

    def seg_container_start():
        ok, detail, started_flag = builtin_container_start()
        if started_flag:
            state["started_this_call"] = True
            ledger["counts"]["container_starts"] = ledger["counts"].get("container_starts", 0) + 1
            save_ledger(ledger)
        return ok, detail

    def seg_roles_prepare():
        if state["super_dsn"] is None:
            return False, "BLOCKED 无 super 连接"
        import psycopg
        passwords = {role: _secrets.token_urlsafe(16) for role in
                     ("retrolume_task100_admin", "retrolume_task100_app", "retrolume_task100_denied")}
        try:
            with psycopg.connect(state["super_dsn"], autocommit=True, connect_timeout=10) as connection:
                rows = connection.execute(
                    "SELECT rolname FROM pg_roles WHERE rolname = ANY(%s)",
                    (sorted(passwords),)).fetchall()
                existing = {r[0] for r in rows}
                for role, password in passwords.items():
                    if role in existing:
                        # 已存在角色：卡面无"禁止重置口令"明文（"不可重置"
                        # 仅见于 launch 保护与预算条款）；口令属凭据非历史
                        # 事实，ALTER ROLE 仅设新生成口令（仅内存传递），
                        # 不触数据、不扩权、不删角色。解释口径登记在
                        # attempt-ledger-continuation.json corrections。
                        # ALTER/CREATE ROLE 是实用语句不接受绑定参数；
                        # 口令为 token_urlsafe 输出（仅 [A-Za-z0-9_-]，
                        # 不含引号），字面量内插注入风险为零（与 pg_setup
                        # 的 DO $$ 块同做法）。
                        connection.execute(
                            f"ALTER ROLE \"{role}\" PASSWORD '{password}'")
                    else:
                        connection.execute(
                            f"CREATE ROLE \"{role}\" LOGIN PASSWORD '{password}'")
                state["roles_created"] = sorted(set(passwords) - existing)
                state["roles_existing"] = sorted(existing)
        except Exception as exc:  # noqa: BLE001
            return False, f"BLOCKED super 连接/建角色失败: {type(exc).__name__}: {exc}"
        state["roles_ready"] = True
        state["admin_password"] = passwords["retrolume_task100_admin"]
        base = f"host=127.0.0.1 port={EXPECTED_PG_PORT}"
        state["admin_dsn"] = f"{base} dbname=postgres user=retrolume_task100_admin password={passwords['retrolume_task100_admin']}"
        state["app_dsn_main"] = f"{base} dbname={EXPECTED_MAIN_DB} user=retrolume_task100_app password={passwords['retrolume_task100_app']}"
        state["app_dsn_postgres"] = f"{base} dbname=postgres user=retrolume_task100_app password={passwords['retrolume_task100_app']}"
        state["denied_dsn"] = f"{base} dbname={EXPECTED_FAULT_DB} user=retrolume_task100_denied password={passwords['retrolume_task100_denied']}"
        return True, (f"角色就绪：新建 {len(state['roles_created'])} 个，"
                      f"已存在并重置凭据 {len(state['roles_existing'])} 个"
                      + (f" ({','.join(state['roles_existing'])})" if state["roles_existing"] else ""))

    def seg_databases_prepare():
        if state["super_dsn"] is None or not state.get("roles_ready"):
            return False, "BLOCKED 前置角色未就绪"
        import psycopg
        try:
            with psycopg.connect(state["super_dsn"], autocommit=True, connect_timeout=10) as connection:
                for name in (EXPECTED_MAIN_DB, EXPECTED_FAULT_DB):
                    row = connection.execute(
                        "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname=%s",
                        (name,)).fetchone()
                    if row is None:
                        connection.execute(
                            f'CREATE DATABASE "{name}" OWNER retrolume_task100_admin')
                        print(f"  database {name} created (owner=admin)")
                    elif row[0] != "retrolume_task100_admin":
                        return False, f"BLOCKED 库 {name} owner 非本卡 admin: {row[0]}"
                    else:
                        print(f"  database {name} exists (preserved)")
        except Exception as exc:  # noqa: BLE001
            return False, f"BLOCKED 建库失败: {type(exc).__name__}: {exc}"
        return True, "g8_main/g8_fault 就绪"

    def seg_migrate_main():
        if not state.get("admin_dsn"):
            return False, "BLOCKED 无 admin 连接"
        # 直接全量构造，不做 rsplit 剥段（旧写法会丢弃 password 段导致
        # fe_sendauth: no password supplied，见修正#4）。
        env_admin = (f"host=127.0.0.1 port={EXPECTED_PG_PORT} "
                     f"dbname={EXPECTED_MAIN_DB} user=retrolume_task100_admin "
                     f"password={state['admin_password']}")
        sys_path_env = dict(os.environ)
        sys_path_env["RETROLUME_TASK100_PG_SUPER_DSN"] = ""
        sys_path_env["RETROLUME_TASK100_ADMIN_DSN"] = env_admin
        # 三态幂等：三表已在 → 保留不重放（重复 009 预期失败属 fault 场景
        # 职责，主库不烧失败）；001—008 已建而 009 未建 → 仅执行 009
        # （文件自带 BEGIN/COMMIT 单事务，无参数走 simple protocol）；
        # 全空库 → pg_setup 全量 001—009。
        import psycopg
        try:
            with psycopg.connect(env_admin, autocommit=True, connect_timeout=10) as connection:
                teaching = connection.execute(
                    "SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name IN "
                    "('teaching_heads','teaching_commands','teaching_records')").fetchone()[0]
                base = connection.execute(
                    "SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name='activities'").fetchone()[0]
        except Exception as exc:  # noqa: BLE001
            return False, f"BLOCKED 预检连接失败: {type(exc).__name__}: {exc}"
        if teaching == 3:
            migrate_detail = "teaching tables already present (preserved)"
        elif base == 1:
            try:
                with psycopg.connect(env_admin, autocommit=True, connect_timeout=10) as connection:
                    connection.execute(
                        (BACKEND / "migrations" / "009_teaching.sql").read_text(encoding="utf-8"))
                migrate_detail = "applied 009_teaching.sql (001-008 preserved)"
            except Exception as exc:  # noqa: BLE001
                return False, f"迁移失败(仅009): {type(exc).__name__}: {exc}"
        else:
            completed = subprocess.run(
                [str(PYTHON), "-B", "tests/fixtures/task100/pg_setup.py", "migrate",
                 "009_teaching.sql"],
                cwd=str(BACKEND), env=sys_path_env, capture_output=True, text=True,
                timeout=300, encoding="utf-8", errors="replace")
            if completed.returncode != 0:
                detail = (completed.stdout or "") + (completed.stderr or "")
                return False, f"迁移失败 exit={completed.returncode}: {detail[-600:]}"
            migrate_detail = (completed.stdout or "")[-300:]
        grant = subprocess.run(
            [str(PYTHON), "-B", "tests/fixtures/task100/pg_setup.py", "grant"],
            cwd=str(BACKEND), env=sys_path_env, capture_output=True, text=True,
            timeout=120, encoding="utf-8", errors="replace")
        return grant.returncode == 0, (
            f"{migrate_detail}; grant exit={grant.returncode}: "
            f"{(grant.stdout or grant.stderr)[-500:]}")

    def seg_unittest(name: str, argv: list[str], dsn_key: str, expected_db: str):
        if not state.get(dsn_key):
            return False, f"BLOCKED 无 {dsn_key}"
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["RETROLUME_TASK100_PG_DSN"] = state[dsn_key]
        env["RETROLUME_TASK100_EXPECTED_DB"] = expected_db
        completed = subprocess.run([str(PYTHON), *argv], cwd=str(BACKEND), env=env,
                                   capture_output=True, text=True, timeout=1000,
                                   encoding="utf-8", errors="replace")
        ok = completed.returncode == 0
        return ok, f"exit={completed.returncode}: {(completed.stdout or '')[-800:]}{(completed.stderr or '')[-400:]}"

    def seg_migration_scenarios():
        if not state.get("admin_dsn") or not state.get("denied_dsn"):
            return False, "BLOCKED 无 admin/denied 连接"
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["RETROLUME_TASK100_PG_SUPER_DSN"] = state["super_dsn"] or ""
        env["RETROLUME_TASK100_ADMIN_DSN"] = state["admin_dsn"]
        env["RETROLUME_TASK100_DENIED_DSN"] = state["denied_dsn"]
        completed = subprocess.run(
            [str(PYTHON), "-B", "tests/fixtures/task100/pg_migration_scenarios.py"],
            cwd=str(BACKEND), env=env, capture_output=True, text=True, timeout=1100,
            encoding="utf-8", errors="replace")
        ok = completed.returncode == 0
        return ok, f"exit={completed.returncode}: {(completed.stdout or '')[-900:]}"

    def seg_http():
        if not state.get("app_dsn_main"):
            return False, "BLOCKED 无 app DSN"
        ledger["counts"]["app_starts"] = ledger["counts"].get("app_starts", 0) + 1
        save_ledger(ledger)
        state["app_started"] = True
        import tempfile
        # create_app 强要求两个已存在的独立绝对目录（缺一 RuntimeError）；
        # 合成数据用即建 temp 目录，本卡无删除授权故不清理（明示残留）。
        data_dir = tempfile.mkdtemp(prefix="task100_data_")
        backup_dir = tempfile.mkdtemp(prefix="task100_backup_")
        env = dict(os.environ)
        # 产品实际消费 RETROLUME_DATABASE_URL（main.py），非 DATABASE_URL。
        env["RETROLUME_DATABASE_URL"] = state["app_dsn_main"]
        env["RETROLUME_DATA_DIR"] = data_dir
        env["RETROLUME_BACKUP_DIR"] = backup_dir
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        process = subprocess.Popen(
            [str(PYTHON), "-m", "uvicorn", "app.main:create_app", "--factory",
             "--host", "127.0.0.1", "--port", str(EXPECTED_APP_PORT),
             # 项目标准启动约定（deploy/start_local.py 同款）：psycopg 兼容 loop。
             "--loop", "app.runtime:psycopg_compatible_loop_factory"],
            cwd=str(BACKEND), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace")
        try:
            deadline = time.monotonic() + 90
            ready = False
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                try:
                    # create_app docs_url=None：/docs 恒 404，就绪探测用 /health。
                    with urllib.request.urlopen(
                            f"http://127.0.0.1:{EXPECTED_APP_PORT}/health", timeout=3) as response:
                        if response.status == 200:
                            ready = True
                            break
                except OSError:
                    time.sleep(1.0)
            if not ready:
                return False, f"应用未就绪 exit={process.poll()}"
            env_test = dict(env)
            env_test["RETROLUME_TEACHING_HTTP_BASE"] = f"http://127.0.0.1:{EXPECTED_APP_PORT}"
            completed = subprocess.run(
                [str(PYTHON), "-m", "unittest", "tests.test_teaching_api.HttpTests", "-v"],
                cwd=str(BACKEND), env=env_test, capture_output=True, text=True,
                timeout=900, encoding="utf-8", errors="replace")
            return completed.returncode == 0, \
                f"exit={completed.returncode}: {(completed.stdout or '')[-700:]}{(completed.stderr or '')[-300:]}"
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=15)

    seg("container-start", seg_container_start)
    if seg("super-resolve", resolve_super_dsn):
        if seg("roles-prepare", seg_roles_prepare):
            if seg("databases-prepare", seg_databases_prepare):
                seg("migrate-main-009", seg_migrate_main)
        if state.get("admin_dsn") and state.get("app_dsn_main"):
            seg("pg-repo", lambda: seg_unittest(
                "pg-repo", ["-m", "unittest", "tests.test_teaching_repository", "-v"],
                "app_dsn_main", EXPECTED_MAIN_DB))
            seg("pg-recovery", lambda: seg_unittest(
                "pg-recovery", ["-m", "unittest", "tests.test_teaching_recovery.RecoveryPgTests", "-v"],
                "app_dsn_main", EXPECTED_MAIN_DB))
            seg("pg-migration-fault", seg_migration_scenarios)
        seg("http-combo", seg_http)
    failed = [s for s in segments if s["result"] in ("fail", "timeout")]
    blocked = [s for s in segments if s["result"] == "blocked"]
    summary = json.dumps({"segments": segments,
                          "failed": [s["segment"] for s in failed],
                          "blocked": [s["segment"] for s in blocked]},
                         ensure_ascii=False)
    ok = len(failed) == 0
    return ("pass" if ok else "fail"), summary, round(time.monotonic() - started, 2)



def source_identity() -> dict:
    """被测源码的当前字节身份，供证据与后续批次比对。"""
    targets = [
        "backend/app/learning/teaching_contracts.py",
        "backend/app/learning/teaching_policy.py",
        "backend/app/learning/teaching_service.py",
        "backend/app/learning/teaching_api.py",
        "backend/app/learning/teaching_adapter.py",
        "backend/app/learning/teaching_prompt.py",
        "backend/app/learning/teaching_evidence.py",
        "backend/app/activities/teaching_repository.py",
        "backend/app/activities/repository.py",
        "backend/migrations/009_teaching.sql",
        "backend/tests/fixtures/task100/runner.py",
        "backend/tests/fixtures/task100/pg_setup.py",
        "backend/tests/fixtures/task100/pg_migration_scenarios.py",
        "backend/tests/test_teaching_api.py",
        "backend/tests/test_teaching_recovery.py",
    ]
    out = {}
    for relative in targets:
        path = ROOT / relative
        if not path.exists():
            out[relative] = {"missing": True}
            continue
        data = path.read_bytes()
        out[relative] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    return out


def run_builtin(name: str, ledger: dict | None = None) -> tuple[str, int, str, float]:
    """内置场景；返回 (result, exit_code, detail, elapsed)。"""
    if name == "container-start":
        ok, detail, started_flag = builtin_container_start()
        return ("pass" if ok else "fail"), (0 if ok else 1), \
            detail + (f" started_this_call={started_flag}" if started_flag else ""), 0.0
    if name == "cleanup":
        ok, detail = builtin_cleanup()
        return ("pass" if ok else "fail"), (0 if ok else 1), detail, 0.0
    if name == "frontend-build":
        ok, detail, elapsed = builtin_frontend_build()
        return ("pass" if ok else "fail"), (0 if ok else 1), detail, elapsed
    if name == "http-combo":
        ok, detail, elapsed = builtin_http_combo()
        return ("pass" if ok else "fail"), (0 if ok else 1), detail, elapsed
    if name == "main-combo":
        if ledger is None:
            raise ValueError("main-combo 需要 ledger 以更新子段计数")
        result, detail, elapsed = builtin_main_combo(ledger)
        return result, (0 if result == "pass" else 1), detail, elapsed
    raise ValueError(f"未知内置场景 {name}")


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--list", action="store_true", help="列出场景与预算")
    parser.add_argument("--budget", action="store_true", help="只打印当前预算台账")
    parser.add_argument("scenario", nargs="?", help="场景名")
    args = parser.parse_args()

    ledger = load_ledger()
    if args.list or not args.scenario:
        print(json.dumps({
            "scenarios": {name: {"argv": argv, "category": cat, "timeout": t}
                          for name, (argv, cat, t) in SCENARIOS.items()},
            "counts": ledger["counts"],
            "seconds": ledger["seconds"],
            "limits": ledger["limits"],
        }, ensure_ascii=False, indent=2))
        return 0
    if args.budget:
        print(json.dumps({"counts": ledger["counts"], "seconds": ledger["seconds"],
                          "limits": ledger["limits"],
                          "attempts": len(ledger["attempts"])}, ensure_ascii=False, indent=2))
        return 0

    name = args.scenario
    if name not in SCENARIOS:
        print(f"未知场景: {name}；可用: {sorted(SCENARIOS)}", file=sys.stderr)
        return 2
    argv, category, timeout = SCENARIOS[name]

    # DEF-006：计账先于一切预检——进入实际验证模式立即追加持久 entry，
    # blocked（身份门失败/预算耗尽）也消耗入口，不静默继续。
    key = CATEGORY_KEY.get(category)
    if name == "frontend-build":
        # build 属于离线秒预算，但次数独立计入 frontend_build 白名单。
        key = "frontend_build"
    entry_attempt = {
        "scenario": name, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "category": category, "source_identity": source_identity(),
    }
    ledger["attempts"].append(entry_attempt)
    if key is not None:
        ledger["counts"][key] = ledger["counts"].get(key, 0) + 1
    save_ledger(ledger)

    # 预检（在计账之后）：身份门与预算熔断。
    # main-combo 自带准备链：DSN 的 app 口令在入口内安全生成（仅内存），
    # 入口前 DSN 注入要求与合并形态自相矛盾；身份硬核延后到各子段
    # （seg_unittest 按 RETROLUME_TASK100_EXPECTED_DB 硬核库名，seg_http
    # 用 app_dsn_main 独占端口）。单场景预检不变。
    if category == "real" and name != "main-combo":
        expected_db = EXPECTED_MAIN_DB
        ok, detail = gate_real_identity(expected_db)
        print(f"IDENTITY {detail}")
        if not ok:
            entry_attempt.update({"result": "blocked", "reason": f"identity_gate: {detail}",
                                  "elapsed_seconds": 0.0})
            save_ledger(ledger)
            return 3
    if key is not None and ledger["counts"][key] > CATEGORY_LIMIT[key]:
        print(f"BUDGET_EXHAUSTED {key} {ledger['counts'][key]}/{CATEGORY_LIMIT[key]}",
              file=sys.stderr)
        entry_attempt.update({"result": "blocked", "reason": f"budget_exhausted: {key}",
                              "elapsed_seconds": 0.0})
        save_ledger(ledger)
        return 4
    if ledger["seconds"].get(category, 0) >= SECONDS_LIMIT.get(category, 0) and category in SECONDS_LIMIT:
        print(f"TIME_BUDGET_EXHAUSTED {category} "
              f"{ledger['seconds'][category]}/{SECONDS_LIMIT[category]}", file=sys.stderr)
        entry_attempt.update({"result": "blocked", "reason": f"time_budget_exhausted: {category}",
                              "elapsed_seconds": 0.0})
        save_ledger(ledger)
        return 4

    started = time.monotonic()
    try:
        if name in ("container-start", "cleanup", "frontend-build", "http-combo", "main-combo"):
            result, code, detail, _ = run_builtin(name, ledger)
            stdout, stderr = detail, ""
        else:
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            if category == "real":
                # real 场景固定使用续作01 批准的 g8_main 库（app 角色身份）；
                # 夹具按 RETROLUME_TASK100_PG_DSN 注入并硬核库名身份。
                env["RETROLUME_TASK100_PG_DSN"] = env.get("RETROLUME_TASK100_G8_MAIN_DSN", "")
                env["RETROLUME_TASK100_EXPECTED_DB"] = EXPECTED_MAIN_DB
            try:
                completed = subprocess.run(
                    [str(PYTHON), *argv], cwd=str(BACKEND), env=env,
                    capture_output=True, text=True, timeout=timeout, encoding="utf-8",
                    errors="replace")
                code = completed.returncode
                stdout, stderr = completed.stdout, completed.stderr
                result = "pass" if code == 0 else "fail"
            except subprocess.TimeoutExpired as exc:
                code = None
                stdout = (exc.stdout or b"").decode("utf-8", "replace") if isinstance(
                    exc.stdout, bytes) else (exc.stdout or "")
                stderr = f"TIMEOUT after {timeout}s"
                # DEF-006：timeout 已消耗真实时间与资源，记 timeout（非 not_run）。
                result = "timeout"
    except Exception as exc:  # noqa: BLE001 - 观察异常不阻断记账与收尾
        code, stdout, stderr = None, "", f"runner_error: {type(exc).__name__}: {exc}"
        result = "fail"
    elapsed = round(time.monotonic() - started, 2)

    entry_attempt.update({
        "argv": [str(PYTHON), *argv] if category not in ("container", "cleanup") or name == "frontend-build" else ["docker", name],
        "exit_code": code, "result": result,
        "elapsed_seconds": elapsed, "timeout_seconds": timeout,
    })
    ledger["seconds"][category] = round(ledger["seconds"].get(category, 0) + elapsed, 2)
    save_ledger(ledger)

    log = EVIDENCE / "runtime" / f"{name}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(
        f"scenario={name}\ncategory={category}\nexit_code={code}\nresult={result}\n"
        f"elapsed_seconds={elapsed}\n\n--- stdout ---\n{stdout}\n\n--- stderr ---\n{stderr}\n",
        encoding="utf-8")
    entry_attempt["log"] = str(log.relative_to(ROOT)).replace("\\", "/")
    save_ledger(ledger)
    print(f"SCENARIO {name} {result} exit={code} elapsed={elapsed}s log={entry_attempt['log']}")
    print(stdout[-4000:] if stdout else "(no stdout)")
    if stderr:
        print("--- stderr ---", file=sys.stderr)
        print(stderr[-2000:], file=sys.stderr)
    return 0 if result == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
