"""TASK-083 离线补足轮01的冻结测试选择；不做发现式搜索。"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "tests"))

IDS = (
    "fixtures.task083.offline_unit.OfflineRepairTests.test_01_command_data_rejects_callable_and_expired_manager_never_spawns",
    "fixtures.task083.offline_unit.OfflineRepairTests.test_02_partial_window_early_exit_reports_cleanup_failure_and_full_reservation",
    "fixtures.task083.offline_unit.OfflineRepairTests.test_03_cancellation_preserves_diagnostic_and_cleans_owner",
    "fixtures.task083.offline_unit.OfflineRepairTests.test_04_claim_response_lost_has_no_job_and_no_false_charge",
    "fixtures.task083.offline_unit.OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry",
    "fixtures.task083.offline_unit.OfflineRepairTests.test_06_timeout_or_cleanup_failure_never_refunds",
    "fixtures.task083.offline_unit.OfflineRepairTests.test_07_controlled_worker_gateway_chain_drains_marked_call",
    "fixtures.task083.offline_unit.LauncherUnitTests.test_08_fake_process_timeout_terminates_exact_owner_without_charge_claim",
    "test_worker_session.ProtocolUnitTests.test_claim_response_lost_and_partial_window_never_spawn",
    "test_worker_session.ProtocolUnitTests.test_unknown_old_job_fails_before_claim",
)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromNames(IDS)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
