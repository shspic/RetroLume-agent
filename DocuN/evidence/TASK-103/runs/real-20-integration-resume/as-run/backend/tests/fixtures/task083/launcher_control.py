"""TASK-083 09轮外层控制者：固定launcher→SUP→worker组合的真实PG验证批。

场景（卡面A—C；D不适用）：
  a   正常完整入口：真实run_supervised_window + 固定SUP + idle worker + 真实PG
      认领/关闭/结算；记录父/SUP/worker PID+创建时间、runTag/G、树退出与DB账。
  b   父级管理截止/无可信子结果：在 _SuspendedSupervisor.wait 真实函数调用边界
      注入确定性触发（业务Job出现即返回超时），验证有界终止、结果None、
      cleanup_incomplete；控制者持确切Job句柄独立收尾，不以SUP退出作树空或退款。
  c1  父在Resume前退出：P子进程在真实resume边界挂起，被精确终止后SUP悬停，
      验证不迟到Resume/不迟到认领，控制者精确收尾悬停SUP并核对映射销毁。
  c2  父在Resume后退出：P在真实wait边界被精确终止，已运行SUP独立完成自身截止
      与映射生命周期；控制者核对DB结算态、对象销毁与无进程残留。

纪律：不打印DSN；每场景新随机schema（迁移001—005），失败/成功现场保留；
不DROP；真实批只此一次启动（A/B/C1/C2各一次SUP+worker）；失败即停批。
"""

from __future__ import annotations

import asyncio
import ctypes
from ctypes import wintypes
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.rows import dict_row

from app.activities import ActivitySpec, PostgresAdmissionLedger, SourceSnapshot
from app.capabilities import Provider
from app.runtime import psycopg_compatible_loop_factory
from app.worker.command import WorkerCommand
from app.worker.session import SessionConfig
from app.worker.supervisor_ipc import NamedMapping
from app.worker.windows_job import JobUnknown, NamedJob, _FILETIME, job_name
import app.worker.launcher as launcher_module
from app.worker.launcher import run_supervised_window

EVID = Path(r"D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-083/launcher-complete-09")
SCENARIO = Path(__file__).with_name("launcher_scenario.py")
MIGRATIONS = [BACKEND / "migrations" / name for name in (
    "001_materials.sql", "002_activities.sql", "003_pdf_review.sql",
    "004_activities_time_budget.sql", "005_activities_dispatch_closed.sql",
)]

CONFIG = SessionConfig(
    window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1.0,
    startup_limit_seconds=2.0, manager_db_timeout_seconds=1.5,
    cleanup_seconds=2.0, mutex_wait_seconds=1.0, manager_overhead_seconds=10.0,
)

PROCESS_QUERY_LIMITED = 0x1000
PROCESS_TERMINATE = 0x0001
SYNCHRONIZE = 0x00100000
ERROR_ALREADY_EXISTS = 183
WAIT_OBJECT_0 = 0
JOB_OBJECT_BASIC_PROCESS_ID_LIST = 3

SCENARIOS = ("a", "b", "c1", "c2")
BATCH_DEADLINE_NS = time.monotonic_ns() + 540_000_000_000  # 卡面每批≤10分钟，留60秒收尾。

# 运行链冻结：13项沿Job07 post-run-check.json 参照值；其余6项做本批pre/post零漂移。
JOB07_REFERENCES = {
    "backend/tests/fixtures/task083/job_batch.py": "648e419cea693aa10630326cb28176e010a82b9f2c3380c33b42169c19bdef5b",
    "backend/tests/fixtures/task083/job_control.py": "5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2",
    "backend/tests/fixtures/task083/scenario_child.py": "98f132f272b952c22ac887efbf8026c5b00ec618838b6d484a3deec3c73f3f36",
    "backend/tests/fixtures/task083/fixture.py": "c9970b8ddc718da1a4e83c6d206a67f6bd000d715578e028c0a0964d9f53dc7f",
    "backend/app/worker/windows_job.py": "d05ca259d5c99e6cc8f67c7fcea01667068a2901066b865239e920bd0f5246f6",
    "backend/app/worker/session.py": "502a37436de83fa5e56636d54ae5a4f694639f18c5e474e02749162e4e15f16c",
    "backend/app/worker/command.py": "b0e91c3a2e65de19656b3c902df49a33bdd29dc135bc9c292e7732e300a5e273",
    "backend/app/worker/worker_main.py": "5d065b5e44b678c08dc34c9e611a5dcaaa2d0aa3ed2c6e588fe7a70ca25a1454",
    "backend/app/worker/launcher.py": "703ceb0344e21a174f3d70e81b05ede5635d700ed84f53e26e9ae70037d2acea",
    "backend/app/worker/supervisor_ipc.py": "57be00aead15114673b180b1abb436dde10ef426a618d56f30d0031e3201ac96",
    "backend/app/worker/supervisor_main.py": "98c420e75671b3ad1823ea5a72a3866221e7cb0fc1defe032feb0a5822afb145",
    "backend/app/worker/gate.py": "7e7588a58869038f53d850816c027aab00ecd1270d2c893d1fc4902978d32674",
    "backend/tests/test_worker_session.py": "720385a66045ce9f576bf7753024ee359fda2dfbae1defc081ba73516f18352c",
}
HASH_FILES = list(JOB07_REFERENCES) + [
    "backend/app/activities/repository.py",
    "backend/migrations/005_activities_dispatch_closed.sql",
    "backend/tests/fixtures/task083/pg_migration.py",
    "backend/tests/fixtures/task083/pg_close.py",
    "backend/tests/fixtures/task083/launcher_control.py",
    "backend/tests/fixtures/task083/launcher_scenario.py",
]
ROOT = BACKEND.parent


