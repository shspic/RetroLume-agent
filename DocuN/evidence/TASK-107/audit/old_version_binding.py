import ast
from metadata import ROOT, OWN, check_deadline, identity, load, now, raw, save, sha

check_deadline()
incoming = load("DocuN/evidence/TASK-107/orchestration-setup-20261008/audit-input.json")
current = incoming["current_files"]
production = {x["path"] for x in incoming["all_G10_production_actual_scope"]}
initial = load(incoming["initial_baseline"])["current_files"]
pre = ROOT / "DocuN/evidence/TASK-106/pre"
protected = [p for p in initial if p not in production and not p.startswith("frontend/dist/")]
bad = [p for p in protected if current.get(p) != initial[p]]
save("G9-protected-inheritance.json", {"at": now(), "initial_objects": len(initial),
                                       "protected_count": len(protected), "changed": bad,
                                       "all_unaffected_match": not bad})

def functions(text):
    tree = ast.parse(text)
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.setdefault(node.name, []).append(ast.dump(node, include_attributes=False))
    return found

rows = []
for stem in ["DocuN/evidence/TASK-106", "DocuN/evidence/TASK-106/continuation-01"]:
    index = load(stem + "/final/run-index.json")
    for item in index["runs"]:
        folder = ROOT / stem / "runs" / item["name"]
        run = identity(folder / "run.json")
        record = load(folder / "run.json")
        expected = item.get("sha256")
        source_file = folder / "pre-source.json"
        manifest = load(source_file) if source_file.exists() else {}
        post_file = folder / "post-source.json"
        after = load(post_file) if post_file.exists() else {}
        if not isinstance(manifest, dict) or not isinstance(after, dict):
            raise RuntimeError("运行源码清单形状需要单独定位")
        source_changes = [p for p in production if p in manifest and manifest[p] != current[p]]
        during = [p for p in manifest if p in after and manifest[p] != after[p]]
        function_map, mismatches, absent = {}, [], []
        for p in production:
            captured = folder / "as-run" / p
            if p not in manifest:
                continue
            if not captured.exists():
                absent.append(p)
                continue
            if sha(raw(captured)) != manifest[p]:
                mismatches.append(p)
            if p.endswith(".py") and manifest[p] != current[p]:
                old_functions = functions(raw(captured).decode("utf-8-sig"))
                new_functions = functions(raw(p).decode("utf-8-sig"))
                function_map[p] = {"same_functions": [n for n in old_functions if old_functions[n] == new_functions.get(n)],
                                   "changed_functions": [n for n in old_functions if old_functions[n] != new_functions.get(n)]}
        rows.append({"round": stem, "name": item["name"], "run": run,
                     "run_index_sha_matches": expected is None or run["sha256"] == expected,
                     "actual_category": record.get("category", item.get("category")),
                     "actual_status": record.get("status"), "elapsed_seconds": record.get("elapsed_seconds"),
                     "source_manifest_count": len(manifest), "production_changed_from_current": source_changes,
                     "during_run_changes": during, "as_run_mismatch": mismatches,
                     "missing_as_run_production": absent, "function_applicability": function_map})
save("all-31-old-runs-version-applicability.json", {"at": now(), "runs": rows,
                                                  "actual_records": len(rows),
                                                  "pass_label_not_used_as_sub_assertion": True})
print({"records": len(rows), "run_hashes_match": all(x["run_index_sha_matches"] for x in rows),
       "protected_changed": bad,
       "runs": [{k: x[k] for k in ["name", "actual_status", "source_manifest_count", "production_changed_from_current", "missing_as_run_production", "as_run_mismatch"]} for x in rows]})
