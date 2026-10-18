from pathlib import Path
p=Path("backend/app/worker/session.py"); raw=p.read_bytes(); bom=b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""; s=raw[len(bom):].decode("utf-8").replace("\r\n","\n")
def rep(a,b):
 global s
 if s.count(a)!=1: raise RuntimeError((s.count(a),a[:100]))
 s=s.replace(a,b,1)
rep('from .windows_job import ActivityMutex, JobUnknown, NamedJob, job_name', 'from .windows_job import (\n    ActivityMutex, ERROR_FILE_NOT_FOUND, JobOpenError, JobUnknown,\n    NamedJob, current_process_session_id, job_name,\n)')
rep('    async def claim_lease(self, activity_id: str, executor_id: str, *, lease_seconds: int, window_seconds: int) -> ActivityLease | None: ...', '    async def claim_lease(self, activity_id: str, executor_id: str, *, lease_seconds: int, window_seconds: int, running_owner_session_id: int | None = None, expected_previous_generation: int | None = None) -> ActivityLease | None: ...')
rep('    manager_overhead_seconds: float = 30.0\n', '    manager_overhead_seconds: float = 30.0\n    single_host_single_session_recovery: bool = False\n')
rep('    def __post_init__(self) -> None:\n        if type(self.window_seconds)', '    def __post_init__(self) -> None:\n        if type(self.single_host_single_session_recovery) is not bool:\n            raise ValueError("单主机单交互会话恢复部署声明须为布尔值")\n        if type(self.window_seconds)')
rep('        self._remaining(manager_deadline_ns)\n\n        config = self.config', '        self._remaining(manager_deadline_ns)\n        session_id = current_process_session_id()  # 生产 SUP 自身读取，失败不认领/恢复。\n\n        config = self.config')
rep('            if snapshot.status == "running":\n                old = NamedJob.open_existing(activity_id, snapshot.execution_generation)\n                old_failure: BaseException | None = None\n                try:\n                    old.terminate()\n                    old_deadline = min(manager_deadline_ns, time.monotonic_ns() + int(config.cleanup_seconds * 1e9))\n                    if not old.wait_empty_until(old_deadline):\n                        raise JobUnknown("旧Job整树未确认退出")\n                except BaseException as exc:\n                    old_failure = exc\n                try:\n                    old.close()\n                except BaseException as exc:\n                    if old_failure is None:\n                        old_failure = exc\n                    else:\n                        cleanup_errors.append(type(exc).__name__)\n                if old_failure is not None:\n                    raise old_failure',
'''            if snapshot.status == "running":
                # 部署声明仅是已配置的运维前提；numeric ID 不能证明同一主机。
                if not config.single_host_single_session_recovery:
                    raise JobUnknown("未配置单主机单交互会话恢复前提")
                if snapshot.running_owner_session_id is None or snapshot.running_owner_session_id != session_id:
                    raise JobUnknown("旧代次会话身份缺失或不匹配")
                if not snapshot.sources_valid or not snapshot.lease_recoverable:
                    raise JobUnknown("来源、截止或数据库租约不允许接续")
                try:
                    old = NamedJob.open_existing(activity_id, snapshot.execution_generation)
                except JobOpenError as exc:
                    if exc.code != ERROR_FILE_NOT_FOUND:
                        raise
                    old = None
                if old is not None:
                    old_failure: BaseException | None = None
                    try:
                        old.terminate()
                        old_deadline = min(manager_deadline_ns, time.monotonic_ns() + int(config.cleanup_seconds * 1e9))
                        if not old.wait_empty_until(old_deadline):
                            raise JobUnknown("旧Job整树未确认退出")
                    except BaseException as exc:
                        old_failure = exc
                    try:
                        old.close()
                    except BaseException as exc:
                        if old_failure is None:
                            old_failure = exc
                        else:
                            cleanup_errors.append(type(exc).__name__)
                    if old_failure is not None:
                        raise old_failure''')
rep('                window_seconds=config.window_seconds,\n            ), manager_deadline_ns)', '                window_seconds=config.window_seconds,\n                running_owner_session_id=session_id,\n                expected_previous_generation=(snapshot.execution_generation if snapshot.status == "running" else None),\n            ), manager_deadline_ns)')
rep('            window = lease.window_seconds\n', '            if lease.running_owner_session_id != session_id:\n                raise JobUnknown("新代次持久会话身份与 SUP 不一致")\n            window = lease.window_seconds\n')
p.write_bytes(bom+s.replace("\n","\r\n").encode("utf-8") if b"\r\n" in raw else bom+s.encode("utf-8"))
