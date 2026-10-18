"""独立于容器和主控制器的固定截止救援，仅停止登记的精确CID。"""
import json
from pathlib import Path
import sys
import time

from supervisor import atomic_json, docker_call, inspect_owned, process_birth


def main():
    registry = Path(sys.argv[1]).resolve()
    result_path = registry.with_name("reaper-result.json")
    data = json.loads(registry.read_text(encoding="utf-8"))
    fixed_deadline = data["controller_deadline_ns"]
    current = data
    bound_cid = None
    atomic_json(registry.with_name("reaper-ready.json"), {"pid": __import__("os").getpid(), "birth": process_birth(__import__("os").getpid()), "deadline_ns": fixed_deadline})
    while time.monotonic_ns() < fixed_deadline:
        try:
            current = json.loads(registry.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        if current.get("complete"):
            atomic_json(result_path, {"state": "控制器已确认收尾", "at_ns": time.monotonic_ns()})
            return
        cid = current.get("cid")
        if cid and cid != bound_cid:
            inspect_owned(data["docker"], cid, current["image"], data["nonce"])
            bound_cid = cid
            atomic_json(registry.with_name("reaper-bound.json"), {"cid": cid, "image": current["image"], "runtime_deadline_ns": current["runtime_deadline_ns"]})
        expired = time.monotonic_ns() >= current.get("runtime_deadline_ns", fixed_deadline)
        parent_lost = process_birth(data["parent_pid"]) != data["parent_birth"]
        if cid and (expired or parent_lost):
            try:
                before = inspect_owned(data["docker"], cid, current["image"], data["nonce"])
                killed = docker_call(data["docker"], ["kill", cid]) if before["state"]["Running"] else None
                after = inspect_owned(data["docker"], cid, current["image"], data["nonce"])
                atomic_json(result_path, {"state": "救援已执行", "reason": "截止" if expired else "控制器身份丢失", "before": before["state"], "kill": killed, "after": after["state"], "tree_confirmation": "仍需原件核对"})
            except Exception as error:
                atomic_json(result_path, {"state": "停止未确认", "error": str(error)[:2000]})
            return
        time.sleep(0.1)
    atomic_json(result_path, {"state": "独立总截止到达", "cid": current.get("cid"), "tree_confirmation": "未确认"})


if __name__ == "__main__":
    main()
