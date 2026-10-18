from metadata import ROOT, OWN, check_deadline, identity, load, now, raw, save, sha

check_deadline()
base = ROOT / "DocuN/evidence/TASK-103/audit-repair-03"
incoming = load("DocuN/evidence/TASK-104/orchestration-review-02-20261007/review-input.json")
baseline = {x["path"]: x["sha256"] for x in load(base / "baseline-identities.json")}
current = incoming["current_files"]
old = load("DocuN/evidence/TASK-104/audit/initial-identity-check.json")
old_product = {str(__import__("pathlib").Path(x["path"]).relative_to(ROOT)).replace("\\", "/"): x["expected"]
               for x in old["checks"] if x["group"] == "current+complete-post"}
changes = {
    "changed": [p for p in baseline if p in current and baseline[p] != current[p]],
    "deleted": [p for p in baseline if p not in current],
    "added": [p for p in current if p not in baseline],
    "unchanged_count": sum(p in current and baseline[p] == current[p] for p in baseline),
    "original_104_product_baseline_count": len(old_product),
    "original_104_baseline_preserved": all(baseline.get(p) == h for p, h in old_product.items()),
}
changes["matches_card"] = (
    set(changes["changed"]) == {x["path"] for x in incoming["actual_changes"]["changed"]}
    and set(changes["deleted"]) == set(incoming["actual_changes"]["deleted"])
    and set(changes["added"]) == {x["path"] for x in incoming["actual_changes"]["added"]}
)
old_js = "frontend/dist/assets/index-D7dvfnOT.js"
changes["old_bundle_pre"] = identity(base / "pre" / old_js)
changes["old_bundle_pre_matches_baseline"] = sha(raw(base / "pre" / old_js)) == baseline[old_js]
save("baseline-inheritance-check.json", {"at": now(), **changes})

frontend = [p for p in current if p.startswith("frontend/src/")]
runs = []
for row in load(base / "final/runs-ledger.json"):
    execution = __import__("pathlib").Path(row["execution_path"])
    record = load(execution)
    before = {x["path"]: x for x in record["before"]}
    after = {x["path"]: x for x in record["after"]}
    failed = []
    for p, expected in before.items():
        actual = identity(execution.parent / "as-run" / p)
        if (actual["sha256"], actual["bytes"]) != (expected["sha256"], expected["bytes"]):
            failed.append({"path": p, "expected": expected, "actual": actual})
    source_match = all(p in before and p in after and before[p]["sha256"] == current[p]
                       and after[p]["sha256"] == current[p] for p in frontend)
    delta = [p for p in before.keys() | after.keys() if before.get(p) != after.get(p)]
    runs.append({
        "name": row["name"], "execution": identity(execution),
        "ledger_execution_sha_matches": sha(raw(execution)) == row["execution_sha256"],
        "actual_argv": record["argv"], "exit_code": record["exit_code"],
        "passed": record["passed"], "at": record["at"], "ended_at": record["ended_at"],
        "allowed_seconds": record["allowed_seconds"], "elapsed_seconds": record["elapsed_seconds"],
        "as_run_count": len(before), "as_run_mismatches": failed,
        "frontend_source_count": len(frontend), "frontend_source_matches_current": source_match,
        "actual_before_after_delta": delta,
        "stdout": identity(execution.parent / "stdout.txt"),
        "stderr": identity(execution.parent / "stderr.txt"),
        "changed_fixture_from_current": [p for p in before if p in current and before[p]["sha256"] != current[p]
                                         and (p.startswith("backend/tests/") or p.startswith("frontend/tests/"))],
    })

loaded = []
for group in ["real-01-r03-main", "real-02-r03-preloaded-targets", "real-03-r03-p1-unique-effect"]:
    result = load(base / "groups" / group / "browser/result.json")
    for entry in result["loaded"]:
        name = entry["path"].split("/")[-1]
        capture = identity(base / "groups" / group / "browser" / name)
        actual = identity(ROOT / "frontend/dist/assets" / name)
        loaded.append({"root": group, "browser_record": entry, "actual_capture": capture,
                       "current_dist": actual,
                       "all_three_match": capture["sha256"] == actual["sha256"] == entry["sha256"]
                       and capture["bytes"] == actual["bytes"] == entry["bytes"]})

js = raw("frontend/dist/assets/index-GgrE4smT.js").decode("utf-8")
needle = "保存已确认，读取期间的新输入仍保留，请核对版本。"
positions = []
start = 0
while True:
    pos = js.find(needle, start)
    if pos < 0:
        break
    positions.append({"offset": pos, "excerpt": js[max(0, pos-650):pos+950]})
    start = pos + len(needle)
save("new-bundle-guard-excerpts.json", {"identity": identity("frontend/dist/assets/index-GgrE4smT.js"),
                                         "matches": positions})
save("all-nine-run-and-loaded-bundle-binding.json", {
    "at": now(), "runs": runs, "actual_run_count": len(runs),
    "loaded": loaded, "complete_loaded_count": len(loaded),
    "all_source_and_as_run_match": all(x["frontend_source_matches_current"] and not x["as_run_mismatches"]
                                       and x["ledger_execution_sha_matches"] for x in runs),
    "all_loaded_match": all(x["all_three_match"] for x in loaded),
    "current_index": identity("frontend/dist/index.html"),
    "current_index_text": raw("frontend/dist/index.html").decode("utf-8"),
})
print({"baseline": changes, "run_count": len(runs),
       "runs": [{k: x[k] for k in ["name", "exit_code", "frontend_source_matches_current", "as_run_count", "actual_before_after_delta", "changed_fixture_from_current"]} for x in runs],
       "as_run_mismatches": sum(len(x["as_run_mismatches"]) for x in runs),
       "loaded_count": len(loaded), "all_loaded_match": all(x["all_three_match"] for x in loaded)})
