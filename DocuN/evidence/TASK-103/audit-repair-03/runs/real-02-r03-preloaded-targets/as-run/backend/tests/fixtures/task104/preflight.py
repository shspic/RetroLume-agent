"""只核本卡 fixture 的语法、路径、日期与实际接口，不运行产品测试。"""
import ast, datetime, json, subprocess, sys, time
from .common import ROOT, EVIDENCE, PERMIT, Control, command, write

def main():
    control = Control()
    control.reserve("fixture_offline", {"purpose": "104专用脚本一次语法/接口预检"})
    started = time.monotonic()
    output = {"permit": PERMIT, "product_tests": 0, "product_compile": 0, "browser_started": 0}
    try:
        assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date().isoformat() == "2026-10-07"
        owned = ROOT / "backend/tests/fixtures/task104"
        files = sorted(owned.glob("*.py"))
        for path in files:
            tree = ast.parse(path.read_text("utf-8-sig"))
            for node in ast.walk(tree):
                modules = [node.module or ""] if isinstance(node, ast.ImportFrom) else [x.name for x in node.names] if isinstance(node, ast.Import) else []
                assert not any(x.startswith("tests.fixtures.task103") for x in modules)
        node = command(["node", "--check", str(ROOT / "frontend/tests/task104-citation-audit.cjs")], timeout=control.remaining(120), cwd=ROOT / "frontend")
        output.update(node_exit=node.returncode, node_stderr=node.stderr, parsed_python_files=[str(x) for x in files])
        assert node.returncode == 0
        assert (ROOT / "frontend/node_modules/playwright/package.json").is_file()
        assert (ROOT / "frontend/dist/index.html").is_file()
        assert (ROOT / "DocuN/evidence/TASK-103/continuation-02/workspace/activity-config.json").is_file()
        output["status"] = "PASS"
    except Exception as exc:
        output.update(status="FAIL", error_type=type(exc).__name__, error=str(exc))
    finally:
        elapsed = time.monotonic() - started
        control.state["used"]["fixture_offline"] += elapsed
        control.state["events"].append({"kind": "fixture离线结果", "elapsed": elapsed, "status": output["status"]})
        control.save()
        output["elapsed_seconds"] = elapsed
        write(EVIDENCE / ("fixture-preflight-" + str(control.state["counts"]["fixture_offline"]) + ".json"), output)
    print(json.dumps(output, ensure_ascii=False))
    return 0 if output["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
