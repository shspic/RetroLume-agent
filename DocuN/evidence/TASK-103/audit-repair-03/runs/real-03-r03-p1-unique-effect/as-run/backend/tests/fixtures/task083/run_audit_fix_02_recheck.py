"""TASK-083 audit-fix-02 only tests affected by fixed interpreter path correction."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "tests"))

IDS = (
    "fixtures.task083.offline_unit.OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry",
    "fixtures.task083.offline_unit.OfflineRepairTests.test_06_timeout_or_cleanup_failure_never_refunds",
    "fixtures.task083.offline_unit.FixedEntryTests.test_12_fixed_command_and_injected_gateway_pass_through_gate",
)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromNames(IDS)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)

