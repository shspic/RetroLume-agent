"""只核对返回材料、文件身份及文档算术，不导入或运行产品。"""

from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
OUT = Path(__file__).resolve().parent
PREP = ROOT / "DocuN/evidence/TASK-122/preparation"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def normal_path(value):
    return Path(str(value).replace("\\\\", "/").replace("\\", "/"))


rows = []


def check_path(path, expected, scope, exception=None):
    p = normal_path(path)
    actual = digest(p) if p.is_file() else None
    expected_now = exception if exception else expected
    rows.append({"scope": scope, "path": p.as_posix(), "expected_original": expected,
                 "expected_current": expected_now, "actual": actual, "match": actual == expected_now})


delivery = load(PREP / "delivery.json")
change = load(PREP / "README-change.json")
readme = ROOT / "README.md"

for item in load(PREP / "input-identity.json")["rows"]:
    allow = change["after_sha256"] if normal_path(item["path"]) == readme else None
    check_path(item["path"], item["expected"], "32_locked_inputs", allow)

for item in delivery["artifacts"]:
    check_path(item["path"], item["sha256"], "returned_artifacts")
check_path(delivery["result_path"], delivery["result_sha256"], "result")
check_path(PREP / "README.before.bin", change["before_sha256"], "README_before")
check_path(readme, change["after_sha256"], "README_after")

