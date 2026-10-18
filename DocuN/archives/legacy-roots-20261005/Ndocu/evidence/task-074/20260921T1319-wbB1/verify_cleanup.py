# -*- coding: utf-8 -*-
"""TASK-074 收尾核验：只输出容器非敏感状态字段（不输出 env/口令）。"""
import json
import subprocess

NAME = "retrolume-task-074-pg-20260921T1319-wbB1"
ID = "7ef8f17e0ded014832ead684ddc5cf224fe91f0a4b38e953e2b6a467c7a4b3cc"
OLD_073 = "da18c806a871780500df3bdf2b612632afa7c5721e122e80437b6c248c1d2a62"

p = subprocess.run(["docker", "inspect", NAME], capture_output=True, timeout=30)
if p.returncode != 0:
    print("INSPECT_FAIL", p.stderr.decode("utf-8", "replace")[:300])
else:
    d = json.loads(p.stdout.decode("utf-8"))[0]
    out = {
        "name": d.get("Name"),
        "id_matches_run": d.get("Id") == ID,
        "image": d.get("Config", {}).get("Image"),
        "labels": d.get("Config", {}).get("Labels"),
        "state_running": d.get("State", {}).get("Running"),
        "state_status": d.get("State", {}).get("Status"),
        "exit_code": d.get("State", {}).get("ExitCode"),
        "finished_at": d.get("State", {}).get("FinishedAt"),
        "restart_policy": d.get("HostConfig", {}).get("RestartPolicy"),
        "port_bindings": d.get("HostConfig", {}).get("PortBindings"),
        "mounts": [{"type": m.get("Type"), "dst": m.get("Destination")} for m in d.get("Mounts", [])],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

po = subprocess.run(["docker", "inspect", OLD_073], capture_output=True, timeout=30)
if po.returncode == 0:
    d = json.loads(po.stdout.decode("utf-8"))[0]
    print(json.dumps({"old_073_container": {"running": d.get("State", {}).get("Running"),
                                            "status": d.get("State", {}).get("Status"),
                                            "note": "保留未触碰，状态仅供确认"}}, ensure_ascii=False))
else:
    print("old_073_container: inspect rc != 0（未触碰）")
