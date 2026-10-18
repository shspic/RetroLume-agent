from pathlib import Path
def edit(path,replacements):
 p=Path(path); raw=p.read_bytes(); bom=b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""; s=raw[len(bom):].decode("utf-8").replace("\r\n","\n")
 for a,b in replacements:
  if s.count(a)!=1: raise RuntimeError((path,s.count(a),a[:70]))
  s=s.replace(a,b,1)
 p.write_bytes(bom+s.replace("\n","\r\n").encode("utf-8") if b"\r\n" in raw else bom+s.encode("utf-8"))
edit("backend/tests/test_worker_session.py",[
 ('return WindowSnapshot("running" if self.old_running else "pending", 1 if self.old_running else 0, 6 if self.old_running else 0, False)', 'return WindowSnapshot("running" if self.old_running else "pending", 1 if self.old_running else 0, 6 if self.old_running else 0, False, 1 if self.old_running else None, self.old_running, True)'),
 ('async def claim_lease(self, activity_id, executor_id, *, lease_seconds, window_seconds):', 'async def claim_lease(self, activity_id, executor_id, *, lease_seconds, window_seconds, running_owner_session_id=None, expected_previous_generation=None):'),
 ('datetime.now(timezone.utc) + timedelta(seconds=window_seconds), self.window,\n', 'datetime.now(timezone.utc) + timedelta(seconds=window_seconds), self.window,\n            running_owner_session_id,\n'),
 ('return SessionConfig(window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1, startup_limit_seconds=2)', 'return SessionConfig(window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1, startup_limit_seconds=2, single_host_single_session_recovery=True)'),
 ('with patch("app.worker.session.ActivityMutex", Owner), patch("app.worker.session.NamedJob.create", side_effect=AssertionError("unexpected spawn")):', 'with patch("app.worker.session.current_process_session_id", return_value=1), patch("app.worker.session.ActivityMutex", Owner), patch("app.worker.session.NamedJob.create", side_effect=AssertionError("unexpected spawn")):'),
 ('with patch("app.worker.session.ActivityMutex", Owner), patch("app.worker.session.NamedJob.open_existing", side_effect=JobUnknown("unknown")):', 'with patch("app.worker.session.current_process_session_id", return_value=1), patch("app.worker.session.ActivityMutex", Owner), patch("app.worker.session.NamedJob.open_existing", side_effect=JobUnknown("unknown")):'),
])
edit("backend/tests/fixtures/task083/offline_unit.py",[
 ('async def claim_lease(self, activity_id, executor_id, *, lease_seconds, window_seconds):', 'async def claim_lease(self, activity_id, executor_id, *, lease_seconds, window_seconds, running_owner_session_id=None, expected_previous_generation=None):'),
 ('datetime.now(timezone.utc) + timedelta(seconds=6), self.window)', 'datetime.now(timezone.utc) + timedelta(seconds=6), self.window, running_owner_session_id)'),
 ('with patch("app.worker.session.ActivityMutex", owner), patch(', 'with patch("app.worker.session.current_process_session_id", return_value=1), patch("app.worker.session.ActivityMutex", owner), patch('),
])
