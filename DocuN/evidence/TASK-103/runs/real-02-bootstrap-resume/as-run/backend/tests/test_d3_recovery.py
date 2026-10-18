"""TASK-083 D3 targeted offline recovery guards. No database or process creation."""
from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.activities import ActivityLedgerConflict, PostgresAdmissionLedger, WindowSnapshot
from app.worker.command import WorkerCommand
from app.worker.session import SessionConfig, SingleWindowSupervisor
from app.worker.windows_job import (
    ERROR_ACCESS_DENIED, ERROR_FILE_NOT_FOUND, JobOpenError, JobUnknown, NamedJob,
)


class Ledger:
    def __init__(self, snapshot, events, claim_error=None):
        self.snapshot, self.events, self.claim_error = snapshot, events, claim_error

    async def inspect_window(self, activity_id):
        self.events.append("inspect")
        return self.snapshot

    async def claim_lease(self, activity_id, executor_id, **kwargs):
        self.events.append(("claim", kwargs["running_owner_session_id"],
                            kwargs["expected_previous_generation"]))
        if self.claim_error:
            raise self.claim_error
        return None  # Exhausted: proves no new Job is created after the old G fold.


class Owner:
    events = None

    def __init__(self, *_args, **_kwargs):
        self.events.append("mutex_acquire")

    def close(self):
        self.events.append("mutex_release")


class OldJob:
    def __init__(self, events, *, wait_result=True, wait_error=None, close_error=None, terminate_error=None):
        self.events = events
        self.wait_result = wait_result
        self.wait_error = wait_error
        self.close_error = close_error
        self.terminate_error = terminate_error

    def terminate(self):
        self.events.append("terminate")
        if self.terminate_error:
            raise self.terminate_error

    def wait_empty_until(self, deadline_ns):
        self.events.append("tree_query")
        if self.wait_error:
            raise self.wait_error
        return self.wait_result

    def close(self):
        self.events.append("old_close")
        if self.close_error:
            raise self.close_error

class D3RecoveryGuards(unittest.IsolatedAsyncioTestCase):
    def config(self, enabled=True):
        return SessionConfig(
            window_seconds=6, request_timeout_seconds=.5, stop_grace_seconds=1,
            startup_limit_seconds=2, single_host_single_session_recovery=enabled,
        )

    async def run_case(self, snapshot, *, enabled=True, open_effect=None, claim_error=None, old_job_options=None):
        events = []
        Owner.events = events
        ledger = Ledger(snapshot, events, claim_error)
        def opening(*_args):
            events.append("open")
            if isinstance(open_effect, BaseException):
                raise open_effect
            return OldJob(events, **(old_job_options or {}))
        with patch("app.worker.session.current_process_session_id", return_value=7), patch(
            "app.worker.session.ActivityMutex", Owner
        ), patch("app.worker.session.NamedJob.open_existing", side_effect=opening), patch(
            "app.worker.session.NamedJob.create", side_effect=AssertionError("late spawn")
        ):
            outcome = await SingleWindowSupervisor(ledger, self.config(enabled)).run_once(
                str(uuid4()), "worker", WorkerCommand(), run_tag="d3-unit",
                manager_deadline_ns=time.monotonic_ns() + 20_000_000_000,
            )
        return outcome, events

    async def test_missing_mismatch_or_unconfigured_never_open_or_claim(self):
        baseline = WindowSnapshot("running", 1, 6, False, 7, True, True)
        for snapshot, enabled in (
            (baseline, False),
            (replace(baseline, running_owner_session_id=None), True),
            (replace(baseline, running_owner_session_id=8), True),
            (replace(baseline, lease_recoverable=False), True),
            (replace(baseline, sources_valid=False), True),
        ):
            outcome, events = await self.run_case(snapshot, enabled=enabled)
            self.assertEqual(outcome.state, "failed_closed")
            self.assertEqual(events, ["mutex_acquire", "inspect", "mutex_release"])

    async def test_only_file_not_found_allows_full_fold_claim(self):
        snapshot = WindowSnapshot("running", 4, 6, False, 7, True, True)
        outcome, events = await self.run_case(snapshot, open_effect=JobOpenError(ERROR_FILE_NOT_FOUND))
        self.assertEqual(outcome.state, "budget_exhausted")
        self.assertEqual(events, ["mutex_acquire", "inspect", "open",
                                  ("claim", 7, 4), "mutex_release"])

    async def test_access_and_other_open_errors_do_not_claim(self):
        snapshot = WindowSnapshot("running", 4, 6, False, 7, True, True)
        for code in (ERROR_ACCESS_DENIED, 87):
            outcome, events = await self.run_case(snapshot, open_effect=JobOpenError(code))
            self.assertEqual(outcome.state, "failed_closed")
            self.assertEqual(events, ["mutex_acquire", "inspect", "open", "mutex_release"])

    async def test_existing_job_zero_and_claim_commit_precede_mutex_release(self):
        snapshot = WindowSnapshot("running", 4, 6, False, 7, True, True)
        outcome, events = await self.run_case(snapshot)
        self.assertEqual(outcome.state, "budget_exhausted")
        self.assertEqual(events, ["mutex_acquire", "inspect", "open", "terminate",
                                  "tree_query", "old_close", ("claim", 7, 4), "mutex_release"])

    async def test_claim_response_lost_does_not_spawn_and_releases_mutex(self):
        snapshot = WindowSnapshot("running", 4, 6, False, 7, True, True)
        outcome, events = await self.run_case(
            snapshot, open_effect=JobOpenError(ERROR_FILE_NOT_FOUND),
            claim_error=TimeoutError("committed, response lost"),
        )
        self.assertEqual(outcome.state, "failed_closed")
        self.assertEqual(events[-2:], [("claim", 7, 4), "mutex_release"])


    async def test_running_refusal_reports_unknown_accounting_and_unconfirmed_tree(self):
        baseline = WindowSnapshot("running", 1, 6, False, 7, True, True)
        for snapshot, enabled in (
            (baseline, False),
            (replace(baseline, running_owner_session_id=None), True),
            (replace(baseline, running_owner_session_id=8), True),
            (replace(baseline, lease_recoverable=False), True),
            (replace(baseline, sources_valid=False), True),
        ):
            outcome, events = await self.run_case(snapshot, enabled=enabled)
            self.assertEqual(outcome.state, "failed_closed")
            self.assertTrue(outcome.cleanup_incomplete)
            self.assertEqual((outcome.settled_seconds, outcome.reserved_seconds, outcome.pending_fold_seconds), (None, None, None))
            self.assertEqual(events, ["mutex_acquire", "inspect", "mutex_release"])

    async def test_old_tree_failures_never_claim_or_report_clean(self):
        snapshot = WindowSnapshot("running", 4, 6, False, 7, True, True)
        for options in (
            {"terminate_error": JobUnknown("terminate")},
            {"wait_error": JobUnknown("query")},
            {"wait_result": False},
            {"close_error": JobUnknown("close")},
        ):
            with self.subTest(options=options):
                outcome, events = await self.run_case(snapshot, old_job_options=options)
                self.assertEqual(outcome.state, "failed_closed")
                self.assertTrue(outcome.cleanup_incomplete)
                self.assertEqual((outcome.settled_seconds, outcome.reserved_seconds, outcome.pending_fold_seconds), (None, None, None))
                self.assertNotIn("claim", [e[0] if isinstance(e, tuple) else e for e in events])
                self.assertNotIn("create", events)
                self.assertEqual(events[-1], "mutex_release")

    async def test_open_unknown_has_unconfirmed_tree_and_no_accounting(self):
        snapshot = WindowSnapshot("running", 4, 6, False, 7, True, True)
        for error in (JobOpenError(ERROR_ACCESS_DENIED), JobOpenError(87), JobUnknown("query")):
            with self.subTest(error=error):
                outcome, events = await self.run_case(snapshot, open_effect=error)
                self.assertTrue(outcome.cleanup_incomplete)
                self.assertEqual((outcome.settled_seconds, outcome.reserved_seconds, outcome.pending_fold_seconds), (None, None, None))
                self.assertEqual(events, ["mutex_acquire", "inspect", "open", "mutex_release"])
