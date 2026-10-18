import collections
import json
from metadata import ROOT, check_deadline, identity, load, now, raw, save, sha

check_deadline()
base = ROOT / "DocuN/evidence/TASK-103/audit-repair-03"
groups = ["real-01-r03-main", "real-02-r03-preloaded-targets", "real-03-r03-p1-unique-effect"]
own_ids = set(load(base / "session.json")["synthetic_memory_ids"])
canonical = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
fingerprints = lambda rows: collections.Counter(canonical(x) for x in rows)
root_checks, commands, browser_cases = [], [], []
unknown_key = "a392c565-1731-4314-b22e-6cee9458f862"
unknown_activity = "be3d572f-8e04-4008-96d3-ec4fc99afa6c"

for group in groups:
    folder = base / "groups" / group
    before, after = load(folder / "pg-before.json"), load(folder / "pg-after.json")
    browser, result = load(folder / "browser/result.json"), load(folder / "result.json")
    browser_cases.append({"root": group, "browser_status": browser["status"],
                          "root_status": result["status"], "cases": browser["cases"]})
    old_missing, allowed_heads, additions = {}, [], {}
    for table, rows in before.items():
        retained = [x for x in rows if not (table == "learning_memories" and x["memory_id"] in own_ids)]
        missing = fingerprints(retained) - fingerprints(after[table])
        if missing:
            old_missing[table] = dict(missing)
        additions[table] = sum((fingerprints(after[table]) - fingerprints(rows)).values())
    for old in before["learning_memories"]:
        if old["memory_id"] not in own_ids:
            continue
        new = next((x for x in after["learning_memories"] if x["memory_id"] == old["memory_id"]), None)
        keys = [k for k in old.keys() | (new or {}).keys() if old.get(k) != (new or {}).get(k)]
        allowed_heads.append({"memory_id": old["memory_id"], "changed_fields": keys,
                              "only_revision_version_updated_at": new is not None
                              and set(keys) <= {"revision", "current_version", "updated_at"}})
    writes = [x for x in browser["network"] if x["event"] == "request" and x["method"] == "POST"]
    for event in writes:
        request = event["payload"]
        key = request["business_key"]
        records = [x for x in after["learning_memory_commands"] if x["business_key"] == key]
        record = records[0] if records else None
        request_body = {"schema": "memory.command.v1", **{k: request[k] for k in ["action", "memory_id", "expected_revision", "body"]}}
        request_hash = sha(canonical(request_body).encode())
        versions = [x for x in after["learning_memory_revisions"] if x["created_by_key"] == key]
        bodies = [x for x in after["learning_memory_bodies"] if any(
            x["memory_id"] == v["memory_id"] and x["version"] == v["version"] for v in versions)]
        body_matches = len(versions) == len(bodies) == 1 and sha(bodies[0]["body"].encode()) == versions[0]["body_sha256"]
        effect = bool(record and record["effect_applied"])
        commands.append({"root": group, "request_at": event["at"], "path": event["path"],
                         "request": request, "computed_request_sha256": request_hash, "M5": records,
                         "request_hash_matches_M5": len(records) == 1 and request_hash == record["request_sha256"],
                         "key_absent_before": not any(x["business_key"] == key for x in before["learning_memory_commands"]),
                         "effect_applied": effect, "M2_created_by_key": versions, "M3_created_by_key": bodies,
                         "effect_body_sha_matches": body_matches if effect else len(versions) == 0,
                         "effect_created_one_version": len(versions) == 1 if effect else len(versions) == 0})
    unknown_before = next(x for x in before["teaching_commands"] if x["business_key"] == unknown_key)
    unknown_after = next(x for x in after["teaching_commands"] if x["business_key"] == unknown_key)
    activity = next(x for x in after["activities"] if x.get("id", x.get("activity_id")) == unknown_activity)
    old_activity = next(x for x in before["activities"] if x.get("id", x.get("activity_id")) == unknown_activity)
    root_checks.append({"root": group, "pg_before": identity(folder / "pg-before.json"),
                        "pg_after": identity(folder / "pg-after.json"), "captured_table_count": len(before),
                        "old_rows_missing_outside_allowed_heads": old_missing,
                        "own_head_changes": allowed_heads, "added_or_modified_row_counts": additions,
                        "non_memory_tables_equal": all(before[t] == after[t] for t in before if not t.startswith("learning_memor")),
                        "own_ids_never_selected": not any(x["memory_id"] in own_ids for x in after["activity_memory_choices"]),
                        "network_POST_count": len(writes), "network_DELETE_count": sum(x.get("method") == "DELETE" for x in browser["network"]),
                        "POST_only_save_revise_own_ids": all(x["path"] == "/api/memories/commands" and x["payload"]["memory_id"] in own_ids
                                                            and x["payload"]["action"] in ["save", "revise"] for x in writes),
                        "UNKNOWN_row_equal": unknown_before == unknown_after, "UNKNOWN_status": unknown_after["status"],
                        "UNKNOWN_activity_equal": activity == old_activity,
                        "UNKNOWN_budget_fields": {k: v for k, v in activity.items() if any(w in k for w in ["budget", "request", "tool", "cost", "reserved", "settled"])}})

