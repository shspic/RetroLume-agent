"""主控只核文件身份、快照及保存事实，不运行产品或测试。"""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
EXECUTION = ROOT / "DocuN/evidence/TASK-123/execution"
HERE = Path(__file__).resolve().parent


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def normalize(value):
    p = Path(str(value).replace("\\\\", "/").replace("\\", "/"))
    return p if p.is_absolute() else ROOT / p


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


checks = []


def identity(path, expected, scope):
    p = normalize(path)
    actual = digest(p) if p.is_file() else None
    checks.append({"scope": scope, "path": p.as_posix(), "expected": expected,
                   "actual": actual, "bytes": p.stat().st_size if p.is_file() else None,
                   "matched": actual == expected})


save = load(EXECUTION / "save-proof.json")
manifest = load(EXECUTION / "delivery-manifest.json")
for row in manifest["rows"]:
    identity(row["path"], row["sha256"], "48_returned_artifacts")
identity(save["result"]["path"], save["result"]["sha256"], "returned_report")

post = load(EXECUTION / "post-snapshot.json")
post_by_path = {row["path"]: row for row in post["products"]}
assert len(post_by_path) == 6
for row in post["products"]:
    identity(row["path"], row["post_sha256"], "six_final_files")

pre = load(EXECUTION / "pre-snapshot.json")
for row in pre["products"]:
    if row["exists"]:
        identity(row["pre_copy"], row["sha256"], "four_original_byte_copies")
        assert row["sha256"] == post_by_path[row["path"]]["pre_sha256"]
    else:
        assert row["pre_copy"] is None and post_by_path[row["path"]]["pre_exists"] is False

inputs = load(ROOT / "DocuN/evidence/TASK-123/orchestration-20261022/input-manifest.json")
for row in inputs["rows"]:
    p = normalize(row["path"])
    rel = p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else None
    expected = post_by_path[rel]["post_sha256"] if rel in post_by_path else row["sha256"]
    identity(p, expected, "43_issued_inputs_allowed_four_changes")

batch = load(EXECUTION / "batch3/command.json")
for row in batch["input_bytes"]:
    identity(row["path"], row["sha256"], "six_as_run_python_inputs")
summary = load(EXECUTION / "batch3/summary.json")
completion = load(EXECUTION / "batch3/completion.json")
log = (EXECUTION / "batch3/stderr.bin").read_text(encoding="utf-8", errors="replace")
batch_checks = {
    "13_methods_no_failure_error_skip": summary["tests_run"] == 13 and not any(summary[k] for k in ("failures", "errors", "skipped")),
    "exit_zero": completion["exit_code"] == 0,
    "original_stderr_13_OK": "Ran 13 tests" in log and "\nOK" in log,
    "all_11_tripwires_zero": len(summary["forbidden_call_counts"]) == 11 and all(v == 0 for v in summary["forbidden_call_counts"].values()),
    "three_batches_only": sorted(p.name for p in EXECUTION.glob("batch*") if p.is_dir()) == ["batch1", "batch2", "batch3"],
    "final_batch_recorded_under_120_seconds": completion["elapsed_seconds"] < 120,
}
for item in completion["logs"]:
    identity(EXECUTION / "batch3" / item["path"], item["sha256"], "as_run_log_binding")

finite = load(EXECUTION / "finite-inputs.json")
text_checks = {}
for name in ("html", "continuation_reason"):
    field = finite[name]
    data = field["text"].encode("utf-8")
    text_checks[name] = (sha256(data).hexdigest() == field["sha256"]
                        and len(data) == field["utf8_bytes"] and len(field["text"]) == field["codepoints"])
identity(finite["inherited_matrix"]["path"], finite["inherited_matrix"]["sha256"], "unchanged_matrix")
identity(finite["unchanged_samples"]["path"], finite["unchanged_samples"]["sha256"], "unchanged_original_samples")
assert finite["enabled"] is False
meter = load(EXECUTION / "metering-evidence.json")
assert meter["token_upper_bound_verified"] is False and meter["provider_runtime_verified"] is False

protected_paths = [
    "DocuN/results/TASK-120-result.md", "DocuN/results/TASK-121-result.md",
    "DocuN/evidence/TASK-120/execution/budget.json", "DocuN/evidence/TASK-120/execution/events.jsonl",
    "DocuN/results/TASK-122-result.md", "DocuN/results/TASK-122-work-decision.md",
    "DocuS/原始需求文档.MD", "DocuS/最终需求文档.MD",
]
protected = {rel: digest(ROOT / rel) for rel in protected_paths}
prior = load(ROOT / "DocuN/evidence/TASK-122/orchestration-acceptance-20261022/return-check.json")
for rel, expected in prior["unchanged_objects_for_publication"].items():
    identity(ROOT / rel, expected, "previous_immutable_outputs")

result = {"schema": "retrolume.task123.orchestration-return.v1", "at": datetime.now(timezone.utc).isoformat(),
    "scope": "主控有限文件/证据身份核对，不是独立代码审计或产品动态验证",
    "identity_count": len(checks), "identities": checks,
    "mismatches": [row for row in checks if not row["matched"]],
    "returned_artifacts": len(manifest["rows"]), "final_files": 6,
    "test_evidence_checks": batch_checks, "finite_text_checks": text_checks,
    "protected_for_publication": protected,
    "final_test_exit": completion["exit_code"], "final_test_parent_seconds": completion["elapsed_seconds"],
    "external_metering_evidence_incomplete": True, "Q": "FROZEN", "orchestrator_product_runtime": 0,
    "passed": all(row["matched"] for row in checks) and all(batch_checks.values()) and all(text_checks.values())}
(HERE / "return-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed": result["passed"], "identities": len(checks), "artifacts": len(manifest["rows"]),
    "mismatches": result["mismatches"], "failed_checks": [k for k, v in batch_checks.items() if not v],
    "test_methods": summary["tests_run"], "test_exit": completion["exit_code"], "runtime": 0}, ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
