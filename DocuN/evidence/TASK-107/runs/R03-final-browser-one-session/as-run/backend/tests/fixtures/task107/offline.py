"""一批仅107夹具的语法/ROOT/冻结接口检查，不导入产品。"""
import ast
import json
import pathlib
import subprocess
import sys
import time
from .common import ROOT, EVIDENCE, atomic_json, charge, checksum, initialize, reserve, state, utc


def main():
    initialize()
    name = "O" + str(state()["counts"]["offline_batch"] + 1).zfill(2) + "-task107-static-fixture"
    reserve("offline_batch", dict(name=name))
    start = time.monotonic(); outputs = []
    try:
        own = ROOT / "backend/tests/fixtures/task107"
        for file in own.rglob("*.py"):
            text = file.read_text(encoding="utf-8")
            ast.parse(text); compile(text, str(file), "exec")
            outputs.append(dict(path=str(file), sha256=checksum(file), fixture_compile_only=True))
        assert ROOT.resolve() == pathlib.Path(__file__).resolve().parents[4]
        plan = json.loads((EVIDENCE / "validation-plan.json").read_text(encoding="utf-8"))
        assert plan["root_plan"]["native_SUP"] <= 8 and plan["root_plan"]["transport_send"] <= 8
        public = json.loads((ROOT / "DocuN/evidence/TASK-106/continuation-01/synthetic/activity-normal.json").read_text(encoding="utf-8"))
        assert public["service"]["timeout_seconds"] <= 2 and public["interview"]["max_output_tokens"] == 512
        result = subprocess.run(["node", "--check", str(ROOT / "frontend/tests/task107-g10-final.mjs")], capture_output=True,
                                text=True, encoding="utf-8", timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            raise RuntimeError("107浏览器语法错误：" + result.stderr)
        record = dict(status="PASS", at=utc(), compiled_fixture_files=outputs, browser_syntax_only=True,
                      product_import_test_compile_build=False, root_model_schema_not_executed=True)
        atomic_json(EVIDENCE / (name + ".json"), record)
        print(json.dumps(dict(status="PASS", fixture_files=len(outputs), browser_syntax=True)))
        return 0
    except BaseException as error:
        atomic_json(EVIDENCE / (name + ".json"), dict(status="FAIL", at=utc(), error_type=type(error).__name__, message=str(error), files=outputs))
        raise
    finally:
        charge("offline", time.monotonic() - start, dict(name=name, per_batch_limit=180))


if __name__ == "__main__":
    sys.exit(main())
