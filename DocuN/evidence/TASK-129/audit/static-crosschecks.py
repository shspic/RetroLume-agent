"""TASK129原件的标准库只读交叉核对；不导入或运行产品。"""
import ast
import collections
import datetime
import hashlib
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path("D:/shspic/project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-129/audit"
BASE = ROOT / "DocuN/evidence/TASK-128/execution"
ROUND = BASE / "continuation-01"
ENTRY = ROUND / "entry-06"
CHECKS = []
READS = {}


def raw(path):
    path = Path(path)
    data = path.read_bytes()
    READS[str(path)] = {"path": str(path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    return data


def load(path):
    return json.loads(raw(path))


def lines(path):
    return [json.loads(line) for line in raw(path).splitlines()]


def check(name, value, detail=None):
    CHECKS.append({"name": name, "satisfied": bool(value), "detail": detail})


manifest = load(ROOT / "DocuN/evidence/TASK-129/orchestration-20261023/input-manifest.json")
state = load(ROUND / "checkpoint.json")
asrun = load(ENTRY / "as-run.json")
input_changes = []
excluded_metadata = []
for row in asrun["inputs"]:
    if Path(row["path"]).name == "TASK-128-work-decision.md":
        excluded_metadata.append({"path": row["path"], "as_run_sha256": row["sha256"], "current_file_not_read": True})
        continue
    actual = hashlib.sha256(raw(row["path"])).hexdigest()
    if actual != row["sha256"]:
        input_changes.append({"path": row["path"], "as_run": row["sha256"], "current": actual})
allowed_after_run = {str(ROOT / p).replace("\\", "/").lower() for p in
                     ["README.md", "deploy/normal-install.md", "DocuN/results/TASK-128-result.md"]}
check("asrun_no_unexplained_drift", all(x["path"].replace("\\", "/").lower() in allowed_after_run for x in input_changes), input_changes)
for folder in [BASE / "entry-04", BASE / "entry-05-ready", ENTRY]:
    snapshot = load(folder / "as-run.json")
    for row in snapshot["helpers"]:
        copy = folder / Path(row["path"]).name
        check("helper_copy_" + folder.name + "/" + copy.name,
              hashlib.sha256(raw(copy)).hexdigest() == row["sha256"] and len(raw(copy)) == row["bytes"])
for row in manifest["products"]:
    path = Path(row["path"])
    check("current_frozen_" + row["relative_path"], hashlib.sha256(raw(path)).hexdigest() == row["sha256"])

before = ast.parse(raw(BASE / "pre/deploy/initialize_normal.py").decode("utf-8"))
after = ast.parse(raw(ROOT / "deploy/initialize_normal.py").decode("utf-8"))
before_nodes = {n.name: n for n in before.body if isinstance(n, ast.FunctionDef)}
after_nodes = {n.name: n for n in after.body if isinstance(n, ast.FunctionDef)}
changed_functions = [name for name in dict.fromkeys([*before_nodes, *after_nodes])
                     if ast.dump(before_nodes[name], include_attributes=False) != ast.dump(after_nodes[name], include_attributes=False)]
check("only_connect_and_identity_functions_changed", set(changed_functions) == {"connect", "observe_identity"}, changed_functions)
before.body = [n for n in before.body if not isinstance(n, ast.FunctionDef) or n.name not in changed_functions]
after.body = [n for n in after.body if not isinstance(n, ast.FunctionDef) or n.name not in changed_functions]
check("all_other_product_ast_unchanged", ast.dump(before, include_attributes=False) == ast.dump(after, include_attributes=False))
tests = load(ROUND / "targeted-tests.json")
check("three_historical_methods_bound_to_current_bytes", tests["run"] == 3 and tests["passed"] and tests["failures"] == tests["errors"] == 0
      and all(hashlib.sha256(raw(p)).hexdigest() == h for p, h in tests["before_after_identical"].items()))

fixed_manifest = load(ROOT / "deploy/normal_install_manifest.json")
migrations = [Path(row["path"]).name[:3] for row in fixed_manifest["migrations"]]
stages = migrations[:13] + ["normal_control"] + migrations[13:] + ["login_roles"]
receipt = lines(ENTRY / "source-success-receipt.jsonl")
trace = lines(ENTRY / "source-success-trace.jsonl")
check("receipt_exact_37_stage_sequence", len(receipt) == 37 and len(stages) == 17
      and receipt[0]["event"] == "intent" and receipt[1]["event"] == "preflight"
      and all(receipt[2 + i * 2] == {"event": "submitted", "stage": stage}
              and receipt[3 + i * 2] == {"event": "confirmed", "stage": stage} for i, stage in enumerate(stages))
      and receipt[-1] == {"event": "complete", "confirmed_stages": stages, "schema_profile": "data_exit.v1.r03"})
check("receipt_manifest_exact", receipt[0]["migrations"] == fixed_manifest["migrations"]
      and receipt[0]["manifest_sha256"] == hashlib.sha256(raw(ROOT / "deploy/normal_install_manifest.json")).hexdigest())
source = state["slots"]["source"]
check("receipt_same_source_identity", receipt[0]["identities"] == source["identities"]
      and receipt[0]["target"]["system_identifier"] == source["database_identity"]["system_identifier"]
      and receipt[0]["target"]["database_oid"] == source["database_identity"]["database_oid"])
submitted = [r["stage"] for r in trace if r["kind"] == "original_migration_submitted"]
commits = [r for r in trace if r["kind"] == "all_real_migration_results_consumed"]
extra_commits = [r for r in trace if r["kind"] == "additional_transaction_commit_returned"]
check("fifteen_actual_original_sql_commits", submitted == migrations and [r["stage"] for r in commits] == migrations
      and all(r["final_status"] == "COMMIT" and r["transaction_status"] == 0 and r["commit_observed"] is True for r in commits))
check("two_additional_actual_transaction_returns", len(extra_commits) == 2 and all(r["transaction_status"] == 0 for r in extra_commits))
boundaries = [r for r in trace if r["kind"] == "control_observed_after_real_commit"]
check("real_control_profile_progression", [(r["boundary"], r["control"]["schema_profile"] if r["control"] else None) for r in boundaries]
      == [("013", None), ("normal_control", "data_exit.v1.r01"), ("014", "data_exit.v1.r02"), ("015", "data_exit.v1.r03")])
identities = [r for r in trace if r["kind"] == "actual_database_identity"]
check("actual_identity_preserved_in_receipt", len(identities) == 2 and all(
    all(r[k] == v for k, v in receipt[1]["observed"].items()) and r["session_login"] == r["installer_login"]
    and r["rolsuper"] is True for r in identities))
check("source_success_real_connection_not_injected", trace[-1]["connections"] == 1 and trace[-1]["write_requests"] == 26
      and trace[-1]["planned_injection_exercised"] is False and any(r["kind"] == "real_connect_returned" for r in trace))
command = load(ENTRY / "command-030.json")
check("success_real_cli_exit_and_stage_result", command["exit_code"] == 0 and json.loads(command["stdout"])["confirmed_stages"] == stages)

rejections = []
for number, case, reason in [(26, "wrong-database_oid", "target_identity_mismatch"), (27, "wrong-system_identifier", "target_identity_mismatch"),
                              (28, "nonempty", "target_not_empty_or_exclusive"), (29, "role-collision", "global_role_collision")]:
    command = load(ENTRY / ("command-" + str(number).zfill(3) + ".json"))
    case_trace = lines(ENTRY / ("source-" + case + "-trace.jsonl"))
    case_receipt = lines(ENTRY / ("source-" + case + "-receipt.jsonl"))
    value = command["exit_code"] == 2 and json.loads(command["stdout"])["reason"] == reason
    value = value and case_trace[-1]["connections"] == 1 and case_trace[-1]["write_requests"] == 0
    value = value and [r["event"] for r in case_receipt] == ["intent", "stopped"]
    value = value and case_receipt[-1]["reason"] == reason and case_receipt[-1]["unknown_stage"] is None and not case_receipt[-1]["confirmed_stages"]
    check("real_rejection_" + case, value)
    rejections.append({"case": case, "trace_rows": len(case_trace), "receipt_rows": len(case_receipt), "reason": reason, "writes": case_trace[-1]["write_requests"]})
observations = load(ENTRY / "check1.json")
check("temporary_object_oid_evidence", observations[2]["created_and_dropped_exact_oid"] == 16385
      and observations[3]["created_and_dropped_exact_oid"] == 16388)

logins = load(ENTRY / "check3.json")
login_projection = []
for row in logins:
    role_by_id = {r["oid"]: r for r in row["roles"]}
    actual = row["actual_login"]
    expected = "retrolume_normal_" + ("app" if row["purpose"] == "business" else "snapshot")
    subject = next(r for r in row["roles"] if r["rolname"] == expected)
    reached = {subject["oid"]}
    while True:
        expanded = reached | {e["roleid"] for e in row["memberships"] if e["member"] in reached and (e["inherit_option"] or e["set_option"] or e["admin_option"])}
        if reached == expanded:
            break
        reached = expanded
    dangerous = ("rolsuper", "rolcreatedb", "rolcreaterole", "rolreplication", "rolbypassrls", "schema_create", "database_create", "owns_objects", "owns_definers")
    safe = all(not any(role_by_id[i][key] for key in dangerous) and not role_by_id[i]["control_privileges"] for i in reached)
    edges = [e for e in row["memberships"] if e["member"] == subject["oid"]]
    safe = safe and all(e["inherit_option"] is True and e["set_option"] is False and e["admin_option"] is False for e in edges)
    check("actual_separate_login_" + row["purpose"], actual["current_user"] == actual["session_user"] == expected
          and actual["reads_maintenance"] is False and safe and all(r["sqlstate"] == "42501" for r in row["actual_refusals"]))
    check("login_expected_group_count_" + row["purpose"], len(edges) == (5 if row["purpose"] == "business" else 1))
    if row["purpose"] == "snapshot":
        check("snapshot_no_business_write", actual["inserts_activity"] is False and len(row["actual_refusals"]) == 4)
    login_projection.append({"purpose": row["purpose"], "actual_login": actual, "refusals": row["actual_refusals"],
                             "reachable_roles": [role_by_id[i]["rolname"] for i in sorted(reached)]})

memory = lines(ENTRY / "memory.jsonl")
low = maximum_low = 0
for row in memory:
    low = low + 1 if row["available_mib"] < 256 else 0
    maximum_low = max(maximum_low, low)
check("no_two_consecutive_low_samples", maximum_low == 1)
check("actual_start_counts_and_no_api", state["entries"] == 6 and source["starts"] == 4
      and state["slots"]["interrupted"]["starts"] == 1 and state["api_starts"] == 0 and state["api_intervals"] == [])
check("pg_holding_sum", abs(sum(r["seconds"] for r in state["pg_intervals"]) - 34.1386296749115) < 1e-9)
for slot in ("source", "interrupted"):
    earlier = load(ENTRY / (slot + "-pre-reuse-identity.json"))
    stop_name = "source-stop-observation-7.json" if slot == "source" else "interrupted-stop-observation-3.json"
    stopped = load(ENTRY / stop_name)
    created = state["slots"][slot]["created_projection"]
    check("stable_container_and_stopped_" + slot, all(earlier[k] == stopped[k] == created[k] for k in ("cid", "image_id", "created", "mounts", "limits"))
          and stopped["state"]["Running"] is False and stopped["state"]["Pid"] == 0)
post = load(ROUND / "post-snapshot.json")
check("historical_no_listener_projection", post["ports"] == [] and post["no_listeners"] is True)

# 仅按已读原始命令中的单一非敏感收据路径核hash，检查完整父链。
command = load(ENTRY / "command-030.json")
private = Path(command["argv"][command["argv"].index("--receipt") + 1])
expected_private = ROOT / ".runtime/normal-first-install/source/receipts/task128-c01-success.jsonl"
check("private_receipt_path_exact", private == expected_private)
if private != expected_private:
    raise SystemExit("private_receipt_path_rejected")
parents = []
for current in reversed((private,) + tuple(private.parents)):
    info = current.lstat()
    if info.st_file_attributes & 1024:
        raise SystemExit("private_receipt_reparse_rejected")
    parents.append(str(current))
private_hash = hashlib.sha256(raw(private)).hexdigest()
copy_hash = hashlib.sha256(raw(ENTRY / "source-success-receipt.jsonl")).hexdigest()
check("private_success_receipt_same_bytes", private_hash == copy_hash == source["successful_receipt_sha256"])

for rel in ["connection.py", "_connection_base.py", "conninfo.py", "_conninfo_utils.py", "_conninfo_attempts.py", "version.py"]:
    raw(ROOT / "backend/.venv/Lib/site-packages/psycopg" / rel)
raw(ROOT / "DocuN/results/TASK-126-result.md")
raw(ROOT / "DocuN/evidence/TASK-128/orchestration-continuation01-20261023/permit.json")
result = {"at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(), "analysis_only_no_product_import": True,
          "checks": CHECKS, "failed": [r for r in CHECKS if not r["satisfied"]], "asrun_post_changes": input_changes,
          "excluded_orchestration_metadata": excluded_metadata,
          "trace_kind_counts": dict(collections.Counter(r["kind"] for r in trace)), "rejections": rejections,
          "logins": login_projection, "memory": {"samples": len(memory), "minimum_mib": min(r["available_mib"] for r in memory),
          "maximum_consecutive_below256": maximum_low}, "private_receipt": {"path": str(private), "safe_parent_chain": parents, "sha256": private_hash},
          "read_hashes": list(READS.values())}
(OUT / "static-crosschecks-02.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"checks": len(CHECKS), "failed": result["failed"], "asrun_post_changes": input_changes,
                  "receipt_sha256": copy_hash, "memory": result["memory"], "read_hashes": len(READS)}, ensure_ascii=False))
raise SystemExit(1 if result["failed"] else 0)