def log(event: dict) -> None:
    print(json.dumps(event, ensure_ascii=False, default=str), flush=True)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_all() -> dict:
    return {rel: sha256_of(ROOT / rel) for rel in HASH_FILES}


# ---------------------------------------------------------------- Windows句柄

def kernel_api():
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    api.OpenProcess.restype = wintypes.HANDLE
    api.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(_FILETIME)] * 4)]
    api.GetProcessTimes.restype = wintypes.BOOL
    api.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    api.TerminateProcess.restype = wintypes.BOOL
    api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    api.CreateEventW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
    api.CreateEventW.restype = wintypes.HANDLE
    api.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    api.OpenEventW.restype = wintypes.HANDLE
    api.SetEvent.argtypes = [wintypes.HANDLE]
    api.SetEvent.restype = wintypes.BOOL
    api.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
    api.QueryInformationJobObject.restype = wintypes.BOOL
    return api


def created_100ns(api, handle) -> int:
    times = [_FILETIME() for _ in range(4)]
    if not api.GetProcessTimes(handle, *(ctypes.byref(x) for x in times)):
        raise OSError(f"GetProcessTimes error {ctypes.get_last_error()}")
    return (int(times[0].dwHighDateTime) << 32) | int(times[0].dwLowDateTime)


def self_created_100ns(api) -> int:
    return created_100ns(api, ctypes.c_void_p(-1))  # GetCurrentProcess() 伪句柄。


def open_pid(api, pid: int, access: int = PROCESS_QUERY_LIMITED | SYNCHRONIZE):
    return api.OpenProcess(access, False, pid)


def pid_state(api, pid: int, expected_created: int | None = None) -> dict:
    handle = open_pid(api, pid)
    if not handle:
        return {"pid": pid, "open": False, "last_error": ctypes.get_last_error(),
                "alive": False, "created_100ns": None}
    try:
        created = created_100ns(api, handle)
        alive = api.WaitForSingleObject(handle, 0) != WAIT_OBJECT_0
        return {"pid": pid, "open": True, "created_100ns": created, "alive": alive,
                "created_matches": None if expected_created is None else created == expected_created}
    finally:
        api.CloseHandle(handle)


def terminate_and_wait(api, handle, seconds: float) -> bool:
    if api.WaitForSingleObject(handle, 0) == WAIT_OBJECT_0:
        return True
    api.TerminateProcess(handle, 1)
    return api.WaitForSingleObject(handle, int(seconds * 1000)) == WAIT_OBJECT_0


def new_event_or_reject(api, name: str):
    ctypes.set_last_error(0)
    handle = api.CreateEventW(None, True, False, name)
    code = ctypes.get_last_error()
    if not handle or code == ERROR_ALREADY_EXISTS:
        if handle:
            api.CloseHandle(handle)
        raise AssertionError(f"control event create/collision error={code}")
    return handle


def query_job_pids(api, job_handle) -> dict:
    buf = (ctypes.c_size_t * 66)()
    if not api.QueryInformationJobObject(job_handle, JOB_OBJECT_BASIC_PROCESS_ID_LIST,
                                         buf, ctypes.sizeof(buf), None):
        raise OSError(f"QueryInformationJobObject error {ctypes.get_last_error()}")
    assigned = buf[0] & 0xFFFFFFFF
    in_list = (buf[0] >> 32) & 0xFFFFFFFF
    pids = [int(buf[i]) for i in range(1, 1 + min(in_list, 64))]
    return {"assigned": assigned, "in_list": in_list, "pids": pids}


def workers_of(api, pids: list[int]) -> list[dict]:
    records = []
    for pid in pids:
        handle = open_pid(api, pid)
        if not handle:
            records.append({"pid": pid, "open": False, "last_error": ctypes.get_last_error()})
            continue
        try:
            records.append({"pid": pid, "open": True, "created_100ns": created_100ns(api, handle)})
        finally:
            api.CloseHandle(handle)
    return records


# ---------------------------------------------------------------- DB 辅助

def db_row(scoped_dsn: str, query: str, params=()):
    with psycopg.connect(scoped_dsn, connect_timeout=3, row_factory=dict_row) as conn:
        return (conn.execute(query, params)).fetchone()


