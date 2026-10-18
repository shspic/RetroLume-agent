"""冻结本卡真实文件、有限diff、复用边界、构建起源与预算，不生成通过结论。"""
import ast
from datetime import datetime,timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
from artifacts import ROOT,E,write,digest,files

start_ms=int(sys.argv[1])
pre=json.loads((E/"pre-manifest.json").read_text(encoding="utf-8-sig"))
before={r["path"]:r for r in pre}
# 原始pre-manifest只列修改前40个直接目标。dist的原字节已在第一次
# 离线入口及首次build前分别冻结，保留原导航，另加真实起源，不假称当时已列入pre。
dist_pre=json.loads((E/"as-run/offline-01/manifest.json").read_text(encoding="utf-8"))
dist_before=[]
for row in dist_pre["files"]:
    if row["path"].startswith("frontend/dist/"):
        item={**row,"snapshot":"DocuN/evidence/TASK-097/as-run/offline-01/files/"+row["path"]}
        assert digest(ROOT/item["snapshot"])==row["sha256"]
        dist_before.append(item);before[row["path"]]=item
write(E/"pre-dist-manifest.json",dist_before)
manifest=[];changed=[];limited=[]
selected=files()
for src in selected:
    relative=src.relative_to(ROOT).as_posix()
    destination=E/"final/files"/relative
    destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,destination)
    manifest.append({"path":relative,"sha256":digest(src),"bytes":src.stat().st_size})
product_new={p.relative_to(ROOT).as_posix() for p in (ROOT/"backend/app/learning").glob("*.py")}
product_new.add("frontend/src/activities/LearningResult.tsx")
product_new.add("frontend/src/activities/learningIntentMatch.ts")
tests_new={p.relative_to(ROOT).as_posix() for p in (ROOT/"backend/tests").glob("test_learning_*.py")}
tests_new|={p.relative_to(ROOT).as_posix() for p in (ROOT/"backend/tests/fixtures/task097").glob("*.py")}
tests_new|={p.relative_to(ROOT).as_posix() for p in (ROOT/"frontend/tests").glob("task097-*.mjs")}
targets=set(before)|product_new|tests_new|{p.relative_to(ROOT).as_posix() for p in (ROOT/"frontend/dist").rglob("*") if p.is_file()}
for relative in sorted(targets):
    path=ROOT/relative
    old=before.get(relative)
    newhash=digest(path) if path.is_file() else None
    oldhash=old["sha256"] if old else None
    status="unchanged" if newhash==oldhash else "modified" if oldhash and newhash else "deleted" if oldhash else "added"
    row={"path":relative,"status":status,"pre_sha256":oldhash,"post_sha256":newhash,
        "bytes":path.stat().st_size if path.is_file() else 0}
    if status!="unchanged":changed.append(row)
    if status!="unchanged" and not relative.startswith("frontend/dist/"):
        original=(E/"pre"/relative).read_text(encoding="utf-8-sig") if old else ""
        current=path.read_text(encoding="utf-8-sig") if path.is_file() else ""
        limited.extend(difflib.unified_diff(original.splitlines(True),current.splitlines(True),
            fromfile="pre/"+relative if old else "/dev/null",tofile="post/"+relative,n=3))
write(E/"post-manifest.json",manifest);write(E/"changes.json",changed)
(E/"limited.diff").write_text("".join(limited),encoding="utf-8")
# 原件夹具仅选内容地址目录，不包含运行配置、环境或口令。
originals=[]
for runtime in (E/"runtime").rglob("originals"):
    if not runtime.is_dir():continue
    for path in runtime.rglob("*"):
        if path.is_file():
            rel=path.relative_to(ROOT)
            dst=E/"final/fixtures"/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dst)
            originals.append({"path":rel.as_posix(),"sha256":digest(path),"bytes":path.stat().st_size})
write(E/"original-fixture-snapshot.json",originals)
indexed=json.loads((E/"input-verification.json").read_text(encoding="utf-8-sig"))
write(E/"post-index-check.json",[{"path":r["path"],"pre_sha256":r["actual"],
    "post_sha256":digest(ROOT/r["path"]),"changed":digest(ROOT/r["path"])!=r["actual"]} for r in indexed])
# 既有写/锁/恢复、主要模型与迁移的语义或字节不变，不用静态检查替代动态结果。
repo="backend/app/activities/repository.py"
old=(E/"pre"/repo).read_bytes();new=(ROOT/repo).read_bytes()
names={"ActivitySpec","ActivityLease","claim_lease","settle_execution_window","cancel_activity","admit",
    "mark_dispatch_started","record_outcome","recover_window","begin_window_close","revise_scope"}