class D3ClockOrder(unittest.IsolatedAsyncioTestCase):
    async def _case(self, method):
        events = []
        sampled = datetime(2026, 9, 25, tzinfo=timezone.utc)
        class Clock:
            @staticmethod
            def now(tz):
                assert tz is timezone.utc
                events.append("clock")
                assert events[:3] == ["source_lock", "activity_select", "activity_fetch"]
                return sampled
        row = {
            "status": "pending", "execution_generation": 0, "running_reserved_seconds": 0,
            "running_settled_seconds": 0, "running_owner_session_id": None,
            "dispatch_closed": False, "lease_expires_at": sampled - timedelta(seconds=1),
            "deadline_at": sampled - timedelta(seconds=1) if method == "claim" else sampled + timedelta(seconds=1),
            "max_running_seconds": 6, "scope_revision": 1,
        }
        class Cursor:
            async def fetchone(self):
                events.append("activity_fetch")
                return row
        class Connection:
            async def execute(self, query, params):
                assert "FROM activities" in query and "FOR UPDATE" in query
                events.append("activity_select")
                return Cursor()
        async def source_lock(*args):
            events.append("source_lock")
            return True
        async def transact(operation):
            return await operation(Connection())
        ledger = PostgresAdmissionLedger("postgresql://unused")
        # G3 范围 CAS 起 claim/inspect 会对来源行做 scope 提示复核（_scope_key），
        # 假行需带 version_id/source_revision；不改变本用例的时钟顺序断言。
        fake_sources = [{"source_id": "synthetic", "version_id": "synthetic-version", "source_revision": 0}]
        with patch.object(ledger, "_source_rows", return_value=fake_sources), patch.object(
            ledger, "_lock_sources", side_effect=source_lock
        ), patch.object(ledger, "_transaction", side_effect=transact), patch(
            "app.activities.repository.datetime", Clock
        ):
            if method == "claim":
                with self.assertRaises(ActivityLedgerConflict):
                    await ledger.claim_lease(str(uuid4()), "worker", lease_seconds=6, window_seconds=6, running_owner_session_id=0)
            else:
                snapshot = await ledger.inspect_window(str(uuid4()))
                self.assertTrue(snapshot.lease_recoverable)
        self.assertEqual(events, ["source_lock", "activity_select", "activity_fetch", "clock"])

    async def test_claim_samples_after_both_locks(self):
        await self._case("claim")

    async def test_inspect_samples_after_both_locks(self):
        await self._case("inspect")

class WindowsOpenErrorTests(unittest.TestCase):
    def test_open_keeps_exact_code(self):
        import ctypes
        class Kernel:
            def __init__(self, code):
                self.code = code
            def OpenJobObjectW(self, *_args):
                ctypes.set_last_error(self.code)
                return 0
        for code in (2, 5, 87):
            with self.subTest(code=code), patch("app.worker.windows_job._kernel", return_value=Kernel(code)):
                with self.assertRaises(JobOpenError) as caught:
                    NamedJob.open_existing(str(uuid4()), 1)
                self.assertEqual(caught.exception.code, code)


if __name__ == "__main__":
    unittest.main(verbosity=2)
