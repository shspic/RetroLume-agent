"""真实批前离线检查，只编译/读AST，不执行被检查runner。"""
from pathlib import Path
import ast
import json
import time

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "Ndocu/evidence/task-089"
started = time.monotonic()
here = Path(__file__).resolve().parent
sources = {p.name: p.read_text(encoding="utf-8") for p in here.glob("*.py")}
for name, source in sources.items(): compile(source, name, "exec")
tree = ast.parse(sources["real_batch.py"])
verbs = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "docker":
        arg = node.args[0]
        if isinstance(arg, ast.List):
            verb = ast.literal_eval(arg.elts[0])
            assert verb in ("inspect", "start", "exec", "stop")
            verbs.append(verb)
source = sources["real_batch.py"]
assert 'len(budget["real_attempts"])' in source and 'budget["real_attempts"].append' in source
assert 'child.stop(deadline - 30)' in source and 'state["outer_tree_zero"] = child.active() == 0' in source
assert '"stop", "--time", "10", CID' in source and 'state["container_stopped"]' in source
assert 'input_text=f"CREATE ROLE' in source and 'env["RETROLUME_ACTIVITY_RESULTS_TEST_DATABASE_URL"] = dsn' in source
assert 'write(folder / "manifest.json", state)' in source
assert "Config.Env" not in source
compatibility = {}
for name in ("test_activity_ledger.py", "test_activity_recovery.py", "test_activity_time_budget.py"):
    old = ROOT / "Ndocu/evidence/task-088/pre" / ("backend__tests__" + name)
    now = ROOT / "backend/tests" / name
    compatibility[name] = old.read_text(encoding="utf-8") == now.read_text(encoding="utf-8")
assert all(compatibility.values())
result = {"compile_count": len(sources), "docker_literal_verbs": verbs,
          "no_create_run_volume_create": True, "single_budget_ledger": True,
          "precise_cleanup_and_credentials_static_review": True,
          "legacy_tests_restored_to_088_pre": compatibility,
          "boundary": "static inspection only; not dynamic timeout or database proof",
          "seconds": time.monotonic() - started}
(EVIDENCE / "runner-static-check.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
budget_path = EVIDENCE / "budget-manifest.json"
budget = json.loads(budget_path.read_text(encoding="utf-8-sig"))
budget["offline_used_seconds"] += result["seconds"]
budget["offline_runs"].append({"path": "Ndocu/evidence/task-089/runner-static-check.json", "seconds": result["seconds"], "exit": 0})
budget_path.write_text(json.dumps(budget, indent=2), encoding="utf-8")
print(json.dumps(result))
