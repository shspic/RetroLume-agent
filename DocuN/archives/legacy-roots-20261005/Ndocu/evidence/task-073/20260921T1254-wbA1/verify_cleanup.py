# -*- coding: utf-8 -*-
"""TASK-073 收尾核验：只输出容器非敏感状态字段（不输出 env/口令）。"""
import json
import subprocess

NAME = "retrolume-task-073-pg-20260921T1254-wbA1"
ID = "da18c806a871780500df3bdf2b612632afa7c5721e122e80437b6c248c1d2a62"

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