read_events = [json.loads(line) for line in (PREP / "read-ledger.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
latest_reads = {normal_path(item["path"]).as_posix(): item for item in read_events}
for path, item in latest_reads.items():
    allow = change["after_sha256"] if normal_path(path) == readme else None
    check_path(path, item["sha256"], "read_file_identity", allow)

matrix = load(PREP / "remaining-must-matrix.json")
counts = Counter(action["kind"] for action in matrix["actions_in_recommended_order"])
actions = matrix["actions_in_recommended_order"]
row_counts = Counter(action["row"] for action in actions)
by_role = Counter(action["activity"] for action in actions)
math_checks = {
    "89_actual_action_descriptors": len(actions) == 89,
    "41_model_41_query_6_index_1_html": counts == {"model": 41, "query_embedding": 41, "source_index_embedding": 6, "html": 1},
    "13_row_counts": all(row_counts[row["id"]] == row["requests"] for row in matrix["rows"]),
    "three_role_counts": dict(by_role) == {"learning": 43, "interview": 28, "supplement": 18},
    "reservation": sum(action["reserve_microunits"] for action in actions) == 22250000,
    "planned_reservation_within_adopted_global": 22250000 <= matrix["global_max_cost_microunits"] == 25000000,
    "28_must_descriptors": len(matrix["must_coverage"]) == 28,
    "no_activation": matrix["activation_eligible"] is False and matrix["real_completed_requests"] == 0,
    "interview_no_failure_buffer_explicit": matrix["roster"][1]["remaining_requests_after_normal_path"] == 0,
}
for roster in matrix["roster"]:
    role = roster["role"]
    planned = by_role[role]
    math_checks["roster_" + role] = (planned == roster["planned_requests"]
        and roster["planned_reserve_microunits"] == planned * 250000
        and roster["remaining_requests_after_normal_path"] == roster["max_requests"] - planned
        and roster["remaining_reserve_microunits_after_normal_path"] == roster["max_cost_microunits"] - planned * 250000)

samples = load(ROOT / "DocuN/evidence/TASK-116/design/sample-inputs.json")
fragments = load(PREP / "sample-fragments.json")
reconstructed = []
source_counts = []
for source in samples["sources"]:
    offset = 0
    before = len(reconstructed)
    for line_number, text in enumerate(source["text"].splitlines(keepends=True), 1):
        for start in range(0, len(text), 2048):
            part = text[start:start + 2048]
            reconstructed.append({"alias": source["alias"], "line": line_number,
                "start_offset": offset + start, "end_offset": offset + start + len(part),
                "codepoints": len(part), "utf8_bytes": len(part.encode("utf-8")),
                "raw_text_sha256": sha256(part.encode("utf-8")).hexdigest(),
                "json_string_sha256": sha256(canonical(part)).hexdigest(),
                "json_string_bytes": len(canonical(part)),
                "source_id": None, "version_id": None, "revision": None, "evidence_id": None})
        offset += len(text)
    source_counts.append(len(reconstructed) - before)
math_checks["24_fragment_descriptors_match_exact_frozen_text"] = reconstructed == fragments["fragments"] and len(reconstructed) == 24
math_checks["6_static_batches"] = (len(reconstructed) + 3) // 4 == fragments["source_index_calls"] == 6
upper = len(canonical({"model": "embedding-3", "input": [], "dimensions": 512})) + sum(sorted((item["json_string_bytes"] for item in reconstructed), reverse=True)[:4]) + 3
math_checks["446_wire_bytes_static_upper"] = upper == fragments["any_four_fragment_payload_bytes_upper_bound"] == 446
math_checks["token_proof_still_unknown"] = fragments["token_bound_verified"] is False and fragments["tokens_per_item_and_batch"] is None

cost = load(PREP / "cost-calculation.json")
for name, length, output, input_rate, output_rate in [
    ("embedding_shared_absolute_65536", 65536, 0, "2", "8"),
    ("learning_256_absolute_65536", 65536, 256, "2", "8"),
    ("teaching_interview_2048_absolute_65536", 65536, 2048, "2", "8"),
    ("html_4096_absolute_65536", 65536, 4096, "2", "8"),
    ("embedding_own_rate_absolute_65536", 65536, 0, "0.5", "0"),
    ("embedding_own_rate_draft_32768", 32768, 0, "0.5", "0"),
    ("source_batch_shared_byte_illustration", 446, 0, "2", "8"),
]:
    calculated = int(((Decimal(length + 4096) * Decimal(input_rate) + Decimal(output) * Decimal(output_rate)) * Decimal("1.25")).to_integral_value(rounding=ROUND_CEILING))
    math_checks["conditional_cost_" + name] = calculated == cost["classes_microunits"][name]
math_checks["not_account_quote"] = cost["actual_applicable_per_request_ceiling"] is None

command_ledger = load(PREP / "command-ledger.json")
immutable = {path: digest(ROOT / path) for path in [
    "DocuN/results/TASK-120-result.md", "DocuN/results/TASK-121-result.md",
    "DocuN/evidence/TASK-120/execution/budget.json", "DocuN/evidence/TASK-120/execution/events.jsonl",
    "DocuS/原始需求文档.MD", "DocuS/最终需求文档.MD",
]}
result = {
    "schema": "retrolume.task122.orchestration-return-check.v1",
    "at": datetime.now(timezone.utc).isoformat(), "purpose": "主控有限文件核证，不是独审或产品验证",
    "identity_rows": rows, "identity_count": len(rows), "identity_mismatches": [row for row in rows if not row["match"]],
    "document_arithmetic_checks": math_checks,
    "static_fragment_counts": source_counts, "actions_by_kind": dict(counts), "actions_by_role": dict(by_role),
    "unchanged_objects_for_publication": immutable,
    "execution_control": {"known_command_wall_seconds": command_ledger["known_command_wall_seconds_including_final_check"],
        "delivery_conservative_charge_seconds": delivery["budget"]["conservative_charge_seconds"],
        "known_minimum_metadata_lookup_failures": command_ledger["subcommand_exit_limitations"]["known_minimum_failures"],
        "unknown_subcommand_failures_retained": True, "product_runtime_observed_in_report": 0,
        "limit": "原始元数据子命令未知及保守预留保留，不以报告零运行自述替代独立进程审计"},
    "passed": not any(not row["match"] for row in rows) and all(math_checks.values()),
}
(OUT / "return-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed": result["passed"], "identity_rows": len(rows),
    "mismatches": result["identity_mismatches"], "failed_document_checks": [k for k, v in math_checks.items() if not v],
    "actions": len(actions), "static_fragments": len(reconstructed), "runtime": 0}, ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
