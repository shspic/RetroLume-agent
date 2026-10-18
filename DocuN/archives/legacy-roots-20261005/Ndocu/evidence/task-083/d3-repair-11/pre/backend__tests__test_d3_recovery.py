"""TASK-083 D3 targeted offline recovery guards. No database or process creation."""
from __future__ import annotations

import asyncio
from dataclasses import replace
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.activities import WindowSnapshot
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
    def __init__(self, events):
        self.events = events

    def terminate(self):
        self.events.append("terminate")

    def wait_empty_until(self, deadline_ns):
        self.events.append("tree_zero")
        return True

    def close(self):
        self.events.append("old_close")


class D3RecoveryGuards(unittest.IsolatedAsyncioTestCase):
    def config(self, enabled=True):
        return SessionConfig(
            window_seconds=6, request_timeout_seconds=.5, stop_grace_seconds=1,
            startup_limit_seconds=2, single_host_single_session_recovery=enabled,
        )

    async def run_case(self, snapshot, *, enabled=True, open_effect=None, claim_error=None):
        events = []
        Owner.events = events
        ledger = Ledger(snapshot, events, claim_error)
        def opening(*_args):
            events.append("open")
            if isinstance(open_effect, BaseException):
                raise open_effect
            return OldJob(events)
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
                                  "tree_zero", "old_close", ("claim", 7, 4), "mutex_release"])

    async def test_claim_response_lost_does_not_spawn_and_releases_mutex(self):
        snapshot = WindowSnapshot("running", 4, 6, False, 7, True, True)
        outcome, events = await self.run_case(
            snapshot, open_effect=JobOpenError(ERROR_FILE_NOT_FOUND),
            claim_error=TimeoutError("committed, response lost"),
        )
        self.assertEqual(outcome.state, "failed_closed")
        self.assertEqual(events[-2:], [("claim", 7, 4), "mutex_release"])


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