def bodies(raw):
    return {node.name:ast.dump(node,include_attributes=False) for node in ast.walk(ast.parse(raw))
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and node.name in names}
a,b=bodies(old),bodies(new)
core={"repository_existing_bytes_unchanged_prefix":new.startswith(old),"compared_existing_names":sorted(a),
    "all_existing_named_bodies_unchanged":all(b.get(k)==v for k,v in a.items()),"write_subjects_changed":[]}
core["repository_existing_prefix_equal_after_CRLF_normalization"]=new.replace(b"\r\n",b"\n").startswith(old.replace(b"\r\n",b"\n"))
core["byte_prefix_note"]="末尾既有只读read_operation的行尾由CRLF转LF，旧正文和全部既有写/锁/恢复主体未改；两个只读助手追加其后"
unchanged=[]
for relative in ["backend/app/worker/launcher.py","backend/app/worker/session.py","backend/app/worker/gate.py",
    "backend/app/worker/supervisor_ipc.py","backend/app/worker/supervisor_main.py","backend/app/worker/windows_job.py",
    "backend/app/worker/one_tool.py","backend/app/capabilities/transport.py","backend/app/capabilities/tools.py",
    "backend/app/capabilities/tool_execution.py","backend/app/local_session.py"]:
    p=E/"pre"/relative
    if not p.exists():raise ValueError("冻结主体pre缺失: "+relative)
    unchanged.append({"path":relative,"pre_sha256":digest(p),"post_sha256":digest(ROOT/relative),"unchanged":digest(p)==digest(ROOT/relative)})
core["frozen_modules"]=unchanged
core["migrations"]=[{"path":p.relative_to(ROOT).as_posix(),"sha256":digest(p)} for p in (ROOT/"backend/migrations").glob("00[1-8]_*.sql")]
assert core["all_existing_named_bodies_unchanged"] and core["repository_existing_prefix_equal_after_CRLF_normalization"] and all(r["unchanged"] for r in unchanged)
write(E/"core-freeze-check.json",core)
# 修正diff只从真实as-run原件计算，不改失败原件。
for label in ["integration-01-pg","integration-02-pg","integration-03-business","integration-04-business",
    "integration-05-business","integration-06-browser","integration-07-browser","integration-08-browser"]:
    prior=E/"as-run"/label/"files"
    diff=[]
    for relative in sorted(product_new|tests_new|{"backend/app/capabilities/gateway.py","backend/app/learning/api.py",
        "frontend/src/activities/ActivityWorkspace.tsx"}):
        p=prior/relative;q=ROOT/relative
        if p.is_file() and q.is_file() and digest(p)!=digest(q):
            diff.extend(difflib.unified_diff(p.read_text(encoding="utf-8-sig").splitlines(True),q.read_text(encoding="utf-8-sig").splitlines(True),
                fromfile=label+"/"+relative,tofile="final/"+relative,n=3))
    (E/(label+"-to-final.diff")).write_text("".join(diff),encoding="utf-8")
builds=[]
for directory in sorted((E/"as-run").glob("build-*")):
    asrun=json.loads((directory/"manifest.json").read_text(encoding="utf-8"))
    run=json.loads((directory/"run.json").read_text(encoding="utf-8"))
    outputs={k:v for k,v in run["post_hashes"].items() if k.startswith("frontend/dist/")}
    builds.append({"label":directory.name,"command":asrun["command"],"exit_code":run["exit_code"],
        "seconds":run["elapsed_seconds"],"source_inputs":[r for r in asrun["files"] if r["path"].startswith("frontend/src/")
            or r["path"] in {"frontend/package.json","frontend/package-lock.json","frontend/index.html","frontend/tsconfig.json"}],"outputs":outputs,
        "raw_stdout":str((directory/"stdout.bin").relative_to(ROOT)),"raw_stderr":str((directory/"stderr.bin").relative_to(ROOT))})
served=[]
for p in E.glob("integration-*/browser-report.json"):
    report=json.loads(p.read_text(encoding="utf-8"))
    served.append({"batch":p.parent.name,"aggregate_ok":report["ok"],"assets":report["assets"]})
