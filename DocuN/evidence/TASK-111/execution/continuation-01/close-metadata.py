"""仅封存实际账与源码身份，不加载产品或验证夹具、不启动业务资源。"""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[5]
C01 = Path(__file__).resolve().parent
EXEC = C01.parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
    path.write_text(raw + "\n", encoding="utf-8")


now = time.monotonic_ns()
utc = datetime.now(timezone.utc).isoformat()
timing = read(C01 / "timing.json")
if timing["phase"] != "implementation_offline":
    raise SystemExit("phase already closed; do not duplicate")
elapsed = (now - timing["phase_start_ns"]) / 1e9
cutoff = timing["phase_start_ns"] + int(timing["caps_seconds"]["implementation_offline"] * 1e9)
segment = {"phase": timing["phase"], "start_ns": timing["phase_start_ns"],
           "end_ns": now, "seconds": elapsed, "next": "return_metadata",
           "cap_deadline_ns": cutoff, "cap_exceeded": now > cutoff,
           "first_stop_observed_utc": "2026-10-10T08:11:59Z",
           "recorded_utc": utc, "includes_elapsed_wait_and_reasoning": True}
with (C01 / "phase-events.jsonl").open("a", encoding="utf-8") as stream:
    stream.write(json.dumps(segment, ensure_ascii=False) + "\n")
timing["used_seconds"]["implementation_offline"] += elapsed
timing["phase"] = "return_metadata"
timing["phase_start_ns"] = now
timing["stopped_for"] = "implementation_offline_3600_seconds_exceeded"
timing["stop_observed_ns"] = now
timing["overrun_seconds"] = max(0, (now - cutoff) / 1e9)
write(C01 / "timing.json", timing)
budget = read(EXEC / "budget.json")
write(C01 / "budget-at-stop.json", budget)
write(C01 / "stop-receipt.json", {"permit": timing["permit"], "at_utc": utc,
      "at_ns": now, "implementation_deadline_ns": cutoff,
      "original_deadline_ns": timing["original_deadline_ns"],
      "implementation_elapsed_seconds": elapsed, "implementation_limit_seconds": 3600,
      "counts": budget["counts"], "active_batch": budget["active_batch"],
      "new_real_batches": 0, "new_renderer_creates": 0, "new_renderer_starts": 0,
      "reason": "actual_elapsed_cap_exceeded_not_a_new_authorization",
      "execution_compliance": "FAIL_forward_phase_cap_not_enforced_continuously",
      "scope": "账本与源码元数据封存；不是运行验证或停止树证明"})

rows = read(C01 / "pre-source.json")
known = {row["path"] for row in rows}
extra = ["backend/tests/fixtures/task111/runtime.py", "backend/app/preview/host_job.py"]
extra += [str(path.relative_to(ROOT)).replace("\\", "/")
          for path in (ROOT / "backend/tests/fixtures/task111").glob("c01*.py")]
for relative in extra:
    if relative not in known:
        rows.append({"path": relative, "pre_unavailable": True})
        known.add(relative)
out = []
diff_parts = []
delivery = C01 / "delivery"
delivery.mkdir(exist_ok=True)
for before in rows:
    relative = before["path"]
    source = ROOT / relative
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    prior = C01 / "pre" / relative
    old = prior.read_bytes() if prior.is_file() else None
    row = {"path": relative, "bytes": len(raw), "sha256": digest,
           "mtime_utc": datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(),
           "pre_sha256": hashlib.sha256(old).hexdigest() if old is not None else None,
           "pre_available": old is not None, "changed_from_saved_pre": old != raw if old is not None else None,
           "dynamic_as_run": None}
    destination = delivery / "source" / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    out.append(row)
    if old is not None and old != raw:
        diff_parts += difflib.unified_diff(old.decode("utf-8-sig").splitlines(True),
                    raw.decode("utf-8-sig").splitlines(True),
                    fromfile="saved-pre/" + relative, tofile="post/" + relative)
write(delivery / "final-source-identity.json", out)
(delivery / "saved-pre-to-post.diff").write_text("".join(diff_parts), encoding="utf-8")
write(delivery / "pre-gaps.json", [row for row in out if not row["pre_available"]])
print(json.dumps({"stop_recorded": True, "implementation_elapsed_seconds": elapsed,
                  "overrun_seconds": timing["overrun_seconds"], "saved_sources": len(out),
                  "pre_gaps": [row["path"] for row in out if not row["pre_available"]]}))