save("eight-POST-and-persistent-effect-binding.json", {
    "at": now(), "commands": commands, "distinct_keys": len({x["request"]["business_key"] for x in commands}),
    "actual_POST_count": len(commands), "effects": sum(x["effect_applied"] for x in commands),
    "no_op_count": sum(not x["effect_applied"] for x in commands), "roots": root_checks,
    "all_request_hashes_and_effects_match": all(x["request_hash_matches_M5"] and x["effect_body_sha_matches"] and x["effect_created_one_version"] for x in commands)})
save("actual-and-inherited-case-binding.json", {"at": now(), "roots": browser_cases})

folder = base / "groups" / groups[-1] / "browser"
browser = load(folder / "result.json")
case = next(x for x in browser["cases"] if x["name"].startswith("P1"))
post, listing = load(folder / "p1-post-controller.json"), load(folder / "p1-confirmed-refresh-controller.json")
clean, final = load(folder / "p1-clean-B-before-release-values.json"), load(folder / "p1-after-values.json")
keys = ["id", "version", "revision", "sha", "owner", "title", "text"]
order = [post["server_response_at"], post["delivered_at"], listing["request_at"], listing["server_response_at"],
         listing["clean_B_loaded_at"], listing["release_attempt_at"], listing["delivered_at"]]
after_old_A_gets = [x for x in browser["network"] if x["event"] == "request"
                    and x["path"] == "/api/memories/" + case["A"] and x["at"] >= listing["clean_B_loaded_at"]]
proof = {"at": now(), "real_root": groups[-1], "ordered_controller_milliseconds": order,
         "strict_order": all(a < b for a, b in zip(order, order[1:])),
         "post_controller": identity(folder / "p1-post-controller.json"),
         "list_controller": identity(folder / "p1-confirmed-refresh-controller.json"),
         "clean_B": clean["fields"], "after_release_before_further_edit": case["after"],
         "full_B_identity_and_body_same": all(clean["fields"][k] == case["after"][k] for k in keys),
         "clean_B_has_no_draft": not any(x["memory_id"] == case["B"] and x["owner"] == clean["fields"]["owner"] for x in clean["drafts"]),
         "old_A_detail_GET_increment": len(after_old_A_gets),
         "new_B_drafts": [x for x in final["drafts"] if x["memory_id"] == case["B"]],
         "final_editor": final["fields"], "intents_after": final["intents"],
         "receipt": case["receipt"], "persistent_command": next(x for x in commands if x["root"] == groups[-1])}
save("F01-exact-window-binding.json", proof)

folder = base / "groups" / groups[1] / "browser"
browser = load(folder / "result.json")
case = browser["cases"][-1]
controller = load(folder / "late-citation-controller.json")
network = browser["network"]
citation = controller["response"]["citation"]
start, end = controller["request_at"], controller["delivered_at"]
phase = [x for x in network if start <= x["at"] <= end]
aborts = [x for x in phase if x["event"] == "requestfailed" and x["path"] == controller["path"]]
original = base / "workspace" / groups[1] / "data/originals" / citation["original_sha256"]
dom = raw(folder / "citation-after-dom.txt").decode("utf-8-sig")
proof = {"at": now(), "real_root": groups[1], "controller": identity(folder / "late-citation-controller.json"),
         "actual_GET_path": controller["path"], "status": controller["status"], "citation": citation,
         "order_milliseconds": [start, controller["server_response_at"], controller["new_panel_loaded_at"], controller["release_attempt_at"], end],
         "new_panel_loaded_before_delivery_attempt": controller["new_panel_loaded_at"] <= controller["release_attempt_at"] < end,
         "route_fulfill_returned": "delivered_at" in controller, "client_request_failed": aborts,
         "client_citation_response_events": [x for x in network if x["event"] == "response" and x["path"] == controller["path"]],
         "new_activity": case["new_activity"], "new_head": case["new_head"],
         "new_workspace_events": [x for x in phase if x["path"] == "/api/activities/" + case["new_activity"] + "/teaching/workspace"],
         "citation_phase_POST_count": sum(x.get("event") == "request" and x.get("method") == "POST" for x in phase),
         "old_full_quote_present_in_new_DOM": citation["text"] in dom,
         "new_DOM_contains_revision_1": "待生成路径 · 修订 1 · 目标版本 1" in dom,
         "original_bytes": identity(original), "citation_text_sha_matches_original": sha(citation["text"].encode()) == sha(raw(original)) == citation["original_sha256"],
         "dedicated_PG_snapshots_during_citation_phase": False,
         "PG_evidence_scope": "整根前后21表；非记忆表相等，旧行除允许A/B头版本字段外保留；不声称取得引用阶段专属PG快照",
         "native_screenshots": [identity(folder / name) for name in ["citation-held.png", "citation-after.png"]]}
save("E01-late-citation-layered-binding.json", proof)
print({"commands": len(commands), "keys": len({x["request"]["business_key"] for x in commands}),
       "effects": sum(x["effect_applied"] for x in commands), "no_op": sum(not x["effect_applied"] for x in commands),
       "all_request_hashes_and_effects_match": all(x["request_hash_matches_M5"] and x["effect_body_sha_matches"] and x["effect_created_one_version"] for x in commands),
       "root_checks": root_checks, "citation_phase_POST_count": proof["citation_phase_POST_count"],
       "citation_text_sha_matches_original": proof["citation_text_sha_matches_original"], "citation_aborts": aborts})