write(E/"build-binding.json",{"builds":builds,"browser_actual_served":served,"final_build":builds[-1]["label"],
    "final_bundle_browser_served":False,"browser_bundle":"build-02","final_ui_change":"意图匹配与迟到保护；纯函数+typecheck/build，浏览器not_run"})
ledger=json.loads((E/"attempt-ledger.json").read_text(encoding="utf-8"))
sup=[]
for p in E.glob("integration-*/sup-launch-*.json"):
    sup.append({"batch":p.parent.name,**json.loads(p.read_text(encoding="utf-8"))})
sessions=[{"batch":p.parent.name,**json.loads(p.read_text(encoding="utf-8"))} for p in E.glob("integration-*/session-*.json")]
jobs=[{"batch":p.parent.name,**json.loads(p.read_text(encoding="utf-8"))} for p in E.glob("integration-*/job-close-*.json")]
claims=[]
for s in sessions:claims.append({"batch":s["batch"],"run_tag":s["run_tag"],"generation":s["generation"],
    "reached_claim":s["generation"] is not None,"state":s["state"],"active_processes_at_end":s["active_processes_at_end"]})
# 一个旧普通直接调用在安装观察包装器前绑定函数，未保存SessionOutcome；真实Job、进程及发送原件仍在。
write(E/"supervision-ledger.json",{"actual_launch_attempts":len(sup),"launches":sup,"session_receipts":sessions,
    "claim_observations":claims,"real_job_close":jobs,"missing_session_outcome_count":len(sup)-len(sessions),
    "missing_reason":"legacy直接调用先导入原run_one_call，再安装观察器；不减少启动计数，claim按真实Job代次补证"})
budget={"active_started_at":datetime.fromtimestamp(start_ms/1000,timezone.utc).isoformat(),"frozen_at":datetime.now(timezone.utc).isoformat(),
    "active_wall_upper_bound_seconds":time.time()-start_ms/1000,"contract_creation_seconds_from_start":(E/"implementation-contract.md").stat().st_ctime-start_ms/1000,
    "offline_seconds":sum(r.get("seconds",0) for r in ledger),"business_seconds":sum(r.get("business_seconds",0) for r in ledger),
    "cleanup_seconds":sum(r.get("cleanup_seconds",0) for r in ledger),"entries":sum(r["category"]=="integration_entry" for r in ledger),
    "container_starts":sum(r["category"]=="container_start" for r in ledger),"supervision_sessions":len(sup),
    "browser_actual_launch_attempts":len(list(E.glob("integration-*/browser-actual-start.json"))),
    "browser_driver_attempts_conservative":len(list(E.glob("integration-*/browser-launch.json"))),
    "limits":{"active_seconds":28800,"offline_seconds":2400,"business_seconds":3600,"cleanup_seconds":600,"entries":8,"container_starts":8,"supervision_sessions":16,"browser_starts":4},
    "stop_reason":"8集成入口和8容器start已达上限；任何剩余秒数或监督余量不授权新入口",
    "old095_history":"原入口10/start9/业务claim10/保守监督14/279.677业务秒/24.592清理秒及旧未知均不更改，不使用余量"}
budget["offline_measured_seconds"]=budget["offline_seconds"]
budget["offline_unmetered_consistency_charged_seconds"]=60
budget["offline_unmetered_note"]="首次证据finalize及一次只读核对的输出编码失败未纳入独立秒表；用60秒保守计入额度，非实际耗时宣称；普通阅读/写文计主动墙钟上界"
budget["offline_seconds"]+=60
write(E/"budget-final.json",budget)
environment={"platform":sys.platform,"python":sys.version,"actual_model":"Codex based on GPT-6; exact client model identifier unavailable",
    "client":"Codex desktop","cwd":str(ROOT),"timezone":"Asia/Shanghai","subagents":0,"network_model_cost":"zero real provider/model calls and fees"}
write(E/"environment.json",environment)
state=json.loads((E/"execution-ledger.json").read_text(encoding="utf-8"))
state["original_registered_started_at"]=state["started_at"];state["active_started_at"]=budget["active_started_at"]
state["status"]="partial_candidate_implementation";state["budget_actual"]=budget;state["accounting_source"]="attempt-ledger.json + actual SUP/browser records; card only, not project status"
write(E/"execution-ledger.json",state)
print(json.dumps({"final_snapshot_files":len(manifest),"changed_files":len(changed),"entries":budget["entries"],"sup":len(sup),
    "active_seconds":round(budget["active_wall_upper_bound_seconds"],3),"core_subjects_unchanged":True,"final_bundle_browser_run":False}))
