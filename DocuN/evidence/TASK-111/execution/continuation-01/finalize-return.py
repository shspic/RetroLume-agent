"""封闭交回元数据并原字节附回旧结果；不加载产品、不运行验收。"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[5]
C01 = Path(__file__).resolve().parent
EXEC = C01.parent
DELIVERY = C01 / "delivery"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic(path, value):
    pending = path.with_suffix(path.suffix + ".return-new")
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
    with pending.open("w", encoding="utf-8") as stream:
        stream.write(raw + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(pending, path)


if (DELIVERY / "returned-receipt.json").exists():
    raise SystemExit("already finalized; do not duplicate receipt")
timing = read(C01 / "timing.json")
budget = read(EXEC / "budget.json")
resource = read(C01 / "resource-close.json")
stop = read(C01 / "stop-receipt.json")
if timing["phase"] != "return_metadata" or budget["active_batch"] is not None:
    raise SystemExit("unexpected live phase or batch")
old = (C01 / "pre/TASK-111-result.md").read_bytes()
result_path = ROOT / "DocuN/results/TASK-111-result.md"
old_sha = hashlib.sha256(old).hexdigest()
if len(old) != 25338 or old_sha != "72bb21f612fcee8287c77099383721986ed844fc8e290eacf23e9f501afd2fe0" or result_path.read_bytes() != old:
    raise SystemExit("original result changed; refuse to overwrite")
event_path = EXEC / "events.jsonl"
pre_events = (C01 / "pre/events.jsonl").read_bytes()
if not event_path.read_bytes().startswith(pre_events):
    raise SystemExit("original event prefix changed")
now = time.monotonic_ns()
utc = datetime.now(timezone.utc).isoformat()
gross = (now - timing["phase_start_ns"]) / 1e9
cleanup = resource["seconds"]
metadata = gross - cleanup
if metadata < 0:
    raise SystemExit("invalid non-overlap classification")
timing["used_seconds"]["metadata"] += metadata
timing["used_seconds"]["cleanup"] = cleanup
timing["return_metadata_seconds"] = metadata
timing["phase"] = "complete"
timing["phase_start_ns"] = now
timing["result_status"] = "PARTIAL_STOPPED_CAP_EXCEEDED"
timing["at_utc"] = utc
timing["implementation_cap_breach_preserved"] = True
atomic(C01 / "timing.json", timing)
with (C01 / "phase-events.jsonl").open("a", encoding="utf-8") as stream:
    stream.write(json.dumps({"phase":"return_metadata", "start_ns":now-int(gross*1e9),
        "end_ns":now, "gross_seconds":gross, "metadata_seconds":metadata,
        "cleanup_seconds":cleanup, "cleanup_inside_segment_deducted_once":True,
        "next":"complete", "at_utc":utc}, ensure_ascii=False) + "\n")
with event_path.open("ab") as stream:
    for kind, data in (("c01_stop_receipt", {"receipt":str(C01 / "stop-receipt.json"),
            "reason":stop["reason"], "execution_compliance":stop["execution_compliance"]}),
            ("c01_resource_close", {"receipt":str(C01 / "resource-close.json"),
            "seconds":cleanup, "read_only":True, "new_resources_started":False,
            "scope":"resource inventory only; no dynamic TreeProof or budget settlement"})):
        budget["events"] += 1
        row = {"event":budget["events"], "kind":kind, "pid":os.getpid(),
               "at_ns":now, "at_utc":utc, "data":data}
        stream.write((json.dumps(row,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8"))
    stream.flush()
    os.fsync(stream.fileno())
budget["time_seconds"]["cleanup"] += cleanup
atomic(EXEC / "budget.json", budget)
atomic(C01 / "budget-at-return.json", budget)
prefix_path = C01 / "result-prefix.md"
prefix = prefix_path.read_text(encoding="utf-8")
footer = (f"最终封账于{utc}：本轮metadata累计{timing['used_seconds']['metadata']:.6f}秒，"
          f"实施／关联离线7530.953秒，real=0，独立资源核查cleanup={cleanup:.7f}秒；"
          f"累计账cleanup={budget['time_seconds']['cleanup']:.7f}秒。"
          "交回段扣去内含的资源核查一次，旧原件及超限事实保留。\n\n")
marker = "## 以下保留续作前25338字节完整原报告"
if prefix.count(marker) != 1 or "*" in prefix:
    raise SystemExit("invalid report prefix")
prefix = prefix.replace(marker, footer + marker)
prefix_path.write_text(prefix, encoding="utf-8")
prefix_raw = prefix.encode("utf-8")
complete = prefix_raw + old
pending = result_path.with_suffix(".md.return-new")
with pending.open("wb") as stream:
    stream.write(complete)
    stream.flush()
    os.fsync(stream.fileno())
os.replace(pending, result_path)
saved = result_path.read_bytes()
if saved != complete or saved[-len(old):] != old:
    raise SystemExit("saved result differs")
manifest = []
for path in sorted(C01.rglob("*")):
    if not path.is_file() or path.name in {"returned-receipt.json","delivery-manifest.json"}:
        continue
    raw = path.read_bytes()
    manifest.append({"path":str(path.relative_to(ROOT)).replace("\\","/"),
                     "bytes":len(raw), "sha256":hashlib.sha256(raw).hexdigest()})
atomic(DELIVERY / "delivery-manifest.json", manifest)
receipt = {"permit":timing["permit"], "at_utc":utc, "result_path":str(result_path),
    "bytes":len(saved), "sha256":hashlib.sha256(saved).hexdigest(), "readable":True,
    "original_suffix_bytes":len(old), "original_suffix_sha256":old_sha,
    "original_suffix_exact":True, "original_events_prefix_exact":True,
    "status":"PARTIAL_STOPPED_CAP_EXCEEDED", "new_real_batches":0,
    "new_renderer_creates":0, "new_renderer_starts":0,
    "counts":budget["counts"], "time_seconds":budget["time_seconds"],
    "forward_used_seconds":timing["used_seconds"],
    "metadata_cap_ok":timing["used_seconds"]["metadata"]<=1200,
    "fixed_original_deadline_unmodified":budget["deadline_ns"]==902913370092600,
    "manifest_items":len(manifest),
    "manifest_sha256":hashlib.sha256((DELIVERY/"delivery-manifest.json").read_bytes()).hexdigest(),
    "no_full_audit_or_release_signature":True}
atomic(DELIVERY / "returned-receipt.json", receipt)
print(json.dumps(receipt,ensure_ascii=False))
