"""卡内预算停止后的只读收尾；不启动资源、不连接数据库、不恢复安装。"""
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
here = Path(__file__).absolute().parent
root = here.parents[3]
spec = importlib.util.spec_from_file_location("task127_final_support", here / "win-support.py")
native = importlib.util.module_from_spec(spec); spec.loader.exec_module(native)
def sha(raw):return hashlib.sha256(raw).hexdigest()
state_raw = (here / "checkpoint.json").read_bytes()
state = json.loads(state_raw)
docker = Path(os.environ["LOCALAPPDATA"]) / "Programs/DockerDesktop/resources/bin/docker.exe"
env = {key: os.environ[key] for key in ("SystemRoot", "WINDIR", "TEMP", "TMP", "ComSpec", "USERPROFILE", "APPDATA", "LOCALAPPDATA") if key in os.environ}
env["PATH"] = str(docker.parent) + os.pathsep + str(Path(env["SystemRoot"]) / "System32")
commands = []
def inspect(kind, identity):
    started = time.perf_counter()
    args = [str(docker), kind, "inspect", identity]
    result = subprocess.run(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    commands.append({"argv": args, "exit_code": result.returncode, "wall_seconds": time.perf_counter() - started})
    assert result.returncode == 0
    return json.loads(result.stdout)[0]
objects, secret_values = {}, []
for slot, known in state["slots"].items():
    container = inspect("container", known["cid"])
    assert container["Id"] == known["cid"] and container["Image"] == known["created_projection"]["image_id"]
    assert container["Name"].lstrip("/") == known["created_projection"]["mounts"][0]["Name"].removesuffix("-data")
    assert container["State"]["Running"] is False and container["State"]["Pid"] == 0
    volume = inspect("volume", known["volume"]["Name"])
    assert all(volume.get(key) == known["volume"].get(key) for key in ("Name", "CreatedAt", "Driver", "Labels", "Mountpoint"))
    network = inspect("network", known["network_id"])
    assert all(network[key] == known["network"][key] for key in ("Name", "Id", "Created", "Driver", "Labels"))
    roots = [native.file_identity(Path(row["path"])) for row in known["roots"]]
    assert roots == known["roots"]
    home = Path(known["home"])
    secret_values.extend(native.protect_secret((home / "credentials.dpapi").read_bytes(), decrypt=True).split(b"\0"))
    receipts = []
    receipt_name = "wrong-database_oid.jsonl" if slot == "source" else "expected-unknown.jsonl"
    receipt_path = home / "receipts" / receipt_name
    raw = receipt_path.read_bytes(); rows = [json.loads(line) for line in raw.splitlines()]
    copy_path = here / "entry-03" / (slot + "-" + receipt_name.replace(".jsonl", "-receipt.jsonl"))
    assert copy_path.read_bytes() == raw
    assert len(rows) == 2 and rows[-1] == {"event": "stopped", "reason": "installation_stopped", "confirmed_stages": [], "unknown_stage": None}
    receipts.append({"private_path": str(receipt_path), "evidence_path": str(copy_path), "sha256": sha(raw), "lines": len(rows), "final": rows[-1]})
    objects[slot] = {"cid": container["Id"], "image_id": container["Image"], "created": container["Created"], "state": container["State"],
                     "mounts": container["Mounts"], "volume": {key: volume.get(key) for key in ("Name", "CreatedAt", "Driver", "Labels")},
                     "network": {key: network[key] for key in ("Name", "Id", "Created", "Driver", "Labels")}, "roots": roots,
                     "last_observed_database_identity": known["database_identity"], "database_reopened_during_finalization": False,
                     "receipts": receipts}
manifest = json.loads((here.parent / "orchestration-20261022/input-manifest.json").read_bytes())
inputs = []
for row in manifest["sources"]:
    raw = Path(row["absolute_path"]).read_bytes()
    inputs.append({"path": row["absolute_path"], "bytes": len(raw), "sha256": sha(raw), "unchanged": sha(raw) == row["sha256"]})
assert all(row["unchanged"] for row in inputs)
pre = json.loads((here / "pre-snapshot.json").read_bytes())
public = Path("D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4")
rules = [{"path": row["path"], "sha256": sha((public / row["path"]).read_bytes()), "unchanged": sha((public / row["path"]).read_bytes()) == row["sha256"]} for row in pre["rules"]]
assert all(row["unchanged"] for row in rules)
for name in ("README.md", "deploy/normal-install.md"):
    assert (here / "pre" / name).read_bytes() == (root / name).read_bytes()
    destination = here / "post" / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:stream.write((root / name).read_bytes())
with (here / "allowed-documents.diff").open("x", encoding="utf-8") as stream:stream.write("")
scanned = []
for directory in (here, here / "pre", here / "pre/deploy", here / "entry-02", here / "entry-03"):
    for path in directory.iterdir():
        if not path.is_file():continue
        raw = path.read_bytes()
        assert not any(value in raw for value in secret_values)
        scanned.append({"path": str(path), "bytes": len(raw), "sha256": sha(raw)})
for slot, known in state["slots"].items():
    for path in (Path(known["home"]) / "config").iterdir():
        if path.is_file():assert not any(value in path.read_bytes() for value in secret_values)
owners = native.port_owners({55482, 55483, 18122, 18124, 18126})
assert not any(row["state"] == 2 for row in owners)
record = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "objects": objects, "inputs": inputs, "rules": rules, "read_only_commands": commands,
          "checkpoint_sha256": sha(state_raw), "candidate_port_observations": owners, "no_listening_selected_pg_or_api_candidate_ports": True,
          "api_started": state["api_starts"], "api_pids_ever_owned": [], "memory_available_mib": native.available_mib(),
          "pg_holding_seconds": sum(row["seconds"] for row in state["pg_intervals"]), "api_holding_seconds": 0,
          "secret_scan": {"matched": 0, "evidence_files": len(scanned), "scan_bytes": "only current task execution and own new config files"},
          "evidence_inventory": scanned, "q": "FROZEN", "T0": None, "provider_calls_by_task": 0, "provider_fees_cny_by_task": 0,
          "outbound_claim_scope": "No task provider/browser/renderer/job launched; native API never started. Not a platform-wide traffic claim.",
          "entries": state["entries"], "further_entry_permitted": False, "root_cause_stable": False, "all_resource_objects_retained": True}
with (here / "final-checkpoint.json").open("xb") as out:out.write(state_raw)
with (here / "post-snapshot.json").open("x", encoding="utf-8") as out:json.dump(record, out, ensure_ascii=False, indent=2)
print(json.dumps({"post_snapshot_saved": True, "stopped_cids": {key: value["cid"] for key, value in objects.items()}, "inputs_unchanged": len(inputs), "rules_unchanged": len(rules), "holding_pg_seconds": record["pg_holding_seconds"], "secret_matches": 0, "entries": state["entries"]}, ensure_ascii=False))
