"""097最终证据组装、只读资源核对和保存证明；不启动业务资源。"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from artifacts import ROOT, E, PY, append_event, digest, freeze, write


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main():
    start_ms = int(sys.argv[1])
    label = "offline-11-final-evidence"
    command = [str(PY), "-B", str(Path(__file__).resolve()), str(start_ms)]
    snapshot = freeze(label, command, "最终文件/起源链/计数一致性与精确资源只读核查；无容器start、应用、SUP、模型或浏览器启动")
    begin = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    processes = []
    for name, script, args in [
        ("freeze", E / "finalize.py", [str(start_ms)]),
        ("resources", E / "final_resources.py", []),
    ]:
        cmd = [str(PY), "-B", str(script), *args]
        before = time.monotonic()
        child = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=60)
        (snapshot / (name + ".stdout.bin")).write_bytes(child.stdout)
        (snapshot / (name + ".stderr.bin")).write_bytes(child.stderr)
        processes.append({"command": cmd, "exit_code": child.returncode, "seconds": time.monotonic() - before})
        if child.returncode:
            write(E / "closing-run.json", {"started_at": started, "processes": processes, "exit_code": child.returncode})
            append_event({"category": "offline", "label": label, "command": command,
                "seconds": time.monotonic() - begin, "exit_code": child.returncode})
            raise RuntimeError("最终证据子步骤失败，保留原始输出，不写通过证明")

    post = read(E / "post-manifest.json")
    current = {r["path"]: r for r in post}
    for row in post:
        assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
        assert digest(E / "final/files" / row["path"]) == row["sha256"], row["path"]
    applicability = []
    snapshot_files = 0
    imported_files = 0
    for folder in sorted((E / "as-run").iterdir()):
        p = folder / "manifest.json"
        if not p.is_file():
            continue
        manifest = read(p)
        original = {r["path"]: r for r in manifest["files"]}
        for row in manifest["files"]:
            assert digest(folder / "files" / row["path"]) == row["sha256"], (folder.name, row["path"])
            snapshot_files += 1
        changed = []
        same = []
        for path, row in original.items():
            final = current.get(path)
            if final and final["sha256"] == row["sha256"]:
                same.append(path)
            else:
                changed.append({"path": path, "observed_sha256": row["sha256"],
                    "final_sha256": None if final is None else final["sha256"],
                    "observed_bytes": str((folder / "files" / path).relative_to(ROOT)),
                    "final_bytes": None if final is None else "DocuN/evidence/TASK-097/final/files/" + path})
        applicability.append({"batch": folder.name, "manifest": str(p.relative_to(ROOT)),
            "identical_files": same, "different_files": changed,
            "absent_in_observed_snapshot": sorted(set(current) - set(original)),
            "meaning": "字节相同支持版本绑定；不同保留观察版本，不自动追认最终通过或使整批FAIL变绿"})
        runtime = E / folder.name
        if runtime.is_dir():
            for imports in runtime.glob("imports-*.json"):
                for module, row in read(imports).items():
                    assert row["path"] in original, (folder.name, module, row["path"])
                    assert original[row["path"]]["sha256"] == row["sha256"], (folder.name, module)
                    imported_files += 1
    write(E / "evidence-applicability.json", applicability)

    core = read(E / "core-freeze-check.json")
    assert core["all_existing_named_bodies_unchanged"]
    assert core["repository_existing_prefix_equal_after_CRLF_normalization"]
    assert all(r["unchanged"] for r in core["frozen_modules"])
    allowed = {r["path"] for r in read(E / "changes.json")}
    assert all(not r["changed"] or r["path"] in allowed for r in read(E / "post-index-check.json"))
    builds = read(E / "build-binding.json")
    final_build = builds["builds"][-1]
    assert final_build["label"] == "build-05-complete-inputs" and final_build["exit_code"] == 0
    for row in final_build["source_inputs"]:
        assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    assert {"frontend/index.html", "frontend/tsconfig.json"}.issubset({r["path"] for r in final_build["source_inputs"]})
    assert len(final_build["outputs"]) == 4
    for path, value in final_build["outputs"].items():
        assert digest(ROOT / path) == value, path
    assert final_build["outputs"] == builds["builds"][-2]["outputs"]
    for served in builds["browser_actual_served"]:
        for asset in served["assets"]:
            assert asset["served_sha256"] == asset["dist_sha256"]
    assert not builds["final_bundle_browser_served"]
    resources = read(E / "resources-final.json")
    assert resources["container"]["running"] is False and resources["container"]["pid"] == 0
    assert resources["tree_zero"] and all(v == "released" for v in resources["ports"].values())
    sup = read(E / "supervision-ledger.json")
    assert sup["actual_launch_attempts"] == 15
    assert len(sup["session_receipts"]) == 14 and sup["missing_session_outcome_count"] == 1
    assert len(sup["real_job_close"]) == 15
    assert all(r["active_processes_at_end"] == 0 for r in sup["session_receipts"])
    assert len(read(E / "integration-07-browser/browser-report.json")["checks"]) == 6
    assert len(read(E / "integration-08-browser/browser-report.json")["checks"]) == 1
    assert all(read(E / p / "run.json")["exit_code"] == 1 for p in [
        "integration-01-pg", "integration-02-pg", "integration-03-business", "integration-04-business",
        "integration-05-business", "integration-06-browser", "integration-07-browser", "integration-08-browser"])
    matrix = (E / "acceptance-matrix.md").read_text(encoding="utf-8")
    assert all(f"## T{i:02d} " in matrix for i in range(1, 19))

    # 核查阶段在秒表内，普通文档阅读/写入属于主动墙钟上界。
    elapsed = time.monotonic() - begin
    append_event({"category": "offline", "label": label, "command": command,
        "seconds": elapsed, "exit_code": 0, "scope": "原件/hash/版本导航及精确资源只读核查，非动态业务复验"})
    history = read(E / "attempt-ledger.json")
    budget = read(E / "budget-final.json")
    measured = sum(r.get("seconds", 0) for r in history)
    charged = measured + budget["offline_unmetered_consistency_charged_seconds"]
    budget["offline_measured_seconds"] = measured
    budget["offline_seconds"] = charged
    budget["frozen_at"] = datetime.now(timezone.utc).isoformat()
    budget["active_wall_upper_bound_seconds"] = time.time() - start_ms / 1000
    assert budget["entries"] == 8 and budget["container_starts"] == 8
    assert budget["active_wall_upper_bound_seconds"] < 28800 and charged < 2400
    assert elapsed < 60
    write(E / "budget-final.json", budget)
    state = read(E / "execution-ledger.json")
    state["budget_actual"] = budget
    write(E / "execution-ledger.json", state)

    result = ROOT / "DocuN/results/TASK-097-result.md"
    text = result.read_text(encoding="utf-8")
    values = {"FINAL_FILE_COUNT": len(post), "CHANGED_FILE_COUNT": len(read(E / "changes.json")),
        "ACTIVE_SECONDS": f"{budget['active_wall_upper_bound_seconds']:.3f}",
        "ACTIVE_REMAINING": f"{28800-budget['active_wall_upper_bound_seconds']:.3f}",
        "OFFLINE_MEASURED": f"{measured:.3f}", "OFFLINE_CHARGED": f"{charged:.3f}",
        "OFFLINE_REMAINING": f"{2400-charged:.3f}"}
    for name, value in values.items():
        text = text.replace("{{" + name + "}}", str(value))
    assert "{{" not in text
    result.write_text(text, encoding="utf-8")
    delivered = [result, E / "implementation-contract.md", E / "implementation-notes.md",
        E / "acceptance-matrix.md", E / "evidence-navigation.md"]
    links = []
    for document in delivered:
        for target in re.findall(r"\]\((D:/[^)]+)\)", document.read_text(encoding="utf-8")):
            if target.endswith("/delivery-proof.json"):
                continue
            assert Path(target).is_file(), (document.name, target)
            links.append(target)
    write(E / "closing-run.json", {"started_at": started, "ended_at": datetime.now(timezone.utc).isoformat(),
        "command": command, "processes": processes, "seconds": elapsed, "exit_code": 0,
        "scope": "保存/hash/导航和资源只读核查，不是新集成入口或行为测试"})
    (snapshot / "stdout.bin").write_text(json.dumps({"snapshot_files_verified": snapshot_files,
        "actual_import_records_bound": imported_files, "product_snapshot_files": len(post),
        "entries": 8, "starts": 8, "sup": 15, "candidate_verification": "partial",
        "exit_code": 0}, ensure_ascii=True) + "\n", encoding="utf-8")
    (snapshot / "stderr.bin").write_bytes(b"")
    write(snapshot / "run.json", {"exit_code": 0, "elapsed_seconds": elapsed,
        "scope": "evidence consistency only", "post_hashes": {r["path"]: digest(ROOT / r["path"]) for r in post}})
    write(E / "delivery-proof.json", {"at": datetime.now(timezone.utc).isoformat(), "exit_code": 0,
        "status": "partial_candidate_implementation", "documents_saved_and_readable": [
            {"path": str(p), "sha256": digest(p), "bytes": p.stat().st_size,
                "read_back_equal": p.read_text(encoding="utf-8").encode("utf-8") == p.read_bytes()} for p in delivered],
        "valid_absolute_links": len(links), "post_files_verified": len(post),
        "as_run_file_bytes_verified": snapshot_files, "actual_imports_bound_to_as_run": imported_files,
        "final_build": "build-05-complete-inputs", "final_bundle_browser_run": False,
        "resource_proof": {"path": str(E / "resources-final.json"), "sha256": digest(E / "resources-final.json")},
        "budget": budget, "independent_audit": "not performed; no self-signing"})
    print(json.dumps({"result": str(result), "sha256": digest(result), "bytes": result.stat().st_size,
        "saved_readable": True, "status": "partial_candidate_implementation", "offline_measured": round(measured, 3),
        "offline_charged": round(charged, 3), "active_wall_upper_bound": round(budget["active_wall_upper_bound_seconds"], 3),
        "snapshots_verified": snapshot_files, "imports_verified": imported_files}, ensure_ascii=True))


if __name__ == "__main__":
    main()
