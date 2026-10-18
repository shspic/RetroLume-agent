"""fixture-repair-04 最终离线批runner：单一计时来源time.perf_counter。

首命令失败即停止后续命令；无重试。日志按命令写入unit-final-0N.log（字节保真），
meta写入unit-final-meta.txt。runner本身不参与测试逻辑。
"""
import subprocess
import time
from pathlib import Path

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
EV = ROOT / "Ndocu/evidence/task-083/fixture-repair-04"
PY = ROOT / "backend/.venv/Scripts/python.exe"
COMMANDS = [
    [str(PY), "-B", str(ROOT / "backend/tests/fixtures/task083/focused_unit.py"),
     "EventControlTests.test_04_start_collision_closes_only_returned_handle",
     "EventControlTests.test_04_start_creation_error_and_new_handle",
     "StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt",
     "StartLifecycleTests.test_04_start_handle_release_exactly_once_on_failure",
     "LauncherTests.test_d1_deadline_before_resume_terminates_exact_owner"],
    [str(PY), "-B", str(ROOT / "backend/tests/fixtures/task083/offline_unit.py"),
     "OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry"],
]

meta = ["TASK-083 fixture-repair-04 final offline batch; single timing source time.perf_counter"]
total_start = time.perf_counter()
stopped_at = None
for index, command in enumerate(COMMANDS, 1):
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=str(ROOT), capture_output=True)
    elapsed = time.perf_counter() - started
    (EV / f"unit-final-0{index}.log").write_bytes(proc.stdout + proc.stderr)
    meta.append(f"command {index}: exit={proc.returncode} elapsed_seconds={elapsed:.7f}")
    meta.append(f"  cmd={command}")
    if proc.returncode != 0:
        stopped_at = index
        break
total = time.perf_counter() - total_start
meta.append(f"total_elapsed_seconds={total:.7f}")
meta.append(f"stopped_at_command={stopped_at}" if stopped_at is not None else "all_commands_passed")
(EV / "unit-final-meta.txt").write_text("\n".join(meta) + "\n", encoding="utf-8")
print("\n".join(meta))
