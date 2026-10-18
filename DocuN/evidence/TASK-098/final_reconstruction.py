"""只读重建原始身份/计数/浏览器层级，写098派生索引，不执行旧runner。"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time

from probe_support import HERE, ROOT, RUN, load, publish


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    old = ROOT / "DocuN/evidence/TASK-097"
    reconstruction = load(HERE / "static-reconstruction.json")
    original_input = load(old / "input-snapshot.json")
    entries = original_input["current_files"]
    if isinstance(entries, dict):
        entries = [{"path": path, "sha256": value if isinstance(value, str) else value["sha256"]} for path, value in entries.items()]
    preserved = []
    for item in entries:
        if item["path"].startswith("backend/migrations/") or item["path"] in ("backend/requirements.lock", "frontend/package-lock.json", "frontend/package.json"):
            actual = digest(ROOT / item["path"])
            preserved.append({**item, "actual": actual, "matches_original_input": actual == item["sha256"]})

    bindings = reconstruction["as_run_bindings"]
    selected = {}
    for path, value in bindings.items():
        if any(label in path for label in ("build-05-complete", "integration-02", "integration-05", "integration-09", "integration-10", "integration-11", "offline-02", "offline-03", "offline-05", "offline-07", "offline-09")):
            changed = [x["path"] for x in value["objects"] if not x["current_match"] and x["path"].startswith(("backend/app/", "frontend/src/"))]
            selected[path] = {"command": value["command"], "objects": len(value["objects"]),
                              "saved_bytes_all_match": all(x["saved_bytes_match"] for x in value["objects"]),
                              "product_differences_from_current": changed}

    old_attempts = []
    old_sessions = []
    created = {}
    imports = []
    browser_cases = []
    raw_entry_rows = []
    for folder in sorted(old.glob("integration-*")):
        if not folder.is_dir():
            continue
        run = load(folder / "run.json")
        attempts = []
        for path in sorted(folder.glob("sup-launch-*.json")):
            value = load(path)
            attempts.append({"source": path.relative_to(ROOT).as_posix(), **value})
            if value.get("created"):
                created[(value["pid"], value["created_100ns"])] = {"source": path.relative_to(ROOT).as_posix(), **value}
        old_attempts += attempts
        for path in sorted(folder.glob("sup-launch-*.tmp")):
            value = load(path)
            if value.get("created"):
                created[(value["pid"], value["created_100ns"])] = {"source": path.relative_to(ROOT).as_posix(), **value}
        sessions = [{"source": path.relative_to(ROOT).as_posix(), **load(path)} for path in folder.glob("session-*.json")]
        old_sessions += sessions
        resumed_by_boot = [identity for identity in created if (folder / f"boot-{identity[0]}.json").exists()]
        jobs = [{"source": p.relative_to(ROOT).as_posix(), **load(p)} for p in folder.glob("job-close-*.json")]
        raw_entry_rows.append({"directory": folder.relative_to(ROOT).as_posix(), "run": run,
                              "recorded_create_attempts": len(attempts), "session_outcomes": len(sessions),
                              "booted_created_SUP": len(resumed_by_boot), "job_close_records": jobs,
                              "browser_actual_start": (folder / "browser-actual-start.json").exists(),
                              "driver_attempt": (folder / "browser-launch.json").exists()})
        if folder.name in {"integration-09-combined", "integration-10-repair", "integration-11-ui-only"}:
            manifest_path = next(Path(ROOT).glob(f"DocuN/evidence/TASK-097/continuation-01/as-run/{folder.name}/manifest.json"))
            manifest = load(manifest_path)
            objects = manifest.get("objects", manifest.get("files", []))
            if isinstance(objects, dict):
                object_map = {path: value if isinstance(value, str) else value["sha256"] for path, value in objects.items()}
            else:
                object_map = {x["path"]: x["sha256"] for x in objects}
            for path in folder.glob("imports-*.json"):
                for module, facts in load(path).items():
                    if facts["path"].startswith("backend/app/"):
                        imports.append({"source": path.relative_to(ROOT).as_posix(), "module": module, **facts,
                                        "as_run_match": object_map.get(facts["path"]) == facts["sha256"],
                                        "current_match": digest(ROOT / facts["path"]) == facts["sha256"]})
            report = load(folder / "browser-report.json")
            for index, case in enumerate(report["cases"], 1):
                image = folder / f"{index}-{case['name']}.png"
                if case["status"] == "FAIL":
                    image = folder / f"{index}-{case['name']}-FAIL.png"
                browser_cases.append({"entry": folder.name, "report": (folder / "browser-report.json").relative_to(ROOT).as_posix(),
                    **case, "screenshot": image.relative_to(ROOT).as_posix() if image.exists() else None,
                    "screenshot_sha256": digest(image) if image.exists() else None,
                    "timeline_requests": len(report["requests"]), "has_completed_interval": "ended_at" in case})

    accepted = {}
    for case in browser_cases:
        if case["status"] == "PASS" and case["has_completed_interval"]:
            accepted[case["name"]] = case
    build = next(value for path, value in bindings.items() if "build-05-complete-inputs" in path)
    bundle = []
    for served in load(old / "integration-09-combined/served-bundle.json"):
        path = ROOT / "frontend/dist" / served["path"]
        browser_report = load(old / "integration-09-combined/browser-report.json")
        proven_case = next(c for c in browser_report["cases"] if c["name"] == "served_final_bundle")
        bundle.append({**served, "current_match": digest(path) == served["sha256"],
                       "browser_case_match": served in proven_case["actual"]})

    new_manifest = load(RUN / "as-run-manifest.json")
    new_map = {x["path"]: x["sha256"] for x in new_manifest["objects"]}
    new_imports = []
    for path in RUN.glob("import-*.json"):
        facts = load(path)
        new_imports.append({"source": path.name, **facts,
                            "as_run_match": new_map.get(facts["path"]) == facts["sha256"],
                            "current_match": digest(ROOT / facts["path"]) == facts["sha256"]})
    new_saved = [{"path": entry["path"], "saved_match": digest(RUN / "as-run/files" / entry["path"]) == entry["sha256"],
                  "current_match": digest(ROOT / entry["path"]) == entry["sha256"]} for entry in new_manifest["objects"]]
    prepared = sorted([load(p) for p in RUN.glob("candidate-prepared-*.json")], key=lambda x: x["monotonic_ns"])
    new_created = [load(p) for p in RUN.glob("sup-created-*.json")]
    new_resumed = [load(p) for p in RUN.glob("sup-resumed-*.json")]
    new_sessions = [load(p) for p in RUN.glob("session-*.json")]
    new_receipt_hash = load(RUN / "competition-checks.json")["payload_sha256"]
    old_ledger = load(old / "continuation-01/supervision-ledger.json")
    summaries = {
        "original_migrations_and_locks": preserved,
        "selected_as_run": selected,
        "old_entry_reconstruction": raw_entry_rows,
        "old_created_identities": list(created.values()),
        "old_SUP_counts": {"recorded_create_attempts": len(old_attempts), "actual_created_including_original_temp": len(created),
            "resumed_lower_bound_by_boot": sum(x["booted_created_SUP"] for x in raw_entry_rows),
            "job_close_records": sum(len(x["job_close_records"]) for x in raw_entry_rows),
            "session_outcomes": len(old_sessions), "session_claim_generation_records": sum(x["generation"] is not None for x in old_sessions),
            "pre_CreateProcess_observer_failure_extra": sum(x.get("error_type") == "JSONDecodeError" and x.get("manager_pid") is None for x in old_sessions),
            "created_before_resume_failure": sum(x.get("error_type") == "PermissionError" and x.get("manager_pid") is None for x in old_sessions),
            "old_missing_outcome_count_from_ledger": old_ledger["old_missing_outcome_count"],
            "creation_attempt_vs_observer_entry_note": "创建尝试23与09前置观察读取失败1分列；按进入create函数计至少24，不能把未调用CreateProcess称已创建"},
        "old_current_product_imports": imports,
        "build05_input_current_match": all(x["current_match"] for x in build["objects"]),
        "served_final_bundle": bundle,
        "all_browser_cases_preserving_failures": browser_cases,
        "accepted_browser_unique_count": len(accepted),
        "accepted_browser_cases": list(accepted.values()),
        "new_as_run_binding": new_saved,
        "new_import_binding": new_imports,
        "new_concurrency_summary": {"prepared": prepared, "created": new_created, "resumed": new_resumed,
            "sessions": [{k: s[k] for k in ("run_tag", "state", "generation", "job_name", "pid", "worker_created_100ns", "manager_pid", "manager_created_100ns", "active_processes_at_end", "settled_seconds", "reserved_seconds", "cleanup_incomplete")} for s in new_sessions],
            "winner_receipt_hash_matches_pg": any(s["model_receipt"] and s["model_receipt"]["result"]["payload_sha256"] == new_receipt_hash for s in new_sessions),
            "transport_records": len(list(RUN.glob("transport-*.json"))), "gate_close_records": [load(p) for p in RUN.glob("gate-closed-*.json")],
            "job_close_records": [load(p) for p in RUN.glob("job-closed-*.json")],
            "network_denied_dynamic_records": len(list(RUN.glob("network-denied-*.json"))),
            "old_business_matches_after_FK_cleanup": load(RUN / "old-business-after.json")["matches_baseline"]},
        "at": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": time.monotonic() - started,
        "new_business_entry": False, "new_browser": 0, "old_runner_executed": False}
    publish("evidence-reconstruction-final.json", summaries, HERE)
    print(json.dumps({"elapsed_seconds": summaries["elapsed_seconds"], "old_SUP_counts": summaries["old_SUP_counts"],
        "old_import_records": len(imports), "old_import_all_as_run_match": all(x["as_run_match"] for x in imports),
        "old_import_all_current_match": all(x["current_match"] for x in imports),
        "migrations_locks_unchanged": all(x["matches_original_input"] for x in preserved),
        "browser_unique": len(accepted), "build05_match": summaries["build05_input_current_match"],
        "bundle_match": all(x["current_match"] and x["browser_case_match"] for x in bundle),
        "new_saved_objects": len(new_saved), "new_saved_all_match": all(x["saved_match"] and x["current_match"] for x in new_saved),
        "new_import_records": len(new_imports), "new_import_all_match": all(x["as_run_match"] and x["current_match"] for x in new_imports)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
