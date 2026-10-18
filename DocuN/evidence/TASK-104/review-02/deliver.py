import os
import pathlib
import time
from metadata import ROOT, OWN, check_deadline, identity, load, now, raw, save, sha

check_deadline()
incoming_path = ROOT / "DocuN/evidence/TASK-104/orchestration-review-02-20261007/review-input.json"
incoming = load(incoming_path)
initial = load(OWN / "initial-identity-check.json")
if sha(raw(incoming_path)) != initial["input"]["sha256"]:
    raise RuntimeError("本轮输入发生漂移")
rows = []
for p, h in incoming["current_files"].items():
    actual = identity(p)
    rows.append({**actual, "expected_sha256": h, "match": actual["sha256"] == h})
for r in incoming["rules_contracts"]:
    actual = identity(r["path"])
    rows.append({**actual, "expected_sha256": r["sha256"], "match": actual["sha256"] == r["sha256"]})
if not all(x["match"] for x in rows):
    raise RuntimeError("末次当前对象或规则漂移")

# 只重核本轮已配对的原件指针，不重采旧链或运行产品。
pointers = {}
def collect(value):
    if isinstance(value, dict):
        if {"path", "sha256", "bytes"} <= value.keys() and pathlib.Path(value["path"]).is_absolute():
            pointers[value["path"]] = value
        for item in value.values():
            collect(item)
    elif isinstance(value, list):
        for item in value:
            collect(item)

for name in ["F01-exact-window-binding.json", "E01-late-citation-layered-binding.json",
             "eight-POST-and-persistent-effect-binding.json", "execution-control-independent-binding.json",
             "all-nine-run-and-loaded-bundle-binding.json", "pre-current-source-chain.json"]:
    collect(load(OWN / name))
witnesses = []
for p, expected in pointers.items():
    actual = identity(p)
    witnesses.append({**actual, "expected_sha256": expected["sha256"], "match": actual["sha256"] == expected["sha256"]
                       and actual["bytes"] == expected["bytes"]})
if not all(x["match"] for x in witnesses):
    raise RuntimeError("本轮原件指针发生漂移")
save("final-identity-check.json", {"at": now(), "current_objects": 308, "rules_contracts": 9,
                                    "checks": rows, "raw_pointer_checks": witnesses,
                                    "all_match": True, "entry": identity("AGENTS.md"),
                                    "task_card": identity("DocuN/tasks/TASK-104.md")})

receipt = load(OWN / "audit-receipt.json")
command_log = load(OWN / "metadata-command-log.json")
active_seconds = time.perf_counter() - receipt["monotonic_origin"]
metadata_seconds = receipt["metadata_seconds_initial_charge"] + command_log["measured_commands_seconds"] + 90
if active_seconds >= 7200 or metadata_seconds >= 1200:
    raise RuntimeError("交付前审计预算触顶")
report = ROOT / "DocuN/results/TASK-104-result.md"
old = raw(OWN / "original-result-bytes.md")
expected = "54306f7a9e7145f52ef22cdd8c99511f173f9674deda22f2418779ab32d48d3b"
if len(old) != 21896 or sha(old) != expected or raw(report) != old:
    raise RuntimeError("原104报告不是已确认原字节，禁止覆写")
prefix = raw(OWN / "report-prefix-draft.md").decode("utf-8")
prefix = prefix.replace("{{FINAL_AT}}", now()).replace("{{ACTIVE_SECONDS}}", f"{active_seconds:.3f}")
prefix = prefix.replace("{{METADATA_SECONDS}}", f"{metadata_seconds:.3f}")
prefix_bytes = prefix.encode("utf-8")
if "{{" in prefix or "*" in prefix:
    raise RuntimeError("新前缀存在占位符或违规星号")
(OWN / "report-prefix.md").write_bytes(prefix_bytes)
account = {
    "status": "审计完成待回传", "at": now(), "permit": receipt["permit"],
    "monotonic_origin": receipt["monotonic_origin"], "active_deadline_monotonic": receipt["active_deadline_monotonic"],
    "active_used_seconds_at_save": active_seconds, "active_limit_seconds": 7200,
    "metadata_charged_seconds": metadata_seconds, "metadata_limit_seconds": 1200,
    "metadata_initial_unmeasured_charge": 120, "metadata_early_known_charge": 1.5,
    "metadata_measured_commands_seconds": command_log["measured_commands_seconds"],
    "metadata_web_display_writing_and_last_delivery_unmeasured_conservative_charge": 90,
    "metadata_exact_split_unknown": True,
    "new_real_tests_product_fixture_compile_build_PG_SQL_HTTP_browser_resources_model_POST_password_DDL": 0,
    "official_primary_pages_read": 1, "all_metadata_errors_retained": True,
    "original_report_bytes": 21896, "original_report_sha256": expected,
    "code_conclusion": "通过有限增量，F01关闭，无本次确定同链阻断",
    "evidence_conclusion": "通过准确P1与引用卸载取消晚到有限证据",
    "execution_control_conclusion": "通过有限核证，旧失败/保守/未知保留",
    "overall": "批准G9有限切片具备交编排关闭条件，未代签共享状态",
}
save("session-accounting.json", account)
temporary = OWN / "assembled-result.tmp"
temporary.write_bytes(prefix_bytes + old)
os.replace(temporary, report)
actual = raw(report)
if actual != prefix_bytes + old or sha(actual[-21896:]) != expected:
    raise RuntimeError("交付suffix验证失败")
actual.decode("utf-8")
save("delivery-check.json", {"at": now(), "report": identity(report), "prefix_bytes": len(prefix_bytes),
                             "prefix_sha256": sha(prefix_bytes), "historical_suffix_bytes": 21896,
                             "historical_suffix_sha256": sha(actual[-21896:]),
                             "exact_history_suffix_preserved": actual[-21896:] == old,
                             "report_readable_utf8": True, "snapshot_all_match": True,
                             "raw_pointer_count": len(witnesses), "actual_new_execution_count": 0})
account["active_used_seconds_at_delivery_check"] = time.perf_counter() - receipt["monotonic_origin"]
account["delivery_check_complete"] = True
save("session-accounting.json", account)
print({"report": identity(report), "prefix_bytes": len(prefix_bytes), "history_exact": actual[-21896:] == old,
       "current_and_rules_matched": len(rows), "raw_pointer_matched": len(witnesses),
       "active_seconds": account["active_used_seconds_at_delivery_check"], "metadata_seconds": metadata_seconds,
       "actual_new_execution_count": 0})