def build_activity(scoped_dsn: str, activity_id: str) -> None:
    """与 pg_close.build 相同的合成数据，仅建活动不认领（认领由SUP执行）。"""
    source_id, version_id = str(uuid4()), str(uuid4())

    async def setup() -> None:
        async with await psycopg.AsyncConnection.connect(scoped_dsn, autocommit=True) as conn:
            await conn.execute("INSERT INTO material_sources(id,title,revision) VALUES (%s,'task083',0)", (source_id,))
            await conn.execute(
                "INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES (%s,%s,'task083.txt','txt',%s,1)",
                (version_id, source_id, "d" * 64),
            )
            await conn.execute("UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s", (version_id, source_id))
        spec = ActivitySpec(
            activity_id=activity_id,
            sources=(SourceSnapshot(source_id, version_id, 1),),
            deadline_at=datetime.now(timezone.utc) + timedelta(minutes=20),
            max_requests=8, max_cost_microunits=800, reserve_cost_microunits=100,
            max_request_bytes=4096, max_output_tokens=256, max_running_seconds=180,
            allowed_models=((Provider.DEEPSEEK_CHAT_COMPLETIONS.value, "synthetic-model"),),
            allowed_tools=(), scope_revision=1,
        )
        await PostgresAdmissionLedger(scoped_dsn).create_activity(spec)

    asyncio.run(setup(), loop_factory=psycopg_compatible_loop_factory)


