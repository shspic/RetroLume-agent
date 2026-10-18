"""仅核对交回文件、规则指纹与资源元数据，不执行产品或测试。"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess
import time

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = Path(__file__).resolve().parent
EXEC = ROOT / "DocuN/evidence/TASK-111/execution"
OUT.mkdir(parents=True, exist_ok=True)

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def command(args):
    try:
        proc = subprocess.run(args, capture_output=True, timeout=20)
        if proc.returncode:
            return {"exit_code": proc.returncode, "object_read": False}
        return {"exit_code": 0, "data": json.loads(proc.stdout.decode("utf-8-sig"))}
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return {"error_type": type(exc).__name__, "object_read": False}

stamp = dt.datetime.now(dt.timezone.utc).isoformat()
rules = []
for entry in read(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json"):
    actual = identity(Path(entry["absolute_path"]))
    rules.append({"path": entry["absolute_path"], "expected": entry["sha256"], **actual,
                  "matches": actual["sha256"] == entry["sha256"]})
save("rules-check.json", rules)
if not all(entry["matches"] for entry in rules):
    raise SystemExit("锁定规则指纹变化，停止依赖写入")

returned = read(EXEC / "delivery/result-receipt.json")
report_path = ROOT / "DocuN/results/TASK-111-result.md"
report = {"path": str(report_path), **identity(report_path)}
report["matches_returned_receipt"] = all(report[key] == returned[key] for key in ("bytes", "sha256"))
if not report["matches_returned_receipt"]:
    raise SystemExit("交回结果指纹变化，需核对最新结果")
(OUT / "returned-result.md").write_bytes(report_path.read_bytes())

sources = []
for manifest in ("final-source-identity.json", "supplemental-source-identity.json"):
    for entry in read(EXEC / "delivery" / manifest):
        path = ROOT / entry["path"]
        if not path.resolve().is_relative_to(ROOT.resolve()):
            raise SystemExit("源清单越出项目")
        actual = identity(path)
        sources.append({"manifest": manifest, "path": entry["path"], **actual,
                        "expected_sha256": entry["sha256"], "matches": actual["sha256"] == entry["sha256"]})
save("source-check.json", sources)
if not all(entry["matches"] for entry in sources):
    raise SystemExit("交回源码发生漂移，需查明后出卡")

inputs = []
for relative in (
    "AGENTS.md", "DocuN/results/TASK-110-result.md", "DocuN/results/TASK-110-work-decision.md",
    "DocuN/tasks/TASK-111.md", "DocuN/results/TASK-111-work-decision.md",
    "DocuS/最终需求文档.MD", "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD", "DocuS/文档变更记录.MD",
    "DocuN/evidence/TASK-111/execution/budget.json",
    "DocuN/evidence/TASK-111/execution/session-start.json",
    "DocuN/evidence/TASK-111/execution/delivery/as-run-final-differences.json",
    "DocuN/evidence/TASK-111/execution/real-06/attempt-01/native-results.json",
    "DocuN/evidence/TASK-111/execution/real-06/attempt-02/http-effects.json",
    "DocuN/evidence/TASK-111/execution/cleanup-resume-20261010/cleanup-receipt.json",
):
    path = ROOT / relative
    inputs.append({"path": relative, **identity(path)})
save("input-receipt.json", inputs)
before = OUT / "before"
before.mkdir(exist_ok=True)
for relative in ("DocuN/tasks/TASK-111.md", "DocuN/results/TASK-111-work-decision.md",
                 "DocuS/架构动态文档.MD", "DocuS/执行动态文档.MD", "DocuS/文档变更记录.MD"):
    (before / relative.replace("/", "__")).write_bytes((ROOT / relative).read_bytes())

cid = "1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51"
pg = command(["docker", "container", "inspect", cid])
if "data" in pg:
    obj = pg.pop("data")[0]
    host = obj.get("HostConfig", {})
    state = obj.get("State", {})
    pg.update({"id": obj.get("Id"), "image": obj.get("Image"), "name": obj.get("Name"),
               "running": state.get("Running"), "pid": state.get("Pid"), "status": state.get("Status"),
               "mounts": [{key: mount.get(key) for key in ("Type", "Name", "Destination", "RW")} for mount in obj.get("Mounts", [])],
               "ports": host.get("PortBindings"), "memory": host.get("Memory"), "nano_cpus": host.get("NanoCpus"),
               "pids_limit": host.get("PidsLimit")})
image_id = "sha256:8ec35cf6df9c13eef0c3b15567e72ac0cd7382c19b586469cb4aaca48e8ef015"
renderer = command(["docker", "image", "inspect", image_id])
if "data" in renderer:
    obj = renderer.pop("data")[0]
    renderer.update({key: obj.get(key) for key in ("Id", "RepoTags", "RepoDigests", "Os", "Architecture")})
previews = command(["docker", "container", "ls", "-a", "--filter", "name=retrolume-task-111-g11-preview-", "--format", "{{json .}}"])
if "data" in previews:
    previews["entries"] = previews.pop("data")
elif previews.get("error_type") == "JSONDecodeError":
    proc = subprocess.run(["docker", "container", "ls", "-a", "--filter", "name=retrolume-task-111-g11-preview-", "--format", "{{.ID}}"], capture_output=True, timeout=20)
    previews = {"exit_code": proc.returncode, "container_ids": proc.stdout.decode("utf-8", errors="replace").split()}

ps = r"$ErrorActionPreference='Stop'; $taskListeners=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(18111,55451) } | Select-Object LocalAddress,LocalPort,OwningProcess); $taskProcesses=@(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(47588,52420) -or ($_.CommandLine -and ($_.CommandLine -match 'task111[\\/]workloop\.py|app\.preview\.production_reaper|app\.preview\.production_supervisor|uvicorn.*18111')) } | Select-Object ProcessId,ParentProcessId,Name,CreationDate); [PSCustomObject]@{listeners=$taskListeners;possible_owned_processes=$taskProcesses} | ConvertTo-Json -Depth 8 -Compress"
host = command(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps])
if "data" in host:
    host = host.pop("data")
resources = {"read_utc": stamp, "read_only": True, "pg": pg, "renderer_image": renderer, "previews": previews, "host": host,
             "scope": "仅精确对象只读元数据，不读取口令或完整Env；不启动资源、不作树空动态验收"}
save("resource-recheck.json", resources)

budget = read(EXEC / "budget.json")
session = read(EXEC / "session-start.json")
deadline = dt.datetime.fromisoformat(session["first_read_utc_conservative"]) + dt.timedelta(seconds=43200)
clock = {"read_utc": stamp, "host_monotonic_ns": time.monotonic_ns(), "old_deadline_ns": budget["deadline_ns"],
         "old_deadline_utc": deadline.isoformat(), "remaining_seconds": (budget["deadline_ns"] - time.monotonic_ns()) / 1e9,
         "utc_remaining_seconds": (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds(),
         "rule": "接续不重开原12小时，未知旧分类投入不补造"}
save("clock-recheck.json", clock)
save("returned-receipt.json", {"TASK": "TASK-111", "R": "R-105", "read_utc": stamp, "report": report,
     "rule_matches": len(rules), "source_matches": len(sources), "budget": budget,
     "root_cumulative_including_sealed_109": 78 + budget["counts"]["real_batches"],
     "implementation": "候选已返回，完整功能与最终源码动态验证未完成", "evidence": "部分A/B有效；renderer启动0；M01至M12未闭合",
     "execution_control": "原6根/2Reaper/6offline额度到达，旧分类投入不完整，失败和清场保留",
     "independent_audit": "完整G11仍待稳定后一次新隔离增强审计", "runtime_executed_by_orchestrator": False})
print(json.dumps({"report_matches": report["matches_returned_receipt"], "rules_matches": len(rules), "source_matches": len(sources),
      "pg": pg, "renderer_image": renderer, "previews": previews, "host": host, "clock": clock}, ensure_ascii=False))
