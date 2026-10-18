"""两个正常远端场景优先；数值期望来自独立手算，不消耗新的模型发送。"""
import json,time
from .control import atomic,CONTINUE_ROOT,EVIDENCE


def cases(fresh):
    rows=[]
    for kind,item in fresh.items():
        steps=[{"label":"高度 h","value":"3","expect":"58.8"},{"label":"高度 h","value":"0","expect":"0 J"},{"label":"质量 m","value":"0","expect":"0 J"}] if kind=="energy" else [
          {"label":"成功概率 p","value":"0.5","expect":"0.375"},{"label":"成功次数 k","value":"0","expect":"0.125"},{"label":"成功概率 p","value":"0","expect":"1"},
          {"label":"试验次数 n","value":"0","expect":"1"},{"label":"试验次数 n","value":"20","expect":"1"},{"label":"成功次数 k","value":"20","expect":"0"}]
        rows.append({"kind":kind,"activity_id":item["activity_id"],"parent":item["parent"],"artifact_id":item["receipt"]["artifact_id"],"steps":steps})
    return rows


def verify_after_browser(matrix,folder):
    results=json.loads((folder/"browser-effects.json").read_text(encoding="utf-8"));assert len(results)>=11
    registrations=[]
    for root in (EVIDENCE/"synthetic/http-control").iterdir():
        if not root.is_dir() or not (root/"supervisor-result.json").exists():continue
        record=json.loads((root/"supervisor-result.json").read_text(encoding="utf-8"))
        if record.get("confirmed") and record.get("proof",{}).get("tree_confirmation")=="private_pid_init_terminated":registrations.append(record)
    assert len(registrations)>=2,"two normal complete runtime tree proofs missing"
    atomic(folder/"normal-result.json",{"status":"PASS_NORMAL_REMOTE_AND_STOP_ONLY","normal_browser_records":results,"treeproofs":registrations,"all_M01_M12":False})
