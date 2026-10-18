"""只读冻结身份核对并登记本卡独立审计的初始控制账。"""
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[4]
AUDIT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    path = AUDIT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

def verify(rows, relative=False):
    result = []
    for row in rows:
        p = ROOT / row["path"] if relative else Path(row.get("path", row.get("absolute_path", "")))
        expected = row.get("sha256")
        exists = p.is_file()
        actual = digest(p) if exists else None
        result.append({"path": str(p), "exists": exists, "expected": expected, "actual": actual,
                       "match": actual == expected if expected is not None else not exists})
    return result

def main():
    now = dt.datetime.now(dt.timezone.utc)
    manifest = json.loads((ROOT / "DocuN/evidence/TASK-115/orchestration-20261013/input-manifest.json").read_text(encoding="utf-8-sig"))
    rules = json.loads((ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json").read_text(encoding="utf-8-sig"))
    checked = {"observed_utc": now.isoformat(), "rules": verify(rules),
               "context": verify(manifest["context"]), "frozen_files": verify(manifest["frozen_files"], True)}
    save("identity-before.json", checked)
    deltas = [r for r in manifest["frozen_files"] if r.get("change") != "unchanged"]
    save("frozen-deltas.json", deltas)
    control = AUDIT / "control"
    control.mkdir(exist_ok=True)
    receipt = control / "receipt.json"
    if not receipt.exists():
        conservative = dt.datetime.fromisoformat("2026-10-13T06:16:24.914938+00:00")
        save("control/receipt.json", {
            "task": "TASK-115", "round": "R-109", "permit": "TASK-115-STEP017-AUDIT-20261013",
            "client": "Codex desktop", "model": "GPT-6 (system label; no external model identity verification)",
            "independence": "用户转入当前新会话，未参与 TASK-113/114 实现，无子 Agent",
            "observed_utc": now.isoformat(), "observed_monotonic_ns": time.monotonic_ns(),
            "first_tool_utc": None, "first_tool_monotonic_ns": None,
            "timing_deviation": "首个工具调用未同步落盘 UTC/mono；不补造时间。用许可保存时点起算作为本轮活动和日历的保守上界，所有间隔连续计入。",
            "conservative_start_utc": conservative.isoformat(),
            "pre_receipt_charge_seconds": (now-conservative).total_seconds(),
            "exposure": "读取共享状态当前版本段时看到主控候选摘要；披露污染边界。未读 TASK114 结果自评或实现聊天，不用摘要支持审计结论。",
            "old_usage": {"roots":18,"pg_start":27,"windows":11,"api":5,"browser":3,"build":3,
                          "holding_seconds":377.280,"offline_seconds":51.238,"active_at_freeze_seconds":9185.438,
                          "old_calendar_seconds":55525.796,"old_net_active":"unknown"},
            "limits":{"active":21600,"calendar":172800,"roots":4,"create_attempts":2,"pg_success":1,
                      "source_start":3,"target07_start":2,"api":3,"browser":2,"holding":2400,
                      "business_holding":2100,"cleanup":300,"offline":3600},
            "new_counts":{"roots":0,"create_attempts":0,"pg_success":0,"source_start":0,"target07_start":0,
                          "api":0,"browser":0,"holding_seconds":0,"offline_test_seconds":0,
                          "native":0,"preview":0,"build":0,"provider":0,"fees":0,"public_network":0}})
    print(json.dumps({"manifest_keys":list(manifest),"checked":{k:len(v) for k,v in checked.items() if isinstance(v,list)},
                      "mismatches":{k:[r for r in v if not r["match"]] for k,v in checked.items() if isinstance(v,list)},
                      "deltas":[{"path":r["path"],"change":r.get("change")} for r in deltas]},ensure_ascii=False))

if __name__ == "__main__":
    main()
