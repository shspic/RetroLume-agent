# TASK-083 launcher-complete-09 静态预检批（1/3命令批）：py_compile、导入、
# SessionConfig 校验、launcher 调用边界文本核对（P补丁点/控制者注入点）。
import json
import py_compile
import re
import sys
from pathlib import Path

BACKEND = Path(r"D:/shspic/project_NO3_RetroLume-agent/backend")
FIX = BACKEND / "tests/fixtures/task083"
results = {}

# 1) 编译
for name in ("launcher_control.py", "launcher_scenario.py"):
    py_compile.compile(str(FIX / name), doraise=True)
    results[f"compile:{name}"] = "OK"

# 2) 导入（无副作用；main有__main__守卫）
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "tests"))
import fixtures.task083.launcher_control as lc
import fixtures.task083.launcher_scenario as ls
results["imports"] = "OK"

# 3) 配置校验（两份CONFIG一致且满足SessionConfig不变量）
c, s = lc.CONFIG, ls.CONFIG
assert c.window_seconds == 6 and s.window_seconds == 6
assert abs(c.manager_total_seconds - 16.0) < 1e-9
assert abs(s.manager_total_seconds - 16.0) < 1e-9
assert c.window_seconds > c.startup_limit_seconds + c.request_timeout_seconds + c.stop_grace_seconds
assert c.manager_overhead_seconds > c.mutex_wait_seconds + 3 * c.manager_db_timeout_seconds + c.cleanup_seconds
results["config"] = {"window": c.window_seconds, "manager_total": c.manager_total_seconds}

# 4) launcher 调用边界文本核对（补丁点真实存在且语义匹配）
launcher_src = (BACKEND / "app/worker/launcher.py").read_text(encoding="utf-8")
ipc_src = (BACKEND / "app/worker/supervisor_ipc.py").read_text(encoding="utf-8")
checks = {
    "main_wait_bounded": "process.wait(_remaining(run_deadline_ns))" in launcher_src,
    "terminate_probe_wait0": "if not self.wait(0)" in launcher_src,
    "sup_exit_wait": "exited = process.wait(_remaining(deadline_ns))" in launcher_src,
    "mapping_create_call": "mapping = NamedMapping.create(mapping_name)" in launcher_src,
    "resume_call": "process.resume()" in launcher_src,
    "outcome_none_account": "settled_seconds=None,reserved_seconds=None,pending_fold_seconds=None" in launcher_src.replace(" ", ""),
}
results["launcher_text"] = checks
assert all(checks.values()), checks
assert "_MAPPING_NAME" in ipc_src and "MAP_SIZE = 16_384" in ipc_src and "RetroLume" in ipc_src

# 5) 结果/字段形状核对
assert len(lc.HASH_FILES) == 19
assert callable(lc.scenario_a) and callable(lc.scenario_b) and callable(lc.scenario_c)
from app.worker.session import SessionOutcome
assert len(SessionOutcome.__dataclass_fields__) == 17  # 与asdict(outcome)形状一致
print(json.dumps(results, ensure_ascii=False))