def prepare_schema(base_dsn: str, letter: str) -> tuple[str, str]:
    schema = "task083_d1_" + letter + "_" + uuid4().hex[:8]
    with psycopg.connect(base_dsn, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    scoped = make_conninfo(base_dsn, options=f"-c search_path={schema}")
    with psycopg.connect(scoped, autocommit=True) as conn:
        for path in MIGRATIONS:
            conn.execute(path.read_text(encoding="utf-8"))
    return schema, scoped


# ---------------------------------------------------------------- A场景观察线程

class WorkerWatcher(threading.Thread):
    """A场景在飞观察：记录worker PID+创建时间（只读，不干预SUP）。"""

    def __init__(self, scoped: str, activity_id: str, api):
        super().__init__(daemon=True)
        self.scoped = scoped
        self.activity_id = activity_id
        self.api = api
        self.stop_event = threading.Event()
        self.result: dict | None = None

    def run(self) -> None:
        deadline = time.monotonic() + 20.0
        try:
            conn = psycopg.connect(self.scoped, connect_timeout=3, row_factory=dict_row)
        except Exception as exc:  # 连接失败不干预场景，仅如实记录。
            self.result = {"watcher_error": type(exc).__name__}
            return
        try:
            while not self.stop_event.is_set() and time.monotonic() < deadline:
                row = conn.execute(
                    "SELECT execution_generation, status FROM activities WHERE id=%s",
                    (self.activity_id,)).fetchone()
                if row and row["status"] == "running":
                    try:
                        job = NamedJob.open_existing(self.activity_id, row["execution_generation"])
                    except JobUnknown:
                        time.sleep(0.03)
                        continue
                    try:
                        listing = query_job_pids(self.api, job.handle)
                        self.result = {
                            "generation": row["execution_generation"],
                            "active_at_query": job.active_processes(),
                            "workers": workers_of(self.api, listing["pids"]),
                        }
                    finally:
                        job.close()
                    return
                time.sleep(0.03)
            self.result = {"missed": True}
        except Exception as exc:
            self.result = {"watcher_error": type(exc).__name__}
        finally:
            conn.close()


# ---------------------------------------------------------------- B场景注入控制

class DeadlineTrigger:
    """在 _SuspendedSupervisor.wait 真实调用边界注入确定性管理截止触发。

    触发条件是真实可观察事实：DB status=running（claim已提交）且精确命名的
    业务Job对象已存在。控制者随即持有该Job句柄——SUP死亡后最后句柄不关闭，
    对象归属移交控制者，不以SUP退出作树空或退款证明。
    """

    def __init__(self, scoped: str, activity_id: str):
        self.scoped = scoped
        self.activity_id = activity_id
        self.fired = False
        self.generation: int | None = None
        self.job: NamedJob | None = None

    def try_trigger(self) -> bool:
        if self.fired:
            return False
        row = db_row(self.scoped,
                     "SELECT execution_generation, status FROM activities WHERE id=%s",
                     (self.activity_id,))
        if not row or row["status"] != "running":
            return False
        try:
            self.job = NamedJob.open_existing(self.activity_id, row["execution_generation"])
        except JobUnknown:
            return False
        self.generation = row["execution_generation"]
        self.fired = True
        return True

    def release_handle(self) -> None:
        if self.job is not None:
            try:
                self.job.close()
            except BaseException:
                pass
            self.job = None


# ---------------------------------------------------------------- P子进程驱动

class PProcess:
    def __init__(self, mode: str, activity_id: str, run_tag: str, schema: str, base_dsn: str, api):
        self.mode = mode
        self.api = api
        self.evidence = EVID / f"p-evidence-{mode}-{run_tag}.jsonl"
        self.stderr_file = EVID / f"p-stderr-{mode}-{run_tag}.log"
        base = f"Local\\RetroLume.Task083.{run_tag}"
        self.barrier_name = f"{base}.Barrier"
        self.go_name = f"{base}.Go"
        self.barrier = None
        self.go = None
        try:
            self.barrier = new_event_or_reject(api, self.barrier_name)
            self.go = new_event_or_reject(api, self.go_name)
        except BaseException:
            self._close_events()
            raise
        env = os.environ.copy()
        env["RETROLUME_TASK_083_D1_DATABASE_URL"] = base_dsn  # P读后立即pop， grandchildren环境干净。
        self.stderr_fh = open(self.stderr_file, "w", encoding="utf-8")
        self.proc = subprocess.Popen(
            [sys.executable, "-B", str(SCENARIO), mode, activity_id, run_tag,
             self.barrier_name, self.go_name, str(self.evidence), schema],
            cwd=str(BACKEND), env=env,
            stdout=subprocess.DEVNULL, stderr=self.stderr_fh,
        )
        self.launcher_pid = self.proc.pid
        self.handles: list[dict] = []

    def wait_barrier(self, seconds: float) -> bool:
        return self.api.WaitForSingleObject(self.barrier, int(seconds * 1000)) == WAIT_OBJECT_0

    def read_evidence(self) -> list[dict]:
        time.sleep(0.05)  # 信号先于文件写出已由signal()先写后置序保证；短暂等待读取完成。
        records = []
        if self.evidence.exists():
            for line in self.evidence.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(json.loads(line))
        return records

    def open_handles(self, python_pid: int) -> None:
        self.handles = []
        for label, pid in (("python", python_pid), ("launcher", self.launcher_pid)):
            handle = open_pid(self.api, pid, PROCESS_QUERY_LIMITED | SYNCHRONIZE | PROCESS_TERMINATE)
            if not handle:
                raise AssertionError(f"P {label} 精确句柄不可得 pid={pid}")
            self.handles.append({"label": label, "pid": pid, "handle": handle,
                                 "created_100ns": created_100ns(self.api, handle)})

    def kill(self, wait_s: float = 5.0) -> dict:
        """精确终止P（python先于launcher；同一进程则只终止一次）。不触及SUP。"""
        outcome = []
        seen = set()
        for item in self.handles:
            if item["pid"] in seen:
                continue
            seen.add(item["pid"])
            dead = terminate_and_wait(self.api, item["handle"], wait_s)
            outcome.append({"label": item["label"], "pid": item["pid"], "dead": dead})
        return {"terminated": outcome}

    def _close_events(self) -> None:
        for handle in (self.barrier, self.go):
            if handle:
                self.api.CloseHandle(handle)
        self.barrier = None
        self.go = None

    def close(self) -> None:
        for item in self.handles:
            self.api.CloseHandle(item["handle"])
        self.handles = []
        self._close_events()
        self.stderr_fh.close()
        if self.proc.poll() is None:  # 兜底：P若仍存活（屏障前失败等），按精确PID树收尾。
            try:
                subprocess.run(["taskkill", "/PID", str(self.proc.pid), "/T", "/F"],
                               capture_output=True, timeout=15)
                self.proc.wait(timeout=15)
            except BaseException:
                pass


# ---------------------------------------------------------------- 场景实现

def scenario_a(base_dsn: str, api) -> dict:
    activity_id = str(uuid4())
    run_tag = "d1-09a-" + uuid4().hex[:8]
    schema, scoped = prepare_schema(base_dsn, "a")
    build_activity(scoped, activity_id)
    g0 = db_row(scoped, "SELECT execution_generation, status FROM activities WHERE id=%s", (activity_id,))
    record = {"scenario": "a", "run_tag": run_tag, "activity_id": activity_id, "schema": schema,
              "pre_claim": g0, "parent": {"pid": os.getpid(), "created_100ns": self_created_100ns(api)}}
    if g0["status"] != "pending":
        raise AssertionError("A前置状态非pending")
    watcher = WorkerWatcher(scoped, activity_id, api)
    watcher.start()
    started = time.monotonic()
    outcome = run_supervised_window(
        PostgresAdmissionLedger(scoped), CONFIG, activity_id, f"worker-{run_tag}",
        WorkerCommand(), run_tag=run_tag,
    )
    wall = time.monotonic() - started
    watcher.stop_event.set()
    watcher.join(timeout=5)
    record["wall_seconds"] = round(wall, 3)
    record["outcome"] = asdict(outcome)
    record["watcher"] = watcher.result
    if watcher.result and watcher.result.get("workers"):
        record["watcher"]["workers"] = [
            {**w, "matches_outcome_pid": None if outcome.pid is None else w["pid"] == outcome.pid}
            for w in watcher.result["workers"]]

    if outcome.state != "settled":
        raise AssertionError(f"A state={outcome.state}")
    if outcome.generation is None or outcome.job_name != job_name(activity_id, outcome.generation):
        raise AssertionError("A Job身份不匹配")
    if outcome.pid is None or outcome.active_processes_at_end != 0:
        raise AssertionError("A worker/树退出证据缺失")
    if not (outcome.settled_seconds is not None and 1 <= outcome.settled_seconds <= CONFIG.window_seconds
            and outcome.reserved_seconds == 0 and outcome.pending_fold_seconds == 0):
        raise AssertionError("A 结算账目不符")
    if outcome.cleanup_incomplete or outcome.cleanup_errors:
        raise AssertionError(f"A cleanup_incomplete errors={outcome.cleanup_errors}")
    if outcome.manager_pid is None or not outcome.manager_created_100ns:
        raise AssertionError("A SUP身份缺失")
    timing = outcome.timing_diagnostic
    if not timing or timing[1] <= timing[0] or not (1 <= timing[3] <= CONFIG.window_seconds) \
            or timing[3] != outcome.settled_seconds or timing[4] != CONFIG.window_seconds:
        raise AssertionError(f"A timing_diagnostic={timing}")

    row = db_row(scoped, """SELECT status, execution_generation, running_reserved_seconds,
                                   running_settled_seconds, dispatch_closed, last_settled_generation,
                                   last_settled_seconds FROM activities WHERE id=%s""", (activity_id,))
    record["db_after"] = row
    if row["status"] != "pending" or row["running_reserved_seconds"] != 0 \
            or row["running_settled_seconds"] != outcome.settled_seconds \
            or row["dispatch_closed"] is not True \
            or row["execution_generation"] != outcome.generation + 1 \
            or row["last_settled_generation"] != outcome.generation \
            or row["last_settled_seconds"] != outcome.settled_seconds:
        raise AssertionError(f"A DB终态不符 {row}")

    record["supervisor_after"] = pid_state(api, outcome.manager_pid, outcome.manager_created_100ns)
    if record["supervisor_after"]["alive"]:
        raise AssertionError("A SUP进程未退出")
    record["worker_after"] = pid_state(api, outcome.pid)
    record["pass"] = True
    return record


def scenario_b(base_dsn: str, api) -> dict:
    activity_id = str(uuid4())
    run_tag = "d1-09b-" + uuid4().hex[:8]
    schema, scoped = prepare_schema(base_dsn, "b")
    build_activity(scoped, activity_id)
    record = {"scenario": "b", "run_tag": run_tag, "activity_id": activity_id, "schema": schema,
              "parent": {"pid": os.getpid(), "created_100ns": self_created_100ns(api)}}
    trigger = DeadlineTrigger(scoped, activity_id)
    real_wait = launcher_module._SuspendedSupervisor.wait

    def injected_wait(self, seconds):
        if seconds <= 0 or trigger.fired:  # wait(0)是terminate内部探测，保持真实语义。
            return real_wait(self, seconds)
        waited = 0.0
        while waited < seconds:
            if real_wait(self, 0):
                return True  # SUP先行退出（异常路径），交回真实结果语义。
            if trigger.try_trigger():
                return False  # 确定性触发：业务Job在管，父级管理截止此刻到达。
            time.sleep(0.03)
            waited += 0.03
        return real_wait(self, 0)

    launcher_module._SuspendedSupervisor.wait = injected_wait
    started = time.monotonic()
    try:
        outcome = run_supervised_window(
            PostgresAdmissionLedger(scoped), CONFIG, activity_id, f"worker-{run_tag}",
            WorkerCommand(), run_tag=run_tag,
        )
    finally:
        launcher_module._SuspendedSupervisor.wait = real_wait
        if sys.exc_info()[0] is not None:
            _emergency_job_cleanup(trigger)  # spawn/终止异常路径：不留控制者持有的Job对象。
    record["wall_seconds"] = round(time.monotonic() - started, 3)
    record["outcome"] = asdict(outcome)
    record["trigger"] = {"fired": trigger.fired, "generation": trigger.generation}
    if not trigger.fired or trigger.generation is None:
        raise AssertionError("B 确定性触发未发生（SUP未在管理窗内创建业务Job）")

    if outcome.state != "manager_timeout_unconfirmed":
        raise AssertionError(f"B state={outcome.state}")
    if not (outcome.settled_seconds is None and outcome.reserved_seconds is None
            and outcome.pending_fold_seconds is None):
        raise AssertionError("B 无可信子结果时应为None账目")
    if not outcome.cleanup_incomplete:
        raise AssertionError("B cleanup_incomplete应为True")
    if outcome.manager_pid is None or not outcome.manager_created_100ns:
        raise AssertionError("B SUP身份缺失")

    job = trigger.job
    assert job is not None
    try:
        record["job_after_sup_exit"] = {
            "job_name": job.name,
            "active_processes": job.active_processes(),
            "pids": workers_of(api, query_job_pids(api, job.handle)["pids"]),
        }
        # 控制者确切收尾：终止整树→确认空→关句柄。对象因控制者句柄而存活至今。
        job.terminate()
        if not job.wait_empty_until(time.monotonic_ns() + 10_000_000_000):
            raise AssertionError("B 控制者无法确认业务Job整树为空")
        record["job_after_sup_exit"]["active_after_controller_terminate"] = job.active_processes()
    finally:
        try:
            job.close()
        finally:
            trigger.release_handle()

    record["supervisor_after"] = pid_state(api, outcome.manager_pid, outcome.manager_created_100ns)
    if record["supervisor_after"]["alive"]:
        raise AssertionError("B SUP进程未在管理截止路径内被终止")
    row = db_row(scoped, """SELECT status, execution_generation, running_reserved_seconds,
                                   running_settled_seconds, dispatch_closed, executor_id,
                                   lease_expires_at FROM activities WHERE id=%s""", (activity_id,))
    record["db_after"] = row
    if row["status"] != "running" or row["running_reserved_seconds"] != CONFIG.window_seconds \
            or row["running_settled_seconds"] != 0 or row["dispatch_closed"] is not False \
            or row["execution_generation"] != trigger.generation or row["lease_expires_at"] is None:
        raise AssertionError(f"B DB应保留保守预扣（不退款） {row}")
    record["pass"] = True
    return record


def _emergency_job_cleanup(trigger: DeadlineTrigger) -> None:
    """B场景失败路径：控制者仍持业务Job句柄时必须自行收尾，不留给进程死亡语义。"""
    if trigger.job is None:
        return
    try:
        trigger.job.terminate()
        trigger.job.wait_empty_until(time.monotonic_ns() + 5_000_000_000)
    except BaseException:
        pass
    finally:
        trigger.release_handle()


def _read_pre_resume(records: list[dict], mode: str) -> dict:
    for item in records:
        if item.get("phase") == "pre_resume" and item.get("mode") == mode:
            return item
    raise AssertionError(f"{mode} 未收到pre_resume屏障记录")


def scenario_c(base_dsn: str, api, mode: str) -> dict:
    activity_id = str(uuid4())
    run_tag = f"d1-09{mode}-" + uuid4().hex[:8]
    schema, scoped = prepare_schema(base_dsn, mode)
    build_activity(scoped, activity_id)
    g0 = db_row(scoped, "SELECT execution_generation, status FROM activities WHERE id=%s", (activity_id,))
    record = {"scenario": mode, "run_tag": run_tag, "activity_id": activity_id, "schema": schema,
              "pre_claim": g0}
    if g0["status"] != "pending":
        raise AssertionError(f"{mode} 前置状态非pending")

    sup_holder: dict = {}
    proc = PProcess(mode, activity_id, run_tag, schema, base_dsn, api)
    try:
        if not proc.wait_barrier(10.0):
            raise AssertionError(f"{mode} 10秒内未收到P屏障信号")
        records = proc.read_evidence()
        record["p_evidence"] = records
        pre = _read_pre_resume(records, mode)
        if pre["activity_id"] != activity_id or pre["run_tag"] != run_tag:
            raise AssertionError(f"{mode} P屏障身份不匹配")
        sup_pid, sup_created = pre["supervisor_pid"], pre["supervisor_created_100ns"]
        mapping_name = pre["mapping_name"]
        if not sup_pid or not sup_created or not mapping_name:
            raise AssertionError(f"{mode} P屏障SUP/映射身份缺失")
        sup_holder["pid"] = sup_pid
        sup_holder["created"] = sup_created
        proc.open_handles(pre["python_pid"])
        record["p_handles"] = [{k: v for k, v in h.items() if k != "handle"} for h in proc.handles]

        if mode == "c1":
            # c1：P在resume边界（SUP仍悬停未运行）即被精确终止。
            record["p_kill"] = proc.kill()
            for item in record["p_kill"]["terminated"]:
                if not item["dead"]:
                    raise AssertionError(f"{mode} P进程终止未确认 {item}")
            sup_state = pid_state(api, sup_pid, sup_created)
            record["supervisor_at_parent_death"] = sup_state
            if not sup_state["open"] or sup_state["created_matches"] is not True:
                raise AssertionError(f"{mode} SUP精确身份不可核验 {sup_state}")
            if not sup_state["alive"]:
                raise AssertionError("c1 SUP应在父死亡后保持悬停")
            row = db_row(scoped, "SELECT status, execution_generation, running_reserved_seconds,"
                                 " running_settled_seconds, dispatch_closed FROM activities WHERE id=%s",
                         (activity_id,))
            record["db_after_parent_death"] = row
            if row["status"] != "pending" or row["running_reserved_seconds"] != 0 \
                    or row["dispatch_closed"] is not False:
                raise AssertionError(f"c1 悬停期不应有认领/开门 {row}")
            for generation in (g0["execution_generation"], g0["execution_generation"] + 1):
                try:
                    NamedJob.open_existing(activity_id, generation).close()
                    raise AssertionError(f"c1 业务Job不应存在 G{generation}")
                except JobUnknown:
                    pass
            record["no_job_objects"] = True
            time.sleep(2.0)  # 有界负观察：悬停SUP既不自行Resume也不产生任何DB副作用。
            sup_state2 = pid_state(api, sup_pid, sup_created)
            record["supervisor_after_hover"] = sup_state2
            if not sup_state2["open"] or not sup_state2["alive"] or not sup_state2["created_matches"]:
                raise AssertionError("c1 悬停观察期SUP状态变化")
            handle = open_pid(api, sup_pid, PROCESS_QUERY_LIMITED | SYNCHRONIZE | PROCESS_TERMINATE)
            if not handle:
                raise AssertionError("c1 终止前SUP精确句柄不可得")
            try:
                if created_100ns(api, handle) != sup_created:
                    raise AssertionError("c1 终止前SUP创建时间不匹配")
                if not terminate_and_wait(api, handle, 5.0):
                    raise AssertionError("c1 悬停SUP终止未确认")
            finally:
                api.CloseHandle(handle)
            record["hover_cleanup"] = "terminated_by_controller"
            try:
                NamedMapping.open_existing(mapping_name)
                raise AssertionError("c1 SUP映射应在全部句柄关闭后销毁")
            except Exception:
                record["mapping_destroyed"] = True
            row = db_row(scoped, "SELECT status, execution_generation FROM activities WHERE id=%s",
                         (activity_id,))
            record["db_final"] = row
            if row["status"] != "pending":
                raise AssertionError("c1 最终DB状态应仍为pending")
            record["pass"] = True
            return record

        # c2：P的屏障事件在resume时即置位（父端wait在resume后立即进入，先于子端
        # 认领完成）；故at_wait之后还需等待SUP真实认领且业务Job中出现worker（有界
        # 10秒轮询，触发条件全部是真实可观察事实），再观察mid-flight并终止P。
        at_wait_deadline = time.monotonic() + 10.0
        at_wait_seen = False
        while time.monotonic() < at_wait_deadline:
            if any(item.get("phase") == "at_wait" for item in proc.read_evidence()):
                at_wait_seen = True
                break
            time.sleep(0.05)
        record["p_evidence"] = proc.read_evidence()
        if not at_wait_seen:
            raise AssertionError("c2 10秒内未到达主等待屏障（SUP未认领/未创建Job）")
        claim_deadline = time.monotonic() + 10.0
        mid = None
        job = None
        while time.monotonic() < claim_deadline:
            row = db_row(scoped, "SELECT execution_generation, status FROM activities WHERE id=%s",
                         (activity_id,))
            if row and row["status"] == "running":
                try:
                    candidate = NamedJob.open_existing(activity_id, row["execution_generation"])
                except JobUnknown:
                    time.sleep(0.03)  # Job尚未创建（claim与create之间的毫秒级间隙）。
                    continue
                try:
                    if candidate.active_processes() <= 0:
                        time.sleep(0.03)  # Job已建但worker尚未spawn（毫秒级间隙）。
                        continue
                    mid = row
                    job = candidate
                    break
                finally:
                    if job is None:
                        candidate.close()
            time.sleep(0.03)
        if mid is None or job is None:
            raise AssertionError(f"c2 10秒内SUP未认领或业务Job中无worker（最后状态 {row}）")
        record["db_at_parent_death"] = mid
        try:
            active_mid = job.active_processes()
            listing = query_job_pids(api, job.handle)
        finally:
            job.close()
        if active_mid <= 0:
            raise AssertionError("c2 父死亡时业务Job应仍有进程")
        record["mid_flight"] = {"generation": mid["execution_generation"], "active": active_mid,
                                "workers": workers_of(api, listing["pids"])}

        record["p_kill"] = proc.kill()
        for item in record["p_kill"]["terminated"]:
            if not item["dead"]:
                raise AssertionError(f"{mode} P进程终止未确认 {item}")
        sup_state = pid_state(api, sup_pid, sup_created)
        record["supervisor_at_parent_death"] = sup_state
        if not sup_state["open"] or sup_state["created_matches"] is not True:
            raise AssertionError(f"{mode} SUP精确身份不可核验 {sup_state}")
        if not sup_state["alive"]:
            raise AssertionError("c2 父死亡时SUP应仍存活")

        # 已运行SUP独立遵守自身截止与映射生命周期；控制者有界等待其自然退出。
        sup_handle = open_pid(api, sup_pid, PROCESS_QUERY_LIMITED | SYNCHRONIZE | PROCESS_TERMINATE)
        if not sup_handle:
            raise AssertionError("c2 SUP句柄不可得")
        exited = False
        try:
            exited = api.WaitForSingleObject(sup_handle, int(25.0 * 1000)) == WAIT_OBJECT_0
        finally:
            if not exited:
                terminate_and_wait(api, sup_handle, 5.0)  # 兜底精确终止（预期不触发）。
            api.CloseHandle(sup_handle)
        record["supervisor_self_exit"] = exited
        if not exited:
            record["supervisor_fallback_cleanup"] = True

        row = db_row(scoped, """SELECT status, execution_generation, running_reserved_seconds,
                                       running_settled_seconds, dispatch_closed,
                                       last_settled_generation FROM activities WHERE id=%s""",
                     (activity_id,))
        record["db_final"] = row
        if row["status"] != "pending" or row["running_reserved_seconds"] != 0 \
                or row["running_settled_seconds"] < 1 or row["dispatch_closed"] is not True \
                or row["last_settled_generation"] != mid["execution_generation"] \
                or row["execution_generation"] != mid["execution_generation"] + 1:
            raise AssertionError(f"c2 SUP应独立完成结算 {row}")
        try:
            NamedJob.open_existing(activity_id, mid["execution_generation"]).close()
            raise AssertionError("c2 业务Job对象应在SUP收尾后销毁")
        except JobUnknown:
            record["job_object_destroyed"] = True
        try:
            NamedMapping.open_existing(mapping_name)
            raise AssertionError("c2 SUP映射应随父/SUP句柄关闭而销毁")
        except Exception:
            record["mapping_destroyed"] = True
        residue = [pid_state(api, w["pid"], w.get("created_100ns")) for w in record["mid_flight"]["workers"]]
        record["worker_residue"] = residue
        # created_matches=False意味着PID已被无关进程复用，不计为残留。
        if any(item["alive"] and item.get("created_matches") is not False for item in residue):
            raise AssertionError("c2 worker进程残留")
        record["pass"] = True
        return record
    finally:
        # 失败路径安全网：SUP身份已知且仍存活时按精确PID+创建时间终止（正常路径
        # 中SUP已由控制者终止（c1）或自行退出（c2），此网不触发）。
        if sup_holder.get("pid"):
            try:
                state = pid_state(api, sup_holder["pid"], sup_holder["created"])
                if state.get("open") and state.get("alive") and state.get("created_matches"):
                    handle = open_pid(api, sup_holder["pid"],
                                      PROCESS_QUERY_LIMITED | SYNCHRONIZE | PROCESS_TERMINATE)
                    if handle:
                        try:
                            terminate_and_wait(api, handle, 5.0)
                        finally:
                            api.CloseHandle(handle)
                        record["supervisor_emergency_cleanup"] = True
            except BaseException:
                pass
        proc.close()


# ---------------------------------------------------------------- 批入口

def main() -> int:
    dsn = os.environ.pop("RETROLUME_TASK_083_D1_DATABASE_URL", "")
    if not dsn:
        log({"event": "blocked", "reason": "DSN missing"})
        return 2
    requested = [a.lower() for a in sys.argv[1:]] or list(SCENARIOS)
    unknown = [item for item in requested if item not in SCENARIOS]
    if unknown:
        log({"event": "blocked", "reason": f"unknown scenarios {unknown}"})
        return 2
    EVID.mkdir(parents=True, exist_ok=True)
    api = kernel_api()

    info = conninfo_to_dict(dsn)
    started_at = datetime.now(timezone.utc).isoformat()
    hashes_pre = hash_all()
    drift_since_job07 = {k: v for k, v in hashes_pre.items()
                         if k in JOB07_REFERENCES and JOB07_REFERENCES[k] != v}
    log({"event": "identity", "db": info.get("dbname"), "user": info.get("user"),
         "hash_drift_since_job07": drift_since_job07})
    if drift_since_job07:
        log({"event": "blocked", "reason": "frozen chain drifted since job-run-07; investigate first"})
        return 2
    with psycopg.connect(dsn, connect_timeout=5) as conn:
        identity = conn.execute(
            "SELECT current_database(), current_user, inet_server_port()").fetchone()
    identity_ok = tuple(identity) == (info.get("dbname"), info.get("user"), 5432)
    log({"event": "pg_identity", "ok": identity_ok, "row": list(identity)})
    if not identity_ok:
        return 2

    results = {"run_base": started_at, "config": asdict(CONFIG),
               "manager_total_seconds": CONFIG.manager_total_seconds,
               "scenarios": [], "all_pass": False}
    for name in requested:
        remaining_s = (BATCH_DEADLINE_NS - time.monotonic_ns()) / 1e9
        if remaining_s <= 60:
            log({"event": "batch_deadline", "scenario": name})
            break
        log({"event": "scenario_start", "scenario": name, "budget_left": round(remaining_s, 1)})
        try:
            if name == "a":
                record = scenario_a(dsn, api)
            elif name == "b":
                record = scenario_b(dsn, api)
            else:
                record = scenario_c(dsn, api, name)
        except BaseException as exc:
            log({"event": "scenario_stop_batch", "scenario": name,
                 "error_type": type(exc).__name__, "detail": str(exc)[:400]})
            results["scenarios"].append({"scenario": name, "pass": False,
                                         "error_type": type(exc).__name__, "detail": str(exc)[:400]})
            break
        results["scenarios"].append(record)
        log({"event": "scenario_done", "scenario": name, "pass": True})

    hashes_post = hash_all()
    results["hash_drift_in_batch"] = {k: [hashes_pre.get(k), hashes_post.get(k)]
                                      for k in HASH_FILES if hashes_pre.get(k) != hashes_post.get(k)}
    results["all_pass"] = (not results["hash_drift_in_batch"]) and all(
        item.get("pass") for item in results["scenarios"]) and len(
        results["scenarios"]) == len(requested)
    out = EVID / "results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    log({"event": "batch_done", "all_pass": results["all_pass"],
         "drift": results["hash_drift_in_batch"],
         "results_path": str(out)})
    return 0 if results["all_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
