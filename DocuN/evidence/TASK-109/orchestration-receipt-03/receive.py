"""回收C02真实启动/Crashpad/精确停止原件，不运行或重启产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-109"
C02 = BASE / "execution/continuation-02"
OUT = BASE / "orchestration-receipt-03"
CID = "5bd9e24d2a8ba06403f4daf4120aedcd7fe0ef4f0e3ae5f162b723918f189059"


def sha(data): return hashlib.sha256(data).hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name; assert not p.exists(), "不覆盖已完成回收"
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    proof = load(C02 / "delivery-proof.json")
    report = (ROOT / "DocuN/results/TASK-109-result.md").read_bytes()
    old = (BASE / "orchestration-receipt-02/TASK-109-C01-as-returned.md").read_bytes()
    assert len(report)==proof["result"]["bytes"]==37685 and sha(report)==proof["result"]["sha256"] and report.endswith(old)
    current = load(BASE / "orchestration-receipt-02/current-baseline.json")
    for rel, expected in current.items(): assert sha((ROOT/rel).read_bytes())==expected
    extra = proof["new_source"]; path=Path(extra["path"]); assert sha(path.read_bytes())==extra["sha256"]
    current[str(path.relative_to(ROOT)).replace("\\","/")]=extra["sha256"]
    for row in proof["old_sessions"]: assert sha(Path(row["path"]).read_bytes())==row["expected_sha256"]
    root = load(C02 / "root-04/root-result.json")
    assert root["state"]=="ERROR" and root["global_ordinal"]==74 and not root["business_phase_entered"]
    observations=load(C02 / "root-04/observations.json")
    assert [row["kind"] for row in observations]==["processes_before_launch","load_identity","terminal"]
    assert observations[0]["data"]["own_uid"]==10001 and observations[1]["data"]["package"]=="1.62.1"
    msg=observations[2]["data"]["message"]
    assert len(msg)==2000 and "chrome_crashpad_handler: --database is required" in msg
    cleanup=load(C02 / "root-04/cleanup.json")
    assert cleanup["cid"]==CID and cleanup["kill"]["code"]==cleanup["wait"]["code"]==0 and cleanup["wait"]["stdout"].strip()=="137"
    state=cleanup["after"]["state"]; assert not state["Running"] and state["Pid"]==0 and not state["Restarting"]
    process=subprocess.run(["docker.exe","inspect","--type","container",CID],capture_output=True,timeout=15)
    assert process.returncode==0
    raw=json.loads(process.stdout)[0]
    assert raw["Id"]==CID and not raw["State"]["Running"] and raw["State"]["Pid"]==0
    assert raw["Config"]["Labels"]["retrolume.action-permit"]=="TASK-109-G11-C02-20261009"
    selected={}
    keys={"HOME","XDG_CONFIG_HOME","XDG_CACHE_HOME","XDG_RUNTIME_DIR","TMPDIR"}
    for row in raw["Config"].get("Env",[]):
        name,sep,value=row.partition("=")
        if name in keys and sep: selected[name]=value
    live={"cid":CID,"image":raw["Image"],"state":raw["State"],"user":raw["Config"].get("User"),
          "declared_home_paths_only":selected,"tmpfs_declared":raw["HostConfig"].get("Tmpfs"),
          "runtime_directory_uid_mode_writability": "未观测；stopped后的Config不能代替活进程目录事实",
          "raw_Env_not_saved":True,"not_restarted":True}
    before=[]
    for rel in ["DocuS/执行动态文档.MD","DocuS/架构动态文档.MD","DocuS/文档变更记录.MD","DocuN/tasks/TASK-109.md","DocuN/results/TASK-109-work-decision.md"]:
        data=(ROOT/rel).read_bytes(); p=OUT/"before"/rel; p.parent.mkdir(parents=True,exist_ok=True); assert not p.exists(); p.write_bytes(data)
        before.append({"path":rel,"sha256":sha(data),"bytes":len(data)})
    copy=OUT/"TASK-109-C02-as-returned.md"; assert not copy.exists(); copy.write_bytes(report)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat()
    sources=[]
    for p in list(C02.glob("*.json"))+list((C02/"root-04").glob("*.json"))+[C02/"root-04/docker-events.log"]:
        sources.append({"path":str(p),"sha256":sha(p.read_bytes()),"bytes":len(p.read_bytes())})
    save("current-baseline.json",current); save("before-manifest.json",before); save("evidence-identities.json",sources)
    save("container-readonly.json",{"at":now,"container":live,"main_start_exec_or_tests":0})
    save("diagnosis-scope.json",{"confirmed":"Crashpad必需database启动参数错误可见，Chrome进程启动过但Browser未就绪",
        "root_cause":"未核；原消息2000字符截断，不能唯一归因HOME/XDG或权限",
        "next":"不重建image，在原容量tmpfs内显式用户home/XDG/所有权与可写探测、完整限定browser stderr；只一有据卡内修正",
        "primary_sources":[
          {"url":"https://chromium.googlesource.com/crashpad/crashpad/+/76a67a37b1d01128ff21b900f49912753dc49d1e/handler/crashpad_handler.md","supports":"handler要求database参数，父目录应存在；不是该binary版本的唯一根因证明"},
          {"url":"https://chromium.googlesource.com/chromium/src/+/refs/tags/133.0.6846.2/docs/linux/debugging_minidump.md","supports":"旧版文档将Linux Crash Reports放于XDG_CONFIG_HOME产品子目录，只作机制指引，不套为151实际事实"}],
        "disable_sandbox_or_crashpad_not_allowed":True,"full_platform_tree_pass":False})
    save("receipt.json",{"at":now,"TASK":"TASK-109","R":"R-103","round":"C02","report_bytes":len(report),"report_sha256":sha(report),
        "old27219_exact_suffix":True,"source_scope":len(current),"Node_actual":"v24.18.1","package_actual":"1.62.1","UID":10001,
        "Chrome_file_actual_sha256":observations[1]["data"]["executable_sha256"],"Chrome_spawn_pid":19,"browser_ready":False,
        "root_R04_ERROR_kept":True,"exact_container_stopped":True,"physical_namespace_inference_pending_review":True,
        "global_roots":74,"task_roots":4,"builds_used_limit":"2/2 sealed","preview_used":1,"controller_used":1,
        "real_total":85.797,"R04_real_including_cleanup":4.656,"R04_stop_subseconds":1.0,"preview_window":3.047,
        "C02_active_upper":958.5,"metadata_reserved_upper":300,"offline":0.015,"cleanup_upper":30,
        "acceptance":"普通接受真实加载及精确停止子事实；环境阻断，未签Browser/sandbox/navigation/H0或完整G11",
        "next":"同109C03合并完整stderr+有限目录环境修正+就绪后同容器直接真实探针，普通修正不拆卡",
        "main_product_writes_build_tests_SQL_starts":0})
    print(json.dumps({"report":len(report),"current":len(current),"Node_loaded":True,"Crashpad_tail_truncated":True,"CID_stopped":True,
        "root_cause_unique":False,"Browser_ready":False,"main_runtime":0},ensure_ascii=False))


if __name__=="__main__": main()
