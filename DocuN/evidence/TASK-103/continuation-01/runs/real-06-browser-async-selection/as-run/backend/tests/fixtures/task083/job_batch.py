"""Frozen future Job batch entry: all scenarios use an outer identity controller.

Do not invoke until an independent audit and a new run budget authorize it.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import time

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))

from fixtures.task083.job_control import verify_last_handle, verify_scenario


async def main() -> int:
    batch_deadline_ns = time.monotonic_ns() + 55_000_000_000
    fixture = Path(__file__).with_name("fixture.py")
    # 04 is last because its last-handle observation has no post-close Job query.
    for mode in ("01", "02", "03", "05", "04"):
        remaining = (batch_deadline_ns - time.monotonic_ns()) / 1e9
        if remaining <= 5:
            print(json.dumps({"mode": mode, "status": "batch_deadline", "cleanup_incomplete": True}), flush=True)
            return 2
        try:
            if mode == "04":
                result = await asyncio.wait_for(verify_last_handle(fixture, BACKEND), timeout=min(28, remaining - 5))
                if not result["worker_signaled_after_last_job_handle_closed"] or result["active_processes_before_supervisor_exit"] != 1:
                    raise AssertionError("last-handle fixture did not establish its bounded one-process observation")
            else:
                result = await asyncio.wait_for(verify_scenario(mode, BACKEND), timeout=min(28, remaining - 5))
                if result["cleanup_incomplete"] or result["active_processes_at_end"] != 0:
                    raise AssertionError("exact Job tree not confirmed empty")
            print(json.dumps({"mode": mode, "status": "observed", **result}), flush=True)
        except BaseException as exc:
            print(json.dumps({"mode": mode, "status": "stop_batch", "cleanup_incomplete": True,
                              "error_type": type(exc).__name__, "detail": str(exc)}), flush=True)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

