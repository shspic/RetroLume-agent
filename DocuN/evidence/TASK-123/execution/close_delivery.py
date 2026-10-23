"""收尾预算与保存复读，不修改共享账或产品。"""
import datetime
import hashlib
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if sys.argv[1] == "budget":
    permit = json.loads((ROOT / "DocuN/evidence/TASK-123/orchestration-20261022/permit.json").read_bytes())
    now = datetime.datetime.now(datetime.timezone.utc)
    elapsed = (now - datetime.datetime.fromisoformat(permit["issued_at"])).total_seconds()
    charge = elapsed + 300 + 600
    assert charge < 7200 and now < datetime.datetime.fromisoformat(permit["calendar_deadline"])
    value = {"at": now.isoformat(), "cap_seconds": 7200, "exact_total_tool_wall_seconds": None,
        "conservative_charge_seconds": charge, "permit_to_this_record_seconds": elapsed,
        "parallel_and_unrecorded_allowance_seconds": 300, "closing_reserve_seconds": 600,
        "remaining_after_conservative_charge_seconds": 7200 - charge,
        "method": "用permit签发至收尾的整段历时覆盖工具与中间采样/推理空档，再为已发生短并行文件读取/未记录项保守加300秒，另保留600秒收尾。不是实测工具wall；各批原始实测单列，早期截断项仍unknown。",
        "test_parent_elapsed_seconds": [120.031, 20.453, 1.828],
        "prior_TASK122": {"conservative_charge_seconds": 1340.9775537, "known_command_wall_seconds": 37.4398905,
            "metadata_failures_at_least": 2, "unknown_subcommand_exits_timings_preserved": True},
        "prior_TASK120": {"wall_seconds": 69357.418110, "holding_seconds": 2943.704295, "failures": 149,
            "TASK117_original_failures": 81, "root_PG_starts": "64/64", "permission_restored": False},
        "specific_model_id": None, "new_cumulative_tokens": None,
        "new_runtime": {"provider_calls": 0, "actual_fee_microunits": 0, "PG": 0, "SQL": 0, "Docker": 0,
            "API_server": 0, "browser": 0, "Job": 0, "preview": 0, "Git_writes": 0, "subagents": 0},
        "tripwire_evidence": "batch3/summary.json", "no_claim_of_current_old_resource_scan": True}
    save("budget.json", value)
    print(json.dumps(value, ensure_ascii=False))
elif sys.argv[1] == "seal":
    now = datetime.datetime.now(datetime.timezone.utc)
    result = ROOT / "DocuN/results/TASK-123-result.md"
    raw = result.read_bytes()
    text = raw.decode("utf-8")
    assert text.startswith("# TASK-123") and len(text) > 3000
    for token in ("metering-evidence.json", "deployment-handoff.md", "finite-inputs.json", "product.diff", "batch3", "7200"):
        assert token in text, token
    snapshot = json.loads((OUT / "post-snapshot.json").read_bytes())
    for row in snapshot["products"]:
        assert sha((ROOT / row["path"]).read_bytes()) == row["post_sha256"], row["path"]
    budget = json.loads((OUT / "budget.json").read_bytes())
    closing_seconds = (now - datetime.datetime.fromisoformat(budget["at"])).total_seconds()
    assert closing_seconds < budget["closing_reserve_seconds"]
    rows = []
    excluded = {"delivery-manifest.json", "save-proof.json"}
    for path in sorted(OUT.rglob("*")):
        assert path.resolve().is_relative_to(OUT), str(path)
        if not path.is_file() or path.name in excluded: continue
        data = path.read_bytes()
        if path.suffix == ".json": json.loads(data)
        rows.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": len(data), "sha256": sha(data)})
    result_row = {"path": str(result.relative_to(ROOT)).replace("\\", "/"), "bytes": len(raw), "sha256": sha(raw)}
    rows.append(result_row)
    save("delivery-manifest.json", {"sealed_at": now.isoformat(), "rows": rows,
        "excluded_self_and_save_proof": sorted(excluded), "product_snapshot": "post-snapshot.json"})
    for row in rows:
        assert sha((ROOT / row["path"]).read_bytes()) == row["sha256"]
    proof = {"saved_and_reread": True, "at": now.isoformat(), "result": result_row,
        "artifact_rows": len(rows), "product_count": len(snapshot["products"]),
        "closing_elapsed_seconds": closing_seconds, "all_manifest_rows_reread_match": True,
        "final_acceptance_by_orchestrator_only": True}
    save("save-proof.json", proof)
    print(json.dumps(proof, ensure_ascii=False))
