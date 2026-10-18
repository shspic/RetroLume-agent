"""TASK-095 收尾：账目核数、最终快照与哈希、凭据清理、终止条目。"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402


def relative(path_text: str) -> str:
    text = path_text.replace("\\", "/")
    root = str(common.ROOT).replace("\\", "/")
    if text.startswith(root):
        text = text[len(root):]
    return text.lstrip("/")


def main() -> None:
    entries = json.loads((common.EVIDENCE / "attempt-ledger.json").read_text(encoding="utf-8"))
    starts = sum(int(entry.get("container_starts") or 0) for entry in entries)
    business = round(sum(float(entry.get("business_seconds") or 0) for entry in entries), 1)
    cleanup = round(sum(float(entry.get("cleanup_seconds") or 0) for entry in entries), 1)
    print("entries:", len(entries), "container_starts:", starts,
          "business_s:", business, "cleanup_s:", cleanup)
    for entry in entries:
        print(" -", entry.get("at"), entry.get("batch"), entry.get("phase"),
              entry.get("result", ""), (entry.get("reason") or "")[:40])

    pre = {}
    previous = common.EVIDENCE.parent / "TASK-094"
    for item in json.loads((previous / "files-read-hashes.json").read_text(encoding="utf-8")):
        pre[relative(item["path"])] = item["sha256"]
    for item in json.loads((previous / "revision-01" / "files-read-hashes-revision-01.json").read_text(encoding="utf-8")):
        pre[relative(item["path"])] = item["sha256"]
    pre["backend/app/activities/repository.py"] = "26c8eecff3c09ac34a4025cf2901eeedccd83250b9def788e1b53748d4168bc3"
    pre["backend/app/activities/service.py"] = "1718c9ef46e2d3fbebc90ce72a64211a36a53011bb53df247fffeb76591dbe03"

    current = common.product_hashes()
    record = {}
    snapshot = common.EVIDENCE / "final-snapshot"
    for rel, post in current.items():
        record[rel] = {"pre": pre.get(rel), "post": post, "changed": pre.get(rel) != post}
        destination = snapshot / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(common.ROOT / rel, destination)
    (snapshot / "product-hashes-final.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    changed = [key for key, value in record.items() if value["changed"]]
    print("snapshot files:", len(record), "changed/new:", len(changed))
    for key in sorted(changed):
        print("   *", key, record[key]["post"][:16])

    dsn_file = common.RUNTIME / "dsn.json"
    if dsn_file.is_file():
        dsn_file.unlink()
    print("dsn.json removed:", not dsn_file.exists())

    facts = common.inspect_guard()
    print("container state now:", facts["state_running"], facts["pid"])

    common.append_attempt({
        "batch": "post-batch-fixes", "phase": "offline-fix",
        "note": "UI展开操作未取回单操作正文与面板误用列表行渲染两处缺陷修复（产品文件）；typecheck/build通过；批次/会话/启动上限已尽，未再做实机复验",
        "result": "fixed-offline-live-reverification-pending",
    })
    common.append_attempt({
        "batch": "stop-decision", "phase": "budget-stop",
        "note": "同缺陷两次有据修正并以构建验证；批次入口与监督会话各超上限1次（含首检夹具误判与运行期才可见缺陷返工），按卡面停止规则停止实机运行并交回",
        "result": "stopped-per-card-rule",
    })
    print("closing entries appended")


if __name__ == "__main__":
    main()
